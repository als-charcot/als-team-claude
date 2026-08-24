# CLAUDE.md — ALS Research Team

Shared configuration for our team's work with Claude Code. Anyone who clones this
repo and opens it with Claude Code gets these rules and the skills in
`.claude/skills/` automatically. Edit, commit, and push to update the team; pull to
get others' updates.

## First-time setup

- If the user is new here or asks you to "set up my workspace" (or to read `SETUP.md`),
  follow **`SETUP.md`** — it creates the `data/` and `projects/` folders, checks out their own
  branch `researchers/<name>`, downloads and extracts the PRO-ACT data into
  `data/PROACT_ALL_FORMS/`, and verifies everything.

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
  inside) and work there. **Derive the researcher's name as described in “Knowing which researcher you're working with” below** (ask only if the clone carries no identity yet).
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

## Visualizations

- **Default to Plotly** for charts — it's clean and interactive. Save the interactive
  chart as an HTML file in the experiment's `outputs/`.
- When a figure goes into a PDF report, also export a static image (PNG via `kaleido`).
- Label axes, units, and groups clearly; use colorblind-safe colors.

## Collaboration & branches (how work gets shared)

- Each researcher has **one durable branch: `researchers/<name>`**. All their pushes go
  there. **`main` and `develop` are protected — never push to them**, and never push to
  another person's branch. The maintainer merges work upward into `develop`.
- **We do not use pull requests.** The commit history on each person's branch is the record.
- Personal work is **private by default** (`projects/`, `data/` are git-ignored). It becomes
  shared only by **promotion**: use the **share-work** skill to copy the finished
  deliverable into `findings/<name>/<slug>/`, append a `HYPOTHESIS_LOG.md` entry, and push
  to their branch. Never promote raw data or very large files (> ~10 MB).
- To get others' work, use the **team-sync** skill ("pull the latest from the team repo").

### The promotion protocol (exactly what gets copied)

Promoted into `findings/<name>/<slug>/` — **these and nothing else**:

- `report.pdf` — the polished report
- the end-to-end script that produced it (e.g. `analysis.py`)
- key figures as `.png`
- `README.md` — the question, the finding **with effect size and n**, the caveats, and how
  to re-run it
- plus **one appended entry** in `HYPOTHESIS_LOG.md` (repo root)

**Never promoted** — it stays in `projects/` / `data/`:

- any raw or derived **patient data** — never, under any circumstances, even de-identified
- scratch scripts, dead ends, half-finished work
- virtual environments, `__pycache__`, caches
- files over ~10 MB (e.g. large interactive Plotly HTML) — keep them local and share the
  PDF plus a static PNG instead

If you are asked to promote something on the second list, **refuse and say why in plain
language**, then offer the allowed alternative (e.g. the PDF plus a static PNG).

### Hard rules for you (Claude)

- **Never push to `main` or `develop`.** They are protected and belong to the maintainer.
- **Never commit anything from `data/`** — no patient data leaves the machine, ever.
- **Push only to `researchers/<name>`**, the current researcher's own branch — never
  anyone else's.

### Knowing which researcher you're working with

You start every session knowing nothing — the **clone carries the identity**, so derive it
rather than asking. In priority order:

1. **Repo-local git config:** `git config user.name` — set during setup; the authority.
2. **The current branch:** `researchers/<slug>` names them (e.g. `researchers/manu`).
3. **Their folder:** a single `projects/<name>/` directory.

Only if none of these exist: **ask once**. And regardless of *how* you learned the name —
asked, or derived from the branch or folder — **make sure it is persisted**: if the
repo-local `git config user.name` is unset, set it, and if `user.email` is unset, ask once
for **the email address they use on GitHub** and set that too (commits are linked to their
GitHub account by email — a missing or wrong email breaks attribution and can make the
first commit fail outright). Check out their `researchers/<slug>` branch. After that, no
session ever needs to ask again. Never guess a name, and never derive identity from the
machine's global git config (that may be a work identity).

### Casual wording maps to the right action

Researchers won't use git vocabulary. "Save this", "send it up", "back this up", "publish
this" mean *promote, commit and push* — use **share-work**. "Get the latest", "what's new",
"catch me up" mean *pull* — use **team-sync**. Work out which one they mean rather than
asking for exact terminology, then say in one plain sentence what you're about to do and
confirm it with them before acting.

## Output locations

- **`projects/<name>/<experiment>/`** — where each researcher's work goes: an experiment
  folder under that person's name, with its own `scripts/` and `outputs/`. Create it when
  a new experiment starts. (`projects/` is git-ignored — personal work stays local and
  private until it is deliberately promoted into `findings/`.)
- **`findings/<name>/<slug>/`** — tracked. The finished, shared deliverable only (report
  PDF, the script, key figures, a short README). See `findings/README.md`.
- **`HYPOTHESIS_LOG.md`** (repo root) — tracked. The index of all shared findings.
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

**Then check for prior art — every time, before running anything:** search
`HYPOTHESIS_LOG.md` and `findings/` for entries touching the same question, variables, or
forms. If something exists, tell the researcher **who** tested **what**, **when**, with
which inputs, and what came of it — then ask whether to build on it, replicate it, or
proceed differently. Duplicating a colleague's test unknowingly wastes a week; building on
it is the whole point of the log.

**Then register the intent before running.** Append an entry with **Status: Under analysis**
(owner, date, hypothesis, planned data & inputs) and share it, so colleagues can see the
question is being worked on *right now* — the log is a claim board, not just an archive.
Update that same entry to Supported / Refuted / Inconclusive when the result lands, rather
than adding a second one.
