# ALS Team — Claude Code Shared Setup

This repository is our team's shared Claude configuration: the rules Claude follows
(`CLAUDE.md`), the skills it loads (`.claude/skills/`), templates, and references.
Set it up once with a single prompt, then just work inside it — Claude Code uses
everything here automatically and keeps itself up to date.

> **Use Claude Code — the "Code" tab in the Claude desktop app — NOT Cowork.**
> Only the Code tab reads `CLAUDE.md` and auto-loads our skills. Cowork does neither,
> so you'd get a generic Claude with none of our team setup. The interface is the same
> and no coding knowledge is needed — the Code tab just unlocks everything we built.

> **Windows or Mac — both work the same.** Claude figures out your operating system and
> runs the right commands. Folder paths below are written with `/`; on Windows they're
> the exact same folders (shown with `\`).

## One-time setup (no coding required)

### Step 1 — Create a GitHub account

Go to **https://github.com/signup**, use any email, pick a simple lowercase username
(it's public and you'll keep it), verify the emailed code, and choose the **Free**
plan. You don't need an account to set up your workspace, but you'll need one soon — so
we can make the repo private and so you can share work with the team later. Set it up now.

### Step 2 — Set up your workspace with one prompt

1. Open the **Claude desktop app** and go to the **Code** tab.
2. Open a **new, empty folder** anywhere on your computer — this becomes your ALS workspace.
3. Paste this prompt and press enter (approve any install prompts Claude shows):

   > *"If git isn't installed, install it. Then clone
   > https://github.com/emompi/als-team-claude into this folder (use the current
   > directory), and read SETUP.md to set up my workspace."*

Claude does the rest — installs anything needed, clones the team config (rules + skills),
creates the folder structure, and **downloads the PRO-ACT data automatically**. It tells
you when everything is ready.

### What Claude sets up

Indentation shows what's inside what (like an outline):

```
ALS/                    your workspace — put it anywhere
   CLAUDE.md            team rules — load automatically
   .claude/skills/      135 skills — load automatically
   findings/            SHARED: everyone's finished work
      their-name/       one folder per researcher, per finding
   HYPOTHESIS_LOG.md    SHARED: the index of all findings
   templates/  references/  scripts/  outputs/   (shared/examples)
   data/                ALL data, one shared place — git-ignored
      PROACT_ALL_FORMS/ the PRO-ACT data (downloaded for you)
   projects/            PRIVATE: your analyses — git-ignored
      your-name/        Claude creates this per experiment
         fvc-slope/     one experiment: its own scripts/ + outputs/
```

- **Data** lives in the one `data/` folder; every analysis reads from there (never copied
  per project). The dataset is distributed separately — ask the maintainer for the link.
- **Your work** goes in `projects/<your-name>/<experiment>/` — Claude creates it when you
  start a new experiment. It is **private to your machine**.

### Branches — you have your own

You work on **one durable branch: `researchers/<your-name>`**, and you push only there.
`main` and `develop` are protected — you never push to them; the maintainer merges work
upward when the team should build on it. **We don't use pull requests.**

### Sharing your work — you promote it

Nothing syncs by itself. When a piece is finished, say **"share this work with the team."**
Claude copies just the deliverable (report PDF, the script, key figures, a short README)
into `findings/<your-name>/<slug>/`, appends your entry to `HYPOTHESIS_LOG.md`, and pushes
your branch. See [`findings/README.md`](findings/README.md) for exactly what is and isn't
shared.

### The hard rules

1. **One ALS folder.** Put it anywhere, but everything lives inside it.
2. **It IS the repo** — never move or rename `CLAUDE.md` or `.claude/`.
3. **All data lives in `data/`** — one shared copy, never duplicated per project.
4. **Your analyses go in `projects/<your-name>/<experiment>/`** (Claude creates it) and
   read from `data/`.
5. **Never commit patient data.** `data/` and `projects/` are git-ignored for you.
6. **You push only to `researchers/<your-name>`** — never to `main` or `develop`.

## Using it — the golden rule

**Always open your ALS folder with the Code tab.** Because the rules and skills sit at
the top of that folder, opening it (or any project inside it) loads everything
automatically. Then just tell Claude which project and where the data is:

> "Start a new experiment called `fvc-slope`. The data is in `data/PROACT_ALL_FORMS`. Show
> how ALSFRS-R declines over time for bulbar vs limb onset, save the figures, and write it
> up as a polished PDF."

(Claude will create `projects/<your-name>/fvc-slope/` and work there.)

Claude follows the team rules — it writes a script, saves figures, and produces a
report in our standard format. You don't install Python, libraries, or virtual
environments yourself: Claude Code sets those up and runs them for you.

## Staying current — automatic

Each time you open your ALS folder in the Code tab, Claude **automatically pulls the
latest rules and skills**. You never have to remember to update. Your `data/` and
`projects/` folders are git-ignored, so updates never touch your data or your work.

## What's in here

- `CLAUDE.md` — the rules Claude follows for our work
- `.claude/skills/` — the team's skills (see `INDEX.md` there)
- `findings/` — **the team's shared, finished work**, one folder per researcher
- `HYPOTHESIS_LOG.md` — **the index of every shared finding**
- `templates/` — report, sprint and hypothesis-log templates
- `references/` — shared reference docs (e.g., methodology pitfalls)
- `scripts/`, `outputs/` — shared/example material only, **not** personal work

## The three things you'll ever need to say

| When | Say this |
|---|---|
| Start of a session | *"Pull the latest from the team repo."* |
| You have something worth keeping | *"Share this work with the team."* |
| Catching up | *"What's new from the team since last week?"* |

Say it however comes naturally — "get the latest", "save this", "send it up" all work.

## Data note

This repo is set up for **de-identified PRO-ACT** data. Do not put
patient-identifiable data here. The PRO-ACT data is distributed separately (Google
Drive link above) and is never committed to this repo.

## Help

Ask the maintainer — happy to help you get set up or unstuck.
