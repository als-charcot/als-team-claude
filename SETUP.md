# SETUP — workspace setup runbook (for Claude, not the researcher)

This file is instructions for **Claude Code**. When a researcher opens this repo with the
**Code tab** and asks you to "set up my workspace" (or "read SETUP.md and set me up"),
follow the steps below. The researcher is **not a coder** — be friendly and brief, do the
work yourself, report what you did, and only stop to ask when something genuinely needs
their decision (e.g., consent to install software).

## 0. Orient
- Confirm this folder is the team repo: `CLAUDE.md` and `.claude/skills/` are present.
- This folder **is** the researcher's ALS workspace. Do everything relative to it.

## 1. Create the standard folders (idempotent — never overwrite existing content)
- Ensure `data/` and `projects/` exist at the repo root. Create them only if missing.

## 2. Get the PRO-ACT data into `data/PROACT_ALL_FORMS/`
- **If `data/PROACT_ALL_FORMS/` already contains `F_PROACT_*.csv` files, skip this step.**
- Otherwise download and extract it:
  1. Make sure Python is available; install **gdown** if needed: `pip install gdown`.
  2. Download the dataset zip (Google Drive file id `1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm`):
     `gdown "https://drive.google.com/uc?id=1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm" -O data/proact.zip`
  3. Unzip it. The archive contains a **dated wrapper folder** (e.g.
     `2026_02_27_PROACT_ALL_FORMS/`) holding the CSVs. Move that folder's **contents** so
     the `F_PROACT_*.csv` files sit directly inside `data/PROACT_ALL_FORMS/` (flatten the
     wrapper). Delete `data/proact.zip` afterward.
  - **If the download fails** (no network, Drive change): don't get stuck. Give the
    researcher the link below and ask them to download + unzip into
    `data/PROACT_ALL_FORMS/`, then continue.
    `https://drive.google.com/file/d/1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm/view`
- **Verify:** list `data/PROACT_ALL_FORMS/` and confirm ~18 `F_PROACT_*.csv` files.

## 3. Quick sanity check
- Load `data/PROACT_ALL_FORMS/F_PROACT_ALSFRS.csv` and report its row count and a few
  column names, so the researcher can see the data is readable. Read from `data/` —
  **never copy the data into a project folder.**

## 4. Environment (do NOT pre-install everything now)
- When an actual analysis needs libraries, create a virtual environment **inside that
  project's folder**, install only what's needed, and record a `requirements.txt`.
- If Python or git is missing and a task needs it, offer to install it (with consent).

## 5. Updates
- If this folder is a git clone, offer to run `git pull` to get the latest rules/skills.
- If it was downloaded as a ZIP, tell them updates come by re-downloading the ZIP from the
  repo (Code button → Download ZIP).

## 6. Confirm and hand off
- Confirm the `CLAUDE.md` rules and the skills are active.
- Tell the researcher, in one short summary: data lives in `data/PROACT_ALL_FORMS/`, their
  analyses go in `projects/<name>/`, and suggest a starter prompt:
  > "Work in `projects/fvc-slope`; the data is in `data/PROACT_ALL_FORMS`. Show how
  > ALSFRS-R declines over time for bulbar vs limb onset, and whether baseline FVC predicts
  > a faster decline. Save the figures and write it up as a polished PDF."
