---
description: Promote your finished work into findings/, log it, and push it to your own branch.
argument-hint: "[optional: which experiment / what to share]"
allowed-tools: Bash
---

Follow the **share-work** skill (`.claude/skills/share-work/SKILL.md`) exactly.

What the user wants shared: **$ARGUMENTS**

Reminder of the hard rules: never push to `main` or `develop`, never commit anything from
`data/`, push only to `researchers/<name>`. Show the file list and get confirmation before
copying. Promote the report as **both `report.pdf` and `report.md`**, and make sure the
`HYPOTHESIS_LOG.md` entry records the **dataset + release** and the **cohort & inputs** —
updating an existing "Under analysis" entry rather than adding a duplicate.
