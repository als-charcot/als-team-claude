---
name: share-work
description: >-
  Share a researcher's finished work with the team by promoting it into findings/, adding a
  hypothesis-log entry, committing it with their name, and pushing to their own branch. Use
  when the user says "share this work with the team", "share this finding", "push my work",
  or "publish this to the team repo" — and equally for casual phrasings that mean the same
  thing: "save this", "send it up", "send this to the team", "back this up", "put this in
  the repo", "commit this", "upload my work". Also use when they want completed analysis to
  become visible to colleagues. Never pushes to main or develop.
---

# Share work with the team

The researcher's own work lives in `projects/<name>/` and `data/`, which are **git-ignored
and stay on their machine**. Sharing means *promoting* a finished deliverable into the
tracked `findings/` folder and pushing it to **their own branch**. Nothing else is shared.

## Hard rules

- **Never push to `main` or `develop`.** Those are protected and belong to the maintainer.
- **Never commit anything from `data/`** — no patient data, ever, even de-identified.
- **Push only to the researcher's own branch:** `researchers/<name>`.
- Don't share half-finished work. If the analysis isn't complete, say so and offer to
  finish it first.

## Steps

1. **Identify the researcher** from the clone, in this order: repo-local
   `git config user.name` → the current `researchers/<slug>` branch → their
   `projects/<name>/` folder. Only ask if none exist — and then persist the answer
   (repo-local `git config user.name`). Slug = lowercase first name ("David Devos" → `david`).

2. **Confirm what's being shared.** Identify the deliverable in their project folder —
   normally the report PDF, the end-to-end script, and any key figures. Show the list and
   confirm before copying. Exclude: raw data, virtual environments, caches, and very large
   files (> ~10 MB, e.g. big interactive HTML — keep those local and mention it).

3. **Promote it** into `findings/<name>/<slug>/` (create the folders). Copy:
   - the report PDF
   - the script that produced it
   - key figures (PNG)
   - a short `README.md`: the question, the finding with **effect size and n**, the caveats,
     and how to re-run it.

4. **Add a hypothesis-log entry.** Append a block to `HYPOTHESIS_LOG.md` at the repo root
   using the format in `templates/HYPOTHESIS_LOG_TEMPLATE.md` (status, owner, hypothesis,
   finding with effect size + n, evidence path, open questions). Keep it short.

5. **Commit and push to their branch:**
   - Make sure their branch exists and is checked out: `researchers/<name>`
     (create it from the current `main` if it doesn't exist yet).
   - Stage **only** `findings/<name>/<slug>/` and `HYPOTHESIS_LOG.md`.
   - Commit with a clear message: what was found, in one line, plus a short body.
   - Push: `git push -u origin researchers/<name>`.
   - If the push is rejected because they lack access or aren't signed in, explain plainly
     and tell them to ask the maintainer (Emmanuel) — don't try to work around it.

6. **Report back** in plain language: what was shared, which branch it went to, and that
   the maintainer will merge it into `develop` when the team should build on it. Give them
   the commit's short hash so they can reference it.

## Notes

- The commit history *is* the record — that's why the commit message matters. Write it so a
  colleague reading the log in a year understands what was found.
- If the same finding is being updated, add a new commit rather than rewriting history.
- Pull requests are not part of our flow. Researchers push to their own branch; the
  maintainer merges upward.
