"""Summaries of the calculator's results: plain text for the command line, and a one-page
HTML summary to print or share, with no patient-level data."""

import calendar
import html

NAMES = {
    "m1": "Total enrollment",
    "m2": "Medicaid enrollment",
    "m3": "Newly enrolled",
    "m4": "Average duration of treatment",
    "m5": "Monthly contact rate",
    "m6": "Improvement rate",
    "m7": "Remission rate",
    "m8": "Psychiatric consultation rate",
    "m9": "Depression screening rate",
    "m10": "Depression screening yield",
    "m11": "Care manager staffing (BHCM FTE)",
}
NO_VALUE = "no patients to count this month"
NO_DISCHARGES = "nobody was discharged this month"


def value(m, r):
    if "count" in r:
        return str(r["count"])
    if m == "m4":
        return f"{r['weeks']} weeks" if r["weeks"] is not None else NO_DISCHARGES
    if m == "m11":
        return f"{r['fte']} FTE" if r["fte"] is not None else "not attested"
    if r["percent"] is None:
        return NO_VALUE
    text = f"{r['numerator']} of {r['denominator']}, {r['percent']}%"
    if m == "m10":  # NYS asks for the count and the proportion
        plural = "" if r["numerator"] == 1 else "s"
        return f"{r['numerator']} patient{plural}, {text}"
    return text


def describe_rows(issue):
    """ ' — 3 rows (C1, C7, C9)', or '' when the issue isn't about particular rows."""
    if not issue["examples"]:
        return ""
    more = ", …" if issue["count"] > len(issue["examples"]) else ""
    count = f" — {issue['count']} rows" if issue["count"] > 1 else ""
    return f"{count} ({', '.join(issue['examples'])}{more})"


def summary(results):
    lines = [f"CoCM caseload metrics for {results['reporting_month']}", ""]
    checks = results.get("checks", [])
    if checks:
        errors = sum(1 for i in checks if i["level"] == "error")
        looks = len(checks) - errors
        parts = ([f"{errors} problem{'s' if errors != 1 else ''} that left rows out"] if errors else []) \
            + ([f"{looks} thing{'s' if looks != 1 else ''} to look at"] if looks else [])
        lines.append(f"Data check: {', '.join(parts)}. Details at the end.")
        lines.append("")
    else:
        lines += ["Data check: no problems found.", ""]
    width = max(len(n) for n in NAMES.values())
    for m, name in NAMES.items():
        lines.append(f"  {m[1:]:>2}. {name:<{width}}  {value(m, results['metrics'][m])}")
    for title, key in (("What to tell OMH", "disclosures"), ("Before you report", "warnings")):
        if results[key]:
            lines += ["", f"{title}:"] + [f"  - {x}" for x in results[key]]
    if checks:
        lines += ["", "Data check:"]
        for issue in checks:
            lines.append(f"  {issue['level'].upper():7} {issue['table']}: {issue['message']}"
                         + describe_rows(issue))
    if results["fell_out"]:
        lines += ["", "Patients not counted, and why (keep this at your site):"]
        for m, rows in results["fell_out"].items():
            lines.append(f"  {m[1:]}. {NAMES[m]}")
            lines += [f"     {r['patient_id']}: {r['reason']}" for r in rows]
    return "\n".join(lines)


SITE = "https://spier-project.github.io/nys-omh-cocm-caseload-reporting/"
GUIDE = SITE + "docs/guide/"


def month_name(month):
    year, number = month.split("-")
    return f"{calendar.month_name[int(number)]} {year}"


def cells(m, r):
    """(result, numerator, denominator) for the summary's table; '' where there's none."""
    if "count" in r:
        return str(r["count"]), "", ""
    if m == "m4":
        return (f"{r['weeks']} weeks" if r["weeks"] is not None else NO_DISCHARGES.capitalize()), "", ""
    if m == "m11":
        return (f"{r['fte']} FTE" if r["fte"] is not None else "Not attested"), "", ""
    result = f"{r['percent']}%" if r["percent"] is not None else NO_VALUE.capitalize()
    return result, str(r["numerator"]), str(r["denominator"])


