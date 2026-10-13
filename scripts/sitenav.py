"""The published site's map and header, shared by scripts/build_web.py (the calculator)
and scripts/build_guide.py (the guide's pages).

SECTIONS sets the header's links and the guide's reading order. Every published page
under docs/ must appear in it exactly once: build_guide.py fails if one is missing, so a
new page can't be published without a place in the navigation.

Paths are relative to docs/. Each section lands on its first page.
"""

import html

STYLES = ("tokens.css", "site.css")  # every page; then each page adds its own

SECTIONS = [  # (header label, [(group or None, [pages])])
    ("Guide", [
        (None, ["guide/start-here.md", "guide/about-the-program.md",
                "guide/medicaid-billing.md", "guide/site-setup.md",
                "guide/example-caseload.md"]),
        ("Concepts", ["guide/concepts/reporting-month.md",
                      "guide/concepts/enrollment-and-discharge.md",
                      "guide/concepts/medicaid.md", "guide/concepts/scales-and-outcomes.md",
                      "guide/concepts/contacts-and-reviews.md", "guide/concepts/screening.md",
                      "guide/concepts/bhcm-fte.md"]),
    ]),
    ("Metrics", [
        (None, ["guide/metrics/at-a-glance.md",
                "guide/metrics/01-total-enrollment.md",
                "guide/metrics/02-medicaid-enrollment.md",
                "guide/metrics/03-newly-enrolled.md",
                "guide/metrics/04-average-duration-of-treatment.md",
                "guide/metrics/05-monthly-contact-rate.md",
                "guide/metrics/06-improvement-rate.md",
                "guide/metrics/07-remission-rate.md",
                "guide/metrics/08-psychiatric-consultation-rate.md",
                "guide/metrics/09-depression-screening-rate.md",
                "guide/metrics/10-depression-screening-yield.md",
                "guide/metrics/11-bhcm-staffing.md"]),
    ]),
    ("Getting the data", [
        (None, ["collecting/requests.md", "collecting/overview.md", "collecting/workbook.md"]),
        ("Systems", ["collecting/ehrs/README.md",
                     "collecting/registries/prototype-cocm-registry.md"]),
    ]),
    ("Reference", [
        (None, ["reference/our-calls.md", "reference/instruments.md",
                "reference/data-contract.md",
                "reference/nys-source/nys-omh-cocm-metrics-2025.md"]),
    ]),
]

CALCULATOR = "Calculator"


def reading_order():
    """Every guide page, in order, with its section and group: [(page, section, group)]."""
    return [(page, section, group)
            for section, groups in SECTIONS
            for group, pages in groups
            for page in pages]


def landing(section):
    """The first page of a header section."""
    return next(p for p, s, _ in reading_order() if s == section)


def html_name(page):
    """docs-relative .md path -> its published path under web/docs/."""
    head, name = page.rsplit("/", 1) if "/" in page else ("", page)
    name = "index.html" if name == "README.md" else name[:-3] + ".html"
    return f"{head}/{name}" if head else name


def group_landing(section, group):
    return next(p for p, s, g in reading_order() if s == section and g == group)


def header(calculator_href, section_href, current, on_landing):
    """The site header. calculator_href is the calculator's URL from this page;
    section_href(section) is a section's landing URL; current is the label to mark, and
    on_landing says whether this page is that link's target (aria-current="page") or
    just inside its section (aria-current="true")."""
    items = [(CALCULATOR, calculator_href)] + [(s, section_href(s)) for s, _ in SECTIONS]
    mark = ' aria-current="page"' if on_landing else ' aria-current="true"'
    links = "\n".join(
        f'<li><a href="{html.escape(href)}"{mark if label == current else ""}>'
        f"{html.escape(label)}</a></li>"
        for label, href in items)
    return f"""<a class="skip" href="#main">Skip to content</a>
<header class="site"><div class="site-inner">
<a class="brand" href="{html.escape(calculator_href)}">CoCM caseload reporting</a>
<nav aria-label="Site"><ul>
{links}
</ul></nav>
</div></header>"""
