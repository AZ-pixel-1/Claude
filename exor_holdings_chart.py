#!/usr/bin/env python3
"""
Exor N.V.: ADR Price vs NAV per ADR (Last 2 Years)

Blue line: Exor share price (EXO.AS) converted to USD
Red line:  NAV per share recalculated daily from listed holdings' prices,
           plus fixed "Other Assets" ($10.7B) and minus "Net Debt" ($2.4B).

Data sources: Monthly reference prices collected from Yahoo Finance, MacroTrends,
TradingEconomics, StockAnalysis, CNBC, and other public sources, then interpolated
to daily frequency.

For live data, run with internet access and yfinance:
    pip install yfinance && python exor_holdings_chart.py --live
"""

import sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np
from datetime import datetime

# ── Try live mode with yfinance if --live flag is passed ─────────────────
if "--live" in sys.argv:
    import yfinance as yf
    from datetime import timedelta

    end_date = datetime(2026, 2, 21)
    start_date = end_date - timedelta(days=730)

    holdings = {
        "RACE":   (37.8,  "USD"),
        "STLA":   (449.4, "USD"),
        "PHG":    (182.5, "USD"),
        "CNH":    (366.9, "USD"),
        "IVG.MI": (73.4,  "EUR"),
        "JUVE.MI":(247.9, "EUR"),
    }
    other_assets_m = 10_700
    net_debt_m     =  2_400
    exor_shares_m  = 39_300 / 191  # ~205.76 M

    tickers = list(holdings.keys()) + ["EXO.AS", "EURUSD=X"]
    print("Downloading live data …")
    raw = yf.download(tickers, start=start_date, end=end_date,
                      auto_adjust=True, progress=False)
    close = raw["Close"]
    eurusd = close["EURUSD=X"]
    exor_price_usd = close["EXO.AS"] * eurusd

    nav_m = pd.Series(0.0, index=close.index)
    for tk, (sh, ccy) in holdings.items():
        p = close[tk].copy()
        if ccy == "EUR":
            p = p * eurusd
        nav_m = nav_m.add(p * sh, fill_value=0)
    nav_m += other_assets_m
    nav_m -= net_debt_m
    nav_per_adr = nav_m / exor_shares_m

    df = pd.DataFrame({
        "Exor ADR Price": exor_price_usd,
        "NAV per ADR": nav_per_adr,
    }).dropna()