# The summary is a standalone download, so it can't link web/styles/tokens.css: it carries
# a copy of the light tokens it uses, which tests/test_styles.py keeps in step. Its font is
# the system font, so it prints without fetching one.
SUMMARY_STYLE = """
  :root {
    --paper: #ffffff; --ink: #1e2a33; --muted: #56656f; --line: #cfdad7; --spruce: #1f6f5c;
    --amber: #8a5300; --amber-soft: #fbf0dc; --brick: #9c3424; --brick-soft: #f8e4e0;
    --font-body: system-ui, -apple-system, "Segoe UI", sans-serif;
    --space-1: .25rem; --space-2: .5rem; --space-3: .75rem; --space-4: 1rem;
    --space-6: 1.5rem; --space-7: 2rem; --border-thin: 1px; --border-accent: 4px;
    --measure: 46rem;
  }
  body { margin: 0; background: var(--paper); color: var(--ink);
         font: 15px/1.5 var(--font-body); }
  main { max-width: var(--measure); margin: 0 auto; padding: var(--space-7) var(--space-4); }
  h1 { font-size: 1.6rem; margin: 0 0 var(--space-1); }
  h2 { font-size: 1.05rem; margin: var(--space-6) 0 var(--space-2); }
  p, ul { margin: 0 0 var(--space-2); }
  .meta { color: var(--muted); }
  .panel { border-left: var(--border-accent) solid var(--amber); background: var(--amber-soft);
           padding: var(--space-2) var(--space-3); }
  .panel.error { border-color: var(--brick); background: var(--brick-soft); }
  table { border-collapse: collapse; width: 100%; }
  th, td { text-align: left; padding: var(--space-1) var(--space-2);
           border-bottom: var(--border-thin) solid var(--line); vertical-align: top; }
  th { font-size: .85rem; color: var(--muted); }
  td.num, th.num { text-align: right; font-variant-numeric: tabular-nums; }
  td.result { font-weight: 700; }
  footer { margin-top: var(--space-6); font-size: .85rem; color: var(--muted); }
  a { color: var(--spruce); }
  @media print { main { padding: 0; } a { color: inherit; text-decoration: none; } }
"""

PAGES = {
    "m1": "01-total-enrollment", "m2": "02-medicaid-enrollment", "m3": "03-newly-enrolled",
    "m4": "04-average-duration-of-treatment", "m5": "05-monthly-contact-rate",
    "m6": "06-improvement-rate", "m7": "07-remission-rate",
    "m8": "08-psychiatric-consultation-rate", "m9": "09-depression-screening-rate",
    "m10": "10-depression-screening-yield", "m11": "11-bhcm-staffing",
}


def summary_html(results, made=None):
    """A one-page summary to print, keep or share: the eleven numbers, the data check, and
    what to tell OMH. It leaves out every patient id: the list of patients each rate didn't
    count stays in the full results. `made` is the date it was made, as text."""
    e = html.escape
    month = month_name(results["reporting_month"])
    meta = [f"Reporting month: {e(month)}"]
    if results.get("site_id"):
        meta.append(f"Site: {e(str(results['site_id']))}")
    if made:
        meta.append(f"Made {e(made)}")
    out = ["<!doctype html>", '<html lang="en">', "<head>", '<meta charset="utf-8">',
           '<meta name="viewport" content="width=device-width, initial-scale=1">',
           f"<title>CoCM caseload summary, {e(month)}</title>",
           f"<style>{SUMMARY_STYLE}</style>", "</head>", "<body>", "<main>",
           "<h1>CoCM caseload summary</h1>",
           f'<p class="meta">{" · ".join(meta)}</p>']

    checks = results.get("checks", [])
    errors = sum(1 for i in checks if i["level"] == "error")
    looks = len(checks) - errors
    if errors:
        out.append(f'<p class="panel error">Data check: {errors} problem{"s" if errors != 1 else ""} '
                   "left rows out of these numbers. Fix them in the files and calculate again "
                   "before reporting.</p>")
    elif looks:
        out.append(f'<p class="panel">Data check: {looks} thing{"s" if looks != 1 else ""} to look '
                   "at. They're counted, but may not be what you expect.</p>")
    else:
        out.append("<p>Data check: no problems found.</p>")

    out += ["<h2>The eleven metrics</h2>", "<table>",
            '<thead><tr><th class="num" scope="col">#</th><th scope="col">Metric</th>'
            '<th class="num" scope="col">Result</th><th class="num" scope="col">Numerator</th>'
            '<th class="num" scope="col">Denominator</th></tr></thead>', "<tbody>"]
    for m, name in NAMES.items():
        result, numerator, denominator = cells(m, results["metrics"][m])
        out.append(f'<tr><td class="num">{m[1:]}</td>'
                   f'<td><a href="{GUIDE}metrics/{PAGES[m]}.html">{e(name)}</a></td>'
                   f'<td class="num result">{e(result)}</td><td class="num">{e(numerator)}</td>'
                   f'<td class="num">{e(denominator)}</td></tr>')
    out += ["</tbody>", "</table>"]

    if results["warnings"]:
        out += ["<h2>Before you report</h2>", "<ul>"]
        out += [f"<li>{e(w)}</li>" for w in results["warnings"]]
        out.append("</ul>")
    out += ["<h2>What to tell OMH</h2>",
            "<p>How these numbers were counted. Include these notes with your report.</p>", "<ul>"]
    out += [f"<li>{e(d)}</li>" for d in results["disclosures"]] or ["<li>None</li>"]
    out.append("</ul>")

    out += ["<footer>",
            "<p>This summary has no patient-level data. The list of patients each rate didn't "
            "count, and why, is in the full results; keep that at your site.</p>",
            f'<p>Counted with the <a href="{SITE}">'
            f'CoCM caseload calculator</a>, following an <a href="{GUIDE}start-here.html">opinionated guide</a> '
            "to OMH's caseload metrics. It is an independent project, not an OMH product.</p>",
            "</footer>", "</main>", "</body>", "</html>"]
    return "\n".join(out) + "\n"
