---
description: Pick up where you left off, and see what the team has done since.
allowed-tools: Bash
---

Follow the **team-sync** skill (`.claude/skills/team-sync/SKILL.md`), both halves, in order.

**First, where this researcher left off.** They have opened a fresh conversation with no
context, so derive it rather than asking: their unclosed **Under analysis** entries in
`HYPOTHESIS_LOG.md`, their most recently modified folders under `projects/<name>/`, their
recent commits on their own branch, and the leads they own (`scripts/leads.py list --owner
<username> --live`).

**Then what changed on the team's side** since they last pulled.

Report unfinished work first, then what is already shared, then what is waiting on them. If
nothing is unfinished, say so and offer the unblocked questions on the register. Never invent
work in progress.
