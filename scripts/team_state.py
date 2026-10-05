#!/usr/bin/env python3
"""The team's current state, put in front of Claude without anybody asking for it.

    python scripts/team_state.py refresh          read every branch, write the cache
    python scripts/team_state.py digest --full    the session-start version
    python scripts/team_state.py digest --brief   the per-prompt version

WHY THIS EXISTS. `prior_art.py` could always answer "has anybody done this". What made it
run was a paragraph in CLAUDE.md asking Claude to run it, and a paragraph is a wish. These
two digests are wired to hooks instead, so the board arrives WITH the question rather than
being fetched if somebody remembers. A researcher can still ask for any of it directly; this
is about what happens when they do not.

THE COST, AND HOW IT IS KEPT DOWN. Reading nine branches takes about a second and a network
round trip, which is fine once per session and far too much per prompt. So `refresh` does the
real work at session start and writes a cache; `digest --brief` reads that cache and never
touches the network. A cache older than CACHE_MAX_AGE_MIN is reported as stale rather than
silently trusted, because a confidently out-of-date board is worse than an honestly old one.

IT FAILS OPEN. Every path here prints nothing rather than an error. A researcher must never
see a stack trace because a convenience could not reach the network.

Stdlib only.
"""
from __future__ import annotations
import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".state" / "team_state.json"
CACHE_MAX_AGE_MIN = 45

# A brief digest rides on every prompt, so it has a hard ceiling. Past this it stops being
# a reminder and starts being the thing that fills the conversation it exists to protect.
BRIEF_MAX_LINES = 16


def quiet(*_a) -> None:
    sys.exit(0)


def collect() -> dict:
    import prior_art as pa

    refs = pa.branches()
    leads, hyps = pa.harvest(refs)
    me = (pa.git("config", "--local", "user.name") or "").strip()
    branch = (pa.git("rev-parse", "--abbrev-ref", "HEAD") or "").strip()

    def live_h(h):
        return (h.get("status") or "").lower() in pa.LIVE_HYP

    return {
        "at": time.time(),
        "me": me,
        "branch": branch,
        "branches": len(refs),
        "unclaimed": sorted({l["id"] for l in leads
                             if (l.get("status") or "") == "open"
                             and (l.get("waiting_on") or "") == "nothing"}),
        "open_other": sorted({l["id"] for l in leads
                              if (l.get("status") or "") == "open"
                              and (l.get("waiting_on") or "") != "nothing"}),
        "under_test": [{"id": l["id"], "title": (l.get("title") or "")[:60],
                        "owner": l.get("owner", "?"),
                        "since": l.get("last_reviewed", "")}
                       for l in leads if (l.get("status") or "") == "under-test"],
        "running": [{"id": h["id"], "title": h.get("title", "")[:60],
                     "owner": h.get("owner", "?"), "since": h.get("date", "")}
                    for h in hyps if live_h(h)],
        "done": [{"id": h["id"], "title": h.get("title", "")[:60],
                  "owner": h.get("owner", "?"), "status": h.get("status", "")}
                 for h in hyps if not live_h(h)],
    }


def load() -> tuple[dict | None, bool]:
    """(state, stale). Never raises."""
    try:
        d = json.loads(CACHE.read_text(encoding="utf-8"))
    except Exception:
        return None, True
    age_min = (time.time() - float(d.get("at", 0))) / 60.0
    return d, age_min > CACHE_MAX_AGE_MIN


def mine(state: dict, rows: list[dict]) -> list[dict]:
    me = (state.get("me") or "").lower()
    if not me:
        return []
    return [r for r in rows if (r.get("owner") or "").lower() == me]


def cmd_refresh(_a) -> int:
    try:
        state = collect()
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(state, indent=1), encoding="utf-8")
    except Exception:
        quiet()
    return 0


def cmd_digest(a) -> int:
    if a.full:
        try:
            state = collect()
            CACHE.parent.mkdir(parents=True, exist_ok=True)
            CACHE.write_text(json.dumps(state, indent=1), encoding="utf-8")
        except Exception:
            quiet()
        stale = False
    else:
        state, stale = load()
        if not state:
            quiet()  # nothing cached yet; the session-start hook will fill it

    L: list[str] = []
    out_mine = mine(state, state.get("running", [])) + mine(state, state.get("under_test", []))

    if a.full:
        L.append(f"TEAM STATE  ({state.get('branches', 0)} branches read)")
        L.append(f"  you are on: {state.get('branch', '?')}  as  {state.get('me') or 'IDENTITY NOT SET'}")
        done = state.get("done", [])
        if done:
            L.append(f"  on the shared board: {len(done)} finding(s)")
            for h in done[:4]:
                L.append(f"      {h['id']}  {h['title']}  ({h['owner']}, {h['status']})")
    else:
        L.append("TEAM STATE (cached)")

    running = state.get("running", []) + state.get("under_test", [])
    if running:
        L.append(f"  claimed right now, do not duplicate:")
        for r in running[:5]:
            L.append(f"      {r['id']}  {r['title']}  ({r['owner']}, since {r.get('since', '?')})")
    else:
        L.append("  claimed right now: nothing")

    unclaimed = state.get("unclaimed", [])
    if unclaimed:
        L.append(f"  open and unblocked, nobody has taken them: {', '.join(unclaimed)}")
    if a.full and state.get("open_other"):
        L.append(f"  open but waiting on data or outside evidence: "
                 f"{', '.join(state['open_other'])}")

    if out_mine:
        L.append("  YOURS, claimed and not closed:")
        for r in out_mine:
            L.append(f"      {r['id']}  {r['title']}  (since {r.get('since', '?')})")

    if stale:
        L.append(f"  (this picture is over {CACHE_MAX_AGE_MIN} minutes old; "
                 f"run scripts/prior_art.py running for the live one)")

    L.append("  Before registering anything, run: "
             "python scripts/prior_art.py check \"<the question>\"")

    if not a.full:
        L = L[:BRIEF_MAX_LINES]
    text = "\n".join(L)
    if a.hook_event:
        # Plain stdout is not reliably added to the model's context; additionalContext is.
        print(json.dumps({"hookSpecificOutput": {"hookEventName": a.hook_event,
                                                 "additionalContext": text},
                          "suppressOutput": True}))
    else:
        print(text)
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("refresh", help="read every branch and cache the result")
    r.set_defaults(f=cmd_refresh)
    d = sub.add_parser("digest", help="print the state for a hook to inject")
    g = d.add_mutually_exclusive_group(required=True)
    g.add_argument("--full", action="store_true", help="session start: reads live")
    g.add_argument("--brief", action="store_true", help="per prompt: reads the cache only")
    d.add_argument("--hook-event", dest="hook_event",
                   choices=["SessionStart", "UserPromptSubmit"],
                   help="emit hook JSON so the text is injected as context")
    d.set_defaults(f=cmd_digest)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception:
        quiet()
