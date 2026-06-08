"""
Demo experiment: ALS progression visualizations
-------------------------------------------------
Figures produced (saved to outputs/):
  1. alsfrs_trajectory.png  — median ALSFRS-R decline by onset type
  2. fvc_vs_slope.png        — baseline FVC% vs decline rate, by onset type
  3. survival_by_tertile.png — Kaplan-Meier: fast / medium / slow progressors

Files needed (set PROACT_DIR below):
  F_PROACT_ALSFRS.csv, F_PROACT_ALSHISTORY.csv,
  F_PROACT_DEMOGRAPHICS.csv, F_PROACT_FVC.csv, F_PROACT_DEATHDATA.csv

Usage:
  python scripts/demo_alsfrs_progression.py
"""

import os, sys
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

# ── SET THIS TO YOUR LOCAL PROACT FOLDER ─────────────────────────────────────
PROACT_DIR = r"PROACT_ALL_FORMS"
# Example absolute path (Windows):
#   PROACT_DIR = r"C:\Users\yourname\Documents\PROACT_ALL_FORMS"
# ─────────────────────────────────────────────────────────────────────────────

OUT = "outputs"
os.makedirs(OUT, exist_ok=True)

COLORS = {"Bulbar": "#E05C5C", "Limb": "#4A90D9", "Limb+Bulbar": "#F0A500"}

def load(fname):
    path = os.path.join(PROACT_DIR, fname)
    if not os.path.exists(path):
        sys.exit(f"ERROR: cannot find {path}\nSet PROACT_DIR at the top of this script.")
    return pd.read_csv(path, encoding="utf-8-sig", low_memory=False)

# ── LOAD ──────────────────────────────────────────────────────────────────────
print("Loading data...")
alsfrs   = load("F_PROACT_ALSFRS.csv")
history  = load("F_PROACT_ALSHISTORY.csv")
fvc_raw  = load("F_PROACT_FVC.csv")
death    = load("F_PROACT_DEATHDATA.csv")

# ── ONSET TYPE ────────────────────────────────────────────────────────────────
hist1 = history.drop_duplicates("subject_id").copy()

def get_onset(row):
    # try string column first (more complete)
    for col in ["Site_of_Onset"]:
        val = str(row.get(col, ""))
        if "Bulbar" in val: return "Bulbar"
        if "Limb and Bulbar" in val or "Limb+Bulbar" in val: return "Limb+Bulbar"
        if "Limb" in val or "Spine" in val: return "Limb"
    # fall back to binary flag columns
    if row.get("Site_of_Onset___Bulbar") == 1: return "Bulbar"
    if row.get("Site_of_Onset___Limb_and_Bulbar") == 1: return "Limb+Bulbar"
    if row.get("Site_of_Onset___Limb") == 1 or row.get("Site_of_Onset___Spine") == 1:
        return "Limb"
    return None

hist1["onset_type"] = hist1.apply(get_onset, axis=1)
onset = hist1[["subject_id","onset_type"]].dropna()
print(f"  Subjects with onset type: {len(onset):,}")
print(f"  {onset['onset_type'].value_counts().to_dict()}")

# ── ALSFRS-R SCORE + SLOPE ────────────────────────────────────────────────────
alsfrs["score"] = pd.to_numeric(alsfrs["ALSFRS_R_Total"], errors="coerce")
alsfrs["score"] = alsfrs["score"].fillna(
    pd.to_numeric(alsfrs["ALSFRS_Total"], errors="coerce"))
alsfrs["delta"] = pd.to_numeric(alsfrs["ALSFRS_Delta"], errors="coerce")
valid = alsfrs.dropna(subset=["score","delta"]).copy()

def ols_slope(df):
    if len(df) < 3: return np.nan
    m, *_ = stats.linregress(df["delta"].values, df["score"].values)
    return m * 30   # convert per-day → per-month

slopes = (valid.groupby("subject_id")
               .apply(ols_slope)
               .rename("slope_per_month")
               .reset_index())

