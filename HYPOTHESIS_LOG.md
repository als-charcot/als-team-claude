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

---

## H-002 — Blood neurofilament light chain (NfL) vs ALSFRS-R decline slope and survival

- **Status:** Supported (H1, primary); H2 (survival) Inconclusive — not adequately testable
- **Owner:** Manu
- **Date:** 2026-09-07 (closed 2026-09-07)

**Hypothesis:** In PRO-ACT, (1) higher baseline serum **NfL** is associated with a faster
(more negative) **ALSFRS-R** decline slope; and (2) higher baseline **NfL** is associated with
shorter survival. Secondary: test whether the NfL↔slope association differs above vs below a
61 pg/mL cutoff.

**Motivation (outside claim, recorded per research-watch):** medRxiv **preprint — NOT peer
reviewed**, Arguedas et al., "Predictive ALS survival using ALSFRS-R slope & NfL: insights
from the ALS/MND Natural History Consortium data and biofluid collection" (2026-08-10, n=300).
Reports plasma NfL correlated with ALSFRS-R average rate of change **r = −0.53 (95% CI −0.62 to
−0.42)**, association differing at a **61 pg/mL** cutoff. <https://doi.org/10.64898/2026.08.06.26359910>.
This is a hypothesis to test in our data, not a finding.

**Dataset:** PRO-ACT, `data/PROACT_ALL_FORMS` (local distribution snapshot). Note the outside
claim used **plasma** NfL; PRO-ACT NfL is **serum** — matrix/assay differences mean the absolute
61 pg/mL cutoff may not transfer, so it is tested as a robustness check, not assumed.

**Cohort & inputs:** `F_PROACT_Neurofilament` (serum NfL, pg/mL, `Collection_Delta`; serum only,
baseline = earliest draw 0–90 d), `F_PROACT_ALSFRS` (`ALSFRS_R_Total`, `ALSFRS_Delta` →
per-subject slope, reusing the H-001 definition: ≥3 visits, ≥90-day span, first 18 months),
`F_PROACT_DEATHDATA`, with age/sex/onset/disease-duration/baseline-ALSFRS-R as covariates.
**Riluzole dropped** (no "No" rows in this cohort → trial-presence flag, not a treatment
contrast). Join on `subject_id`. **Primary cohort n = 788** (serum-baseline NfL ∩ fittable slope).

**Method:** Spearman (headline) + Pearson(log-NfL) vs slope with bootstrap/Fisher-z CIs;
5,000-shuffle permutation negative control; OLS unadjusted/adjusted + a precision-weighted (WLS)
re-estimation for the generated-regressor structure; partial correlation controlling disease
duration; 61 pg/mL split as illustration. Cox for NfL→death (exploratory). Effect sizes reported
throughout.

**Finding (H1, SUPPORTED):** Higher baseline serum NfL → faster ALSFRS-R decline. **Spearman
ρ = −0.43 (95% CI [−0.48, −0.37]), n = 788, permutation p = 2×10⁻⁴.** Survives adjustment
(β = −0.47 [−0.62, −0.32], n = 365; −0.51 [−0.62, −0.40] on the less-selected n = 734) and
precision-weighting (β = −0.46 [−0.51, −0.40]); partial r = −0.35 controlling disease duration.
Direction replicates the motivating plasma preprint (r = −0.53), attenuated as expected for serum.
**Observational; the cohort is limb-enriched and faster-progressing (a single/few-substudy frame),
so it generalises to that population, not ALS at large.**

**Finding (H2, INCONCLUSIVE — not testable here):** NfL↔survival cannot be estimated in PRO-ACT:
only 114 NfL subjects have a death record and **all 114 died (0 censored)** — a decedent-only,
collider-selected linkage. The within-decedent Cox HR (1.24, 95% CI [1.00, 1.54], p = 0.05) is
null on its own terms and is not a mortality hazard ratio.

**Adversarial review (closed the experiment; 4 independent lenses, fresh contexts):**
- **Confounding:** HOLDS — survives adjustment + partial correlation; NfL not a mere duration proxy.
- **Survivorship:** HOLDS — selection biases ρ *toward the null*, so −0.43 is conservative.
- **Statistics:** HOLDS for the rank correlation; β *magnitude* specification-dependent; cutoff/Cox demoted.
- **Reproducibility:** HOLDS — byte-identical re-runs; every number ties to the pipeline (`claims.json`, 14/14).
- **Withdrawn/demoted:** "adjusted for riluzole" (withdrawn); 61 pg/mL as independent evidence (demoted to
  re-expression); Cox mortality HR (demoted to collider-biased within-decedent rank); "max 27,212 pg/mL"
  (corrected → 840, was an excluded CSF outlier).

**Evidence:** `projects/manu/nfl-alsfrs-slope/` — `scripts/analysis.py`, `outputs/report.md` (+ PDF),
`fig1`–`fig4`, `claims.json`, `results.json`. Local, not yet promoted.

**Open questions:** Does the association hold in a bulbar-onset cohort (absent here)? Can a
longitudinal NfL slope (798 subjects have ≥2 draws) outperform baseline NfL? Would linkage to a
cohort with censored survival make H2 testable? Is the serum→plasma cutoff mapping recoverable?

