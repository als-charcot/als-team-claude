[STATUS|green|Follow-up to the <ORIGINAL-DATE> review — <ONE-SENTENCE TRIGGER>]
**Quick context for this short report.** The earlier review (`<ORIGINAL-REPORT-FILENAME>.pdf`) ran <WHAT-IT-COVERED> and <WHAT-IT-LEFT-OPEN>. Since then, <WHAT-CHANGED-OR-LANDED>, so we ran <WHAT-WE-NOW-RAN>. **This follow-up reports only what changed**: <ONE-SENTENCE-DELTA>. The original report's headline findings are <not refuted | refined | overturned in one specific way>.

[KEYSTAT|<NEW-NUMBER-1>|First new headline number — what it measures|tight context: p, n, comparator. Above/below the original report's threshold X.]

[KEYSTAT|<NEW-NUMBER-2>|Second new headline number — what it counts|tight context: how derived, what it survived.]

[KEYSTAT|0|Original-report claims invalidated|None. The <substituted | preliminary> result is <refined | extended>, not contradicted: <one specific aspect refined>; <another aspect>.]

<<PAGEBREAK>>

## What changed vs the <ORIGINAL-DATE> report

| Aspect | <ORIGINAL-DATE> report (<short label>) | This follow-up (<short label>) |
|--------|--------------------------------------|--------------------------------|
| n with full predictors | <old n> (<what it covered>) | <new n> (<what it covers now>) |
| <Headline metric> | <old number with CI / p> | **<new number with CI / p>** |
| <Second metric> | <old number> | <new number> |
| <Newly testable thing> | not testable | **<new number with CI / p>** |
| <Another newly testable thing> | not derivable | **<new number>** |
| <Open question from original — call it back by Q-number> | <how the original framed it> | <how this follow-up resolves / addresses it> |

<<PAGEBREAK>>

## Finding 1 (<new analysis name>) — One-sentence claim with the headline number

![Caption that becomes the figure caption](../figures/<new_figure_1>.png)

[STATUS|<green|amber|red>|One-line label — what test supports / refutes]
2-3 sentence body restating the finding with numbers and the asymmetry that establishes it.

[MEDICAL]: 2-4 lines on clinical/biological meaning.

[DATA-SCIENCE]: 2-4 lines on statistical framing.

[LAY]: 2-4 lines plain-English explanation.

[DATA]: 2-4 lines with a concrete number or row from the actual data.

<<PAGEBREAK>>

## Finding 2 (<if applicable, otherwise skip this section>) — Second new finding

![Caption for figure 2](../figures/<new_figure_2>.png)

[STATUS|<color>|Label]
Body…

[MEDICAL]: …

[DATA-SCIENCE]: …

[LAY]: …

[DATA]: …

<<PAGEBREAK>>

## What was gained

[BOX|green|Gain 1 — <short title of the strongest new result>]
Body framing the gain as a delta from the original report. Quote the original's number and the new number. End with one-sentence interpretation of why this matters.
[/BOX]

[BOX|green|Gain 2 — <short title of the second gain>]
Body, same shape.
[/BOX]

[BOX|green|Gain 3 — <short title of the third gain, if there is one>]
Body, same shape.
[/BOX]

## What was lost (small, almost nothing)

[BOX|amber|Loss 1 — <short title of the largest cost>]
Typically a sample-size loss or a CI-widening — the price of the more direct measurement. Frame as a trade, not a regression.
[/BOX]

[BOX|amber|Loss 2 — <second loss, often a marginal-significance loss>]
Body. Mention if the underlying biology is still captured by another predictor.
[/BOX]

[BOX|gray|Loss 3 (almost none) — <Original report's headline numbers>]
**Use this slot to explicitly state that the original report's claims stand.** The numbers reported there are correct for the model they describe; they are the same biology measured with a less direct probe. This BOX is the structural counterpart of the "0 invalidated" KEYSTAT on page 1.
[/BOX]

<<PAGEBREAK>>

## Open questions raised by the follow-up

[QUESTION|Q1|<First new open question, framed as a yes/no or pick-one for the colleague>]
Body. Specify what kind of answer would help. If the question echoes one from the original (e.g. "your Q2 about X") name it explicitly.

[QUESTION|Q2|<Second new open question>]
Body. The question is the title; the body provides specific framing.

[QUESTION|Q3|<Third new open question — typically "should we formalise the follow-up paper?">]
Body. Suggest a write-up direction and ask whether the colleague agrees.

[BOX|gray|Reproducibility — additions since the <ORIGINAL-DATE> report]
- `<project>/scripts/<NN_new_script>.py` — what it does
- `<project>/results/<new_subfolder>/<files>.tsv` — what they contain
- `<project>/figures/<new_figure>.png` — what it shows
Data source: `<path>` (whatever the new data is). End-to-end runtime ~X minutes; no new external dependencies. Reference the original report at `<project>/reports/<ORIGINAL>.pdf`.
[/BOX]
