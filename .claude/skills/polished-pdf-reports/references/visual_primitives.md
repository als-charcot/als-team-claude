# Visual primitives — full reference

This is the complete syntax reference for every primitive the renderer understands. Anything not on this list either renders as a plain paragraph or breaks.

## `<<PAGEBREAK>>`

Forces a page break. Place on its own line with blank lines on either side.

```
…some content…

<<PAGEBREAK>>

…next page content…
```

The renderer does **not** auto-page-break on `##` headings. All page breaks are explicit. This is intentional — it makes layout deterministic.

## `[KEYSTAT|<stat>|<label>|<context>]`

Big-number callout. Three pipe-separated fields:

- `<stat>` — the number itself, e.g. `+0.218`, `49`, `3 / 3`, `1.66`. Renders large and bold.
- `<label>` — short descriptor, e.g. `ALS × MS genetic correlation`. Renders bold-medium next to the stat.
- `<context>` — one-line context: p-value, n, comparator, sanity-check. Renders small under the label.

**Hard rules:**
- One physical line in the markdown source. No wrapping.
- 2–3 KEYSTATs per cover page. More than 3 dilutes the headline.
- No markdown-formatting inside any field — these are rendered directly.

```
[KEYSTAT|+0.218|ALS × MS genetic correlation|p = 1.6e-3, n_SNPs = 443k. Specifically neuroimmune.]
```

## `[STATUS|<color>|<label>] body…`

Coloured banner with bold label and a body paragraph. Used:

- Once on the cover, just under the title (overall project status).
- Once under each finding's image (this finding's status).
- Optionally once in the "How to read this report" section (caveats).

