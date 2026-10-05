#!/usr/bin/env python3
"""prior_art.py — has anybody on the team already done this?

    python scripts/prior_art.py check "does an NfL trend beat a single draw"
    python scripts/prior_art.py running
    python scripts/prior_art.py next-id --kind L

WHY THIS EXISTS. Every researcher works on their own branch, so a question somebody claimed
this morning is invisible to everybody else until the maintainer merges. That is too slow to
stop two people spending a week on the same thing. This reads every branch directly, so a
claim is visible the moment it is pushed and never has to reach the trunk first.

WHAT IT DOES NOT DO. It does not decide whether two questions are the same. It gathers
candidates by matching words and puts them in front of you. Judging whether your question is
genuinely the one already claimed is a reading job, and it stays with the person or with
Claude. A script that decided this would be confidently wrong on the interesting cases.

WHY TWO MATCHING WORDS AND NOT ONE. One shared word is noise. When the lead register was
matched against a fortnight of literature at one word it produced twenty-six suggestions
including a study in pigs; at two it produced four, and they were the right four. `ALS` is
never matched on at all, because every entry here is about ALS and because PubMed reads a
bare ALS as Advanced Life Support and Crossref reads it as the German word.

SCOPE. Leads marked `scope: local` belong to one person and are skipped entirely. They are
not offered to you and they do not block you.

Stdlib only. Reads with `git show` and `git ls-tree`, so nothing is checked out and no
working tree is touched.
"""
from __future__ import annotations
import argparse, os, re, subprocess, sys, time
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
TRUNK = ["origin/develop", "origin/main"]
LEADS_DIR = "leads"
LOG = "HYPOTHESIS_LOG.md"

# A claim nobody has closed after this long is worth asking about. Manu asked for the age
# rather than an expiry: the script reports, a human decides.
STALE_DAYS = 30

# Words that match everything here and therefore discriminate nothing. `als` and `proact`
# are in this list for two reasons: every entry is about them, and both are ambiguous
# outside this repo.
STOP = set("""
a an and are as at be been but by can could did do does for from had has have how i if in
into is it its may might must no not of on or our over per shall should since so some such
than that the their then there these they this those to under until up upon was we were
what when where whether which while who whom why will with within without would you your
als proact patient patients patient's subject subjects cohort data dataset analysis study
studies effect effects association associated predict predicts predictor question test
tested testing result results finding findings baseline measure measured measurement
""".split())

WORD = re.compile(r"[a-z0-9][a-z0-9\-]*")
LIVE_LEAD = {"open", "under-test", "parked"}
LIVE_HYP = {"under analysis", "proposed"}


# ───────────────────────────── git plumbing ──────────────────────────────

def git(*args: str) -> str | None:
    """Return stdout, or None if git failed. Never raises, so one unreadable branch cannot
    take the whole check down with it."""
    env = dict(os.environ, MSYS_NO_PATHCONV="1")  # harmless here, needed under Git Bash
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, env=env,
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=30)
    except Exception:
        return None
    return r.stdout if r.returncode == 0 else None


def branches(include_trunk: bool = True) -> list[str]:
    out = git("for-each-ref", "--format=%(refname)",
              "refs/remotes/origin/researchers") or ""
    refs = [ln.strip().replace("refs/remotes/", "", 1)
            for ln in out.splitlines() if ln.strip()]
    if include_trunk:
        for t in TRUNK:
            if git("rev-parse", "--verify", "--quiet", t):
                refs.append(t)
    return refs


def who(ref: str) -> str:
    return ref.rsplit("/", 1)[-1] if "researchers/" in ref else ref.replace("origin/", "")


# ───────────────────────────── reading a branch ──────────────────────────────

