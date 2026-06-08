# Follow-up reports — when to ship a second PDF instead of amending the first

A frequent question once a polished report has been delivered: new data arrives, an analysis runs that wasn't previously possible, or a finding changes. Do you update the original report, or ship a new one?

The short answer: **prefer a new follow-up PDF whenever the trigger is a discrete event** ("we got data access", "we ran the literal version of analysis X", "we re-ran with covariates"). Update the original only when fixing a defect (wrong number, broken figure, typo).

This document captures the follow-up pattern that worked for the Kabashi review's PROACT follow-up — its structure, framing, and the trade it implies.

## Why a follow-up beats an amendment

1. **The original report is dated.** A reader who saw v1 and a reader who only sees v2 should be reading the same thing. If you edit the original in place, the v1 readers' mental map (the Q3 in their notes) no longer matches what's on the page.
2. **Provenance.** "We ran X on date D and got Y" is a fact. The follow-up records when each piece arrived. The original isn't a moving document.
3. **The follow-up can be honest about what changed.** Amending a report to silently swap an OR 1.66 for an OR 2.51 in the same Finding F4 is misleading — the reader doesn't know whether you re-ran something or fixed an error. A follow-up frames the new result as new.
4. **Two short reports beat one long one.** Follow-ups should be 4-8 pages — readable on their own as a focused brief.

When to update the original instead:
- Number was wrong (typo, miscalculation, regression bug).
- Figure rendered wrong (axis mislabel, wrong colour assignment).
- A claim was overstated and needs softening — and a follow-up would feel ceremonial for the size of the correction.

## Structure that works

The follow-up has six recognisable parts. Most fit on 5-7 pages total.

### 1. Cover with green status banner

The default status for a follow-up is **green** — it announces that an analysis ran successfully and there's information to report. Use **amber** if the follow-up is reporting mixed or refining results. Use **red** only if the follow-up is reporting that a previously-headline finding has been refuted.

Status banner body opens with one sentence locating the follow-up against the original:
> "Follow-up to the May-08 review — we now have the literal Analysis 1 result + a bonus NfL finding."

Then a paragraph of "quick context for this short report" summarising what the original said, what the follow-up adds, and what it does NOT change. This paragraph is the most-read piece of writing in the follow-up — invest in it.

### 2. Three KEYSTATs anchoring the change

The first two KEYSTATs are the new results — the numbers the reader will quote. The third KEYSTAT is a **null-anchor**: a number that tells the reader what *didn't* change.

The pattern used in the Kabashi follow-up:
- `[KEYSTAT|2.51|...]` — the new headline number
- `[KEYSTAT|−0.353|...]` — the new bonus number
- `[KEYSTAT|0|Substituted-result claims invalidated|None. The substituted Analysis 1 is refined, not contradicted...]`

The "0" KEYSTAT is the most important visual element in the follow-up. It tells the reader at a glance: *the original is not being torn up*. Without it, the reader's anxiety is "what did I miss?" — and the follow-up doesn't answer that question.

If the follow-up genuinely does invalidate something, the third KEYSTAT becomes the *count* of things invalidated (e.g. `[KEYSTAT|1|Substituted-result claims invalidated|Finding F4's OR magnitude was an underestimate...]`).

### 3. "What changed" comparison table

A pipe table with three columns: **Aspect | Original report | This follow-up**.

Rows are the aspects that the colleague will care about — typically the headline numbers, sample sizes, key adjustments, and any open question from the original that this follow-up resolves.

The Kabashi follow-up's table had eight rows including a row that explicitly named "OR > 2 threshold question (your Q4)" — calling back to a specific question from the original report. **Calling out a question from the original** is the highest-leverage row you can write — it tells the reader you remembered what they asked.

The table is `KeepTogether`-wrapped by the renderer; if it doesn't fit on the cover, push the whole "## What changed" heading and table to the next page with a `<<PAGEBREAK>>` directive between the third KEYSTAT and the heading.

### 4. New findings — one page per finding

Standard finding layout: heading + image + STATUS + 4 callouts ([MEDICAL] / [DATA-SCIENCE] / [LAY] / [DATA]).

These are usually 1-2 findings, not 4-5. If you have more than 2, the follow-up is probably big enough that it should stand alone as a primary deliverable, not a follow-up.

### 5. "What was gained / What was lost" sections

Two `## What was gained` and `## What was lost` sections, each containing 2-4 coloured BOXes. This is the most distinctive piece of the follow-up format and the part that makes it feel honest rather than promotional.

**Gain BOXes** are green. Each gets a title like "Gain 1 — Bulbar-onset OR now clears the OR > 2 threshold". Body explains the gain in 2-4 lines, framed as a delta from the original report.

**Loss BOXes** are amber or gray (never red — red would imply the original was wrong, not just less powerful). Each gets a title like "Loss 1 — Sample size dropped from 8,520 to 686 in the joint model". Body explains the trade.

