---
name: adversarial-review
description: >-
  Audit a finding against what the analysis script actually computed, before it is shared or
  written up. Finds numbers that drifted from the pipeline, cohorts that are not the cohort,
  checks that cannot fail, and statistics that answer a different question. Use when a
  finding is about to be promoted or reported, when a result feels too clean, when a report
  quotes numbers a script also produces, or when the user asks to "red-team", "review",
  "challenge", "audit", "sanity-check" or "stress-test" an analysis or a finding. Runs
  independent reviewers with separate context, each on a different failure lens.
license: MIT
metadata:
  version: 1.0
  scope: PRO-ACT cohort analyses for the ALS team
---

# Adversarial review

A finding accumulates numbers faster than it can keep them consistent. A figure is generated
on Tuesday, a sentence is typed beside it on Wednesday, the cohort definition is tightened on
Friday. The figure regenerates. The sentence does not. Nothing errors, the script still runs,
and the defect exists only in the report.

This is the discipline for catching that before a colleague builds on it. It is an audit of
**your own live analysis**, run on the assumption that it is currently wrong in a way you
cannot see. It is not peer review of someone else's manuscript (see `peer-review`) and not
evidence grading (see `scientific-critical-thinking`).

Three convictions drive it:

1. **A number in prose is a claim about a pipeline.** If nothing ties them together, they
   have already diverged.
2. **A reviewer given your summary reviews your summary.** Give them the data and the script.
3. **A check that has never failed may be incapable of failing.** Prove it can fail.

## When to run it

- **Always before `share-work` promotes a finding.** This is a gate, not an option.
- Before any report or slide leaves the researcher's machine.
- When an effect is surprisingly clean, or a p-value is very small with a tiny effect size.
- When a cohort was redefined after the first results were seen.

## Phase 0 — Pin the state of record

Before reviewing anything, establish what the analysis *currently* computes. Re-run the
end-to-end script and capture its outputs (the summary JSON/CSV it writes, the figures, the
row counts). **The state of record is the script's output, never the report's prose.**

If the script cannot be re-run, that is finding number one: stop and say so.

## Phase 1 — Enumerate the claim surface

List every falsifiable assertion in the deliverable: each number, each n, each effect size
and interval, each named subgroup, each figure caption, and each mechanism claim. A claim is
anything a colleague could act on. Write them down before reviewing, so nothing is quietly
skipped.

Then run the standing gate, which does this mechanically:

```
python .claude/skills/adversarial-review/scripts/claim_audit.py claims.json
```

## Phase 2 — Fan out adversarially

This is the heart of the skill, and the part that is easy to do in a way that looks right and
achieves nothing. **Each reviewer is a separate agent with its own fresh context window.**

```
   YOUR SESSION                        holds the whole history: the analysis,
   (knows everything)                  your reasoning, why you believe it
        │
        │  dispatches, one per lens. each gets ONLY the payload below.
        │
   ┌────┴────┬─────────┬─────────┬─────────┐
   ▼         ▼         ▼         ▼         ▼
 confound  surviv.   stats    reprod.   (clinical)
 FRESH     FRESH     FRESH    FRESH      FRESH        ← separate context each
   │         │         │         │         │
   │  no reviewer sees: your summary, your reasoning, this conversation,
   │  or any other reviewer's verdict. They cannot agree by influence.
   ▼         ▼         ▼         ▼         ▼
     verdicts return independently, and only then are they compared
```

**What each reviewer is given (the whole payload, nothing more):**

1. The claim under review, **quoted verbatim**.
2. Paths to the **script**, its **summary output**, and the **data**.
3. Its **one lens**, and which catalogue sections apply.
4. The output shape, and the instruction to transcribe before verdict.

**What each reviewer is deliberately NOT given:**

- Your summary of the analysis, or why you think it is right. A reviewer handed your
  reasoning inherits your blind spots and returns them to you as agreement.
- Any other reviewer's verdict, or their findings in progress. Reviewers run in parallel
  precisely so they cannot converge by influence.
- The conversation history. A fresh context is what makes the second opinion a second
  opinion rather than an echo.

**Why independence is the whole point.** If three reviewers with separate contexts, separate
lenses and no knowledge of each other land on the same defect, that agreement carries
information. If they were shown each other's work, or your reasoning, it carries none. The
value is not the number of reviewers; it is that none of them could have been influenced.

Worked examples of a lens verifying and refuting a claim, including a reviewer that
over-claimed and how that was caught: **`references/examples.md`**.
Full rules and a prompt skeleton: `references/fanout-lenses.md`.

The minimum four lenses for a PRO-ACT cohort finding:

| Lens | Asks |
|---|---|
| **Confounding and indication** | who ended up in each group, and why |
| **Survivorship and missingness** | who had to survive or be measured to appear at all |
| **Statistics and instruments** | does the number answer the stated question |
| **Reproducibility** | does the script, re-run, still produce this exact number |

Use different Claude model tiers across reviewers where it is available, so a result is not
judged only by the kind of model that produced it.

**Rules that make the fan-out work, and are easy to lose:**

- The reviewer holds the **data and the script**, not the summary.
- Frame the job as **finding**, not judging. "Try to refute this" beats "is this correct".
- Force **transcription before verdict**: make them quote the line of code or the number
  they are challenging, so they cannot object to something that is not there.
- Require **structured, enumerated verdicts**, so they can be counted and recorded.
- Reviewers are **read-only**. They never edit the analysis.

## Phase 3 — Interrogate the instruments

Ask of each check and each statistic: *could this have failed?* Run the catalogue in
`references/failure-modes.md`, which enumerates the ways a PRO-ACT analysis produces a
confident number that means nothing.

For any effect that survives, run a **negative control**:

```
python .claude/skills/adversarial-review/scripts/mutation_check.py --help
```

Permute the exposure or the outcome and confirm the effect collapses. An effect that
survives its own permutation test is measuring the pipeline, not the disease.

## Phase 4 — Fix at source, then re-derive

Fix the **script**, never the sentence. Then re-run end to end and regenerate every number,
figure and caption from the corrected output. A hand-patched number is a defect with a
longer fuse.

## Phase 5 — Record what was withdrawn, and why

Any claim that does not survive goes into the finding's `README.md` under **Withdrawn**, with
the mechanism that defeated it. Not deleted silently. A withdrawn claim with its reason is
one of the most useful things in the repo: it stops the next person re-deriving it.

Append the surviving verdicts to the `HYPOTHESIS_LOG.md` entry, so the team sees what the
finding was challenged on and what held.

## Phase 6 — Install the standing gate

Add a `claims.json` beside the analysis so every future run re-checks the prose against the
pipeline. Two properties matter, and both are easy to lose:

- **A pattern that matches nothing is a failure, not a pass.** Otherwise the check silently
  stops running the moment somebody rewords a sentence, which is exactly when it is needed.
- **Names are checked too.** A report that names the wrong subgroups is worse than one that
  miscounts them.

## The editorial rule

Report what survived and what did not, with the mechanism. Never soften a withdrawal into a
"limitation". If four reviewers attacked a finding and it held, say so and say on what. If it
fell, say what defeated it. The point of the exercise is that the surviving claims are worth
more, not that the report sounds more confident.

## Files

- `references/fanout-lenses.md` — the lenses, the five prompt rules, a prompt skeleton
- `references/examples.md` — worked examples: a claim refuted, a claim that held, and a
  reviewer over-claiming
- `references/failure-modes.md` — the PRO-ACT instrument-failure catalogue
- `scripts/claim_audit.py` — the standing gate: prose numbers vs pipeline output
- `scripts/mutation_check.py` — permutation and negative controls
