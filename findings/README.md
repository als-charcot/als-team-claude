# findings/ — the team's shared, finished work

This folder is the one place where a researcher's work becomes **visible to the team**.
Everything else you do stays on your machine (`projects/` and `data/` are git-ignored).

## How work gets here

You don't copy things in by hand. When an analysis is finished, say to Claude:

> "Share this work with the team."

Claude promotes the deliverable here, adds your entry to `HYPOTHESIS_LOG.md`, and pushes it
to **your own branch** (`researchers/<your-name>`). The maintainer merges it into `develop`
when the team should build on it.

## Layout

```
findings/
└── <your-name>/
    └── <short-slug>/
        ├── README.md      the question, the finding (effect size + n), caveats, how to re-run
        ├── report.pdf     the polished report (for people)
        ├── report.md      the same report in markdown (for Claude to search/quote)
        ├── analysis.py    the end-to-end script that produced it
        └── *.png          key figures
```

## What belongs here

- **Finished** work — an analysis you'd be willing to have a colleague build on.
- Negative and inconclusive results **do** belong here. A logged dead end saves the next
  person weeks.

## What does not belong here

- Raw or derived **patient data** — never, even de-identified. It lives only in `data/`.
- Scratch work, dead ends in progress, half-written scripts — those stay in `projects/`.
- Very large files (> ~10 MB), e.g. big interactive HTML charts. Keep those local and
  share the PDF plus a static PNG instead.
