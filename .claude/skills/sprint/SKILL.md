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
- Restate the request as a **testable hypothesis**. Agree **success criteria**: what result
  would actually answer it, the effect size that would matter, and the expected n.
- Confirm the data and which forms/columns (list columns first; never assume).
- Set up the workspace: a branch `analysis/<name>/<slug>` and `projects/<name>/<slug>/`.
- Copy `templates/SPRINT_TEMPLATE.md` into the project folder and fill in the top.

## Stage 2 — Plan (use plan mode)
- Draft the whole approach before running anything: data prep, method, the exact
  figures/tables, and the statistics (with assumptions). Show it; get the go-ahead.

## Stage 3 — Execute
- Write one end-to-end script in the project's `scripts/`; save figures to `outputs/`.
- **Use parallel agents where they add coverage or speed** — e.g. one agent per subgroup,
  model, or dataset. Fan out, then combine the results.

## Stage 4 — Stress-test (this is what makes the result trustworthy)
- Spawn several **independent adversarial agents** to try to *break* the finding, each with
  a different lens, and run the `references/methodology_pitfalls.md` checklist (circular
  design, no confounder adjustment, survivorship / healthy-user bias, multiple testing,
  observational→causal overreach). Keep only what survives.

## Stage 5 — Write up, log, and share
- Produce the report with the **polished-pdf-reports** skill (the team's 6-part per-finding
  structure). Save it to `outputs/`.
- Append a **hypothesis-log entry** (`templates/HYPOTHESIS_LOG_TEMPLATE.md`): status,
  finding with effect size + n, evidence / commit link, open questions.
- Summarize for the user: what we asked, what we found, how confident, and what's next.

## Notes
- **One question per sprint.** If scope creeps, spin the extra question into its own sprint.
- **Time-box it** (a day, or a week). A negative result that is logged is a success.
