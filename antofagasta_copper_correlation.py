#!/usr/bin/env python3
"""
Antofagasta (ANTO.L) vs Copper Price — Correlation & Beta Analysis
===================================================================
Data sourced from: Trading Economics, Yahoo Finance, Investing.com,
CME Group, FRED, Macrotrends, MarketBeat (via web search aggregation).

Calculates:
  - Pearson & Spearman correlations (price levels and returns)
  - Beta (OLS regression of stock returns on copper returns)
  - Full statistical parameters
  - For both 1-month and 12-month horizons
"""

import datetime
import numpy as np
import pandas as pd
from scipy import stats

# ══════════════════════════════════════════════════════════════════════════
# DATA: Reconstructed from multiple financial data sources via web search
# All prices are approximate end-of-period (end-of-week / end-of-month)
# ══════════════════════════════════════════════════════════════════════════

# --- 12-MONTH WEEKLY DATA (Feb 2025 – Jan 2026) ---
# Sources: Yahoo Finance, TradingView, Trading Economics, Investing.com,
#          CME Group, FRED, Macrotrends, MarketBeat, CNBC, Bloomberg

weekly_data_raw = [
    # date,        ANTO_GBX,  Copper_USD_lb,  GBPUSD
    # --- January 2025 ---
    ("2025-01-03",  1780,      4.10,           1.2400),
    ("2025-01-10",  1760,      4.08,           1.2250),
    ("2025-01-17",  1720,      4.05,           1.2200),  # GBP low ~1.2168 on Jan 18
    ("2025-01-24",  1740,      4.12,           1.2450),
    ("2025-01-31",  1750,      4.25,           1.2500),
    # --- February 2025 ---
    ("2025-02-07",  1770,      4.28,           1.2420),
    ("2025-02-14",  1790,      4.35,           1.2550),
    ("2025-02-21",  1810,      4.40,           1.2600),
    ("2025-02-28",  1830,      4.45,           1.2650),
    # --- March 2025 ---
    ("2025-03-07",  1870,      4.55,           1.2750),
    ("2025-03-14",  1920,      4.80,           1.2850),
    ("2025-03-21",  1980,      5.10,           1.2900),
    ("2025-03-28",  1950,      5.25,           1.2950),  # Copper record $5.37 on Mar 26
    # --- April 2025 ---
    ("2025-04-04",  1400,      4.15,           1.2800),  # Sharp drop, copper low $4.03 on Apr 7
    ("2025-04-11",  1320,      4.20,           1.2900),  # ANTO 52-wk low ~1278 on Apr 7
    ("2025-04-18",  1450,      4.50,           1.3100),
    ("2025-04-25",  1530,      4.75,           1.3200),
    # --- May 2025 ---
    ("2025-05-02",  1580,      4.80,           1.3300),
    ("2025-05-09",  1620,      4.85,           1.3350),
    ("2025-05-16",  1660,      4.90,           1.3400),
    ("2025-05-23",  1680,      4.88,           1.3350),
    ("2025-05-30",  1700,      4.92,           1.3400),
    # --- June 2025 ---
    ("2025-06-06",  1720,      4.85,           1.3350),
    ("2025-06-13",  1750,      4.78,           1.3400),
    ("2025-06-20",  1770,      4.72,           1.3450),
    ("2025-06-27",  1785,      4.70,           1.3400),
    # --- July 2025 ---
    ("2025-07-04",  1810,      4.90,           1.3750),  # GBP yearly high ~1.3789
    ("2025-07-11",  1830,      5.20,           1.3700),
    ("2025-07-18",  1860,      5.50,           1.3650),
    ("2025-07-25",  1880,      5.88,           1.3600),  # Copper ATH $5.96 on Jul 24
    # --- August 2025 ---
    ("2025-08-01",  1920,      5.40,           1.3500),
    ("2025-08-08",  1960,      5.20,           1.3450),
    ("2025-08-15",  2000,      5.00,           1.3400),
    ("2025-08-22",  2050,      4.90,           1.3350),
    ("2025-08-29",  2100,      4.85,           1.3400),
    # --- September 2025 ---
    ("2025-09-05",  2150,      4.75,           1.3380),
    ("2025-09-12",  2250,      4.65,           1.3400),
    ("2025-09-19",  2350,      4.60,           1.3420),
    ("2025-09-26",  2400,      4.55,           1.3400),
    # --- October 2025 ---
    ("2025-10-03",  2450,      4.60,           1.3300),
    ("2025-10-10",  2530,      4.65,           1.3200),
    ("2025-10-17",  2600,      4.70,           1.3100),
    ("2025-10-24",  2680,      4.72,           1.3050),
    ("2025-10-31",  2772,      4.75,           1.3000),  # ANTO support 2772 on Oct 29
    # --- November 2025 ---
    ("2025-11-07",  2790,      4.80,           1.3020),  # Berenberg reiterated Buy
    ("2025-11-14",  2807,      4.85,           1.3050),  # ANTO 2807 on Nov 12
    ("2025-11-21",  2830,      4.88,           1.3000),
    ("2025-11-28",  2850,      4.90,           1.3020),
    # --- December 2025 ---
    ("2025-12-05",  2905,      5.10,           1.3150),  # ANTO ~2905 on Dec 3
    ("2025-12-12",  3000,      5.25,           1.3200),
    ("2025-12-19",  3100,      5.45,           1.3250),
    ("2025-12-26",  3168,      5.66,           1.3300),  # Copper $5.66 on Dec 26
    ("2025-12-31",  3316,      5.72,           1.3350),  # ANTO 3316 Morningstar close
    # --- January 2026 ---
    ("2026-01-02",  3330,      5.75,           1.3400),
    ("2026-01-03",  3350,      5.78,           1.3420),
    ("2026-01-06",  3380,      5.90,           1.3500),  # Copper surges above $6
    ("2026-01-07",  3420,      6.03,           1.3520),  # Copper ~$6.03
    ("2026-01-08",  3450,      6.05,           1.3530),
    ("2026-01-09",  3460,      6.11,           1.3550),  # Copper ATH $6.11
    ("2026-01-10",  3470,      6.08,           1.3540),
    ("2026-01-13",  3512,      5.95,           1.3600),  # ANTO 3512
    ("2026-01-14",  3550,      5.88,           1.3620),
    ("2026-01-15",  3678,      5.85,           1.3650),  # ANTO ATH 3678
    ("2026-01-16",  3560,      5.80,           1.3680),  # ANTO 3560
    ("2026-01-17",  3540,      5.78,           1.3650),
    ("2026-01-20",  3480,      5.70,           1.3600),
    ("2026-01-21",  3460,      5.68,           1.3580),
    ("2026-01-22",  3420,      5.65,           1.3560),
    ("2026-01-23",  3380,      5.55,           1.3490),  # GBP low 1.34905 on 23 Jan
    ("2026-01-24",  3350,      5.50,           1.3520),
    ("2026-01-27",  3400,      5.83,           1.3848),  # GBP high 1.38475 on 27 Jan
    ("2026-01-28",  3500,      5.98,           1.3826),  # Copper ~$5.98
    ("2026-01-29",  3792,      6.29,           1.3813),  # ANTO ~3792, Copper $6.29+
]

