# ALS Team — Claude Code Shared Setup

This repository holds our team's shared Claude configuration: the rules Claude
follows (`CLAUDE.md`), a curated set of skills (`.claude/skills/`), and templates.
Clone it once, and Claude Code uses everything here automatically.

## One-time setup (no coding required)

### Step 1 — Get the PRO-ACT data

Download the shared data folder and save it somewhere on your computer (e.g. your
Documents folder). It contains all the PROACT CSV files the analyses need.

> **📁 [Download PRO-ACT data from Google Drive](DRIVE_LINK_HERE)**

Once downloaded, note the path to that folder — you'll point Claude at it when running
analyses (e.g. `C:\Users\yourname\Documents\PROACT_ALL_FORMS`).

### Step 2 — Clone this repo

1. Go to **https://github.com/emompi/als-team-claude** in your browser.
2. Click the green **Code** button → **Download ZIP** → unzip it anywhere you like.
   (Or if you use GitHub Desktop: File → Clone Repository → URL → paste the link above.)

### Step 3 — Open with Claude

Open the unzipped folder in the **Claude desktop app** (Code tab) or run `claude`
inside it from a terminal. That's it — Claude reads `CLAUDE.md` and loads all the
skills automatically.

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

When the maintainer updates the rules or adds a skill, get the latest by re-downloading
the ZIP (same link above), or — if you cloned with GitHub Desktop — click
**Fetch origin** then **Pull**.

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
