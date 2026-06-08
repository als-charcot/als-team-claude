# SETUP — workspace setup runbook (for Claude, not the researcher)

This file is instructions for **Claude Code**. When a researcher opens this repo with the
**Code tab** and asks you to "set up my workspace" (or "read SETUP.md and set me up"),
follow these steps.

**The researcher is not technical.** They should not have to install anything or run
commands. **You do all the technical work** — installing tools, extracting archives,
verifying — and only pause for a quick yes/no when you need their consent to install
software. The *one* thing they do by hand is download the dataset (a single click in
their browser); you place it for them.

## 0. Orient
- Confirm `CLAUDE.md` and `.claude/skills/` are present. This folder **is** their ALS
  workspace. Work relative to it.

## 1. Tools & updates (you install what's missing — never ask them to)
- If a `.git` folder exists here, this is a git **clone** and stays updatable. If `git`
  isn't installed, offer to install it yourself (Windows: `winget install --id Git.Git -e`),
  then run `git pull` to fetch the latest rules and skills.
- If this is **not** a clone (it was downloaded as a ZIP), updates come by re-downloading
  the ZIP. A clone is better for automatic updates — mention that, and offer to set it up.

## 2. Create the standard folders (idempotent — never overwrite)
- Ensure `data/` and `projects/` exist at the repo root; create them only if missing.

## 3. Get the PRO-ACT data into `data/PROACT_ALL_FORMS/`  (they download; YOU place it)
- **If `data/PROACT_ALL_FORMS/` already contains `F_PROACT_*.csv` files, skip this step.**
- Otherwise:
  1. Ask the researcher to download the dataset zip — one click:
     `https://drive.google.com/file/d/1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm/view`
  2. Find the downloaded zip yourself (check this ALS folder and the user's `Downloads`
     folder; if you can't find it, ask them for the path).
  3. **Extract it yourself — no Python needed.** On Windows use PowerShell:
     `Expand-Archive -Path "<path-to>.zip" -DestinationPath "data\_extract" -Force`
  4. The archive contains a **dated wrapper folder** (e.g. `2026_02_27_PROACT_ALL_FORMS/`)
     holding the CSVs. Move that folder's **contents** into `data/PROACT_ALL_FORMS/` so the
     `F_PROACT_*.csv` files sit directly inside it (flatten the wrapper). Remove the temp
     folder and the zip.
  - *Optional shortcut (only if Python is already available, or you install it yourself with
    consent — never make the researcher do it):* `pip install gdown` then
    `gdown "https://drive.google.com/uc?id=1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm" -O data/proact.zip`.
- **Verify:** list `data/PROACT_ALL_FORMS/` and confirm ~18 `F_PROACT_*.csv` files.

## 4. Sanity check
- Read `data/PROACT_ALL_FORMS/F_PROACT_ALSFRS.csv` and report its row count and a few
  column names so the researcher sees the data is readable. Read from `data/` — **never
  copy the data into a project folder.**

## 5. Analyses & environments (your job, not theirs)
- When an analysis needs Python or libraries, install and manage them **yourself**: create
  a virtual environment inside that project's folder, install only what's needed, and record
  a `requirements.txt`. The researcher never installs Python or packages.

## 6. Confirm and hand off
- Confirm the `CLAUDE.md` rules and skills are active.
- Summarize in one short message: data is in `data/PROACT_ALL_FORMS/`, analyses go in
  `projects/<name>/`, and suggest a starter prompt:
  > "Work in `projects/fvc-slope`; the data is in `data/PROACT_ALL_FORMS`. Show how ALSFRS-R
  > declines over time for bulbar vs limb onset, and whether baseline FVC predicts a faster
  > decline. Save the figures and write it up as a polished PDF."
