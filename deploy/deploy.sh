#!/usr/bin/env bash
# DiscoveryFX — Ubuntu VPS deploy script (test branch).
# Run on the VPS in /opt/discoveryfx-mvp.
#
# Usage:
#   ./deploy/deploy.sh
#
# What it does:
#   1. Pulls latest origin/test from GitHub
#   2. Rebuilds + restarts the 5-service stack (web/api/worker/postgres/redis)
#   3. Waits for healthy
#   4. Smoke-tests the web container and direct API port

set -euo pipefail

cd "$(dirname "$0")/.."
REPO_ROOT="$(pwd)"
echo "[deploy] repo root: $REPO_ROOT"

CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT_BRANCH" != "test" ]]; then
  echo "[deploy] ERROR: expected branch 'test', got '$CURRENT_BRANCH'." >&2
  echo "[deploy]        run:  git checkout test && ./deploy/deploy.sh" >&2
  exit 1
fi

echo "[deploy] pulling latest origin/test…"
git fetch --prune origin
git pull --ff-only origin test

echo "[deploy] rebuilding + restarting stack…"
docker compose up -d --build

echo "[deploy] waiting 8s for services to settle…"
sleep 8

echo "[deploy] service status:"
docker compose ps

echo "[deploy] smoke tests:"
echo -n "  /api/health  via api:12092 → "
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:12092/api/health || true
echo -n "  /            via web:12091 → "
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:12091/ || true
echo -n "  /api/health  via web:12091 (proxy) → "
curl -sS -o /dev/null -w "%{http_code}\n" http://127.0.0.1:12091/api/health || true

echo "[deploy] done."
