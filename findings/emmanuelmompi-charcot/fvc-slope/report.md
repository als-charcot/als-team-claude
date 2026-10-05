<!-- Generated from report.pdf. The PDF is the typeset version; this is what prior-art checks read. -->

FVC & onset site as predictors of
ALSFRS-R decline in ALS
PRO-ACT cohort — bulbar declines faster and low baseline FVC predicts steeper
decline, both small effects

PRO-ACT (Pooled Resource Open-Access ALS Clinical Trials), de-identified

n = 5,394 subjects with a fittable ALSFRS-R slope (0-18 months)

Headline: bulbar -0.23 pts/mo faster (d=-0.25); FVC% vs slope r=0.21

Status: both hypotheses supported, effect sizes small, observational

Reproducibility: scripts/analysis.py, <1 min end-to-end

BOTH HYPOTHESES SUPPORTED — BUT EFFECT SIZES ARE SMALL; REPORT THEM AS SUCH

In 5,394 PRO-ACT patients with a fittable ALSFRS-R trajectory over their first 18 months,
bulbar-onset disease declines faster than limb-onset (-1.24 vs -1.01 points/month), and lower
baseline forced vital capacity (FVC, % predicted) predicts a steeper subsequent decline. Both
associations are highly significant given the large sample, yet both are modest in magnitude
(Cohen's d = -0.25; Pearson r = 0.21) and the individual distributions overlap heavily. These are
real, reproducible cohort patterns — not deterministic rules for an individual patient.

-0.23
pts/mo

d = -0.25

r = 0.21

Extra ALSFRS-R loss per month, bulbar vs limb
Mixed-model groupxtime interaction; 95% CI [-0.29, -0.16]; p = 6x10-13; n = 4,157.

Effect size, bulbar vs limb decline slope
"Small" by Cohen's convention; 95% CI [-0.33, -0.18]. Significant != large.

Baseline FVC% vs decline slope
Weak positive; p = 3x10-18, n = 1,766. Higher FVC -> slower decline.

fvc-slope — PRO-ACT ALSFRS-R decline analysis

Page 1

Hypotheses — formal statement & verdict

#

H1

H2

H3

Claim (formal)

Status

Mean ALSFRS-R decline slope differs
by onset site (bulbar != limb)

Supported — small effect

Baseline FVC (% predicted) is inversely
associated with decline slope

Supported — weak effect

The FVC->slope association survives
adjustment for age, sex, disease
duration, onset, riluzole

Supported (b essentially unchanged)

H1 (formal): H0: m(slope, bulbar) = m(slope, limb)  vs  H1: m(slope, bulbar) != m(slope, limb), where slope is
the per-subject OLS decline rate of ALSFRS-R (points/month) over months 0–18.

H2/H3 (formal): in the model  slope = b0 + b1(FVC%) + g(z) + e  (with e the error term), test H0: b1 = 0 —
first with covariates z = none (unadjusted), then with z = {age, sex, disease duration, onset, riluzole}.

Data sources & pipeline

Data — PRO-ACT (Pooled Resource Open-Access ALS Clinical Trials), de-identified

  (cid:127)  F_PROACT_ALSFRS — longitudinal ALSFRS-R total (0–48) with day offset ALSFRS_Delta; 51,947
scored visits.

  (cid:127)  F_PROACT_ALSHISTORY — site of onset (bulbar / limb flags + text); onset date for disease
duration.

  (cid:127)  F_PROACT_FVC — spirometry, pct_of_Normal (FVC % predicted), best of <=3 trials per visit.

  (cid:127)  F_PROACT_DEMOGRAPHICS / F_PROACT_RILUZOLE — age, sex, riluzole use (confounders).

  (cid:127)  Join key: subject_id. All reads from data/PROACT_ALL_FORMS/; nothing copied out.

Pipeline — one end-to-end script, `scripts/analysis.py`

1 Fit each subject's ALSFRS-R slope over months 0–18 (>=3 visits, >=90-day span; median 8
visits/subject).

2 Assign pure-Bulbar vs pure-Limb onset (subjects flagged both / neither excluded).
3 Take baseline FVC% (earliest visit, window -30 to +90 days).
4 Welch t, Mann–Whitney, Cohen's d (CI), linear mixed-effects groupxtime; OLS slope~FVC%,
unadjusted + adjusted.

