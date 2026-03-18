"""
Fetch individual trades from IBKR using the Flex Web Service API.

Requires environment variables:
  IBKR_FLEX_TOKEN    - Your Flex Web Service token from IBKR Account Management
  IBKR_FLEX_QUERY_ID - The Flex Query ID configured to return trades

The Flex Query should be set up in IBKR Account Management → Reports → Flex Queries
to return Trade data (Activity Flex Query) for the desired period.
"""

import os
import sys
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

FLEX_REQUEST_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.SendRequest"
FLEX_DOWNLOAD_URL = "https://gdcdyn.interactivebrokers.com/Universal/servlet/FlexStatementService.GetStatement"

MAX_POLL_ATTEMPTS = 10
POLL_INTERVAL_SECS = 5


def request_flex_report(token: str, query_id: str) -> str:
    """Request a Flex report and return the reference code."""
    url = f"{FLEX_REQUEST_URL}?t={token}&q={query_id}&v=3"
    resp = urlopen(Request(url), timeout=30)
    xml_data = resp.read().decode("utf-8")
    root = ET.fromstring(xml_data)

    status = root.findtext("Status")
    if status != "Success":
        error_msg = root.findtext("ErrorMessage", "Unknown error")
        raise RuntimeError(f"Flex request failed: {error_msg}")

    reference_code = root.findtext("ReferenceCode")
    if not reference_code:
        raise RuntimeError("No reference code returned from Flex request")

    return reference_code


def download_flex_report(token: str, reference_code: str) -> str:
    """Poll for and download the completed Flex report XML."""
    url = f"{FLEX_DOWNLOAD_URL}?t={token}&q={reference_code}&v=3"

    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        resp = urlopen(Request(url), timeout=60)
        data = resp.read().decode("utf-8")

        # If the response is still XML with a status, the report isn't ready yet
        if data.strip().startswith("<FlexStatementResponse"):
            root = ET.fromstring(data)
            status = root.findtext("Status")
            if status == "Warn" or status == "Success":
                # Still generating
                print(f"  Report generating... (attempt {attempt}/{MAX_POLL_ATTEMPTS})")
                time.sleep(POLL_INTERVAL_SECS)
                continue
            elif status == "Fail":
                error_msg = root.findtext("ErrorMessage", "Unknown error")
                raise RuntimeError(f"Flex report failed: {error_msg}")

        # Got the actual report
        return data

    raise RuntimeError(f"Report not ready after {MAX_POLL_ATTEMPTS} attempts")


def dump_xml_structure(xml_data: str):
    """Print the XML element tree structure for debugging."""
    root = ET.fromstring(xml_data)
    print("\n  XML structure:")

    def walk(elem, depth=0):
        attrs = f" ({len(elem.attrib)} attrs)" if elem.attrib else ""
        children = len(list(elem))
        child_info = f" [{children} children]" if children else ""
        print(f"    {'  ' * depth}<{elem.tag}>{attrs}{child_info}")
        if depth < 4:  # limit depth
            for child in elem:
                walk(child, depth + 1)

    walk(root)
    print()


def parse_trades(xml_data: str) -> list[dict]:
    """Parse trade records from Flex report XML."""
    root = ET.fromstring(xml_data)
    trades = []

    # Try multiple element names that IBKR uses for trade data
    trade_tags = ["Trade", "Order", "Execution", "TradeConfirm",
                  "UnbundledCommissionDetail", "TransactionTax"]

    for tag in trade_tags:
        for elem in root.iter(tag):
            trade = {"_source_tag": tag}
            for key, value in elem.attrib.items():
                trade[key] = value
            trades.append(trade)
        if trades:
            print(f"  Found trades in <{tag}> elements")
            break

    # If nothing found, try grabbing any element with trade-like attributes
    if not trades:
        for elem in root.iter():
            if elem.attrib.get("symbol") or elem.attrib.get("tradeDate"):
                trade = {"_source_tag": elem.tag}
                for key, value in elem.attrib.items():
                    trade[key] = value
                trades.append(trade)
        if trades:
            print(f"  Found trades via attribute search in <{trades[0]['_source_tag']}> elements")

    return trades


