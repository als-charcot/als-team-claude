---
name: polished-pdf-reports
description: Use this skill whenever the user asks for a "polished PDF", "presentation-quality PDF", "clean report PDF", "share with colleague PDF", "final report" / "final-deliverable PDF" for a research project, a standalone "follow-up report" PDF after new data or a new analysis lands, or wants to convert a Markdown report into a visually-structured deliverable without "boring multi-page paragraphs" or "weird formatting". Produces tight, page-disciplined PDFs using a fixed set of visual primitives (KEYSTAT, STATUS, BOX, QUESTION, four-level callouts) that every assertion sits inside, plus a verification loop that catches orphan callouts and stranded boxes before delivery. Also covers when to ship a separate follow-up PDF (gain/loss framing, comparison table, "0 invalidated" KEYSTAT anchor) instead of amending the original.
license: Internal — Charcot ALS workspace
metadata:
  version: 1.1
  origin: derived from Kabashi/REPORT_FOR_COLLEAGUE.pdf, Kabashi/PROACT_FOLLOWUP.pdf, and CrossDisease/CROSSDISEASE_REPORT.pdf (May 2026)
---

# Polished PDF Reports

## Overview

This skill produces single-deliverable PDF reports that look like a curated briefing rather than a wall of text. It enforces three things:

1. **Every assertion lives in a visual primitive.** Plain prose paragraphs are the exception; KEYSTAT cards, STATUS banners, BOX cards, QUESTION cards, and four-level callouts (`[MEDICAL]` / `[DATA-SCIENCE]` / `[LAY]` / `[DATA]`) are the rule.
2. **Page discipline.** Each finding (image + status + 4 callouts) fits on one page. Tables don't split. No orphan single-callout pages. No half-empty pages with a stranded box. Page breaks are explicit (`<<PAGEBREAK>>`), not implicit.
3. **Verification loop.** After rendering, every page is rasterized at 110 DPI via PyMuPDF and visually checked for orphans, stranded boxes, and overflow. Iteration continues until the layout is clean.

The deliverable is **one** PDF the user can share. Per-experiment / per-section archive PDFs go in a sibling `_archive/` folder.

## When to use

Use this skill when the user wants any of:

- "Make me a polished PDF for my colleague"
- "A final report PDF for project X"
- "A presentation-quality PDF — no boring multi-page paragraphs"
- "A consolidated single-PDF deliverable" for a research project that has accumulated many sub-reports
- "Convert this Markdown report to a PDF that looks like a briefing"
- "Make it visually appealing — KEYSTAT / STATUS / callouts"
- A second-opinion PDF pass on an already-rendered report whose layout has orphan callouts, stranded boxes, or oversized findings

Do NOT use this skill for:

