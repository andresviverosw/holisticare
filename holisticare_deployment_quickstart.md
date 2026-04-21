# HolistiCare — Hybrid Deployment Quickstart

**Target:** Hetzner CPX21 (compute) + Neon (managed Postgres + pgvector) + Cloudflare Pages (frontend)
**Companion:** see `holisticare_deployment_analysis.md` for the rationale
**Estimated effort:** ~1 focused weekend (8–12 hrs)
**Prerequisites:** GitHub repo with the project pushed, a domain you control (or buy a `.app`/`.io`/`.mx` for ~$15/yr)

---

## Phase 0 — Accounts (15 min)

| Account | Purpose | Cost |
|---|---|---|
| Hetzner Cloud | VPS | €8.5/mo |
| Neon | Postgres + pgvector | $0 (free) → $19 (Launch) |
| Cloudflare | DNS + Pages + R2 | Free at MVP scale |
| UptimeRobot | External health probe | Free |
| Sentry | Error tracking | Free (5k events/mo) |

Add an SSH key (`ssh-keygen -t ed25519`) and paste the public key into Hetzner's *Security → SSH Keys* before creating the server.

---

## Phase 1 — Database on Neon (20 min)

1. **Create a Neon project.** Region: `aws-us-east-2` (Ohio) is the lowest-latency free-tier option from Mexico (~50–70 ms). Postgres version 16.
2. **Enable pgvector.** Open the SQL editor in the Neon console and run:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
   ```
3. **Bootstrap the schema** by applying your existing `infra/init.sql`:
   ```bash
   # From your local machine
   psql "postgres://<neon-conn-string>?sslmode=require" -f infra/init.sql
   ```
   The `IF NOT EXISTS` guards make this idempotent — safe to re-run.
4. **Capture two connection strings** from the Neon console:
   - **Pooled** (PgBouncer endpoint, port 5432, hostname has `-pooler`) → for the FastAPI app.
   - **Direct** (no `-pooler`) → for migrations and `psql` work.
5. **Disable autosuspend** before pilot traffic arrives. Free tier suspends after 5 min idle (cold start adds 1–3 s). On the Launch plan you can pin `min_compute = 0.25 CU`.

> **Note:** Your `clinical_chunks` IVFFlat index uses `lists = 100`. That's tuned for a few hundred thousand chunks; it's fine for MVP. Re-tune (`lists ≈ rows / 1000`) once the corpus passes ~50k chunks.

---

## Phase 2 — Hetzner VPS (30 min)

1. **Create a CPX21** (3 vCPU AMD / 4 GB / 80 GB) in Falkenstein or Helsinki. Image: Ubuntu 24.04 LTS. Attach your SSH key. Enable IPv4+IPv6 and Hetzner backups (€2/mo — non-negotiable).
2. **Reserve a floating IP** (€1/mo) so you can rebuild the box without changing DNS.
3. **Initial SSH and harden:**
   ```bash
   ssh root@<floating-ip>

   # Create non-root user
   adduser --disabled-password --gecos "" deploy
   usermod -aG sudo deploy
   mkdir -p /home/deploy/.ssh
   cp ~/.ssh/authorized_keys /home/deploy/.ssh/
   chown -R deploy:deploy /home/deploy/.ssh
   chmod 700 /home/deploy/.ssh && chmod 600 /home/deploy/.ssh/authorized_keys

   # Disable root login + password auth
   sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
   sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
   systemctl restart ssh

   # Firewall: only 22, 80, 443
   ufw default deny incoming && ufw default allow outgoing
   ufw allow 22/tcp && ufw allow 80/tcp && ufw allow 443/tcp
   ufw --force enable

   # fail2ban for SSH
   apt update && apt install -y fail2ban
   systemctl enable --now fail2ban

   # Unattended security upgrades
   apt install -y unattended-upgrades
   dpkg-reconfigure --priority=low unattended-upgrades
   ```
4. **Install Docker** (official convenience script):
   ```bash
   su - deploy
   curl -fsSL https://get.docker.com | sudo sh
   sudo usermod -aG docker deploy
   # Log out and back in for group change
   ```

---

## Phase 3 — DNS (10 min)

In Cloudflare DNS for your domain (`holisticare.app` or whatever you bought):

| Type | Name | Target | Proxy |
|---|---|---|---|
| A | `api` | `<hetzner-floating-ip>` | DNS only (grey cloud) |
| CNAME | `app` | `<your-pages-project>.pages.dev` | Proxied (orange cloud) |
| CNAME | `www` | `app` | Proxied |

Keep `api` un-proxied so Caddy gets a real client IP and can issue Let's Encrypt certs without Cloudflare's MITM. Proxy the SPA host for free DDoS / caching.

---

## Phase 4 — Backend deployment (90 min)

### 4.1 Production overlay for Compose

Your current `docker-compose.yml` is a dev setup (bind-mounts source, `--reload`, includes `db`, includes `frontend` running Vite dev server). Don't run that in prod. Add a sibling file:

**`docker-compose.prod.yml`** (new file, place at repo root):

```yaml
services:
  backend:
    image: ghcr.io/<your-gh-user>/holisticare-backend:latest
    container_name: holisticare_backend
    restart: unless-stopped
    env_file: .env.prod
    expose:
      - "8000"
    # No bind-mount, no --reload
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2
    networks: [web]

  caddy:
    image: caddy:2
    container_name: holisticare_caddy
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./Caddyfile:/etc/caddy/Caddyfile:ro
      - caddy_data:/data
      - caddy_config:/config
    depends_on: [backend]
    networks: [web]

