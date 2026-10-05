#!/usr/bin/env python3
"""The lead register: open questions that are never deleted, only re-checked.

    python scripts/leads.py new      --title "..." --waiting-on more-data --kind inconclusive-null
    python scripts/leads.py list     [--waiting-on X] [--kind Y] [--owner Z] [--status open]
    python scripts/leads.py due      [--as-of YYYY-MM-DD]
    python scripts/leads.py match    research-watch/2026-09-14-als.index.md
    python scripts/leads.py touch    L-003 --note "re-checked, still waiting" [--next 90]
    python scripts/leads.py resolve  L-003 --status resolved-supported --note "tested as H-004"
    python scripts/leads.py index

WHY THIS EXISTS. A finding is a claim we believe. A lead is a question we could not answer
yet, and the reason we could not answer it is the most useful thing about it: it says what
would have to change. A register that only lists leads is a graveyard. A register that
indexes them BY WHAT THEY ARE WAITING FOR can tell you, when something changes, exactly which
questions just became answerable.

SO THE ORGANISING AXIS IS `waiting_on`, NOT the topic:

  more-data        a bigger n of the same kind would settle it
  other-data       needs a dataset we do not have (different variables, different linkage)
  method           the data is here; we have not applied the right method yet
  external         waiting on evidence from outside: a paper, a trial readout, a release
  decision         blocked on a human decision or an access request, not on evidence
  nothing          actionable right now, nobody has picked it up

A lead is NEVER deleted. It is resolved, superseded, or parked, and it keeps its history.
Deleting one throws away the knowledge that somebody already looked.

SCOPE: `team` (default) or `local`. A local lead is one person's own thread. It keeps its
file, its history and its literature matching, but it stays out of LEADS.md and out of the
cross-branch claim check, so nobody else is offered it and nobody else is blocked by it.
Promote one with `leads.py touch <id> --scope team`. A lead with no scope field is a TEAM
lead, because a lead wrongly shared is merely visible while a lead wrongly hidden is lost.

ONE FILE PER LEAD (leads/L-00N.md, YAML-ish frontmatter + notes) so two researchers adding
leads on different branches never collide. LEADS.md is a generated index, not the source.

Stdlib only.
"""
from __future__ import annotations
import argparse, json, os, re, sys
from datetime import date, timedelta
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
LEADS_DIR = ROOT / "leads"
INDEX = ROOT / "LEADS.md"

WAITING = {
    "more-data":  "A bigger sample of the same kind would settle it",
    "other-data": "Needs a dataset we do not have",
    "method":     "The data is here; the right method has not been applied",
    "external":   "Waiting on evidence from outside (a paper, a trial readout, a release)",
    "decision":   "Blocked on a human decision or an access request, not on evidence",
    "nothing":    "Actionable right now, nobody has picked it up",
}
KINDS = {
    "inconclusive-null": "The data could not see an effect of the size that would matter",
    "choice-dependent":  "The answer moves with an arbitrary analysis choice",
    "subgroup-signal":   "A signal in a subgroup, not confirmed",
    "external-claim":    "Somebody else reported it; we have not tested it here",
    "data-gap":          "A question our data cannot reach at all",
    "method-gap":        "A question needing a method we have not used",
    "withdrawn-claim":   "A claim a review removed, which a better design might rescue",
}
STATUSES = ["open", "under-test", "parked", "resolved-supported",
            "resolved-refuted", "superseded"]
LIVE = {"open", "under-test", "parked"}

# A lead is either the team's to pick up, or one person's own. `local` is the private
# default-off: the lead is still a file with a history, still matched against new
# literature, still never deleted. It is simply not offered to anybody else, so it stays
# out of LEADS.md and out of the cross-branch claim check. Promote with
# `leads.py touch <id> --scope team`.
SCOPES = {
    "team":  "On the shared register. Anybody may pick it up",
    "local": "Yours alone. Not indexed, and not offered to the team",
}
DEFAULT_SCOPE = "team"


def scope_of(l: dict) -> str:
    """Leads written before this field existed are team leads, which is the safe default:
    a lead wrongly shared is visible, a lead wrongly hidden is silently lost to the team."""
    s = (l.get("scope") or DEFAULT_SCOPE).strip()
    return s if s in SCOPES else DEFAULT_SCOPE

DEFAULT_REVIEW_DAYS = {"more-data": 180, "other-data": 180, "method": 90,
                       "external": 60, "decision": 30, "nothing": 90}