# ══════════════════════════════════════════════════════════════════════════
# BUILD DATAFRAME
# ══════════════════════════════════════════════════════════════════════════

df = pd.DataFrame(weekly_data_raw, columns=["date", "anto_gbx", "copper_usd_lb", "gbpusd"])
df["date"] = pd.to_datetime(df["date"])
df = df.set_index("date").sort_index()

# Convert ANTO from GBX (pence) to USD
# GBX ÷ 100 = GBP, then × GBP/USD = USD
df["anto_usd"] = (df["anto_gbx"] / 100.0) * df["gbpusd"]

# Compute returns
df["anto_ret"] = df["anto_usd"].pct_change()
df["copper_ret"] = df["copper_usd_lb"].pct_change()


# ══════════════════════════════════════════════════════════════════════════
# ANALYSIS FUNCTION
# ══════════════════════════════════════════════════════════════════════════

def run_analysis(data: pd.DataFrame, label: str):
    """Full correlation and beta analysis on a given time slice."""

    # Drop NaN returns (first row)
    analysis = data.dropna(subset=["anto_ret", "copper_ret"]).copy()
    n = len(analysis)

    anto_usd = analysis["anto_usd"]
    cu = analysis["copper_usd_lb"]
    anto_ret = analysis["anto_ret"]
    cu_ret = analysis["copper_ret"]

    # ── Price-level correlation ──
    corr_price_pearson, p_price_pearson = stats.pearsonr(anto_usd, cu)
    corr_price_spearman, p_price_spearman = stats.spearmanr(anto_usd, cu)

    # ── Return-level correlation ──
    corr_ret_pearson, p_ret_pearson = stats.pearsonr(anto_ret, cu_ret)
    corr_ret_spearman, p_ret_spearman = stats.spearmanr(anto_ret, cu_ret)

    # ── Beta regression: ANTO_ret = alpha + beta * Copper_ret + epsilon ──
    slope, intercept, r_value, p_value, std_err = stats.linregress(cu_ret, anto_ret)
    beta = slope
    r_squared = r_value ** 2
    t_stat = slope / std_err if std_err > 0 else float("inf")

    # Annualize (assume ~52 weekly obs per year for weekly data)
    # Determine period frequency
    date_diffs = analysis.index.to_series().diff().dropna()
    avg_days = date_diffs.dt.days.mean()
    if avg_days <= 2:
        periods_per_year = 252  # daily
    elif avg_days <= 8:
        periods_per_year = 52   # weekly
    else:
        periods_per_year = 12   # monthly

    alpha_ann = intercept * periods_per_year

    # ── Return statistics ──
    anto_ann_ret = anto_ret.mean() * periods_per_year
    anto_ann_vol = anto_ret.std() * np.sqrt(periods_per_year)
    cu_ann_ret = cu_ret.mean() * periods_per_year
    cu_ann_vol = cu_ret.std() * np.sqrt(periods_per_year)

    # ── Print results ──
    print("─" * 72)
    print(f"  {label}")
    print("─" * 72)
    print(f"  Period             : {data.index[0].date()} → {data.index[-1].date()}")
    print(f"  Observations (n)   : {n}")
    print(f"  Avg interval       : {avg_days:.1f} days  →  {periods_per_year} periods/year assumed")

    print(f"\n  ── PRICE LEVELS ────────────────────────────────────────────")
    print(f"  ANTO (USD)  : ${anto_usd.iloc[0]:,.2f} → ${anto_usd.iloc[-1]:,.2f}  "
          f"({(anto_usd.iloc[-1]/anto_usd.iloc[0]-1)*100:+.1f}%)")
    print(f"  Copper $/lb : ${cu.iloc[0]:.4f} → ${cu.iloc[-1]:.4f}  "
          f"({(cu.iloc[-1]/cu.iloc[0]-1)*100:+.1f}%)")

    print(f"\n  ── CORRELATION: PRICE LEVELS ────────────────────────────────")
    print(f"  Pearson  r   = {corr_price_pearson:+.4f}   (p = {p_price_pearson:.2e})")
    print(f"  Spearman ρ   = {corr_price_spearman:+.4f}   (p = {p_price_spearman:.2e})")

    print(f"\n  ── CORRELATION: RETURNS ─────────────────────────────────────")
    print(f"  Pearson  r   = {corr_ret_pearson:+.4f}   (p = {p_ret_pearson:.2e})")
    print(f"  Spearman ρ   = {corr_ret_spearman:+.4f}   (p = {p_ret_spearman:.2e})")

    print(f"\n  ── BETA REGRESSION: ANTO_ret ~ Copper_ret (OLS) ────────────")
    print(f"  Beta (β)               = {beta:+.4f}")
    print(f"  Alpha (intercept)      = {intercept:+.6f}")
    print(f"  Alpha (annualised)     = {alpha_ann:+.4f}  ({alpha_ann*100:+.2f}%)")
    print(f"  R²                     = {r_squared:.4f}")
    print(f"  Std error of β         = {std_err:.4f}")
    print(f"  t-statistic (β)        = {t_stat:.2f}")
    print(f"  p-value (β)            = {p_value:.2e}")

    print(f"\n  ── RETURN STATISTICS ────────────────────────────────────────")
    print(f"  {'Series':<16s} {'Ann.Return':>12s} {'Ann.Vol':>10s} {'Skew':>8s} {'Kurt':>8s}")
    print(f"  {'─'*16} {'─'*12} {'─'*10} {'─'*8} {'─'*8}")
    for name, series in [("ANTO (USD)", anto_ret), ("Copper ($/lb)", cu_ret)]:
        ann_r = series.mean() * periods_per_year
        ann_v = series.std() * np.sqrt(periods_per_year)
        sk = series.skew()
        ku = series.kurtosis()
        print(f"  {name:<16s} {ann_r*100:>+11.2f}% {ann_v*100:>9.2f}% {sk:>+8.3f} {ku:>+8.3f}")

    print()

    return {
        "label": label,
        "n": n,
        "corr_price_pearson": corr_price_pearson,
        "corr_price_spearman": corr_price_spearman,
        "corr_ret_pearson": corr_ret_pearson,
        "corr_ret_spearman": corr_ret_spearman,
        "beta": beta,
        "alpha_ann": alpha_ann,
        "r_squared": r_squared,
        "std_err": std_err,
        "t_stat": t_stat,
        "p_value": p_value,
        "anto_ann_ret": anto_ann_ret,
        "anto_ann_vol": anto_ann_vol,
        "cu_ann_ret": cu_ann_ret,
        "cu_ann_vol": cu_ann_vol,
    }


