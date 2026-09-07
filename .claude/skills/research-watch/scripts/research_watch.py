#!/usr/bin/env python3
"""Harvest recent ALS research developments from validated sources, label every item by
evidence tier, and write a digest a researcher can interrogate.

    python research_watch.py "ALS neurofilament" --days 30
    python research_watch.py "C9orf72" "TDP-43" --days 14 --sources pubmed,preprints
    python research_watch.py "ALS" --days 7 --out research-watch/weekly.md

WHY THIS EXISTS. A press release, a preprint and a randomised trial are not the same kind
of claim, but they arrive looking alike. This tool never presents an item without saying
what KIND of evidence it is, and never presents an item it could not fetch a real URL for.

SOURCES IMPLEMENTED (all validated by the team, all free, none needs an API key):
  pubmed      PubMed / MEDLINE            -> tier: peer-reviewed
  trials      ClinicalTrials.gov (API v2) -> tier: trial registration
  preprints   bioRxiv + medRxiv           -> tier: preprint, NOT peer reviewed

Each adapter reports its own item count, and a source that returns zero says so out loud.
A source that errors is reported as an error, never silently dropped: a harvester that
quietly loses a feed reports success forever.

Stdlib only. No API keys. Deliberately polite to every endpoint.
"""
from __future__ import annotations
import argparse, json, os, re, sys, time, urllib.parse, urllib.request, urllib.error
import xml.etree.ElementTree as ET
import concurrent.futures as cf
from datetime import date, datetime, timedelta

try:                                    # Greek letters and dashes in titles vs cp1252
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

CONTACT = os.environ.get("ALS_WATCH_CONTACT", "als-team@example.org")
UA = f"ALS-Team-Research-Watch/1.0 (mailto:{CONTACT})"

# Coverage caveats raised during a run; surfaced in the digest, never swallowed.
PARTIAL: list[str] = []

# Evidence tiers, and the label the reader must see. Ordered most to least probative.
TIERS = {
    "peer-reviewed":      ("Peer-reviewed publication", 0),
    "trial":              ("Trial registration (a plan or status change, not a result)", 1),
    "preprint":           ("PREPRINT - NOT PEER REVIEWED", 2),
    "conference":         ("Conference abstract - not equivalent to a full publication", 3),
    "press-release":      ("COMPANY-PROVIDED information", 4),
    "patent":             ("Patent - not evidence of clinical effectiveness", 5),
    "news":               ("Secondary news coverage", 6),
}


def get(url: str, timeout: int = 30, tries: int = 3) -> bytes:
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except Exception as e:                       # noqa: BLE001 - report, don't crash
            last = e
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"{type(last).__name__}: {last}")


