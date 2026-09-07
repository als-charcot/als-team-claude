# The PRO-ACT instrument-failure catalogue

Ways a cohort analysis produces a confident number that means nothing. Run this against any
finding before it is shared. Each entry: the failure, how it looks from the inside, and the
test that exposes it.

---

## A. The cohort that is not the cohort

### A1 — Two definitions of the same cohort diverge
The script filters `>= 3 visits` in one place and `>= 3 visits spanning >= 90 days` in
another. Both report "n = 5,394". One of them is wrong and neither errors.
**Test:** print n at every filtering step and reconcile the funnel by hand. Every drop must
have a stated reason.

### A2 — A stable n with an unstable set
The count is identical across runs, so it looks settled, while membership changes because a
join reorders or a tie is broken differently.
**Test:** hash the sorted `subject_id` list, not just its length. Compare hashes across runs.

### A3 — Subjects excluded by a metadata side effect
A subject drops out because a covariate used for adjustment is missing, not because they
failed a stated criterion. The exclusion is invisible in the written method.
**Test:** compare n before and after the model call. Any silent loss is an unstated
exclusion criterion, and must be reported.

### A4 — The join multiplies rows
A one-to-many join on `subject_id` (several visits, several drug records) inflates the
effective n, so every standard error shrinks.
**Test:** assert one row per subject before any per-subject statistic. Count distinct
`subject_id` and compare with `len(df)`.

---

## B. The check that cannot fail

### B1 — A check over an empty set reports success
A validation loop over a filtered frame that is empty passes trivially.
**Test:** assert the frame is non-empty before asserting anything about its contents.

### B2 — A regex or lookup that silently matches nothing
A caption check whose pattern no longer matches the reworded sentence passes forever.
**Test:** a pattern with zero matches is a hard failure. `claim_audit.py` enforces this.

### B3 — A negative result with no positive control
"No association" is reported by a pipeline that has never demonstrated it can detect one.
**Test:** inject a known synthetic effect and confirm the pipeline recovers it. If it cannot,
the null is uninformative.

---

## C. The number that is a property of its own criterion

### C1 — A slope fitted through too few points
An ALSFRS-R slope from 3 visits over 8 weeks is dominated by measurement noise, yet enters
the analysis with the same weight as a slope from 12 visits over 2 years.
**Test:** report the distribution of visit counts and follow-up span. Re-run weighting by
follow-up, or restricted to well-observed subjects, and see whether the effect survives.

### C2 — A threshold cut through a continuum
"Fast progressors" defined at a slope cut-off that was chosen after seeing the data.
**Test:** re-run across a range of thresholds. An effect that exists only near one cut-off is
a property of the cut-off.

### C3 — A floor or ceiling effect read as biology
ALSFRS-R sub-scores bottom out at zero. Once a domain is at floor, decline stops being
measurable, and the slope flattens for a reason that is not clinical improvement.
**Test:** exclude or model the at-floor period; check whether the flattening moves with it.

### C4 — A capped field read as a complete list
A concomitant-medication or history field truncated at N entries, read as if it enumerated
everything.
**Test:** check the distribution of entries per subject for a suspicious ceiling.

---

## D. Who had to survive to appear

### D1 — Survivorship in the outcome definition
A per-subject decline slope requires enough surviving visits to fit. The fastest progressors
die or drop out before contributing one, so they are absent from the very quantity meant to
describe them.
**Test:** compare baseline characteristics of subjects with and without a fittable slope. If
they differ, the analysed cohort is not the enrolled cohort. Consider a joint
longitudinal-survival model.

### D2 — Immortal time from a time-varying exposure
Treating "on drug" as a fixed baseline attribute assigns pre-exposure survival to the exposed
group.
**Test:** align time zero to exposure start; model the exposure as time-varying.

### D3 — Prevalent-user bias
Subjects already established on a treatment at enrolment have, by definition, tolerated it and
survived to enrolment.
**Test:** restrict to incident users, or state the bias explicitly and stop short of a causal
reading.

### D4 — Missing not at random
Baseline FVC is missing more often in sicker or bulbar-onset subjects, so a
complete-case analysis silently selects a healthier cohort.
**Test:** compare characteristics of missing vs present. Report the missingness rate beside
every n. Consider multiple imputation, or restrict and say so.

---

## E. The statistic that answers a different question

### E1 — A tiny p-value from a large n
With thousands of subjects, a clinically meaningless difference reaches p < 0.001.
**Test:** the effect size and its interval decide, never the p-value. If the effect size is
not in the sentence, the sentence is not a finding. (This is also a `CLAUDE.md` rule.)

### E2 — Repeated measures treated as independent
Multiple visits per subject inflate the effective sample size and shrink every interval.
**Test:** account for clustering (mixed-effects or per-subject summaries). Compare intervals
under both to see how much was borrowed.

### E3 — Adjustment on a collider or a mediator
Adjusting for something caused by both exposure and outcome, or on the causal path, can
create or erase an association.
**Test:** state the assumed causal structure before choosing covariates. Report unadjusted
and adjusted side by side.

### E4 — Multiple testing across forms and subgroups
Sweeping many candidate predictors across many forms guarantees findings.
**Test:** state how many comparisons were made, control the false discovery rate, and report
the pre-specified hypothesis separately from the exploratory sweep.

### E5 — In-sample fit reported as predictive performance
R² on the data used to fit is not prediction.
**Test:** hold out, or cross-validate, and report the out-of-sample number.

### E6 — A subgroup effect without an interaction test
"Significant in bulbar onset, not in limb" with no test of whether the two differ.
**Test:** fit the interaction. Two different p-values are not a difference.

### E7 — Correlation reported in causal language
"Predicts", "drives", "slows" applied to an observational association.
**Test:** every mechanism claim on cohort data gets hedged, per `CLAUDE.md`. Reserve causal
verbs for designs that support them.

---

## F. The number that drifted

### F1 — A figure regenerated, a caption did not
The most common defect, and the one `claim_audit.py` exists to prevent.
**Test:** every typed number is tied by pattern to a value the script writes out.

### F2 — A result quoted from a superseded run
The report cites a number from before the cohort was tightened.
**Test:** re-run end to end and diff every number in the report against the fresh output.

### F3 — A hand-computed value in prose
Any number typed rather than emitted, including rounded percentages and differences.
**Test:** emit it from the script. If it is worth stating, it is worth computing.