volumes:
  caddy_data:
  caddy_config:

networks:
  web:
```

Notes:
- Drops the `db` service entirely (Neon owns it).
- Drops the `frontend` service (Cloudflare Pages owns it).
- Pulls a built image from GitHub Container Registry instead of building on the box. Build via GH Actions on push to `main`.
- 2 workers is a safe default for CPX21; the cross-encoder loads once per worker so memory will be ~1.5–2× a single-worker baseline. Watch `docker stats`.

### 4.2 Caddyfile

**`Caddyfile`** (repo root):

```caddy
api.holisticare.app {
    reverse_proxy backend:8000
    encode zstd gzip
    log {
        output file /data/access.log
        format json
    }
}
```

That's it — Caddy auto-issues and renews Let's Encrypt certs. No nginx config rabbit hole.

### 4.3 Production `.env.prod`

Copy `.env.example` → `.env.prod` on the server (never commit). Critical changes vs. dev:

```bash
# ─── Database (Neon pooled connection) ─────────────────────────
POSTGRES_USER=<neon-user>
POSTGRES_PASSWORD=<neon-password>
POSTGRES_DB=<neon-db>
POSTGRES_HOST=ep-xxxx-pooler.us-east-2.aws.neon.tech
POSTGRES_PORT=5432
# CRITICAL: your async SQLAlchemy DSN must include sslmode=require
# Verify app/core/database.py builds the DSN with ?ssl=require for asyncpg

# ─── App (production hardening) ────────────────────────────────
DEBUG=false
SECRET_KEY=<openssl rand -hex 32>
CORS_ORIGINS=https://app.holisticare.app
ALLOW_DEV_AUTH=false      # NON-NEGOTIABLE in prod (NOM-024)

# ─── LLM / embeddings: same as dev ─────────────────────────────
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
RAG_LLM_FALLBACK_OPENAI=true
```

> **Verify before deploy:** check `app/core/database.py` to confirm the asyncpg DSN includes `ssl=require` (or equivalent). Neon refuses non-TLS connections. If it doesn't, the connection will fail with a TLS handshake error on first query.

### 4.4 Build and ship

Add a GH Actions workflow (`.github/workflows/build-backend.yml`) that on push to `main`:
1. Builds `backend/Dockerfile`
2. Pushes to `ghcr.io/<user>/holisticare-backend:latest` and `:sha-<commit>`

On the server:
```bash
cd ~/holisticare
docker login ghcr.io   # PAT with read:packages
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
docker compose -f docker-compose.prod.yml logs -f backend
```

Smoke test:
```bash
curl https://api.holisticare.app/health   # adapt to your actual health route
curl -X POST https://api.holisticare.app/auth/dev-login   # MUST 404 in prod
```

---

## Phase 5 — Frontend on Cloudflare Pages (20 min)

1. Cloudflare dashboard → **Workers & Pages → Create → Pages → Connect to Git**.
2. Pick your repo. Build settings:
   - **Build command:** `cd frontend && npm ci && npm run build`
   - **Build output:** `frontend/dist`
   - **Root directory:** (leave blank)
   - **Node version:** 20 (set as env var `NODE_VERSION=20`)
3. **Environment variables:**
   - `VITE_API_BASE_URL=https://api.holisticare.app`
   - `NODE_VERSION=20`
4. Confirm your frontend code reads `import.meta.env.VITE_API_BASE_URL` and falls back to `/api` only in dev. If it currently relies on Vite's dev-server proxy (`VITE_PROXY_TARGET`), you'll need a small refactor to make the API base URL configurable. Search for `fetch(` and `axios.create` in `frontend/src/` to confirm.
5. Custom domain: Pages → Custom domains → add `app.holisticare.app`. Cloudflare configures DNS automatically since you're already on their nameservers.

---

## Phase 6 — Initial data + first user (30 min)

1. **Ingest the mock corpus.** From your laptop, against the production API:
   ```bash
   # Mint a temporary admin token via dev login on a STAGING instance,
   # then call /rag/ingest on prod with it. Or write a one-off CLI that
   # signs an admin JWT locally using SECRET_KEY.
   curl -X POST https://api.holisticare.app/rag/ingest \
     -H "Authorization: Bearer <admin-token>" \
     -H "Content-Type: application/json" \
     -d '{"source_dir": "data/mock", "force_reindex": false}'
   ```
   Note: the mock PDFs need to exist *in the container*. Either bake them into the image (acceptable for synthetic data only) or mount them via a volume.
