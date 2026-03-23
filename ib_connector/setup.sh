#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────
# IBeam Paper Account Setup Script
# ─────────────────────────────────────────────────────────────
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "══════════════════════════════════════════════════════════"
echo "  IBeam — Interactive Brokers Paper Account Setup"
echo "══════════════════════════════════════════════════════════"

# Step 1: Check .env
if [ ! -f .env ]; then
    echo ""
    echo "  No .env file found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "  ┌─────────────────────────────────────────────────┐"
    echo "  │  ACTION REQUIRED:                               │"
    echo "  │                                                  │"
    echo "  │  Edit .env with your IB paper account creds:    │"
    echo "  │    IBEAM_ACCOUNT=YOUR_PAPER_USERNAME             │"
    echo "  │    IBEAM_PASSWORD=YOUR_PAPER_PASSWORD             │"
    echo "  │                                                  │"
    echo "  │  Paper usernames typically start with 'D' or    │"
    echo "  │  'DU' (e.g., DU1234567).                        │"
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
    echo "          Edit .env with your real paper account details."
    exit 1
fi

echo ""
echo "  Account: $IBEAM_ACCOUNT"
echo "  Mode:    Paper Trading"
echo ""

# Step 2: Pull IBeam image
echo "  Pulling IBeam Docker image..."
docker pull voyz/ibeam:latest

# Step 3: Start container
echo ""
echo "  Starting IBeam container..."
docker compose up -d

echo ""
echo "  Waiting for authentication (this takes ~60 seconds)..."
echo ""

# Step 4: Wait for auth with progress
for i in $(seq 1 12); do
    sleep 5
    printf "  [%2d/60s] Checking..." "$((i * 5))"

    # Check if container is still running
    if ! docker compose ps --status running | grep -q ibeam; then
        echo " container stopped!"
        echo ""
        echo "  [ERROR] IBeam container exited. Check logs:"
        echo "          docker compose logs ibeam"
        exit 1
    fi

    # Check auth status
    STATUS=$(curl -kfs https://localhost:5000/v1/api/iserver/auth/status 2>/dev/null || echo "")
    if echo "$STATUS" | grep -q '"authenticated":true'; then
        echo " AUTHENTICATED!"
        echo ""
        echo "══════════════════════════════════════════════════════════"
        echo "  SUCCESS — Connected to IB Paper Account"
        echo "══════════════════════════════════════════════════════════"
        echo ""
        echo "  API endpoint: https://localhost:5000/v1/api"
        echo ""
        echo "  Run connectivity check:"
        echo "    python check_ib_connectivity.py"
        echo ""
        echo "  Fetch quotes:"
        echo "    python check_ib_connectivity.py --quotes AAPL MSFT"
        echo ""
        echo "  View logs:"
        echo "    docker compose logs -f ibeam"
        echo ""
        echo "  Stop:"
        echo "    docker compose down"
        echo ""
        exit 0
    fi

    echo " waiting..."
done

echo ""
echo "  [WARN] Authentication not confirmed after 60s."
echo "         This may be normal — IBeam might need more time."
echo ""
echo "  Check status manually:"
echo "    docker compose logs -f ibeam"
echo "    python check_ib_connectivity.py --status"
echo ""
echo "  Common issues:"
echo "    - Wrong credentials in .env"
echo "    - 2FA pending on your IBKR mobile app"
echo "    - Account not enabled for paper trading"
echo ""
