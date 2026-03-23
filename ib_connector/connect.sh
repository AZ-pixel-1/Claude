#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Connect to remote IBeam instance via SSH tunnel
# ─────────────────────────────────────────────────────────────
# This script:
#   1. Opens an SSH tunnel to the Oracle Cloud VM
#   2. Forwards port 5500 (read-only proxy) to localhost
#   3. Tests connectivity
#
# Usage: ./connect.sh <vm-ip>
# ─────────────────────────────────────────────────────────────
set -euo pipefail

VM_IP="${1:-}"
SSH_KEY="${2:-~/.ssh/ib-oracle-vm}"

if [[ -z "$VM_IP" ]]; then
    echo ""
    echo "Usage: ./connect.sh <vm-ip-address> [ssh-key-path]"
    echo ""
    echo "  vm-ip-address:  Your Oracle Cloud VM's public IP"
    echo "  ssh-key-path:   Path to SSH private key (default: ~/.ssh/ib-oracle-vm)"
    echo ""
    exit 1
fi

echo "══════════════════════════════════════════════════════════"
echo "  Connecting to IBeam on $VM_IP (READ-ONLY)"
echo "══════════════════════════════════════════════════════════"
echo ""

# Check if tunnel is already running
if curl -kfs https://localhost:5500/v1/api/iserver/auth/status &>/dev/null; then
    echo "  [OK] Already connected! Tunnel is active."
    echo ""
    echo "  Test:  python check_ib_connectivity.py"
    exit 0
fi

# Open SSH tunnel in background
echo "  Opening SSH tunnel (localhost:5500 → $VM_IP:5500)..."
ssh -f -N -L 5500:localhost:5500 -i "$SSH_KEY" -o StrictHostKeyChecking=accept-new ubuntu@"$VM_IP"

sleep 2

# Test connectivity
STATUS=$(curl -kfs https://localhost:5500/v1/api/iserver/auth/status 2>/dev/null || echo "")
if echo "$STATUS" | grep -q '"authenticated":true'; then
    echo "  [OK] Connected and authenticated!"
    echo ""
    echo "  READ-ONLY API: https://localhost:5500/v1/api"
    echo ""
    echo "  Test:  python check_ib_connectivity.py"
    echo ""
    echo "  To close tunnel later:  pkill -f 'ssh.*5500.*$VM_IP'"
else
    echo "  [WARN] Tunnel open but IBeam may not be running on the VM."
    echo ""
    echo "  SSH into the VM and start IBeam:"
    echo "    ssh -i $SSH_KEY ubuntu@$VM_IP"
    echo "    /opt/ibeam/start-ibeam.sh"
fi
