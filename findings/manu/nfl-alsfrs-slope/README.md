# H-002 — Blood neurofilament light chain (NfL) vs ALSFRS-R decline slope (PRO-ACT)

**Owner:** Manu · **Dataset:** PRO-ACT (`data/PROACT_ALL_FORMS`, local snapshot) · **Date:** 2026-09-07

## Question

Does higher baseline blood **NfL** go with faster **ALSFRS-R** decline in PRO-ACT — and does it
predict survival? Motivated by a medRxiv **preprint** (Arguedas et al., ALS/MND NHC, n=300;
plasma NfL vs ALSFRS-R rate of change r = −0.53, 61 pg/mL cutoff). Tested here on **serum** NfL
in an independent, larger cohort.

## Finding

**H1 — Supported.** Higher baseline serum NfL correlates with a faster ALSFRS-R decline slope:
**Spearman ρ = −0.43 (95% CI [−0.48, −0.37]), n = 788, permutation p = 2×10⁻⁴.** Holds after
adjustment (β = −0.47 per log-unit NfL, n = 365; −0.51 on the less-selected n = 734) and under
precision-weighting (β = −0.46); partial r = −0.35 controlling disease duration. Direction
replicates the plasma preprint (−0.53), attenuated as expected for serum.

**H2 (survival) — Inconclusive, not adequately testable.** Only 114 NfL subjects have a death
record and **all 114 died (0 censored)** — a decedent-only, collider-selected linkage. The Cox
restatement (HR = 1.24 per SD log-NfL, 95% CI [1.00, 1.54], p = 0.05) is null on its own terms and
is **not** a mortality hazard ratio.

## Caveats

- **Observational** — NfL and ALSFRS-R decline are two readouts of the same axonal degeneration
  (shared cause), not evidence NfL drives progression.
- **Non-representative cohort** — limb-onset-enriched, near-bulbar-free, faster-progressing; the
  specific legacy trials that assayed NfL, not ALS at large. Absolute NfL and the 61 pg/mL cutoff
  are likely assay/trial-specific (serum here, plasma in the preprint).
- **β magnitude is specification-dependent** (the outcome is itself an estimated slope —
  generated-regressor structure); the rank correlation is robust, the coefficient magnitude less so.
- **Survivorship in the slope** (≥3 visits over ≥90 days) under-represents the fastest progressors,
  biasing H1 **toward zero** — so ρ = −0.43 is a conservative floor.

## Adversarial review (closed the experiment)

Four independent reviewers, fresh contexts, one lens each — **confounding, survivorship,
statistics, reproducibility**. The primary rank association held on all four. Demoted/withdrawn:
"adjusted for riluzole" (withdrawn — trial-presence flag, not a treatment contrast); the 61 pg/mL
cutoff as independent corroboration (demoted to a re-expression); the Cox mortality HR (demoted to a
collider-biased within-decedent rank association); "max 27,212 pg/mL" (corrected → 840, an excluded
CSF outlier). See the report's *Withdrawn / demoted claims* section.

## How to re-run

```
projects/manu/nfl-alsfrs-slope/.venv/Scripts/python.exe projects/manu/nfl-alsfrs-slope/scripts/analysis.py
```

Reads `data/PROACT_ALL_FORMS/` (serum NfL, ALSFRS-R, death, demographics, ALS history); writes
`results.json` and figures. Deterministic (RNG seed 20260907 for the bootstrap CI and the
5,000-shuffle permutation). A standing gate (`claims.json`, kept in the project folder) ties every
headline number in the report to the pipeline output (14/14). `analysis.py` here is the exact
end-to-end script; figures `fig1`–`fig4` are the promoted PNGs.