2. **Create the first clinician account.** Since `ALLOW_DEV_AUTH=false`, write a one-off seed script (`backend/scripts/seed_clinician.py`) that inserts directly via the ORM and run it once via `docker compose exec backend python scripts/seed_clinician.py`. Map this to a user story — `US-AUTH-XXX` — and commit it.

---

## Phase 7 — Backups, monitoring, hygiene (45 min)

### 7.1 Independent Postgres backups (don't trust the vendor alone)

Cron on the VPS, output to Cloudflare R2:

```bash
# /etc/cron.daily/pg-backup
#!/bin/bash
set -euo pipefail
TS=$(date -u +%Y%m%dT%H%M%SZ)
DUMP=/tmp/holisticare-${TS}.sql.gz
PGPASSWORD=<neon-password> pg_dump \
  -h ep-xxxx.us-east-2.aws.neon.tech \  # use DIRECT (non-pooler) endpoint
  -U <user> -d <db> --no-owner --no-privileges \
  | gzip > "$DUMP"
rclone copy "$DUMP" r2:holisticare-backups/
rm "$DUMP"
# Retention: keep 30 days
rclone delete --min-age 30d r2:holisticare-backups/
```

Test the restore path quarterly. Untested backups don't exist.

### 7.2 Monitoring

- **UptimeRobot** → HTTPS probe on `https://api.holisticare.app/health` every 5 min, email + push on failure.
- **Sentry** → add `sentry-sdk[fastapi]` to `backend/requirements.txt`, init in `app/main.py` with `dsn=os.getenv("SENTRY_DSN")`, set `SENTRY_DSN` only in `.env.prod`.
- **`docker stats`** is your friend for the first week — confirm the cross-encoder RSS stays under ~2 GB.

### 7.3 Secrets hygiene

- Rotate `SECRET_KEY` only when you're prepared to invalidate all JWTs.
- API keys (Anthropic, OpenAI) live in `.env.prod` on the server, mode 600, owned by `deploy`. Never in the image, never in the repo.
- Encrypt `.env.prod` to R2 nightly via `restic` so a disk loss doesn't lose secrets:
  ```bash
  restic -r s3:r2.../holisticare-secrets backup /home/deploy/holisticare/.env.prod
  ```

---

## Phase 8 — Compliance loose ends (do these before any real patient touches the system)

1. **Patient consent text** in the intake flow must explicitly cover cross-border transfer to the US (Neon) and processing by Anthropic/OpenAI. Map to an `US-COMP-XXX` story and have the practitioner co-designer review the wording.
2. **DPA / Data Processing Agreement** — request from Neon (auto-available on paid plans), Anthropic (Zero Data Retention available on Console), OpenAI (request via privacy@openai.com), Cloudflare (auto-included in TOS).
3. **Audit logging** — confirm every plan generation, approval, and rejection writes to a durable log (your existing `intake_profile_audit` table covers intake; add equivalent for plans if not present). NOM-024 expects traceability.
4. **Disable `/auth/dev-login`** — already enforced via `ALLOW_DEV_AUTH=false`, but add a `pytest` that hits the endpoint against a prod-config fixture and asserts 404. This belongs in CI.

---

## Pre-launch checklist

- [ ] `ALLOW_DEV_AUTH=false` in `.env.prod`, verified by `curl` returning 404
- [ ] `DEBUG=false`, `SECRET_KEY` is a fresh `openssl rand -hex 32`
- [ ] CORS locked to `https://app.holisticare.app` only
- [ ] Neon connection uses pooled endpoint + `sslmode=require`
- [ ] `infra/init.sql` applied to Neon, `pgvector` extension confirmed
- [ ] Cross-encoder model downloaded and cached in the image (don't pull on first request)
- [ ] HTTPS works on both `api.` and `app.` subdomains, valid certs
- [ ] Sentry receiving a test event
- [ ] UptimeRobot probe is green
- [ ] First `pg_dump` cron has run successfully and the dump opens locally
- [ ] Patient consent + DPA paperwork drafted
- [ ] Restore drill documented (even just 3 lines in this repo's README)

---

## Cost summary (steady state)

| Item | Monthly |
|---|---|
| Hetzner CPX21 + backups + floating IP | ~$13 |
| Neon Launch tier (post-pilot) | $19 |
| Cloudflare (DNS, Pages, R2 ~5 GB) | <$1 |
| Sentry / UptimeRobot | $0 |
| Domain (amortised) | ~$1.25 |
| **Total** | **~$35/mo** |

LLM costs (Anthropic + OpenAI embeddings) are workload-dependent and not included — expect $20–80/mo at MVP traffic with judicious caching.
