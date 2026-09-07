#!/usr/bin/env python3
"""Negative control: break the link the finding depends on, and confirm the effect collapses.

An effect that survives having its own exposure shuffled is measuring the pipeline, not the
disease. This runs that test two ways.

MODE 1 -- permute a column, in-process (fast, no re-run of your script)

    python mutation_check.py permute --csv cohort.csv \
        --outcome alsfrs_slope --exposure fvc_baseline --n 1000

  Computes the observed association, then recomputes it with the exposure shuffled N times.
  Reports where the observed value sits in the permutation distribution. A real effect sits
  outside it; an artefact sits inside.

  Categorical exposure (e.g. onset site) is detected automatically and compared by group
  difference in means; numeric exposure uses Pearson r.

MODE 2 -- permute, then re-run YOUR script and re-extract the number (slower, stronger)

    python mutation_check.py rerun --csv cohort.csv --exposure fvc_baseline \
        --cmd "python analysis.py --input {csv}" \
        --extract "r = (-?[0-9.]+)" --n 20

  Writes a shuffled copy of the CSV, runs your command against it, and pulls the effect out
  of stdout with a regex. This tests the whole pipeline, including any leakage your in-process
  calculation would not see.

Both modes exit non-zero if the observed effect is NOT clearly separated from the null,
so this can gate a share.
"""
from __future__ import annotations
import argparse, csv, os, random, re, statistics as st, subprocess, sys, tempfile
from pathlib import Path


def read_csv(p: Path):
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def numeric(rows, col):
    out = []
    for r in rows:
        v = (r.get(col) or "").strip()
        if v in ("", "NA", "NaN", "None"):
            out.append(None)
        else:
            try:
                out.append(float(v))
            except ValueError:
                return None          # not a numeric column
    return out


def pearson(xs, ys):
    pairs = [(x, y) for x, y in zip(xs, ys) if x is not None and y is not None]
    if len(pairs) < 3:
        return None
    xs2 = [p[0] for p in pairs]; ys2 = [p[1] for p in pairs]
    mx, my = st.fmean(xs2), st.fmean(ys2)
    num = sum((x - mx) * (y - my) for x, y in pairs)
    dx = sum((x - mx) ** 2 for x in xs2) ** .5
    dy = sum((y - my) ** 2 for y in ys2) ** .5
    return None if dx == 0 or dy == 0 else num / (dx * dy)


def group_diff(labels, ys):
    """Difference in mean outcome between the two largest label groups."""
    buckets: dict[str, list[float]] = {}
    for lab, y in zip(labels, ys):
        if y is None or lab is None or str(lab).strip() == "":
            continue
        buckets.setdefault(str(lab).strip(), []).append(y)
    big = sorted(buckets.items(), key=lambda kv: -len(kv[1]))[:2]
    if len(big) < 2 or min(len(v) for _, v in big) < 3:
        return None
    return st.fmean(big[0][1]) - st.fmean(big[1][1]), big[0][0], big[1][0]


def summarise(observed, null, label, alpha=0.05):
    null = [v for v in null if v is not None]
    if observed is None or len(null) < 10:
        print("  could not compute a usable effect or null distribution")
        return 1
    extreme = sum(1 for v in null if abs(v) >= abs(observed))
    p = (extreme + 1) / (len(null) + 1)
    lo = min(null); hi = max(null)
    print(f"\n  observed {label}: {observed:+.4f}")
    print(f"  null from {len(null)} permutations: mean {st.fmean(null):+.4f}, "
          f"range [{lo:+.4f}, {hi:+.4f}]")
    print(f"  permutations at least as extreme: {extreme}  ->  p = {p:.4f}")
    if p <= alpha and abs(observed) > abs(hi if observed > 0 else lo) * 0.99:
        print("\n  PASS  the effect is outside the null. Breaking the link destroyed it,")
        print("        which is what a real association should do.")
        return 0
    if p <= alpha:
        print("\n  PASS (marginal)  the effect is separated from the null, but some")
        print("        permutations came close. Report the permutation p alongside the effect.")
        return 0
    print("\n  FAIL  the effect survives shuffling. It is a property of the pipeline or the")
    print("        cohort construction, not of the exposure. Do not share this finding.")
    return 1


