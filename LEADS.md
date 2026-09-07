# Leads — ALS team

**This is not the hypothesis log, and the difference is the point.**

`HYPOTHESIS_LOG.md` holds **findings**: things we tested and now believe, with effect sizes,
and which survived the adversarial review. This file holds **leads**: questions the data
could not answer, effects that depend on an arbitrary choice, and subgroup signals worth a
second look.

A lead is a **routing decision** — where to spend the next effort. It is not evidence.

## The rules, which exist because a lead read as a finding is worse than no lead

1. **A lead never counts as prior art.** The pre-analysis check reads `HYPOTHESIS_LOG.md`.
   If a lead appeared there, the next person would build on something never demonstrated.
2. **Promotion is one-way and needs new evidence.** A lead becomes a hypothesis only when
   tested on data that did not generate it: a locked holdout, a different cohort, a new
   release. Re-analysing the same data more cleverly does not promote it.
3. **Every lead expires.** An open question nobody has revisited in six months is either
   worth doing or worth closing. Stale leads are cleared, not inherited.
4. **The vocabulary is bounded.** "Not excluded", "could not be detected", "would need
   n = X". Never "suggests", "trends toward", "promising", "likely".
5. **Every lead states its analysable n and how many contrasts were screened.** A tail
   selected from many contrasts is not a single test.

Numbered L-001, L-002, … newest at the bottom. Written by the **expand-findings** skill;
format in [`templates/LEAD_TEMPLATE.md`](templates/LEAD_TEMPLATE.md).

---

<!-- New leads are appended below this line. -->
