# Contributing to the ALS Team repo

This repo is our shared Claude setup: the rules in `CLAUDE.md` and the skills in
`.claude/skills/`. You don't need to be a coder to contribute — GitHub Desktop has
buttons for everything below. When in doubt, ask the maintainer.

## The basic loop (GitHub Desktop)

1. **Fetch origin → Pull** before you start, so you have everyone's latest work.
2. Make your change (see below).
3. **Commit** with a short message describing what you changed.
4. **Push** so the team gets it.

If a Commit/Push ever shows a conflict or an error you don't understand, **stop and
ask the maintainer** rather than clicking through it.

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

## Doing an analysis

- Work on a branch named for the **hypothesis or question**, not for yourself —
  e.g. `analysis/alice/h024-fvc-slope`. The branch is disposable; you are durable.
- Exploratory / throwaway work can live in `scripts/<your-name>/scratch/`.
- Follow `CLAUDE.md`: write an end-to-end script to `scripts/`, save figures and the
  PDF to `outputs/`, and produce the report in the `polished-pdf-reports` format.
- A **draft pull request** is welcome even for incomplete or negative results — they
  save the next person from repeating the work.

## The hypothesis log

The hypothesis log is our shared memory. After an analysis, add a short entry
(status, finding with effect size + n, a link to the script/commit, open questions).
Use `templates/HYPOTHESIS_LOG_TEMPLATE.md` as the format. Paste the commit link so
others can trace the evidence.

## Data — never commit it

The PRO-ACT data (`PROACT_ALL_FORMS/`) is distributed separately and is excluded by
`.gitignore`. Never commit patient data — even de-identified — into this repo.