fvc-slope — PRO-ACT ALSFRS-R decline analysis

Page 2

Finding F1 — Bulbar onset declines faster: -1.24 vs
-1.01 ALSFRS-R points/month

Mean ALSFRS-R trajectory over the first 18 months, bulbar vs limb onset, with 95% confidence bands.

SUPPORTED BY A MIXED-EFFECTS GROUPxTIME INTERACTION, P = 6x10-13

The two mean trajectories start together (~38/48) and separate progressively: the bulbar curve sits
below the limb curve from ~month 6 onward. The groupxtime interaction is -0.23 points/month
(95% CI [-0.29, -0.16]) — bulbar patients lose roughly 4 extra ALSFRS-R points over 18
months.

CLINICAL / MEDICAL
Bulbar-onset ALS begins in the brainstem motor nuclei governing speech and swallowing, and carries a
worse prognosis than limb onset in most cohorts — earlier respiratory and nutritional compromise
accelerate global functional loss captured by ALSFRS-R. The faster total-score decline here is consistent
with that clinical picture.

DATA-SCIENCE / STATISTICS
Per-subject OLS slopes: bulbar mean -1.244 (SD 0.97, n=930), limb -1.012 (SD 0.90, n=3,227). Welch t =
-6.51, p = 1.0x10-10; Mann–Whitney p = 3.7x10-13. The mixed model (random intercept + slope per
subject) confirms the difference isn't an artifact of unequal visit counts.

PLAIN ENGLISH
Think of two groups coasting downhill. Both start at the same height and both roll down, but the bulbar
group's hill is slightly steeper, so after a year and a half they've dropped noticeably lower. On average —
any single person can roll faster or slower than their group.

CONCRETE DATA EXAMPLE
Bulbar exemplar subject_id = 4453116: baseline ALSFRS-R 33, 14 visits, slope -1.065/mo. Limb exemplar
subject_id = 9971365: baseline 36, 7 visits, slope -0.833/mo — a slower drop, illustrating the group
tendency at the individual level.

fvc-slope — PRO-ACT ALSFRS-R decline analysis

Page 3

Finding F2 — The difference is statistically robust but
small: distributions overlap heavily

Per-subject decline-slope distributions by onset site (violin + box); dotted line marks zero/no-decline.

REAL BUT MODEST — COHEN'S D = -0.25 (SMALL); DO NOT OVER-INTERPRET

The group means differ, but the two slope distributions sit almost on top of each other. Cohen's d =
-0.25 (95% CI [-0.33, -0.18]) is a small effect: onset site shifts the average decline rate a little, and
explains only a sliver of the person-to-person variation in how fast ALS progresses.

CLINICAL / MEDICAL
Clinically, this cautions against using onset site alone to prognosticate an individual. Many limb-onset
patients decline faster than the average bulbar patient and vice versa; onset site is one weak axis among
many (age, respiratory status, rate of spread).

DATA-SCIENCE / STATISTICS
With n~=4,000, a tiny mean gap (0.23 pts/mo) yields p~=10-13 — a textbook case of the CLAUDE.md rule
that in large cohorts significance != importance. The honest summary is the effect size and its CI, not the
p-value. Both non-parametric (Mann–Whitney) and parametric tests agree, so the direction is solid.

PLAIN ENGLISH
Two overlapping crowds of runners: the bulbar crowd is on average a touch slower to the finish, but if you
pick one runner from each crowd you often can't tell which is which. The average difference is real; the
overlap is huge.

CONCRETE DATA EXAMPLE
Bulbar median slope -1.066/mo vs limb median -0.833/mo — a 0.23-point/month median gap, mirroring
the mean gap. The SDs (~0.9–0.97) are ~4x that gap, which is exactly why the violins overlap.

fvc-slope — PRO-ACT ALSFRS-R decline analysis

Page 4

Finding F3 — Lower baseline FVC predicts faster
decline, and it holds after adjustment

Baseline FVC (% predicted) vs subsequent ALSFRS-R decline slope, colored by onset; black line is the OLS fit.

