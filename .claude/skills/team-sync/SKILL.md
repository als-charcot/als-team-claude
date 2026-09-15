---
name: team-sync
description: >-
  Bring down the team's latest shared rules, skills and findings, and summarise what changed.
  Use when the user starts a fresh session and needs to pick up where they left off:
  "where did I get to", "what was I working on", "catch me up on my own work",
  "remind me what I was doing", "pick up where I left off". Also when they say
  "pull the latest", "pull from the team repo", "sync with the team",
  "what's new from the team", "what has everyone been working on" — and equally for casual
  phrasings that mean the same thing: "get the latest", "catch me up", "update my setup",
  "grab the newest version", "has anyone shared anything". Also use when they ask to catch
  up on colleagues' shared work.
---

# Sync with the team

Two jobs: get the latest shared work onto their machine, and tell them what changed in
plain language.

## Pull the latest

**Important:** researchers work on their own branch (`researchers/<name>`), but shared
updates — new skills, rule changes, colleagues' findings — land on **`main`**. So a plain
`git pull` pulls only their own branch and silently gets nothing. Always sync **from
`origin/main`**, whatever branch they are on.

1. Check for uncommitted local changes first. `data/` and `projects/` are git-ignored so
   they're never at risk — but if a *tracked* file has local edits, say so and ask before
   proceeding rather than discarding anything.
2. `git fetch origin`, then merge `origin/main` into their current branch:
   `git merge --no-edit origin/main`. Never rebase, never force, never discard their work.
   (A SessionStart hook already attempts this on every launch; running it again is safe and
   is how they catch up if that attempt had to back out.)
3. **If the merge conflicts**, do not leave conflict markers sitting in their tree:
   - `HYPOTHESIS_LOG.md` should resolve itself (`.gitattributes` sets `merge=union`).
   - For anything else, explain in plain language what disagrees. Their own work in
     `findings/<name>/` will essentially never conflict; a conflict in a shared file means
     they edited something they weren't expected to. Offer to keep the team's version, and
     if they're unsure, `git merge --abort` and tell them to ask the maintainer.
4. Confirm what happened: how many commits came down, or "already up to date."

## Then: where THEY left off

A researcher starting a fresh conversation has no context, and neither do you. Before
summarising the team's work, answer the question they actually care about: **what was I in
the middle of?**

You start knowing nothing, so read it off the repository rather than asking:

1. **Who they are and where they are.** Repo-local `git config --local user.name` and the
   current `researchers/<username>` branch. The session hook has already warned them if
   either is wrong.

2. **Questions they registered but have not closed.** Search `HYPOTHESIS_LOG.md` for entries
   whose owner is them and whose **Status is "Under analysis"**. That is the strongest signal
   of unfinished work: they told the team they were working on it and never posted a result.
   Report the hypothesis, the date they registered it, and the planned data and method.

3. **Their own working folders.** List `projects/<name>/` and report the most recently
   modified experiment folders, with what is in them: a script, outputs, a draft report. This
   is git-ignored and local, so it is the only place a half-finished analysis lives.

4. **Their commits on their own branch**, newest first, so they can see what they last
   shared and when.

5. **Leads they own.** `python scripts/leads.py list --owner <username> --live`, plus
   anything from `leads.py due` that is theirs.

Then say, in plain language and in this order: **what is unfinished**, what is already
shared, and what is waiting on them. Offer to resume the unfinished thing.

**If nothing is unfinished, say so plainly** and offer the two questions on the register that
are not blocked by anything. Do not invent work in progress to fill the silence.

## Then summarise what's new

Read the recent history and report, briefly and concretely:

- **New or changed skills / rules** — what capability they now have that they didn't before.
- **New shared findings** — look at `findings/` and the recent entries in
  `HYPOTHESIS_LOG.md`. For each: who found it, the question, and the headline result with
  its **effect size and n**.
- **Anything that affects how they work** (a changed rule in `CLAUDE.md`).

Keep it to a short bulleted digest. Point to the report PDF in `findings/<name>/<slug>/`
for anything they want to read in full, and offer to summarise a specific finding.

## If they ask "what's new since <date>"

Scope the history to that window and summarise only those changes.

## Notes

- This is safe to run at the start of every session; it's the first of the three things
  researchers are asked to do.
- Their own work is never uploaded by this skill — to share, use the **share-work** skill.

## After syncing, check the lead register

Shared rules and findings are only half of what changed. Run:

```
python scripts/leads.py due
```

Any lead listed there has not been looked at in a while. Report them to the researcher in
plain language: what the open question is, and what would resolve it. **A lead is never
deleted** — if it is still open, say so and record the re-check with
`leads.py touch <id> --note "..."`, which pushes the next review out.

If they have run **research-watch** recently, also run
`python scripts/leads.py match <the digest's .index.md>`. That is how new literature gets
connected to questions the team could not answer before. A keyword match is a prompt to
look, never evidence: open the item and decide.
