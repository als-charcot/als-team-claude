# Hypothesis Log — ALS team

The team's shared memory. One short entry per finding: status, the result **with effect size
and n**, a link to the evidence, and what's still open. About two minutes to write.

**You don't edit this by hand.** When you share work ("share this work with the team"),
Claude appends your entry automatically. Format reference:
[`templates/HYPOTHESIS_LOG_TEMPLATE.md`](templates/HYPOTHESIS_LOG_TEMPLATE.md).

Negative and inconclusive results belong here too — a logged dead end saves the next person
weeks of repeating it.

Entries are numbered H-001, H-002, … newest at the bottom.

---

<!-- New entries are appended below this line. -->

## H-001 — ALSFRS-R decline by onset site, and baseline FVC as a predictor

- **Status:** Supported (weak)
- **Owner:** Manu
- **Date:** 2026-08-24

**Hypothesis:** (1) Mean ALSFRS-R decline slope differs by onset site (bulbar ≠ limb);
(2) lower baseline FVC (% predicted) is associated with a faster ALSFRS-R decline slope,
including after confounder adjustment.

**Data & inputs:** PRO-ACT forms `F_PROACT_ALSFRS`, `F_PROACT_ALSHISTORY`, `F_PROACT_FVC`,
`F_PROACT_DEMOGRAPHICS`, `F_PROACT_RILUZOLE` (join on `subject_id`). Cohort: ≥3 ALSFRS-R
visits spanning ≥90 days within the first 18 months. n = 5,394 with a fittable slope
(930 bulbar, 3,227 limb; 1,766 with baseline FVC%).

**Method:** Per-subject OLS ALSFRS-R slope (pts/month). Bulbar vs limb: Welch t, Mann–Whitney,
Cohen's d, and a linear mixed-effects model (group×time). FVC→slope: OLS, unadjusted and
adjusted for age, sex, disease duration, onset, riluzole.

**Finding:** Bulbar declines faster (−1.24 vs −1.01 pts/mo; mixed-model group×time −0.23,
95% CI [−0.29, −0.16], p = 6e-13) but the effect is small — **Cohen's d = −0.25** [−0.33, −0.18],
distributions overlap heavily. Lower baseline FVC% predicts faster decline: **Pearson r = 0.21**
[0.16, 0.25], n = 1,766; adjusted β = 0.0135 pts/mo per FVC-point (p = 2.8e-14), stable under
adjustment (adj. R² ≈ 0.14). Both real, both weak; observational.

**Evidence:** `findings/manu/fvc-slope/` — report.pdf, analysis.py, 3 figures, README.

**Open questions:** Does a joint survival + longitudinal model (correcting for early-dropout
survivorship) recover a larger bulbar–limb gap? Does combining FVC% + onset + baseline
ALSFRS-R + age reach useful prognostic R²?

