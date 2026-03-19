"""
Interactive Brokers - Today's PNL by Asset
Connects to TWS/IB Gateway and displays daily P&L per position.
"""

import sys
import time
from ib_insync import IB, util


def get_daily_pnl_by_asset(host='127.0.0.1', port=7497, client_id=1):
    """Connect to IB and fetch today's PNL broken down by asset."""
    ib = IB()

    print(f"Connecting to IB on {host}:{port}...")
    try:
        ib.connect(host, port, clientId=client_id)
    except Exception as e:
        print(f"Connection failed: {e}")
        print("Make sure TWS or IB Gateway is running and API connections are enabled.")
        print("  - TWS paper: port 7497 | TWS live: port 7496")
        print("  - Gateway paper: port 4002 | Gateway live: port 4001")
        sys.exit(1)

    print("Connected. Fetching account and PNL data...\n")

    # Get managed accounts
    accounts = ib.managedAccounts()
    account = accounts[0] if accounts else None
    if not account:
        print("No managed accounts found.")
        ib.disconnect()
        sys.exit(1)

    # Request PNL for the account
    account_pnl = ib.reqPnL(account)
    ib.sleep(2)  # wait for data

    # Request PNL per position (single stock level)
    portfolio = ib.portfolio(account)
    pnl_singles = []
    for item in portfolio:
        contract = item.contract
        pnl_single = ib.reqPnLSingle(account, '', contract.conId)
        pnl_singles.append((contract, pnl_single))

    ib.sleep(2)  # wait for all PNL data

    # Display account-level PNL
    print("=" * 70)
    print(f"  Account: {account}")
    print(f"  Daily PNL:      {account_pnl.dailyPnL:>12,.2f}" if account_pnl.dailyPnL else "  Daily PNL:      N/A")
    print(f"  Unrealized PNL: {account_pnl.unrealizedPnL:>12,.2f}" if account_pnl.unrealizedPnL else "  Unrealized PNL: N/A")
    print(f"  Realized PNL:   {account_pnl.realizedPnL:>12,.2f}" if account_pnl.realizedPnL else "  Realized PNL:   N/A")
    print("=" * 70)

    # Display per-asset PNL
    print(f"\n{'Asset':<20} {'Type':<6} {'Pos':>8} {'Mkt Price':>12} {'Value':>14} {'Daily PNL':>12} {'Unrl PNL':>12} {'Rl PNL':>12}")
    print("-" * 100)

    total_daily = 0
    total_unrealized = 0
    total_realized = 0
    rows = []

    for contract, pnl_single in pnl_singles:
        symbol = contract.symbol
        sec_type = contract.secType
        pos = pnl_single.position if pnl_single.position else 0
        mkt_price = pnl_single.value / pos if pos != 0 and pnl_single.value else 0
        value = pnl_single.value if pnl_single.value else 0
        daily = pnl_single.dailyPnL if pnl_single.dailyPnL else 0
        unrealized = pnl_single.unrealizedPnL if pnl_single.unrealizedPnL else 0
        realized = pnl_single.realizedPnL if pnl_single.realizedPnL else 0

        rows.append((symbol, sec_type, pos, mkt_price, value, daily, unrealized, realized))
        total_daily += daily
        total_unrealized += unrealized
        total_realized += realized

    # Sort by absolute daily PNL descending
    rows.sort(key=lambda r: abs(r[5]), reverse=True)

    for symbol, sec_type, pos, mkt_price, value, daily, unrealized, realized in rows:
        daily_str = f"{daily:>12,.2f}" if daily else f"{'0.00':>12}"
        unrl_str = f"{unrealized:>12,.2f}" if unrealized else f"{'0.00':>12}"
        rl_str = f"{realized:>12,.2f}" if realized else f"{'0.00':>12}"

        print(f"{symbol:<20} {sec_type:<6} {pos:>8,.0f} {mkt_price:>12,.2f} {value:>14,.2f} {daily_str} {unrl_str} {rl_str}")

    print("-" * 100)
    print(f"{'TOTAL':<20} {'':6} {'':>8} {'':>12} {'':>14} {total_daily:>12,.2f} {total_unrealized:>12,.2f} {total_realized:>12,.2f}")
    print()

    # Cleanup
    ib.cancelPnL(account_pnl)
    for _, pnl_single in pnl_singles:
        ib.cancelPnLSingle(pnl_single)
    ib.disconnect()
    print("Disconnected.")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description="Show today's IB PNL by asset")
    parser.add_argument('--host', default='127.0.0.1', help='TWS/Gateway host (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=7497, help='TWS/Gateway port (default: 7497 for TWS paper)')
    parser.add_argument('--client-id', type=int, default=1, help='Client ID (default: 1)')
    args = parser.parse_args()

    get_daily_pnl_by_asset(args.host, args.port, args.client_id)
