# Try it yourself — agents & a sprint (Week 8)

Two things to try in **your own** ALS workspace (the Code tab). No setup — the `sprint` and
`pubmed-feed` skills are already in this repo, so **pull the latest** and they're just there.

---

## A. See the agents work — put a claim on trial  (~2 minutes)

Paste this into Claude Code:

> "Have three independent agents each try to disprove this claim from a different angle —
> confounding, survivorship bias, and statistics — then tell me only what survives:
> *'riluzole users decline slower on ALSFRS-R, so riluzole slows ALS.'*"

**What you'll see:** three separate agent panels open in the chat, work *in parallel*, and each
report a verdict — then Claude reconciles them. That is delegation + fan-out, made visible.

Now do it again on **one of your own beliefs** about the data. Did it survive?

---

## B. Run a real sprint  (~15–30 minutes)

Pick **one sharp question** and say:

> "Start a sprint on: *<your question>*. Use the PRO-ACT data in `data/PROACT_ALL_FORMS`."

Claude will walk the recipe: **frame** it → **plan** (you approve before anything runs) →
**execute** (fanning out agents where parallel helps) → **stress-test** the finding with
independent adversarial agents → **write up** a polished PDF + a hypothesis-log entry, all in
`projects/<your-name>/<slug>/`.

**Bring next week:** the PDF + your one-line hypothesis-log entry.

---

## Good to know

- **Your work stays local.** `projects/` and `data/` are git-ignored — you don't push your
  experiment. Share a result deliberately by pasting the commit link into the hypothesis log.
- **What everyone shares is the *skills*, not the experiments** — those come from this repo.
- **Guardrail:** agents can be *confidently wrong*. Keep effect sizes (not just p-values), and
  make every claim trace back to a real number or `subject_id`. Use agents to *attack* your
  ideas, not just confirm them.
