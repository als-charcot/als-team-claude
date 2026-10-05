#!/usr/bin/env python3
"""PreToolUse hook: convert a document to markdown before Claude reads it.

Wired to the Read tool in `.claude/settings.json`. When Claude is about to read a PDF, Word,
PowerPoint or Excel file, this converts it to markdown with MarkItDown and rewrites the path
so the read lands on the markdown instead. Nobody asks for it and nobody runs it.

WHY. A PDF page reaches the model twice, once as extracted text and once as a picture of the
page, which Anthropic's own documentation puts at 1,500 to 3,000 tokens per page. The
markdown is the text half on its own. On a thirty page paper that is the difference between
filling a conversation and barely denting it.

WHY IT IS A HOOK AND NOT A SKILL. A skill is offered to the model, which may or may not take
it. A hook runs every time. The repo already learned this the hard way: a guard that depends
on somebody remembering is a wish, not a guard.

IT FAILS OPEN, DELIBERATELY. If MarkItDown is missing, or the file is encrypted, or the
conversion produces nothing useful, this prints nothing and the original read proceeds
exactly as it would have. A researcher mid-analysis must never be blocked by a speed
optimisation. The only cost of failing open is the tokens we were trying to save.

Reads the hook payload on stdin, prints hook JSON on stdout. Stdlib only.
"""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / ".converted"
HANDLED = {".pdf", ".docx", ".pptx", ".xlsx", ".doc", ".ppt", ".xls"}

# Below this many characters the conversion is treated as having failed. A scanned PDF with
# no text layer converts "successfully" to almost nothing, and handing Claude an empty file
# is worse than handing it the original: it looks like the paper said nothing.
MIN_USEFUL_CHARS = 200


def nothing() -> None:
    """Say nothing, so the read proceeds untouched."""
    sys.exit(0)


def cache_path(src: Path) -> Path:
    """Keyed on the full path and the file's mtime+size, so editing a document reconverts it
    without anyone having to clear a cache."""
    st = src.stat()
    key = f"{src.resolve()}|{st.st_mtime_ns}|{st.st_size}"
    digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:16]
    return CACHE / f"{src.stem[:40]}-{digest}.md"


def convert(src: Path, dst: Path) -> bool:
    dst.parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run([sys.executable, "-m", "markitdown", str(src)],
                           capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
    except Exception:
        return False
    if r.returncode != 0 or not r.stdout or len(r.stdout.strip()) < MIN_USEFUL_CHARS:
        return False
    header = (f"<!-- Converted from {src.name} by scripts/convert_for_read.py. "
              f"The original is unchanged at {src}. -->\n\n")
    try:
        dst.write_text(header + r.stdout, encoding="utf-8")
    except Exception:
        return False
    return True


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        nothing()

    tool_input = payload.get("tool_input") or {}
    raw = tool_input.get("file_path")
    if not raw:
        nothing()

    src = Path(raw)
    if src.suffix.lower() not in HANDLED:
        nothing()
    if not src.is_file():
        nothing()  # let Read produce its own, clearer, not-found error

    dst = cache_path(src)
    if not dst.exists() and not convert(src, dst):
        nothing()

    pages = dst.read_text(encoding="utf-8", errors="replace").count("\n") // 50 + 1
    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": {**tool_input, "file_path": str(dst)},
        },
        "systemMessage": (f"Read {src.name} as markdown instead of the original "
                          f"(about {pages} page{'s' if pages != 1 else ''} of text). "
                          f"The original file is untouched."),
        "suppressOutput": True,
    }))


if __name__ == "__main__":
    main()
