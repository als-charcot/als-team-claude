"""
fvc-slope — ALSFRS-R decline in bulbar vs limb onset, and baseline FVC as a
predictor of decline rate.  PRO-ACT (Pooled Resource Open-Access ALS Clinical Trials).

End-to-end:
  1. Load ALSFRS, ALSHISTORY, FVC, DEMOGRAPHICS, RILUZOLE from data/PROACT_ALL_FORMS.
  2. Derive per-subject ALSFRS-R decline slope (points/month) over the first 18 months.
  3. Onset group (pure Bulbar vs pure Limb) from ALSHISTORY.
  4. Baseline FVC (% of predicted) from the earliest FVC visit.
  5. Compare slopes bulbar vs limb (Welch t, Mann-Whitney, Cohen's d + CI, linear
     mixed-effects group x time interaction).
  6. Regress slope on baseline FVC%, unadjusted and adjusted for confounders.
  7. Save Plotly figures (HTML + PNG) and a results.json to outputs/.

Run:
    projects/manu/fvc-slope/.venv/Scripts/python.exe projects/manu/fvc-slope/scripts/analysis.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
import plotly.graph_objects as go
import plotly.express as px

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[4]          # workspace root
DATA = ROOT / "data" / "PROACT_ALL_FORMS"
OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

DAYS_PER_MONTH = 30.44
WINDOW_DAYS = 18 * DAYS_PER_MONTH                    # first 18 months
MIN_POINTS = 3                                       # >=3 ALSFRS-R points to fit a slope
MIN_SPAN_DAYS = 90                                   # slope must span >= ~3 months

PALETTE = {"Bulbar": "#D55E00", "Limb": "#0072B2"}   # colorblind-safe (Okabe-Ito)


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"F_PROACT_{name}.csv", encoding="utf-8-sig")


# ── 1. ALSFRS-R longitudinal → per-subject slope ──────────────────────────────
def build_slopes() -> pd.DataFrame:
    als = load("ALSFRS")[["subject_id", "ALSFRS_R_Total", "ALSFRS_Delta"]].copy()
    als = als.dropna(subset=["ALSFRS_R_Total", "ALSFRS_Delta"])
    als["ALSFRS_Delta"] = pd.to_numeric(als["ALSFRS_Delta"], errors="coerce")
    als["ALSFRS_R_Total"] = pd.to_numeric(als["ALSFRS_R_Total"], errors="coerce")
    als = als.dropna()
    # window: baseline (delta 0) through 18 months; drop pre-baseline negatives
    als = als[(als["ALSFRS_Delta"] >= 0) & (als["ALSFRS_Delta"] <= WINDOW_DAYS)]
    als["months"] = als["ALSFRS_Delta"] / DAYS_PER_MONTH

    rows = []
    long_records = []
    for sid, g in als.groupby("subject_id"):
        g = g.sort_values("months")
        span = g["ALSFRS_Delta"].max() - g["ALSFRS_Delta"].min()
        if len(g) < MIN_POINTS or span < MIN_SPAN_DAYS:
            continue
        # OLS slope of ALSFRS-R on months
        slope, intercept, r, p, se = stats.linregress(g["months"], g["ALSFRS_R_Total"])
        rows.append({
            "subject_id": sid,
            "slope": slope,                    # points / month (negative = decline)
            "baseline_alsfrsr": g["ALSFRS_R_Total"].iloc[0],
            "n_points": len(g),
            "followup_months": g["months"].max(),
        })
        for _, rr in g.iterrows():
            long_records.append({"subject_id": sid, "months": rr["months"],
                                 "ALSFRS_R_Total": rr["ALSFRS_R_Total"]})
    slopes = pd.DataFrame(rows)
    longdf = pd.DataFrame(long_records)
    return slopes, longdf


# ── 2. onset group ────────────────────────────────────────────────────────────
def build_onset() -> pd.DataFrame:
    h = load("ALSHISTORY")
    for c in ["Site_of_Onset___Bulbar", "Site_of_Onset___Limb"]:
        h[c] = pd.to_numeric(h[c], errors="coerce")
    txt = h["Site_of_Onset"].fillna("").astype(str)
    h["bulbar_txt"] = txt.str.contains("Bulbar", case=False) & ~txt.str.contains("Limb", case=False)
    h["limb_txt"] = txt.str.contains("Limb", case=False) & ~txt.str.contains("Bulbar", case=False)
    agg = h.groupby("subject_id").agg(
        bulbar=("Site_of_Onset___Bulbar", "max"),
        limb=("Site_of_Onset___Limb", "max"),
        bulbar_txt=("bulbar_txt", "max"),
        limb_txt=("limb_txt", "max"),
    ).reset_index()
    bul = (agg["bulbar"] == 1) | (agg["bulbar_txt"])
    lim = (agg["limb"] == 1) | (agg["limb_txt"])
    grp = np.where(bul & ~lim, "Bulbar", np.where(lim & ~bul, "Limb", None))
    agg["onset"] = grp
    return agg[["subject_id", "onset"]].dropna()


# ── 3. baseline FVC% predicted ────────────────────────────────────────────────
def build_fvc() -> pd.DataFrame:
    f = load("FVC").copy()
    f["Forced_Vital_Capacity_Delta"] = pd.to_numeric(f["Forced_Vital_Capacity_Delta"], errors="coerce")
    for c in ["pct_of_Normal_Trial_1", "pct_of_Normal_Trial_2", "pct_of_Normal_Trial_3"]:
        f[c] = pd.to_numeric(f[c], errors="coerce")
    # best of up to 3 trials at each visit (standard spirometry reporting)
    f["fvc_pct"] = f[["pct_of_Normal_Trial_1", "pct_of_Normal_Trial_2",
                      "pct_of_Normal_Trial_3"]].max(axis=1)
    f = f.dropna(subset=["fvc_pct", "Forced_Vital_Capacity_Delta"])
    # baseline visit = earliest around day 0 (allow small pre-baseline, up to 90d)
    f = f[(f["Forced_Vital_Capacity_Delta"] >= -30) & (f["Forced_Vital_Capacity_Delta"] <= 90)]
    f = f.sort_values(["subject_id", "Forced_Vital_Capacity_Delta"])
    base = f.groupby("subject_id").first().reset_index()
    return base[["subject_id", "fvc_pct"]].rename(columns={"fvc_pct": "baseline_fvc_pct"})


# ── 4. covariates ─────────────────────────────────────────────────────────────
def build_covariates() -> pd.DataFrame:
    d = load("DEMOGRAPHICS")
    d["Age"] = pd.to_numeric(d["Age"], errors="coerce")
    d["Sex"] = d["Sex"].astype(str).str.strip()
    d = d.groupby("subject_id").agg(age=("Age", "max"), sex=("Sex", "first")).reset_index()

    h = load("ALSHISTORY")
    h["Onset_Delta"] = pd.to_numeric(h["Onset_Delta"], errors="coerce")
    # disease duration at baseline (months) = -onset_delta/30.44 (onset before day 0)
    dd = h.groupby("subject_id")["Onset_Delta"].min().reset_index()
    dd["disease_dur_months"] = -dd["Onset_Delta"] / DAYS_PER_MONTH
    dd = dd[["subject_id", "disease_dur_months"]]

    try:
        ril = load("RILUZOLE")
        if "Subject_used_Riluzole" in ril.columns:
            ril["ril"] = ril["Subject_used_Riluzole"].astype(str).str.strip().str.lower().isin(["yes", "1", "true"])
        else:
            ril["ril"] = True  # presence in riluzole form implies use
        rr = ril.groupby("subject_id")["ril"].max().reset_index().rename(columns={"ril": "riluzole"})
    except Exception:
        rr = pd.DataFrame(columns=["subject_id", "riluzole"])

    cov = d.merge(dd, on="subject_id", how="outer")
    if len(rr):
        cov = cov.merge(rr, on="subject_id", how="left")
        cov["riluzole"] = cov["riluzole"].fillna(False)
    return cov


# ── stats helpers ─────────────────────────────────────────────────────────────
def cohens_d(a, b):
    a, b = np.asarray(a), np.asarray(b)
    n1, n2 = len(a), len(b)
    s = np.sqrt(((n1 - 1) * a.std(ddof=1) ** 2 + (n2 - 1) * b.std(ddof=1) ** 2) / (n1 + n2 - 2))
    d = (a.mean() - b.mean()) / s
    se = np.sqrt((n1 + n2) / (n1 * n2) + d ** 2 / (2 * (n1 + n2)))
    return d, (d - 1.96 * se, d + 1.96 * se)


def pearson_ci(r, n):
    z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
    lo, hi = np.tanh(z - 1.96 * se), np.tanh(z + 1.96 * se)
    return lo, hi


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    slopes, longdf = build_slopes()
    onset = build_onset()
    fvc = build_fvc()
    cov = build_covariates()

    df = slopes.merge(onset, on="subject_id", how="left") \
               .merge(fvc, on="subject_id", how="left") \
               .merge(cov, on="subject_id", how="left")

    results = {"window_months": 18, "min_points": MIN_POINTS}
    results["n_subjects_with_slope"] = int(len(slopes))
    results["slope_overall_mean"] = float(slopes["slope"].mean())
    results["median_points_per_subject"] = float(slopes["n_points"].median())

    # ===== Analysis A: bulbar vs limb =====
    grp = df.dropna(subset=["onset"])
    bul = grp.loc[grp.onset == "Bulbar", "slope"]
    lim = grp.loc[grp.onset == "Limb", "slope"]
    t, p_t = stats.ttest_ind(bul, lim, equal_var=False)
    u, p_u = stats.mannwhitneyu(bul, lim, alternative="two-sided")
    d, dci = cohens_d(bul, lim)
    A = {
        "n_bulbar": int(len(bul)), "n_limb": int(len(lim)),
        "mean_slope_bulbar": float(bul.mean()), "sd_slope_bulbar": float(bul.std(ddof=1)),
        "mean_slope_limb": float(lim.mean()), "sd_slope_limb": float(lim.std(ddof=1)),
        "median_slope_bulbar": float(bul.median()), "median_slope_limb": float(lim.median()),
        "welch_t": float(t), "welch_p": float(p_t),
        "mannwhitney_u": float(u), "mannwhitney_p": float(p_u),
        "cohens_d": float(d), "cohens_d_ci": [float(dci[0]), float(dci[1])],
    }

    # linear mixed-effects: ALSFRS_R ~ months * onset, random slope per subject
    lm = longdf.merge(onset, on="subject_id", how="inner").dropna()
    lm["onset"] = pd.Categorical(lm["onset"], categories=["Limb", "Bulbar"])
    md = smf.mixedlm("ALSFRS_R_Total ~ months * onset", lm, groups=lm["subject_id"],
                     re_formula="~months")
    mfit = md.fit(method="lbfgs", maxiter=200)
    inter = "months:onset[T.Bulbar]"
    A["mixedlm_interaction_coef"] = float(mfit.params[inter])
    A["mixedlm_interaction_ci"] = [float(mfit.conf_int().loc[inter, 0]),
                                   float(mfit.conf_int().loc[inter, 1])]
    A["mixedlm_interaction_p"] = float(mfit.pvalues[inter])
    A["mixedlm_limb_slope"] = float(mfit.params["months"])
    results["analysis_A"] = A

    # example subjects
    ex_b = grp.loc[grp.onset == "Bulbar"].sort_values("slope").iloc[len(bul)//2]
    ex_l = grp.loc[grp.onset == "Limb"].sort_values("slope").iloc[len(lim)//2]
    results["example_bulbar"] = {"subject_id": int(ex_b.subject_id), "slope": float(ex_b.slope),
                                 "baseline": float(ex_b.baseline_alsfrsr), "n": int(ex_b.n_points)}
    results["example_limb"] = {"subject_id": int(ex_l.subject_id), "slope": float(ex_l.slope),
                               "baseline": float(ex_l.baseline_alsfrsr), "n": int(ex_l.n_points)}

    # ===== Analysis B: baseline FVC% predicts slope =====
    fb = df.dropna(subset=["baseline_fvc_pct", "slope"]).copy()
    r_p, p_p = stats.pearsonr(fb["baseline_fvc_pct"], fb["slope"])
    r_s, p_s = stats.spearmanr(fb["baseline_fvc_pct"], fb["slope"])
    lo, hi = pearson_ci(r_p, len(fb))
    # unadjusted regression: slope ~ fvc
    m_un = smf.ols("slope ~ baseline_fvc_pct", fb).fit()
    # adjusted regression
    fb_adj = fb.dropna(subset=["age", "sex", "disease_dur_months", "onset"]).copy()
    if "riluzole" in fb_adj.columns:
        formula = "slope ~ baseline_fvc_pct + age + C(sex) + disease_dur_months + C(onset) + C(riluzole)"
    else:
        formula = "slope ~ baseline_fvc_pct + age + C(sex) + disease_dur_months + C(onset)"
    m_adj = smf.ols(formula, fb_adj).fit()
    B = {
        "n": int(len(fb)),
        "pearson_r": float(r_p), "pearson_p": float(p_p), "pearson_ci": [float(lo), float(hi)],
        "spearman_r": float(r_s), "spearman_p": float(p_s),
        "beta_unadj": float(m_un.params["baseline_fvc_pct"]),
        "beta_unadj_ci": [float(m_un.conf_int().loc["baseline_fvc_pct", 0]),
                          float(m_un.conf_int().loc["baseline_fvc_pct", 1])],
        "r2_unadj": float(m_un.rsquared),
        "n_adj": int(len(fb_adj)),
        "beta_adj": float(m_adj.params["baseline_fvc_pct"]),
        "beta_adj_ci": [float(m_adj.conf_int().loc["baseline_fvc_pct", 0]),
                        float(m_adj.conf_int().loc["baseline_fvc_pct", 1])],
        "beta_adj_p": float(m_adj.pvalues["baseline_fvc_pct"]),
        "r2_adj": float(m_adj.rsquared),
    }
    ex_fvc = fb.sort_values("baseline_fvc_pct").iloc[len(fb)//10]  # a low-FVC example
    B["example_lowfvc"] = {"subject_id": int(ex_fvc.subject_id),
                           "fvc_pct": float(ex_fvc.baseline_fvc_pct), "slope": float(ex_fvc.slope)}
    results["analysis_B"] = B

    # ===== FIGURES =====
    make_fig1(longdf, onset, A)
    make_fig2(grp)
    make_fig3(fb, m_un)

    with open(OUT / "results.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print(json.dumps(results, indent=2))
    df.to_csv(OUT / "subject_level.csv", index=False)   # local only (git-ignored)
    print(f"\n[OK] figures + results.json written to {OUT}")


def _save(fig, name):
    fig.write_html(str(OUT / f"{name}.html"), include_plotlyjs="cdn")
    fig.write_image(str(OUT / f"{name}.png"), width=1000, height=600, scale=2)


def make_fig1(longdf, onset, A):
    lm = longdf.merge(onset, on="subject_id", how="inner")
    lm["mbin"] = (lm["months"] // 1.5) * 1.5 + 0.75      # 1.5-month bins
    fig = go.Figure()
    for grp_name in ["Limb", "Bulbar"]:
        sub = lm[lm.onset == grp_name]
        agg = sub.groupby("mbin")["ALSFRS_R_Total"].agg(["mean", "sem", "count"]).reset_index()
        agg = agg[agg["count"] >= 20]
        c = PALETTE[grp_name]
        fig.add_trace(go.Scatter(
            x=list(agg.mbin) + list(agg.mbin[::-1]),
            y=list(agg["mean"] + 1.96 * agg["sem"]) + list((agg["mean"] - 1.96 * agg["sem"])[::-1]),
            fill="toself", fillcolor=c, opacity=0.15, line=dict(color="rgba(0,0,0,0)"),
            hoverinfo="skip", showlegend=False))
        fig.add_trace(go.Scatter(x=agg.mbin, y=agg["mean"], mode="lines+markers",
                                 name=f"{grp_name} onset", line=dict(color=c, width=3)))
    fig.update_layout(
        title="Mean ALSFRS-R trajectory over first 18 months, by site of onset",
        xaxis_title="Months since baseline", yaxis_title="ALSFRS-R total (0–48)",
        template="plotly_white", font=dict(size=14), legend=dict(x=0.02, y=0.02))
    _save(fig, "fig1_trajectory")


def make_fig2(grp):
    fig = go.Figure()
    for grp_name in ["Limb", "Bulbar"]:
        s = grp.loc[grp.onset == grp_name, "slope"]
        fig.add_trace(go.Violin(y=s, name=f"{grp_name} onset", box_visible=True,
                                meanline_visible=True, line_color=PALETTE[grp_name],
                                fillcolor=PALETTE[grp_name], opacity=0.5, points=False))
    fig.update_layout(
        title="Per-subject ALSFRS-R decline slope by site of onset",
        yaxis_title="Decline slope (ALSFRS-R points / month)",
        template="plotly_white", font=dict(size=14), showlegend=False)
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    _save(fig, "fig2_slope_violin")


def make_fig3(fb, model):
    fig = px.scatter(fb, x="baseline_fvc_pct", y="slope", color="onset",
                     color_discrete_map=PALETTE, opacity=0.45,
                     labels={"baseline_fvc_pct": "Baseline FVC (% predicted)",
                             "slope": "Decline slope (ALSFRS-R points / month)",
                             "onset": "Onset"})
    xs = np.linspace(fb["baseline_fvc_pct"].quantile(0.01),
                     fb["baseline_fvc_pct"].quantile(0.99), 50)
    ys = model.params["Intercept"] + model.params["baseline_fvc_pct"] * xs
    fig.add_trace(go.Scatter(x=xs, y=ys, mode="lines", name="OLS fit",
                             line=dict(color="black", width=3)))
    fig.update_layout(title="Baseline FVC (% predicted) vs subsequent ALSFRS-R decline slope",
                      template="plotly_white", font=dict(size=14))
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    _save(fig, "fig3_fvc_vs_slope")


if __name__ == "__main__":
    main()
