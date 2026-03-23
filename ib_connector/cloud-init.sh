#!/bin/bash
# ─────────────────────────────────────────────────────────────
# Cloud-init script for Oracle Cloud Free Tier VM
# Sets up Docker + IBeam read-only infrastructure
# ─────────────────────────────────────────────────────────────
# This runs ONCE when the VM is first created.
# After this, use connect.sh from Claude Code to start IBeam.
# ─────────────────────────────────────────────────────────────

set -euo pipefail
exec > /var/log/ibeam-setup.log 2>&1

echo "=== IBeam VM Setup Starting ==="

# Update system
apt-get update -y
apt-get upgrade -y

# Install Docker
apt-get install -y ca-certificates curl gnupg
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Enable Docker
systemctl enable docker
systemctl start docker

# Create ibeam directory
mkdir -p /opt/ibeam
cd /opt/ibeam

# Write docker-compose.yml
cat > docker-compose.yml << 'COMPOSE'
version: "3.8"

services:
  ibeam:
    image: voyz/ibeam:latest
    container_name: ibeam-live
    restart: unless-stopped
    expose:
      - "5000"
    environment:
      IBEAM_ACCOUNT: ${IBEAM_ACCOUNT}
      IBEAM_PASSWORD: ${IBEAM_PASSWORD}
      IBEAM_GATEWAY_BASE_URL: "https://localhost:5000"
      IBEAM_MAINTENANCE_INTERVAL: 50
      IBEAM_MAX_FAILED_AUTH: 5
      IBEAM_REQUEST_RETRIES: 3
      IBEAM_REQUEST_TIMEOUT: 30
      IBEAM_PAGE_LOAD_TIMEOUT: 60
    volumes:
      - ibeam_inputs:/srv/ibeam/inputs
    healthcheck:
      test: ["CMD", "curl", "-kfs", "https://localhost:5000/v1/api/iserver/auth/status"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  readonly-proxy:
    image: nginx:alpine
    container_name: ib-readonly-proxy
    restart: unless-stopped
    depends_on:
      ibeam:
        condition: service_healthy
    ports:
      # Bind to 0.0.0.0 so it's accessible via SSH tunnel
      # Firewall blocks external access — only SSH tunnel gets through
      - "127.0.0.1:5500:5500"
    volumes:
      - ./nginx-readonly.conf:/etc/nginx/nginx.conf:ro
      - proxy_ssl:/etc/nginx/ssl
    entrypoint: ["/bin/sh", "-c"]
    command:
      - |
        mkdir -p /etc/nginx/ssl
        apk add --no-cache openssl > /dev/null 2>&1
        openssl req -x509 -nodes -days 365 \
          -newkey rsa:2048 \
          -keyout /etc/nginx/ssl/proxy.key \
          -out /etc/nginx/ssl/proxy.crt \
          -subj "/CN=localhost" 2>/dev/null
        echo "Read-only proxy ready on port 5500"
        nginx -g 'daemon off;'

volumes:
  ibeam_inputs:
  proxy_ssl:
COMPOSE

# Write nginx read-only config
cat > nginx-readonly.conf << 'NGINX'
worker_processes 1;
error_log /var/log/nginx/error.log warn;

events {
    worker_connections 64;
}

http {
    log_format main '$remote_addr [$time_local] "$request" $status';
    access_log /var/log/nginx/access.log main;

    upstream ibeam {
        server ibeam:5000;
    }

    server {
        listen 5500 ssl;
        ssl_certificate     /etc/nginx/ssl/proxy.crt;
        ssl_certificate_key /etc/nginx/ssl/proxy.key;

        # BLOCK EVERYTHING BY DEFAULT
        location / {
            return 403 '{"error": "BLOCKED - read-only mode, trading is disabled"}';
            add_header Content-Type application/json always;
        }

        # ALLOWED: Authentication
        location /v1/api/iserver/auth/status {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }
        location /v1/api/iserver/auth/ssodh/init {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }

        # ALLOWED: Account info (read-only)
        location /v1/api/iserver/accounts {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }
        location /v1/api/one/user {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }

        # ALLOWED: Portfolio (GET only)
        location /v1/api/portfolio {
            limit_except GET {
                deny all;
            }
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }

        # ALLOWED: Market data
        location /v1/api/iserver/marketdata/snapshot {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }
        location /v1/api/iserver/marketdata/history {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }
        location /v1/api/iserver/marketdata/unsubscribeall {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }
        location /v1/api/md/ {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }

        # ALLOWED: Security definitions / search
        location /v1/api/iserver/secdef/ {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }
        location /v1/api/trsrv/ {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }

        # ALLOWED: Contract info (GET only)
        location /v1/api/iserver/contract/ {
            limit_except GET {
                deny all;
            }
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }

        # ALLOWED: Scanner
        location /v1/api/iserver/scanner/ {
            proxy_pass https://ibeam;
            proxy_ssl_verify off;
        }
    }
}
NGINX

# Write the start script (run on VM to start IBeam with credentials)
cat > start-ibeam.sh << 'START'
#!/bin/bash
set -euo pipefail
cd /opt/ibeam

echo "══════════════════════════════════════════════════"
echo "  IBeam — Start (READ-ONLY, no trading)"
echo "══════════════════════════════════════════════════"
echo ""

read -rp "  IB Username: " IBEAM_ACCOUNT
read -rsp "  IB Password: " IBEAM_PASSWORD
echo ""

export IBEAM_ACCOUNT IBEAM_PASSWORD

docker compose down 2>/dev/null || true
docker compose up -d

echo ""
echo "  Starting... approve 2FA on your phone if prompted."
echo "  Checking auth (up to 90s)..."
echo ""

for i in $(seq 1 18); do
    sleep 5
    STATUS=$(curl -kfs https://localhost:5500/v1/api/iserver/auth/status 2>/dev/null || echo "")
    if echo "$STATUS" | grep -q '"authenticated":true'; then
        echo "  [OK] Authenticated! API ready on localhost:5500"
        exit 0
    fi
    printf "  [%2d/90s] waiting...\n" "$((i * 5))"
done

echo "  [WARN] Auth not confirmed after 90s. Check: docker compose logs ibeam"
START
chmod +x start-ibeam.sh

# Configure firewall — only allow SSH, block everything else
if command -v ufw &>/dev/null; then
    ufw --force reset
    ufw default deny incoming
    ufw default allow outgoing
    ufw allow 22/tcp   # SSH only
    ufw --force enable
fi

# Also configure iptables as backup
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --dport 5500 -j DROP
iptables -A INPUT -p tcp --dport 5000 -j DROP

echo "=== IBeam VM Setup Complete ==="
echo "SSH in and run: /opt/ibeam/start-ibeam.sh"