def today() -> date:
    return date.fromisoformat(os.environ.get("LEADS_TODAY") or date.today().isoformat())


def parse_lead(p: Path) -> dict | None:
    txt = p.read_text(encoding="utf-8", errors="replace")
    if not txt.startswith("---"):
        return None
    _, fm, body = txt.split("---", 2)
    d: dict = {"_path": p, "body": body.strip()}
    for ln in fm.strip().splitlines():
        if ":" not in ln or ln.strip().startswith("#"):
            continue
        k, v = ln.split(":", 1)
        k, v = k.strip(), v.strip()
        if v.startswith("[") and v.endswith("]"):
            d[k] = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
        else:
            d[k] = v.strip("'\"")
    return d


def load_all() -> list[dict]:
    if not LEADS_DIR.exists():
        return []
    out = [parse_lead(p) for p in sorted(LEADS_DIR.glob("L-*.md"))]
    return [x for x in out if x]


def next_id() -> str:
    n = 0
    for l in load_all():
        m = re.match(r"L-(\d+)", l.get("id", ""))
        if m:
            n = max(n, int(m.group(1)))
    return f"L-{n + 1:03d}"


def write_lead(d: dict, body: str) -> Path:
    LEADS_DIR.mkdir(exist_ok=True)
    order = ["id", "title", "status", "kind", "waiting_on", "scope", "owner", "origin",
             "dataset", "created", "last_reviewed", "next_review", "keywords",
             "resolves_when", "estimated_n"]
    lines = ["---"]
    for k in order:
        v = d.get(k)
        if v in (None, "", []):
            continue
        lines.append(f"{k}: [{', '.join(v)}]" if isinstance(v, list) else f"{k}: {v}")
    lines.append("---")
    p = LEADS_DIR / f"{d['id']}.md"
    p.write_text("\n".join(lines) + "\n\n" + body.strip() + "\n", encoding="utf-8")
    return p


def append_history(l: dict, note: str) -> None:
    """History is append-only. A lead's value is partly the record that someone looked."""
    p: Path = l["_path"]
    txt = p.read_text(encoding="utf-8", errors="replace")
    if "## History" not in txt:
        txt = txt.rstrip() + "\n\n## History\n"
    txt = txt.rstrip() + f"\n- {today().isoformat()} — {note}\n"
    p.write_text(txt, encoding="utf-8")


def set_fields(l: dict, **kw) -> None:
    p: Path = l["_path"]
    txt = p.read_text(encoding="utf-8", errors="replace")
    head, fm, body = txt.split("---", 2)
    lines = fm.strip().splitlines()
    for k, v in kw.items():
        if v is None:
            continue
        val = f"[{', '.join(v)}]" if isinstance(v, list) else str(v)
        for i, ln in enumerate(lines):
            if ln.split(":", 1)[0].strip() == k:
                lines[i] = f"{k}: {val}"
                break
        else:
            lines.append(f"{k}: {val}")
    p.write_text("---\n" + "\n".join(lines) + "\n---" + body, encoding="utf-8")


def fmt_row(l: dict) -> str:
    due = l.get("next_review", "")
    overdue = bool(due) and due <= today().isoformat() and l.get("status") in LIVE
    mine = "local " if scope_of(l) == "local" else "      "
    return (f"  {l.get('id','?'):7s} {'!' if overdue else ' '} {mine}"
            f"{l.get('status','?'):18s} {l.get('waiting_on','?'):11s} "
            f"{(l.get('title') or '')[:52]}")


# ───────────────────────────── commands ──────────────────────────────

