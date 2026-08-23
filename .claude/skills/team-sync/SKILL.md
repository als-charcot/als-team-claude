---
name: team-sync
description: >-
  Bring down the team's latest shared rules, skills and findings, and summarise what changed.
  Use when the user says "pull the latest", "pull from the team repo", "sync with the team",
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
