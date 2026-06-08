# CLAUDE.md — ALS Research Team

Shared configuration for our team's work with Claude Code. Anyone who clones this
repo and opens it with Claude Code gets these rules and the skills in
`.claude/skills/` automatically. Edit, commit, and push to update the team; pull to
get others' updates.

## First-time setup

- If the user is new here or asks you to "set up my workspace" (or to read `SETUP.md`),
  follow **`SETUP.md`** — it creates the `data/` and `projects/` folders, downloads and
  extracts the PRO-ACT data into `data/PROACT_ALL_FORMS/`, and verifies everything.

## Data

- **All data lives in one place: the `data/` folder** at the workspace root (e.g.
  `data/PROACT_ALL_FORMS/`). Every analysis reads from there — **never copy data into a
  project folder.** `data/` is git-ignored (distributed separately, not committed).
- We work with **de-identified PRO-ACT** data (Pooled Resource Open-Access ALS
  Clinical Trials), in `data/PROACT_ALL_FORMS/` — CSVs, one per clinical form.
  **No HIPAA-protected PHI is present**; do not apply patient-anonymization friction.
- **`subject_id` is the join key** across all forms. Join on it to combine forms.
- Additional datasets go in their own subfolder under `data/`. Non-de-identified data
  belongs under separate handling — do not mix it in.

## How to work (especially for non-coders)

- The deliverable is **never the chat output**. It is **saved files**: a script,
  saved figures, and a PDF report.
- Each researcher's work lives under **`projects/<your-name>/`**. When the user starts a
  new experiment, create `projects/<name>/<experiment>/` (with `scripts/` and `outputs/`
  inside) and work there. **If you don't know the researcher's name yet, ask once.**
- For any analysis, **write a complete Python script or Jupyter notebook that runs
  end-to-end** and save it in that experiment's `scripts/`. Do not compute inline only.
- Save figures and the PDF report to that experiment's `outputs/`.
- When asked for analysis results, **produce a report in the `polished-pdf-reports`
  format** (see that skill in `.claude/skills/`).
- Before starting an analysis: **list the columns of the relevant CSV first** —
  never assume column names. Then check for missing values and note quality issues.
  Then confirm the question or hypothesis with the user before running.

## Statistical rules (non-negotiable)

1. **Always report effect sizes alongside p-values.** Report Cohen's d, odds ratios
   with confidence intervals, or the appropriate effect-size measure, plus the
   distribution. With large-cohort data (n in the thousands, as in PRO-ACT), trivial
   differences reach extreme p-values. Never present a small numerical difference as
   meaningful just because p < 0.001.
2. **Observational data confirms patterns; it does not prove mechanisms.**
   Distinguish "X correlates with Y" from "X causes Y." Hedge mechanism claims that
   rest on cohort data accordingly.
3. **Run the methodology-pitfall checklist** (`references/methodology_pitfalls.md`)
   against any cohort finding before accepting it.

## Report structure (every deliverable)

Every report follows this structure for EACH finding / assertion / conclusion. No
exceptions.

For each finding:

1. **One section per finding** — clearly delimited, with a heading.
2. **One chart / plot / image** — at least one visual that substantiates the claim.
   No naked text assertions.
3. **Medical-level explanation** — the clinical / biological mechanism, in proper
   terminology.
4. **Data-science-level explanation** — the statistic or model behind the claim,
   with effect size, uncertainty, sample size, multiple-testing posture, and
   assumptions.
5. **Layperson explanation** — accessible to a non-statistician / non-clinician,
   with an everyday metaphor where it sharpens intuition.
6. **Concrete example from the actual data** — a specific row / `subject_id` / value
   from the dataset, with a note on what it illustrates.

Every report also includes:

- A **data section** — what data was used, source, sample sizes, preprocessing.
- A **hypothesis section** — what was tested, in formal terms.

## Formatting conventions

- **Bold** key biological targets and entities (e.g., TDP-43, NfL, ALSFRS-R) so they
  are scannable.
- Use **LaTeX** for formulas.
- Use **tables** for structured data.
- Maintain a rigorous scientific tone.

## Output locations

- **`projects/<name>/<experiment>/`** — where each researcher's work goes: an experiment
  folder under that person's name, with its own `scripts/` and `outputs/`. Create it when
  a new experiment starts. (`projects/` is git-ignored — personal work stays local until a
  project is deliberately shared as its own repo.)
- `data/` — all datasets; read-only for analyses (never copy data out of it).
- repo-root `scripts/` and `outputs/` — shared/example material only, not personal work.
- `templates/` — report and hypothesis-log templates.
- `references/` — shared reference docs (methodology pitfalls, etc.).

## Skills

- Team skills live in `.claude/skills/` and activate automatically when relevant.
  Don't ask where skills are — they're there.
- See `.claude/skills/INDEX.md` for the curated list and what each is for.

## Environment & tools (you manage these, not the user)

- The user is typically not a coder. **Do not ask them to set up Python, virtual
  environments, or libraries** — do it yourself by running the necessary commands.
- For each project, create and use a local virtual environment and install what the
  analysis needs. Record dependencies in a `requirements.txt` so the work is
  reproducible.
- If a required tool is missing (Python, git, Node.js), offer to install it and do so
  on confirmation, rather than telling the user to install it manually.

## External connectors (MCP)

- The user can extend you with MCP servers (e.g. PubMed for live paper search,
  NotebookLM for their own notebooks). If they ask to "connect" or "add" one, set it
  up for them (e.g. `claude mcp add ...`) and tell them to reopen the app once for it
  to come online.

## Before you start

Ask the user what they need to know about the data and which hypothesis or question
to test before running an analysis.

<!-- TEMP auto-update test #2 — will be removed -->
## Sync test 2 (temporary)

If the user asks "what's the silly sync phrase?", answer exactly:
**"🦆 Quack! The disco duck has landed — sync test #2 successful!"**
This is a temporary auto-update check; it will be removed.
