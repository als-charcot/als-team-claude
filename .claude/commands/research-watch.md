---
description: Find what is new in ALS research from the team's validated sources, labelled by evidence tier.
argument-hint: <keywords> [--days N]
allowed-tools: Bash
---

Follow the **research-watch** skill (`.claude/skills/research-watch/SKILL.md`).

Search for: **$ARGUMENTS**

If no keywords were given, ask what topic to watch. Run the harvester, then summarise the
digest for the researcher **leading with the evidence tier of each item, never the headline**.
Report any source that failed or returned nothing. Finish by offering the obvious next step:
whether the most interesting claim could be tested against PRO-ACT, which means a prior-art
check and a hypothesis-log entry before anything runs.
