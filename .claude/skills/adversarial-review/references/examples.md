# Worked examples

Four examples of a single reviewer, working alone with a fresh context, on one lens. They
show what a good verdict looks like, what an unusable one looks like, and why the
transcribe-before-verdict rule matters more than any other rule here.

All examples use illustrative claims, not anyone's shared work.

---

## Example 1 — A claim refuted, with the transcription that proves it

**Claim under review:** *"In PRO-ACT, riluzole users decline more slowly on ALSFRS-R
(p < 0.001), so riluzole slows ALS progression."*

**Reviewer:** survivorship and missingness. Fresh context. Given the claim, the script, and
the data. Not given: anyone's summary, or the other reviewers.

```
lens: survivorship and missingness

transcription:
  analysis.py:41   grp = g.groupby("subject_id").filter(lambda d: len(d) >= 3)
  analysis.py:52   slope, *_ = stats.linregress(g["months"], g["ALSFRS_R_Total"])
  summary.json     "n_with_slope": 5394,  "n_enrolled": 8617

defects:
  1. The outcome requires >= 3 visits to fit a slope (analysis.py:41), so a subject must
     survive and stay enrolled long enough to be measurable at all. 3,223 of 8,617 enrolled
     subjects never produce one. | The fastest progressors are absent from the very
     quantity meant to describe progression rate. | fatal
  2. Exposure is read once at baseline, so pre-exposure survival is credited to the exposed
     group. | Classic immortal time. | serious

verdict: claim does NOT hold as stated
one_line: Report the exclusion cascade and refit with exposure as time-varying.
```

**Why this verdict is usable.** Every defect points at a line or a number. The maintainer can
open `analysis.py:41`, see the filter, and decide. Nothing has to be taken on trust.

---

## Example 2 — The same claim, a different lens, reaching the same place independently

**Reviewer:** confounding and indication. Fresh context. Never saw Example 1.

```
lens: confounding and indication

transcription:
  data      F_PROACT_RILUZOLE: subjects on riluzole have median baseline ALSFRS-R 39.1
            vs 35.4 for those not on it
  analysis.py:88  model = ols("slope ~ riluzole", data=df)   # no covariates

defects:
  1. No adjustment at all (analysis.py:88), and the groups differ by 3.7 ALSFRS-R points at
     baseline. | Riluzole is prescribed to healthier, earlier-stage patients who reach
     specialist clinics, so the groups are not exchangeable. | fatal

verdict: claim does NOT hold as stated
one_line: The comparison is confounded by indication; an unadjusted contrast cannot support
a causal verb.
```

**This is what independence buys you.** Two reviewers, separate contexts, different lenses,
no knowledge of each other, arriving at "does not hold" by different routes. That agreement
carries information. Had the second reviewer been shown the first one's verdict, it would
carry none.

---

## Example 3 — A claim that held, because the reviewer tried to break it and failed

A verdict of "holds" is only worth something if the reviewer genuinely attacked it. Which is
why the prompt says *try to refute this*, not *is this correct*.

**Claim under review:** *"Bulbar-onset subjects decline faster than limb-onset
(mean difference 0.23 points/month), a small effect with heavily overlapping distributions."*

**Reviewer:** statistics and instruments. Fresh context.

```
lens: statistics and instruments

transcription:
  summary.json  "cohens_d": -0.25, "ci": [-0.33, -0.18], "n_bulbar": 930, "n_limb": 3227
  analysis.py:112  mixed = smf.mixedlm("score ~ group*months", df, groups=df["subject_id"])

attempts to refute, and what happened:
  - Tried: repeated measures treated as independent. Refuted by analysis.py:112, which
    clusters on subject_id. Interval is not borrowed.
  - Tried: a tiny p-value dressed up as a finding. Refuted; the claim leads with the effect
    size and its interval, and calls the effect small.
  - Tried: group imbalance (930 vs 3227) invalidating the contrast. Refuted; Welch and
    Mann-Whitney agree, and the CI is not driven by the smaller group.

defects:
  1. "Heavily overlapping" is asserted without a stated overlap statistic. | A reader cannot
     check it. | minor

verdict: holds with a stated caveat
one_line: Quote the overlap coefficient rather than describing the overlap in words.
```

**Note the shape.** The reviewer records what it tried and failed to break. A bare "looks
fine" is not a verdict, because it is indistinguishable from not having looked.

---

## Example 4 — A reviewer over-claiming, and how it was caught

Reviewers are not authorities. They are fresh, motivated, and sometimes wrong. This one
transcribed a line from the wrong file.

```
lens: statistics and instruments

transcription:
  scripts/demo_progression.py:74   score = score.fillna(other_scale_total)

defects:
  1. Missing scores on the 0-48 scale are filled from the 0-40 scale, putting artifactual
     8-point steps inside one subject's trajectory. | The slope measures scale-switching,
     not decline. | fatal

verdict: claim does NOT hold as stated
```

**What the maintainer did.** Opened the cited line. The defect was real, so it was fixed.
Then checked whether it affected *this* finding, and it did not: the finding under review
used its own script, which reads one scale only and drops rows missing it.

**Outcome:** one genuine defect fixed at source, in a different file. One verdict correctly
**not** applied to the claim it was aimed at.

**The lesson, and it is the important one.** The reviewer was required to quote the line it
was challenging. That single rule is what made the real defect findable *and* what made the
misdirected verdict checkable. Without the transcription there would have been an
authoritative-sounding "fatal" verdict and no way to tell which of the two it was.

**So: never act on a verdict without opening what it points at.** Confirm the defect, then
confirm it applies to the claim under review. Both steps, every time.

---

## Reading a set of verdicts

| Pattern | What it means | What to do |
|---|---|---|
| Several lenses, same defect, independently | strong signal | fix at source, re-derive |
| One lens, cited precisely | probably real, possibly narrow | open the citation and confirm scope |
| One lens, nothing cited | unusable | discard, or re-run that lens |
| All lenses "holds", each having tried | the claim is in good shape | ship it with the caveats they raised |
| All lenses "holds", none having tried | the review did not happen | re-run with a sharper prompt |

Count the verdicts. Deduplicate across lenses, keeping both mechanisms. Fix at source.
Record what was withdrawn, with the mechanism. Then append the surviving verdicts to the
`HYPOTHESIS_LOG.md` entry, so the next person sees what the finding was challenged on.
