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

1. Check for uncommitted local changes first. `data/` and `projects/` are git-ignored so
   they're never at risk — but if a *tracked* file has local edits, say so and ask before
   proceeding rather than discarding anything.
2. Fetch and update: pull `main` (the trusted shared copy) and, if the maintainer has asked
   the team to track it, `develop`. Never force anything; never discard their work.
3. If git reports a conflict or anything unexpected, **stop and explain it in plain
   language**, then suggest they ask the maintainer. Do not click through it.

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