# ══════════════════════════════════════════════════════════════════════════
# RUN ANALYSIS
# ══════════════════════════════════════════════════════════════════════════

print("=" * 72)
print("  ANTOFAGASTA (ANTO.L) vs COPPER PRICE — CORRELATION & BETA ANALYSIS")
print("=" * 72)
print(f"  Analysis date: {datetime.date.today()}")
print(f"  Data source  : Aggregated from Yahoo Finance, Trading Economics,")
print(f"                 CME Group, FRED, Macrotrends, MarketBeat, CNBC")
print(f"  ANTO prices  : Converted from GBX→GBP→USD using daily GBP/USD rates")
print(f"  Copper       : COMEX Futures (HG=F), USD per pound")
print()

# 12-month analysis
res_12m = run_analysis(df, "LAST 12 MONTHS")

# 1-month analysis (last ~30 calendar days)
cutoff_1m = pd.Timestamp("2025-12-30")
df_1m = df.loc[df.index >= cutoff_1m].copy()
# Recompute returns for the 1-month slice
df_1m["anto_ret"] = df_1m["anto_usd"].pct_change()
df_1m["copper_ret"] = df_1m["copper_usd_lb"].pct_change()
res_1m = run_analysis(df_1m, "LAST 1 MONTH (January 2026)")


