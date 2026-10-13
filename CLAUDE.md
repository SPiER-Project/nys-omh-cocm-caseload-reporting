# NYS OMH CoCM Caseload Reporting

How New York clinics report the eleven monthly Collaborative Care (CoCM) caseload metrics to
the NY State Office of Mental Health, and tools that calculate them. Remote: SPiER-Project.
Published calculator: https://spier-project.github.io/nys-omh-cocm-caseload-reporting/

## Goals, in order

1. **Opinionated guidance for clinics** (`docs/guide/`): what each metric counts, and how to
   get each fact out of a registry, an EHR or billing.
2. **Tools that calculate the metrics** from the site's data, without the data leaving the
   site.

The guide comes first. Tooling follows the guide, never the other way round.

## Status

- The guide is written. All 31 calls in `docs/reference/our-calls.md` still **need
  approval**; some also need a clinician's sign-off. Treat the guide as provisional.
- Built:
  - the calculator, at the command line and in the browser;
  - the workbook and the CSV templates;
  - FHIR input for the EHR half of the data;
  - pseudonymous patient ids;
  - the data check.
- Waiting on NYS: the REDCap form and deadline, so there's no submission output yet.
- Open items: `docs/open-questions.md`.

## Measure decisions

- **Never settle an open measure decision silently.** Raise it with the user.
- Every interpretation of the NYS document is a call, with two halves:
  - the reasoning, in `docs/reference/our-calls.md`;
  - the values, in `rules/calls.toml`.
- A new call starts as `status = "proposed"`, `approval = "needed"`. Only the user adopts
  or approves a call.
- Look up codes and thresholds (LOINC, CPT, payer types, cutoffs) in a source, and cite it
  on `docs/reference/instruments.md`. Never state them from memory.

## Layout

| Path | What it is |
|---|---|
| `docs/guide/` | The guide: metric pages, concept pages, site setup, the example caseload |
| `docs/collecting/` | Where each fact lives, the routes for getting it out, the workbook, the EHR report spec, registry mappings |
| `docs/reference/` | Our calls, the instruments, the data contract (with its FHIR mapping), the NYS source document |
| `docs/archive/` | Draft v0.1 and its review notes. Frozen: never edit; fix the guide instead |
| `rules/calls.toml` | Every value the calls set; the calculator's settings |
| `calculator/` | Standard-library Python: checks, compute, CSV, workbook and FHIR readers, pseudonyms, and the CLI and browser entry points |
| `web/` | The browser page, the downloads, the guide's pages and their stylesheets (`web/styles/`), all published by Pages |
| `tests/` | Fixtures (synthetic), the worked-example registry and its lock file, unit tests |
| `scripts/` | Builders and checkers |

## What's generated, and from where

| Source of truth | Generates | Rebuild with |
|---|---|---|
| `rules/calls.toml` | Values and tables between `<!--rule:…-->` and `<!--rules:…-->` markers in the docs | `python3 scripts/rules.py sync` |
| `tests/fixtures/*/expected.toml` | Results between `<!--expect:…-->` markers | `python3 scripts/examples.py sync` |
| `docs/reference/data-contract.md` | `calculator/schema.py` | `python3 scripts/build_schema.py` |
| The data contract and the example fixture | `web/cocm-workbook*.xlsx` and `web/cocm-csv-*.zip` | `python3 scripts/build_workbook.py` |
| `web/template.html`, `calculator/`, the rules, the example | `web/index.html` | `python3 scripts/build_web.py` |
| `docs/guide/`, `docs/collecting/`, `docs/reference/` | The guide's pages, `web/docs/` | `python3 scripts/build_guide.py` |

- Never edit generated output or text between markers. Change the source and rebuild.
- If a call changes, a worked example that depends on it goes stale. Rework the example on
  its pages, then run `python3 scripts/examples.py verify <name>`.

## Checks

CI runs all of these on every PR. Run them before committing:

```bash
python3 scripts/rules.py check && python3 scripts/examples.py check && \
python3 -m unittest discover tests && python3 scripts/build_schema.py --check && \
python3 scripts/build_workbook.py --check && python3 scripts/build_web.py --check && \
python3 scripts/build_guide.py --check && python3 scripts/check_links.py
```

## Conventions

- **No real patient data anywhere.** Fixtures and examples are invented.
- **The calculator uses the standard library only,** and its core works on text, not files,
  because the same code runs in the browser through Pyodide. Only `__main__.py`,
  `pseudonymize.py` and `inputs.py` touch files.
- **Writing for clinic readers** is direct and plain, with no hype words. Describe the
  guide as an opinionated approach to the NYS guidelines, not as filling gaps NYS left.
- **Pull requests:**
  - one PR per piece of work, branched from `origin/main`;
  - the user reviews and merges, then asks for the next piece;
  - never stack a PR on another PR's branch.
- **Styles:** every value is a token in `web/styles/tokens.css`. Component stylesheets
  (`site.css`, `guide.css`, `calculator.css`) use tokens only, and pages carry no styles of
  their own; `tests/test_styles.py` checks both.
- **Navigation:** `scripts/sitenav.py` is the site map. It sets the header, breadcrumbs and
  next and previous for every page. A new guide page must be added there, or the guide
  build fails.
- **Pages** republishes `web/` on every push to `main`. The guide is read there, at
  `docs/guide/start-here.html`: after changing a doc, rebuild its page.
