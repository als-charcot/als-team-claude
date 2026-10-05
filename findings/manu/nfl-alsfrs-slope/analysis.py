"""
nfl-alsfrs-slope (H-002) — Blood neurofilament light chain (NfL) as a correlate of
ALSFRS-R decline slope, with an exploratory (underpowered) survival look.
PRO-ACT (Pooled Resource Open-Access ALS Clinical Trials).

Motivation: medRxiv PREPRINT (not peer reviewed), Arguedas et al. (ALS/MND NHC, n=300),
reports plasma NfL vs ALSFRS-R rate of change r=-0.53 [-0.62,-0.42], cutoff 61 pg/mL.
Here we test it in PRO-ACT SERUM NfL. Serum != plasma: the 61 cutoff is a robustness
check, not an assumption.

End-to-end:
  1. Baseline serum NfL (earliest draw, 0-90d) from F_PROACT_Neurofilament.
  2. Per-subject ALSFRS-R slope (pts/month), first 18 months, >=3 visits, >=90d span
     (identical to H-001 fvc-slope, for consistency and to build on it).
  3. Covariates: age, sex, onset site, disease duration, baseline ALSFRS-R.
     (Riluzole excluded: it is a trial-presence flag here, not a treatment contrast.)
  4. PRIMARY (H1): Spearman + Pearson(log NfL) vs slope, with CIs; unadjusted + adjusted
     OLS; 61 pg/mL cutoff robustness; permutation negative control on the headline Spearman.
  5. EXPLORATORY (H2, flagged underpowered): baseline NfL vs time-to-death among the small
     decedent-only overlap (no censoring available) — Spearman + Cox HR per SD log-NfL.
  6. Save Plotly figures (HTML + PNG) and results.json to outputs/.

Run:
    projects/manu/nfl-alsfrs-slope/.venv/Scripts/python.exe projects/manu/nfl-alsfrs-slope/scripts/analysis.py
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from lifelines import CoxPHFitter
import plotly.graph_objects as go

# ── paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).resolve().parents[4]
DATA = ROOT / "data" / "PROACT_ALL_FORMS"
OUT = Path(__file__).resolve().parents[1] / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

DAYS_PER_MONTH = 30.44
WINDOW_DAYS = 18 * DAYS_PER_MONTH        # first 18 months (H-001 convention)
MIN_POINTS = 3                            # >=3 ALSFRS-R points to fit a slope
MIN_SPAN_DAYS = 90                        # slope must span >= ~3 months
BASELINE_MAX_DELTA = 90                   # baseline NfL within first 90 days
CUTOFF_PGML = 61.0                        # preprint's (plasma) cutoff, tested on serum
N_PERM = 5000
RNG = np.random.default_rng(20260907)

# colorblind-safe (Okabe-Ito), matching H-001
C_MAIN, C_FIT, C_HI, C_LO = "#0072B2", "#000000", "#D55E00", "#009E73"


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(DATA / f"F_PROACT_{name}.csv", encoding="utf-8-sig")


# ── 1. baseline serum NfL ─────────────────────────────────────────────────────
def build_nfl() -> pd.DataFrame:
    nf = load("Neurofilament").copy()
    nf["Result"] = pd.to_numeric(nf["Result"], errors="coerce")
    nf["Collection_Delta"] = pd.to_numeric(nf["Collection_Delta"], errors="coerce")
    nf = nf[nf["Matrix"].astype(str).str.upper() == "SERUM"]         # serum only
    nf = nf.dropna(subset=["Result", "Collection_Delta"])
    nf = nf[nf["Result"] > 0]
    nf = nf[(nf["Collection_Delta"] >= 0) & (nf["Collection_Delta"] <= BASELINE_MAX_DELTA)]
    nf = nf.sort_values(["subject_id", "Collection_Delta"])
    base = nf.groupby("subject_id").first().reset_index()
    base = base[["subject_id", "Collection_Delta", "Result"]].rename(
        columns={"Result": "baseline_nfl", "Collection_Delta": "nfl_delta"})
    base["log_nfl"] = np.log(base["baseline_nfl"])
    return base


# ── 2. ALSFRS-R slope (identical to H-001) ────────────────────────────────────
def build_slopes() -> pd.DataFrame:
    als = load("ALSFRS")[["subject_id", "ALSFRS_R_Total", "ALSFRS_Delta"]].copy()
    als["ALSFRS_Delta"] = pd.to_numeric(als["ALSFRS_Delta"], errors="coerce")
    als["ALSFRS_R_Total"] = pd.to_numeric(als["ALSFRS_R_Total"], errors="coerce")
    als = als.dropna()
    als = als[(als["ALSFRS_Delta"] >= 0) & (als["ALSFRS_Delta"] <= WINDOW_DAYS)]
    als["months"] = als["ALSFRS_Delta"] / DAYS_PER_MONTH
    rows = []
    for sid, g in als.groupby("subject_id"):
        g = g.sort_values("months")
        span = g["ALSFRS_Delta"].max() - g["ALSFRS_Delta"].min()
        if len(g) < MIN_POINTS or span < MIN_SPAN_DAYS:
            continue
        slope, intercept, r, p, se = stats.linregress(g["months"], g["ALSFRS_R_Total"])
        rows.append({"subject_id": sid, "slope": slope, "slope_se": se,
                     "baseline_alsfrsr": g["ALSFRS_R_Total"].iloc[0], "n_points": len(g)})
    return pd.DataFrame(rows)


# ── 3. covariates (from H-001) ────────────────────────────────────────────────
def build_onset() -> pd.DataFrame:
    h = load("ALSHISTORY")
    for c in ["Site_of_Onset___Bulbar", "Site_of_Onset___Limb"]:
        if c in h.columns:
            h[c] = pd.to_numeric(h[c], errors="coerce")
    txt = h["Site_of_Onset"].fillna("").astype(str) if "Site_of_Onset" in h.columns else pd.Series("", index=h.index)
    h["bulbar_txt"] = txt.str.contains("Bulbar", case=False) & ~txt.str.contains("Limb", case=False)
    h["limb_txt"] = txt.str.contains("Limb", case=False) & ~txt.str.contains("Bulbar", case=False)
    agg = h.groupby("subject_id").agg(
        bulbar=("Site_of_Onset___Bulbar", "max"), limb=("Site_of_Onset___Limb", "max"),
        bulbar_txt=("bulbar_txt", "max"), limb_txt=("limb_txt", "max")).reset_index()
    bul = (agg["bulbar"] == 1) | (agg["bulbar_txt"])
    lim = (agg["limb"] == 1) | (agg["limb_txt"])
    agg["onset"] = np.where(bul & ~lim, "Bulbar", np.where(lim & ~bul, "Limb", None))
    return agg[["subject_id", "onset"]].dropna()


def build_covariates() -> pd.DataFrame:
    d = load("DEMOGRAPHICS")
    d["Age"] = pd.to_numeric(d["Age"], errors="coerce")
    d["Sex"] = d["Sex"].astype(str).str.strip()
    d = d.groupby("subject_id").agg(age=("Age", "max"), sex=("Sex", "first")).reset_index()
    h = load("ALSHISTORY")
    h["Onset_Delta"] = pd.to_numeric(h["Onset_Delta"], errors="coerce")
    dd = h.groupby("subject_id")["Onset_Delta"].min().reset_index()
    dd["disease_dur_months"] = -dd["Onset_Delta"] / DAYS_PER_MONTH
    dd = dd[["subject_id", "disease_dur_months"]]
    # NOTE: riluzole intentionally NOT built as a covariate — in the NfL cohort the riluzole
    # form has no "No" rows, so it would encode trial-presence, not treatment use
    # (adversarial-review, confounding lens). Left out rather than mislabelled as a control.
    cov = d.merge(dd, on="subject_id", how="outer")
    return cov


# ── stats helpers ─────────────────────────────────────────────────────────────
def pearson_ci(r, n):
    z = np.arctanh(r); se = 1 / np.sqrt(n - 3)
    return float(np.tanh(z - 1.96 * se)), float(np.tanh(z + 1.96 * se))


def spearman_boot_ci(x, y, n_boot=2000):
    x, y = np.asarray(x), np.asarray(y); n = len(x)
    rs = []
    for _ in range(n_boot):
        idx = RNG.integers(0, n, n)
        rr = stats.spearmanr(x[idx], y[idx]).statistic
        if not np.isnan(rr):
            rs.append(rr)
    return float(np.percentile(rs, 2.5)), float(np.percentile(rs, 97.5))


def perm_test_spearman(x, y, n_perm=N_PERM):
    x, y = np.asarray(x), np.asarray(y)
    obs = stats.spearmanr(x, y).statistic
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = stats.spearmanr(x, RNG.permutation(y)).statistic
    p = (np.sum(np.abs(null) >= abs(obs)) + 1) / (n_perm + 1)
    return float(obs), null, float(p)


# ── main ──────────────────────────────────────────────────────────────────────
def main():
    nfl = build_nfl()
    slopes = build_slopes()
    onset = build_onset()
    cov = build_covariates()

    df = (nfl.merge(slopes, on="subject_id", how="inner")
             .merge(onset, on="subject_id", how="left")
             .merge(cov, on="subject_id", how="left"))

    R = {"cutoff_pgml": CUTOFF_PGML, "window_months": 18, "min_points": MIN_POINTS,
         "baseline_max_delta_days": BASELINE_MAX_DELTA, "n_perm": N_PERM}
    R["n_nfl_subjects_serum_baseline"] = int(len(nfl))
    R["n_slope_subjects"] = int(len(slopes))
    R["n_primary"] = int(len(df))
    R["nfl_median_pgml"] = float(nfl["baseline_nfl"].median())
    R["nfl_iqr_pgml"] = [float(nfl["baseline_nfl"].quantile(.25)), float(nfl["baseline_nfl"].quantile(.75))]
    R["nfl_max_pgml"] = float(nfl["baseline_nfl"].max())   # max of the ANALYZED serum-baseline variable

    # ===== PRIMARY H1: NfL vs ALSFRS-R slope =====
    d1 = df.dropna(subset=["baseline_nfl", "slope"]).copy()
    n1 = len(d1)
    rho, p_rho = stats.spearmanr(d1["baseline_nfl"], d1["slope"])
    rho_lo, rho_hi = spearman_boot_ci(d1["baseline_nfl"].values, d1["slope"].values)
    r_p, p_p = stats.pearsonr(d1["log_nfl"], d1["slope"])
    r_lo, r_hi = pearson_ci(r_p, n1)
    m_un = smf.ols("slope ~ log_nfl", d1).fit()
    # Adjusted model. Riluzole is INTENTIONALLY EXCLUDED: in this cohort the riluzole form
    # carries no "No" rows, so the coded variable is a trial-presence flag, not a treatment
    # contrast — adjusting for it would be misleading (adversarial-review, confounding lens).
    d1_adj = d1.dropna(subset=["age", "sex", "disease_dur_months", "onset", "baseline_alsfrsr"]).copy()
    m_adj = smf.ols("slope ~ log_nfl + age + C(sex) + disease_dur_months + C(onset) + baseline_alsfrsr",
                    d1_adj).fit()
    # Apples-to-apples: unadjusted on the SAME complete-case cohort, so the adjusted vs
    # unadjusted contrast is not conflated with the cohort shrinking from 788 to n_adj.
    m_un_same = smf.ols("slope ~ log_nfl", d1_adj).fit()
    # Less-selected adjusted model: drop the onset requirement (onset missingness is a
    # trial-recording artifact, balanced on NfL and slope), recovering a larger cohort.
    d1_adj2 = d1.dropna(subset=["age", "sex", "disease_dur_months", "baseline_alsfrsr"]).copy()
    m_adj2 = smf.ols("slope ~ log_nfl + age + C(sex) + disease_dur_months + baseline_alsfrsr",
                     d1_adj2).fit()
    # Precision-weighted robustness (WLS): each per-subject slope is itself an OLS estimate
    # with its own SE (generated-regressor structure); down-weight the noisy ones.
    wls_df = d1[d1["slope_se"] > 0].copy()
    m_wls = smf.wls("slope ~ log_nfl", wls_df, weights=1.0 / wls_df["slope_se"] ** 2).fit()
    # Partial correlation of NfL vs slope, controlling disease duration (a genuine confounder):
    # residualize both on duration, then correlate the residuals.
    pc = d1.dropna(subset=["disease_dur_months"]).copy()
    rx = pc["log_nfl"] - smf.ols("log_nfl ~ disease_dur_months", pc).fit().predict(pc)
    ry = pc["slope"] - smf.ols("slope ~ disease_dur_months", pc).fit().predict(pc)
    partial_r = float(stats.pearsonr(rx, ry)[0])
    obs, null, p_perm = perm_test_spearman(d1["baseline_nfl"].values, d1["slope"].values)

    # 61 pg/mL cutoff robustness (serum!)
    d1["high61"] = (d1["baseline_nfl"] > CUTOFF_PGML)
    hi, lo = d1.loc[d1.high61, "slope"], d1.loc[~d1.high61, "slope"]
    t_c, p_c = stats.ttest_ind(hi, lo, equal_var=False)
    m_int = smf.ols("slope ~ log_nfl * high61", d1).fit()

    H1 = {
        "n": n1,
        "spearman_rho": float(rho), "spearman_p": float(p_rho), "spearman_ci": [rho_lo, rho_hi],
        "pearson_lognfl_r": float(r_p), "pearson_p": float(p_p), "pearson_ci": [r_lo, r_hi],
        "beta_unadj": float(m_un.params["log_nfl"]),
        "beta_unadj_ci": [float(m_un.conf_int().loc["log_nfl", 0]), float(m_un.conf_int().loc["log_nfl", 1])],
        "beta_unadj_p": float(m_un.pvalues["log_nfl"]), "r2_unadj": float(m_un.rsquared),
        "n_adj": int(len(d1_adj)),
        "beta_adj": float(m_adj.params["log_nfl"]),
        "beta_adj_ci": [float(m_adj.conf_int().loc["log_nfl", 0]), float(m_adj.conf_int().loc["log_nfl", 1])],
        "beta_adj_p": float(m_adj.pvalues["log_nfl"]), "r2_adj": float(m_adj.rsquared),
        "beta_unadj_same_cohort": float(m_un_same.params["log_nfl"]),   # unadjusted on the n_adj cohort
        "n_adj_noonset": int(len(d1_adj2)),
        "beta_adj_noonset": float(m_adj2.params["log_nfl"]),
        "beta_adj_noonset_ci": [float(m_adj2.conf_int().loc["log_nfl", 0]), float(m_adj2.conf_int().loc["log_nfl", 1])],
        "beta_adj_noonset_p": float(m_adj2.pvalues["log_nfl"]),
        "n_wls": int(len(wls_df)),
        "beta_wls": float(m_wls.params["log_nfl"]),
        "beta_wls_ci": [float(m_wls.conf_int().loc["log_nfl", 0]), float(m_wls.conf_int().loc["log_nfl", 1])],
        "partial_r_ctrl_duration": partial_r,
        "perm_observed_rho": obs, "perm_p": p_perm,
        "perm_null_mean": float(null.mean()), "perm_null_sd": float(null.std()),
        "cutoff_n_high": int(hi.shape[0]), "cutoff_n_low": int(lo.shape[0]),
        "cutoff_mean_slope_high": float(hi.mean()), "cutoff_mean_slope_low": float(lo.mean()),
        "cutoff_welch_t": float(t_c), "cutoff_welch_p": float(p_c),
        "cutoff_interaction_coef": float(m_int.params["log_nfl:high61[T.True]"]),
        "cutoff_interaction_p": float(m_int.pvalues["log_nfl:high61[T.True]"]),
    }
    # concrete examples
    d1s = d1.sort_values("baseline_nfl")
    ex_hi = d1s.iloc[int(0.95 * n1)]           # high-NfL subject
    ex_lo = d1s.iloc[int(0.05 * n1)]           # low-NfL subject
    H1["example_high_nfl"] = {"subject_id": int(ex_hi.subject_id), "nfl": float(ex_hi.baseline_nfl),
                              "slope": float(ex_hi.slope), "baseline_alsfrsr": float(ex_hi.baseline_alsfrsr)}
    H1["example_low_nfl"] = {"subject_id": int(ex_lo.subject_id), "nfl": float(ex_lo.baseline_nfl),
                             "slope": float(ex_lo.slope), "baseline_alsfrsr": float(ex_lo.baseline_alsfrsr)}
    R["H1"] = H1

    # ===== EXPLORATORY H2 (flagged, underpowered): NfL vs survival =====
    death = load("DEATHDATA")[["subject_id", "Subject_Died", "Death_Days"]].copy()
    death["Death_Days"] = pd.to_numeric(death["Death_Days"], errors="coerce")
    death["died"] = death["Subject_Died"].astype(str).str.lower().eq("yes").astype(int)
    s = nfl.merge(death, on="subject_id", how="inner").dropna(subset=["Death_Days"])
    s = s[s["Death_Days"] >= 0]
    H2 = {"n": int(len(s)), "n_events": int(s["died"].sum()), "n_censored": int((s["died"] == 0).sum())}
    if len(s) >= 10:
        rho2, p2 = stats.spearmanr(s["log_nfl"], s["Death_Days"])
        H2["spearman_lognfl_vs_deathdays"] = float(rho2)
        H2["spearman_p"] = float(p2)
        s = s.copy()
        s["z_lognfl"] = (s["log_nfl"] - s["log_nfl"].mean()) / s["log_nfl"].std(ddof=0)
        try:
            cph = CoxPHFitter()
            cph.fit(s[["Death_Days", "died", "z_lognfl"]], duration_col="Death_Days", event_col="died")
            H2["cox_hr_per_sd_lognfl"] = float(np.exp(cph.params_["z_lognfl"]))
            ci = cph.confidence_intervals_
            H2["cox_hr_ci"] = [float(np.exp(ci.iloc[0, 0])), float(np.exp(ci.iloc[0, 1]))]
            H2["cox_p"] = float(cph.summary.loc["z_lognfl", "p"])
        except Exception as e:
            H2["cox_error"] = str(e)
        ex_s = s.sort_values("baseline_nfl").iloc[int(0.9 * len(s))]
        H2["example"] = {"subject_id": int(ex_s.subject_id), "nfl": float(ex_s.baseline_nfl),
                         "death_days": float(ex_s.Death_Days)}
    R["H2_exploratory"] = H2

    # ===== FIGURES =====
    make_fig1(d1, m_un)
    make_fig2(obs, null, p_perm)
    make_fig3(d1)
    if len(s) >= 10:
        make_fig4(s)

    with open(OUT / "results.json", "w") as fh:
        json.dump(R, fh, indent=2)
    print(json.dumps(R, indent=2))
    df.to_csv(OUT / "subject_level.csv", index=False)     # local only (git-ignored)
    print(f"\n[OK] results.json + figures written to {OUT}")


def _save(fig, name):
    fig.write_html(str(OUT / f"{name}.html"), include_plotlyjs="cdn")
    fig.write_image(str(OUT / f"{name}.png"), width=1000, height=600, scale=2)


def make_fig1(d1, model):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=d1["baseline_nfl"], y=d1["slope"], mode="markers",
                             marker=dict(color=C_MAIN, opacity=0.4, size=6),
                             name="subject", hovertemplate="NfL %{x:.0f} pg/mL<br>slope %{y:.2f}<extra></extra>"))
    xs_log = np.linspace(d1["log_nfl"].quantile(0.01), d1["log_nfl"].quantile(0.99), 60)
    ys = model.params["Intercept"] + model.params["log_nfl"] * xs_log
    fig.add_trace(go.Scatter(x=np.exp(xs_log), y=ys, mode="lines",
                             line=dict(color=C_FIT, width=3), name="OLS fit (log NfL)"))
    # cutoff drawn as a trace (raw data coords) — reliable on a log axis, unlike add_vline
    fig.add_trace(go.Scatter(x=[CUTOFF_PGML, CUTOFF_PGML],
                             y=[d1["slope"].min(), d1["slope"].max()], mode="lines",
                             line=dict(color=C_HI, dash="dot", width=2), name="61 pg/mL cutoff"))
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.update_layout(title="Baseline serum NfL vs subsequent ALSFRS-R decline slope",
                      xaxis_title="Baseline serum NfL (pg/mL, log scale)",
                      yaxis_title="ALSFRS-R decline slope (points / month)",
                      xaxis_type="log", template="plotly_white", font=dict(size=14))
    _save(fig, "fig1_nfl_vs_slope")


def make_fig2(obs, null, p_perm):
    fig = go.Figure()
    fig.add_trace(go.Histogram(x=null, nbinsx=60, marker_color="#999999",
                               name="permuted null"))
    fig.add_vline(x=obs, line_color=C_HI, line_width=3,
                  annotation_text=f"observed ρ={obs:.2f}", annotation_position="top left")
    fig.update_layout(
        title=f"Permutation negative control (5000 shuffles), permutation p={p_perm:.4g}",
        xaxis_title="Spearman ρ under random NfL–slope pairing",
        yaxis_title="count", template="plotly_white", font=dict(size=14), showlegend=False)
    _save(fig, "fig2_permutation_null")


def make_fig3(d1):
    fig = go.Figure()
    for label, mask, col in [("NfL ≤ 61 pg/mL", ~d1["high61"], C_LO), ("NfL > 61 pg/mL", d1["high61"], C_HI)]:
        fig.add_trace(go.Violin(y=d1.loc[mask, "slope"], name=label, box_visible=True,
                                meanline_visible=True, line_color=col, fillcolor=col,
                                opacity=0.5, points=False))
    fig.add_hline(y=0, line_dash="dot", line_color="gray")
    fig.update_layout(title="ALSFRS-R decline slope by serum NfL, split at the preprint's 61 pg/mL cutoff",
                      yaxis_title="ALSFRS-R decline slope (points / month)",
                      template="plotly_white", font=dict(size=14), showlegend=False)
    _save(fig, "fig3_cutoff_violin")


def make_fig4(s):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=s["baseline_nfl"], y=s["Death_Days"], mode="markers",
                             marker=dict(color=C_HI, opacity=0.6, size=8),
                             hovertemplate="NfL %{x:.0f} pg/mL<br>death day %{y:.0f}<extra></extra>"))
    fig.update_layout(
        title=f"EXPLORATORY (n={len(s)}, all deaths, no censoring): baseline NfL vs time to death",
        xaxis_title="Baseline serum NfL (pg/mL, log scale)", xaxis_type="log",
        yaxis_title="Days from baseline to death", template="plotly_white", font=dict(size=14))
    _save(fig, "fig4_survival_exploratory")


if __name__ == "__main__":
    main()