SUPPORTED AND CONFOUNDER-ROBUST — ADJUSTED EFFECT UNCHANGED, P = 3E-14

Patients with lower baseline FVC% decline faster (more negative slope): Pearson r = 0.21 (95% CI
[0.16, 0.25]), n = 1,766. Each 10-point drop in baseline FVC% predicts ~=0.13 points/month
faster ALSFRS-R decline. Adjusting for age, sex, disease duration, onset site and riluzole leaves
the effect essentially unchanged (b 0.0118 -> 0.0135).

CLINICAL / MEDICAL
FVC indexes respiratory (diaphragm/accessory) muscle strength, the system whose failure drives ALS
mortality. A low baseline FVC signals disease that has already reached the respiratory motor pool,
plausibly marking a more aggressive or more advanced phenotype — hence the faster global functional
decline.

DATA-SCIENCE / STATISTICS
Unadjusted OLS: b = 0.0118 pts/mo per FVC% (95% CI [0.0092, 0.0145]), R2 = 0.042. Adjusted OLS
(n=1,150): b = 0.0135 (95% CI [0.0100, 0.0169]), p = 2.8x10-14, R2 = 0.136. The predictor is weak (R2
small) but stable under adjustment — consistent with an independent, not confounded, association.

PLAIN ENGLISH
Baseline breathing capacity is like the tread left on a tire: less tread at the start tends to mean a bumpier,
faster-worsening road ahead. It nudges the odds — it doesn't dictate the destination, since most of the
variation is still unexplained.

CONCRETE DATA EXAMPLE
Exemplar subject_id = 7511360: baseline FVC 69% predicted (low end) with a subsequent slope of -2.32
pts/mo — more than double the cohort-average decline, illustrating the low-FVC / fast-decline corner of the
scatter.

fvc-slope — PRO-ACT ALSFRS-R decline analysis

Page 5

What couldn't be refuted, and the caveats

Both hypotheses survived their tests

  (cid:127)  H1 (bulbar > limb decline) survives Welch t, Mann–Whitney, and a mixed-effects model — direction is
robust.
  (cid:127)  H2/H3 (low FVC -> faster decline) survives confounder adjustment with a stable b — the association
is not explained by age, sex, disease duration, onset, or riluzole.

What these results are NOT
  (cid:127)  Not large. Both effects are small (d = -0.25; r = 0.21). Neither is an individual-level predictor.
  (cid:127)  Not causal. This is observational cohort data — it confirms patterns, it does not prove that bulbar
physiology or low FVC cause faster decline (per CLAUDE.md rule 2).

  (cid:127)  Not survivorship-free. Slopes are conditioned on >=3 visits in 18 months; the fastest-progressing
patients (early dropout/death) are under-represented, likely attenuating both effects.

Methodology-pitfall checklist (references/methodology_pitfalls.md)

Circularity: avoided — groups defined by onset/FVC, outcome is an independent slope. Confounders:
adjusted (age, sex, disease duration, onset, riluzole). Survivorship: acknowledged (18-mo window,
>=3-visit filter). Multiple testing: only 3 pre-specified hypotheses; no fishing. Causal overreach:
explicitly hedged.

Open questions for external review

 Q1

 Q2

Is the >=3-visit / 18-month filter attenuating the true bulbar effect?
Fast progressors drop out earliest. A joint (survival + longitudinal) model might recover a
larger bulbar–limb gap. Worth a sensitivity analysis with an inverse-probability-of-dropout
weight.

Should FVC% and onset be combined into one prognostic model?
Each is weak alone; a multivariable slope model (FVC% + onset + baseline ALSFRS-R +
age) might reach useful prognostic R2. Do you want that as a follow-up?

Reproducibility — runs end-to-end on a laptop

  (cid:127)  1 script — projects/manu/fvc-slope/scripts/analysis.py (~300 lines), venv + requirements.txt pinned.

  (cid:127)  3 figures (PNG + interactive HTML), 1 results.json, 1 subject-level CSV (local only).

  (cid:127)  Reads data/PROACT_ALL_FORMS/; runtime < 1 minute. Re-run: python scripts/analysis.py.

fvc-slope — PRO-ACT ALSFRS-R decline analysis

Page 6


