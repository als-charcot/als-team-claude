# Layout discipline — page-break rules and worked examples

The hardest part of producing a polished report isn't the writing — it's making the renderer place each piece on the right page. This document captures the rules and the patches that fix the most common failures.

## The contract

Each report obeys six layout rules:

1. **One finding per page.** Heading + image (≤2.6 in) + STATUS + 4 callouts = ~7-9 inches of vertical space. If callouts are 2-4 lines each, this fits on a US-letter page with margins.
2. **`<<PAGEBREAK>>` before every `## Finding` section.** Always. Never let the previous content's tail spill into a finding.
3. **Tables are atomic.** Wrapped in `KeepTogether`. If a long table can't fit on its current page, it jumps to the next — leaving a gap if the heading doesn't jump with it. Fix: `<<PAGEBREAK>>` before the heading.
4. **No more than 4 BOXes per page** (typically). "What was refuted" gets its own page. "Couldn't be refuted" gets its own. "Promising" gets its own. "Tiers" gets its own.
5. **Don't waste a heading on a single small BOX.** If `## Reproducibility` is followed by a 5-line BOX and they'd land alone on a page, drop the heading and put the title inside the BOX — it has its own title bar.
6. **No orphan callouts.** If F1's `[DATA]` callout lands alone at the top of page 4 (page 3 had heading + image + STATUS + 3 callouts), the F1 callouts are too long. Tighten F1's first three callouts so all four fit on F1's page.

## The verification loop

After every render:

```bash
python scripts/reports/build_report.py
python scripts/reports/verify_layout.py reports/REPORT.pdf
```

Then read every `reports/_preview/page_NN.png` and tag each as:

- ✅ Clean — content fills most of the page, no orphan, no awkward gap.
- ⚠️ Underfull — content ends well above the page bottom but the next page is full.
- 🔴 Orphan — single callout / single BOX / heading alone, with > half the page blank.
- 🔴 Overflow — content visibly cut off or pushed to next page mid-section.

Underfull pages are usually fine (the alternative is forcing content to bleed). Orphans and overflows always need fixing.

## Common failures and their patches

### Failure: hypotheses table splits onto page 2

**Symptom:** Page 1 has the cover + first 4 rows of the table. Page 2 has rows 5–6 of the table, then a small data-sources BOX, then half-empty.

**Cause:** Combined content (cover + KEYSTATs + table + BOX) is taller than one page. The table is `KeepTogether`, so it stays atomic — but the heading above it isn't grouped with it.

**Patch:** Add `<<PAGEBREAK>>` before the `## Hypotheses` heading. Now page 1 = cover + KEYSTATs only; page 2 = `## Hypotheses` + table + data sources BOX.

```diff
 [KEYSTAT|3 / 3|Wightman 2024 r_g pairs replicated|...]

+<<PAGEBREAK>>
+
 ## Hypotheses (H1–H6) — current status after v4
```

### Failure: finding overflows to a half-empty page 2

**Symptom:** F2 = heading + image + STATUS + first 2 callouts on page 5. Last 2 callouts on page 6 with the rest of page 6 blank.

**Cause:** F2's callouts are too long collectively. With 2.6-inch image + STATUS banner + heading + 4 long callouts, the total exceeds page height.

**Patch:** Tighten the longest callouts to 2-4 lines each. Don't repeat what STATUS already said. Move tangential context out — usually `[MEDICAL]` and `[DATA-SCIENCE]` are the two that bloat.

Worked example — before:

```
[MEDICAL]: Multiple sclerosis is autoimmune CNS, distinct from
neurodegeneration. T2D is metabolic, non-CNS, non-classically-immune.
If ALS shares genetics with MS but not T2D, the shared signal is
specifically *neuroimmune*, not "any chronic disease." Consistent
with TBK1 / OPTN / C9orf72 / TARDBP literature — sporadic ALS is
increasingly recognised as having an immune component.
```

After (3 lines instead of 6):

