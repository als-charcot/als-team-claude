#!/usr/bin/env python3
"""Tie every number typed in a report to a value the analysis script actually computed.

    python claim_audit.py claims.json [--root DIR] [-v]

A report that quotes numbers a script also produces will drift from it. The figures
regenerate on every run; the sentences beside them do not. Nothing errors, the script still
runs, and the defect exists only in the report.

This is the standing gate. Each claim declares WHERE the number is written, HOW to find it
(a regex with exactly one capture group), and WHAT it should equal (a path into the script's
own JSON or CSV output).

TWO PROPERTIES MAKE IT WORK, AND BOTH ARE EASY TO LOSE:

  A PATTERN THAT MATCHES NOTHING IS A FAILURE, NOT A PASS. Otherwise the check silently
  stops running the moment somebody rewords a sentence, which is exactly when it is needed.

  NAMES ARE CHECKED TOO. A report that names the wrong subgroups is worse than one that
  miscounts them, and a set check catches what a number check cannot.

CONFIG
------
{
  "sources":   {"stats": "outputs/summary.json", "table": "outputs/cohort.csv"},
  "documents": {"report": "outputs/report.md", "readme": "README.md"},
  "claims": [
    {"doc": "report", "kind": "number",
     "pattern": "n = ([0-9,]+) subjects with a fittable slope",
     "source": "stats", "path": "cohort.n_with_slope", "tol": 0},

    {"doc": "report", "kind": "number",
     "pattern": "Cohen's d = (-?[0-9.]+)",
     "source": "stats", "path": "bulbar_vs_limb.cohens_d", "tol": 0.005},

    {"doc": "report", "kind": "set",
     "pattern": "onset groups compared: ([A-Za-z, ]+)",
     "source": "stats", "path": "bulbar_vs_limb.groups", "sep": ","}
  ]
}

`path` walks JSON with dots, and supports `col:NAME` on a CSV source to collect a column.
Exit code is non-zero if any claim fails, so this can gate a share.
"""
from __future__ import annotations
import argparse, csv, json, re, sys
from pathlib import Path


def load_source(p: Path):
    if p.suffix.lower() == ".json":
        return json.loads(p.read_text(encoding="utf-8"))
    if p.suffix.lower() in (".csv", ".tsv"):
        d = "\t" if p.suffix.lower() == ".tsv" else ","
        with p.open(encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f, delimiter=d))
    raise ValueError(f"unsupported source type: {p}")


def walk(obj, path: str):
    """Dotted path into JSON, or 'col:NAME' to collect a CSV column."""
    if path.startswith("col:"):
        name = path[4:]
        if not isinstance(obj, list):
            raise KeyError("col: requires a CSV source")
        if obj and name not in obj[0]:
            raise KeyError(f"no column {name!r}; have {list(obj[0])}")
        return [r[name] for r in obj]
    cur = obj
    for part in path.split("."):
        if isinstance(cur, list):
            cur = cur[int(part)]
        else:
            if part not in cur:
                raise KeyError(f"{path!r}: no key {part!r}; have {list(cur)[:12]}")
            cur = cur[part]
    return cur


def as_number(x):
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x).strip().replace(",", "").replace("−", "-").replace("%", "")
    # prose punctuation often ends up inside a greedy capture group ("d = -0.55.")
    s = s.rstrip(".,;:)]}")
    return float(s)


def norm_set(vals, sep=","):
    if isinstance(vals, str):
        vals = vals.split(sep)
    return sorted({str(v).strip().lower() for v in vals if str(v).strip()})


def main() -> int:
    ap = argparse.ArgumentParser(description="Audit typed claims against pipeline output.")
    ap.add_argument("config")
    ap.add_argument("--root", default=".", help="paths in the config are relative to this")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args()

    root = Path(a.root).resolve()
    cfg = json.loads(Path(a.config).read_text(encoding="utf-8"))

    sources, docs, problems = {}, {}, []
    for k, rel in cfg.get("sources", {}).items():
        p = root / rel
        if not p.exists():
            problems.append(f"SOURCE MISSING  {k} -> {rel}")
        else:
            try:
                sources[k] = load_source(p)
            except Exception as e:
                problems.append(f"SOURCE UNREADABLE  {k} -> {rel}: {e}")
    for k, rel in cfg.get("documents", {}).items():
        p = root / rel
        if not p.exists():
            problems.append(f"DOCUMENT MISSING  {k} -> {rel}")
        else:
            docs[k] = p.read_text(encoding="utf-8", errors="replace")

    checked = passed = 0
    for i, c in enumerate(cfg.get("claims", []), 1):
        tag = f"claim {i} [{c.get('doc','?')}] {c.get('pattern','')[:52]}"
        doc = docs.get(c.get("doc"))
        if doc is None:
            problems.append(f"{tag}\n    document not loaded")
            continue
        try:
            rx = re.compile(c["pattern"])
        except re.error as e:
            problems.append(f"{tag}\n    bad regex: {e}")
            continue
        if rx.groups != 1:
            problems.append(f"{tag}\n    pattern must have exactly one capture group, has {rx.groups}")
            continue

        matches = rx.findall(doc)
        checked += 1
        # A pattern that matches nothing is a FAILURE, not a pass.
        if not matches:
            problems.append(f"{tag}\n    PATTERN MATCHED NOTHING. The prose was reworded, or "
                            f"the claim was removed. Re-point the pattern or drop the claim.")
            continue
        if len(set(matches)) > 1:
            problems.append(f"{tag}\n    the same claim is stated inconsistently in one document: {sorted(set(matches))}")
            continue
        found = matches[0]

        if c.get("source") not in sources:
            problems.append(f"{tag}\n    source {c.get('source')!r} not loaded")
            continue
        try:
            expect = walk(sources[c["source"]], c["path"])
        except Exception as e:
            problems.append(f"{tag}\n    cannot resolve path {c.get('path')!r}: {e}")
            continue

        kind = c.get("kind", "number")
        try:
            if kind == "number":
                got, want = as_number(found), as_number(expect)
                tol = float(c.get("tol", 0))
                ok = abs(got - want) <= tol
                detail = f"report says {got:g}, pipeline says {want:g} (tol {tol:g})"
            elif kind == "set":
                sep = c.get("sep", ",")
                got, want = norm_set(found, sep), norm_set(expect, sep)
                ok = got == want
                missing = [x for x in want if x not in got]
                extra = [x for x in got if x not in want]
                detail = f"missing {missing}, unexpected {extra}" if not ok else "sets match"
            elif kind == "text":
                ok = str(found).strip() == str(expect).strip()
                detail = f"report says {found!r}, pipeline says {expect!r}"
            else:
                problems.append(f"{tag}\n    unknown kind {kind!r}")
                continue
        except Exception as e:
            problems.append(f"{tag}\n    comparison failed: {e}")
            continue

        if ok:
            passed += 1
            if a.verbose:
                print(f"  ok    {tag}\n          {detail}")
        else:
            problems.append(f"{tag}\n    DRIFTED: {detail}")

    print(f"\nclaim audit: {passed}/{checked} claims verified against the pipeline")
    if problems:
        print(f"\n{len(problems)} problem(s):\n")
        for p in problems:
            print(f"  FAIL  {p}\n")
        print("Fix the SCRIPT and re-derive, never the sentence.")
        return 1
    if checked == 0:
        print("\nNo claims were checked. An empty audit is not a pass.")
        return 1
    print("Every typed number is tied to a value the pipeline computes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