else:
    # ── Embedded reference data (monthly observations) ───────────────────
    # Collected Feb 2026 from public financial data sources.
    # Prices are approximate month-end closing prices.

    # Helper to build a daily-interpolated Series from monthly observations
    def _monthly_to_daily(date_price_pairs):
        dates = [datetime.strptime(d, "%Y-%m-%d") for d, _ in date_price_pairs]
        vals  = [v for _, v in date_price_pairs]
        s = pd.Series(vals, index=pd.DatetimeIndex(dates))
        s = s.resample("D").interpolate(method="linear")
        return s

    # ── RACE (Ferrari) — NYSE, USD ──────────────────────────────────────
    race_data = [
        ("2024-02-21", 375.0), ("2024-03-15", 400.0), ("2024-03-28", 408.0),
        ("2024-04-30", 393.0), ("2024-05-24", 426.0), ("2024-06-28", 415.0),
        ("2024-07-31", 432.0), ("2024-08-30", 440.0), ("2024-09-30", 436.0),
        ("2024-10-31", 445.0), ("2024-11-29", 425.0), ("2024-12-31", 419.0),
        ("2025-01-31", 448.0), ("2025-02-21", 485.0), ("2025-02-28", 490.0),
        ("2025-03-31", 465.0), ("2025-04-30", 458.0), ("2025-05-30", 482.0),
        ("2025-06-30", 500.0), ("2025-07-25", 518.0), ("2025-07-31", 510.0),
        ("2025-08-29", 478.0), ("2025-09-30", 458.0), ("2025-10-31", 418.0),
        ("2025-11-28", 388.0), ("2025-12-31", 348.0), ("2026-01-30", 335.0),
        ("2026-02-20", 375.0),
    ]

    # ── STLA (Stellantis) — NYSE, USD ───────────────────────────────────
    stla_data = [
        ("2024-02-21", 24.50), ("2024-03-21", 29.50), ("2024-03-28", 27.80),
        ("2024-04-30", 24.80), ("2024-05-15", 23.16), ("2024-05-31", 21.50),
        ("2024-06-28", 19.80), ("2024-07-31", 17.50), ("2024-08-30", 15.20),
        ("2024-09-30", 14.30), ("2024-10-31", 13.50), ("2024-11-29", 12.50),
        ("2024-12-31", 12.80), ("2025-01-31", 13.50), ("2025-02-25", 14.28),
        ("2025-03-31", 11.50), ("2025-04-08", 8.39),  ("2025-04-30", 9.80),
        ("2025-05-30", 11.00), ("2025-06-30", 12.00), ("2025-07-31", 12.50),
        ("2025-08-29", 12.80), ("2025-09-30", 13.00), ("2025-10-31", 13.50),
        ("2025-11-28", 14.00), ("2025-12-31", 14.20), ("2026-01-30", 10.80),
        ("2026-02-05", 9.54),  ("2026-02-06", 7.03),  ("2026-02-13", 7.75),
        ("2026-02-20", 7.51),
    ]

    # ── PHG (Philips) — NYSE, USD ───────────────────────────────────────
    phg_data = [
        ("2024-02-21", 21.50), ("2024-03-28", 22.80), ("2024-04-30", 23.20),
        ("2024-05-31", 25.50), ("2024-06-28", 27.50), ("2024-07-31", 26.00),
        ("2024-08-30", 25.80), ("2024-09-30", 26.50), ("2024-10-31", 24.50),
        ("2024-11-29", 23.80), ("2024-12-31", 24.00), ("2025-01-30", 28.70),
        ("2025-02-28", 29.00), ("2025-03-31", 27.50), ("2025-04-30", 26.00),
        ("2025-05-30", 27.00), ("2025-06-30", 28.50), ("2025-07-31", 30.50),
        ("2025-08-29", 28.50), ("2025-09-30", 26.50), ("2025-10-31", 24.00),
        ("2025-11-28", 22.00), ("2025-12-31", 23.10), ("2026-01-30", 27.50),
        ("2026-02-17", 31.17),
    ]

    # ── CNH (CNH Industrial) — NYSE, USD ────────────────────────────────
    cnh_data = [
        ("2024-02-21", 12.00), ("2024-03-28", 12.50), ("2024-04-30", 11.80),
        ("2024-05-31", 11.50), ("2024-06-28", 10.80), ("2024-07-31", 10.50),
        ("2024-08-30", 10.20), ("2024-09-30", 10.80), ("2024-10-31", 10.50),
        ("2024-11-29", 11.00), ("2024-12-31", 10.80), ("2025-01-31", 10.50),
        ("2025-02-28", 11.00), ("2025-03-31", 10.00), ("2025-04-30", 9.20),
        ("2025-05-30", 10.50), ("2025-06-30", 11.20), ("2025-07-31", 11.80),
        ("2025-08-29", 12.00), ("2025-09-30", 12.20), ("2025-10-31", 12.50),
        ("2025-11-28", 11.00), ("2025-12-31", 10.50), ("2026-01-12", 10.26),
        ("2026-02-20", 13.05),
    ]

    # ── IVG.MI (Iveco Group) — Milan, EUR ───────────────────────────────
    ivg_data = [
        ("2024-02-21", 10.50), ("2024-03-28", 11.20), ("2024-04-30", 11.80),
        ("2024-05-31", 12.80), ("2024-06-28", 12.00), ("2024-07-31", 11.20),
        ("2024-08-30", 11.00), ("2024-09-30", 10.20), ("2024-10-31",  9.50),
        ("2024-11-29",  9.20), ("2024-12-31",  9.50), ("2025-01-31", 11.50),
        ("2025-02-28", 13.50), ("2025-03-31", 14.80), ("2025-04-30", 16.00),
        ("2025-05-27", 20.39), ("2025-06-30", 18.50), ("2025-07-31", 18.20),
        ("2025-08-29", 17.50), ("2025-09-30", 18.00), ("2025-10-31", 18.50),
        ("2025-11-28", 18.00), ("2025-12-31", 17.50), ("2026-01-30", 18.50),
        ("2026-02-08", 18.95),
    ]

    # ── JUVE.MI (Juventus FC) — Milan, EUR ──────────────────────────────
    juve_data = [
        ("2024-02-21", 2.80), ("2024-03-28", 2.85), ("2024-04-30", 2.90),
        ("2024-05-31", 2.95), ("2024-06-28", 2.85), ("2024-07-31", 2.90),
        ("2024-08-30", 2.95), ("2024-09-30", 3.10), ("2024-10-31", 3.20),
        ("2024-11-29", 3.00), ("2024-12-31", 2.90), ("2025-01-31", 3.00),
        ("2025-02-28", 3.15), ("2025-03-31", 3.25), ("2025-04-30", 3.35),
        ("2025-05-30", 3.45), ("2025-06-30", 3.56), ("2025-07-31", 3.35),
        ("2025-08-29", 3.10), ("2025-09-23", 2.82), ("2025-10-31", 2.60),
        ("2025-11-28", 2.50), ("2025-12-31", 2.40), ("2026-01-30", 2.35),
        ("2026-02-20", 2.29),
    ]

    # ── EXO.AS (Exor N.V.) — Amsterdam Euronext, EUR ────────────────────
    exo_data = [
        ("2024-02-21", 93.00), ("2024-03-28", 96.00), ("2024-04-30", 100.50),
        ("2024-05-27", 105.40), ("2024-06-28", 98.50), ("2024-07-31", 96.00),
        ("2024-08-30", 94.00), ("2024-09-30", 96.00), ("2024-10-31", 93.50),
        ("2024-11-29", 90.50), ("2024-12-31", 88.50), ("2025-01-31", 86.00),
        ("2025-02-28", 91.50), ("2025-03-31", 89.00), ("2025-04-30", 87.00),
        ("2025-05-30", 93.00), ("2025-06-30", 96.00), ("2025-07-31", 98.00),
        ("2025-08-29", 93.50), ("2025-09-30", 88.00), ("2025-10-31", 82.00),
        ("2025-11-28", 77.50), ("2025-12-31", 74.50), ("2026-01-13", 73.60),
        ("2026-01-30", 73.80), ("2026-02-20", 74.05),
    ]

    # ── EUR/USD exchange rate ───────────────────────────────────────────
    # 2024: avg 1.0822, high 1.1203, low 1.0350, year down -6.23%
    # 2025: avg 1.1306, high 1.1868 (Sep 16), low 1.0257 (Jan 12), year up +13.34%
    # Jan 27, 2026: peaked ~1.2016; Feb 20, 2026: ~1.1785
    eurusd_data = [
        ("2024-02-21", 1.082), ("2024-03-28", 1.079), ("2024-04-30", 1.072),
        ("2024-05-31", 1.085), ("2024-06-28", 1.071), ("2024-07-31", 1.082),
        ("2024-08-30", 1.108), ("2024-09-30", 1.114), ("2024-10-31", 1.088),
        ("2024-11-29", 1.058), ("2024-12-31", 1.035), ("2025-01-12", 1.026),
        ("2025-01-31", 1.036), ("2025-02-28", 1.042), ("2025-03-31", 1.082),
        ("2025-04-30", 1.133), ("2025-05-30", 1.137), ("2025-06-30", 1.143),
        ("2025-07-31", 1.148), ("2025-08-29", 1.107), ("2025-09-16", 1.187),
        ("2025-09-30", 1.175), ("2025-10-31", 1.155), ("2025-11-28", 1.140),
        ("2025-12-31", 1.135), ("2026-01-27", 1.200), ("2026-01-31", 1.185),
        ("2026-02-20", 1.178),
    ]

    # ── Build daily-interpolated series ──────────────────────────────────
    race  = _monthly_to_daily(race_data)
    stla  = _monthly_to_daily(stla_data)
    phg   = _monthly_to_daily(phg_data)
    cnh   = _monthly_to_daily(cnh_data)
    ivg   = _monthly_to_daily(ivg_data)    # EUR
    juve  = _monthly_to_daily(juve_data)   # EUR
    exo   = _monthly_to_daily(exo_data)    # EUR
    eurusd = _monthly_to_daily(eurusd_data)

    # Align all series to a common date index (business days only)
    idx = pd.bdate_range(start="2024-02-21", end="2026-02-20")
    race   = race.reindex(idx).interpolate()
    stla   = stla.reindex(idx).interpolate()
    phg    = phg.reindex(idx).interpolate()
    cnh    = cnh.reindex(idx).interpolate()
    ivg    = ivg.reindex(idx).interpolate()
    juve   = juve.reindex(idx).interpolate()
    exo    = exo.reindex(idx).interpolate()
    eurusd = eurusd.reindex(idx).interpolate()

    # Holdings (millions of shares owned)
    holdings_info = {
        "RACE":   (race,  37.8,  "USD"),
        "STLA":   (stla,  449.4, "USD"),
        "PHG":    (phg,   182.5, "USD"),
        "CNH":    (cnh,   366.9, "USD"),
        "IVG.MI": (ivg,   73.4,  "EUR"),
        "JUVE.MI":(juve,  247.9, "EUR"),
    }
    other_assets_m = 10_700   # $10.7 B in millions
    net_debt_m     =  2_400   # $2.4 B in millions
    exor_shares_m  = 39_300 / 191  # ~205.76 M ADR-equivalent shares

    # Exor ADR price = EXO.AS (EUR) × EUR/USD
    exor_price_usd = exo * eurusd

    # NAV (in $ millions)
    nav_m = pd.Series(0.0, index=idx)
    for name, (prices, shares_m, ccy) in holdings_info.items():
        p = prices.copy()
        if ccy == "EUR":
            p = p * eurusd
        nav_m += p * shares_m

    nav_m += other_assets_m
    nav_m -= net_debt_m
    nav_per_adr = nav_m / exor_shares_m

    df = pd.DataFrame({
        "Exor ADR Price": exor_price_usd,
        "NAV per ADR": nav_per_adr,
    }).dropna()

