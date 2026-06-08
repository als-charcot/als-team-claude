# Methodology Pitfalls — Checklist for Cohort / Observational Findings

Before accepting any cohort-style finding from PRO-ACT (or similar observational
data), verify that NONE of the following are present. Each has produced false,
"too-good-to-be-true" results in real ALS analyses.

1. **Circular / tautological design.** Cohorts defined by an outcome, then compared
   on that same outcome (e.g., grouping patients by decline rate, then "finding"
   they differ in decline rate). The result is built into the design.

2. **No confounder adjustment.** Age, sex, disease duration, site of onset, and
   treatment status are missing from the model. Raw group differences may reflect
   these confounders rather than the variable of interest.

3. **Survivorship bias.** The analysis is conditional on subjects still alive or
   still enrolled, which systematically distorts longitudinal estimates.

4. **Healthy-user bias.** In medication comparisons, users may be healthier (or
   sicker) at baseline than non-users for reasons unrelated to the drug. Compare
   baselines before attributing differences to treatment.

5. **Buggy multiple-testing / FDR correction.** Verify the correction is implemented
   correctly and applied to the right family of tests. A broken FDR step
   manufactures significance.

6. **Observational-to-causal overreach.** Interpreting a correlation in cohort data
   as a proven mechanism. Cohort data can confirm a pattern and make a hypothesis
   leading; it cannot prove causation on its own.

---

**Useful pattern:** when checking a surprising result, examine multiple failure
modes in parallel — run confounders, survivorship, healthy-user effects, and the
multiple-testing step each as a separate pass, rather than trusting a single
clean-looking result.
