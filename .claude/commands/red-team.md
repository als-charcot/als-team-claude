---
description: Adversarially audit a finding against what the analysis actually computed, before it ships.
argument-hint: <the finding, or a path to the analysis>
allowed-tools: Bash
---

Follow the **adversarial-review** skill (`.claude/skills/adversarial-review/SKILL.md`) exactly.

What to review: **$ARGUMENTS**

If nothing was named, review the most recent finding in the current project folder. Work the
six phases: pin the state of record, enumerate the claim surface, fan out independent
reviewers on separate lenses, interrogate the instruments against
`references/failure-modes.md`, fix at source and re-derive, then record what was withdrawn
and why. Reviewers are read-only. Fix the script, never the sentence.