- Plain markdown-to-PDF with no design constraints (use the workspace's `pdf` skill or pandoc directly)
- Forms, fillable PDFs, OCR, PDF manipulation (use the `pdf` skill)
- Slides / Keynote / PowerPoint (different deliverable shape)

## The visual primitives

These are the building blocks. Every report uses these and only these for structured content.

### Cover (top of page 1)

The renderer auto-generates a title block from the build-script's `title=` / `subtitle=` / `cover_meta=[]`. Don't write a title in the markdown — it would duplicate.

### `[KEYSTAT|<stat>|<label>|<context>]`

Big-number callout. Exactly the shape used for "+0.218 / ALS × MS genetic correlation / p = 1.6 × 10⁻³…". Use 2–3 KEYSTATs per cover page to anchor the headline numbers. Each KEYSTAT is one line in the markdown — do not wrap.

```
[KEYSTAT|+0.218|ALS × MS genetic correlation|p = 1.6e-3, n_SNPs = 443k. Specifically neuroimmune.]
```

### `[STATUS|<color>|<label>] body…`

Coloured status badge above a body paragraph. Use immediately under each finding's image. Body can flow onto subsequent non-blank lines (the parser concatenates until a blank line or another directive).

Colors: `green` `amber` `red` `blue` `purple` `gray`.

```
[STATUS|green|H2 supported by independent T2D control]
ALS × MS = +0.218 (95% CI lower bound +0.082)…
```

### `[BOX|<color>|<title>] … [/BOX]`

Multi-line summary card. Use for data-source lists, pipeline summaries, "what was refuted / couldn't be refuted / looks promising" blocks, and the final reproducibility footer. Title goes in the header bar; body supports bullets, bold/italic, and short paragraphs.

```
[BOX|blue|Data sources — all public, all workspace-resident]
- **6 GWAS** (ALS van Rheenen 2021, …)
- **6 GEO transcriptomic datasets** for AD / PD / ALS
[/BOX]
```

### `[QUESTION|<id>|<title>] body…`

Open-question card. Use the trailing "questions for external review" section. Body can flow onto subsequent non-blank lines.

```
[QUESTION|Q1|Concerns we missed in our self-redteams]
The v3 redteam found 11 concerns; v4 found 8 more…
```

### Four-level callouts

Used inside each finding (one of each, in this order):

```
[MEDICAL]: clinical/biological-meaning explanation, 2-4 lines.
[DATA-SCIENCE]: statistical/methodological explanation, 2-4 lines.
[LAY]: plain-English explanation with metaphor where useful, 2-4 lines.
[DATA]: a concrete number or row from the actual data, 2-4 lines.
```

Each renders as a labelled left-bordered block in its own colour (red/blue/green/amber respectively). Each callout flushes the finding's KeepTogether group, so callouts can flow naturally across pages — the heading + image + status group stays atomic; callouts don't.

### `<<PAGEBREAK>>`

Explicit page break. Place between major sections (cover → data sources, data sources → F1, between findings, between "what was refuted" / "couldn't be refuted" / "promising" / "tiers"). The renderer does NOT auto-page-break on `##` — that's the design.

## The page-discipline contract

Each report obeys these rules:

1. **One finding per page.** Heading + image + STATUS + 4 callouts = ~7-9 inches of vertical space. If callouts are tight (2-4 lines each, no longer), it fits.
2. **`<<PAGEBREAK>>` before every `## Finding` section.**
3. **Tables are atomic.** The renderer wraps `add_table()` in `KeepTogether` so multi-row tables don't split. If a long table can't fit on the cover, put `<<PAGEBREAK>>` before the heading + table to push them to their own page.
4. **No more than 4 BOXes per page.** "What was refuted" gets a page; "couldn't be refuted" gets its own page; "promising" gets its own; "tiers" gets its own.
5. **No `## Reproducibility` or `## Open questions` heading sitting alone.** If the BOX following the heading is small, drop the `##` heading and put the title inside the BOX itself (the BOX has its own title bar).
6. **Heading + content inseparable.** If a `##` heading would land at the bottom of a page with content following overflow, add `<<PAGEBREAK>>` before the heading.

## Build pattern

Three files per project:

```
project/
├── reports/
│   ├── REPORT.md                     ← the markdown report
│   ├── REPORT.pdf                    ← rendered output (canonical deliverable)
│   └── _archive/                     ← legacy / per-section reports
└── scripts/reports/
    ├── report_pdf_lib.py             ← the renderer library (copy from this skill)
    ├── build_report.py               ← thin wrapper (copy from templates/)
    └── verify_layout.py              ← PyMuPDF page-rasteriser (copy from this skill)
```

### 1. Copy the library

```bash
cp skills/polished-pdf-reports/scripts/report_pdf_lib.py project/scripts/reports/
cp skills/polished-pdf-reports/templates/build_report.py project/scripts/reports/
cp skills/polished-pdf-reports/scripts/verify_layout.py project/scripts/reports/
```

### 2. Write the markdown

Start from `templates/REPORT_TEMPLATE.md`. Tighten every callout to 2-4 lines. Don't write a title heading — the renderer adds it from build script kwargs.

### 3. Render + verify

```bash
python project/scripts/reports/build_report.py            # renders REPORT.pdf
python project/scripts/reports/verify_layout.py REPORT.pdf  # rasterises pages to _preview/
```

Then read every `_preview/page_NN.png`, looking for:

- Page with only a single orphan callout → tighten preceding callouts so they fit on the previous page
- Page with only one BOX and lots of blank space → drop the `##` heading or merge BOX with previous page's content
- Table split across pages → already handled by KeepTogether on `add_table`; if it still splits, the table is taller than a page (rare — shorten cells)
- Heading orphaned at bottom of page → add `<<PAGEBREAK>>` before the heading

Iterate until clean.

### 4. Archive legacy reports

Once `REPORT.pdf` is the canonical single deliverable, move per-section / draft / writeup PDFs to `reports/_archive/`. The user gets one PDF, not a folder of fifteen.

## Follow-up reports (separate PDF, not amendment)

When new data lands or a previously-blocked analysis becomes runnable, **prefer a separate follow-up PDF** instead of editing the original. Update the original only for defect fixes (wrong number, broken figure, typo). The original report is dated provenance; the follow-up announces itself.

A follow-up PDF is 4-8 pages (typically 6) with this recognisable shape:

1. **Cover** — green STATUS banner, context paragraph linking to original, three KEYSTATs.
   - The third KEYSTAT is the **null-anchor**: `[KEYSTAT|0|Original-report claims invalidated|None. The result is refined, not contradicted...]`. If the follow-up genuinely invalidates something, the `0` becomes the real count.
2. **"What changed" comparison table** — three columns (Aspect / Original / Follow-up). Include an explicit row that names a question or threshold from the original report ("OR > 2 threshold question (your Q4)") so the reader knows you remembered what they asked.
3. **New findings** — 1-2 standard finding pages (heading + image + STATUS + 4 callouts).
4. **"What was gained" + "What was lost"** sections — 2-4 green Gain BOXes and 2-4 amber/gray Loss BOXes. The final loss BOX is typically the **"Loss N (almost none)"** structural counterpart to the "0 invalidated" KEYSTAT, explicitly stating the original's numbers stand correct for the model they describe.
5. **Open Questions Q1-Q3** raised by the follow-up (re-numbered fresh; the follow-up is standalone).
6. **Reproducibility BOX** listing **only the additions** since the original.

Use `templates/FOLLOWUP_TEMPLATE.md` + `templates/build_followup.py` to start. See `references/followup_reports.md` for the full pattern + worked example.

**Naming:** `<TRIGGER>_FOLLOWUP.pdf` (e.g. `PROACT_FOLLOWUP.pdf`) or `<DATE>_FOLLOWUP.pdf` — not `REPORT_v2.pdf`. The original keeps its filename.

## What goes where

- **`SKILL.md`** (this file) — when to use, philosophy, primitives quick reference, build pattern, follow-up pattern
- **`scripts/report_pdf_lib.py`** — the canonical ReportLab-based renderer (do not edit per project; copy verbatim)
- **`scripts/verify_layout.py`** — PyMuPDF page-rasteriser for the verification loop
- **`templates/build_report.py`** — minimal wrapper script for a primary report
- **`templates/build_followup.py`** — minimal wrapper script for a follow-up report
- **`templates/REPORT_TEMPLATE.md`** — example markdown for a primary report, showing every primitive
- **`templates/FOLLOWUP_TEMPLATE.md`** — example markdown for a follow-up (gain/loss + comparison table)
- **`references/visual_primitives.md`** — full reference for KEYSTAT / STATUS / BOX / QUESTION / callout syntax
- **`references/layout_discipline.md`** — page-break rules + worked examples of fixing common overflow problems
- **`references/iteration_loop.md`** — how to use the verification loop, common failure patterns
- **`references/followup_reports.md`** — when to write a follow-up vs amend, structure, naming, worked example

## Provenance

Derived from three production reports built in the Charcot ALS workspace, May 2026:

- `Kabashi/reports/REPORT_FOR_COLLEAGUE.pdf` — 9-page Kabashi review (two analyses, four findings, four open questions)
- `Kabashi/reports/PROACT_FOLLOWUP.pdf` — 6-page follow-up after PRO-ACT data access landed (literal Analysis 1 + bonus NfL, gain/loss framing, "0 invalidated" null-anchor)
- `CrossDisease/reports/CROSSDISEASE_REPORT.pdf` — 11-page CrossDisease consolidated report (four findings, three categories of result-boxes, three tiers of v5 paths, four open questions)

All three PDFs followed the same recipe and survived the same verification loop. The canonical library version is the one with `add_table()` wrapped in `KeepTogether` (CrossDisease, post-fix May 7 2026).
