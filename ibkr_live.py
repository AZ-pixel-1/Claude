"""
Connect to IBKR TWS/Gateway via ib_insync and export account data.

Requires:
  - pip install ib_insync
  - TWS or IB Gateway running with API enabled
  - TWS API Settings: Enable ActiveX and Socket Clients

Environment variables (optional):
  IBKR_HOST     - default: 127.0.0.1
  IBKR_PORT     - default: 7496 (live) or 7497 (paper)
  IBKR_CLIENT_ID - default: 1
"""

import json
import os
import sys
from datetime import datetime

try:
    from ib_insync import IB, util
except ImportError:
    print("Error: ib_insync not installed. Run: pip install ib_insync")
    sys.exit(1)


def connect(host="127.0.0.1", port=7496, client_id=1):
    ib = IB()
    ib.connect(host, port, clientId=client_id, timeout=10)
    return ib


def fetch_all(ib):
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
        ib.sleep(1)  # wait for data
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

    # Recent executions (trades today)
    executions = ib.executions()
    data["executions"] = [
        {
            "symbol": e.contract.symbol,
            "secType": e.contract.secType,
            "side": e.execution.side,
            "shares": float(e.execution.shares),
            "price": float(e.execution.price),
            "time": str(e.execution.time),
            "orderId": e.execution.orderId,
            "commission": float(e.commissionReport.commission) if e.commissionReport else None,
        }
        for e in executions
    ]

    return data


def print_summary(data):
    print(f"Connected at {data['timestamp']}")
    print(f"Accounts: {', '.join(data['accounts'])}")
    print()

    # Key account metrics
    key_tags = {"NetLiquidation", "TotalCashValue", "UnrealizedPnL", "RealizedPnL",
                "GrossPositionValue", "MaintMarginReq", "AvailableFunds"}
    print("=== Account Summary ===")
    for s in data["account_summary"]:
        if s["tag"] in key_tags:
            print(f"  {s['tag']:>25s}: {s['value']:>15s} {s['currency']}")

    # P&L
    print("\n=== P&L ===")
    for p in data["pnl"]:
        print(f"  {p['account']}: daily={p['dailyPnL']}, unrealized={p['unrealizedPnL']}, realized={p['realizedPnL']}")

    # Positions
    print(f"\n=== Positions ({len(data['positions'])}) ===")
    for p in data["positions"]:
        print(f"  {p['symbol']:>10s} {p['secType']:>5s}  qty={p['position']:>10.2f}  avgCost={p['avgCost']:>10.2f}  {p['currency']}")

    # Open orders
    if data["open_orders"]:
        print(f"\n=== Open Orders ({len(data['open_orders'])}) ===")
        for o in data["open_orders"]:
            print(f"  {o['symbol']:>10s} {o['action']} {o['totalQuantity']} @ {o['lmtPrice']} ({o['orderType']})")

    # Executions
    if data["executions"]:
        print(f"\n=== Today's Executions ({len(data['executions'])}) ===")
        for e in data["executions"]:
            print(f"  {e['symbol']:>10s} {e['side']} {e['shares']} @ {e['price']} at {e['time']}")


def main():
    host = os.environ.get("IBKR_HOST", "127.0.0.1")
    port = int(os.environ.get("IBKR_PORT", "7496"))
    client_id = int(os.environ.get("IBKR_CLIENT_ID", "1"))

    print(f"Connecting to TWS at {host}:{port}...")
    ib = connect(host, port, client_id)

    try:
        data = fetch_all(ib)

        # Save JSON snapshot
        output_file = "ibkr_snapshot.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2, default=str)
        print(f"Snapshot saved to {output_file}\n")

        print_summary(data)
    finally:
        ib.disconnect()


if __name__ == "__main__":
    main()
