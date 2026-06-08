# SETUP — workspace setup runbook (for Claude, not the researcher)

This file is instructions for **Claude Code**. When a researcher opens this repo with the
**Code tab** and asks you to "set up my workspace" (or "read SETUP.md and set me up"),
follow these steps.

**The researcher is not technical.** They should not have to install anything, run
commands, or download anything by hand. **You do all the technical work** — installing
tools, downloading and extracting the data, verifying — and only pause for a quick yes/no
when you need consent to install software.

**Tell the user what you're doing as you go.** Before each step, say plainly what you're
about to do ("I'll create your folders, then download the data...") and confirm when it's
done. Don't silently create or change things — they should be able to follow along.

**First, detect the operating system (Windows or macOS) and use the matching commands
below.** Paths here use forward slashes (`data/PROACT_ALL_FORMS/`) — they refer to the
same folders on either OS.

## 0. Orient
- Confirm `CLAUDE.md` and `.claude/skills/` are present. This folder **is** their ALS
  workspace. Work relative to it.

## 1. Tools & updates (you install what's missing — never ask them to)
- If a `.git` folder exists here, this is a git **clone** and stays updatable. If `git`
  isn't installed, install it yourself (with consent), then run `git pull`:
  - **Windows:** `winget install --id Git.Git -e`
  - **macOS:** `xcode-select --install` (git ships with the Command Line Tools), or
    `brew install git` if Homebrew is present. git is often already installed on macOS.
- If this is **not** a clone (downloaded ZIP), updates come by re-downloading the ZIP; a
  clone is better for automatic updates — offer to set one up.

## 2. Create the standard folders (idempotent — never overwrite)
- Ensure `data/` and `projects/` exist at the repo root; create them only if missing.

## 3. Download the PRO-ACT data into `data/PROACT_ALL_FORMS/`  (you do this automatically)
- **If `data/PROACT_ALL_FORMS/` already contains `F_PROACT_*.csv` files, skip this step.**
- Otherwise **download it yourself — do NOT ask the researcher to download or to go find a
  file.** Tell them you're downloading the dataset (~25 MB), then:
  1. Make sure Python is available; install it if missing, with consent (Windows:
     `winget install --id Python.Python.3.12 -e`; macOS: `brew install python` or python.org).
  2. Install gdown: `pip install gdown`.
  3. Download the dataset zip (Google Drive file id `1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm`):
     `gdown "https://drive.google.com/uc?id=1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm" -O data/proact.zip`
  4. Extract it (Windows: `Expand-Archive -Path data/proact.zip -DestinationPath data/_extract -Force`;
     macOS: `unzip data/proact.zip -d data/_extract`). The archive has a **dated wrapper
     folder** (e.g. `2026_02_27_PROACT_ALL_FORMS/`) holding the CSVs — move its **contents**
     into `data/PROACT_ALL_FORMS/` (flatten the wrapper). Delete the zip and the temp folder.
  - **Only if the automatic download genuinely fails** (no network, Drive change): then, as a
    fallback, give the researcher the link and ask them to download + unzip it into
    `data/PROACT_ALL_FORMS/`: `https://drive.google.com/file/d/1vhxfZ0EalFs1proJCqi8yepiUVn_2BRm/view`
- **Verify:** list `data/PROACT_ALL_FORMS/` and confirm ~18 `F_PROACT_*.csv` files, then tell
  the user the data is ready.

## 4. Sanity check
- Read `data/PROACT_ALL_FORMS/F_PROACT_ALSFRS.csv` and report its row count and a few
  column names so the researcher sees the data is readable. Read from `data/` — **never
  copy the data into a project folder.**

## 5. Analyses & environments (your job, not theirs)
- When an analysis needs Python or libraries, install and manage them **yourself**: create
  a virtual environment inside that project's folder, install only what's needed, and record
  a `requirements.txt`. Install Python itself if missing (Windows: `winget install` the
  Python package; macOS: `brew install python` or the python.org installer). The researcher
  never installs Python or packages.

## 6. Confirm and hand off
- Confirm the `CLAUDE.md` rules and skills are active.
- Summarize in one short message: data is in `data/PROACT_ALL_FORMS/`, and each experiment
  goes in `projects/<their-name>/<experiment>/` (you create it; ask their name once if you
  don't know it). Suggest a starter prompt:
  > "Start a new experiment called `fvc-slope`; the data is in `data/PROACT_ALL_FORMS`. Show
  > how ALSFRS-R declines over time for bulbar vs limb onset, and whether baseline FVC
  > predicts a faster decline. Save the figures and write it up as a polished PDF."