```
[MEDICAL]: MS is autoimmune CNS; T2D is metabolic, non-CNS. ALS
sharing with MS but not T2D means the signal is specifically
*neuroimmune*, not "any chronic disease." Consistent with
TBK1 / OPTN / C9orf72 / TARDBP literature.
```

### Failure: a single small BOX alone on the last page

**Symptom:** Final BOX (typically reproducibility) sits alone on page N+1 with most of the page blank. Page N had the open questions and ended with comfortable space.

**Cause:** `## Reproducibility` heading + small BOX needed to flow from the bottom of page N, but the heading-spacing pushed both onto page N+1.

**Patch:** Drop the `## Reproducibility` heading. Put "Reproducibility" in the BOX title. Now the BOX flows naturally on page N.

```diff
-## Reproducibility
-
-[BOX|gray|Everything reproduces end-to-end on a workstation]
+[BOX|gray|Reproducibility — everything reproduces end-to-end on a workstation]
```

### Failure: "What was refuted" + "couldn't be refuted" run together

**Symptom:** Page 7 has 4 red BOXes ("refuted") + the first green BOX of "couldn't be refuted". Page 8 has the rest of "couldn't be refuted" + "promising" header. Section boundaries disappear.

**Cause:** No explicit page break between sections. The renderer flows BOXes back-to-back.

**Patch:** Add `<<PAGEBREAK>>` between every result-category heading.

```diff
 [BOX|red|v3 DGE was inflated...]
 ...
 [/BOX]

+<<PAGEBREAK>>
+
 ## What couldn't be refuted (in the data)
```

### Failure: callout body crosses pages mid-sentence

**Symptom:** F4's `[DATA]` callout starts at the bottom of page 7, last two lines bleed onto page 8.

**Cause:** Callouts are *not* wrapped in KeepTogether (intentionally — wrapping all 4 callouts together would overflow).

**Patch:** Tighten the previous callouts so the `[DATA]` callout starts higher on the page, or shorten `[DATA]` itself. If only the last 1-2 lines bleed, this is usually acceptable — it's a callout body crossing, not a heading orphan.

If it's truly distracting, the strongest patch is to add a page break before F4 so it has more headroom. But this is usually a sign that the finding is over-written.

### Failure: figure caption far below the figure

**Symptom:** Figure renders, then there's vertical space, then the caption. Looks disconnected.

**Cause:** This is normal at the bottom of a figure when a STATUS or callout follows — the spacing between figure block and next block adds up.

**Not a bug.** The caption is bonded to the figure inside `add_image()`. The space below is the spacing-after on the figure block, which deliberately separates it from the next element.

## Sequencing — recommended page allocation

For a typical 4-finding report:

| page | content |
|------|---------|
| 1 | Cover (title + status banner + 3 KEYSTATs) |
| 2 | Hypotheses table + Data sources BOX + Pipeline BOX |
| 3 | Finding F1 (heading + image + STATUS + 4 callouts) |
| 4 | Finding F2 |
| 5 | Finding F3 |
| 6 | Finding F4 |
| 7 | What was refuted (4 red BOXes) |
| 8 | What couldn't be refuted (4 BOXes — usually 1 green + 3 amber) |
| 9 | What looks promising (3-4 green BOXes) |
| 10 | Possible next-version paths (3 tier BOXes — blue / amber / gray) |
| 11 | How to read + Open questions Q1-Q4 + Reproducibility BOX |

11 pages total. If you have more findings, this scales linearly — F5 goes between F4 and "What was refuted", etc.

## When to break the contract

Two acceptable exceptions:

1. **A finding has an unusually large image** (e.g., a heatmap that needs full page height for legibility). Increase `max_h` for that one image. Accept that callouts will spill to a second page; place `<<PAGEBREAK>>` between F-N's image-page and F-N's callout-page.
2. **A long table is the central deliverable** (e.g., a top-50 gene table). Give it its own page or two. Use `<<PAGEBREAK>>` before and after.

In both cases, the discipline still holds: each piece lives on a coherent page, no orphans, no half-blank gaps.
