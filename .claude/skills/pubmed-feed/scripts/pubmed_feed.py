#!/usr/bin/env python3
"""
pubmed_feed.py — search PubMed for recent papers on your keywords and append them
to a running Markdown list. Uses NCBI E-utilities (public; no account required).

Examples
--------
  py pubmed_feed.py "ALS neurofilament"                 # last 7 days, up to 20 papers
  py pubmed_feed.py "ALS biomarker" --days 30 --max 15
  py pubmed_feed.py "amyotrophic lateral sclerosis AND TDP-43" --since 2026/06/01 --until 2026/07/13
  py pubmed_feed.py "ALS" --out literature/als-feed.md

A free NCBI API key is optional (only raises the rate limit). If you have one:
  set NCBI_API_KEY=xxxxx   (Windows)   /   export NCBI_API_KEY=xxxxx  (Mac/Linux)
"""
import argparse, json, os, sys, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
TOOL = "als-team-pubmed-feed"
EMAIL = "emmanuel.mompi@smartglobe.fr"     # NCBI etiquette (helps them contact you, not required)
API_KEY = os.environ.get("NCBI_API_KEY", "")


def _get(endpoint, params):
    params = {**params, "tool": TOOL, "email": EMAIL}
    if API_KEY:
        params["api_key"] = API_KEY
    url = f"{EUTILS}/{endpoint}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": TOOL})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read()


def search(query, retmax, days, since, until):
    params = {"db": "pubmed", "term": query, "retmax": retmax,
              "sort": "date", "retmode": "json", "datetype": "pdat"}
    if since or until:
        params["mindate"] = since or "1900/01/01"
        params["maxdate"] = until or datetime.now(timezone.utc).strftime("%Y/%m/%d")
    else:
        params["reldate"] = days
    data = json.loads(_get("esearch.fcgi", params))
    res = data["esearchresult"]
    return res.get("idlist", []), int(res.get("count", 0))


def _text(node):
    return "".join(node.itertext()).strip() if node is not None else ""


def fetch_details(pmids):
    if not pmids:
        return []
    xml = _get("efetch.fcgi", {"db": "pubmed", "id": ",".join(pmids), "retmode": "xml"})
    root = ET.fromstring(xml)
    out = []
    for art in root.findall(".//PubmedArticle"):
        pmid = _text(art.find(".//PMID"))
        title = _text(art.find(".//ArticleTitle")) or "(no title)"
        # abstract (may be several labelled sections)
        parts = []
        for ab in art.findall(".//Abstract/AbstractText"):
            lbl = ab.get("Label")
            txt = _text(ab)
            parts.append(f"**{lbl}:** {txt}" if lbl else txt)
        abstract = "\n\n".join(p for p in parts if p) or "(no abstract)"
        # authors
        names = []
        for a in art.findall(".//AuthorList/Author"):
            last = _text(a.find("LastName"))
            init = _text(a.find("Initials"))
            coll = _text(a.find("CollectiveName"))
            if last:
                names.append(f"{last} {init}".strip())
            elif coll:
                names.append(coll)
        authors = ", ".join(names[:3]) + (" et al." if len(names) > 3 else "")
        journal = _text(art.find(".//Journal/Title")) or _text(art.find(".//Journal/ISOAbbreviation"))
        # date
        pd = art.find(".//JournalIssue/PubDate")
        if pd is not None:
            y = _text(pd.find("Year")); m = _text(pd.find("Month")); d = _text(pd.find("Day"))
            date = " ".join(x for x in (y, m, d) if x) or _text(pd.find("MedlineDate"))
        else:
            date = ""
        doi = ""
        for idn in art.findall(".//ArticleId"):
            if idn.get("IdType") == "doi":
                doi = _text(idn)
        out.append({"pmid": pmid, "title": title, "abstract": abstract,
                    "authors": authors or "(authors n/a)", "journal": journal or "(journal n/a)",
                    "date": date, "doi": doi})
    return out


def existing_pmids(path):
    if not os.path.exists(path):
        return set()
    import re
    with open(path, encoding="utf-8") as f:
        return set(re.findall(r"PMID:\s*(\d+)", f.read()))


def render(entry):
    url = f"https://pubmed.ncbi.nlm.nih.gov/{entry['pmid']}/"
    doi = f" · doi:{entry['doi']}" if entry["doi"] else ""
    return (f"### {entry['title']}\n"
            f"*{entry['authors']}* — **{entry['journal']}**, {entry['date']}  \n"
            f"PMID: {entry['pmid']} · [{url}]({url}){doi}\n\n"
            f"{entry['abstract']}\n")


def main():
    ap = argparse.ArgumentParser(description="Append recent PubMed papers to a running list.")
    ap.add_argument("query", nargs="+", help="keywords / PubMed query (quote multi-word phrases)")
    ap.add_argument("--days", type=int, default=7, help="look back this many days (default 7)")
    ap.add_argument("--max", type=int, default=20, help="max papers to fetch (default 20)")
    ap.add_argument("--since", help="start date YYYY/MM/DD (overrides --days)")
    ap.add_argument("--until", help="end date YYYY/MM/DD")
    ap.add_argument("--out", default="pubmed-feed.md", help="running list file (default pubmed-feed.md)")
    a = ap.parse_args()
    try:  # make console output safe for any terminal codepage (e.g. Greek letters in titles)
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    query = " ".join(a.query)

    window = (f"{a.since or '...'} to {a.until or 'today'}" if (a.since or a.until)
              else f"last {a.days} days")
    print(f"PubMed: \"{query}\"  ({window}, up to {a.max})")

    ids, total = search(query, a.max, a.days, a.since, a.until)
    print(f"  {total} total match this query; pulling {len(ids)} most recent.")
    if not ids:
        print("  No papers in this window. Try a wider --days or different keywords.")
        return
    time.sleep(0.4)
    entries = fetch_details(ids)

    seen = existing_pmids(a.out)
    fresh = [e for e in entries if e["pmid"] not in seen]
    dupes = len(entries) - len(fresh)

    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    stamp = datetime.now(timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
    new_file = not os.path.exists(a.out)
    with open(a.out, "a", encoding="utf-8") as f:
        if new_file:
            f.write("# PubMed feed — running literature list\n\n")
        f.write(f"\n---\n\n## {stamp} — \"{query}\" ({window})\n\n")
        if fresh:
            for e in fresh:
                f.write(render(e) + "\n")
        else:
            f.write("_No new papers since last run._\n")

    print(f"  {len(fresh)} new added" + (f", {dupes} already in list (skipped)." if dupes else "."))
    for e in fresh:
        print(f"   • {e['title'][:90]}  [{e['journal']}, {e['date']}]")
    print(f"  -> saved to {os.path.abspath(a.out)}")


if __name__ == "__main__":
    main()