**A Loss 3 (or final loss) box that explicitly names "almost no loss"** is a recognised pattern. The body acknowledges that the original report's numbers stand correct for the model they describe, even if the new model refines them. This is the structural counterpart to the "0 invalidated" KEYSTAT on the cover.

```
[BOX|gray|Loss 3 (almost none) — Original report's headline numbers]
The OR = 1.66 / 1.83 substituted-version numbers in the May-08 report
stand correct for the model they describe (univariate-style logistic
on the full 8,520-subject cohort with only categorical predictors).
They are not refuted by the literal analysis — they are the same
biology measured with a less direct probe.
[/BOX]
```

### 6. Open questions raised by the follow-up + reproducibility

Usually 2-3 new open questions. Number them Q1-Q3 (NOT Q5-Q7 even if the original had Q1-Q4) — the follow-up is a standalone document and its own questions reset.

Reproducibility BOX lists only the **additions** since the original. It does not restate the original's pipeline. The footer line should mention the data source and reference the original report by filename.

## Length and pacing

- 4-8 pages total. Typically 6.
- Cover: 1 page.
- Comparison table: 1 page.
- Findings: 1 page each (1-2 typically).
- Gain/Loss: 1-2 pages combined.
- Open Questions + Reproducibility: 1 page.

If the follow-up exceeds 10 pages, it's not really a follow-up — it's a second primary report. In that case, ship it as a primary report (with its own self-contained cover, hypotheses, full findings, etc.) and let the reader notice that it covers the same project as the previous one.

## Naming

For follow-ups, use `<TRIGGER>_FOLLOWUP.pdf` or `<DATE>_FOLLOWUP.pdf` rather than `REPORT_FOR_COLLEAGUE_v2.pdf`. Examples that worked:

- `PROACT_FOLLOWUP.pdf` — follow-up triggered by PRO-ACT data access landing
- `WIGHTMAN2024_FOLLOWUP.pdf` — follow-up after Wightman published
- `2026_05_16_FOLLOWUP.pdf` — date-stamped if there will be multiple follow-ups on the same project

The original keeps its name; the follow-up announces itself.

## What the follow-up should NOT do

1. **Don't re-explain the methodology.** Reference the original. The reader has it.
2. **Don't restate the original findings.** If the reader wants those, they read the original. The follow-up reports only the delta.
3. **Don't bury bad news.** If the follow-up refutes a key finding from the original, that goes in the cover paragraph and the "0" KEYSTAT becomes a real count of invalidated claims. Don't hide it on page 5.
4. **Don't include the full data-sources table from the original.** Mention only the new sources used in the follow-up.
5. **Don't include the project status / hypotheses section.** Those belong in the original; the follow-up is single-purpose.

## When the follow-up itself needs a follow-up

If results from a follow-up generate yet another round of analysis, ship a second follow-up — same pattern. Don't chain "follow-up to the follow-up" naming; date-stamp them. After ~3 follow-ups, consider a consolidating writeup that supersedes the chain and goes in `_archive/`.

## Worked example — Kabashi PROACT follow-up

The Kabashi project had two priority analyses. Analysis 2 ran cleanly. Analysis 1 was blocked on PRO-ACT data access, so a substituted version ran with bulbar-onset + El Escorial as proxies (Finding F4, OR 1.66 / 1.83). The original `REPORT_FOR_COLLEAGUE.pdf` reported both Analysis 2 (3 findings) and the substituted Analysis 1 (1 finding), and a "What's still needed" section mapping PRO-ACT tables to the literal analysis.

When the workspace's existing PRO-ACT data was confirmed to contain the same release the colleague had applied for, the literal Analysis 1 became runnable. Plus a bonus NfL × ALSFRS-R slope correlation that wasn't in the colleague's original brief but was enabled "free" by the now-accessible Neurofilament table.

The follow-up (`PROACT_FOLLOWUP.pdf`, 6 pages, 219 KB):

- **Cover** — green status, "we now have the literal Analysis 1 + bonus NfL", three KEYSTATs (2.51 / −0.353 / **0 invalidated**)
- **Comparison table** — 8 rows side-by-side substituted-vs-literal, including an explicit "OR > 2 threshold question (your Q4)" row that calls back to the original
- **Finding 1 (literal)** — multi-axial UMN+LMN pattern
- **Finding 2 (bonus NfL)** — limb-onset-specific
- **What was gained** (3 green BOXes) + **What was lost** (3 amber/gray BOXes, last one is "Loss 3 (almost none)")
- **Open Questions Q1-Q3** + reproducibility additions only

Total elapsed iteration time: ~25 minutes (write + render + verify + tighten 1 callout). Original `REPORT_FOR_COLLEAGUE.pdf` was left untouched. Both PDFs ship together.
