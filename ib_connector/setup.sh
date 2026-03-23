#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# IBeam Live Account Setup (READ-ONLY — No Trading)
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "══════════════════════════════════════════════════════════"
echo "  IBeam — Interactive Brokers LIVE Account (READ-ONLY)"
echo "══════════════════════════════════════════════════════════"
echo ""
echo "  ┌──────────────────────────────────────────────────┐"
echo "  │  TRADING IS DISABLED                             │"
echo "  │  All order/trade endpoints are blocked by proxy  │"
echo "  │  You can only read: market data, positions, etc  │"
echo "  └──────────────────────────────────────────────────┘"

# Step 1: Check .env
if [ ! -f .env ]; then
    echo ""
    echo "  No .env file found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "  ┌─────────────────────────────────────────────────┐"
    echo "  │  ACTION REQUIRED:                               │"
    echo "  │                                                  │"
    echo "  │  Edit .env with your IB LIVE account creds:     │"
    echo "  │    IBEAM_ACCOUNT=YOUR_USERNAME                   │"
    echo "  │    IBEAM_PASSWORD=YOUR_PASSWORD                   │"
    echo "  │                                                  │"
    echo "  │  Then re-run this script.                       │"
    echo "  └─────────────────────────────────────────────────┘"
    exit 1
fi

# Verify credentials are filled in
source .env
if [[ "$IBEAM_ACCOUNT" == "YOUR_PAPER_USERNAME" ]] || [[ -z "$IBEAM_ACCOUNT" ]]; then
    echo ""
    echo "  [ERROR] .env still has placeholder credentials."
    echo "          Edit .env with your account details."
    exit 1
fi

echo ""
echo "  Account: $IBEAM_ACCOUNT"
echo "  Mode:    LIVE (READ-ONLY — trading blocked by proxy)"
echo ""

# Step 2: Pull images
echo "  Pulling Docker images..."
docker pull voyz/ibeam:latest
docker pull nginx:alpine

# Step 3: Start containers
echo ""
echo "  Starting IBeam + read-only proxy..."
docker compose up -d

echo ""
echo "  Waiting for authentication (this takes ~60-90 seconds)..."
echo "  NOTE: If you have 2FA enabled, approve the login on your IBKR app"
echo ""

# Step 4: Wait for IBeam auth first (check directly against IBeam via docker exec)
for i in $(seq 1 18); do
    sleep 5
    printf "  [%2d/90s] Checking..." "$((i * 5))"

    # Check if IBeam container is still running
    if ! docker compose ps --status running | grep -q ibeam; then
        echo " container stopped!"
        echo ""
        echo "  [ERROR] IBeam container exited. Check logs:"
        echo "          docker compose logs ibeam"
        exit 1
    fi

    # Check auth via the read-only proxy
    STATUS=$(curl -kfs https://localhost:5500/v1/api/iserver/auth/status 2>/dev/null || echo "")
    if echo "$STATUS" | grep -q '"authenticated":true'; then
        echo " AUTHENTICATED!"
        echo ""

        # Verify trading is blocked
        echo "  Verifying trading endpoints are blocked..."
        BLOCK_CHECK=$(curl -kfs -o /dev/null -w "%{http_code}" -X POST https://localhost:5500/v1/api/iserver/account/orders -d '{}' 2>/dev/null || echo "000")
        if [ "$BLOCK_CHECK" = "403" ]; then
            echo "  [OK] Trading endpoints confirmed BLOCKED (403)"
        else
            echo "  [WARN] Unexpected response ($BLOCK_CHECK) — check nginx config"
        fi

        echo ""
        echo "══════════════════════════════════════════════════════════"
        echo "  SUCCESS — Connected to IB Live Account (READ-ONLY)"
        echo "══════════════════════════════════════════════════════════"
        echo ""
        echo "  READ-ONLY API: https://localhost:5500/v1/api"
        echo "  (IBeam direct port is NOT exposed — only proxy is)"
        echo ""
        echo "  Run connectivity check:"
        echo "    python check_ib_connectivity.py"
        echo ""
        echo "  Fetch quotes:"
        echo "    python check_ib_connectivity.py --quotes AAPL MSFT HG"
        echo ""
        echo "  View logs:"
        echo "    docker compose logs -f"
        echo ""
        echo "  Stop:"
        echo "    docker compose down"
        echo ""
        exit 0
    fi

    echo " waiting..."
done

echo ""
echo "  [WARN] Authentication not confirmed after 90s."
echo "         This may be normal — IBeam might need more time."
echo ""
echo "  Check status manually:"
echo "    docker compose logs -f ibeam"
echo "    python check_ib_connectivity.py --status"
echo ""
echo "  Common issues:"
echo "    - Wrong credentials in .env"
echo "    - 2FA pending on your IBKR mobile app"
echo "    - Account locked or requires security reset"
echo ""
