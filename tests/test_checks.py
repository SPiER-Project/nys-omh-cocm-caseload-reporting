"""Tests for the data check that runs before anything is counted.

    python3 -m unittest discover tests
"""

import csv
import glob
import io
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from calculator import calculate, read_rules, read_tables  # noqa: E402
from calculator.checks import check  # noqa: E402

with open(os.path.join(ROOT, "rules", "calls.toml")) as f:
    SETTINGS = read_rules(f.read())
EXAMPLE = os.path.join(ROOT, "tests", "fixtures", "example-caseload")


def example():
    texts = {}
    for path in glob.glob(os.path.join(EXAMPLE, "*.csv")):
        with open(path, newline="") as f:
            texts[os.path.splitext(os.path.basename(path))[0]] = f.read()
    return texts


def edit(texts, table, old, new):
    assert old in texts[table], old
    return {**texts, table: texts[table].replace(old, new, 1)}


def rows(text):
    return list(csv.DictReader(io.StringIO(text)))


class CleanDataTests(unittest.TestCase):
    def test_the_fixtures_have_no_issues(self):
        for directory in ("example-caseload", "screening-example"):
            texts = {}
            for path in glob.glob(os.path.join(ROOT, "tests", "fixtures", directory, "*.csv")):
                with open(path, newline="") as f:
                    texts[os.path.splitext(os.path.basename(path))[0]] = f.read()
            with self.subTest(fixture=directory):
                self.assertEqual(check(texts, SETTINGS, "2025-03")[1], [])


class ErrorTests(unittest.TestCase):
    """Rows that can't be used are left out, and named."""

    def assert_left_out(self, texts, table, record_id, words):
        clean, issues = check(texts, SETTINGS, "2025-03")
        first = rows(clean[table])[0].keys() if rows(clean[table]) else []
        id_column = next(iter(first), None)
        self.assertNotIn(record_id, [r[id_column] for r in rows(clean[table])] if id_column else [])
        matching = [i for i in issues if i["level"] == "error" and i["table"] == table
                    and words in i["message"]]
        self.assertTrue(matching, issues)
        self.assertIn(record_id, matching[0]["examples"])

    def test_value_not_allowed(self):
        texts = edit(example(), "contact", "C16,P4,2024-12-10,bhcm,treatment", "C16,P4,2024-12-10,bhcm,Treatment")
        self.assert_left_out(texts, "contact", "C16", "isn't an allowed value")

    def test_bad_date(self):
        texts = edit(example(), "contact", "C16,P4,2024-12-10", "C16,P4,12/10/2024")
        self.assert_left_out(texts, "contact", "C16", "isn't a date")

    def test_impossible_date(self):
        texts = edit(example(), "contact", "C16,P4,2024-12-10", "C16,P4,2024-02-30")
        self.assert_left_out(texts, "contact", "C16", "isn't a date")

    def test_required_value_blank(self):
        texts = edit(example(), "scale_result", "S2,P1,2025-03-10,phq9,8", "S2,P1,2025-03-10,phq9,")
        self.assert_left_out(texts, "scale_result", "S2", "total_score is blank")

    def test_score_out_of_range(self):
        texts = edit(example(), "scale_result", "S2,P1,2025-03-10,phq9,8", "S2,P1,2025-03-10,phq9,35")
        self.assert_left_out(texts, "scale_result", "S2", "must be 0–27")

    def test_discharged_before_enrolled(self):
        texts = edit(example(), "cocm_episode", "E9,P9,2024-12-09", "E9,P9,2025-04-09")
        self.assert_left_out(texts, "cocm_episode", "E9", "discharged before enrolled")

    def test_missing_required_column_leaves_the_table_out(self):
        texts = {**example(), "patient": "patient_id\nP1\n"}
        clean, issues = check(texts, SETTINGS, "2025-03")
        self.assertEqual(rows(clean["patient"]), [])
        self.assertTrue(any("missing required column birth_date" in i["message"] for i in issues))

    def test_a_left_out_row_changes_the_numbers_visibly(self):
        # Without the check, a mistyped contact kind would silently cost P1 their contact.
        texts = edit(example(), "contact", "C6,P1,2025-03-10,bhcm,treatment", "C6,P1,2025-03-10,bhcm,session")
        clean, issues = check(texts, SETTINGS, "2025-03")
        metrics = calculate(read_tables(clean), SETTINGS, "2025-03")["metrics"]
        self.assertEqual(metrics["m5"]["numerator"], 6)
        self.assertTrue(any("C6" in i["examples"] for i in issues))


class WarningTests(unittest.TestCase):
    """Rows that are kept but probably wrong are flagged."""

    def warnings(self, texts, month="2025-03"):
        clean, issues = check(texts, SETTINGS, month)
        return {(i["table"], i["message"].split(",")[0]): i["examples"]
                for i in issues if i["level"] == "warning"}

    def test_patient_not_in_the_patient_table(self):
        texts = {**example(), "psych_review": example()["psych_review"] + "R9,P99,2025-03-15,true,pcp\n"}
        found = self.warnings(texts)
        self.assertEqual(found[("psych_review", "patient_id isn't in the patient table")], ["P99"])

    def test_enrolled_patient_without_coverage(self):
        texts = {**example(), "coverage": "\n".join(
            line for line in example()["coverage"].splitlines() if not line.startswith("P8,")) + "\n"}
        found = self.warnings(texts)
        self.assertEqual(found[("coverage", "an enrolled patient has no coverage")], ["P8"])

    def test_enrolled_patient_without_a_primary_scale_score(self):
        texts = edit(example(), "cocm_episode", "E8,P8,2024-12-16,registry,depression,phq9",
                     "E8,P8,2024-12-16,registry,depression,gad7")
        found = self.warnings(texts)
        self.assertIn("P8", found[("scale_result", "an enrolled patient has no score on their primary scale since enrollment")])

    def test_duplicate_record_ids(self):
        texts = edit(example(), "contact", "C2,P1", "C1,P1")
        found = self.warnings(texts)
        self.assertEqual(found[("contact", "contact_id is used by more than one row")], ["C1"])

    def test_site_month_for_another_month(self):
        found = self.warnings(example(), month="2025-04")
        self.assertIn(("site_month", "reporting_month is 2025-03"), found)

    def test_unknown_column_and_table(self):
        texts = {**example(), "visits": "a\n1\n",
                 "patient": example()["patient"].replace("patient_id,birth_date", "patient_id,birth_date,mrn", 1)}
        found = self.warnings(texts)
        self.assertIn(("visits", "isn't a data-contract table"), found)
        self.assertIn(("patient", "column mrn isn't in the data contract"), found)


if __name__ == "__main__":
    unittest.main()