def filter_last_month(trades: list[dict]) -> list[dict]:
    """Filter trades to those from the last 30 days."""
    cutoff = datetime.now() - timedelta(days=30)
    filtered = []

    for trade in trades:
        # IBKR uses dateTime or tradeDate fields
        date_str = trade.get("dateTime") or trade.get("tradeDate") or ""
        if not date_str:
            filtered.append(trade)  # include if no date to filter on
            continue

        # Handle formats: "YYYYMMDD" or "YYYYMMDD;HHmmss" or "YYYY-MM-DD"
        date_part = date_str.split(";")[0].replace("-", "")
        try:
            trade_date = datetime.strptime(date_part[:8], "%Y%m%d")
            if trade_date >= cutoff:
                filtered.append(trade)
        except ValueError:
            filtered.append(trade)  # include if date can't be parsed

    return filtered


def format_trade(trade: dict) -> str:
    """Format a single trade for display."""
    symbol = trade.get("symbol", "???")
    date_str = trade.get("dateTime") or trade.get("tradeDate", "")
    buy_sell = trade.get("buySell") or trade.get("side", "")
    quantity = trade.get("quantity", "")
    price = trade.get("tradePrice") or trade.get("price", "")
    currency = trade.get("currency", "")
    commission = trade.get("ibCommission") or trade.get("commission", "")
    proceeds = trade.get("proceeds", "")
    asset_class = trade.get("assetCategory", "")

    parts = [f"{symbol:>10s}"]
    if date_str:
        parts.append(f"Date: {date_str}")
    if buy_sell:
        parts.append(f"Side: {buy_sell}")
    if quantity:
        parts.append(f"Qty: {quantity}")
    if price:
        parts.append(f"Price: {price}")
    if currency:
        parts.append(f"Ccy: {currency}")
    if proceeds:
        parts.append(f"Proceeds: {proceeds}")
    if commission:
        parts.append(f"Comm: {commission}")
    if asset_class:
        parts.append(f"Type: {asset_class}")

    return " | ".join(parts)


def main():
    token = os.environ.get("IBKR_FLEX_TOKEN")
    query_id = os.environ.get("IBKR_FLEX_QUERY_ID")

    if not token or not query_id:
        print("Error: Set IBKR_FLEX_TOKEN and IBKR_FLEX_QUERY_ID environment variables.")
        print()
        print("To set up Flex Queries:")
        print("  1. Log in to IBKR Account Management")
        print("  2. Go to Reports → Flex Queries → Activity Flex Queries")
        print("  3. Create a query that includes 'Trades' section")
        print("  4. Set the period to 'Last 30 Days' (or desired range)")
        print("  5. Note the Query ID")
        print("  6. Go to Reports → Settings → Flex Web Service")
        print("  7. Generate a token")
        print()
        print("Then run:")
        print("  export IBKR_FLEX_TOKEN='your_token_here'")
        print("  export IBKR_FLEX_QUERY_ID='your_query_id_here'")
        print(f"  python {sys.argv[0]}")
        sys.exit(1)

    print("Requesting Flex report from IBKR...")
    reference_code = request_flex_report(token, query_id)
    print(f"  Reference code: {reference_code}")

    print("Downloading report...")
    xml_data = download_flex_report(token, reference_code)

    trades = parse_trades(xml_data)
    print(f"  Found {len(trades)} total trade(s) in report")

    if not trades:
        dump_xml_structure(xml_data)

    recent_trades = filter_last_month(trades)
    print(f"  {len(recent_trades)} trade(s) in the last 30 days")
    print()

    # Always save raw XML for inspection
    output_file = "ibkr_trades_report.xml"
    with open(output_file, "w") as f:
        f.write(xml_data)
    print(f"Raw XML saved to {output_file}")

    if not recent_trades:
        print("No trades found in the last 30 days.")
        print(f"Check {output_file} to inspect the raw report.")
        return
    print()

    # Display trades
    print("=" * 100)
    print("TRADES - Last 30 Days")
    print("=" * 100)
    for i, trade in enumerate(recent_trades, 1):
        print(f"  {i:3d}. {format_trade(trade)}")
    print("=" * 100)

    # Also save as CSV
    if recent_trades:
        csv_file = "ibkr_trades_last_month.csv"
        all_keys = sorted({k for t in recent_trades for k in t})
        with open(csv_file, "w") as f:
            f.write(",".join(all_keys) + "\n")
            for trade in recent_trades:
                row = [trade.get(k, "").replace(",", ";") for k in all_keys]
                f.write(",".join(row) + "\n")
        print(f"\nCSV saved to {csv_file}")


if __name__ == "__main__":
    main()
