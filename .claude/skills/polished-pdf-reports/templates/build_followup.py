"""Render a Markdown follow-up report to a polished PDF using report_pdf_lib.

Use this template when you've already shipped a primary report (REPORT.pdf
via build_report.py) and have new findings worth a separate ~6-page brief
rather than amending the original. See references/followup_reports.md for
when to follow up vs amend.

Copy this into your project's scripts/reports/ folder alongside the
existing build_report.py. The renderer library (report_pdf_lib.py) is
shared between the two builds.

Usage:
    python build_followup.py

Output:
    reports/<PROJECT>_FOLLOWUP.pdf
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "reports"))
from report_pdf_lib import build_report

REPORTS = ROOT / "reports"


# ─────────────────────────────────────────────────────────────────────────────
# EDIT THESE ↓
# ─────────────────────────────────────────────────────────────────────────────

MD_PATH = REPORTS / "FOLLOWUP.md"               # or e.g. PROACT_FOLLOWUP.md
PDF_PATH = REPORTS / "FOLLOWUP.pdf"

TITLE = "Project name — follow-up: <one-line label of what triggered the follow-up>"
SUBTITLE = "Short follow-up to the <ORIGINAL-DATE> review: what was gained, what was lost."
FOOTER_LABEL = "Project follow-up — <one-line trigger>"

COVER_META = [
    "From: <team name>",
    "Date: <YYYY-MM-DD>",
    "Pipeline: <project>/scripts/<NN_new_script>.py  (~X min, workstation)",
    "Data source: <path or release name>",
    "Read after: <ORIGINAL-REPORT-FILENAME>.pdf (<original date>, the primary review)",
]

# ─────────────────────────────────────────────────────────────────────────────
# EDIT THESE ↑
# ─────────────────────────────────────────────────────────────────────────────


def main() -> int:
    build_report(
        md_path=MD_PATH,
        pdf_path=PDF_PATH,
        title=TITLE,
        subtitle=SUBTITLE,
        footer_label=FOOTER_LABEL,
        cover_meta=COVER_META,
    )
    sz = PDF_PATH.stat().st_size / 1024
    print(f"[OK] {PDF_PATH.name} ({sz:.0f} KB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
