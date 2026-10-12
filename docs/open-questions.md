# Open questions

Only what is still open. Each measure question raised after draft v0.1 (Q-01 – Q-09)
now has a call in [`our-calls.md`](reference/our-calls.md), and each call lists the
question it replaces. Every call still needs approval.

## For NYS

| Question | Notes |
|---|---|
| Does the quarterly REDCap report want each month's numbers, or one number per quarter? | The guide counts each month. If OMH wants each month, a quarter is three monthly reports. If it wants one number per quarter, new enrollments and durations combine across months, but enrollment counts and rates need a quarter definition (unique patients, not three months added up). |
| Practices enrolling ADHD patients must also report a Vanderbilt completion rate. How is it defined? | It's in OMH's eligible diagnosis list, not the eleven metrics, so the guide doesn't count it yet. |
| What are the REDCap form's fields and the submission deadline? | The deadline may override the [15-day run lag](reference/our-calls.md#when-to-run-the-report). The calculator's output should match the form exactly. (Q-T5) |
| Does NYS want patient-level data, or only the eleven numbers? | Assumed: only the numbers. The patient-level detail stays at the site. (Q-T4) |
| Does NYS already use a remission definition at any site? | If so, it replaces our [remission thresholds](reference/our-calls.md#remission-thresholds). |

## For a clinician

Calls marked **Needs clinical sign-off** in [`our-calls.md`](reference/our-calls.md):

- Elevated-baseline thresholds for PCL-5, SCARED, PSC-17, SMFQ and NICHQ Vanderbilt.
- Remission thresholds for the same five scales, including the Vanderbilt symptom-count rule.

## To verify against a source

Things stated from memory, which is the mistake the archived review note R-14 warns
about:

- A spot-check of the [LOINC codes](reference/instruments.md#loinc-codes) on loinc.org,
  which blocks automated access. They were checked against the HL7 terminology server
  and the NLM's LOINC index.
- The PCL-5 cutoff against the National Center for PTSD's own guidance, and the GAD-7
  severity bands against Spitzer et al. (2006).
- The qualifying-visit code list, including the telehealth codes.

## To review with Virna Little

- **Should the billing codes that stand in for enrollment include G0568 and G0569?**
  The [CY 2026 Physician Fee Schedule final rule](https://www.federalregister.gov/documents/2025/11/05/2025-19787/medicare-and-medicaid-programs-cy-2026-payment-policies-under-the-physician-fee-schedule-and-other)
  (90 FR 49266, November 5, 2025) created them from January 1, 2026 as add-ons to
  Medicare's advanced primary care management (APCM) codes G0556–G0558. G0568 is based
  on 99492 (the first month of CoCM) and G0569 on 99493 (a later month). They have no
  time thresholds, and the APCM base code must be billed by the same practitioner in the
  same month. A practice billing APCM can use them in place of 99492 and 99493, so a
  site inferring enrollment from Medicare claims would miss those months without them.
  The rule's regulatory text (§ 425.400(c)(1)(x)(B)) labels G0568 and G0569 as general
  behavioral health integration and G0570 as CoCM, the reverse of the rule's preamble
  and CMS's [Behavioral Health Integration Services](https://www.cms.gov/files/document/mln909432-behavioral-health-integration-services.pdf)
  booklet. The guide follows the preamble and the booklet.

## The tooling

| ID | Question | Notes |
|---|---|---|
| Q-T1 | Which way in do we build first? | See the [tooling plan](tooling.md#what-to-build-first). |

## About the guide

| Question | Notes |
|---|---|
| Whose calls are these? | "Our call" needs an "our": SPiER, HTD, a named working group, or unattributed. |
| Who approves a call? | Every call is marked **approval needed**. Someone has to be able to approve it: the same group, a clinical lead for the calls that need clinical sign-off, or NYS itself. |