def cmd_new(a) -> int:
    if a.waiting_on not in WAITING:
        print(f"--waiting-on must be one of: {', '.join(WAITING)}"); return 2
    if a.kind not in KINDS:
        print(f"--kind must be one of: {', '.join(KINDS)}"); return 2
    scope = (a.scope or DEFAULT_SCOPE).strip()
    if scope not in SCOPES:
        print(f"--scope must be one of: {', '.join(SCOPES)}"); return 2
    lid = next_id()
    days = a.review_days or DEFAULT_REVIEW_DAYS[a.waiting_on]
    d = dict(id=lid, title=a.title, status="open", kind=a.kind, waiting_on=a.waiting_on,
             scope=scope, owner=a.owner or "unassigned", origin=a.origin or "-",
             dataset=a.dataset or "-", created=today().isoformat(),
             last_reviewed=today().isoformat(),
             next_review=(today() + timedelta(days=days)).isoformat(),
             keywords=[k.strip() for k in (a.keywords or "").split(",") if k.strip()],
             resolves_when=a.resolves_when or "", estimated_n=a.estimated_n or "")
    body = (f"## What is open\n\n{a.note or a.title}\n\n"
            f"## What would resolve it\n\n{a.resolves_when or 'Not yet stated.'}\n\n"
            f"## Explicitly not claimed\n\n"
            f"No effect is asserted to exist. This is a question, not a result.\n\n"
            f"## History\n\n- {today().isoformat()} — raised\n")
    p = write_lead(d, body)
    print(f"created {lid}  ->  {p.relative_to(ROOT)}")
    print(f"  waiting on : {a.waiting_on}  ({WAITING[a.waiting_on]})")
    print(f"  scope      : {scope}  ({SCOPES[scope]})")
    print(f"  next review: {d['next_review']}")
    if scope == "local":
        print(f"  {lid} stays off LEADS.md and out of the claim check. "
              f"Share it with: leads.py touch {lid} --scope team")
    cmd_index(a)
    return 0


def cmd_list(a) -> int:
    ls = load_all()
    for f in ("waiting_on", "kind", "owner", "status"):
        want = getattr(a, f, None)
        if want:
            ls = [l for l in ls if l.get(f) == want]
    if getattr(a, "scope", None):
        ls = [l for l in ls if scope_of(l) == a.scope]
    if getattr(a, "live", False):
        ls = [l for l in ls if l.get("status") in LIVE]
    if not ls:
        print("no leads match"); return 0
    ls.sort(key=lambda l: (l.get("waiting_on", ""), l.get("next_review", "")))
    cur = None
    for l in ls:
        w = l.get("waiting_on")
        if w != cur:
            cur = w
            print(f"\n  WAITING ON: {w}   {WAITING.get(w,'')}")
        print(fmt_row(l))
    n_over = sum(1 for l in ls if l.get("next_review", "9") <= today().isoformat()
                 and l.get("status") in LIVE)
    print(f"\n  {len(ls)} lead(s); {n_over} due for review (marked !)")
    return 0


def cmd_due(a) -> int:
    asof = a.as_of or today().isoformat()
    ls = [l for l in load_all()
          if l.get("status") in LIVE and (l.get("next_review") or "9") <= asof]
    if not ls:
        print(f"Nothing due as of {asof}. Every live lead has been looked at recently.")
        return 0
    print(f"\n  {len(ls)} lead(s) due for review as of {asof}\n")
    for l in sorted(ls, key=lambda x: x.get("next_review", "")):
        print(f"  {l['id']}  (due {l.get('next_review')})  waiting on {l.get('waiting_on')}")
        print(f"       {l.get('title','')}")
        if l.get("resolves_when"):
            print(f"       resolves when: {l['resolves_when']}")
    print("\n  Re-check each, then record it:  leads.py touch <id> --note \"...\"")
    print("  A lead is never deleted. If it is still open, say so and push the date out.")
    return 0


def cmd_match(a) -> int:
    """Cross-reference open leads against a research-watch digest.

    This is what makes the register something you FOLLOW rather than something you keep.
    When new literature arrives, the leads whose keywords it touches are the ones that may
    just have become answerable.
    """
    src = Path(a.digest)
    if not src.exists():
        print(f"no such file: {src}"); return 2
    text = src.read_text(encoding="utf-8", errors="replace")
    # split into items on the index format: "- **[TAG]** title"
    items = re.findall(r"- \*\*\[([A-Z\- ]+)\]\*\*\s*(.+)", text)
    if not items:
        items = [("?", ln.strip("- ").strip()) for ln in text.splitlines()
                 if ln.strip().startswith("- ")]
    ls = [l for l in load_all() if l.get("status") in LIVE]
    hits = []
    for l in ls:
        kws = [k.lower() for k in (l.get("keywords") or []) if len(k) > 2]
        if not kws:
            continue
        for tag, title in items:
            t = title.lower()
            matched = [k for k in kws
                       if re.search(r"(?<![a-z0-9])" + re.escape(k) + r"(?![a-z0-9])", t)]
            # A single generic keyword matches far too much: "neurofilament" alone
            # pulled in papers on type 2 diabetes and porcine cardiac arrest.
            # Requiring a second keyword is what turns this from noise into a
            # prompt worth reading.
            if len(matched) >= a.min_matches:
                hits.append((l, tag.strip(), title.strip(), matched))
    if not hits:
        print(f"\n  No open lead matches anything in {src.name} on "
              f"{a.min_matches}+ keywords.")
        print(f"  Checked {len(ls)} live lead(s) against {len(items)} item(s).")
        print("  That is a real answer, not a failure. Use --min-matches 1")
        print("  to skim the loose matches yourself.")
        return 0
    hits.sort(key=lambda h: -len(h[3]))
    print(f"\n  {len(hits)} possible connection(s), each matching "
          f"{a.min_matches}+ of a lead's keywords\n")
    seen = set()
    for l, tag, title, matched in hits:
        if l["id"] not in seen:
            seen.add(l["id"])
            print(f"  {l['id']}  {l.get('title','')}")
            print(f"        waiting on {l.get('waiting_on')}  ·  "
                  f"resolves when: {l.get('resolves_when','-')}")
        print(f"        [{tag}] {title[:78]}")
        print(f"        matched on: {', '.join(matched)}")
    print("\n  A keyword match is a prompt to look, not evidence. Open the item, decide")
    print("  whether it actually bears on the lead, then record the outcome with `touch`.")
    return 0


