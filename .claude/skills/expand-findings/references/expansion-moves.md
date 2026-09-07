# The expansion catalogue

Ways to recover signal that conservative defaults discard, each with the guardrail that stops
it manufacturing a false lead. Ordered by cost. **Do the cheap moves first**; reaching for
heavy machinery before stating the analysable n is skipping the part that matters.

Every move here was stress-tested by an independent reviewer asked to find the abuse path.
**None survived unchanged** — the guardrails below are the hardening those reviews demanded,
and they are load-bearing rather than advisory. The recurring lesson: *a guardrail written as
prose gets ignored under pressure to find something, so wherever it can be a check in code,
it is.*

---

## Cheap

### C1 — State the analysable n, never the headline cohort size
PRO-ACT pools trials with different forms. ALSFRS-R visits, FVC records and vital status each
cover a different and much smaller subset. An MDE computed against "10,000 subjects" is
fiction.
**Report:** analysable n and event count *per outcome*, beside every interval.
**Guardrail:** `precision_report.py` prints a warning when `--n` is omitted and says the MDE
is meaningless without it.

### C2 — Triage every null with the compatibility ratio
R = largest effect still compatible ÷ the margin you would not want to miss. R ≥ 1 means a
clinically important effect is still on the table.
**Report:** "we could not detect an effect smaller than X; effects up to Y remain compatible".
**Guardrail:** the phrasing is bounded. Never "trends toward", never "suggests".

### C3 — Ban retrospective power; report precision instead
Power computed on the observed effect is circular: it is a transform of the p-value and tells
you nothing new.
**Instead:** MDE from the realized standard error, against a pre-registered margin.
**Guardrail:** the margin must be `CONFIRMED` in `effect_thresholds.md`. The tool refuses
otherwise, and an ad-hoc margin can open a question but never close one.

### C4 — Print the interaction MDE before writing "no evidence of effect modification"
Interaction tests have roughly a quarter the power of the main effect. Most subgroup nulls in
a cohort this size are uninformative by construction.
**Guardrail:** if the interaction MDE exceeds any plausible modification, the honest statement
is "this analysis could not detect effect modification", not "there is none".

### C5 — Report the whole distribution of a screen, never the tail
**Report:** the p-value histogram, the total number of comparisons, and the chance expectation
beside the number of hits.
**Guardrail:** a tail quoted without its distribution is a finding manufactured by selection.

### C6 — Put the magnitude inside an ALS plausibility envelope
An effect far larger than any approved therapy achieved is usually a bug, not a discovery.
**Guardrail:** an implausibly large effect triggers a search for a defect *before* it is
recorded as a lead. Treat it as suspected scale-mixing, a join that multiplied rows, or
survivorship.

---

## Moderate

### M1 — Replace per-subject slopes with a mixed model on all visits
A per-subject OLS slope discards everyone below the visit threshold and weights a noisy
3-visit slope equally with a well-observed one.
**Instead:** a mixed-effects model on all available visits, which uses subjects a slope filter
deleted and weights by precision automatically.
**Guardrail:** report the change in analysable n. If the conclusion changes, that is the
finding — report the dependency.

### M2 — Instrument the exclusion cascade and profile who it deletes
**Report:** n at every filtering step with a stated reason, and a baseline comparison of
excluded versus included.
**Guardrail:** any silent loss is an unstated exclusion criterion and must be named. If those
excluded differ systematically, the analysed cohort is not the enrolled cohort and every
estimate is conditional on selection.

### M3 — Multiple imputation in place of complete-case analysis
Baseline FVC missingness is not random: it is harder to measure in bulbar and
respiratory-failing patients, so complete-case analysis silently selects a healthier cohort.
**Guardrail:** report the missingness rate beside every n, and report complete-case and
imputed side by side. Imputation is not a way to make a result appear.

### M4 — Shrink every subgroup estimate before quoting it
The most extreme subgroup estimate in a scan is biased away from zero by selection.
Empirical-Bayes shrinkage toward the overall effect corrects most of it.
**Guardrail:** quote the shrunken estimate, and never the raw maximum. Report how many
subgroups were examined.

### M5 — Test for trend, not for difference
A graded dose-response is far harder to produce by chance than a single contrast.
**Guardrail:** the trend must be pre-specified as the hypothesis. Choosing "trend" after a
pairwise contrast failed is the forking path.

