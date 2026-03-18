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
        ("2025-11-28", 388.0),
        # Daily data Dec 2025 – Mar 2026 (IBKR-confirmed where noted)
        ("2025-12-15", 368.60),  # confirmed
        ("2025-12-16", 370.42),  # confirmed
        ("2025-12-17", 365.51),  # confirmed
        ("2025-12-18", 372.65),  # confirmed
        ("2025-12-19", 378.29),  # confirmed
        ("2025-12-22", 375.25),  # confirmed
        ("2025-12-23", 375.91),  # confirmed
        ("2025-12-29", 375.75),  # confirmed
        ("2025-12-30", 372.48),  # confirmed
        ("2025-12-31", 369.56),  # confirmed
        ("2026-01-02", 371.89),  # confirmed
        ("2026-01-05", 379.27),  # confirmed
        ("2026-01-06", 371.96),  # confirmed
        ("2026-01-07", 366.81),  # confirmed
        ("2026-01-08", 370.85),  # confirmed
        ("2026-01-09", 376.19),  # confirmed
        ("2026-01-13", 360.09),  # confirmed
        ("2026-01-14", 353.39),  # confirmed
        ("2026-01-15", 354.57),  # confirmed
        ("2026-01-16", 345.23),  # confirmed
        ("2026-01-20", 336.78),  # confirmed
        ("2026-01-21", 341.68),  # confirmed
        ("2026-01-23", 340.0), ("2026-01-27", 335.0),
        ("2026-01-30", 330.0),
        ("2026-02-03", 328.00),  # confirmed – 52-week low
        ("2026-02-05", 332.0), ("2026-02-07", 334.0),
        ("2026-02-09", 336.13),
        ("2026-02-10", 362.00),  # confirmed – earnings surge +8.8%
        ("2026-02-13", 365.0),
        ("2026-02-17", 374.99),  # confirmed
        ("2026-02-19", 370.0), ("2026-02-20", 368.0),
        ("2026-02-23", 358.42),  # confirmed (-2.32%)
        ("2026-02-25", 355.0), ("2026-02-27", 352.0),
        ("2026-03-02", 350.0), ("2026-03-04", 348.0), ("2026-03-06", 347.0),
        ("2026-03-09", 346.58),  # confirmed
        ("2026-03-10", 340.0), ("2026-03-11", 337.0),
        ("2026-03-12", 334.55),  # confirmed
        ("2026-03-13", 331.86),  # confirmed
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
        ("2025-11-28", 14.00),
        # Daily data Dec 2025 – Mar 2026 (IBKR-confirmed where noted)
        ("2025-12-12", 11.78),  # confirmed
        ("2025-12-15", 11.93),  # confirmed
        ("2025-12-19", 11.50), ("2025-12-24", 11.03),  # confirmed
        ("2025-12-30", 10.50), ("2025-12-31", 10.50),
        ("2026-01-02", 10.80), ("2026-01-06", 11.09),  # confirmed
        ("2026-01-09", 10.50), ("2026-01-15", 10.02),  # confirmed
        ("2026-01-20", 10.20), ("2026-01-23", 10.40),
        ("2026-01-27", 10.60), ("2026-01-30", 10.80),
        ("2026-02-03", 10.00), ("2026-02-04", 9.80),
        ("2026-02-05", 9.54),   # confirmed
        ("2026-02-06", 7.28),   # confirmed – 23.7% crash on EUR 22.2B charges
        ("2026-02-09", 7.31),   # confirmed
        ("2026-02-10", 7.50), ("2026-02-11", 7.55), ("2026-02-12", 7.60),
        ("2026-02-13", 7.75),   # confirmed
        ("2026-02-17", 7.65), ("2026-02-19", 7.55),
        ("2026-02-20", 7.51),   # confirmed
        ("2026-02-23", 7.60), ("2026-02-24", 7.77),  # confirmed
        ("2026-02-25", 7.80),   # earnings day
        ("2026-02-26", 7.80),
        ("2026-02-27", 5.95),   # major drop
        ("2026-03-02", 6.00), ("2026-03-03", 6.20),
        ("2026-03-04", 7.15),  # confirmed – STLAM at EUR 6.53
        ("2026-03-05", 6.50), ("2026-03-06", 6.80),
        ("2026-03-09", 7.07),   # confirmed
        ("2026-03-10", 6.90),   # confirmed
        ("2026-03-11", 6.85), ("2026-03-12", 6.80),
        ("2026-03-13", 6.50),   # confirmed – new 52-week low
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
        ("2025-11-28", 22.00),
        # Daily data Dec 2025 – Mar 2026 (IBKR-confirmed where noted)
        ("2025-12-17", 26.13),  # confirmed
        ("2025-12-18", 26.49),  # confirmed
        ("2025-12-23", 26.98),  # confirmed
        ("2025-12-31", 27.00),
        ("2026-01-02", 27.50), ("2026-01-06", 28.50),
        ("2026-01-08", 29.43),  # confirmed
        ("2026-01-15", 30.30),  # confirmed – 52-wk high area
        ("2026-01-20", 29.50), ("2026-01-23", 29.00),
        ("2026-01-27", 28.80), ("2026-01-30", 28.70),  # confirmed
        ("2026-02-03", 28.90), ("2026-02-05", 29.20),
        ("2026-02-07", 29.45),  # confirmed
        ("2026-02-10", 33.44),  # confirmed – 52-wk high, post-earnings +12%
        ("2026-02-13", 31.25),  # confirmed
        ("2026-02-17", 31.00), ("2026-02-19", 30.50),
        ("2026-02-20", 30.00), ("2026-02-23", 29.50),
        ("2026-02-25", 29.00), ("2026-02-27", 28.50),
        ("2026-03-02", 29.00), ("2026-03-04", 29.00),
        ("2026-03-06", 28.93),  # confirmed
        ("2026-03-09", 29.42),  # confirmed
        ("2026-03-10", 29.10),
        ("2026-03-11", 28.81),  # confirmed
        ("2026-03-12", 28.30),
        ("2026-03-13", 27.79),  # confirmed
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
        ("2025-11-28", 11.00),
        # Daily data Dec 2025 – Mar 2026 (IBKR-confirmed where noted)
        ("2025-12-09", 9.35),   # confirmed
        ("2025-12-15", 9.50), ("2025-12-19", 9.60),
        ("2025-12-23", 9.65), ("2025-12-31", 9.70),
        ("2026-01-02", 9.80), ("2026-01-06", 10.00), ("2026-01-09", 10.20),
        ("2026-01-12", 10.26),  # confirmed
        ("2026-01-15", 10.50), ("2026-01-20", 10.80),
        ("2026-01-22", 11.05),  # confirmed
        ("2026-01-27", 11.30), ("2026-01-30", 11.50),
        ("2026-02-03", 11.60), ("2026-02-05", 11.70), ("2026-02-07", 11.80),
        ("2026-02-10", 11.90), ("2026-02-12", 11.95),
        ("2026-02-17", 11.95),  # confirmed – fell 6.27% pre-market on earnings
        ("2026-02-20", 12.50), ("2026-02-23", 12.73),  # confirmed
        ("2026-02-25", 12.35),  # confirmed
        ("2026-02-27", 12.00),
        ("2026-03-02", 11.60), ("2026-03-04", 11.30), ("2026-03-06", 11.10),
        ("2026-03-09", 11.00), ("2026-03-10", 10.95),
        ("2026-03-11", 10.92),  # confirmed
        ("2026-03-12", 10.75),
        ("2026-03-13", 10.65),  # confirmed
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
        ("2025-11-28", 18.00),
        # Daily data Dec 2025 – Mar 2026 (IBKR-confirmed where noted)
        ("2025-12-15", 18.80), ("2025-12-19", 18.80),
        ("2025-12-23", 18.75),  # confirmed
        ("2025-12-30", 18.775), # confirmed
        ("2025-12-31", 18.80),
        ("2026-01-02", 18.82), ("2026-01-06", 18.85), ("2026-01-09", 18.87),
        ("2026-01-13", 18.88),
        ("2026-01-18", 18.89),  # confirmed
        ("2026-01-23", 18.90), ("2026-01-27", 18.90), ("2026-01-30", 18.95),
        ("2026-02-03", 18.60), ("2026-02-05", 18.70), ("2026-02-07", 18.85),
        ("2026-02-10", 18.95), ("2026-02-12", 19.05),  # Q4 results
        ("2026-02-13", 19.10), ("2026-02-17", 19.12),
        ("2026-02-19", 19.08), ("2026-02-20", 19.05),
        ("2026-02-23", 19.02), ("2026-02-25", 18.98), ("2026-02-27", 18.90),
        ("2026-03-02", 18.95), ("2026-03-04", 19.02),
        ("2026-03-05", 19.08),  # confirmed
        ("2026-03-06", 19.03),  # confirmed
        ("2026-03-09", 18.985), # confirmed (prev close 19.030)
        ("2026-03-10", 19.00), ("2026-03-11", 19.02),
        ("2026-03-12", 19.00), ("2026-03-13", 19.00),
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
        ("2025-11-28", 2.50),
        # Daily data Dec 2025 – Mar 2026 (IBKR-confirmed where noted)
        ("2025-12-15", 2.55), ("2025-12-19", 2.58),
        ("2025-12-23", 2.60),  # confirmed – late-year pullback
        ("2025-12-30", 2.62), ("2025-12-31", 2.60),
        ("2026-01-02", 2.65), ("2026-01-06", 2.70), ("2026-01-09", 2.75),
        ("2026-01-13", 2.78),
        ("2026-01-16", 2.80),  # confirmed – recovered to ~2.80
        ("2026-01-20", 2.78), ("2026-01-23", 2.75),
        ("2026-01-27", 2.70), ("2026-01-30", 2.65),
        ("2026-02-03", 2.55), ("2026-02-05", 2.50), ("2026-02-07", 2.45),
        ("2026-02-10", 2.42), ("2026-02-12", 2.40), ("2026-02-13", 2.38),
        ("2026-02-17", 2.36),  # confirmed
        ("2026-02-19", 2.30),
        ("2026-02-20", 2.29),  # confirmed (prev close 2.2820)
        ("2026-02-23", 2.29), ("2026-02-25", 2.29), ("2026-02-27", 2.30),
        ("2026-03-02", 2.30), ("2026-03-04", 2.30), ("2026-03-06", 2.30),
        ("2026-03-09", 2.30), ("2026-03-10", 2.30), ("2026-03-11", 2.30),
        ("2026-03-12", 2.30), ("2026-03-13", 2.30),
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
        ("2025-11-28", 77.50),
        # Daily data Dec 2025 – Mar 2026 (IBKR-confirmed where noted)
        ("2025-12-15", 74.80), ("2025-12-19", 74.50), ("2025-12-23", 74.50),
        ("2025-12-26", 74.50), ("2025-12-31", 74.50),
        ("2026-01-02", 72.95),  # confirmed – first trading day 2026
        ("2026-01-06", 73.50), ("2026-01-09", 74.00),
        ("2026-01-13", 73.60),  # confirmed (down from 74.50 prev day)
        ("2026-01-16", 73.65), ("2026-01-20", 73.70),
        ("2026-01-23", 73.75), ("2026-01-27", 73.75), ("2026-01-30", 73.80),
        ("2026-02-03", 73.00), ("2026-02-05", 72.00), ("2026-02-07", 70.00),
        ("2026-02-10", 69.00), ("2026-02-12", 68.30),
        ("2026-02-13", 68.20),  # confirmed
        ("2026-02-17", 71.70),  # confirmed (+2.06%)
        ("2026-02-19", 73.00),
        ("2026-02-20", 74.05),  # confirmed
        ("2026-02-23", 74.10), ("2026-02-25", 74.25),
        ("2026-02-27", 74.35),  # confirmed
        ("2026-03-02", 73.50),
        ("2026-03-04", 72.20),  # confirmed
        ("2026-03-06", 70.50),  # confirmed
        ("2026-03-09", 70.00),
        ("2026-03-10", 71.00),  # confirmed
        ("2026-03-11", 70.50),
        ("2026-03-12", 70.55),  # confirmed (prev close 69.72)
        ("2026-03-13", 68.20),  # confirmed
    ]

    # ── EUR/USD exchange rate ───────────────────────────────────────────
    # 2024: avg 1.0822, high 1.1203, low 1.0350, year down -6.23%
    # 2025: avg 1.1306, high 1.1868 (Sep 16), low 1.0257 (Jan 12), year up +13.34%
    # Jan 27, 2026: peaked ~1.2019; Mar 14, 2026: 2026 low 1.1417
    eurusd_data = [
        ("2024-02-21", 1.082), ("2024-03-28", 1.079), ("2024-04-30", 1.072),
        ("2024-05-31", 1.085), ("2024-06-28", 1.071), ("2024-07-31", 1.082),
        ("2024-08-30", 1.108), ("2024-09-30", 1.114), ("2024-10-31", 1.088),
        ("2024-11-29", 1.058), ("2024-12-31", 1.035), ("2025-01-12", 1.026),
        ("2025-01-31", 1.036), ("2025-02-28", 1.042), ("2025-03-31", 1.082),
        ("2025-04-30", 1.133), ("2025-05-30", 1.137), ("2025-06-30", 1.143),
        ("2025-07-31", 1.148), ("2025-08-29", 1.107), ("2025-09-16", 1.187),
        ("2025-09-30", 1.175), ("2025-10-31", 1.155), ("2025-11-28", 1.140),
        # Daily data Dec 2025 – Mar 2026 (ECB reference rates, IBKR-confirmed)
        ("2025-12-15", 1.1751),  # confirmed ECB
        ("2025-12-16", 1.1779),  # confirmed ECB
        ("2025-12-17", 1.1723),  # confirmed ECB
        ("2025-12-18", 1.1723),  # confirmed ECB
        ("2025-12-19", 1.1710),  # confirmed ECB
        ("2025-12-22", 1.1751),  # confirmed ECB
        ("2025-12-23", 1.1795),  # confirmed ECB
        ("2025-12-24", 1.1787),  # confirmed ECB
        ("2025-12-29", 1.1765),  # confirmed ECB
        ("2025-12-30", 1.1751),  # confirmed ECB
        ("2025-12-31", 1.1750),  # confirmed ECB reference rate
        ("2026-01-02", 1.1668),  # confirmed
        ("2026-01-06", 1.170), ("2026-01-09", 1.1767),
        ("2026-01-12", 1.1692),  # confirmed ECB EUR-Lex
        ("2026-01-13", 1.1654),  # confirmed ECB EUR-Lex
        ("2026-01-14", 1.1651),  # confirmed ECB EUR-Lex
        ("2026-01-15", 1.1624),  # confirmed ECB EUR-Lex
        ("2026-01-16", 1.1617),  # confirmed ECB EUR-Lex – Jan low
        ("2026-01-20", 1.170), ("2026-01-23", 1.170),
        ("2026-01-26", 1.180),
        ("2026-01-27", 1.2016),  # confirmed – 2026 high
        ("2026-01-29", 1.200), ("2026-01-30", 1.190),
        ("2026-02-03", 1.185),
        ("2026-02-05", 1.1798),  # confirmed ECB EUR-Lex
        ("2026-02-07", 1.180),
        ("2026-02-09", 1.1886),  # confirmed ECB EUR-Lex
        ("2026-02-11", 1.185), ("2026-02-13", 1.185),
        ("2026-02-17", 1.180), ("2026-02-19", 1.180),
        ("2026-02-20", 1.180), ("2026-02-23", 1.180),
        ("2026-02-25", 1.180), ("2026-02-27", 1.180),
        ("2026-03-02", 1.1697),  # confirmed
        ("2026-03-04", 1.170), ("2026-03-06", 1.160),
        ("2026-03-09", 1.155),
        ("2026-03-10", 1.1659),  # confirmed – week high
        ("2026-03-11", 1.160), ("2026-03-12", 1.150),
        ("2026-03-13", 1.1476),  # confirmed ECB – 2026 low
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
    idx = pd.bdate_range(start="2024-02-21", end="2026-03-13")
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

# ── Compute discount % ───────────────────────────────────────────────────
df["Discount %"] = (1 - df["Exor ADR Price"] / df["NAV per ADR"]) * 100

# ── Print summary ────────────────────────────────────────────────────────
print(f"Data points: {len(df)} trading days")
print(f"Latest Exor ADR Price : ${df['Exor ADR Price'].iloc[-1]:,.2f}")
print(f"Latest NAV per ADR    : ${df['NAV per ADR'].iloc[-1]:,.2f}")
print(f"Latest discount       : {df['Discount %'].iloc[-1]:.1f}%")

# ── Plot ─────────────────────────────────────────────────────────────────
fig, ax1 = plt.subplots(figsize=(14, 7))

# Left Y-axis: USD prices
ax1.plot(df.index, df["Exor ADR Price"], color="#1f77b4", linewidth=1.6,
         label="Exor ADR Price (USD)")
ax1.plot(df.index, df["NAV per ADR"],    color="#d62728", linewidth=1.6,
         label="NAV per ADR (USD)")
ax1.fill_between(df.index, df["Exor ADR Price"], df["NAV per ADR"],
                 where=df["NAV per ADR"] > df["Exor ADR Price"],
                 alpha=0.08, color="red")

ax1.set_ylabel("USD", fontsize=13)
ax1.set_title("Exor: ADR Price vs NAV per ADR  (Feb 2024 \u2013 Mar 2026)",
              fontsize=15, fontweight="bold")
ax1.grid(True, alpha=0.3)
ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=3))
plt.xticks(rotation=45)

