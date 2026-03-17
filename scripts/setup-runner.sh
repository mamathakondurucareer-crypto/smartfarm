#!/usr/bin/env bash
# ─────────────────────────────────────────────────────────────────────────────
# Register your Mac as a GitHub Actions self-hosted runner for SmartFarm.
#
# Prerequisites:
#   • Docker Desktop running
#   • GitHub repo admin access
#
# Usage:
#   chmod +x scripts/setup-runner.sh
#   ./scripts/setup-runner.sh
# ─────────────────────────────────────────────────────────────────────────────
set -euo pipefail

RUNNER_DIR="$HOME/actions-runner"
RUNNER_VERSION="2.323.0"   # update if GitHub releases a newer version

# ── 1. Get token from user ────────────────────────────────────────────────────
echo ""
echo "════════════════════════════════════════════════════════════"
echo "  SmartFarm — GitHub Actions Self-Hosted Runner Setup"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Step 1: Go to your GitHub repo → Settings → Actions → Runners"
echo "        → New self-hosted runner → macOS"
echo "        Copy the registration token shown on that page."
echo ""
read -rp "Paste your runner registration token: " RUNNER_TOKEN
read -rp "GitHub repo URL (e.g. https://github.com/org/smartfarm): " REPO_URL

# ── 2. Download runner ────────────────────────────────────────────────────────
mkdir -p "$RUNNER_DIR"
cd "$RUNNER_DIR"

ARCH=$(uname -m)
if [ "$ARCH" = "arm64" ]; then
  RUNNER_PKG="actions-runner-osx-arm64-${RUNNER_VERSION}.tar.gz"
else
  RUNNER_PKG="actions-runner-osx-x64-${RUNNER_VERSION}.tar.gz"
fi

echo ""
echo "Downloading GitHub Actions runner v${RUNNER_VERSION} (${ARCH})..."
curl -sL "https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/${RUNNER_PKG}" \
  -o "$RUNNER_PKG"
tar xzf "$RUNNER_PKG"
rm "$RUNNER_PKG"

# ── 3. Configure ─────────────────────────────────────────────────────────────
echo ""
echo "Configuring runner..."
./config.sh \
  --url "$REPO_URL" \
  --token "$RUNNER_TOKEN" \
  --name "mac-local-$(hostname -s)" \
  --labels "self-hosted,macOS,local" \
  --work "_work" \
  --unattended

# ── 4. Install as a launchd service (runs on login, survives reboots) ─────────
echo ""
echo "Installing runner as a macOS launchd service..."
./svc.sh install
./svc.sh start

echo ""
echo "════════════════════════════════════════════════════════════"
echo "  Runner registered and running."
echo ""
echo "  Status:   cd $RUNNER_DIR && ./svc.sh status"
echo "  Stop:     cd $RUNNER_DIR && ./svc.sh stop"
echo "  Uninstall:cd $RUNNER_DIR && ./svc.sh uninstall"
echo "════════════════════════════════════════════════════════════"
echo ""
echo "Next: Add GitHub environment secrets in your repo:"
echo "  Settings → Environments → test  (and → prod)"
echo ""
echo "  Required secrets for BOTH environments:"
echo "    POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD"
echo "    SECRET_KEY, ALLOWED_ORIGINS, ANTHROPIC_API_KEY"
echo ""
echo "  Additional secrets for PROD only:"
echo "    ADMIN_USERNAME, ADMIN_EMAIL, ADMIN_PASSWORD"
echo ""
