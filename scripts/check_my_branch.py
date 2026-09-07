#!/usr/bin/env python3
"""Am I on my own branch, with an identity, pointing at somewhere real?

Runs automatically at the start of every Claude Code session (see .claude/settings.json).
Says nothing when everything is fine, so it is silent almost always. When something IS wrong
it prints exactly what to do about it.

WHY THIS IS A SCRIPT AND NOT A PARAGRAPH IN SETUP.MD. There are four ways to end up
somewhere wrong, and all four look normal from the outside:

  * sitting on main or develop, where nothing you write can ever be pushed;
  * on a branch created locally with `checkout -b`, which tracks nothing, so the first push
    goes nowhere useful;
  * on a branch whose remote counterpart was renamed or removed, where `git pull` fails and
    `git push` would recreate a retired name for the whole team;
  * with no repo-local identity, so commits are attributed to whatever the machine's global
    git config happens to say, which is often an unrelated work account.

Exit code is always 0. This informs, it never blocks: a researcher mid-analysis should not be
stopped by a branch warning.
"""
from __future__ import annotations
import subprocess, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent


def git(*a) -> str:
    try:
        r = subprocess.run(["git", "-C", str(ROOT), *a],
                           capture_output=True, text=True, timeout=20)
        return (r.stdout or "").strip()
    except Exception:
        return ""


def main() -> int:
    if not (ROOT / ".git").exists():
        return 0                                  # a ZIP download; nothing to check

    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if not branch:
        return 0

    problems: list[str] = []
    fixes: list[str] = []

    # 1. On a protected branch. Nothing written here can ever be shared.
    if branch in ("main", "develop"):
        remotes = [l.split()[0].replace("origin/", "")
                   for l in git("branch", "-r", "--list", "origin/researchers/*").splitlines()
                   if l.strip()]
        problems.append(f"You are on '{branch}', which is protected. Work committed here "
                        f"cannot be pushed, and the push will be rejected.")
        if remotes:
            fixes.append("Check out your own branch. The ones that exist are:\n      "
                         + "\n      ".join(sorted(remotes))
                         + "\n    Use a plain checkout so tracking is set up automatically:\n"
                         + f"      git checkout {sorted(remotes)[0]}")
        else:
            fixes.append("Ask the maintainer (Emmanuel) which branch is yours.")

    elif not branch.startswith("researchers/"):
        problems.append(f"Branch '{branch}' is not a researcher branch. Shared work is only "
                        f"ever pushed to 'researchers/<your-github-username>'.")
        fixes.append("Switch to your own branch, or ask the maintainer to create it.")

    # 2. Upstream missing or gone.
    # Read the upstream from config, not from rev-parse @{u}: once the remote branch is
    # gone, rev-parse fails and hands back the literal "@{u}", which then gets printed at
    # the researcher as if it were a branch name.
    up_remote = git("config", f"branch.{branch}.remote")
    up_merge = git("config", f"branch.{branch}.merge").replace("refs/heads/", "")
    upstream = f"{up_remote}/{up_merge}" if (up_remote and up_merge) else ""

    if branch.startswith("researchers/"):
        if not upstream:
            problems.append(f"Branch '{branch}' tracks nothing. It was probably created "
                            f"locally with 'checkout -b' instead of checked out from the "
                            f"remote, so 'git pull' will fail and a push may go nowhere useful.")
            fixes.append("git fetch origin --prune\n"
                         f"    git branch --set-upstream-to=origin/{branch}\n"
                         "    If that says the upstream does not exist, the branch is not on "
                         "the remote at all - stop and ask the maintainer rather than creating it.")
        else:
            tracked = git("for-each-ref", "--format=%(upstream:track)",
                          f"refs/heads/{branch}")
            if "gone" in tracked:
                problems.append(f"Branch '{branch}' tracks '{upstream}', which no longer "
                                f"exists on the remote. It was renamed or removed. "
                                f"'git pull' will fail, and a push would RECREATE the "
                                f"retired name for the whole team.")
                fixes.append("git fetch origin --prune\n"
                             "    then rename to the name that does exist and repoint:\n"
                             "      git branch -m <old> researchers/<your-github-username>\n"
                             "      git branch --set-upstream-to=origin/researchers/<your-github-username>\n"
                             "    Never run a 'git push origin HEAD:<old-name>' suggestion; "
                             "that is what resurrects the retired branch.")
            elif upstream.replace("origin/", "") != branch:
                problems.append(f"Branch '{branch}' tracks '{upstream}', which is a DIFFERENT "
                                f"name. A push could write to the wrong branch.")
                fixes.append(f"git branch --set-upstream-to=origin/{branch}")

    # 3. Identity not persisted in this clone.
    name = git("config", "--local", "user.name")
    email = git("config", "--local", "user.email")
    if not name or not email:
        missing = " and ".join(x for x, v in (("user.name", name), ("user.email", email)) if not v)
        problems.append(f"This clone has no repo-local {missing}. Commits would be attributed "
                        f"to the machine's global git identity, which is often an unrelated "
                        f"work account, and the commit would not be linked to the right "
                        f"GitHub user.")
        fixes.append('git config --local user.name "<your name>"\n'
                     '    git config --local user.email "<the email you use on GitHub>"')

    if not problems:
        return 0

    print("\n" + "=" * 78)
    print("  BRANCH / IDENTITY CHECK - something needs fixing before you share work")
    print("=" * 78)
    for i, (p, f) in enumerate(zip(problems, fixes + [""] * len(problems)), 1):
        print(f"\n  {i}. {p}")
        if f:
            print(f"\n     Fix:\n      {f}")
    print("\n" + "=" * 78)
    print("  Claude: resolve this with the researcher before any commit or push. Do not")
    print("  work around it by pushing to a different branch than the one that is theirs.")
    print("=" * 78 + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
