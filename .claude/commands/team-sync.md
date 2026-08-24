---
description: Pull the team's latest rules, skills and shared findings, then summarise what changed.
argument-hint: "[optional: since <date>]"
allowed-tools: Bash
---

Follow the **team-sync** skill (`.claude/skills/team-sync/SKILL.md`) exactly.

Extra context from the user: **$ARGUMENTS**

Reminder of the essentials: sync from **`origin/main`** (never a plain `git pull` — the
researcher is on their own branch and would get nothing), never force or discard their work,
and finish with a short plain-language digest of what changed. If `$ARGUMENTS` names a time
window, scope the summary to it.