def cmd_touch(a) -> int:
    ls = {l["id"]: l for l in load_all()}
    l = ls.get(a.lead_id)
    if not l:
        print(f"no such lead: {a.lead_id}"); return 2
    new_scope = getattr(a, "scope", None)
    if new_scope and new_scope not in SCOPES:
        print(f"--scope must be one of: {', '.join(SCOPES)}"); return 2
    days = a.next or DEFAULT_REVIEW_DAYS.get(l.get("waiting_on", "nothing"), 90)
    nxt = (today() + timedelta(days=days)).isoformat()
    was = scope_of(l)
    new_owner = getattr(a, "owner", None)
    was_owner = l.get("owner", "unassigned")
    set_fields(l, last_reviewed=today().isoformat(), next_review=nxt,
               waiting_on=a.waiting_on, status=a.status, scope=new_scope,
               owner=new_owner)
    note = a.note or "re-checked, still open"
    if new_scope and new_scope != was:
        note = f"scope {was} -> {new_scope}. {note}"
    if new_owner and new_owner != was_owner:
        # Who raised a lead and who takes it are routinely different people. The history
        # keeps both; the frontmatter names whoever is on it now.
        note = f"owner {was_owner} -> {new_owner}. {note}"
    append_history(l, note)
    print(f"{a.lead_id} reviewed. next review {nxt}")
    if new_scope and new_scope != was:
        print(f"  scope is now {new_scope}  ({SCOPES[new_scope]})")
    cmd_index(a)
    return 0


def cmd_resolve(a) -> int:
    if a.status not in STATUSES:
        print(f"--status must be one of: {', '.join(STATUSES)}"); return 2
    ls = {l["id"]: l for l in load_all()}
    l = ls.get(a.lead_id)
    if not l:
        print(f"no such lead: {a.lead_id}"); return 2
    set_fields(l, status=a.status, last_reviewed=today().isoformat())
    append_history(l, f"{a.status}: {a.note or '(no note)'}")
    print(f"{a.lead_id} -> {a.status}. The lead stays in the register with its history.")
    cmd_index(a)
    return 0


