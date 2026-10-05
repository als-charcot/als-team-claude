#!/usr/bin/env python3
"""PreToolUse guard: a finding cannot reach the team without a registration behind it.

Wired to Bash in `.claude/settings.json`, filtered to `git push`. If the push would carry
anything under `findings/` and no entry in `HYPOTHESIS_LOG.md` points at that work, it
refuses and says exactly what is missing.

WHY HERE AND NOWHERE ELSE. You cannot mechanically stop somebody running an analysis, and
you should not try. What you can do is make the result unshareable until the question was
declared. The push is the only moment where the whole team is about to be affected, which
makes it the one place a refusal is both enforceable and fair.

WHAT IT DELIBERATELY DOES NOT CHECK. It does not compare the entry's owner against the git
identity. The log records display names ("Manu") while git records usernames ("emompi"), and
a guard that refused on that mismatch would refuse the maintainer's own pushes today. It
reports the mismatch and lets it through; tightening this needs the identity question
settled first, not a stricter regex.

HOW IT FAILS, WHICH IS THE PART THAT MATTERS. On a definite violation it refuses. On an
internal problem (no upstream, git unavailable, an unreadable log) it ALLOWS and says that
it could not check. A crashed guard that strands a non-coder mid-push is a worse failure
than the one it exists to prevent, and a guard that hides its own blind spots is not
trustworthy.

Stdlib only.
"""
from __future__ import annotations
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG = "HYPOTHESIS_LOG.md"
FINDING = re.compile(r"^findings/([^/]+)/([^/]+)/")


def say(obj: dict) -> None:
    print(json.dumps(obj))
    sys.exit(0)


def allow_quietly() -> None:
    sys.exit(0)


def allow_but_warn(why: str) -> None:
    say({"systemMessage": f"Registration check skipped: {why}. The push was not blocked.",
         "suppressOutput": True})


def refuse(reason: str) -> None:
    say({"hookSpecificOutput": {"hookEventName": "PreToolUse",
                                "permissionDecision": "deny",
                                "permissionDecisionReason": reason}})


def git(*args: str) -> str | None:
    env = dict(os.environ, MSYS_NO_PATHCONV="1")
    try:
        r = subprocess.run(["git", *args], cwd=ROOT, env=env, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=20)
    except Exception:
        return None
    return r.stdout if r.returncode == 0 else None


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        allow_quietly()

    cmd = ((payload.get("tool_input") or {}).get("command") or "")
    if not re.search(r"\bgit\s+push\b", cmd):
        allow_quietly()

    upstream = (git("rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}") or "").strip()
    if not upstream:
        allow_but_warn("this branch tracks nothing, so there is no range to inspect")

    changed = git("diff", "--name-only", f"{upstream}..HEAD")
    if changed is None:
        allow_but_warn("the pushed range could not be read")

    slugs = set()
    for line in changed.splitlines():
        m = FINDING.match(line.strip())
        if m:
            slugs.add(f"findings/{m.group(1)}/{m.group(2)}")
    if not slugs:
        allow_quietly()  # nothing is being shared with the team; not this guard's business

    log_text = git("show", f"HEAD:{LOG}")
    if log_text is None:
        refuse(f"This push adds {', '.join(sorted(slugs))} but {LOG} could not be read at "
               f"HEAD, so there is no way to confirm the question was registered. Registering "
               f"a question before testing it is not optional here. Ask Claude to register "
               f"the question, then push again.")

    missing = [s for s in sorted(slugs) if s not in log_text]
    if not missing:
        owners = sorted(set(re.findall(r"\*\*Owner:\*\*\s*(.+)", log_text)))
        me = (git("config", "--local", "user.name") or "").strip()
        note = ""
        if me and owners and not any(me.lower() == o.strip().lower() for o in owners):
            note = (f" (The log records owners as {', '.join(o.strip() for o in owners)} "
                    f"while git identifies you as {me}. Not blocking on that, but worth "
                    f"making consistent.)")
        say({"systemMessage": f"Registration check passed for "
                              f"{', '.join(sorted(slugs))}.{note}",
             "suppressOutput": True})

    refuse(
        "This push would share work that was never registered.\n\n"
        f"Being shared: {', '.join(missing)}\n"
        f"Not referenced anywhere in {LOG}.\n\n"
        "A finding reaches the team only after the question behind it was written down, so "
        "that a colleague can see it was being worked on rather than discovering it "
        "afterwards. This is the one rule the project treats as non-negotiable.\n\n"
        "To fix it: ask Claude to register this question and record the result in "
        f"{LOG} with its evidence path, then push again. If you believe this is wrong, run "
        f"`git diff --name-only {upstream}..HEAD` to see what the push actually carries, and "
        "tell the maintainer rather than working around the check."
    )


if __name__ == "__main__":
    try:
        main()
    except Exception:
        allow_quietly()
