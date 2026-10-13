# The eleven metrics at a glance

What each metric counts, in a sentence, and how it's reported. Each one links to its own
page, which has the full rule, a worked example, where the data lives and the common
mistakes. Every rule is provisional until approved.

| # | Metric | What it counts | Reported as |
|---|---|---|---|
| 1 | [Total enrollment](01-total-enrollment.md) | Patients enrolled in CoCM on any day this month, whatever their insurance | A count |
| 2 | [Medicaid enrollment](02-medicaid-enrollment.md) | Metric 1, limited to patients with New York Medicaid on the first day of the month | A count |
| 3 | [Newly enrolled](03-newly-enrolled.md) | Medicaid patients whose initial assessment, and so their enrollment, was this month | A count |
| 4 | [Average duration of treatment](04-average-duration-of-treatment.md) | For Medicaid patients discharged this month, the average time from enrollment to discharge | Weeks, to one decimal place. No value if nobody was discharged |
| 5 | [Monthly contact rate](05-monthly-contact-rate.md) | Of the Medicaid patients in metric 2, the share with both a clinical contact and a scored symptom scale this month | A percentage. Target: 80% or more |
| 6 | [Improvement rate](06-improvement-rate.md) | Of Medicaid patients with <!--rule:seventy-days.days-->70<!--/rule--> days or more in treatment and an elevated baseline, the share whose latest score on their primary scale meets NYS's improvement criteria | A percentage. Target: 60% or more |
| 7 | [Remission rate](07-remission-rate.md) | Of the Medicaid patients in metric 2, the share with an elevated baseline and a primary-scale score this month below the remission threshold (on the PHQ-9, below <!--rule:remission-thresholds.thresholds.phq9.below-->5<!--/rule-->) | A percentage. No target |
| 8 | [Psychiatric consultation rate](08-psychiatric-consultation-rate.md) | Of the patients in metric 6's denominator who haven't improved, the share whose case the psychiatric consultant reviewed in the <!--rule:psychiatric-case-review.window_days-->60<!--/rule--> days ending on the last day of the month | A percentage. Target: 80% or more |
| 9 | [Depression screening rate](09-depression-screening-rate.md) | Of patients <!--rule:who-should-be-screened.age_floor-->12<!--/rule--> or older with a qualifying medical visit this month, across the whole practice, the share with a PHQ-2 or PHQ-9 in the <!--rule:what-counts-as-screened.lookback_months-->12<!--/rule--> months ending this month | A percentage. Target: 85% |
| 10 | [Depression screening yield](10-depression-screening-yield.md) | Of patients across the practice whose first PHQ-9 in <!--rule:initial-phq-9.lookback_days-->365<!--/rule--> days was this month, those who scored <!--rule:nys.screening_yield_positive_at_or_above-->10<!--/rule--> or more | A count and a percentage. No target |
| 11 | [Care manager staffing (BHCM FTE)](11-bhcm-staffing.md) | The behavioral health care managers' time spent on CoCM this month, as full-time equivalents | A number such as 2.1, which the site attests |

## Who each metric covers

- **Metrics 1 to 8** are about the CoCM caseload. Metric 1 counts every payer; metrics 2
  to 8 count Medicaid patients only.
- **Metrics 9 and 10** are about the whole practice, every payer, not only CoCM patients.
  Their data comes from billing and the EHR, not the CoCM registry.
- **Metric 11** is about staff, not patients.

## How the rates fit together

- Metrics 5 and 7 share a denominator: every Medicaid patient enrolled this month, which
  is metric 2.
- Metric 8 picks up where metric 6 leaves off. Every patient in metric 6's denominator
  either improved, or goes on to metric 8's denominator.
- Dividing metric 1 by metric 11 gives patients per care manager. NYS's optimal caseload
  is more than 75 per full-time care manager.

The terms these rules use, such as enrolled, elevated baseline and primary scale, are
explained on the [concept pages](../start-here.md#the-concepts-the-metrics-share).
