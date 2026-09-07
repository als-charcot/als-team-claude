---
name: research-watch
description: >-
  Find what is new in ALS research outside PRO-ACT, from sources the team has validated, and
  label every item by how strong the evidence actually is. Use when the user asks what is new
  or recent in a topic, for the latest papers, findings, trials, preprints or news, to catch
  up on the literature, to check whether anyone has published on something, whether a claim
  or a drug or a target has been reported elsewhere, or to keep watch on a topic over time.
  Also use for casual phrasings: "anything new on C9orf72", "what's happening with ASOs",
  "has anyone tried this", "any new trials", "what did I miss this month".
license: MIT
metadata:
  version: 0.1
  status: three sources live, build-out ordered in references/sources.md
---

# Research watch

PRO-ACT tells the team what happened in trials that have already run. This tells them what
is happening now: new papers, new trials, new preprints. It exists because the team asked
to be able to *interrogate* outside research, not just read that somebody announced
something.

**The organising idea: a press release and a randomised trial are not the same kind of
claim, but they arrive looking alike.** So nothing in a digest is presented without its
evidence tier, and nothing is presented that has no resolvable primary-source link.

## Run it

```
python .claude/skills/research-watch/scripts/research_watch.py "ALS neurofilament" --days 30
```

| Flag | Meaning |
|---|---|
| `--days N` | how far back to look (default 30) |
| `--max N` | cap per source (default 25) |
| `--sources` | `pubmed,trials,preprints` — any subset, comma-separated |
| `--out PATH` | digest path (default `research-watch/<date>-<slug>.md`) |
| `--show N` | print only N titles to the console (default: all of them) |

**It is a standalone module, and that is the point.** It is plain Python with no external
dependencies and no API keys, so all the fetching, de-duplication, ranking and tier-labelling
happens deterministically in one command. You are not paying tokens for the work, only for
reading the result.

**Read the console output first; it is usually enough.** Every run prints each item with its
tier tag, so a single command gives you what you need to summarise without opening any file.
Two files are written:

- **`<name>.index.md`** — one line per item, no abstracts. Read **this** one when you need the
  file. Roughly a fifth the size of the full digest.
- **`<name>.md`** — the full digest with abstracts. Open it only for the specific items a
  researcher actually asks about.

Do not read the full digest to write a summary. Use the console output, or the index.

Set `ALS_WATCH_CONTACT` to the researcher's email so the tool identifies itself politely to
NCBI and the other endpoints. No source needs an API key.

**Live sources, and the tier each one carries:**

| Source | Tier | Default |
|---|---|---|
| PubMed / MEDLINE | peer-reviewed publication | yes |
| ClinicalTrials.gov | trial registration, a plan or status change, **not a result** | yes |
| bioRxiv + medRxiv | **preprint, not peer reviewed** | yes |
| openFDA drug labels | **regulatory record**, a label or decision, not a study result | yes |
| Crossref | peer-reviewed publication | **no, opt-in** |

**Why Crossref is opt-in rather than default.** Its relevance ranking is not reliable for
these queries. A search for "ALS neurofilament" returned German-language papers about museums
and archives, because *als* is an ordinary German word. It now post-filters so every query
term must actually appear, which removes the noise but leaves it returning nothing for most
searches, since Crossref frequently carries no abstract to match against. A source that
usually returns nothing while looking like coverage is worse than one nobody switched on, so
it is off by default. Add `--sources ...,crossref` when you want full-phrase journal coverage,
and it stays useful for resolving a DOI when linking news back to a paper.

The full registry of every validated source, what is wired up, what is next, and what is
blocked and why: **`references/sources.md`**. Do not add a source that is not approved
there; the list is a team decision, not a technical one.

## How to use it with a researcher

1. **Turn their question into keywords, and say what you searched.** The tool matches on
   all terms, so "ALS neurofilament" is narrow and "neurofilament" is broad. If a search
   returns nothing, that is a real result about that phrasing, so report it as such and
   offer a broader one rather than quietly widening it yourself.

2. **Lead with the tier, not the headline.** When you summarise a digest, say what kind of
   evidence each item is before you say what it claims. "A preprint, not yet peer
   reviewed, reports..." is the correct shape. Never flatten tiers into "studies show".

3. **Read the source-status block at the top of every digest.** It reports a count per
   source, and says out loud when a source returned nothing or failed. **A source that
   failed makes the digest incomplete**, and you must say so rather than presenting what
   arrived as if it were the whole picture.

4. **Never upgrade a claim.** A trial registration means somebody plans to test something.
   A preprint means somebody wrote it down. A press release is the company's own account.
   None of them is a finding, and the digest's tier labels exist to stop that slide.

5. **Connect news back to the primary source.** If an item is secondary coverage, find the
   paper, trial or announcement underneath it before treating it as anything.

6. **Then offer the obvious next step:** check the item against our own data. The strongest
   use of this tool is "somebody reports X; can we see X in PRO-ACT?" That becomes a
   hypothesis, which means the prior-art check and the register-before-running rule in
   `CLAUDE.md`, and the adversarial review at the end.

## Interrogating a claim, which is the point of the tool

When a researcher asks whether an outside claim holds up, do not answer from the abstract.

- Pull the item and read what was actually measured: design, n, population, outcome,
  effect size and interval.
- Ask whether the claim is even testable in PRO-ACT: are the variables present, is the
  cohort comparable, is the follow-up long enough?
- Run the prior-art check first. Somebody on the team may already have tested it.
- If it is testable, register it in `HYPOTHESIS_LOG.md` as **Under analysis** with the
  outside claim recorded as the motivation, then treat it as a normal experiment, review
  and all.
- If it is not testable with our data, say that plainly and say what would be needed.

**A finding that contradicts an outside claim is a real result** and belongs in the log
with the citation it argues against.

## Digests are local until shared

A digest lands in `research-watch/`, which is git-ignored, so it stays on the researcher's
machine like their `projects/` work. If one is worth the team's attention, promote it the
normal way with **share-work** rather than committing it by hand.

## Honest limits, so nobody over-reads a digest

- **Preprint search is a window scan.** The bioRxiv/medRxiv API has no keyword search (a
  `search=` parameter is silently ignored, which was verified, not assumed), so the tool
  pages the date window and filters locally. Long windows get capped, and the digest says
  so at the top.
- **Three sources is not the field.** Regulatory decisions, conference abstracts, company
  announcements, patents and news are all approved but not yet wired. A quiet digest means
  those three sources were quiet, not that nothing happened.
- **Ranking is keyword frequency plus tier plus recency.** It is a sort order, not a
  judgement of importance. Do not present the top item as the most important one.
