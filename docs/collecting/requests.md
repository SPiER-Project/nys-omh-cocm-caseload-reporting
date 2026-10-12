# Asking for the data

Most of the work of a first report is asking other people for data: billing for coverage
and visits, the EHR team for PHQ results, whoever keeps the registry for the CoCM
records. These requests are ready to send. Copy one, fill in the parts in [brackets], and
attach or link the [CSV templates](https://spier-project.github.io/nys-omh-cocm-caseload-reporting/cocm-csv-templates.zip),
so the reply comes back in the shape the calculator reads.

**Before sending any of them:**
- **Agree how files will come back.** Every report below contains patient information.
  Ask for it through your organization's secure file share or secure email, not ordinary
  email.
- **Ask for the MRN as the patient id in every report,** so the reports join. If the
  tables will leave your site, pseudonymize them with your site's key first (see
  [one patient id](overview.md#one-patient-id)).
- **Ask once, then ask for the same report every month.** The first request takes the
  most explaining; after that it's "the same as last month, for [month]".

Which requests a site needs depends on its route ([collecting the data](overview.md#pick-your-route)):

| Request | Who usually has it | Every site? |
|---|---|---|
| [Coverage](#coverage) | Billing or practice management | Yes |
| [Practice visits](#practice-visits) | Billing or practice management | Yes |
| [PHQ results](#phq-results) | The EHR team or a report writer | Yes |
| [CoCM records](#cocm-records) | Whoever keeps the registry, or the EHR team if there's no registry | Yes, unless the program lead fills in the workbook from the registry themselves |
| [Program facts](#program-facts) | The program lead | Yes |

## Coverage

> **Subject:** Coverage report for CoCM reporting, [month and year]
>
> Hi [name],
>
> For our Collaborative Care report to the NYS Office of Mental Health, I need each
> patient's insurance coverage, with dates. Could you run a report of every coverage
> period that was active on any day of [month and year], for the patients in the attached
> list (or for all patients seen in [month and year], if that's easier)?
>
> One row per coverage period, with these columns:
> - **patient_id:** the MRN
> - **payer_category:** one of medicaid_ffs, medicaid_managed_care,
>   dual_medicare_medicaid, child_health_plus, essential_plan, medicare, commercial,
>   self_pay, other
> - **start_date** and **end_date:** the period's effective dates, as YYYY-MM-DD (blank
>   end date if still active)
> - **plan_name:** the plan as it appears in billing
>
> Every period, not just the current one, and secondary coverage too. If mapping plans to
> the categories is hard, send the plan names and I'll map them.
>
> Please send it as coverage.csv (the template is attached) through [our secure file
> share]. Thank you!

The payer mapping behind `payer_category` is a one-time job; see
[Medicaid](../guide/concepts/medicaid.md#what-the-program-should-do).

## Practice visits

> **Subject:** Visits report for CoCM reporting, [month and year]
>
> Hi [name],
>
> For our Collaborative Care report to the NYS Office of Mental Health, I need every
> visit at [practice] from [first day] to [last day of the month], all payers. It's the
> denominator for the depression screening rate.
>
> One row per visit, with these columns:
> - **visit_id:** the encounter or visit number
> - **patient_id:** the MRN
> - **visit_date:** as YYYY-MM-DD
> - **provider_category:** primary_care, other_medical, behavioral_health, nursing_only
>   or ancillary, from the rendering provider's type or specialty
> - **billing_codes:** the CPT and HCPCS codes billed for the visit, separated by ;
> - **modality:** in_person, video or phone
>
> Please include every visit, not only office visits: the calculator works out which
> ones count. And please send each patient's date of birth too, as patient.csv with
> patient_id and birth_date.
>
> Please send them as practice_visit.csv and patient.csv (templates attached) through
> [our secure file share]. Thank you!

## PHQ results

> **Subject:** PHQ-2 and PHQ-9 results for CoCM reporting, [month and year]
>
> Hi [name],
>
> For our Collaborative Care report to the NYS Office of Mental Health, I need every
> scored PHQ-2, PHQ-9 and PHQ-A (the adolescent PHQ-9) recorded for any patient in the
> <!--rule:extraction.phq_history_months-->13<!--/rule--> months ending [last day of the month], from every department and every
> questionnaire or flowsheet that holds one, including the patient portal.
>
> One row per scored result, with these columns:
> - **result_id:** the result or observation id
> - **patient_id:** the MRN
> - **administered_date:** when it was completed, as YYYY-MM-DD in local time
> - **instrument:** phq2, phq9 or phq_a
> - **total_score:** the total score (leave out declined or unscored forms)
>
> If our EHR can produce a FHIR export of these as Observations instead, that works too.
>
> Please send it as scale_result.csv (template attached) through [our secure file
> share]. Thank you!

The <!--rule:extraction.phq_history_months-->13<!--/rule--> months cover both screening metrics: <!--rule:what-counts-as-screened.lookback_months-->12<!--/rule--> months for the
screening rate, and the <!--rule:initial-phq-9.lookback_days-->365<!--/rule--> days before each PHQ-9 for the yield. A FHIR export of
patients, coverage, encounters and observations can replace the first three requests;
see [reading FHIR](../tooling.md#reading-fhir).

## CoCM records

> **Subject:** Collaborative Care records for CoCM reporting, [month and year]
>
> Hi [name],
>
> For our Collaborative Care report to the NYS Office of Mental Health, I need the CoCM
> records for every patient enrolled at any time in [month and year], and for any
> enrollment still open, however old.
>
> Four lists, each with the MRN as patient_id and dates as YYYY-MM-DD:
> 1. **Enrollments** (cocm_episode.csv): episode id, enrollment date (the date of the
>    BHCM's initial assessment, not the referral), primary condition, primary scale,
>    discharge date and reason.
> 2. **Contacts** (contact.csv): every contact and outreach attempt since each enrollment
>    began: date, who made it (bhcm or other), what kind (treatment, outreach_attempt,
>    scheduling, no_show, message), and in person, video or phone.
> 3. **Symptom scales** (scale_result.csv): every scored PHQ-9, GAD-7, PCL-5, SMFQ,
>    SCARED, PSC-17 and Vanderbilt since each enrollment began, with the form (child,
>    parent, teacher) where there is one.
> 4. **Psychiatric case reviews** (psych_review.csv): every patient the psychiatric
>    consultant reviewed in the <!--rule:psychiatric-case-review.window_days-->60<!--/rule--> days ending [last day of the month], one row
>    per patient, with whether a recommendation was documented.
>
> The templates attached list every column and the values each one allows.
>
> Please send them through [our secure file share]. Thank you!

If the registry is a spreadsheet the program lead keeps, it's usually quicker for them
to fill in the [workbook](workbook.md) than to answer this request.

## Program facts

These aren't a request to anyone else. The program lead fills in one row of
`site_month.csv`, or the `site_month` tab of the workbook:
- the reporting month;
- BHCM FTE for the month ([BHCM FTE](../guide/concepts/bhcm-fte.md));
- the screening age floor the practice uses;
- one sentence on how contacts were judged to be treatment;
- the date the data was pulled, and the system it came from.

## When the files come back

Add them all to the [calculator page](https://spier-project.github.io/nys-omh-cocm-caseload-reporting/).
Its data check lists any rows it can't use, by id, and anything that looks wrong. Send
those lists back to whoever ran the report: they're usually a quick fix once someone can
see the rows.