def mode_permute(a) -> int:
    rows = read_csv(Path(a.csv))
    ys = numeric(rows, a.outcome)
    if ys is None:
        print(f"outcome {a.outcome!r} is not numeric"); return 1
    xs_num = numeric(rows, a.exposure)
    rnd = random.Random(a.seed)

    if xs_num is not None:
        obs = pearson(xs_num, ys)
        pool = [v for v in xs_num]
        null = []
        for _ in range(a.n):
            rnd.shuffle(pool)
            null.append(pearson(pool, ys))
        print(f"exposure {a.exposure!r} is numeric -> Pearson r vs {a.outcome!r}")
        return summarise(obs, null, "r")

    labels = [(r.get(a.exposure) or "").strip() for r in rows]
    g = group_diff(labels, ys)
    if g is None:
        print(f"could not form two comparable groups from {a.exposure!r}"); return 1
    obs, g1, g2 = g
    print(f"exposure {a.exposure!r} is categorical -> mean {a.outcome} difference, {g1} minus {g2}")
    pool = list(labels); null = []
    for _ in range(a.n):
        rnd.shuffle(pool)
        r = group_diff(pool, ys)
        null.append(r[0] if r else None)
    return summarise(obs, null, "difference")


def run_and_extract(cmd: str, csv_path: Path, rx: re.Pattern):
    filled = cmd.replace("{csv}", str(csv_path))
    try:
        out = subprocess.run(filled, shell=True, capture_output=True, text=True, timeout=1800)
    except subprocess.TimeoutExpired:
        return None
    blob = (out.stdout or "") + (out.stderr or "")
    m = rx.search(blob)
    return float(m.group(1)) if m else None


def mode_rerun(a) -> int:
    src = Path(a.csv); rows = read_csv(src)
    rx = re.compile(a.extract)
    if rx.groups != 1:
        print("--extract must have exactly one capture group"); return 1
    print(f"baseline run: {a.cmd}")
    obs = run_and_extract(a.cmd, src, rx)
    if obs is None:
        print("  could not extract the effect from the baseline run. Check --extract."); return 1
    print(f"  observed effect: {obs:+.4f}")

    rnd = random.Random(a.seed)
    col = [r.get(a.exposure) for r in rows]
    fields = list(rows[0].keys())
    null = []
    tmp = Path(tempfile.mkdtemp(prefix="mutcheck_"))
    for i in range(a.n):
        rnd.shuffle(col)
        for r, v in zip(rows, col):
            r[a.exposure] = v
        p = tmp / f"shuffled_{i}.csv"
        with p.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields); w.writeheader(); w.writerows(rows)
        v = run_and_extract(a.cmd, p, rx)
        null.append(v)
        print(f"  permutation {i+1}/{a.n}: {'n/a' if v is None else f'{v:+.4f}'}")
        try: os.unlink(p)
        except OSError: pass
    return summarise(obs, null, "effect")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="mode", required=True)

    p1 = sub.add_parser("permute", help="in-process permutation test")
    p1.add_argument("--csv", required=True)
    p1.add_argument("--outcome", required=True)
    p1.add_argument("--exposure", required=True)
    p1.add_argument("--n", type=int, default=1000)
    p1.add_argument("--seed", type=int, default=7)

    p2 = sub.add_parser("rerun", help="permute, re-run your script, re-extract the number")
    p2.add_argument("--csv", required=True)
    p2.add_argument("--exposure", required=True)
    p2.add_argument("--cmd", required=True, help="use {csv} where the input path goes")
    p2.add_argument("--extract", required=True, help="regex with one capture group")
    p2.add_argument("--n", type=int, default=20)
    p2.add_argument("--seed", type=int, default=7)

    a = ap.parse_args()
    return mode_permute(a) if a.mode == "permute" else mode_rerun(a)


if __name__ == "__main__":
    sys.exit(main())
