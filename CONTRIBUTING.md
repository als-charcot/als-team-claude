# Contributing to the ALS Team repo

This repo is our shared Claude setup: the rules in `CLAUDE.md` and the skills in
`.claude/skills/`. You don't need to be a coder to contribute — GitHub Desktop has
buttons for everything below. When in doubt, ask the maintainer.

## The basic loop — just ask Claude

You don't need git commands or buttons. In the Code tab:

1. **"Pull the latest from the team repo."** — start of a session.
2. Do your work.
3. **"Share this work with the team."** — when you have something worth keeping.
4. **"What's new from the team since last week?"** — to catch up.

(GitHub Desktop's **Fetch origin → Pull** does step 1 too, if you prefer buttons.)

If git ever shows a conflict or an error you don't understand, **stop and ask the
maintainer** rather than clicking through it. That's the whole safety rule.

## Proposing a change to the rules (`CLAUDE.md`)

The rules in `CLAUDE.md` apply to everyone, so changes are worth a quick discussion.

- Small wording fixes / clarifications: edit `CLAUDE.md`, commit, push.
- Anything that changes how we work (a new statistical rule, a new report
  requirement): **mention it to the team / maintainer first**, then commit.

## Adding a skill

A skill is a folder with a `SKILL.md` file at its root (optionally with `scripts/`,
`references/`, `templates/`).

1. Copy the skill's folder into `.claude/skills/`.
2. **Do not double-wrap.** The path must be
   `.claude/skills/<skill-name>/SKILL.md`, not
   `.claude/skills/<skill-name>/<skill-name>/SKILL.md`.
3. Add a one-line entry to `.claude/skills/INDEX.md` so people can find it.
4. Commit and push.

The starter repo intentionally ships a curated set (see `INDEX.md`). Add a new skill
when a real project needs it — not just in case.

## Doing an analysis, and sharing it

**You have one branch, and it's yours: `researchers/<your-name>`.** It is durable — it
isn't deleted or rewritten. Its history is the record of your work.

- `main` and `develop` are **protected**. You never push to them. The maintainer merges
  work upward into `develop` when the team should build on it.
- You never push to anyone else's branch, and nobody pushes to yours.
- **We don't use pull requests.** You push to your own branch; that's it.

Where the work lives:

- **While you work:** `projects/<your-name>/<experiment>/` — with its own `scripts/` and
  `outputs/`. This is **git-ignored**: private, on your machine only. Scratch, dead ends
  and half-finished work all belong here.
- **When it's finished:** say *"share this work with the team."* Claude promotes the
  deliverable (report PDF, the script, key figures, a short README) into
  `findings/<your-name>/<slug>/`, appends your `HYPOTHESIS_LOG.md` entry, commits it with
  your name, and pushes your branch. See [`findings/README.md`](findings/README.md).
- Repo-root `scripts/` and `outputs/` are **shared examples only** — not personal work.

Negative and inconclusive results are worth sharing. A logged dead end saves the next
person from repeating it.

## The hypothesis log

The hypothesis log is our shared memory. After an analysis, add a short entry
(status, finding with effect size + n, a link to the script/commit, open questions).
Use `templates/HYPOTHESIS_LOG_TEMPLATE.md` as the format. Paste the commit link so
others can trace the evidence.

## Data — never commit it

The PRO-ACT data (`PROACT_ALL_FORMS/`) is distributed separately and is excluded by
`.gitignore`. Never commit patient data — even de-identified — into this repo.
