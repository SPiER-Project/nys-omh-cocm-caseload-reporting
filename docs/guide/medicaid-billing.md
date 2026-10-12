# NYS Medicaid billing for Collaborative Care

How a certified practice bills New York State Medicaid for Collaborative Care, summarized
from OMH's billing guidance (updated June 2025, with changes effective September 1,
2025). It's here because billing and reporting draw on the same records, and a billing
lead and a program lead need the same picture.

This is a summary, not billing advice. The rules and rates change; check the current
guidance with OMH at NYSCollaborativeCare@omh.ny.gov before submitting claims. This guide
is an independent project, not an OMH product.

## Who can bill

Practices certified in the NYS Collaborative Care Medicaid Program
([about the program](about-the-program.md)), from the effective date OMH gives them.
Article 28 clinics submit institutional claims; non-Article 28 practices (group practices
and private practitioners) submit professional claims.

## Which patients

**Medicaid patients with an eligible diagnosis.** Collaborative Care is carved out of
Medicaid managed care, so claims for every Medicaid patient, managed care members
included, go directly to fee-for-service Medicaid.

The eligible diagnoses (OMH's 2024 ICD-10 code list):

| Condition | ICD-10 codes |
|---|---|
| Depression | F32.0–F32.5, F32.9, F32.A, F32.81 (premenstrual dysphoric disorder), F33.0–F33.3, F33.41, F33.42, F33.9, F34.1 (dysthymia), F06.30 (mood disorder due to another condition) |
| Perinatal | O99.340–O99.343, O99.345 (mental disorders complicating pregnancy or the puerperium), F53 (puerperal psychosis), N94.3 (premenstrual tension syndrome) |
| Anxiety | F41.0, F41.1, F41.3, F41.8, F41.9, F40 and F40.1, F40.10, F40.11, F40.8, F40.9 (phobic anxiety disorders) |
| Trauma | F43.0 (acute stress reaction), F43.1, F43.10, F43.11, F43.12 (PTSD) |
| Suicide risk | Z91.5 (personal history of self-harm), R45.851 (suicidal ideation) |
| ADHD, ages 6–18 only | F90.0, F90.1, F90.2, F90.9 |

The list gives the recurrent mild depression code as "F33"; F33.0 is the billable code
for it. Practices enrolling patients with ADHD must also report a **Vanderbilt
completion rate** with the quarterly report.

**Dual Medicare–Medicaid patients:** Medicaid pays last. Bill Medicare first with the
CPT codes below, then Medicaid, showing what Medicare paid. A month billed with T2022,
which Medicare doesn't accept, can be zero-filled and sent straight to Medicaid.

## What a billable month needs

For each patient, each calendar month:
- **at least one clinical contact,** in which treatment is delivered and documented in
  the chart. It can be in person, a group session, or by phone if treatment is delivered;
- **at least one validated symptom-monitoring scale,** recorded in the registry;
- the patient managed in a state-approved registry;
- the BHCM consulting a psychiatric consultant for an hour or more each week about
  enrolled patients. The consultant can't bill Medicaid for that consultation.

These are the same two things [metric 5](metrics/05-monthly-contact-rate.md) counts: a
month that meets them is a month of active treatment.

## Which code

The code depends on the care team's total Collaborative Care time in the month:

| Code | When | Rate (from September 1, 2025) |
|---|---|---|
| 99492 | The first month of care, with at least 70 minutes | $172.97 |
| 99493 | Any later month, with at least 60 minutes | $172.97 |
| T2022 | A month below those minutes. There's no minimum time for T2022 | $172.97 |
| 99494 | An add-on for at least 30 minutes beyond the 70 or 60 (90 minutes or more in total). One per patient per month, and never with T2022 | $86.48 |

## How to claim

- **Date of service:** the last day of the month. If the patient's Medicaid eligibility
  ends during the month, use their last day of eligibility.
- **Article 28, institutional claims** (837i or UB-04):
  - value code 24 followed by the rate code, for example `245246`;
  - rate code **5246**, the monthly case payment, with the procedure code on the line;
  - for the add-on, a second, separate claim with rate code **5261** and procedure code
    99494;
  - rate codes 5247, 5248 and 5249 are no longer paid.
- **Non-Article 28, professional claims** (837p or CMS-1500):
  - the procedure codes only, since professional claims carry no rate codes;
  - the directing primary care provider's NPI as attending provider, plus a
    Medicaid-enrolled referring provider if the attending isn't enrolled;
  - the billing provider needs specialty code **333** on their provider file, which OMH
    adds during certification;
  - Service Authorization Exception Code **7** (special handling), in box 25D of the
    eMedNY 150003 form.

## Limits

- **24 months of Collaborative Care per patient,** not necessarily in a row. The limit
  resets after six months without a service. Most patients improve and are discharged
  within nine months.
- **Timely filing: 90 days** from the date of service. Later claims need OMH's prior
  approval to use delay reason code 3, and must then be submitted within 30 days of the
  approval letter.
- **Earlier rules that no longer apply** (from September 1, 2025): the 25% retainage, the
  12-month limit, and the separate year-two rate.

## Billing other services alongside

The monthly case payment can sit alongside separately billed services, but time spent on
those services can't count toward the Collaborative Care minutes:
- **FQHCs:** the PPS rate for face-to-face counseling by a psychiatrist, licensed
  psychologist or licensed social worker.
- **Article 28 clinics:** a separate claim with the appropriate APG rate code for a
  psychiatrist's or licensed psychologist's services. A licensed social worker's
  face-to-face service to a pregnant woman or a child in the program uses special rate
  codes instead of APGs; the guidance lists 4222, 4223 and 4224.
- **Private practitioners:** a separate professional claim for services within their scope.

Patients enrolled in a health home can also receive Collaborative Care.

## Examples from the guidance

| Month | What happened | Article 28 claim |
|---|---|---|
| January, the first month | Enrolled January 10 after a 50-minute assessment; a 15-minute call; 75 minutes in all | January 31, rate code 5246, 99492 |
| April, a later month | One 15-minute call with a PHQ-9; under 60 minutes | April 30, rate code 5246, T2022 |
| June, a later month | 90 minutes across three contacts | Two claims for June 30: rate code 5246 with 99493, and rate code 5261 with 99494 |

## How billing relates to reporting

- **Billed months aren't the same as enrolled months.** A patient stays enrolled in a
  month with no billable contact; the guide counts enrollment from the registry, not from
  claims ([what counts as enrolled](../reference/our-calls.md#what-counts-as-enrolled)).
- **Managed care members are Medicaid patients** for both billing and reporting, which
  matches the guide's [Medicaid call](../reference/our-calls.md#who-counts-as-medicaid).
- **A billable month is a month of active treatment** for metric 5: one clinical contact
  and one symptom scale.

## Sources

| Document | Date | Where |
|---|---|---|
| Medicaid Collaborative Care Program Billing Guidance (OMH and DOH) | Updated June 2025 | [Linked from the AIMS Center's NYS page](https://aims.uw.edu/nyscc/medicaid/) |
| Billing Guidance: Summary of Updates (rates) | Effective September 1, 2025 | [OMH, hosted by the AIMS Center](https://aims.uw.edu/nyscc/wp-content/uploads/2025/06/Updates-Medicaid-Collaborative-Care-Program-Eff.-9.1.25.docx) |
| Eligible diagnosis code list | 2024 | [Linked from the AIMS Center's NYS page](https://aims.uw.edu/nyscc/medicaid/) |
| NYS Medicaid Collaborative Care Provider Certification Overview | August 2025 | [OMH, hosted by the AIMS Center](https://aims.uw.edu/nyscc/wp-content/uploads/2025/11/NYS-CCMP-Provider-Certification-Overview-8.22.25.pdf) |
| eMedNY: submitting claims over 90 days old | — | [eMedNY](https://www.emedny.org/HIPAA/QuickRefDocs/FOD-7001_Sub_Claims_Over_90_days_Old.pdf) |
