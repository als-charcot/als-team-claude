[STATUS|amber|Project status: one-line label of where this stands]
**One-paragraph executive summary** going right under the status banner. State the headline finding(s) and the most important caveats in 3-4 sentences. The colleague who reads only this paragraph + the three KEYSTATs below should walk away knowing what happened.

[KEYSTAT|+0.218|First headline number — what it measures|tight context line: p-value, sample size, sanity-check comparator. One physical line in source.]

[KEYSTAT|49|Second headline number — what it counts|tight context: how the count was derived, what it survived.]

[KEYSTAT|3 / 3|Third headline number — replication / pass-rate|tight context: the reference cohort or known-truth check.]

<<PAGEBREAK>>

## Hypotheses (or: scope, or: claims) — one-page summary table

| # | Claim | Status |
|---|-------|--------|
| H1 | First claim — keep cell text under ~10 words | refuted / supported / weakened / untested |
| **H2** | **Highlight a focal claim with bold** | **supported (specific test name)** |
| H3 | Third claim | untested (why) |

## Data sources & pipeline

[BOX|blue|Data sources — all public / all workspace-resident / etc.]
- **Source 1** (citation, accession) — what it gives you
- **Source 2** — same shape
- **Source 3** — same shape
Total ~X GB on disk. End-to-end ~Y hours. No registered data.
[/BOX]

[BOX|gray|Pipeline — N versions, structured remediation]
**v1** what v1 did, in one line.
**v2** what v2 added, one line.
**v3** what v3 added + the redteam concerns it surfaced.
**v4** what v4 fixed, what's still open.
[/BOX]

<<PAGEBREAK>>

## Finding F1 — one-sentence claim, ideally with the headline number in it

![Caption that becomes the figure caption in the PDF](../figures/fig01.png)

[STATUS|green|One-line label — supported / mixed / refuted by which specific test]
2-3 sentence body restating the finding with numbers and the asymmetry that establishes it. This sits right under the image and gives the reader the "answer" before the four callouts dive into different framings.

[MEDICAL]: 2-4 lines. The clinical/biological meaning. What does this finding mean for the disease mechanism? What known literature does it intersect?

[DATA-SCIENCE]: 2-4 lines. The statistical/methodological framing. Slope, ratio, SE, robustness checks. Why this number rather than that number.

[LAY]: 2-4 lines. Plain English with a metaphor where useful. The colleague's spouse should be able to read this and get the gist.

[DATA]: 2-4 lines. A concrete number or row from the actual data. The exact n_SNPs, the exact ρ, the exact log2FC, the exact gene name. Not summaries — *one literal datapoint*.

<<PAGEBREAK>>

## Finding F2 — second finding, same shape

![Caption for figure 2](../figures/fig02.png)

[STATUS|amber|Mixed result label]
Body…

[MEDICAL]: …

[DATA-SCIENCE]: …

[LAY]: …

[DATA]: …

<<PAGEBREAK>>

## What was refuted (in the data)

[BOX|red|H-X — short summary of the refuted claim]
**Refuted.** Specific test that refuted it, with numbers. Caveat about what kind of refutation this is (plasma-only? specific cohort? specific α?).
[/BOX]

[BOX|red|Second refuted thing]
**Confirmed and partially fixed.** What you found, what the fix changed.
[/BOX]

<<PAGEBREAK>>

## What couldn't be refuted (in the data)

[BOX|green|Hypothesis that survived — short title]
The thing that survived, with the test that supports it and the test that didn't break it.
[/BOX]

[BOX|amber|Hypothesis that's open / weakened]
The thing that's still possible but couldn't be tested with available data, or got demoted by a robustness check.
[/BOX]

<<PAGEBREAK>>

## What looks promising (most-actionable next leads)

[BOX|green|Lead 1 — short title]
Why it's the strongest. **Concrete next step:** specific 1-day or 1-week task that would advance it.
[/BOX]

[BOX|green|Lead 2 — short title]
Same shape — what / why / concrete next step.
[/BOX]

<<PAGEBREAK>>

## Possible next-version paths (ranked by readiness)

[BOX|blue|Tier 1 — actionable immediately]
- **Task A** — what data, expected effort, what it answers.
- **Task B** — same shape.
[/BOX]

[BOX|amber|Tier 2 — gated on something]
- **Task C** — what's the gate (registered-data access? collaboration?).
[/BOX]

[BOX|gray|Tier 3 — depends on data not yet available]
- **Task D** — what's missing.
[/BOX]

<<PAGEBREAK>>

## How to read this report

[STATUS|gray|Two important caveats for honest interpretation]
First caveat — what "supported" / "refuted" actually means here (test-specific, not categorical). Second caveat — anything about who did the redteam, what was self-conducted, what an external pass would still surface.

## Open questions for external review

[QUESTION|Q1|Concerns we missed in our self-redteams]
Short body. The question is the title; the body provides specific framing for what kind of answer would help.

[QUESTION|Q2|Whether the headline number matches your domain prior]
Short body — what we expected, what we got, why it might still be wrong.

[QUESTION|Q3|Whether the candidate panel passes a clinical plausibility filter]
Short body.

[QUESTION|Q4|Which next-version path is highest-priority from your perspective]
Short body — our preference, but we want yours.

[BOX|gray|Reproducibility — everything reproduces end-to-end on a workstation]
- **N scripts** in `project/scripts/` (~K lines)
- **M figures**, ~T result tables
- **X GB on disk**, all public data
- **End-to-end runtime** ~Y hours
For deep dives: `archived_writeup_1.pdf`, `archived_redteam.pdf`, `01-NN_per_section.pdf`.
[/BOX]
