---
description: Search PubMed for recent papers on your keywords and append them to your running literature list (pubmed-feed.md).
argument-hint: <keywords> [--days N] [--max N] [--since YYYY/MM/DD] [--until YYYY/MM/DD]
allowed-tools: Bash
---

Run the team's PubMed feed for the researcher, then summarize what's new.

The user's request: **$ARGUMENTS**

Do this:

1. If `$ARGUMENTS` contains no keywords (empty, or only flags), ask the user which keywords
   or PubMed query to search, then stop and wait.
2. Otherwise run the script from the workspace root, passing the arguments straight through.
   Use the Python launcher for the OS — `py` on Windows, `python3` on macOS/Linux:

   ```
   py ".claude/skills/pubmed-feed/scripts/pubmed_feed.py" $ARGUMENTS
   ```

   Notes:
   - Default window is the **last 7 days**. Widen with `--days 30`, or set an exact range
     with `--since 2026/06/01 --until 2026/07/13`.
   - Quote multi-word phrases, e.g. `"ALS neurofilament"`. PubMed operators work,
     e.g. `"amyotrophic lateral sclerosis AND TDP-43"` (precise terms give cleaner results).
   - Results append to `pubmed-feed.md`; papers already in the list are skipped, so re-runs
     never duplicate.

3. Report back briefly: how many **new** papers were added, then a short bulleted list of
   their titles + journals. Point to `pubmed-feed.md` for full abstracts.
4. Offer to summarize or dig into any specific paper's abstract.

(This is the same tool as the `pubmed-feed` skill — the skill also runs when you just ask
in plain English. Both are safe to run weekly or on demand with different keywords.)
