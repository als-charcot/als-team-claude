#!/usr/bin/env python3
"""Maintainer check: is what we think we shipped actually in the repository?

    python scripts/check_repo_integrity.py

WHY THIS EXISTS. Adding `research-watch/` to `.gitignore`, to keep generated digests local,
also matched `.claude/skills/research-watch/`. `git add -A .claude` then skipped the entire
skill without a word, `git commit` succeeded, and the push looked complete. Researchers would
have pulled a `/research-watch` slash command pointing at a skill that was not there.

`git add` does not error on ignored paths. Nothing failed. That is the point: this is a check
for the class of defect that produces no error, which is the same class the team's own
adversarial-review catalogue is built around.

Exit code is non-zero if anything is wrong, so this can gate a push.
"""
from __future__ import annotations
import os, re, subprocess, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / ".claude" / "skills"
COMMANDS = ROOT / ".claude" / "commands"


def git(*a) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *a],
                          capture_output=True, text=True).stdout


def tracked() -> set[str]:
    return {p.replace("\\", "/") for p in git("ls-files").splitlines() if p}


def main() -> int:
    problems: list[str] = []
    notes: list[str] = []
    files = tracked()

    # 1. Every skill on disk must have its SKILL.md tracked.
    on_disk = sorted(d.name for d in SKILLS.iterdir()
                     if d.is_dir() and (d / "SKILL.md").exists()) if SKILLS.exists() else []
    untracked = [n for n in on_disk
                 if f".claude/skills/{n}/SKILL.md" not in files]
    for n in untracked:
        problems.append(f"skill '{n}' exists on disk but its SKILL.md is NOT tracked in git. "
                        f"Most likely a .gitignore pattern matches it "
                        f"(check: git check-ignore -v .claude/skills/{n}/SKILL.md)")

    # 2. Nothing under .claude/ may be ignored. That directory is the whole product.
    ignored = [p for p in git("ls-files", "--others", "--ignored",
                              "--exclude-standard", ".claude/").splitlines() if p]
    for p in ignored:
        problems.append(f"'{p}' is under .claude/ but is IGNORED by .gitignore. "
                        f"Everything under .claude/ must reach the researchers.")

    # 3. Every skill referenced by a slash command must exist and be tracked.
    if COMMANDS.exists():
        for c in sorted(COMMANDS.glob("*.md")):
            refs = set(re.findall(r"\.claude/skills/[A-Za-z0-9_.-]+/SKILL\.md",
                                  c.read_text(encoding="utf-8", errors="replace")))
            if not refs:
                notes.append(f"/{c.stem} names no skill path explicitly (may be self-contained)")
                continue
            for r in sorted(refs):
                if not (ROOT / r).exists():
                    problems.append(f"/{c.stem} points at '{r}', which does not exist on disk")
                elif r not in files:
                    problems.append(f"/{c.stem} points at '{r}', which exists but is NOT tracked")

    # 4. Every skill directory's own scripts/ and references/ must be tracked too. A skill
    #    whose SKILL.md shipped but whose scripts did not is broken in a subtler way.
    for n in on_disk:
        d = SKILLS / n
        for sub in ("scripts", "references", "templates"):
            p = d / sub
            if not p.is_dir():
                continue
            for f in p.rglob("*"):
                if f.is_file():
                    rel = f.relative_to(ROOT).as_posix()
                    if rel not in files:
                        problems.append(f"'{rel}' is part of skill '{n}' but is NOT tracked")

    # 5. Slash commands themselves must be tracked.
    if COMMANDS.exists():
        for c in sorted(COMMANDS.glob("*.md")):
            rel = c.relative_to(ROOT).as_posix()
            if rel not in files:
                problems.append(f"'{rel}' is not tracked, so /{c.stem} will not reach anyone")

    print(f"repo integrity check: {len(on_disk)} skills on disk, "
          f"{len(list(COMMANDS.glob('*.md'))) if COMMANDS.exists() else 0} slash commands")
    for n in notes:
        print(f"  note  {n}")
    if problems:
        print(f"\n{len(problems)} problem(s):\n")
        for p in problems:
            print(f"  FAIL  {p}\n")
        return 1
    print("Everything on disk that should reach the researchers is tracked in git.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
