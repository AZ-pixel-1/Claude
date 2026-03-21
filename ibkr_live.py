"""
Connect to IBKR TWS/Gateway via ib_insync and export account data + trades.

Requires:
  - pip install ib_insync
  - TWS or IB Gateway running with API enabled
  - TWS API Settings: Enable ActiveX and Socket Clients

Environment variables (optional):
  IBKR_HOST      - default: 127.0.0.1
  IBKR_PORT      - default: 7496 (live) or 7497 (paper)
  IBKR_CLIENT_ID - default: 1

Usage:
  python ibkr_live.py              # full snapshot + trades
  python ibkr_live.py --trades     # trades only (faster)
"""

import json
import os
import sys
from datetime import datetime, timedelta

try:
    from ib_insync import IB, util, ExecutionFilter
except ImportError:
    print("Error: ib_insync not installed. Run: pip install ib_insync")
    sys.exit(1)


def connect(host="127.0.0.1", port=7496, client_id=1):
    ib = IB()
    ib.connect(host, port, clientId=client_id, timeout=10)
    return ib


def fetch_trades(ib):
    """Fetch all available trades/executions from TWS."""
    # reqExecutions returns fills for the current session and recent history
    # TWS typically keeps executions for the last 7 days
    fills = ib.reqExecutions()
    ib.sleep(2)  # allow time for all fills to arrive

    trades = []
    for fill in fills:
        e = fill.execution
        c = fill.contract
        cr = fill.commissionReport
        trades.append({
            "execId": e.execId,
            "time": str(e.time),
            "symbol": c.symbol,
            "secType": c.secType,
            "exchange": e.exchange,
            "currency": c.currency,
            "side": e.side,
            "shares": float(e.shares),
            "price": float(e.price),
            "orderId": e.orderId,
            "acctNumber": e.acctNumber,
            "avgPrice": float(e.avgPrice) if e.avgPrice else None,
            "cumQty": float(e.cumQty) if e.cumQty else None,
            "commission": float(cr.commission) if cr and cr.commission < 1e8 else None,
            "realizedPNL": float(cr.realizedPNL) if cr and cr.realizedPNL < 1e8 else None,
            "currency_comm": cr.currency if cr else None,
        })

    # Sort by time
    trades.sort(key=lambda t: t["time"])
    return trades


def fetch_account(ib):
    """Fetch account summary, positions, P&L, and open orders."""
    data = {
        "timestamp": datetime.now().isoformat(),
        "accounts": ib.managedAccounts(),
    }

    # Account summary
    summary = ib.accountSummary()
    data["account_summary"] = [
        {"account": s.account, "tag": s.tag, "value": s.value, "currency": s.currency}
        for s in summary
    ]

    # Positions
    positions = ib.positions()
    data["positions"] = [
        {
            "account": p.account,
            "symbol": p.contract.symbol,
            "secType": p.contract.secType,
            "exchange": p.contract.exchange,
            "currency": p.contract.currency,
            "position": float(p.position),
            "avgCost": float(p.avgCost),
        }
        for p in positions
    ]

    # P&L
    pnl_list = []
    for account in ib.managedAccounts():
        pnl = ib.reqPnL(account)
        ib.sleep(1)
        pnl_list.append({
            "account": account,
            "dailyPnL": pnl.dailyPnL,
            "unrealizedPnL": pnl.unrealizedPnL,
            "realizedPnL": pnl.realizedPnL,
        })
        ib.cancelPnL(pnl)
    data["pnl"] = pnl_list

    # Open orders
    orders = ib.openOrders()
    data["open_orders"] = [
        {
            "orderId": o.orderId,
            "symbol": o.contract.symbol if hasattr(o, 'contract') and o.contract else "",
            "action": o.action,
            "orderType": o.orderType,
            "totalQuantity": float(o.totalQuantity),
            "lmtPrice": float(o.lmtPrice) if o.lmtPrice else None,
            "status": o.status if hasattr(o, 'status') else "",
        }
        for o in orders
    ]

    return data