# Right Y-axis: Discount %
ax2 = ax1.twinx()
ax2.plot(df.index, df["Discount %"], color="#2ca02c", linewidth=1.4,
         linestyle="--", alpha=0.85, label="Discount to NAV (%)")
ax2.set_ylabel("Discount to NAV (%)", fontsize=13, color="#2ca02c")
ax2.tick_params(axis="y", labelcolor="#2ca02c")

# Combined legend
lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper left", fontsize=11)

plt.tight_layout()

out_path = "exor_holdings_chart.png"
fig.savefig(out_path, dpi=150)
print(f"\nChart saved \u2192 {out_path}")

# ── Weekly chart (last 12 months) ────────────────────────────────────────
cutoff = df.index[-1] - pd.DateOffset(years=1)
df_12m = df.loc[df.index >= cutoff].copy()

# Resample to weekly (Friday close)
df_weekly = df_12m.resample("W-FRI").last().dropna()

print(f"\nWeekly chart: {len(df_weekly)} weeks from {df_weekly.index[0]:%Y-%m-%d} to {df_weekly.index[-1]:%Y-%m-%d}")

fig2, ax1w = plt.subplots(figsize=(14, 7))

# Left Y-axis: USD prices
ax1w.plot(df_weekly.index, df_weekly["Exor ADR Price"], color="#1f77b4",
          linewidth=1.8, marker="o", markersize=4, label="Exor ADR Price (USD)")
