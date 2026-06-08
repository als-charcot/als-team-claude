"""Rasterize each page of a polished PDF report at 110 DPI for visual review.

Use as the verification step in the polished-pdf-reports iteration loop.
After rendering REPORT.pdf, run this script — it writes one PNG per page
into reports/_preview/. Then read each page in Claude / your viewer and
look for:

  - Single-callout orphan pages
  - Stranded BOX cards alone with blank space
  - Tables split across pages
  - Headings orphaned at page bottom
  - Findings overflowing onto a second page

Usage:
    python verify_layout.py reports/REPORT.pdf
    python verify_layout.py reports/REPORT.pdf --dpi 150 --out reports/_preview/
"""
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

try:
    import fitz  # PyMuPDF
except ImportError:
    print("PyMuPDF (fitz) is required. Install with: pip install pymupdf", file=sys.stderr)
    raise


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("pdf", type=Path, help="Path to the rendered PDF")
    ap.add_argument("--out", type=Path, default=None,
                    help="Output folder for page PNGs (default: <pdf-dir>/_preview)")
    ap.add_argument("--dpi", type=int, default=110,
                    help="Render DPI (default: 110, good balance of legibility & speed)")
    ap.add_argument("--clean", action="store_true",
                    help="Delete and recreate the preview folder before rendering")
    args = ap.parse_args()

    if not args.pdf.exists():
        print(f"PDF not found: {args.pdf}", file=sys.stderr)
        return 2

    out = args.out or (args.pdf.parent / "_preview")
    if args.clean and out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True, exist_ok=True)

    # If not cleaning, still wipe any stale page_NN.png so deleted pages don't linger
    for p in out.glob("page_*.png"):
        p.unlink()

    doc = fitz.open(args.pdf)
    n = len(doc)
    print(f"Rendering {n} pages at {args.dpi} DPI to {out}/")
    for i, page in enumerate(doc):
        pix = page.get_pixmap(dpi=args.dpi)
        target = out / f"page_{i+1:02d}.png"
        pix.save(str(target))
    print(f"Done. {n} PNGs in {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
