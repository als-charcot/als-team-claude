# fvc-slope — ALSFRS-R decline by onset site, and baseline FVC as a predictor

**Owner:** Manu · **Date:** 2026-08-24 · **Cohort:** PRO-ACT (de-identified)

## Questions

1. Does **ALSFRS-R** decline faster in **bulbar-onset** than **limb-onset** ALS?
2. Does **lower baseline FVC (% predicted)** predict a steeper subsequent decline?

## Data & inputs

- **Forms:** `F_PROACT_ALSFRS` (ALSFRS-R total over `ALSFRS_Delta`), `F_PROACT_ALSHISTORY`
  (site of onset; onset date), `F_PROACT_FVC` (`pct_of_Normal`, best of ≤3 trials),
  `F_PROACT_DEMOGRAPHICS`, `F_PROACT_RILUZOLE` (confounders). Join key `subject_id`.
- **Cohort:** subjects with ≥3 ALSFRS-R visits spanning ≥90 days within the first 18 months.
  **n = 5,394** with a fittable slope (930 pure-bulbar, 3,227 pure-limb; 1,766 with baseline FVC%).

## Method

Per-subject OLS ALSFRS-R decline slope (points/month). Bulbar vs limb: Welch *t*,
Mann–Whitney, Cohen's *d* (CI), and a linear mixed-effects model (random intercept + slope)
for the group×time interaction. FVC→slope: OLS regression, unadjusted and adjusted for age,
sex, disease duration, onset site, and riluzole.

## Findings (both real, both small)

- **Bulbar declines faster:** −1.24 vs −1.01 ALSFRS-R pts/month; mixed-model group×time
  = **−0.23 pts/mo** (95% CI [−0.29, −0.16], p = 6×10⁻¹³). **Cohen's d = −0.25 (small)**,
  CI [−0.33, −0.18] — distributions overlap heavily; not an individual-level predictor.
- **Lower baseline FVC% → faster decline:** Pearson **r = 0.21** (95% CI [0.16, 0.25],
  n = 1,766). Adjusted β = 0.0135 pts/mo per FVC-point (p = 2.8×10⁻¹⁴), essentially
  unchanged from unadjusted — stable under confounder adjustment; adjusted R² ≈ 0.14.

## Caveats

Observational — patterns, not proven mechanisms. Effects are small despite tiny p-values
(large-n cohort). The ≥3-visit / 18-month filter under-represents the fastest progressors
(early dropout/death), likely **attenuating** both effects.

## Re-run

```
python analysis.py     # reads data/PROACT_ALL_FORMS/, writes figures + results.json
```

Needs `pandas numpy scipy statsmodels plotly kaleido` (Python 3.11+). The report PDF is
built from `outputs/REPORT.md` with the `polished-pdf-reports` skill renderer.