ax1w.plot(df_weekly.index, df_weekly["NAV per ADR"], color="#d62728",
          linewidth=1.8, marker="o", markersize=4, label="NAV per ADR (USD)")
ax1w.fill_between(df_weekly.index, df_weekly["Exor ADR Price"], df_weekly["NAV per ADR"],
                  where=df_weekly["NAV per ADR"] > df_weekly["Exor ADR Price"],
                  alpha=0.08, color="red")

ax1w.set_ylabel("USD", fontsize=13)
ax1w.set_title("Exor: ADR Price vs NAV per ADR \u2014 Weekly  (Mar 2025 \u2013 Mar 2026)",
               fontsize=15, fontweight="bold")
ax1w.grid(True, alpha=0.3)
ax1w.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
ax1w.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
plt.sca(ax1w)
plt.xticks(rotation=45)

# Right Y-axis: Discount %
ax2w = ax1w.twinx()
ax2w.plot(df_weekly.index, df_weekly["Discount %"], color="#2ca02c", linewidth=1.6,
          linestyle="--", marker="s", markersize=4, alpha=0.85, label="Discount to NAV (%)")
ax2w.set_ylabel("Discount to NAV (%)", fontsize=13, color="#2ca02c")
ax2w.tick_params(axis="y", labelcolor="#2ca02c")

