---
name: sprint
description: >-
  Run a focused, time-boxed research sprint on ONE question, end-to-end — frame the
  hypothesis, plan the approach, execute the analysis (with parallel agents where useful),
  stress-test the finding with independent adversarial agents, then write it up and log it.
  Use when the user says "start a sprint", "run a research sprint", "let's do a sprint on
  <question>", "sprint on <hypothesis>", or wants to take one question from idea to a
  shareable, trustworthy result.
---

# Research sprint

Guide the researcher through a complete sprint on **one** sharp question. Keep them in the
loop at each stage; you do the technical work. Follow the team's `CLAUDE.md` rules
throughout (effect sizes with p-values, hedge mechanism claims, save files not chat).

## Stage 1 — Frame (get this right before touching data)
- **Prior-art check first:** search `HYPOTHESIS_LOG.md` and `findings/` for existing work on
  this question. If found, summarize who tested what and with which inputs, and ask whether
  to build on it, replicate it, or proceed differently.
- **Register the intent:** append a `HYPOTHESIS_LOG.md` entry with **Status: Under
  analysis** (owner, date, hypothesis, planned inputs) so nobody duplicates it in flight.
  Update that same entry with the result at Stage 5.
- Restate the request as a **testable hypothesis**. Agree **success criteria**: what result
  would actually answer it, the effect size that would matter, and the expected n.
- Confirm the data and which forms/columns (list columns first; never assume).
- Set up the workspace: work in `projects/<name>/<slug>/` on their own branch `researchers/<name>`.
- Copy `templates/SPRINT_TEMPLATE.md` into the project folder and fill in the top.

## Stage 2 — Plan (use plan mode)
- Draft the whole approach before running anything: data prep, method, the exact
  figures/tables, and the statistics (with assumptions). Show it; get the go-ahead.

## Stage 3 — Execute
- Write one end-to-end script in the project's `scripts/`; save figures to `outputs/`.
- **Use parallel agents where they add coverage or speed** — e.g. one agent per subgroup,
  model, or dataset. Fan out, then combine the results.

## Stage 4 — Stress-test (this is what makes the result trustworthy)
- **Use the adversarial-review skill for this stage.** It carries the lenses, the PRO-ACT
  failure catalogue, the claim audit and the negative control.

- Spawn several **independent adversarial agents** to try to *break* the finding, each with
  a different lens, and run the `references/methodology_pitfalls.md` checklist (circular
  design, no confounder adjustment, survivorship / healthy-user bias, multiple testing,
  observational→causal overreach). Keep only what survives.

## Stage 5 — Write up, then offer to share
- Produce the report with the **polished-pdf-reports** skill (the team's 6-part per-finding
  structure). Save it to that experiment's own `outputs/` — which is **private**
  (`projects/` is git-ignored).
- Summarize for the user: what we asked, what we found, how confident, and what's next.
- Then **offer to share it**: if they agree, hand off to the **share-work** skill, which
  promotes the deliverable into `findings/<name>/<slug>/`, appends the entry to
  `HYPOTHESIS_LOG.md` at the repo root, and pushes to their own branch
  `researchers/<name>`. Nothing is shared unless they say so.

## Notes
- **One question per sprint.** If scope creeps, spin the extra question into its own sprint.
- **Time-box it** (a day, or a week). A negative result that is logged is a success.