def print_trades(trades):
    """Print trades in a formatted table."""
    if not trades:
        print("No trades found.")
        return

    print(f"\n{'='*110}")
    print(f"{'Time':<22s} {'Symbol':<10s} {'Type':<6s} {'Side':<5s} {'Shares':>8s} {'Price':>10s} {'Commission':>12s} {'P&L':>12s} {'Ccy':<4s}")
    print(f"{'='*110}")
    for t in trades:
        comm = f"{t['commission']:.2f}" if t['commission'] is not None else ""
        pnl = f"{t['realizedPNL']:.2f}" if t['realizedPNL'] is not None else ""
        print(f"  {t['time']:<20s} {t['symbol']:<10s} {t['secType']:<6s} {t['side']:<5s} {t['shares']:>8.1f} {t['price']:>10.4f} {comm:>12s} {pnl:>12s} {t['currency']:<4s}")
    print(f"{'='*110}")
    print(f"Total trades: {len(trades)}")

    # Summary by symbol
    symbols = {}
    for t in trades:
        key = t["symbol"]
        if key not in symbols:
            symbols[key] = {"buys": 0, "sells": 0, "total_comm": 0.0, "total_pnl": 0.0}
        if t["side"] == "BOT":
            symbols[key]["buys"] += t["shares"]
        else:
            symbols[key]["sells"] += t["shares"]
        if t["commission"]:
            symbols[key]["total_comm"] += t["commission"]
        if t["realizedPNL"]:
            symbols[key]["total_pnl"] += t["realizedPNL"]

    print(f"\n{'='*70}")
    print(f"{'Symbol':<10s} {'Bought':>10s} {'Sold':>10s} {'Commission':>12s} {'Realized P&L':>14s}")
    print(f"{'='*70}")
    for sym, s in sorted(symbols.items()):
        print(f"  {sym:<10s} {s['buys']:>10.1f} {s['sells']:>10.1f} {s['total_comm']:>12.2f} {s['total_pnl']:>14.2f}")
    print(f"{'='*70}")


def print_account_summary(data):
    """Print account summary."""
    print(f"Connected at {data['timestamp']}")
    print(f"Accounts: {', '.join(data['accounts'])}")
    print()

    key_tags = {"NetLiquidation", "TotalCashValue", "UnrealizedPnL", "RealizedPnL",
                "GrossPositionValue", "MaintMarginReq", "AvailableFunds"}
    print("=== Account Summary ===")
    for s in data["account_summary"]:
        if s["tag"] in key_tags:
            print(f"  {s['tag']:>25s}: {s['value']:>15s} {s['currency']}")

    print("\n=== P&L ===")
    for p in data["pnl"]:
        print(f"  {p['account']}: daily={p['dailyPnL']}, unrealized={p['unrealizedPnL']}, realized={p['realizedPnL']}")

    print(f"\n=== Positions ({len(data['positions'])}) ===")
    for p in data["positions"]:
        print(f"  {p['symbol']:>10s} {p['secType']:>5s}  qty={p['position']:>10.2f}  avgCost={p['avgCost']:>10.2f}  {p['currency']}")

    if data["open_orders"]:
        print(f"\n=== Open Orders ({len(data['open_orders'])}) ===")
        for o in data["open_orders"]:
            print(f"  {o['symbol']:>10s} {o['action']} {o['totalQuantity']} @ {o['lmtPrice']} ({o['orderType']})")


def main():
    host = os.environ.get("IBKR_HOST", "127.0.0.1")
    port = int(os.environ.get("IBKR_PORT", "7496"))
    client_id = int(os.environ.get("IBKR_CLIENT_ID", "1"))
    trades_only = "--trades" in sys.argv

    print(f"Connecting to TWS at {host}:{port}...")
    ib = connect(host, port, client_id)

    try:
        # Always fetch trades
        print("Fetching trades...")
        trades = fetch_trades(ib)
        print(f"  Found {len(trades)} trade(s)")

        if not trades_only:
            print("Fetching account data...")
            account_data = fetch_account(ib)
            account_data["trades"] = trades

            output_file = "ibkr_snapshot.json"
            with open(output_file, "w") as f:
                json.dump(account_data, f, indent=2, default=str)
            print(f"Snapshot saved to {output_file}\n")

            print_account_summary(account_data)

        # Print and save trades
        print_trades(trades)

        if trades:
            trades_file = "ibkr_trades.json"
            with open(trades_file, "w") as f:
                json.dump(trades, f, indent=2, default=str)
            print(f"\nTrades saved to {trades_file}")

            # Also save CSV
            csv_file = "ibkr_trades.csv"
            keys = ["time", "symbol", "secType", "side", "shares", "price",
                     "exchange", "currency", "commission", "realizedPNL", "orderId", "acctNumber"]
            with open(csv_file, "w") as f:
                f.write(",".join(keys) + "\n")
                for t in trades:
                    row = [str(t.get(k, "")) for k in keys]
                    f.write(",".join(row) + "\n")
            print(f"Trades CSV saved to {csv_file}")

    finally:
        ib.disconnect()


if __name__ == "__main__":
    main()
