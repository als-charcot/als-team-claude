#!/usr/bin/env python3
"""Turn "p > 0.05, no association" into a statement about what the data could actually see.

    python precision_report.py --estimate -0.08 --se 0.061 --outcome alsfrs_slope
    python precision_report.py --estimate 0.91 --ci 0.74 1.12 --outcome survival_hr
    python precision_report.py --list-thresholds

WHY THIS EXISTS. In a cohort this size most non-significant results are not evidence of
absence. They are intervals wide enough to still contain an effect as large as every approved
ALS drug. Reporting only "p = 0.63, no association" discards the one thing that separates a
closed door from an open one: how much of the clinically important effect space the data
actually ruled out.

So for every null this reports three numbers, and refuses to report any of them without the
third input a human has to supply:

  MDE   the smallest effect this analysis could have detected (from the REALIZED standard
        error, two-sided alpha, stated power). Not retrospective power, which is circular.
  R     the compatibility ratio: the largest effect still compatible with the data, divided
        by the effect we said we would not want to miss. R >= 1 means a clinically important
        effect is still on the table.
  TOST  two one-sided tests against +/- delta_star. Only this can license the phrase
        "adequately powered null" -- i.e. a genuine CLOSED DOOR.

TWO VERDICTS, AND THEY ARE NOT THE SAME KIND OF THING:

  CLOSED DOOR   MDE < delta_star and TOST rejects. An informative null. This IS a finding,
                and goes through the normal adversarial review.
  INCONCLUSIVE  the effect space was never explored. NOT a finding and NOT evidence of
                anything. It is a routing decision about where to spend the next n.

WHAT THIS TOOL WILL NOT DO. It never says an effect exists, is likely, or is probable. Its
whole vocabulary is "not excluded", "could not have been detected", "would need n = X to
resolve". A wide interval is never converted into a direction, a probability or a mechanism.

delta_star must come from references/effect_thresholds.md and must carry a citation. If the
threshold is unconfirmed, this exits non-zero and prints nothing usable. That is deliberate:
a margin invented after seeing the data is not a margin.
"""
from __future__ import annotations
import argparse, json, math, os, re, sys
from pathlib import Path
from statistics import NormalDist

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

ND = NormalDist()
ROOT = Path(__file__).resolve().parent.parent
THRESHOLDS = ROOT / "references" / "effect_thresholds.md"


def load_thresholds() -> dict:
    """Parse the margin registry. A row is usable only if it has a citation and is CONFIRMED."""
    if not THRESHOLDS.exists():
        return {}
    out = {}
    for ln in THRESHOLDS.read_text(encoding="utf-8", errors="replace").splitlines():
        if not ln.strip().startswith("|"):
            continue
        c = [x.strip() for x in ln.strip().strip("|").split("|")]
        if len(c) < 6 or c[0].lower() in ("key", "---", ":---"):
            continue
        if set(c[0]) <= set("-: "):
            continue
        key, scale, delta, direction, status, citation = c[0], c[1], c[2], c[3], c[4], c[5]
        try:
            dv = float(re.sub(r"[^0-9.\-]", "", delta))
        except ValueError:
            continue
        out[key] = dict(scale=scale, delta_star=abs(dv), direction=direction,
                        status=status.upper(), citation=citation)
    return out


def mde(se: float, alpha: float, power: float) -> float:
    """Smallest true effect detectable with the given power, at the REALIZED precision."""
    return (ND.inv_cdf(1 - alpha / 2) + ND.inv_cdf(power)) * se


def tost(est: float, se: float, d: float, alpha: float) -> tuple[bool, float]:
    """Two one-sided tests against +/- d. Equivalence is rejected-toward-the-null."""
    if se <= 0:
        return False, 1.0
    p_lo = 1 - ND.cdf((est - (-d)) / se)      # H0: effect <= -d
    p_hi = ND.cdf((est - d) / se)             # H0: effect >= +d
    p = max(p_lo, p_hi)
    return p < alpha, p