# ── FVC BASELINE ──────────────────────────────────────────────────────────────
fvc_raw["pct"]   = pd.to_numeric(fvc_raw["pct_of_Normal_Trial_1"], errors="coerce")
fvc_raw["fdelta"] = pd.to_numeric(fvc_raw["Forced_Vital_Capacity_Delta"], errors="coerce")
baseline_fvc = (fvc_raw.dropna(subset=["pct","fdelta"])
                       .sort_values("fdelta")
                       .groupby("subject_id").first()[["pct"]]
                       .rename(columns={"pct":"fvc_pct"})
                       .reset_index())

# ── MASTER ────────────────────────────────────────────────────────────────────
master = (slopes
          .merge(onset, on="subject_id", how="left")
          .merge(baseline_fvc, on="subject_id", how="left")
          .dropna(subset=["slope_per_month"]))

print(f"  Subjects with usable slope: {len(master):,}")

# ── FIGURE 1: TRAJECTORY BY ONSET TYPE ───────────────────────────────────────
print("\nPlot 1: ALSFRS-R trajectory by onset type...")
ao = valid.merge(onset, on="subject_id", how="left").dropna(subset=["onset_type"])
bins = np.arange(0, 750, 90)

fig, ax = plt.subplots(figsize=(9, 5))
for otype, color in COLORS.items():
    grp = ao[ao["onset_type"] == otype].copy()
    if grp.empty: continue
    grp["bin"] = pd.cut(grp["delta"], bins=bins, labels=bins[:-1], right=False)
    binned = grp.dropna(subset=["bin"])
    binned["bin"] = binned["bin"].astype(float)
    agg = binned.groupby("bin")["score"].agg(["median","count",
          lambda x: x.quantile(.25), lambda x: x.quantile(.75)]).reset_index()
    agg.columns = ["bin","median","count","q25","q75"]
    agg = agg[agg["count"] >= 20]
    n = len(grp["subject_id"].unique())
    ax.plot(agg["bin"]/30, agg["median"], color=color, lw=2.5,
            label=f"{otype} (n={n:,})")
    ax.fill_between(agg["bin"]/30, agg["q25"], agg["q75"],
                    color=color, alpha=0.13)

ax.invert_yaxis()
ax.set_xlabel("Months from trial entry", fontsize=12)
ax.set_ylabel("ALSFRS-R Total Score", fontsize=12)
ax.set_title("ALSFRS-R Progression by Site of Onset\n"
             "Median ± IQR · PRO-ACT cohort", fontsize=13)
ax.legend(fontsize=11); ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "alsfrs_trajectory.png"), dpi=150)
plt.close()
print("  Saved: outputs/alsfrs_trajectory.png")

# ── FIGURE 2: BASELINE FVC VS SLOPE ──────────────────────────────────────────
print("Plot 2: baseline FVC vs ALSFRS-R slope...")
fs = master.dropna(subset=["fvc_pct","onset_type"])

fig, ax = plt.subplots(figsize=(8, 5))
for otype, color in COLORS.items():
    grp = fs[fs["onset_type"] == otype]
    if len(grp) < 5: continue
    ax.scatter(grp["fvc_pct"], grp["slope_per_month"],
               color=color, alpha=0.3, s=16, label=f"{otype} (n={len(grp):,})")

x, y = fs["fvc_pct"].values, fs["slope_per_month"].values
ok = np.isfinite(x) & np.isfinite(y)
if ok.sum() > 20:
    m, b, r, p, _ = stats.linregress(x[ok], y[ok])
    xr = np.linspace(np.nanpercentile(x[ok],1), np.nanpercentile(x[ok],99), 200)
    ax.plot(xr, m*xr+b, "k--", lw=1.5, alpha=0.7,
            label=f"Overall: r = {r:.2f},  p = {p:.3f}")

ax.axhline(0, color="gray", lw=0.8, ls=":")
ax.set_xlabel("Baseline FVC (% of normal)", fontsize=12)
ax.set_ylabel("ALSFRS-R slope (points / month)", fontsize=12)
ax.set_title("Does Respiratory Reserve Predict Decline Rate?\n"
             "Baseline FVC% vs ALSFRS-R slope · PRO-ACT", fontsize=13)
