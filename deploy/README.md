# DiscoveryFX — Ubuntu VPS deployment (test branch)

This branch deploys to the same staging VPS as EzTrove (`109.199.121.116`), using
different ports. Five docker containers run side-by-side; only `web` and `api`
are publicly reachable. Postgres and Redis stay on the internal docker network.

## Port map on the VPS

| Service | Public port | Why exposed |
|---|---|---|
| `web` (React + Vite, nginx) | **12091** | Main entry — `http://109.199.121.116:12091` |
| `api` (FastAPI) | **12092** | Direct API access for testing / curl |
| `postgres` | — | Internal only. Reach via `docker exec`. |
| `redis` | — | Internal only. |
| `worker` (RQ) | — | Background process. |

The frontend's `/api/*` calls are proxied by the **container's** nginx to `api:8000` (docker DNS),
so the browser doesn't need to know about port 12092 — it just calls `/api/...` relative to `:12091`.

## First-time VPS setup

```bash
# As root on the VPS:
cd /opt
git clone https://github.com/basharathussain/discoveryfx-mvp.git discoveryfx-mvp
cd discoveryfx-mvp
git checkout test

# Open the public ports in ufw
ufw allow 12091/tcp
ufw allow 12092/tcp

# First build + run
./deploy/deploy.sh
```

After this completes the site is reachable at **`http://109.199.121.116:12091/`** and the
API at **`http://109.199.121.116:12092/api/health`**.

## Ongoing deploys

From your Mac:
```bash
git push origin test
ssh eztrove-vps 'cd /opt/discoveryfx-mvp && ./deploy/deploy.sh'
```

`deploy.sh` does: `git pull origin test` → `docker compose up -d --build` → smoke-test.

## What's different from the `deployment` branch (localhost)

| Concern | `deployment` (localhost) | `test` (VPS) |
|---|---|---|
| Web port | `3001:80` | `12091:80` |
| API port | `8081:8000` | `12092:8000` |
| Postgres port | `5440:5432` (exposed) | internal-only (no host binding) |

## Useful one-liners

```bash
# Tail API logs
ssh eztrove-vps 'cd /opt/discoveryfx-mvp && docker compose logs -f --tail 100 api'

# Open a psql session
ssh eztrove-vps 'docker exec -it discoveryfx-postgres psql -U discoveryfx'

# Stop / start the stack
ssh eztrove-vps 'cd /opt/discoveryfx-mvp && docker compose down'
ssh eztrove-vps 'cd /opt/discoveryfx-mvp && docker compose up -d'
```

## Security notes

- `JWT_SECRET` in `.env` is the dev placeholder. Before any real users, rotate it on the VPS:
  ```bash
  ssh eztrove-vps 'cd /opt/discoveryfx-mvp && \
    sed -i "s|^JWT_SECRET=.*|JWT_SECRET=$(openssl rand -hex 32)|" .env && \
    docker compose restart api worker'
  ```
- API port 12092 is exposed for convenience; close it (`ufw delete allow 12092/tcp`) once
  you no longer need direct API testing — the frontend reaches it via its own nginx proxy.
- Postgres password is the dev default. Rotate before production.

## When you add a domain + HTTPS

Same approach as EzTrove: host nginx reverse-proxies `https://domain` to `127.0.0.1:12091`,
then `certbot --nginx -d <domain>` issues the cert. To keep deploys simple, switch the
container binding to `127.0.0.1:12091:80` at that point so the public surface is only nginx.