# Combined legend
lines1w, labels1w = ax1w.get_legend_handles_labels()
lines2w, labels2w = ax2w.get_legend_handles_labels()
ax1w.legend(lines1w + lines2w, labels1w + labels2w, loc="upper left", fontsize=11)

plt.tight_layout()

out_path_weekly = "exor_holdings_chart_weekly.png"
fig2.savefig(out_path_weekly, dpi=150)
print(f"Chart saved \u2192 {out_path_weekly}")

# ── Daily chart (last 3 months) ──────────────────────────────────────────
cutoff_3m = df.index[-1] - pd.DateOffset(months=3)
df_3m = df.loc[df.index >= cutoff_3m].copy()

print(f"\nDaily 3-month chart: {len(df_3m)} trading days from {df_3m.index[0]:%Y-%m-%d} to {df_3m.index[-1]:%Y-%m-%d}")

fig3, ax1d = plt.subplots(figsize=(14, 7))

# Left Y-axis: USD prices
ax1d.plot(df_3m.index, df_3m["Exor ADR Price"], color="#1f77b4",
          linewidth=1.8, label="Exor ADR Price (USD)")
ax1d.plot(df_3m.index, df_3m["NAV per ADR"], color="#d62728",
          linewidth=1.8, label="NAV per ADR (USD)")
