# The validated source registry

Every source the team has reviewed, with its status and whether it is wired up yet. The
authority is the team's source-validation document; **FG** reviewed it and their decisions
are recorded here verbatim in meaning. Nothing gets monitored because it sounds useful:
it gets monitored because someone approved it.

**Status key**
`LIVE` wired up and running · `READY` free API exists, not yet written · `KEY` needs a paid
or registered API key · `SCRAPE` no API, would need HTML parsing or an agent ·
`QUERY` approved but a question is open

---

## Live now (3 sources, 3 evidence tiers)

| Source | Tier assigned | Status | Notes |
|---|---|---|---|
| **PubMed / MEDLINE** | peer-reviewed | `LIVE` | E-utilities. FG's first approval. Real keyword search, date-windowed. |
| **ClinicalTrials.gov** | trial registration | `LIVE` | API v2, sorted newest-update-first. A registration is a plan or a status change, never a result. |
| **bioRxiv + medRxiv** | preprint, NOT peer reviewed | `LIVE` | See the coverage caveat below. |

**The bioRxiv/medRxiv caveat, because it shapes what the tool can promise.** Their API is
**date-range only**. Passing a `search=` parameter returns exactly the same payload, which
was verified rather than assumed: a silently ignored filter is worse than no filter. So
keyword monitoring means paging the whole window and filtering locally. Roughly 55
preprints per server per day, 30 per page, about 0.7 s per page. A 14-day window is ~26
pages per server; pages are fetched concurrently so this stays a few seconds. Very long
windows are capped, and **the digest says so at the top** rather than quietly returning
less.

---

## Approved, free, not yet wired (the natural build-out order)

| Source | Tier | Status | Why it is next |
|---|---|---|---|
| **OpenAlex** | peer-reviewed + preprint | `QUERY` | Free, no key, excellent search, marks preprints. **Unreachable from the maintainer's machine** (connection failed on repeated attempts) — needs a network check before committing to it. |
| **Crossref** | peer-reviewed | `READY` | Free, no key. Best for DOI resolution and for linking news back to a paper. |
| **WHO ICTRP, EU CTIS, ISRCTN, ANZCTR, jRCT, UMIN, ChiCTR** | trial registration | `READY` | Approved. Non-US trials are genuinely missed by ClinicalTrials.gov alone. ICTRP first, since it aggregates several. |
| **FDA (openFDA)** | regulatory | `READY` | Free API. Approvals, designations, safety communications. |
| **EMA, MHRA, Health Canada, PMDA** | regulatory | `SCRAPE` | Approved, but no clean public API. Needs feeds or fetched pages. |
| **NIH RePORTER** | funding | `READY` | Free API. New grants are an early signal of where work is heading. |
| **CORDIS, UKRI, Wellcome** | funding | `READY`/`SCRAPE` | Approved. |
| **Semantic Scholar** | peer-reviewed | `READY` | Free tier without a key, rate-limited; a key raises limits. |

## Approved but structurally harder

| Source | Status | The obstacle |
|---|---|---|
| **Scopus, Web of Science, Dimensions** | `KEY` | Approved, but all three need paid or institutional API credentials. Worth asking whether the team's institutions already hold them. |
| **Google Scholar** | `SCRAPE` | Approved, but there is no API and automated querying is against its terms. Not implemented, and the reason is a policy one, not a technical one. |
| **Conference abstracts** (ALS/MND Symposium, ENCALS, AAN, SfN, MDA, EAN) | `SCRAPE` | Approved. Abstract books are usually PDFs published in bursts around each meeting, so this is a per-venue job rather than one adapter. |
| **Patents** (Google Patents, Espacenet, WIPO PATENTSCOPE) | `SCRAPE`/`KEY` | Approved. Espacenet OPS is the realistic route and needs registration. The document carries an unresolved note against PATENTSCOPE ("Goulven"). |
| **Company press releases and investor relations** | `SCRAPE` | Approved, and FG flagged **"a lot!"** of companies to monitor, offering **"access to our directory list"**. That list is the blocker: without it we would be guessing which companies matter. |
| **Business Wire, GlobeNewswire, PR Newswire** | `SCRAPE` | Approved. Company-provided tier. |
| **News** (STAT, Endpoints, Fierce Biotech, BioPharma Dive, BioSpace, Nature News, Science, ScienceDaily, Medical Xpress, Neurology Today, Medscape) | `SCRAPE` | Approved. Several are paywalled, which limits us to headline and abstract. Per the labelling rule, each item must link back to its primary source. |
| **Universities and hospitals** (14 approved, MGH through UMC Utrecht) | `SCRAPE` | Approved. Institutional news pages, best served by feeds. |
| **ALS/MND organisations** (9 approved, ALS Association through EverythingALS) | `SCRAPE` | Approved. |

## Flagged by FG as probably redundant

| Source | FG's note |
|---|---|
| **Europe PMC** | *"Not sure, should be included in Pubmed global."* |
| **PubMed Central (PMC)** | *"Not sure, should be included in Pubmed global."* |

**Deliberately not wired, and worth one conversation.** FG's reasoning is about *coverage
overlap* with PubMed, which is largely right for journal articles. But Europe PMC also has
a strong keyword-searchable preprint index, which is exactly the capability bioRxiv's own
API lacks. It would make the preprint tier cheaper and broader. That is a different
question from the one FG answered, so it should be put to them rather than assumed either
way.

## Requested additions, not yet in the registry

- **Horizon Europe** and the EU **Funding & Tenders Portal** — *"Maybe add"*.
- **ALS News Today** — asked for twice, once under news and again under sources
  researchers already use. Cheap to add, has a feed.
- **PULSE** — *"maybe add PULSE keyword"*. Recorded as a **keyword**, not a source, and it
  needs disambiguating before use.
- **The company directory list** — offered by FG. The single highest-value missing input:
  it converts "monitor pharma" from guesswork into a defined list.
- **Specific researchers, labs, companies and priority topics** — those questionnaire
  fields came back blank. Topic priorities in particular would sharpen ranking a lot.

---

## The labelling rules, taken from the validation document

These are requirements, not preferences. The document is explicit that the system must
identify the type and provenance of every result.

1. **Preprints** — included, labelled **not peer reviewed**.
2. **Conference abstracts and posters** — labelled as conference material, **not equivalent
   to a full peer-reviewed publication**.
3. **Company press releases** — labelled as **company-provided** information.
4. **Patents** — labelled as patent information, **not evidence of clinical effectiveness**.
5. **Secondary news** — connected back to the original publication, trial, regulatory
   announcement, institution, company or abstract wherever possible.

And one rule of our own, which follows from the adversarial-review discipline:

6. **An item with no resolvable primary-source URL is marked as uncitable** rather than
   presented as a normal result. A digest entry nobody can open is not evidence.
