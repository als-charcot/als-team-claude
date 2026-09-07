#!/usr/bin/env python3
"""Re-run an analysis under every defensible version of its arbitrary choices, and report
the WHOLE curve. Answers "what if we relaxed some of this?" without letting anyone cherry-pick.

    python relax.py --cmd "python analysis.py --min-visits {mv} --window {w} --outcome {o}" \
                    --grid mv=2,3,4 --grid w=12,18,24 --grid o=total,motor \
                    --extract "beta = (-?[0-9.]+)" --extract-p "p = ([0-9.eE+-]+)" \
                    --baseline mv=3,w=18,o=total

WHY THIS EXISTS. The constraint that destroys the most signal is usually not the p-value
threshold. It is an inclusion filter or an outcome definition adopted for convenience. A
cohort requiring ">= 3 visits over >= 90 days" is a defensible choice, and so are three other
choices, and nobody ever finds out whether the result depended on it.

WHAT IT REPORTS. Every specification, its effect, and where the original sits among them.
Plus the three numbers that decide whether you learned anything:

  direction agreement   the fraction of specifications pointing the same way
  sign flips            specifications that reverse the effect
  dependency            whether the conclusion survives the choices, or rests on one of them

THE ABUSE THIS REFUSES TO ENABLE. Running 40 specifications and quoting the one that reached
significance is the garden of forking paths, and it is the single easiest way to manufacture a
finding. So this tool:

  * always prints the FULL curve, never a filtered view;
  * marks the baseline specification so a reader can see if it was the outlier;
  * prints the fraction of significant specifications next to the chance expectation;
  * refuses to emit a "best" specification, and says so if asked.

A specification curve is evidence about ROBUSTNESS. It is never a way to select a result.
"""
from __future__ import annotations
import argparse, itertools, json, re, subprocess, sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass


def parse_grid(items: list[str]) -> dict[str, list[str]]:
    g = {}
    for it in items:
        if "=" not in it:
            raise SystemExit(f"--grid needs name=v1,v2,...  got {it!r}")
        k, vs = it.split("=", 1)
        vals = [v.strip() for v in vs.split(",") if v.strip()]
        if not vals:
            raise SystemExit(f"--grid {k} has no values")
        g[k.strip()] = vals
    return g