**Colors** (must be one of these — typo'd colours fall back to gray):

| name | hex | typical use |
|------|-----|-------------|
| `green` | #27ae60 | supported, passing, on-track |
| `amber` | #e67e22 | mixed, weakened, partial |
| `red` | #c0392b | refuted, blocked, failed |
| `blue` | #2874a6 | informational, multi-layer, neutral-positive |
| `purple` | #8e44ad | exploratory, novel |
| `gray` | #7f8c8d | caveat, neutral |

**Body parsing:** the body starts on the same line after `]` and continues across subsequent non-blank lines until either:
- A blank line
- Another directive (`#`, `<<`, `[`, `![`, `---`, `|`)

```
[STATUS|green|H2 supported by independent T2D control]
**ALS × MS = +0.218** (95% CI lower bound +0.082, p = 1.6 × 10⁻³)
is comparable to ALS × AD = +0.250.
```

The above renders as one paragraph with the `**bold**` honored.

## `[BOX|<color>|<title>] … [/BOX]`

Multi-line summary card. Title in a coloured header bar, body underneath. Body supports:

- Bullets (`- ` or `* `)
- Bold (`**…**`) and italic (`*…*`)
- Inline code (backticks) — rendered as italic
- Short paragraphs (multiple body lines)

Same colour set as `STATUS`.

**Rules:**
- Always close with `[/BOX]` on its own line.
- Don't put another `BOX` or directive inside.
- Keep BOXes short — a tall BOX won't fit if there are 4 of them on a page.

```
[BOX|blue|Data sources — all public, all workspace-resident]
- **6 GWAS** (ALS van Rheenen 2021, …) from GWAS Catalog FTP
- **6 GEO transcriptomic datasets** for AD / PD / ALS post-mortem brain
- **AnswerALS plasma proteomics + ALSFRS_R clinical** (n = 297)
Total ~3 GB on disk. End-to-end ~3 hours.
[/BOX]
```

## `[QUESTION|<id>|<title>] body…`

Open-question card. Three pipe-separated fields:

- `<id>` — short identifier, e.g. `Q1`, `Q2`. Rendered as a numbered tab.
- `<title>` — the question itself, framed declaratively (e.g. "Whether X matches your domain prior").
- `body` — same body-flow rules as `STATUS`.

Used in the trailing "open questions for external review" section. 3–6 questions is the sweet spot.

```
[QUESTION|Q2|Whether the ALS-MS r_g matches your domain prior]
The magnitude is roughly +0.10 above what we expected based on the
immune-related-ALS-genes literature. Is this within the band of
plausible numbers, or does it hint at a methodology issue?
```

## Four-level callouts

Each callout starts a new paragraph with one of four labels:

```
[MEDICAL]: clinical/biological-meaning explanation, 2-4 lines.
[DATA-SCIENCE]: statistical/methodological explanation, 2-4 lines.
[LAY]: plain-English explanation with metaphor where useful, 2-4 lines.
[DATA]: a concrete number or row from the actual data, 2-4 lines.
```

Each renders with a coloured left border and a small uppercase label:

| directive | label | left-border colour |
|-----------|-------|--------------------|
| `[MEDICAL]` | CLINICAL / MEDICAL | red `#c0392b` |
| `[DATA-SCIENCE]` | DATA-SCIENCE / STATISTICS | blue `#2874a6` |
| `[LAY]` | PLAIN ENGLISH | green `#27ae60` |
| `[DATA]` | CONCRETE DATA EXAMPLE | amber `#e67e22` |

**Body parsing:** same rule as STATUS — flows across non-blank lines until a directive or blank line.

**Rules:**
- Use all four per finding, in the order MEDICAL → DATA-SCIENCE → LAY → DATA.
- 2–4 lines each. Tighter is better. Padding = overflow.
- The DATA callout MUST contain a literal number or row from the data, not a paraphrase. "MAF q = 1.5 × 10⁻⁸ in GSE5281" — not "MAF was strongly significant".
- Each callout flushes the finding's KeepTogether group, so callouts can flow across pages naturally. The heading + image + STATUS are atomic; callouts aren't.

## Tables

Standard Markdown pipe tables work. The renderer auto-styles them with the Charcot palette (light-green header band, alternating row tints) and wraps them in `KeepTogether` so they don't split across pages.

```
| # | Claim | Status |
|---|-------|--------|
| H1 | Mito Complex I + ribosome cross-ND | refuted (plasma); brain untested |
| **H2** | **ALS distinct autoimmune sub-axis** | **supported (T2D-confirmed)** |
```

**Rules:**
- Keep cell text short — long cells force wrap into 3+ lines and bloat the table.
- Bold (`**…**`) inside cells is honoured.
- Tables are atomic. If your table is too tall to fit on the current page, the renderer pushes it to the next page and leaves a gap. Use `<<PAGEBREAK>>` before the table to push the heading along with it.

## Images

Standard Markdown image syntax:

```
![Caption text becomes the figure caption](../figures/fig01.png)
```

The renderer:
- Resolves relative paths against the markdown file's parent dir
- Falls back to `<parent>/figures/<filename>` if the relative path doesn't exist
- Caps height at 2.6 inches (full text width)
- Uses the alt text as a small italic caption

**Rules:**
- Path matters — keep figures alongside the markdown or in a sibling `figures/` folder.
- Caption goes in the `[alt text]` slot, not after.
- Don't include images larger than 2.6 inches tall unless you increase `max_h` in the parser.

## Headings

| markdown | renders as | when to use |
|----------|------------|-------------|
| `## ` | section heading (H1 in the PDF, large bold) | major sections: Hypotheses, Findings, What was refuted |
| `### ` | finding heading (H2 in PDF) — wrapped with next image+status as KeepTogether | not normally used in the polished format; F1/F2 etc use `##` |
| `#### ` | sub-heading | rare |

The first `## ` of the document is suppressed (the title comes from the build script). All subsequent `## ` headings render normally.

## What's intentionally absent

Things this format does NOT support:

- **Footnotes / endnotes** — put context inside `[DATA]` callouts or BOXes instead.
- **HTML embeds** — strip them.
- **Math (LaTeX)** — write Greek letters directly (`ρ`, `χ²`); for inequalities use `≤ ≥`.
- **Multi-column layout** — every primitive is full-text-width.
- **Auto-numbered headings** — number findings in the heading text itself ("Finding F1 — …").

If you find yourself wanting any of these, you're probably writing the wrong kind of report.
