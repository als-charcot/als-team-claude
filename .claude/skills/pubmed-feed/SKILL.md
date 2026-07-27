---
name: pubmed-feed
description: >-
  Search PubMed for recent papers on the user's keywords and append their titles and
  abstracts to a running literature list (pubmed-feed.md). Use whenever the user wants to
  check, pull, or update recent literature; find new papers, articles, or abstracts on a
  topic; asks "what's new on <topic>" or "any recent papers on <topic>"; searches PubMed by
  keyword or date range; or wants a weekly/regular literature check. Works for ALS and any
  other topic. No account needed — uses NCBI's public API.
---

# PubMed feed

A ready-to-run literature hook. The researcher just asks in plain English — no terminal,
no slash command. When their request is about finding or keeping up with recent papers,
run the bundled script and report what's new.

## When to use

Trigger on requests like: "any new ALS neurofilament papers?", "update my reading list",
"what came out on TDP-43 this month", "check PubMed for ALS biomarker studies", "run my
weekly literature check", "find recent abstracts on <topic>".

## How to run it

1. **Keywords** — take them from the request. If none are given, ask which keywords or
   PubMed query to use, then wait.
2. **Time window** — default is the **last 7 days**. Map plain language: "this month" →
   `--days 30`, "last 3 months" → `--days 90`; an explicit range →
   `--since YYYY/MM/DD --until YYYY/MM/DD`.
3. **Run** from the workspace root, using the OS Python launcher (`py` on Windows,
   `python3` on macOS/Linux):

   ```
   py ".claude/skills/pubmed-feed/scripts/pubmed_feed.py" "<keywords>" --days <N>
   ```

   Optional flags: `--max N` (default 20), `--since` / `--until`, `--out <file>`
   (default `pubmed-feed.md`). Quote multi-word phrases; `AND` / `OR` work.

4. **Report back**: how many **new** papers were added, then a short bulleted list of their
   titles + journals. Point to `pubmed-feed.md` for full abstracts. Papers already in the
   list are skipped automatically, so re-runs never duplicate.

## Notes

- PubMed search is **public — no account needed**. An optional free NCBI API key (set the
  `NCBI_API_KEY` environment variable) only raises the rate limit.
- Safe to run **on demand** (just ask) or **weekly** — to automate it, the user can ask
  Claude to schedule a recurring run.
- Every entry saved includes title, authors, journal, date, PMID + link, DOI, and abstract.