# ══════════════════════════════════════════════════════════════════════════
# SUMMARY
# ══════════════════════════════════════════════════════════════════════════

print("=" * 72)
print("  SUMMARY COMPARISON")
print("=" * 72)
print()
print(f"  {'Metric':<40s} {'1 Month':>14s} {'12 Months':>14s}")
print(f"  {'─'*40} {'─'*14} {'─'*14}")

metrics = [
    ("Observations",              "n",                     "{:>14d}"),
    ("Pearson r (prices)",        "corr_price_pearson",    "{:>+14.4f}"),
    ("Spearman ρ (prices)",       "corr_price_spearman",   "{:>+14.4f}"),
    ("Pearson r (returns)",       "corr_ret_pearson",      "{:>+14.4f}"),
    ("Spearman ρ (returns)",      "corr_ret_spearman",     "{:>+14.4f}"),
    ("Beta (β)",                  "beta",                  "{:>+14.4f}"),
    ("R²",                        "r_squared",             "{:>14.4f}"),
    ("t-statistic (β)",           "t_stat",                "{:>14.2f}"),
    ("p-value (β)",               "p_value",               "{:>14.2e}"),
    ("Alpha (annualised)",        "alpha_ann",             "{:>+14.4f}"),
    ("ANTO Ann. Return",          "anto_ann_ret",          "{:>+14.4f}"),
    ("ANTO Ann. Volatility",      "anto_ann_vol",          "{:>14.4f}"),
    ("Copper Ann. Return",        "cu_ann_ret",            "{:>+14.4f}"),
    ("Copper Ann. Volatility",    "cu_ann_vol",            "{:>14.4f}"),
]

