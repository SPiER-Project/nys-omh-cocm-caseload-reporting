"""The data check: what's wrong with the input, before anything is counted.

    check(texts, settings, month) -> (clean_texts, issues)

texts is {table: csv text}. Every row is checked against the data contract
(calculator/schema.py) and against the other tables. Two kinds of issue come back:

- errors: rows that can't be used as they are (a missing required value, a value the
  contract doesn't allow, a date or number that isn't one, an impossible score). They're
  left out of clean_texts, and the issue says which rows, so the site can fix them;
- warnings: rows that are kept but probably wrong, or that won't count the way the site
  may expect (a patient id with no patient row, an enrolled patient with no coverage).

Without this, a typo in a contact's kind or a scale's name would silently not count, and
a site couldn't tell bad data from a bad month.
"""

import csv
import io
import re
from collections import defaultdict
from datetime import date, timedelta

from .compute import FORMS, month_bounds
from .schema import SCHEMA

EXAMPLES = 5  # rows named per issue


def _valid(typ, value):
    if typ == "date":
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            return False
        try:
            date.fromisoformat(value)
        except ValueError:
            return False
        return True
    if typ == "int":
        return re.fullmatch(r"-?\d+", value) is not None
    if typ == "decimal":
        return re.fullmatch(r"-?\d+(\.\d+)?", value) is not None
    if typ == "bool":
        return value in ("true", "false")
    if typ == "YYYY-MM":
        return re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", value) is not None
    return True


class _Issues:
    def __init__(self):
        self.found = defaultdict(list)  # (level, table, message) -> [row labels]

    def add(self, level, table, message, label=None):
        self.found[(level, table, message)].append(label)

    def result(self):
        out = []
        for (level, table, message), labels in self.found.items():
            labels = [x for x in labels if x]
            out.append({"level": level, "table": table, "message": message,
                        "count": max(len(labels), 1), "examples": labels[:EXAMPLES]})
        return sorted(out, key=lambda i: (i["level"] != "error", i["table"], i["message"]))


def check(texts, settings, month):
    issues = _Issues()
    first, last = month_bounds(month)
    rows = {}
    for table in sorted(set(texts) - set(SCHEMA)):
        issues.add("warning", table, "isn't a data-contract table, so it's ignored")

    for table, columns in SCHEMA.items():
        text = texts.get(table) or ""
        reader = csv.DictReader(io.StringIO(text))
        header = reader.fieldnames or []
        spec = {name: (typ, req, allowed) for name, typ, req, allowed in columns}
        id_column = columns[0][0]
        kept = []
        if text.strip():
            for col in header:
                if col not in spec:
                    issues.add("warning", table, f"column {col} isn't in the data contract, so it's ignored")
            missing = [name for name, (_, req, _) in spec.items() if req and name not in header]
            if missing:
                issues.add("error", table, "missing required column " + ", ".join(missing)
                           + "; the whole table is left out")
                rows[table] = []
                continue
        for n, row in enumerate(reader, start=2):
            label = row.get(id_column) or f"line {n}"
            bad = False
            for col, (typ, req, allowed) in spec.items():
                value = (row.get(col) or "").strip()
                row[col] = value
                if not value:
                    if req:
                        issues.add("error", table, f"{col} is blank; those rows are left out", label)
                        bad = True
                    continue
                if allowed is not None and value not in allowed:
                    issues.add("error", table, f"{col} = {value!r} isn't an allowed value; "
                               "those rows are left out", label)
                    bad = True
                elif typ != "enum" and not _valid(typ, value):
                    issues.add("error", table, f"{col} = {value!r} isn't a {typ}; "
                               "those rows are left out", label)
                    bad = True
            if not bad and table == "scale_result":
                bounds = settings.score_ranges.get(row["instrument"])
                score = int(row["total_score"])
                if bounds and not bounds[0] <= score <= bounds[1]:
                    issues.add("error", table, f"a {row['instrument']} score must be "
                               f"{bounds[0]}–{bounds[1]}; those rows are left out", label)
                    bad = True
            if not bad and table == "cocm_episode" and row.get("discharge_date") \
                    and row["discharge_date"] < row["enrollment_date"]:
                issues.add("error", table, "discharged before enrolled; those rows are left out", label)
                bad = True
            if not bad:
                kept.append(row)
        rows[table] = kept

        if id_column != "patient_id" and table != "site_month":  # tables keyed by a record id
            seen = defaultdict(int)
            for row in kept:
                seen[row[id_column]] += 1
            for value, count in seen.items():
                if count > 1:
                    issues.add("warning", table, f"{id_column} is used by more than one row", value)

    # Across tables ----------------------------------------------------------------------
    patients = {r["patient_id"] for r in rows["patient"]}
    for table in ("coverage", "cocm_episode", "contact", "scale_result", "psych_review",
                  "practice_visit"):
        unknown = sorted({r["patient_id"] for r in rows[table]} - patients)
        if unknown and patients:
            effect = (" (visits without a birth date can't count for metric 9)"
                      if table == "practice_visit" else "")
            for pid in unknown:
                issues.add("warning", table, "patient_id isn't in the patient table" + effect, pid)

    covered = {r["patient_id"] for r in rows["coverage"]}
    scored = defaultdict(set)
    for r in rows["scale_result"]:
        scored[r["patient_id"]].add((r["instrument"], r["administered_date"]))
    for e in rows["cocm_episode"]:
        start = e["enrollment_date"]
        if start > last.isoformat() or (e["discharge_date"] and e["discharge_date"] < first.isoformat()):
            continue  # not enrolled this month
        if e["patient_id"] not in covered:
            issues.add("warning", "coverage", "an enrolled patient has no coverage, so they're "
                       "counted as not Medicaid", e["patient_id"])
        due = date.fromisoformat(start) + timedelta(days=settings.baseline_window_days)
        scale = settings.phq_a_counts_as if e["primary_scale"] == "phq_a" else e["primary_scale"]
        family = {scale, "phq_a"} if scale == "phq9" else set(FORMS.get(scale, (scale,)))
        if due <= last and not any(i in family and d >= start for i, d in scored[e["patient_id"]]):
            issues.add("warning", "scale_result", "an enrolled patient has no score on their "
                       "primary scale since enrollment, so they can't count as improved or in "
                       "remission", e["patient_id"])

    site = rows["site_month"]
    if not site:
        issues.add("warning", "site_month", "there's no site_month row, so BHCM FTE isn't "
                   "attested and the guide's screening age floor is used")
    else:
        if len(site) > 1:
            issues.add("warning", "site_month", "there's more than one row; the first is used")
        if site[0]["reporting_month"] != month:
            issues.add("warning", "site_month", f"reporting_month is {site[0]['reporting_month']}, "
                       f"but the report is for {month}")

    clean = {}
    for table, columns in SCHEMA.items():
        if not rows[table] and not (texts.get(table) or "").strip():
            continue
        out = io.StringIO()
        writer = csv.DictWriter(out, fieldnames=[c[0] for c in columns], extrasaction="ignore",
                                lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows[table])
        clean[table] = out.getvalue()
    return clean, issues.result()
