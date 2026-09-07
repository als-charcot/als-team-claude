---
description: Re-run a finished analysis under every defensible version of its arbitrary choices.
argument-hint: [what to relax, or the analysis path]
allowed-tools: Bash
---

Follow the **expand-findings** skill (`.claude/skills/expand-findings/SKILL.md`).

What to relax: **$ARGUMENTS**

If nothing was named, look at the most recent analysis in the current project folder and
propose the grid yourself: the inclusion filters, the outcome definition and the analysis
window are the usual suspects. Show the researcher the grid and get agreement BEFORE running,
because a grid assembled after seeing the results is not a sensitivity analysis.

Then run `scripts/relax.py`, report the **whole curve** with the original marked, and give the
robustness verdict. Never name a best specification. If the result turns out to be
choice-dependent, that dependency is the honest headline, and anything worth carrying forward
is a **lead** for `LEADS.md`, not a finding.
