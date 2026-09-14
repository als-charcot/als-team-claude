---
description: Show, raise, re-check or follow up the team's open questions.
argument-hint: [due | list | new ... | match <digest> | L-00N]
allowed-tools: Bash
---

Work with the lead register via `scripts/leads.py`. What was asked: **$ARGUMENTS**

If nothing was given, run `python scripts/leads.py due` and report what needs re-checking, in
plain language: the open question, what would resolve it, and how long it has been waiting.

Useful paths:
- `leads.py list --live` — everything open, grouped by what it is waiting for
- `leads.py match <a research-watch .index.md>` — connect new literature to open questions
- `leads.py touch L-00N --note "..."` — record a re-check (never delete a lead)
- `leads.py new --title ... --waiting-on ... --kind ...` — raise one

Always regenerate the index afterwards (the tool does it automatically on write commands).
A keyword match from `match` is a prompt to look, not evidence.
