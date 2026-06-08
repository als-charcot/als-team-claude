# ALS Team — Claude Code Shared Setup

This repository holds our team's shared Claude configuration: the rules Claude
follows (`CLAUDE.md`), a curated set of skills (`.claude/skills/`), and templates.
Clone it once, and Claude Code uses everything here automatically.

## One-time setup (no coding required)

1. **Install GitHub Desktop** — a free app with buttons instead of commands:
   https://desktop.github.com
2. **Clone this repo** — in GitHub Desktop: File → Clone Repository → pick this repo
   → choose where to save it on your computer.
3. That's it. The folder on your computer now has everything.

## Using it

1. Open the cloned folder with **Claude Code** (`claude` in the folder, or open the
   folder in the Claude desktop app's Code tab).
2. Claude automatically reads `CLAUDE.md` and loads the skills in `.claude/skills/`.
   You don't have to "turn anything on."
3. Ask for what you need — for example:
   - "Run an exploratory analysis on the ALSFRS-R form."
   - "Test whether baseline FVC predicts ALSFRS-R progression slope."
   - "Write that up as a polished PDF report."
   Claude follows the team rules: it saves a script, saves figures, and produces a
   report in our standard format.

## Staying current

When someone updates the rules or adds a skill, get it by clicking **Fetch origin**
(then **Pull**) in GitHub Desktop. Do this every so often, or whenever told there's
an update.

## Contributing back

Found a useful analysis pattern? Add a skill or improve `CLAUDE.md`, then **Commit**
and **Push** in GitHub Desktop so the rest of the team gets it. Ask the maintainer
if you're unsure.

## What's in here

- `CLAUDE.md` — the rules Claude follows for our work
- `.claude/skills/` — the team's skills (see `INDEX.md` there)
- `templates/` — report and hypothesis-log templates
- `references/` — shared reference docs (e.g., methodology pitfalls)
- `scripts/` — where analysis scripts get saved
- `outputs/` — where figures and reports get saved

## Data note

This repo is set up for **de-identified PRO-ACT** data. Do not put
patient-identifiable data here. The PRO-ACT data itself is distributed separately,
not committed to this repo.

## Help

Ask the maintainer — happy to help you get set up or unstuck.