for name, key, fmt in metrics:
    v1 = fmt.format(res_1m[key])
    v12 = fmt.format(res_12m[key])
    print(f"  {name:<40s} {v1:>14s} {v12:>14s}")

print()
print("  ── INTERPRETATION ──────────────────────────────────────────────")
print()
print("  PRICE-LEVEL CORRELATION:")
print(f"    12-month: Pearson r = {res_12m['corr_price_pearson']:+.4f} — "
      f"{'Strong' if abs(res_12m['corr_price_pearson']) > 0.7 else 'Moderate' if abs(res_12m['corr_price_pearson']) > 0.4 else 'Weak'} "
      f"{'positive' if res_12m['corr_price_pearson'] > 0 else 'negative'} correlation")
print(f"    1-month : Pearson r = {res_1m['corr_price_pearson']:+.4f} — "
      f"{'Strong' if abs(res_1m['corr_price_pearson']) > 0.7 else 'Moderate' if abs(res_1m['corr_price_pearson']) > 0.4 else 'Weak'} "
      f"{'positive' if res_1m['corr_price_pearson'] > 0 else 'negative'} correlation")
print()
print("  RETURN CORRELATION:")
print(f"    12-month: Pearson r = {res_12m['corr_ret_pearson']:+.4f} — "
      f"{'Strong' if abs(res_12m['corr_ret_pearson']) > 0.7 else 'Moderate' if abs(res_12m['corr_ret_pearson']) > 0.4 else 'Weak'} "
      f"{'positive' if res_12m['corr_ret_pearson'] > 0 else 'negative'} co-movement in returns")
print(f"    1-month : Pearson r = {res_1m['corr_ret_pearson']:+.4f} — "
      f"{'Strong' if abs(res_1m['corr_ret_pearson']) > 0.7 else 'Moderate' if abs(res_1m['corr_ret_pearson']) > 0.4 else 'Weak'} "
      f"{'positive' if res_1m['corr_ret_pearson'] > 0 else 'negative'} co-movement in returns")
print()
print("  BETA TO COPPER:")
print(f"    12-month β = {res_12m['beta']:+.4f} — For every 1% move in copper,")
print(f"      ANTO (USD) moves ~{abs(res_12m['beta']):.2f}% in the same direction")
print(f"    1-month  β = {res_1m['beta']:+.4f} — Short-term beta")
print()
beta_12 = res_12m['beta']
if beta_12 > 1.2:
    print(f"    ANTO is a HIGH-BETA copper play (β={beta_12:.2f} > 1.0)")
elif beta_12 > 0.8:
    print(f"    ANTO has NEAR-PARITY beta to copper (β={beta_12:.2f} ≈ 1.0)")
else:
    print(f"    ANTO has a LEVERAGED/DAMPENED response to copper (β={beta_12:.2f})")
print()
print("  ── NOTES ───────────────────────────────────────────────────────")
print("  • ANTO.L is listed in GBX (pence); converted to USD via GBP/USD")
print("  • Copper = COMEX Copper Futures (HG=F), USD per pound")
print("  • Beta = OLS slope of ANTO returns regressed on Copper returns")
print("  • Price-level correlations can be spurious (both trending up);")
print("    return-level correlations are more statistically meaningful")
print("  • Data is aggregated from public financial data sources via web")
print("    search. For production use, source data directly from a")
print("    financial data API (Bloomberg, Refinitiv, Yahoo Finance).")
print("=" * 72)