def norm_title(t: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", (t or "").lower()).strip()


# ─────────────────────────────── adapters ────────────────────────────────────

def fetch_pubmed(query: str, days: int, cap: int) -> list[dict]:
    """PubMed / MEDLINE via E-utilities. Tier: peer-reviewed."""
    q = urllib.parse.quote(query)
    es = (f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=pubmed&term={q}"
          f"&retmax={cap}&retmode=json&datetype=pdat&reldate={days}&sort=date")
    ids = json.loads(get(es))["esearchresult"].get("idlist", [])
    if not ids:
        return []
    time.sleep(0.4)                                  # NCBI: <=3 req/s unkeyed
    ef = ("https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=pubmed"
          f"&id={','.join(ids)}&retmode=xml")
    root = ET.fromstring(get(ef))
    out = []
    for art in root.findall(".//PubmedArticle"):
        pmid = (art.findtext(".//PMID") or "").strip()
        title = " ".join((art.findtext(".//ArticleTitle") or "").split())
        abst = " ".join(" ".join(
            (e.text or "") for e in art.findall(".//Abstract/AbstractText")).split())
        journal = art.findtext(".//Journal/Title") or ""
        doi = ""
        for aid in art.findall(".//ArticleId"):
            if aid.get("IdType") == "doi":
                doi = (aid.text or "").strip()
        y = art.findtext(".//PubDate/Year") or art.findtext(".//PubMedPubDate/Year") or ""
        m = art.findtext(".//PubDate/Month") or ""
        auths = [f"{a.findtext('LastName') or ''} {a.findtext('Initials') or ''}".strip()
                 for a in art.findall(".//Author")[:4]]
        out.append(dict(
            tier="peer-reviewed", source="PubMed / MEDLINE", id=f"pmid:{pmid}", doi=doi,
            title=title, date=f"{y} {m}".strip(), authors=[a for a in auths if a],
            summary=abst, url=f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/", venue=journal))
    return out


def fetch_trials(query: str, days: int, cap: int) -> list[dict]:
    """ClinicalTrials.gov API v2, newest updates first. Tier: trial registration."""
    cutoff = date.today() - timedelta(days=days)
    url = ("https://clinicaltrials.gov/api/v2/studies"
           f"?query.cond={urllib.parse.quote('amyotrophic lateral sclerosis')}"
           f"&query.term={urllib.parse.quote(query)}"
           f"&pageSize={min(cap * 3, 100)}&sort=LastUpdatePostDate%3Adesc")
    studies = json.loads(get(url)).get("studies", [])
    out = []
    for s in studies:
        p = s.get("protocolSection", {})
        idm, stm = p.get("identificationModule", {}), p.get("statusModule", {})
        upd = (stm.get("lastUpdatePostDateStruct") or {}).get("date", "")
        try:                                          # newest-first: stop at the cutoff
            if datetime.strptime(upd, "%Y-%m-%d").date() < cutoff:
                break
        except ValueError:
            pass
        nct = idm.get("nctId", "")
        desc = (p.get("descriptionModule", {}) or {}).get("briefSummary", "") or ""
        des = p.get("designModule", {}) or {}
        phases = ", ".join(des.get("phases", []) or []) or "n/a"
        enroll = ((des.get("enrollmentInfo") or {}).get("count"))
        spon = ((p.get("sponsorCollaboratorsModule", {}) or {}).get("leadSponsor", {}) or {})
        out.append(dict(
            tier="trial", source="ClinicalTrials.gov", id=f"nct:{nct}", doi="",
            title=idm.get("briefTitle", ""), date=upd, authors=[],
            summary=" ".join(desc.split()),
            url=f"https://clinicaltrials.gov/study/{nct}",
            venue=(f"{stm.get('overallStatus','?')} | phase {phases}"
                   + (f" | n={enroll}" if enroll else "")
                   + (f" | {spon.get('name')}" if spon.get("name") else ""))))
    return out[:cap]


def _preprint_page(srv: str, start: str, end: str, cursor: int) -> list[dict]:
    d = json.loads(get(f"https://api.biorxiv.org/details/{srv}/{start}/{end}/{cursor}"))
    return d.get("collection", []) or [], int((d.get("messages") or [{}])[0].get("total") or 0)


def fetch_preprints(query: str, days: int, cap: int,
                    servers=("medrxiv", "biorxiv"), budget_s: float = 90.0) -> list[dict]:
    """bioRxiv + medRxiv.

    Their API is DATE-RANGE ONLY. Verified: passing `search=` returns an identical payload,
    and a silently-ignored filter is worse than no filter, so we never pretend it worked.
    We page the window and filter on the keywords locally.

    The endpoint is slow and highly variable (measured: 1-9 s per 30-record page), so this
    runs under a WALL-CLOCK BUDGET. Whatever is scanned when the budget expires is what you
    get, and the shortfall is reported in the digest. A tool that hangs is worse than one
    that returns less and says so: an unbounded scan of a 14-day window took five minutes.
    """
    terms = [t for t in re.split(r"\s+", query.lower()) if len(t) > 2]
    start = (date.today() - timedelta(days=days)).isoformat()
    end = date.today().isoformat()
    # Budget is split PER SERVER. With one shared deadline the first server consumed it
    # all and the second was left with a single page, which looked like coverage and was not.
    per_server = max(8.0, budget_s / max(1, len(servers)))
    out, seen = [], set()

    for srv in servers:
        deadline = time.time() + per_server
        batches, scanned, total = [], 0, 0
        try:
            first, total = _preprint_page(srv, start, end, 0)
        except Exception as e:                                  # noqa: BLE001
            PARTIAL.append(f"{srv} unavailable ({type(e).__name__}); preprints from it are missing")
            continue
        batches.append(first); scanned = len(first)
        cursors = list(range(len(first), total, 30))
        if cursors and time.time() < deadline:
            ex = cf.ThreadPoolExecutor(max_workers=4)
            futs = {ex.submit(_preprint_page, srv, start, end, c): c for c in cursors}
            try:
                for fu in cf.as_completed(futs, timeout=max(1.0, deadline - time.time())):
                    try:
                        b, _ = fu.result()
                        batches.append(b); scanned += len(b)
                    except Exception:                           # noqa: BLE001
                        pass                                    # one lost page, not the run
            except cf.TimeoutError:
                pass
            # wait=False + cancel_futures is what actually makes the budget a budget: the
            # context manager's blocking shutdown waited for every in-flight request and
            # turned a 25s budget into minutes.
            ex.shutdown(wait=False, cancel_futures=True)
        if total and scanned < total:
            PARTIAL.append(f"{srv}: scanned {scanned} of {total} preprints in the window "
                           f"(time budget {per_server:.0f}s for this server)")
        for batch in batches:
            for it in batch:
                blob = f"{it.get('title','')} {it.get('abstract','')}".lower()
                if terms and not all(t in blob for t in terms):
                    continue
                doi = (it.get("doi") or "").strip()
                if doi in seen:
                    continue
                seen.add(doi)
                out.append(dict(
                    tier="preprint", source=f"{srv} (preprint server)",
                    id=f"doi:{doi}", doi=doi,
                    title=" ".join((it.get("title") or "").split()),
                    date=it.get("date", ""),
                    authors=[a.strip() for a in (it.get("authors") or "").split(";")[:4] if a.strip()],
                    summary=" ".join((it.get("abstract") or "").split()),
                    url=f"https://doi.org/{doi}" if doi else "",
                    venue=f"{srv}, version {it.get('version','?')}, "
                          f"category {it.get('category','n/a')}"))
    out.sort(key=lambda i: i.get("date", ""), reverse=True)
    return out[:cap]


ADAPTERS = {"pubmed": fetch_pubmed, "trials": fetch_trials, "preprints": fetch_preprints}


# ─────────────────────────── dedupe / rank / render ──────────────────────────

def dedupe(items: list[dict]) -> tuple[list[dict], int]:
    """One real-world thing can appear in several sources. Collapse on DOI, then on a
    normalised title, keeping the most probative tier and remembering the alternates."""
    by_key: dict[str, dict] = {}
    dropped = 0
    for it in sorted(items, key=lambda i: TIERS[i["tier"]][1]):
        key = ("doi:" + it["doi"].lower()) if it.get("doi") else None
        tkey = "t:" + norm_title(it["title"])
        hit = (by_key.get(key) if key else None) or by_key.get(tkey)
        if hit:
            hit.setdefault("also_in", []).append(it["source"])
            dropped += 1
            continue
        if key:
            by_key[key] = it
        by_key[tkey] = it
    uniq, seen_id = [], set()
    for v in by_key.values():
        if id(v) not in seen_id:
            seen_id.add(id(v))
            uniq.append(v)
    return uniq, dropped


def rank(items: list[dict], terms: list[str]) -> list[dict]:
    def score(it):
        blob = f"{it['title']} {it.get('summary','')}".lower()
        hits = sum(blob.count(t) for t in terms)
        title_hits = sum(3 for t in terms if t in it["title"].lower())
        return -(hits + title_hits - TIERS[it["tier"]][1]), it.get("date", "")
    return sorted(items, key=score)


def render(items, query, days, stats, dropped) -> str:
    L = [f"# Research watch: {query}", "",
         f"Window: last {days} days, run {date.today().isoformat()}.  "
         f"{len(items)} distinct items after de-duplication "
         f"({dropped} duplicate{'s' if dropped != 1 else ''} merged across sources).", "",
         "**Every item below carries its evidence tier.** A preprint, a trial registration "
         "and a peer-reviewed paper are different kinds of claim. Nothing here is a finding "
         "until someone reads the primary source at the link given.", "",
         "## Sources queried", ""]
    for name, st in stats.items():
        if st["error"]:
            L.append(f"- **{name}** — FAILED: {st['error']}")
        else:
            L.append(f"- **{name}** — {st['n']} item{'s' if st['n'] != 1 else ''}"
                     + ("  (returned nothing for this query and window)" if st["n"] == 0 else ""))
    L.append("")
    if any(s["error"] for s in stats.values()):
        L += ["> A source above failed. Treat this digest as incomplete until it is re-run.", ""]
    for note in PARTIAL:
        L += [f"> Coverage caveat: {note}. Narrow the window or the keywords for full coverage.", ""]
    by_tier: dict[str, list] = {}
    for it in items:
        by_tier.setdefault(it["tier"], []).append(it)
    for tier, (label, _) in sorted(TIERS.items(), key=lambda kv: kv[1][1]):
        group = by_tier.get(tier)
        if not group:
            continue
        L += [f"## {label}", ""]
        for it in group:
            L.append(f"### {it['title'] or '(untitled)'}")
            meta = [x for x in (it.get("date"), it.get("venue"), it["source"]) if x]
            L.append(f"*{'  ·  '.join(meta)}*")
            if it.get("authors"):
                L.append(f"Authors: {', '.join(it['authors'])}"
                         + (" et al." if len(it["authors"]) >= 4 else ""))
            if it.get("also_in"):
                L.append(f"Also appeared in: {', '.join(sorted(set(it['also_in'])))}")
            if it.get("url"):
                L.append(f"Primary source: <{it['url']}>")
            else:
                L.append("Primary source: **none resolved - do not cite this item**")
            s = it.get("summary") or ""
            if s:
                L.append("")
                L.append(s[:1100] + ("..." if len(s) > 1100 else ""))
            L += ["", "---", ""]
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query", nargs="+", help="keywords, e.g. \"ALS neurofilament\"")
    ap.add_argument("--days", type=int, default=30)
    ap.add_argument("--max", type=int, default=25, help="cap per source")
    ap.add_argument("--sources", default="pubmed,trials,preprints")
    ap.add_argument("--preprint-budget", type=float, default=90.0,
                    help="seconds to spend scanning preprint servers (they are slow)")
    ap.add_argument("--out", default=None, help="digest path (default research-watch/<date>-<slug>.md)")
    a = ap.parse_args()

    query = " ".join(a.query)
    terms = [t for t in re.split(r"\s+", query.lower()) if len(t) > 2]
    want = [s.strip() for s in a.sources.split(",") if s.strip()]
    bad = [s for s in want if s not in ADAPTERS]
    if bad:
        print(f"unknown source(s): {bad}. available: {sorted(ADAPTERS)}")
        return 2

    print(f"Research watch: {query!r}, last {a.days} days\n")
    items, stats = [], {}
    for name in want:
        print(f"  {name} ...", end=" ", flush=True)
        try:
            got = (fetch_preprints(query, a.days, a.max, budget_s=a.preprint_budget)
                   if name == 'preprints' else ADAPTERS[name](query, a.days, a.max))
            items += got
            stats[name] = {"n": len(got), "error": None}
            print(f"{len(got)} item(s)" + ("   (nothing found)" if not got else ""))
        except Exception as e:                        # noqa: BLE001
            stats[name] = {"n": 0, "error": str(e)}
            print(f"FAILED: {e}")

    if all(s["error"] for s in stats.values()):
        print("\nEvery source failed. Not writing a digest that would look empty rather "
              "than broken.")
        return 1

    uniq, dropped = dedupe(items)
    ranked = rank(uniq, terms)

    out = a.out or os.path.join(
        "research-watch",
        f"{date.today().isoformat()}-{re.sub(r'[^a-z0-9]+', '-', query.lower()).strip('-')[:40]}.md")
    os.makedirs(os.path.dirname(out) or ".", exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(ranked, query, a.days, stats, dropped))

    print(f"\n{len(ranked)} distinct item(s), {dropped} duplicate(s) merged")
    for tier, (label, _) in sorted(TIERS.items(), key=lambda kv: kv[1][1]):
        n = sum(1 for i in ranked if i["tier"] == tier)
        if n:
            print(f"  {n:3d}  {label}")
    print(f"\nDigest: {out}")
    if any(s["error"] for s in stats.values()):
        print("NOTE: at least one source failed. The digest says so at the top.")
    for note in PARTIAL:
        print(f"NOTE: {note}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