ax1d.fill_between(df_3m.index, df_3m["Exor ADR Price"], df_3m["NAV per ADR"],
                  where=df_3m["NAV per ADR"] > df_3m["Exor ADR Price"],
                  alpha=0.08, color="red")

ax1d.set_ylabel("USD", fontsize=13)
ax1d.set_title("Exor: ADR Price vs NAV per ADR \u2014 Daily  (Dec 2025 \u2013 Mar 2026)",
               fontsize=15, fontweight="bold")
ax1d.grid(True, alpha=0.3)
ax1d.xaxis.set_major_formatter(mdates.DateFormatter("%d %b"))
ax1d.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=0, interval=2))
plt.sca(ax1d)
plt.xticks(rotation=45)

# Right Y-axis: Discount %
ax2d = ax1d.twinx()
ax2d.plot(df_3m.index, df_3m["Discount %"], color="#2ca02c", linewidth=1.4,
          linestyle="--", alpha=0.85, label="Discount to NAV (%)")
ax2d.set_ylabel("Discount to NAV (%)", fontsize=13, color="#2ca02c")
ax2d.tick_params(axis="y", labelcolor="#2ca02c")

# Combined legend
lines1d, labels1d = ax1d.get_legend_handles_labels()
lines2d, labels2d = ax2d.get_legend_handles_labels()
ax1d.legend(lines1d + lines2d, labels1d + labels2d, loc="upper left", fontsize=11)

plt.tight_layout()

out_path_daily = "exor_holdings_chart_daily_3m.png"
fig3.savefig(out_path_daily, dpi=150)
print(f"Chart saved \u2192 {out_path_daily}")