ax.legend(fontsize=10, loc="lower right"); ax.grid(alpha=0.25)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "fvc_vs_slope.png"), dpi=150)
plt.close()
print("  Saved: outputs/fvc_vs_slope.png")

# ── FIGURE 3: KAPLAN-MEIER BY PROGRESSION TERTILE ───────────────────────────
print("Plot 3: survival by progression tertile...")
death["died"]       = (death["Subject_Died"].str.strip().str.lower() == "yes").astype(int)
death["death_days"] = pd.to_numeric(death["Death_Days"], errors="coerce")
death_clean = death[["subject_id","died","death_days"]].drop_duplicates("subject_id")

km_df = master.merge(death_clean, on="subject_id", how="inner")
km_df = km_df.dropna(subset=["slope_per_month"])

t33, t67 = km_df["slope_per_month"].quantile([1/3, 2/3])
def tertile(s):
    if s <= t33: return "Fast (bottom third)"
    if s <= t67: return "Medium"
    return "Slow (top third)"
km_df["tertile"] = km_df["slope_per_month"].apply(tertile)

# For subjects who didn't die, use max observed delta as censored time
max_delta = valid.groupby("subject_id")["delta"].max().rename("max_obs").reset_index()
km_df = km_df.merge(max_delta, on="subject_id", how="left")
km_df["time"] = np.where(km_df["died"]==1,
                          km_df["death_days"],
                          km_df["max_obs"].fillna(365))
km_df = km_df[km_df["time"] > 0]

def km_curve(times, events):
    idx = np.argsort(times)
    t, e = times[idx], events[idx]
    unique_t = np.unique(t)
    n = len(t); surv = 1.0
    pts = [(0, 1.0)]
    for ti in unique_t:
        d = ((t == ti) & (e == 1)).sum()
        if d == 0: n -= (t == ti).sum(); continue
        surv *= (1 - d/n)
        pts.append((ti, surv))
        n -= (t == ti).sum()
    return np.array(pts)

fig, ax = plt.subplots(figsize=(9, 5))
tcolors = {"Fast (bottom third)":"#E05C5C",
           "Medium":"#F0A500",
           "Slow (top third)":"#4A90D9"}
for grp_name, color in tcolors.items():
    grp = km_df[km_df["tertile"] == grp_name]
    if len(grp) < 10: continue
    pts = km_curve(grp["time"].values, grp["died"].values)
    ax.step(pts[:,0]/30, pts[:,1], where="post", color=color, lw=2.2,
            label=f"{grp_name} (n={len(grp):,})")

ax.set_xlabel("Months from trial entry", fontsize=12)
ax.set_ylabel("Survival probability", fontsize=12)
ax.set_title("Survival by Progression Tertile\n"
             "Stratified by ALSFRS-R slope · PRO-ACT", fontsize=13)
ax.legend(fontsize=11); ax.grid(alpha=0.25)
ax.set_ylim(0, 1.05); ax.set_xlim(left=0)
fig.tight_layout()
fig.savefig(os.path.join(OUT, "survival_by_tertile.png"), dpi=150)
plt.close()
print("  Saved: outputs/survival_by_tertile.png")

# ── SUMMARY ───────────────────────────────────────────────────────────────────
b = master[master["onset_type"]=="Bulbar"]["slope_per_month"].dropna()
l = master[master["onset_type"]=="Limb"]["slope_per_month"].dropna()
print("\n── Key numbers ──────────────────────────────────────")
for otype in ["Bulbar","Limb","Limb+Bulbar"]:
    g = master[master["onset_type"]==otype]["slope_per_month"].dropna()
    if len(g): print(f"  {otype:16s}  median slope = {g.median():.2f} pts/month  (n={len(g):,})")
if len(b)>5 and len(l)>5:
    _, p = stats.mannwhitneyu(b, l, alternative="two-sided")
    d = (b.mean()-l.mean()) / np.sqrt((b.std()**2+l.std()**2)/2)
    print(f"\n  Bulbar vs Limb:  p = {p:.4f},  Cohen's d = {d:.3f}")
print("\nDone. Check the outputs/ folder for the three figures.")
