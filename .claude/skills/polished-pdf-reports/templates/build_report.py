"""Render a Markdown report to a polished PDF using report_pdf_lib.

Copy this file into your project's scripts/reports/ folder and edit the
constants at the bottom. The renderer library (report_pdf_lib.py) should
sit alongside this script.

Usage:
    python build_report.py

Output:
    reports/REPORT.pdf   (whatever path you set for PDF_PATH)
"""
from __future__ import annotations

import sys
from pathlib import Path

# scripts/reports/build_report.py  →  project root is two levels up
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts" / "reports"))
from report_pdf_lib import build_report

REPORTS = ROOT / "reports"


# ─────────────────────────────────────────────────────────────────────────────
# EDIT THESE ↓
# ─────────────────────────────────────────────────────────────────────────────

MD_PATH = REPORTS / "REPORT.md"
PDF_PATH = REPORTS / "REPORT.pdf"

TITLE = "Project name — consolidated report"
SUBTITLE = "One-line summary of headline finding and current status"
FOOTER_LABEL = "Project name — consolidated report"

# 4–6 short lines. Each becomes a small line under the cover banner.
COVER_META = [
    "Single consolidated report (~10-12 pages)",
    "Headline: <one-line numerical takeaway>",
    "Status: <green / amber / red label>",
    "Reproducibility: <how to run end-to-end>",
    "Open questions for external review at end of report",
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