def cmd_index(a) -> int:
    everything = load_all()
    ls = [l for l in everything if scope_of(l) == "team"]
    n_local = len(everything) - len(ls)
    live = [l for l in ls if l.get("status") in LIVE]
    done = [l for l in ls if l.get("status") not in LIVE]
    over = [l for l in live if (l.get("next_review") or "9") <= today().isoformat()]
    L = ["# Leads — open questions, never deleted", "",
         "**This is not the hypothesis log.** `HYPOTHESIS_LOG.md` holds findings: things we",
         "tested and now believe. This holds **leads**: questions we could not answer yet.",
         "", "A lead is a routing decision, not evidence. It never counts as prior art, and it",
         "becomes a finding only when tested on data that did not raise it.", "",
         "**Leads are never deleted.** They are resolved, superseded or parked, and they keep",
         "their history, because the record that somebody already looked is worth keeping.", "",
         f"*Generated by `scripts/leads.py index` on {today().isoformat()}. "
         f"Do not edit by hand: edit the files in `leads/`.*", "",
         f"**{len(live)} open · {len(over)} due for review · {len(done)} closed**", "",
         "## Open, grouped by what they are waiting for", ""]
    if n_local:
        L[-2:-2] = [f"*{n_local} further lead(s) are marked `scope: local` and are deliberately "
                    f"absent from this index. They belong to one person and are not offered to "
                    f"the team. They are still files in `leads/` with their full history.*", ""]
    for w, desc in WAITING.items():
        grp = [l for l in live if l.get("waiting_on") == w]
        if not grp:
            continue
        L += [f"### `{w}` — {desc}", "",
              "| id | lead | kind | owner | next review |", "|---|---|---|---|---|"]
        for l in sorted(grp, key=lambda x: x.get("next_review", "")):
            due = l.get("next_review", "")
            flag = " **(due)**" if due <= today().isoformat() else ""
            L.append(f"| [{l['id']}](leads/{l['id']}.md) | {l.get('title','')} | "
                     f"{l.get('kind','')} | {l.get('owner','')} | {due}{flag} |")
        L.append("")
    if done:
        L += ["## Closed, kept for the record", "",
              "| id | lead | outcome |", "|---|---|---|"]
        for l in sorted(done, key=lambda x: x.get("id", "")):
            L.append(f"| [{l['id']}](leads/{l['id']}.md) | {l.get('title','')} | "
                     f"{l.get('status','')} |")
        L.append("")
    L += ["## How to use it", "",
          "```", "python scripts/leads.py due                     what needs re-checking",
          "python scripts/leads.py list --waiting-on more-data",
          "python scripts/leads.py match <a research-watch index>   new papers vs open leads",
          "python scripts/leads.py touch L-003 --note \"...\"        record a re-check",
          "python scripts/leads.py new  ... --scope local           keep a lead to yourself",
          "python scripts/leads.py touch L-003 --scope team         offer it to the team", "```", ""]
    INDEX.write_text("\n".join(L), encoding="utf-8")
    if getattr(a, "_quiet", False):
        return 0
    tail = f", {n_local} local and not indexed" if n_local else ""
    print(f"index written: {INDEX.name}  ({len(live)} open, {len(over)} due, "
          f"{len(done)} closed{tail})")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    n = sub.add_parser("new", help="raise a lead")
    n.add_argument("--title", required=True)
    n.add_argument("--waiting-on", required=True, dest="waiting_on")
    n.add_argument("--kind", required=True)
    n.add_argument("--owner"); n.add_argument("--origin"); n.add_argument("--dataset")
    n.add_argument("--keywords", help="comma-separated; used to match new literature")
    n.add_argument("--resolves-when", dest="resolves_when")
    n.add_argument("--estimated-n", dest="estimated_n")
    n.add_argument("--review-days", type=int, dest="review_days")
    n.add_argument("--scope", choices=sorted(SCOPES),
                   help="team (default, on the shared register) or local (yours alone)")
    n.add_argument("--note")
    n.set_defaults(f=cmd_new)

    l = sub.add_parser("list", help="list leads")
    for x in ("waiting-on", "kind", "owner", "status", "scope"):
        l.add_argument(f"--{x}", dest=x.replace("-", "_"))
    l.add_argument("--live", action="store_true", help="only open/under-test/parked")
    l.set_defaults(f=cmd_list)

    d = sub.add_parser("due", help="what needs re-checking")
    d.add_argument("--as-of", dest="as_of")
    d.set_defaults(f=cmd_due)

    m = sub.add_parser("match", help="cross-reference new literature against open leads")
    m.add_argument("digest", help="a research-watch .index.md or digest")
    m.add_argument("--min-matches", type=int, default=2,
                   help="distinct keywords an item must hit (default 2; 1 is very noisy)")
    m.set_defaults(f=cmd_match)

    t = sub.add_parser("touch", help="record that a lead was re-checked")
    t.add_argument("lead_id"); t.add_argument("--note")
    t.add_argument("--next", type=int, help="days until the next review")
    t.add_argument("--waiting-on", dest="waiting_on"); t.add_argument("--status")
    t.add_argument("--owner", help="who is on it now, which is not always who raised it")
    t.add_argument("--scope", choices=sorted(SCOPES),
                   help="promote a local lead to the team register, or take one back")
    t.set_defaults(f=cmd_touch)

    r = sub.add_parser("resolve", help="close a lead, keeping it in the register")
    r.add_argument("lead_id"); r.add_argument("--status", required=True)
    r.add_argument("--note")
    r.set_defaults(f=cmd_resolve)

    i = sub.add_parser("index", help="regenerate LEADS.md")
    i.set_defaults(f=cmd_index)

    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
