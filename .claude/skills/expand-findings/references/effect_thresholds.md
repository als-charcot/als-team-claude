# The margin registry: the effect we would not want to miss

Every precision report needs one number a human has to decide: **Δ\*, the smallest effect
that would matter clinically.** Without it, "we found nothing" cannot be told apart from "we
could not have seen anything", and that distinction is the entire point of the exercise.

**This file is the gate.** `precision_report.py` reads it and **refuses to run** on any row
that is not marked `CONFIRMED` with a real source. That refusal is deliberate: a margin
chosen after seeing the data is not a margin, it is a rationalisation.

## Every row below ships as NEEDS-CITATION on purpose

The values are the ones commonly used as anchors in ALS work, and the reasoning for each is
given. **But they arrived here without verified provenance, so none of them is usable yet.**
Filling in the source is a clinical judgement for this team, not something to be assumed.

**To confirm a row:** replace `NEEDS-CITATION` with `CONFIRMED`, and replace the citation
field with the actual source — a paper, a trial's powering assumption, or a written team
decision with a date. Then the tool will use it.

Keep the table format exactly as-is; the parser reads the pipe-delimited columns in order:
`key | scale | delta_star | direction | status | citation`

| key | scale | delta_star | direction | status | citation |
|---|---|---|---|---|---|
| alsfrs_slope | points/month (ALSFRS-R, 0-48) | 0.30 | lower is worse | NEEDS-CITATION | anchor: a third of a point per month is roughly the difference trials have been powered to detect over 6-12 months |
| alsfrs_total_change | points (ALSFRS-R, 0-48) | 2.0 | lower is worse | NEEDS-CITATION | anchor: commonly treated as the minimum clinically important difference on the 48-point scale |
| alsfrs_slope_40pt | points/month (old ALSFRS, 0-40) | 0.25 | lower is worse | NEEDS-CITATION | the 40-point and 48-point scales are NOT interchangeable; needs its own margin |
| fvc_pct_slope | % predicted/month | 1.0 | lower is worse | NEEDS-CITATION | anchor: respiratory decline rate used in trial powering |
| fvc_pct_change | % predicted | 5.0 | lower is worse | NEEDS-CITATION | anchor: threshold often treated as clinically relevant for respiratory function |
| survival_hr | log hazard ratio | 0.18 | HR < 1 is better | NEEDS-CITATION | log(0.83); an ~17% hazard reduction is near the effect claimed for approved therapy |
| survival_months | months | 3.0 | higher is better | NEEDS-CITATION | anchor: roughly the survival benefit attributed to existing approved treatment |
| time_to_milestone_hr | log hazard ratio | 0.18 | HR < 1 is better | NEEDS-CITATION | as survival_hr, for time to a functional milestone |
| nfl_pct_change | % change in serum NfL | 15.0 | lower is better | NEEDS-CITATION | biomarker margin; needs a source or an explicit team decision |
| cohens_d | standardised mean difference | 0.20 | context dependent | NEEDS-CITATION | conventional small-effect anchor; prefer a scale-specific margin where one exists |

## Choosing a margin honestly

- **Pick it before you look.** If the analysis has already been run, say so in the citation
  field ("team decision 2026-09-07, set after the first null"), because a reader deserves to
  know the margin was chosen with the result visible.
- **Make it the effect you would act on**, not the effect you hope to find. The question Δ\*
  answers is "how small an effect would still change what we do next?"
- **Scale it to the analysis window.** A margin drawn from a 24-week trial is not the same
  margin for a 24-month observational slope. Rescale it and say so.
- **Match the estimand.** A margin on an ALSFRS-R total change is not a margin on a slope, and
  a margin on the 48-point scale is not a margin on the 40-point one. PRO-ACT pools both.
- **Hazard and odds ratios go on the log scale.** The registry stores the log value; pass the
  ratio with `--log-scale` and the tool converts.

## Why the tool is this strict

Under pressure to find something, a soft margin quietly becomes whatever makes the result look
interesting. Two specific abuses this refuses:

1. **The shrinking margin.** A null is uninformative at Δ\* = 0.30, so Δ\* becomes 0.60 and the
   null becomes a "lead". The registry is versioned in git, so a changed margin is visible in
   the history rather than invisible in a rerun.
2. **The invented margin.** `--delta-star` on the command line is allowed, but only with
   `--i-am-registering-this`, and the output is stamped `UNREGISTERED` and **cannot support a
   closed door**. An ad-hoc margin can open a question; it can never close one.
