---
name: expand-findings
description: >-
  Widen an analysis so conservative defaults do not throw away real leads. Use when a result
  is null or borderline, when the user asks "what if we relaxed some of this", "did we miss
  something", "is that really nothing", "can we look at it another way", "what about a
  subgroup", "does that depend on the cohort definition", or pushes back that the constraints
  are too tight. Also use after any experiment finishes, alongside the adversarial review.
  Reports what the data could actually see, re-runs the analysis under every defensible
  version of its arbitrary choices, and records LEADS separately from findings.
license: MIT
metadata:
  version: 1.0
  scope: PRO-ACT cohort analyses for the ALS team
---

# Expand findings

The counterpart to **adversarial-review**. That skill tries to kill a claim. This one tries
to rescue a lead that conservative defaults discarded. Both run at the end of an experiment,
and they are not in tension: a finding that survives attack is worth more, and a lead that
was never looked for is worth nothing.

**Why this exists.** ALS is uniformly fatal and there are two marginally effective drugs. In a
cohort this size, `p > 0.05` usually means *we could not tell*, not *there is nothing there* —
and treating those as the same thing discards leads that patients cannot afford to lose.

**The one boundary, and it is absolute.** This skill produces **LEADS**, never findings. A
lead is a routing decision about where to spend the next effort. It goes in `LEADS.md`, never
in `HYPOTHESIS_LOG.md`, and it never counts as prior-art support. A lead mistaken for a
finding poisons the shared board the whole team queries, and the next person builds on
something that was never there. That costs exactly the time this skill is meant to save.

## Start here: what could the data actually see?

The cheapest and most defensible move. For any null, run:

```
python .claude/skills/expand-findings/scripts/precision_report.py \
    --estimate -0.08 --se 0.061 --outcome alsfrs_slope --n 5394 --contrasts 12
```

It reports three things and refuses to run without a margin a human registered:

| | |
|---|---|
| **MDE** | the smallest effect this analysis could have detected, from the realized SE. Not retrospective power, which is circular. |
| **R** | the largest effect still compatible, divided by the effect we said we would not want to miss. **R ≥ 1 means a clinically important effect is still on the table.** |
| **TOST** | equivalence against ±Δ\*. Only this licenses the phrase "adequately powered null". |

Two verdicts, and they are different kinds of thing:

- **CLOSED DOOR** — the analysis could have seen a clinically important effect and did not.
  **This is a finding.** Report it and send it through the adversarial review.
- **INCONCLUSIVE** — the effect space was never explored. **Not a finding, not evidence of
  absence.** It is a lead: the question is open and needs more data or a better design.

**The margin is the gate.** Δ\* comes from `references/effect_thresholds.md` and must be
`CONFIRMED` with a real source. Everything ships as `NEEDS-CITATION`, so **the tool refuses
until someone confirms a threshold**. That is deliberate: a margin chosen after seeing the
data is a rationalisation. An ad-hoc `--delta-star` is allowed but stamped `UNREGISTERED`,
and an unregistered margin **can open a question and can never close one**.

## Then: "what if we relaxed some of this?"

This is the question a researcher should ask of every finished analysis, and it usually
matters more than the p-value. The constraint that destroys the most signal is normally an
inclusion filter or an outcome definition adopted for convenience.

```
python .claude/skills/expand-findings/scripts/relax.py \
    --cmd "python analysis.py --min-visits {mv} --window {w} --outcome {o}" \
    --grid mv=2,3,4 --grid w=12,18,24 --grid o=total,motor \
    --extract "beta = (-?[0-9.]+)" --extract-p "p = ([0-9.eE+-]+)" \
    --baseline mv=3,w=18,o=total
```

It re-runs the analysis across the cross-product of the choices and prints the **whole
curve**, with the original marked so a reader can see whether the published number was
typical or the extreme. It reports direction agreement, how many specifications reached
alpha, and which choice moves the answer.

**It will not name a best specification, and it says so.** Running forty specifications and
quoting the one that reached significance is the garden of forking paths, and it is the
easiest way there is to manufacture a finding.

The four outcomes it can report:

- **ROBUST** — the direction and the threshold hold across essentially every choice. Report
  the curve beside the headline.
- **DIRECTION ROBUST, MAGNITUDE CHOICE-DEPENDENT** — everything points the same way but
  significance depends on the choices. **A lead.** Report the range, never one specification.
- **CHOICE-DEPENDENT** — a substantial minority disagree. The honest headline is the
  dependency itself, and that *is* a real finding about the data.
- **NOT ROBUST** — specifications disagree on direction. The original number is a property
  of its choices. Do not report it as a result.

**Choose the grid before running it**, and keep it small and defensible. Every value must be
a choice a competent analyst could have made first. A grid assembled after seeing which way
the wind blows is not a sensitivity analysis.

## The other moves, in order of cost

Full catalogue with the guardrail for each: **`references/expansion-moves.md`**.
Cheap ones first; do not reach for the heavy machinery before the cheap moves are done.

**Cheap.** State the analysable n for *this* outcome, never the headline cohort size. Print
the interaction MDE before writing "no evidence of effect modification". Report the whole
distribution of a screen, not its tail. Put the magnitude inside an ALS plausibility envelope
and treat an implausibly large effect as a suspected bug rather than a discovery.

**Moderate.** Replace per-subject slopes with a mixed model on all visits, which recovers the
subjects a slope filter deleted. Multiple imputation instead of complete-case. Shrink every
subgroup estimate before quoting it. Test for **trend**, not difference. Freeze a small slate
of biologically motivated modifiers *before* looking.

**Heavy.** Treat death as an event rather than as missing data. Split by source trial into
discovery and a locked replication half. Permute the whole search, not just the final test.

## Subgroups: the highest-yield and most dangerous move

An average null can conceal a real effect in a subgroup, and ALS is heterogeneous enough that
this is a genuine route to a breakthrough. It is also the single most reliable way to produce
a false lead.

- **Interaction terms, never subgroup-by-subgroup p-values.** Two different p-values are not
  evidence of a difference. Fit the interaction and report it.
- **Freeze the slate first.** At most five biologically motivated modifiers, written down
  before looking: onset site, age, sex, diagnostic delay, baseline ALSFRS-R, baseline FVC.
- **Pre-baseline only, checked in code.** A subgroup defined on a post-baseline variable, or
  on progression itself, is survivorship wearing a disguise.
- **Say how many subgroups you examined.** Every time.

## Recording a lead

Leads go in **`LEADS.md`** at the repo root, never in `HYPOTHESIS_LOG.md`. Format:
`templates/LEAD_TEMPLATE.md`. Every lead carries an ID (`L-001`), a status, an **expiry
date**, the analysable n, the number of contrasts screened, and what would resolve it.

**Promotion is one-way and needs new evidence.** A lead becomes a hypothesis only when it is
tested on data that was not used to generate it — a locked holdout, a different cohort, or a
new release. Re-analysing the same data more cleverly does not promote a lead. If it did, the
register would just be a slower path to the same false finding.

## What this skill will never do

- Say an effect exists, is likely, or is probable. The vocabulary is *not excluded*, *could
  not have been detected*, *would need n = X to resolve*.
- Turn a wide interval into a direction, a probability, or a mechanism.
- Write to `HYPOTHESIS_LOG.md` or `findings/`.
- Let a lead count as prior art in the pre-analysis check.
- Name a best specification, or report a tail without the distribution it came from.

If a researcher pushes for one of those, say plainly which line it crosses and offer the
version that stays on the right side of it.
