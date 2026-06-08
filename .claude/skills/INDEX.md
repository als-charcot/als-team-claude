# Team Skills — Index

These skills load automatically when you open this repo with Claude Code. The ⭐ set
is the core you'll use most.

> **How to add a skill:** copy its folder (the one containing `SKILL.md`) into
> `.claude/skills/`. Do **not** double-wrap — the `SKILL.md` must sit directly inside
> the skill's own folder, e.g. `.claude/skills/statistical-analysis/SKILL.md`, not
> `.claude/skills/statistical-analysis/statistical-analysis/SKILL.md`. Then commit and
> push so the team gets it.

## Core — research workflow & output (ship in v1)

- ⭐ **polished-pdf-reports** — our standard deliverable format. Tight,
  presentation-quality PDFs where every claim sits in a visual block.
- ⭐ **statistical-analysis** — hypothesis tests, regression, power analysis,
  assumption checks, APA reporting.
- ⭐ **scientific-critical-thinking** — evidence quality, biases, confounders,
  GRADE / Cochrane risk-of-bias.
- ⭐ **exploratory-data-analysis** — the first thing to run on a new CSV; quality
  metrics + markdown report.
- ⭐ **scientific-writing** — manuscripts in flowing prose, IMRAD, reporting
  guidelines.
- ⭐ **scientific-visualization** — publication-ready figures, colorblind-safe
  palettes.
- **peer-review** — structured review passes on each other's reports (CONSORT/STROBE).
- **hypothesis-generation** — structured, testable hypothesis formulation.
- **citation-management** + **paper-lookup** — finding and citing papers correctly.

## Deliverable formats (built into Claude — not shipped here)

- **pdf**, **docx**, **xlsx**, **pptx** — Claude already includes these as built-in
  skills, so it can read/create those file types with nothing added to this repo.
  (They're Anthropic-proprietary and can't be redistributed, which is why they're not
  in `.claude/skills/`.) Your PDF *reports* come from **polished-pdf-reports** above,
  which is self-contained.

## Statistics & ML (add as needed)

- **scikit-survival** — time-to-event modeling (Cox, Random Survival Forests).
  Highly relevant for ALS.
- **statsmodels** — OLS, GLM, mixed models, diagnostics.
- **scikit-learn** + **shap** — predictive modeling + interpretability.
- **pymc** — Bayesian modeling.
- **polars** — fast dataframes.
- **matplotlib** + **seaborn** — plotting.

## Clinical / domain (add as needed)

- **pyhealth** — clinical prediction / EHR.
- **clinical-reports**, **clinical-decision-support**, **treatment-plans** — clinical
  document formats.
- **literature-review** — systematic reviews.
- **database-lookup** — query public biomedical databases.

## The rest of the collection

This repo also includes the **full K-Dense scientific-skills collection** (131 skills
total, MIT-licensed) — drug-discovery / chemistry / materials, genomics, imaging,
lab-platform integrations (Benchling, DNAnexus, etc.), and specialty domains (quantum,
geospatial, finance). The ⭐ set above is what an ALS/clinical team reaches for most;
the rest activate automatically if a task calls for them. Browse the folders in
`.claude/skills/` to see everything available.

The four Anthropic-proprietary skills (**pdf**, **docx**, **xlsx**, **pptx**) are
intentionally *not* here — they ship built into Claude. See `THIRD_PARTY_LICENSES.md`.