def n_to_resolve(se: float, n_now: int | None, d: float, alpha: float, power: float):
    """How much more data would put delta_star inside reach. SE scales as 1/sqrt(n)."""
    need = mde(se, alpha, power)
    if need <= d or not n_now:
        return None
    return int(math.ceil(n_now * (need / d) ** 2))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estimate", type=float, help="the point estimate as reported")
    ap.add_argument("--se", type=float, help="realized standard error (from the model that produced the null)")
    ap.add_argument("--ci", nargs=2, type=float, metavar=("LO", "HI"),
                    help="95%% CI, used to derive SE if --se is not given")
    ap.add_argument("--outcome", help="key in references/effect_thresholds.md")
    ap.add_argument("--delta-star", type=float,
                    help="override the registry margin (requires --i-am-registering-this)")
    ap.add_argument("--i-am-registering-this", action="store_true",
                    help="acknowledge an ad-hoc margin; it is recorded as UNREGISTERED")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--power", type=float, default=0.80)
    ap.add_argument("--n", type=int, help="analysable n for THIS outcome (not the cohort size)")
    ap.add_argument("--events", type=int, help="event count, for time-to-event outcomes")
    ap.add_argument("--log-scale", action="store_true",
                    help="estimate is a hazard/odds ratio; compute on the log scale")
    ap.add_argument("--contrasts", type=int, default=1,
                    help="how many contrasts were screened to arrive here")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--list-thresholds", action="store_true")
    a = ap.parse_args()

    reg = load_thresholds()

    if a.list_thresholds:
        if not reg:
            print("No threshold registry found at", THRESHOLDS)
            return 1
        print(f"{'key':26s} {'delta*':>9s}  {'status':11s} citation")
        for k, v in sorted(reg.items()):
            print(f"{k:26s} {v['delta_star']:>9.4g}  {v['status']:11s} {v['citation'][:44]}")
        print("\nOnly CONFIRMED rows may be used. Rows marked NEEDS-CITATION are refused.")
        return 0

    if a.estimate is None:
        ap.error("--estimate is required")

    est = a.estimate
    se = a.se
    if se is None:
        if not a.ci:
            ap.error("give either --se or --ci")
        lo, hi = sorted(a.ci)
        if a.log_scale:
            if lo <= 0 or hi <= 0:
                ap.error("--log-scale needs a strictly positive CI")
            se = (math.log(hi) - math.log(lo)) / (2 * ND.inv_cdf(0.975))
        else:
            se = (hi - lo) / (2 * ND.inv_cdf(0.975))
    if a.log_scale:
        if est <= 0:
            ap.error("--log-scale needs a positive estimate")
        est = math.log(est)

    # --- the margin. This is the gate. ---
    src, status, citation = None, None, None
    if a.delta_star is not None:
        if not a.i_am_registering_this:
            print("REFUSED. An ad-hoc --delta-star is a margin chosen after seeing the data unless\n"
                  "you say so explicitly. Either add the outcome to\n"
                  f"  {THRESHOLDS}\n"
                  "with a citation, or re-run with --i-am-registering-this and accept that the\n"
                  "output will be stamped UNREGISTERED and cannot support a closed door.")
            return 2
        d, src, status, citation = abs(a.delta_star), "ad-hoc", "UNREGISTERED", "none"
    else:
        if not a.outcome:
            ap.error("--outcome (a registry key) or --delta-star is required")
        row = reg.get(a.outcome)
        if not row:
            print(f"REFUSED. '{a.outcome}' is not in the margin registry.\n"
                  f"  registry: {THRESHOLDS}\n"
                  f"  known keys: {', '.join(sorted(reg)) or '(none)'}\n"
                  "Add the outcome with a cited threshold before asking what the data could see.")
            return 2
        if row["status"] != "CONFIRMED":
            print(f"REFUSED. '{a.outcome}' is in the registry but marked {row['status']}.\n"
                  f"  citation field: {row['citation']}\n"
                  "A margin without a confirmed citation is a number someone made up. Confirm it\n"
                  "with the team, add the source, then re-run.")
            return 2
        d, src, status, citation = row["delta_star"], a.outcome, "CONFIRMED", row["citation"]
        if a.log_scale and row["scale"].lower().startswith("log"):
            pass

    # --- the three numbers ---
    z = ND.inv_cdf(1 - a.alpha / 2)
    lo95, hi95 = est - z * se, est + z * se
    m = mde(se, a.alpha, a.power)
    largest_compatible = max(abs(lo95), abs(hi95))
    R = largest_compatible / d if d else float("inf")
    equiv, p_tost = tost(est, se, d, a.alpha)
    p_null = 2 * (1 - ND.cdf(abs(est) / se)) if se > 0 else 1.0
    need_n = n_to_resolve(se, a.n, d, a.alpha, a.power)

    if p_null < a.alpha:
        verdict = "NOT A NULL"
        meaning = ("This estimate is distinguishable from zero at the stated alpha, so the "
                   "precision report is not the right instrument. Report the effect size and "
                   "interval, and send it through the adversarial review.")
    elif m < d and status != "CONFIRMED":
        # An ad-hoc margin can OPEN a question. It can never close one: otherwise the margin
        # gets widened until the null looks adequately powered, which is the abuse this whole
        # registry exists to prevent.
        verdict = "ADEQUATELY POWERED, MARGIN UNREGISTERED"
        meaning = ("The arithmetic says this null is adequately powered for the margin you "
                   "supplied, but the margin is UNREGISTERED, so this cannot be reported as a "
                   "closed door. Add the outcome to the registry with a citation and re-run. "
                   "An ad-hoc margin can open a question; it can never close one.")
    elif m < d and equiv:
        verdict = "CLOSED DOOR"
        meaning = ("An informative null. The analysis could have detected an effect of "
                   "clinical size and did not, and equivalence to within the margin is "
                   "supported. This IS a finding: report it as one and review it normally.")
    elif m < d and not equiv:
        verdict = "CLOSED DOOR (weak)"
        meaning = ("Adequately powered for the margin, but equivalence is not formally "
                   "supported. Report the interval and the margin; do not claim equivalence.")
    else:
        verdict = "INCONCLUSIVE"
        meaning = ("The effect space was never explored. This is NOT evidence of absence and "
                   "NOT a finding. It is a routing decision: the question is open and needs "
                   "more data or a better-powered design.")

    def fmt(x):
        return f"{math.exp(x):.4g} (ratio)" if a.log_scale else f"{x:+.4g}"

    if a.json:
        print(json.dumps(dict(
            verdict=verdict, estimate=est, se=se, ci95=[lo95, hi95], p_two_sided=p_null,
            mde=m, delta_star=d, compatibility_ratio=R, tost_p=p_tost, equivalence=equiv,
            margin_source=src, margin_status=status, citation=citation,
            analysable_n=a.n, events=a.events, contrasts=a.contrasts,
            n_to_resolve=need_n, alpha=a.alpha, power=a.power, log_scale=a.log_scale), indent=2))
        return 0

    print(f"\n  PRECISION REPORT                                   verdict: {verdict}")
    print(f"  {'-'*74}")
    print(f"  estimate                        {fmt(est)}   (SE {se:.4g}, two-sided p {p_null:.3g})")
    print(f"  95% compatibility interval      [{fmt(lo95)}, {fmt(hi95)}]")
    print(f"  margin we would not want to miss  {d:.4g}   [{status}: {citation[:40]}]")
    print(f"  {'-'*74}")
    print(f"  smallest detectable effect (MDE) {m:.4g}   at alpha {a.alpha}, power {a.power:.0%}")
    print(f"  largest effect still compatible  {largest_compatible:.4g}")
    print(f"  compatibility ratio R            {R:.2f}   "
          f"{'<- a clinically important effect is STILL ON THE TABLE' if R >= 1 else '<- important effects are excluded'}")
    print(f"  TOST equivalence at +/-{d:.4g}      {'supported' if equiv else 'NOT supported'} (p {p_tost:.3g})")
    if a.n:
        print(f"  analysable n for this outcome    {a.n}"
              + (f", events {a.events}" if a.events else ""))
    else:
        print("  analysable n                     NOT GIVEN. Give --n: the headline cohort size is\n"
              "                                   not the n behind this estimate, and the MDE is\n"
              "                                   meaningless without it.")
    if need_n:
        print(f"  n needed to bring the margin in reach   ~{need_n}"
              f"  ({need_n / a.n:.1f}x the current n)")
    if a.contrasts > 1:
        print(f"  contrasts screened to reach here {a.contrasts}"
              "   <- report this; a tail selected from many is not a single test")
    print(f"\n  {meaning}\n")
    if verdict == "INCONCLUSIVE":
        print("  Correct phrasing: \"we could not detect an effect smaller than "
              f"{m:.3g}; effects up to\n  {largest_compatible:.3g} remain compatible with these data.\"\n"
              "  Incorrect phrasing: anything implying an effect exists, is likely, or trends.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