### M6 — Freeze a small modifier slate before looking
At most five biologically motivated modifiers, written down first: onset site, age, sex,
diagnostic delay, baseline ALSFRS-R, baseline FVC.
**Guardrail:** stratifiers must be **pre-baseline**, checked in code. A subgroup defined on a
post-baseline variable, or on progression itself, is survivorship in disguise.

### M7 — Pre-declare an alternative-outcome panel
When the primary outcome is null, a different endpoint may be better powered: time to a
milestone, a domain subscore rather than the total, a composite.
**Guardrail:** the panel is declared before the primary is run, and *all* of it is reported.
Reporting only the endpoint that worked is the same abuse in a new costume.

### M8 — Audit the ALSFRS-R floor effect
Subdomains bottom out at zero. Once at floor, decline stops being measurable and the slope
flattens for a reason that is not clinical improvement.
**Guardrail:** exclude or model the at-floor period and check whether the effect moves with it.

---

## Heavy

### H1 — Treat death as an event, not as missing data
A slope requires survival long enough to fit one, so the fastest progressors are absent from
the very quantity meant to describe progression.
**Instead:** a joint longitudinal-survival model, or inverse-probability weighting for
informative dropout.
**Guardrail:** state the estimand explicitly. A survivor-conditional estimate answers a
different question from a cohort-level one, and the two must not be reported interchangeably.

### H2 — Split by source trial into discovery and a locked replication half
PRO-ACT pools many trials, which makes an internal replication split possible.
**Guardrail:** split **once**, by trial rather than at random (so trial-level confounding does
not leak across), and spend the holdout **exactly once**. A holdout looked at twice is not a
holdout.

### H3 — Permute the whole search, not just the final test
The right null for a screen is "what does the best hit look like when there is no signal at
all?" — which requires permuting and re-running the *entire selection procedure*.
**Guardrail:** permute within pre-declared nuisance strata (source trial at minimum) and move
whole subject blocks, never individual rows. If the observed best hit sits inside the
permutation distribution, the screen is globally null and **no lead leaves it**, however large
the top effect looks.

### H4 — Specification curve across the arbitrary choices
See `scripts/relax.py`. Re-run across the cross-product of defensible choices and report the
whole curve.
**Guardrail:** the grid is chosen before running. The tool prints every specification, marks
the original, and refuses to name a best one.

---

## The Bayesian reframing, and its exact boundary

The argument for widening is fundamentally a **decision** argument: facing a uniformly fatal
disease, the loss function is asymmetric, and a 30% chance of a real effect can be worth
pursuing even though it fails a 5% test.

Defensible moves: a posterior probability that the effect is in the beneficial direction and
that it exceeds the clinical margin; a **prior panel** including a sceptical prior, with the
sceptical result in the headline; a **tipping-point analysis** showing how optimistic a prior
must be to reach a given conclusion.

**The boundary, and it is the whole thing:** this reframing changes what is worth **pursuing**.
It never changes what is asserted as **true**. A posterior probability is reported as a
decision input on a lead card, never as a finding, and never without the sceptical prior
beside it.

---

## The traps specific to this dataset

- **Two scales.** PRO-ACT mixes the 40-point ALSFRS and the 48-point ALSFRS-R. Pooling them
  inflates variance and quietly enlarges every MDE. They need separate margins.
- **Trial eligibility truncates the range.** Entry criteria on FVC and symptom duration
  restrict the very ranges under study, which shrinks detectable effects and makes an MDE
  non-transportable to the clinic population.
- **Exposure prevalence drives the MDE** through p(1−p). A 2–10% exposure can be far worse in
  variance than a balanced one, so "no association" with a rare drug is almost always an
  uninformative null. Print exposure prevalence beside every MDE.
- **Margins come from short trials.** A Δ\* drawn from a 24-week trial is not the same margin
  for a 24-month observational slope. Rescale it and say so.
- **Repeated visits are not independent subjects.** A screen run on visit-level rows inflates
  every statistic. One summary value per subject, or a subject-clustered model.
- **ALSFRS-R items are algebraically dependent.** The 12 items, three subscores and total are
  not independent tests. Screening them all inflates the comparison count while correcting for
  nothing real.
- **Immortal time.** A lead born of a time-varying exposure coded at baseline is an artefact
  of timing, not a lead. Clear the contrast through the methodology-pitfall checklist before
  applying any of this machinery to it.