def parse_frontmatter(txt: str) -> dict:
    if not txt.startswith("---"):
        return {}
    try:
        _, fm, _ = txt.split("---", 2)
    except ValueError:
        return {}
    d: dict = {}
    for ln in fm.strip().splitlines():
        if ":" not in ln or ln.strip().startswith("#"):
            continue
        k, v = ln.split(":", 1)
        k, v = k.strip(), v.strip()
        d[k] = ([x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
                if v.startswith("[") and v.endswith("]") else v.strip("'\""))
    return d


TREE_ROW = re.compile(r"^\d+\s+blob\s+([0-9a-f]+)\s+(.+)$")


def lead_blobs(ref: str) -> list[tuple[str, str]]:
    """(sha, path) for every lead file on a branch.

    Every branch carries a full copy of `leads/`, so the same lead is on all of them. Keying
    on the blob sha means an unchanged lead is read once for the whole team rather than once
    per branch, and it makes divergence visible: two shas for one id means somebody changed
    that lead on their branch, which is exactly the thing worth seeing."""
    listing = git("ls-tree", "-r", ref, "--", LEADS_DIR) or ""
    out = []
    for ln in listing.splitlines():
        m = TREE_ROW.match(ln.strip())
        if m and re.fullmatch(r"leads/L-\d+\.md", m.group(2).strip()):
            out.append((m.group(1), m.group(2).strip()))
    return out


H_HEAD = re.compile(r"^##\s+(H-\d+)\s*[—\-–]\s*(.+?)\s*$", re.M)


def hyps_on(ref: str) -> list[dict]:
    txt = git("show", f"{ref}:{LOG}")
    if not txt:
        return []
    heads = list(H_HEAD.finditer(txt))
    out = []
    for i, m in enumerate(heads):
        body = txt[m.end(): heads[i + 1].start() if i + 1 < len(heads) else len(txt)]
        def field(name: str) -> str:
            f = re.search(rf"\*\*{name}:\*\*\s*(.+)", body)
            return f.group(1).strip() if f else ""
        out.append({"id": m.group(1), "title": m.group(2), "status": field("Status"),
                    "owner": field("Owner"), "date": field("Date"),
                    "text": field("Hypothesis"), "_ref": ref, "_who": who(ref)})
    return out


def harvest(refs: list[str]) -> tuple[list[dict], list[dict]]:
    """Returns deduplicated leads and log entries. Each record carries `_refs`, the branches
    that hold exactly that version, so an unchanged shared copy is reported once."""
    with ThreadPoolExecutor(max_workers=8) as ex:
        per_ref = list(ex.map(lead_blobs, refs))
        hyp_lists = list(ex.map(hyps_on, refs))

    where: dict[str, list[str]] = {}
    for ref, rows in zip(refs, per_ref):
        for sha, _ in rows:
            where.setdefault(sha, []).append(who(ref))
    shas = sorted(where)
    with ThreadPoolExecutor(max_workers=8) as ex:
        blobs = list(ex.map(lambda s: git("cat-file", "-p", s), shas))

    leads = []
    for sha, txt in zip(shas, blobs):
        if not txt:
            continue
        d = parse_frontmatter(txt)
        if not d.get("id"):
            continue
        if (d.get("scope") or "team").strip() == "local":
            continue  # somebody else's private thread; not ours to offer or to block on
        d["_refs"] = sorted(where[sha])
        leads.append(d)

    # Log entries are parsed per branch, so fold identical ones together the same way.
    seen: dict[tuple, dict] = {}
    for hs in hyp_lists:
        for h in hs:
            key = (h["id"], h.get("status"), h.get("owner"), h.get("date"), h.get("title"))
            rec = seen.setdefault(key, {**h, "_refs": []})
            rec["_refs"].append(h["_who"])
    hyps = [{**h, "_refs": sorted(set(h["_refs"]))} for h in seen.values()]
    return leads, hyps


def source(rec: dict, total: int) -> str:
    """Where a record lives, said in the fewest words that stay accurate."""
    refs = rec.get("_refs") or []
    if len(refs) >= total:
        return "the shared copy, on every branch"
    if len(refs) == 1:
        return f"only on {refs[0]}"
    return f"on {len(refs)} branches: {', '.join(refs[:4])}{' ...' if len(refs) > 4 else ''}"


# ───────────────────────────── matching ──────────────────────────────

def toks(*parts) -> set[str]:
    bag: set[str] = set()
    for p in parts:
        if isinstance(p, list):
            p = " ".join(p)
        for w in WORD.findall((p or "").lower()):
            if len(w) > 2 and w not in STOP:
                bag.add(w)
    return bag


def lead_toks(l: dict) -> set[str]:
    return toks(l.get("title"), l.get("keywords"), l.get("resolves_when"))


def hyp_toks(h: dict) -> set[str]:
    return toks(h.get("title"), h.get("text"))


def n_of(n: int, one: str, many: str | None = None) -> str:
    return f"{n} {one if n == 1 else (many or one + 's')}"


def days_since(iso: str) -> int | None:
    try:
        return (date.today() - date.fromisoformat(iso.strip()[:10])).days
    except Exception:
        return None


def age_phrase(iso: str, verb: str) -> str:
    d = days_since(iso)
    if d is None:
        return f"{verb} {iso}" if iso else "no date recorded"
    if d == 0:
        return f"{verb} today"
    return f"{verb} {d} day{'s' if d != 1 else ''} ago"


# ───────────────────────────── commands ──────────────────────────────

def cmd_check(a) -> int:
    t0 = time.time()
    if not a.no_fetch:
        git("fetch", "origin", "--prune", "--quiet")
    refs = branches()
    if not refs:
        print("No researcher branches could be read. Is this a clone with an "
              "'origin' remote? Nothing was checked.")
        return 2
    q = toks(a.question)
    if len(q) < 2:
        print(f"Only {len(q)} usable word{'' if len(q) == 1 else 's'} in that question "
              f"after common words were dropped. Say a little more so there is something "
              f"to match on.")
        return 2

    leads, hyps = harvest(refs)
    lead_hits, hyp_hits = [], []
    for l in leads:
        shared = q & lead_toks(l)
        if len(shared) >= a.min_matches:
            lead_hits.append((l, sorted(shared)))
    for h in hyps:
        shared = q & hyp_toks(h)
        if len(shared) >= a.min_matches:
            hyp_hits.append((h, sorted(shared)))

    live_l = [(l, s) for l, s in lead_hits if (l.get("status") or "") in LIVE_LEAD]
    live_h = [(h, s) for h, s in hyp_hits if (h.get("status") or "").lower() in LIVE_HYP]
    done_h = [(h, s) for h, s in hyp_hits if (h.get("status") or "").lower() not in LIVE_HYP]

    dt = time.time() - t0
    print(f"\nChecked {n_of(len(refs), 'branch', 'branches')} in {dt:.1f}s: "
          f"{n_of(len(leads), 'lead')} and "
          f"{n_of(len(hyps), 'log entry', 'log entries')}.\n")

    if not (lead_hits or hyp_hits):
        print("  Nothing on any branch matches this question.")
        print(f"  (Matched on: {', '.join(sorted(q)[:8])})\n")
        print("  Nobody has claimed it and nobody has tested it. Register it before you run.")
        return 0

    if live_h:
        print("SOMEBODY IS WORKING ON THIS RIGHT NOW")
        for h, s in live_h:
            print(f"  {h['id']}  {h['title'][:64]}")
            print(f"         {h.get('owner','?')}, "
                  f"{age_phrase(h.get('date',''), 'registered')}, status {h.get('status')}")
            print(f"         {source(h, len(refs))}")
            print(f"         matched on: {', '.join(s)}")
        print()
    if live_l:
        print("ALREADY ON THE REGISTER AND STILL OPEN")
        for l, s in live_l:
            print(f"  {l['id']}  {l.get('title','')[:64]}")
            print(f"         owner {l.get('owner','?')}, status {l.get('status')}, "
                  f"waiting on {l.get('waiting_on')}")
            print(f"         {source(l, len(refs))}")
            print(f"         matched on: {', '.join(s)}")
        print()
    if done_h:
        print("ALREADY TESTED, AND THE RESULT IS ON THE BOARD")
        for h, s in done_h:
            print(f"  {h['id']}  {h['title'][:64]}")
            print(f"         {h.get('owner','?')}, {h.get('date','')}, "
                  f"status {h.get('status')}")
            print(f"         {source(h, len(refs))}")
            print(f"         matched on: {', '.join(s)}")
        print()

    print("A match is a candidate, not a verdict. Read the entries above and decide whether")
    print("your question is genuinely the same one. Re-running a question on newer or")
    print("different data is a new finding rather than a duplicate.")
    if a.gate and (live_h or live_l):
        print("\nRefusing to continue: something live overlaps. Pass --no-gate to override.")
        return 1
    return 0


def cmd_running(a) -> int:
    t0 = time.time()
    if not a.no_fetch:
        git("fetch", "origin", "--prune", "--quiet")
    refs = branches()
    leads, hyps = harvest(refs)
    open_h = [h for h in hyps if (h.get("status") or "").lower() in LIVE_HYP]
    open_l = [l for l in leads if (l.get("status") or "") == "under-test"]
    dt = time.time() - t0

    print(f"\nWHAT THE TEAM IS WORKING ON   "
          f"({n_of(len(refs), 'branch', 'branches')}, {dt:.1f}s)\n")
    if not (open_h or open_l):
        print("  Nothing is registered as under way on any branch.\n")
    stale = []
    for h in sorted(open_h, key=lambda x: x.get("date", "")):
        d = days_since(h.get("date", ""))
        mark = "  !" if d is not None and d >= STALE_DAYS else "   "
        print(f"{mark} {h['id']}  {h['title'][:52]:52s}  {h.get('owner','?'):10s} "
              f"{age_phrase(h.get('date',''), 'registered')}")
        if d is not None and d >= STALE_DAYS:
            stale.append(h["id"])
    for l in sorted(open_l, key=lambda x: x.get("last_reviewed", "")):
        d = days_since(l.get("last_reviewed", ""))
        mark = "  !" if d is not None and d >= STALE_DAYS else "   "
        print(f"{mark} {l['id']}  {l.get('title','')[:52]:52s}  {l.get('owner','?'):10s} "
              f"{age_phrase(l.get('last_reviewed',''), 'taken')}")
        if d is not None and d >= STALE_DAYS:
            stale.append(l["id"])

    unclaimed = [l for l in leads if (l.get("status") or "") == "open"]
    if unclaimed:
        print(f"\n  Open and unclaimed: "
              f"{', '.join(sorted({l['id'] for l in unclaimed}))}")
    if stale:
        print(f"\n  ! open {STALE_DAYS} days or more without a conclusion: "
              f"{', '.join(stale)}")
        print("    Worth asking at the Monday meeting whether these are still moving.")
    print()
    return 0


def cmd_next_id(a) -> int:
    if not a.no_fetch:
        git("fetch", "origin", "--prune", "--quiet")
    refs = branches()
    leads, hyps = harvest(refs)
    pool = ([l.get("id", "") for l in leads] if a.kind == "L"
            else [h.get("id", "") for h in hyps])
    n = 0
    for i in pool:
        m = re.match(rf"{a.kind}-(\d+)", i or "")
        if m:
            n = max(n, int(m.group(1)))
    # Allocating from the maximum ACROSS ALL BRANCHES is what stops two people minting the
    # same id on different branches. The residual race is two people allocating within the
    # same few seconds, which duplicates a record rather than losing one.
    print(f"{a.kind}-{n + 1:03d}")
    return 0


def main() -> int:
    # --no-fetch lives on a shared parent so it works before OR after the subcommand.
    # Putting it only on the top level is the kind of detail that makes a tool feel broken.
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--no-fetch", action="store_true",
                        help="skip 'git fetch'; faster, but you may be reading a stale copy")

    ap = argparse.ArgumentParser(description=__doc__, parents=[common],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("check", parents=[common],
                       help="has anybody claimed or tested this already?")
    c.add_argument("question")
    c.add_argument("--min-matches", type=int, default=2, dest="min_matches",
                   help="distinct words a candidate must share (default 2; 1 is very noisy)")
    c.add_argument("--gate", dest="gate", action="store_true", default=True,
                   help="exit non-zero when something live overlaps (the default)")
    c.add_argument("--no-gate", dest="gate", action="store_false",
                   help="report and always exit 0")
    c.set_defaults(f=cmd_check)

    r = sub.add_parser("running", parents=[common],
                       help="what is claimed across the team and not yet closed")
    r.set_defaults(f=cmd_running)

    n = sub.add_parser("next-id", parents=[common],
                       help="allocate the next id across every branch")
    n.add_argument("--kind", choices=["L", "H"], required=True)
    n.set_defaults(f=cmd_next_id)

    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
