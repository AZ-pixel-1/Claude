#!/usr/bin/env python3
"""
Interactive Brokers Connectivity Checker
=========================================
Tests connection to IB Client Portal API via IBeam Docker container.

Usage:
    python check_ib_connectivity.py              # Run all checks
    python check_ib_connectivity.py --status     # Auth status only
    python check_ib_connectivity.py --quotes AAPL MSFT  # Market data
"""

import argparse
import json
import sys
import time
import urllib3

import requests

# IBeam uses a self-signed cert — suppress warnings for localhost
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_URL = "https://localhost:5000/v1/api"
TIMEOUT = 15


def api_get(endpoint: str, params: dict | None = None) -> dict | list | None:
    """Make a GET request to the IB Client Portal API."""
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.get(url, params=params, verify=False, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        print(f"  [FAIL] Cannot connect to {url}")
        print("         Is IBeam running?  docker compose up -d")
        return None
    except requests.HTTPError as e:
        print(f"  [FAIL] HTTP {resp.status_code}: {e}")
        return None
    except requests.JSONDecodeError:
        # Some endpoints return empty body on success
        return {"_raw_status": resp.status_code, "_raw_text": resp.text}


def api_post(endpoint: str, payload: dict | None = None) -> dict | list | None:
    """Make a POST request to the IB Client Portal API."""
    url = f"{BASE_URL}{endpoint}"
    try:
        resp = requests.post(url, json=payload, verify=False, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        print(f"  [FAIL] Cannot connect to {url}")
        return None
    except requests.HTTPError as e:
        print(f"  [FAIL] HTTP {resp.status_code}: {e}")
        return None
    except requests.JSONDecodeError:
        return {"_raw_status": resp.status_code, "_raw_text": resp.text}


# ─── Check Functions ────────────────────────────────────────────────────


def check_auth_status() -> bool:
    """Check if authenticated to IB."""
    print("\n── Authentication Status ──")
    data = api_post("/iserver/auth/status")
    if data is None:
        return False

    authenticated = data.get("authenticated", False)
    connected = data.get("connected", False)
    competing = data.get("competing", False)

    status = "OK" if authenticated else "FAIL"
    print(f"  [{status}] Authenticated: {authenticated}")
    print(f"  [INFO] Connected: {connected}")
    if competing:
        print("  [WARN] Competing session detected — another client is logged in")

    return authenticated


def check_accounts() -> str | None:
    """List brokerage accounts and return the first account ID."""
    print("\n── Accounts ──")
    data = api_get("/iserver/accounts")
    if data is None:
        return None

    accounts = data.get("accounts", [])
    if not accounts:
        print("  [FAIL] No accounts found")
        return None

    for acct in accounts:
        print(f"  [OK] Account: {acct}")

    return accounts[0]


def check_account_summary(account_id: str) -> bool:
    """Fetch account summary (balances, NAV, etc.)."""
    print(f"\n── Account Summary ({account_id}) ──")
    data = api_get(f"/portfolio/{account_id}/summary")
    if data is None:
        return False

    key_fields = [
        ("netliquidation", "Net Liquidation"),
        ("totalcashvalue", "Total Cash"),
        ("grosspositionvalue", "Gross Position Value"),
        ("availablefunds", "Available Funds"),
        ("buyingpower", "Buying Power"),
    ]

    for field, label in key_fields:
        info = data.get(field, {})
        amount = info.get("amount", "N/A")
        currency = info.get("currency", "")
        if amount != "N/A":
            print(f"  {label:<24s}: {amount:>14,.2f} {currency}")
        else:
            print(f"  {label:<24s}: {amount}")

    return True


def check_positions(account_id: str) -> bool:
    """Fetch current positions."""
    print(f"\n── Positions ({account_id}) ──")
    # Must call /portfolio/accounts first to initialize
    api_get("/portfolio/accounts")
    time.sleep(0.5)

    data = api_get(f"/portfolio/{account_id}/positions/0")
    if data is None:
        return False

    if not data or (isinstance(data, dict) and "_raw_status" in data):
        print("  [INFO] No open positions")
        return True

    print(f"  {'Symbol':<10s} {'Qty':>10s} {'Avg Cost':>12s} {'Mkt Value':>12s} {'P&L':>12s}")
    print(f"  {'─'*10} {'─'*10} {'─'*12} {'─'*12} {'─'*12}")
    for pos in data:
        symbol = pos.get("contractDesc", "?")
        qty = pos.get("position", 0)
        avg_cost = pos.get("avgCost", 0)
        mkt_value = pos.get("mktValue", 0)
        pnl = pos.get("unrealizedPnl", 0)
        print(f"  {symbol:<10s} {qty:>10,.1f} {avg_cost:>12,.2f} {mkt_value:>12,.2f} {pnl:>+12,.2f}")

    return True


def check_market_data(symbols: list[str]) -> bool:
    """Fetch live/delayed quotes for given symbols."""
    print(f"\n── Market Data ({', '.join(symbols)}) ──")

    # Step 1: Search for conids
    conids = []
    for symbol in symbols:
        data = api_get(f"/iserver/secdef/search", params={"symbol": symbol})
        if data and isinstance(data, list) and len(data) > 0:
            conid = data[0].get("conid")
            if conid:
                conids.append((symbol, conid))
                print(f"  [OK] {symbol} → conid {conid}")
            else:
                print(f"  [FAIL] No conid for {symbol}")
        else:
            print(f"  [FAIL] Symbol search failed for {symbol}")

    if not conids:
        return False

    # Step 2: Request snapshot quotes
    conid_str = ",".join(str(c) for _, c in conids)
    # Fields: 31=last, 84=bid, 85=ask, 86=high, 87=low, 7295=open
    fields = "31,84,85,86,87,7295"

    # First call initiates the subscription; second call gets data
    api_get(f"/iserver/marketdata/snapshot", params={"conids": conid_str, "fields": fields})
    time.sleep(2)
    data = api_get(f"/iserver/marketdata/snapshot", params={"conids": conid_str, "fields": fields})

    if data is None:
        return False

    print(f"\n  {'Symbol':<8s} {'Last':>10s} {'Bid':>10s} {'Ask':>10s} {'High':>10s} {'Low':>10s}")
    print(f"  {'─'*8} {'─'*10} {'─'*10} {'─'*10} {'─'*10} {'─'*10}")

    for quote in data if isinstance(data, list) else [data]:
        sym = quote.get("55", "?")  # field 55 = symbol
        last = quote.get("31", "N/A")
        bid = quote.get("84", "N/A")
        ask = quote.get("85", "N/A")
        high = quote.get("86", "N/A")
        low = quote.get("87", "N/A")

        def fmt(v):
            if isinstance(v, (int, float)):
                return f"{v:>10,.2f}"
            return f"{str(v):>10s}"

        print(f"  {sym:<8s} {fmt(last)} {fmt(bid)} {fmt(ask)} {fmt(high)} {fmt(low)}")

    return True


def check_server_time() -> bool:
    """Check IB server time (basic connectivity test)."""
    print("\n── Server Info ──")
    data = api_get("/one/user")
    if data is None:
        # Try alternate endpoint
        data = api_get("/iserver/auth/status")
        if data is None:
            return False

    if isinstance(data, dict):
        for key in ["username", "accountId", "ispaper"]:
            if key in data:
                print(f"  {key}: {data[key]}")

    return True


# ─── Main ───────────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Check IB connectivity via IBeam")
    parser.add_argument("--status", action="store_true", help="Auth status only")
    parser.add_argument("--quotes", nargs="+", metavar="SYM", help="Fetch quotes for symbols")
    parser.add_argument("--url", default=BASE_URL, help=f"API base URL (default: {BASE_URL})")
    args = parser.parse_args()

    global BASE_URL
    BASE_URL = args.url

    print("=" * 60)
    print("  IB Client Portal API — Connectivity Check")
    print("=" * 60)

    # Always check auth first
    authenticated = check_auth_status()
    if not authenticated:
        print("\n[FAIL] Not authenticated. Check that:")
        print("  1. IBeam container is running:  docker compose up -d")
        print("  2. Credentials in .env are correct")
        print("  3. Wait ~60s after startup for auth to complete")
        print("  4. Check logs:  docker compose logs -f ibeam")
        sys.exit(1)

    if args.status:
        sys.exit(0)

    if args.quotes:
        ok = check_market_data(args.quotes)
        sys.exit(0 if ok else 1)

    # Full connectivity check
    check_server_time()
    account_id = check_accounts()
    if account_id:
        check_account_summary(account_id)
        check_positions(account_id)
        # Default symbols to test market data
        check_market_data(["AAPL", "MSFT", "HG"])  # HG = Copper futures

    print("\n" + "=" * 60)
    print("  All checks complete")
    print("=" * 60)


if __name__ == "__main__":
    main()