def run_one(cmd_tpl: str, combo: dict, rx, rx_p, rx_n, timeout: int):
    cmd = cmd_tpl
    for k, v in combo.items():
        cmd = cmd.replace("{" + k + "}", str(v))
    left = re.findall(r"\{(\w+)\}", cmd)
    if left:
        return dict(ok=False, err=f"unfilled placeholder(s): {left}", cmd=cmd)
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return dict(ok=False, err=f"timeout after {timeout}s", cmd=cmd)
    blob = (r.stdout or "") + (r.stderr or "")
    m = rx.search(blob)
    if not m:
        return dict(ok=False, err="effect pattern matched nothing", cmd=cmd,
                    exit=r.returncode, tail=blob[-300:])
    out = dict(ok=True, cmd=cmd, exit=r.returncode)
    try:
        out["effect"] = float(m.group(1))
    except ValueError:
        return dict(ok=False, err=f"effect {m.group(1)!r} is not a number", cmd=cmd)
    for name, pat in (("p", rx_p), ("n", rx_n)):
        if pat is not None:
            mm = pat.search(blob)
            if mm:
                try:
                    out[name] = float(mm.group(1))
                except ValueError:
                    pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cmd", required=True, help="command template with {placeholders}")
    ap.add_argument("--grid", action="append", required=True, metavar="NAME=V1,V2",
                    help="one per choice being relaxed; repeatable")
    ap.add_argument("--extract", required=True, help="regex with one group for the effect")
    ap.add_argument("--extract-p", help="regex with one group for the p-value")
    ap.add_argument("--extract-n", help="regex with one group for the analysable n")
    ap.add_argument("--baseline", help="the original choice, e.g. mv=3,w=18")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--timeout", type=int, default=1800)
    ap.add_argument("--max-specs", type=int, default=200)
    ap.add_argument("--json")
    a = ap.parse_args()

    grid = parse_grid(a.grid)
    rx = re.compile(a.extract)
    if rx.groups != 1:
        raise SystemExit("--extract must have exactly one capture group")
    rx_p = re.compile(a.extract_p) if a.extract_p else None
    rx_n = re.compile(a.extract_n) if a.extract_n else None
    for nm, r_ in (("--extract-p", rx_p), ("--extract-n", rx_n)):
        if r_ is not None and r_.groups != 1:
            raise SystemExit(f"{nm} must have exactly one capture group")

    keys = list(grid)
    combos = [dict(zip(keys, vals)) for vals in itertools.product(*(grid[k] for k in keys))]
    if len(combos) > a.max_specs:
        raise SystemExit(f"{len(combos)} specifications exceeds --max-specs {a.max_specs}. "
                         "Narrow the grid: an unbounded sweep is a fishing expedition, and a "
                         "curve nobody reads is not robustness evidence.")

    base = None
    if a.baseline:
        base = {k.strip(): v.strip() for k, v in
                (kv.split("=", 1) for kv in a.baseline.split(",") if "=" in kv)}
        unknown = [k for k in base if k not in grid]
        if unknown:
            raise SystemExit(f"--baseline names unknown choice(s): {unknown}")

    print(f"Relaxing {len(keys)} choice(s) over {len(combos)} specifications")
    for k in keys:
        print(f"  {k}: {', '.join(grid[k])}")
    print()

    results = []
    for i, c in enumerate(combos, 1):
        label = " ".join(f"{k}={c[k]}" for k in keys)
        print(f"  [{i:3d}/{len(combos)}] {label} ...", end=" ", flush=True)
        r = run_one(a.cmd, c, rx, rx_p, rx_n, a.timeout)
        r["combo"] = c
        r["label"] = label
        r["is_baseline"] = bool(base and all(str(c[k]) == str(v) for k, v in base.items()))
        results.append(r)
        print(f"{r['effect']:+.4g}" + (f"  p={r['p']:.3g}" if "p" in r else "")
              if r["ok"] else f"FAILED: {r['err']}")

    ok = [r for r in results if r["ok"]]
    failed = [r for r in results if not r["ok"]]
    if not ok:
        print("\nEvery specification failed. Nothing to report; fix the command or the "
              "extract pattern.")
        for r in failed[:3]:
            print(f"  {r['label']}: {r['err']}")
        return 1

    eff = sorted(r["effect"] for r in ok)
    pos = sum(1 for e in eff if e > 0)
    neg = sum(1 for e in eff if e < 0)
    agree = max(pos, neg) / len(eff)
    sig = [r for r in ok if "p" in r and r["p"] < a.alpha]
    med = eff[len(eff) // 2]
    bl = next((r for r in ok if r["is_baseline"]), None)

    print(f"\n  {'='*74}")
    print(f"  SPECIFICATION CURVE   {len(ok)} ran, {len(failed)} failed")
    print(f"  {'='*74}")
    print(f"  effect range          [{eff[0]:+.4g}, {eff[-1]:+.4g}]   median {med:+.4g}")
    print(f"  direction agreement   {agree:.0%}  ({pos} positive, {neg} negative"
          + (f", {len(eff)-pos-neg} exactly zero" if len(eff) - pos - neg else "") + ")")
    if any("p" in r for r in ok):
        withp = [r for r in ok if "p" in r]
        print(f"  reached alpha={a.alpha}      {len(sig)}/{len(withp)} specifications "
              f"({len(sig)/len(withp):.0%})")
    if bl:
        rank = sorted(eff).index(bl["effect"]) + 1
        print(f"  the original           {bl['effect']:+.4g}  "
              f"(rank {rank} of {len(eff)}; "
              f"{'an OUTLIER at the edge of the curve' if rank <= 2 or rank >= len(eff)-1 else 'inside the body of the curve'})")
    else:
        print("  the original           NOT MARKED. Pass --baseline so a reader can see whether\n"
              "                         the published number was typical or the extreme.")

    print(f"\n  {'-'*74}")
    print("  FULL CURVE (every specification, sorted; nothing hidden)")
    print(f"  {'-'*74}")
    for r in sorted(ok, key=lambda x: x["effect"]):
        mark = " <-- ORIGINAL" if r["is_baseline"] else ""
        star = "*" if ("p" in r and r["p"] < a.alpha) else " "
        print(f"   {star} {r['effect']:+10.4g}  "
              + (f"p={r['p']:<10.3g}" if "p" in r else " " * 13)
              + (f"n={int(r['n']):<7d}" if "n" in r else "")
              + f"  {r['label']}{mark}")
    if any("p" in r for r in ok):
        print(f"   (* = reached alpha {a.alpha})")

    if failed:
        print(f"\n  {len(failed)} specification(s) failed and are NOT in the curve above:")
        for r in failed:
            print(f"    {r['label']}: {r['err']}")
        print("  A curve with silent failures overstates robustness. Fix or explain each one.")

    # --- the interpretation, which is the part that stops the abuse ---
    print(f"\n  {'='*74}")
    if agree >= 0.95 and (not any("p" in r for r in ok) or len(sig) / max(1, len([r for r in ok if "p" in r])) >= 0.8):
        print("  ROBUST. The direction holds across essentially every defensible choice, so the\n"
              "  conclusion does not rest on the arbitrary ones. Report the curve alongside the\n"
              "  headline number.")
    elif agree >= 0.95:
        print("  DIRECTION ROBUST, MAGNITUDE CHOICE-DEPENDENT. Every specification points the\n"
              "  same way, but whether it clears the threshold depends on the choices. That is a\n"
              "  LEAD, not a finding: report the range, never a single specification.")
    elif agree >= 0.70:
        print("  CHOICE-DEPENDENT. A substantial minority of defensible specifications disagree.\n"
              "  The honest headline is the dependency itself: 'the result depends on how the\n"
              "  cohort is defined', which is a real finding about the data and should be\n"
              "  reported as one.")
    else:
        print("  NOT ROBUST. The specifications disagree about direction, so the original number\n"
              "  is a property of its choices rather than of the disease. Do not report the\n"
              "  original as a result. Report that the analysis is not identified by these data.")
    print("  There is no 'best' specification here, and this tool will not name one. Selecting\n"
          "  the specification that agrees with you is how false findings are made.")
    print(f"  {'='*74}\n")

    if a.json:
        Path(a.json).write_text(json.dumps(dict(
            grid=grid, alpha=a.alpha, n_specs=len(combos), n_ok=len(ok), n_failed=len(failed),
            direction_agreement=agree, effect_min=eff[0], effect_max=eff[-1], effect_median=med,
            baseline=(bl or {}).get("effect"), n_significant=len(sig),
            specifications=[{k: v for k, v in r.items() if k != "cmd"} for r in results],
        ), indent=2), encoding="utf-8")
        print(f"  machine-readable curve: {a.json}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
