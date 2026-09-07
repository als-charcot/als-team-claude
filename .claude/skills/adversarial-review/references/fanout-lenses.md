# The fan-out: lenses, rules, and a prompt skeleton

## The five rules

### 1. The reviewer holds the data and the script, not your summary
A reviewer given your conclusion reviews your prose. Give them the paths: the analysis
script, the summary output it wrote, and the data location. Let them look.

### 2. Frame the job as finding, not judging
"Try to refute this" produces work. "Is this correct?" produces agreement. Tell each reviewer
to assume the finding is wrong in the way their lens is designed to catch, and to default to
"defect present" when uncertain.

### 3. Force transcription before verdict
Require the reviewer to quote the exact line of code, or the exact number, they are
challenging, before giving a verdict. This kills objections to things that are not there,
which is the main failure mode of an enthusiastic reviewer.

### 4. Structured, enumerated verdicts
Ask for a fixed shape so verdicts can be counted, recorded and compared:

```
lens:          confounding
defects:       [ {what, where (file:line or number), why it matters, severity: fatal|serious|minor} ]
verdict:       claim does NOT hold as stated | holds with the stated caveat | holds
one_line:      the single most important thing the researcher should change
```

### 5. Read-only, and capped
Reviewers never edit the analysis. They report. Give each one a bounded task, so the review
does not become a second analysis.

---

## The lenses

Each lens gets its own reviewer with fresh context. Independence is the whole point: a
reviewer who has seen another's verdict is no longer a second opinion.

### Confounding and indication
Who ended up in each group, and why? Would a clinician have assigned exposure on grounds that
also predict the outcome? Are the groups exchangeable at baseline? Is any covariate a collider
or a mediator? Refer to catalogue sections D2, D3, E3.

### Survivorship and missingness
Who had to survive, or be measured, to appear in the analysed set at all? Does the outcome
definition itself require follow-up that the sickest subjects never accrue? Is missingness
related to severity? Catalogue A3, D1, D4.

### Statistics and instruments
Does the number answer the stated question? Effect size with an interval, or a bare p-value?
Repeated measures treated as independent? In-sample fit sold as prediction? Multiple testing
declared? Could any check in this script have failed? Catalogue B, C, E.

### Reproducibility
Re-run the script. Does it produce this exact number? Is every number in the report emitted
by the script rather than typed? Is the cohort funnel reconcilable step by step? Catalogue A1,
A2, F.

### Optional fifth: clinical plausibility
Does the magnitude make sense against what is known about ALS progression? Is a causal verb
being used on observational data? Is the finding consistent with trial evidence, and if it
contradicts it, is that acknowledged?

---

## What every prompt must carry

- The **exact claim** under review, quoted verbatim.
- Paths to the **script**, its **summary output**, and the **data**.
- The **lens**, and a pointer to the relevant catalogue sections.
- The instruction to **transcribe before verdict**.
- The **output shape** from rule 4.
- "You are one of several independent reviewers. Do not try to be balanced. Your job is to
  find what your lens catches."
- A note that this is de-identified PRO-ACT data, so there is no patient-privacy constraint on
  discussing subject-level values.

---

## Skeleton

> You are one of several independent reviewers auditing a finding from a PRO-ACT cohort
> analysis. Each reviewer has a different lens. Yours is **<LENS>**.
>
> The claim under review, verbatim:
> "<CLAIM>"
>
> The evidence: script `<PATH>`, its summary output `<PATH>`, data in `data/PROACT_ALL_FORMS/`.
> Read them. Do not rely on any summary of the analysis.
>
> Assume the claim is wrong in a way your lens is designed to catch. Work through the
> relevant entries in `references/failure-modes.md` (<SECTIONS>).
>
> For every defect you find, first **quote the exact line of code or the exact number** you
> are challenging, then explain why it matters. Do not report a defect you cannot point at.
>
> Return exactly this shape:
>   lens, defects (what / where / why it matters / severity), verdict, one_line.
>
> You are read-only. Do not modify anything. Default to reporting a defect when uncertain.
> This is de-identified data with no PHI.

---

## After the fan-out

1. **Count the verdicts.** A claim that a majority of lenses reject does not ship.
2. **Deduplicate.** Two lenses often find one defect from different angles. Merge them, keep
   both mechanisms.
3. **Fix at source and re-derive.** Never patch the sentence.
4. **Record withdrawals** with their mechanism in the finding's `README.md`.
5. **Append the surviving verdicts** to the `HYPOTHESIS_LOG.md` entry, so the team can see
   what the finding was challenged on and what held.
