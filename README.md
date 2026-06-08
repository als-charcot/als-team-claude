# ALS Team — Claude Code Shared Setup

This repository is our team's shared Claude configuration: the rules Claude follows
(`CLAUDE.md`), the skills it loads (`.claude/skills/`), templates, and references.
Download it once, work inside it, and Claude Code uses everything here automatically.

> **Use Claude Code — the "Code" tab in the Claude desktop app — NOT Cowork.**
> Only the Code tab reads `CLAUDE.md` and auto-loads our skills. Cowork does neither,
> so you'd get a generic Claude with none of our team setup. The interface is the same
> and no coding knowledge is needed — the Code tab just unlocks everything we built.

## One-time setup (no coding required)

### Step 1 — Create a GitHub account

Go to **https://github.com/signup**, use any email, pick a simple lowercase username
(it's public and you'll keep it), verify the emailed code, and choose the **Free**
plan. You don't need an account to download this repo, but you'll need one soon to
join project repos and get updates — so set it up now.

### Step 2 — Make your ONE ALS folder

1. Go to **https://github.com/emompi/als-team-claude** → green **Code** button →
   **Download ZIP** → unzip it **anywhere you like** on your computer.
2. This unzipped folder **is your ALS workspace** — `CLAUDE.md` and `.claude/skills/`
   sit at its top, so Claude loads them automatically. Rename it `ALS` if you like.

### Step 3 — Add the data and a projects folder

Inside your ALS folder, you'll keep two folders that are **git-ignored** (never
committed, never shared through this repo):

```
ALS\                       <- this folder is the downloaded repo; put it anywhere
├── CLAUDE.md              <- team rules        (auto-loaded)
├── .claude\skills\        <- team skills       (auto-loaded)
├── templates\  references\  scripts\  outputs\
├── PROACT_ALL_FORMS\      <- the data (from Google Drive) — git-ignored
└── projects\              <- your analyses, one subfolder each — git-ignored
    └── fvc-slope\
        ├── scripts\
        └── outputs\
```

- **Data:** download the PRO-ACT data and put it in `PROACT_ALL_FORMS/` inside your
  ALS folder.

  > **📁 [Download PRO-ACT data from Google Drive](DRIVE_LINK_HERE)**

- **Your work:** make a new subfolder under `projects/` for each analysis.

### The hard rules

1. **One ALS folder.** Put it anywhere, but everything lives inside it.
2. **It IS the repo** — never move or rename `CLAUDE.md` or `.claude/`.
3. **Data goes in `PROACT_ALL_FORMS/`**; every analysis goes in a `projects/` subfolder.
4. **Never commit patient data.** `PROACT_ALL_FORMS/` and `projects/` are git-ignored
   for you.

## Using it — the golden rule

**Always open your ALS folder with the Code tab.** Because the rules and skills sit at
the top of that folder, opening it (or any project inside it) loads everything
automatically. Then just tell Claude which project and where the data is:

> "Let's work in `projects\fvc-slope`. The data is in `PROACT_ALL_FORMS`. Show how
> ALSFRS-R declines over time for bulbar vs limb onset, save the figures, and write it
> up as a polished PDF."

Claude follows the team rules — it writes a script, saves figures, and produces a
report in our standard format. You don't install Python, libraries, or virtual
environments yourself: Claude Code sets those up and runs them for you.

## Staying current

When the maintainer updates the rules or skills, get the latest by re-downloading the
ZIP (same link above), or — if you cloned with GitHub Desktop — click **Fetch origin**
then **Pull**. Your `PROACT_ALL_FORMS/` and `projects/` folders are git-ignored, so
updates never touch your data or your work.

## What's in here

- `CLAUDE.md` — the rules Claude follows for our work
- `.claude/skills/` — the team's skills (see `INDEX.md` there)
- `templates/` — report and hypothesis-log templates
- `references/` — shared reference docs (e.g., methodology pitfalls)
- `scripts/`, `outputs/` — shared/example analysis scripts and outputs

## Data note

This repo is set up for **de-identified PRO-ACT** data. Do not put
patient-identifiable data here. The PRO-ACT data is distributed separately (Google
Drive link above) and is never committed to this repo.

## Help

Ask the maintainer — happy to help you get set up or unstuck.
