# Hypothesis Log

One entry per hypothesis. Keep it short — status, finding, evidence link, open
questions. About two minutes per update. This is the team's shared memory: if it's
maintained, everyone picks up where the last person left off.

Copy the block below for each new hypothesis. Number them H-001, H-002, ...

---

## H-001 — [short title]

- **Status:** Proposed / Under analysis / Supported / Supported (weak) / Refuted / Inconclusive
- **Owner:** [name]
- **Date:** [YYYY-MM-DD]

**Hypothesis:** [what is being tested, in formal terms]

**Data & inputs:** [which PRO-ACT forms/columns; cohort definition and filters; final n]

**Method:** [the model or test, in one line — e.g. "mixed-effects model of ALSFRS-R slope"]

**Finding:** [the result — with effect size, n, and uncertainty, not just a p-value]

**Evidence:** [link to the script / commit / report that supports this]

**Open questions:** [what's unresolved; what to try next]

---

## Example (delete once you have real entries)

## H-024 — FVC vs ALSFRS-R progression slope

- **Status:** Supported (weak)
- **Owner:** Sarah
- **Date:** 2026-06-01

**Hypothesis:** Lower baseline FVC is associated with a faster ALSFRS-R decline
slope across the PRO-ACT cohort.

**Finding:** Spearman rho = -0.31 (n = 412 subjects with >= 3 timepoints,
p < 0.001). Effect is real but smaller than prior literature suggested.

**Evidence:** scripts/h024_fvc_slope.py + outputs/h024_report.pdf (commit abc123)

**Open questions:** Does the effect hold in the bulbar-onset subgroup? Re-run with
treatment group as a covariate.
