# Iteration loop — how to verify and fix layout

The verification loop is what separates a polished PDF from a "rendered markdown" PDF. This document captures the loop and its failure-pattern catalog.

## The loop

```
┌──────────────────────────────────┐
│ 1. write/edit REPORT.md          │
└──────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ 2. python build_report.py        │
│    (renders REPORT.pdf)          │
└──────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ 3. python verify_layout.py       │
│    (rasterises pages → _preview/)│
└──────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────┐
│ 4. read every page_NN.png        │
│    tag clean / underfull /       │
│    orphan / overflow             │
└──────────────────────────────────┘
                 │
        ┌────────┴────────┐
        │                 │
   all clean         orphan/overflow
        │                 │
        ▼                 ▼
   ✅ ship          edit MD → goto 2
```

Typical loop count: 3–5 iterations for a fresh report. After the second pass, you'll usually only be touching one or two pages per iteration.

## Step 4 in detail — what to look for

When you read each `page_NN.png`, classify it:

### ✅ Clean

- Page is mostly full (text reaches roughly the bottom-third of the page or further).
- All blocks are intact (no callout / BOX cut mid-sentence).
- No heading sitting alone at the bottom with no content under it.
- No heading sitting alone at the top with the previous page mostly blank.

### ⚠️ Underfull but acceptable

- Page ends with comfortable space but the next page's content couldn't fit on this page.
- Common at the end of a "What was refuted" page that has 3 BOXes and a tiny gap to the next section's heading on the next page.
- Don't try to fix every underfull page — forcing content can cause overflow elsewhere.

### 🔴 Orphan — must fix

- A single callout, single BOX, or single small element on the page with > 50% blank space.
- Heading alone at the bottom (next page starts with the body it should head).
- Single QUESTION card alone on its page when 3 others are on a different page.

### 🔴 Overflow — must fix

- Content visibly crosses the bottom margin (rare with `KeepTogether`, but possible if image is taller than page).
- Heading + image + STATUS land on page N, all 4 callouts land on page N+1 alone.
- Table split mid-row across two pages (shouldn't happen with the canonical lib — if it does, the table is taller than a page; shorten cells).

## Failure-pattern catalog (with fixes)

### Pattern A — F-N's last callout orphaned on page after

Page X: F-N heading + image + STATUS + 3 callouts. Page X+1: F-N's `[DATA]` callout alone, then huge blank space, then "What was refuted" heading on page X+2.

**Fix:** Tighten the 3 preceding callouts. Aim 2-3 lines per callout, never longer than 4. The `[DATA]` callout should land on page X.

### Pattern B — entire finding on its own oversized page, callout overflow

Page X: F-N heading + image + STATUS only. Page X+1: F-N's 4 callouts.

**Fix:** Image is taller than 2.6 inches, or the STATUS body is too long. Either:
- Cap image height — already done by `max_h=2.6*inch` in `add_image()`. If the image is rendered too tall, the image file itself is too tall; downscale.
- Tighten the STATUS body to one paragraph (≤ 3 sentences).

### Pattern C — Box section runs together with next section

Page X: 3 BOXes from "What was refuted" + first BOX from "Couldn't be refuted". Page X+1: rest of "Couldn't be refuted" + first BOX of "Promising". Section boundaries vanish.

**Fix:** `<<PAGEBREAK>>` between every result-category heading. The renderer doesn't auto-page-break — that's the design.

### Pattern D — table splits

Page X: heading + first 4 rows. Page X+1: rows 5-6 + next section.

**Fix:** With the canonical lib (post-May-7-2026), tables are wrapped in `KeepTogether` so they don't split. If you're seeing this:

- Confirm `report_pdf_lib.py` has `story.append(KeepTogether([t, Spacer(1, 8)]))` in `add_table()` — not the unwrapped `story.append(t); story.append(Spacer(1, 8))`.
- If the table genuinely is taller than a page, you have too many rows. Split into two tables.
- If the table fits on a page but is being pushed off because the heading + table won't fit together, add `<<PAGEBREAK>>` before the heading.

### Pattern E — stranded final BOX (typically reproducibility)

Page X: open questions, ends with comfortable blank space. Page X+1: lone reproducibility BOX with most of the page blank.

**Fix:** Drop the `## Reproducibility` heading. Move the title into the BOX:

```
[BOX|gray|Reproducibility — everything reproduces end-to-end on a workstation]
```

The heading + spacer was what wouldn't fit on page X. The BOX alone slides up onto page X.

### Pattern F — `<<PAGEBREAK>>` causes a 1-block page

You added `<<PAGEBREAK>>` to fix Pattern C, but now the section after it has only 1 BOX that ends well before the page bottom, and the next `<<PAGEBREAK>>` strands it.

**Fix:** Remove the second `<<PAGEBREAK>>`. The single BOX should flow into the next section. Page-breaks should only sit at boundaries that genuinely separate two pages of content.

## How long this should take

For a fresh 11-page report:

- First render: ~30 seconds (the renderer is fast).
- First verification pass: ~3-5 minutes (skim each page).
- First edit pass: ~10 minutes (typically 2-3 patches needed).
- Second render + verify: ~2 minutes.
- Second edit pass: ~5 minutes.
- Third render + verify + ship: ~2 minutes.

Total: ~25 minutes once you know the patterns. If it's taking longer, you're either over-tightening or fighting the wrong pattern. Re-read this catalog.

## Anti-pattern: don't render and ship without verifying

The renderer is good but not magic. A first render will almost always have at least one orphan or overflow. Reports shipped without the verification loop are the ones that look like "here's some content I rendered to PDF" — exactly the failure mode this skill exists to avoid.