# ── Print summary ────────────────────────────────────────────────────────
print(f"Data points: {len(df)} trading days")
print(f"Latest Exor ADR Price : ${df['Exor ADR Price'].iloc[-1]:,.2f}")
print(f"Latest NAV per ADR    : ${df['NAV per ADR'].iloc[-1]:,.2f}")
discount = (1 - df["Exor ADR Price"].iloc[-1] / df["NAV per ADR"].iloc[-1]) * 100
print(f"Latest discount       : {discount:.1f}%")

# ── Plot ─────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 7))

ax.plot(df.index, df["Exor ADR Price"], color="#1f77b4", linewidth=1.6,
        label="Exor ADR Price (USD)")
ax.plot(df.index, df["NAV per ADR"],    color="#d62728", linewidth=1.6,
        label="NAV per ADR (USD)")

# Shade the discount area
ax.fill_between(df.index, df["Exor ADR Price"], df["NAV per ADR"],
                where=df["NAV per ADR"] > df["Exor ADR Price"],
                alpha=0.10, color="red", label="Discount")

ax.set_ylabel("USD", fontsize=13)
ax.set_title("Exor: ADR Price vs NAV per ADR  (Feb 2024 \u2013 Feb 2026)",
             fontsize=15, fontweight="bold")
ax.legend(loc="upper left", fontsize=11)
ax.grid(True, alpha=0.3)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)
plt.tight_layout()

out_path = "exor_holdings_chart.png"
fig.savefig(out_path, dpi=150)
print(f"\nChart saved \u2192 {out_path}")
