# HolistiCare MVP — Deployment Analysis

**Prepared:** 2026-04-21
**Scope:** Production deployment for the HolistiCare MVP (FastAPI + React/Vite + PostgreSQL/pgvector + cross-encoder reranker + Anthropic/OpenAI APIs)
**Target scale:** ~10 clinicians, ~50–200 patients, low concurrent traffic (<5 RPS peak), single tenant
**Constraints:** NOM-024-SSA3-2012, LFPDPPP (Mexican federal data protection), solo-developer ops budget

---

## 1. Executive summary

For a solo developer on a tight budget shipping an MVP for a single Mexican clinical pilot, the recommendation is a **hybrid topology: VPS compute + managed Postgres with pgvector**. Concretely: **Hetzner CPX21 (or a Fly.io Machine in `qro`) for the FastAPI app and cross-encoder reranker; Neon or Supabase for Postgres; Cloudflare Pages for the frontend.** All-in cost ~$25–45/month, deployable in a weekend, with a documented escalation path to AWS `mx-central-1` once a paying customer triggers compliance maturity.

Public cloud "managed everything" is over-engineered for MVP scale and burns $180–350/month with no compliance benefit you can't replicate elsewhere via a signed DPA. PaaS (Render, Railway, Fly full-stack) is attractive ergonomically but typically lacks first-class pgvector or pushes you to an external DB anyway — at which point you've reinvented the hybrid.

---

## 2. Compliance framing (NOM-024 + LFPDPPP)

Two regulatory regimes apply:

- **NOM-024-SSA3-2012** governs interoperability and structure of electronic clinical records. Its operative requirement for HolistiCare is the practitioner-approval gate already encoded in plan governance (`requires_practitioner_review: true`). **It does not mandate data residency in Mexico.**
- **LFPDPPP** classifies clinical data as *datos personales sensibles*. Cross-border transfer is permitted with patient consent, a data-processing agreement (DPA) with the cloud vendor, and equivalent protection in the destination jurisdiction.

Practical implication: US-region hosting is legally workable for the MVP if you (a) execute vendor DPAs, (b) collect explicit cross-border-transfer consent in the intake flow, and (c) document the controls. **HIPAA BAAs are not legally required in Mexico**, but procuring one signals SOC2-grade controls to enterprise buyers later. In-Mexico residency becomes a real differentiator only when selling to IMSS, ISSSTE, or large hospital networks.

---

## 3. Option analysis

### Option 1 — Public cloud, managed services (AWS / GCP / Azure)

**Reference architecture (AWS):** ECS Fargate (2× 0.5 vCPU / 1 GB tasks for the backend), Aurora Serverless v2 PostgreSQL with the `vector` extension, S3 for source PDFs, CloudFront + S3 for the SPA, Secrets Manager, CloudWatch.

| Dimension | Assessment |
|---|---|
| Monthly cost | ~$180–350 floor. Aurora Serverless v2 minimum 0.5 ACU ≈ $43; Fargate 2 small tasks ≈ $25; NAT Gateway ≈ $32; ALB ≈ $20; egress, observability, Secrets Manager on top. GCP (Cloud Run + Cloud SQL) and Azure (Container Apps + Flexible Server) land within ±20%. |
| pgvector | Native: RDS PostgreSQL 16, Aurora PostgreSQL 16, Cloud SQL Postgres 15+, Azure Database for PostgreSQL Flexible Server. All support `CREATE EXTENSION vector`. |
| Compliance | Strongest. SOC2 / ISO 27001 / HIPAA BAA available. **AWS launched `mx-central-1` (Querétaro) in Jan 2025 — the only public cloud with an in-Mexico region.** GCP nearest: São Paulo / Santiago. Azure nearest: US South Central. |
| Deployment complexity | High for a solo dev. IaC (Terraform / CDK), VPC design, IAM, ECS task definitions — easily 1–2 weeks of plumbing before first production deploy. |
| Scalability ceiling | Effectively unlimited; Aurora v2 autoscales storage and compute. |
| Latency from Mexico (Guadalajara baseline) | `mx-central-1`: <20 ms. `us-east-1`: 60–90 ms. `us-west-2`: 50–80 ms. |

**Verdict:** Right answer in 12–18 months, wrong answer this quarter. Premature optimization for both cost and operator time.

### Option 2 — VPS (Hetzner / DigitalOcean / Fly.io / Railway as raw compute)

**Reference architecture (Hetzner):** One CPX21 (3 vCPU / 4 GB / 80 GB SSD) running Docker Compose with backend, Postgres 16 with `pgvector` baked in (`pgvector/pgvector:pg16` image), Caddy reverse proxy with auto-TLS. Frontend on Cloudflare Pages (free).

| Dimension | Assessment |
|---|---|
| Monthly cost | **Hetzner CPX21 ~€8.5 (~$10) + backups €2 + Cloudflare Pages free ≈ $15/mo all-in.** DO Droplet 2vCPU/4GB ≈ $24. Fly.io shared-cpu-2x + 4 GB ≈ $30. Railway: $5 base + usage, typically $20–40. |
| pgvector | Self-managed. The `pgvector/pgvector:pg16` Docker image gives full feature parity and is what your `infra/init.sql` already targets. |
| Compliance | Weakest out of the box. Hetzner: ISO 27001 only, no SOC2, no HIPAA BAA, EU DCs only. DO: SOC2 Type II, HIPAA-eligible only on dedicated tier. Fly.io: SOC2, HIPAA BAA available, has a `qro` (Querétaro) region for Machines. Railway: SOC2, US/EU only, no HIPAA. |
| Deployment complexity | Low. Single Docker Compose, one server, weekend setup. Tradeoff: you own backups, OS patching, Postgres tuning, monitoring. |
| Scalability ceiling | Vertical only on a single VPS — comfortable to ~50 clinicians / few hundred patients. Beyond that, splitting the DB off (i.e. moving to Option 3) becomes mandatory. |
| Latency from Mexico | Hetzner (EU): 150–180 ms. DO NYC3: 70–90 ms. DO SFO3: 50–70 ms. Fly `qro`: <20 ms. Railway us-west: 50–70 ms. |

**Verdict:** Cheapest and simplest, but you carry all the operational risk and the compliance story is harder to defend to enterprise prospects.

### Option 3 — Hybrid (VPS compute + managed Postgres-with-pgvector)

**Reference architecture:** Hetzner CPX21 *or* Fly.io Machine in `qro` for the FastAPI app + cross-encoder reranker. **Neon** (serverless Postgres, native pgvector, generous free tier) or **Supabase** (Postgres + pgvector, free tier, US/EU/SA regions) or **DigitalOcean Managed Postgres** for the database. Frontend on Cloudflare Pages.

| Dimension | Assessment |
|---|---|
| Monthly cost | **Hetzner $10 + Neon free tier ≈ $10/mo during pilot.** Production-tier Neon (Launch plan, autoscaling) starts at $19. Supabase Pro $25. DO Managed Postgres 1 GB ≈ $15. **Realistic all-in: $25–45/mo.** |
| pgvector | First-class on Neon, Supabase, DO Managed PG, Aiven, Crunchy Bridge. All run Postgres 15/16 with the extension pre-enabled — no manual install. |
| Compliance | Materially better than pure VPS. Neon: SOC2 Type II, HIPAA BAA on Business plan (not cheap — skip until needed). Supabase: SOC2 Type II, HIPAA add-on. DO Managed Postgres: SOC2, HIPAA on dedicated. You inherit DB-level compliance posture for free; app-tier compliance is still on you. |
| Deployment complexity | Low–medium. Decouples DB lifecycle from the app server (a real win — you can rebuild the VPS without risking patient data). Connection pooling needs explicit handling (PgBouncer, or Neon's built-in pooler endpoint). |
| Scalability ceiling | High. Managed Postgres autoscales storage and compute; the app tier scales horizontally by adding VPS nodes behind a load balancer. Effectively unbounded for the MVP and the year after. |
| Latency from Mexico | App tier: same as Option 2. DB hop adds 0–50 ms depending on co-location — keep app and DB in the same US-East/West region. |

**Verdict:** Best balance of cost, ops sanity, and a credible compliance story. **Recommended baseline.**

### Option 4 — PaaS (Render / Railway / Fly.io full-stack)

**Reference architecture (Render):** Web service (backend), static site (frontend), Render Postgres add-on, background worker for ingestion. Auto-deploy from Git.

| Dimension | Assessment |
|---|---|
| Monthly cost | Render: Starter web $7 + Postgres $7 + bandwidth ≈ $20–35. Railway: $20–40 with hobby usage. Fly.io full-stack: $30–60 once machines are sized for the cross-encoder. |
| pgvector | **Mixed.** Render Postgres added pgvector in 2024 (verify version). Railway's Postgres template supports it. Fly Postgres requires manual extension install on each replica. Bolting Supabase on as a managed-DB add-on is the safest path on any of the three. |
| Compliance | Render: SOC2 Type II, HIPAA on Enterprise. Railway: SOC2, no HIPAA. Fly: SOC2 Type II, HIPAA BAA available. None offer Mexico residency for the DB; Fly's `qro` region applies to Machines only. |
| Deployment complexity | Lowest. `render.yaml` / `fly.toml`, `git push`, done. CI/CD baked in. Tradeoff: you live inside the platform's abstractions; egress, custom networking, and bursty workloads can get expensive fast. |
| Scalability ceiling | Medium. Fine to a few hundred users; heavy reranker traffic will push you to bigger plans where the cost advantage erodes vs. raw VPS. |
| Latency from Mexico | Fly `qro`: <20 ms (best of any option). Render Oregon: 50–80 ms. Railway us-west: 50–70 ms. |

**Verdict:** Tempting for the deploy-from-Git ergonomics. **Fly.io Machines (`qro`) + a managed Postgres elsewhere is genuinely competitive with Option 3** if latency matters more than operational control. Pure Render or Railway gives negligible savings vs. hybrid.

---

## 4. Recommendation matrix

Scoring 1 (worst) – 5 (best) for an MVP-stage solo developer with the constraints above.

| Criterion | Weight | Public cloud | VPS | Hybrid | PaaS |
|---|---|---|---|---|---|
| Cost (MVP scale) | 25% | 1 | 5 | 4 | 3 |
| pgvector ergonomics | 10% | 5 | 4 | 5 | 3 |
| Compliance posture | 15% | 5 | 2 | 4 | 3 |
| Deployment complexity (lower=better) | 20% | 1 | 4 | 4 | 5 |
| Scalability ceiling | 15% | 5 | 2 | 5 | 4 |
| Latency from Mexico | 15% | 4 | 3 | 4 | 4 |
| **Weighted total** | **100%** | **2.95** | **3.40** | **4.30** | **3.55** |

---

## 5. Final recommendation

**Hybrid: Hetzner CPX21 (or Fly.io `qro` Machine) for the FastAPI app + cross-encoder reranker; Neon (or Supabase) Postgres with pgvector for the database; Cloudflare Pages for the frontend.**

Rationale:

1. **Cost discipline.** $25–45/month preserves capstone and consulting budget. Compare to $200+/mo on AWS for traffic that doesn't yet exist.
2. **Operational sanity.** Decoupling the DB from the VPS eliminates the worst class of solo-dev disasters (botched Postgres upgrade, runaway disk, lost backups). You keep `docker compose up -d` simplicity for the app tier where iteration is highest.
3. **Compliance defensibility.** A Neon/Supabase DPA + a properly worded patient consent flow + the practitioner-approval gate already in the domain model gives you a coherent NOM-024 + LFPDPPP narrative. HIPAA-grade tiers are available when an enterprise prospect actually asks.
4. **Mexico latency.** If latency matters more than ops simplicity, swap Hetzner for **Fly.io Machine in `qro`** — keeps the rest of the stack identical and gets you sub-20 ms from Guadalajara.
5. **Reranker fit.** `cross-encoder/ms-marco-MiniLM-L-6-v2` runs comfortably on 2 vCPU / 4 GB; no GPU needed. CPX21 or 2x-CPU Fly Machine handles MVP throughput with headroom.

### Concrete starting stack

| Layer | Choice | Cost |
|---|---|---|
| Compute | Hetzner CPX21 (Falkenstein/Helsinki), Docker Compose, Caddy + auto-HTTPS | ~$10/mo |
| Database | Neon free tier during dev/pilot → Launch ($19) at first paying clinician; pgvector pre-enabled | $0 → $19/mo |
| Frontend | `npm run build` → Cloudflare Pages | Free |
| Object storage | Cloudflare R2 for ingested PDFs (no egress fees) | $0.015/GB |
| Secrets | `.env` on the VPS, encrypted backup via `restic` to R2/B2 | <$1/mo |
| Monitoring | UptimeRobot free + Sentry free tier | Free |

### When to migrate

| Trigger | Action |
|---|---|
| First paid Mexican clinic with >50 patients | Upgrade Neon to Launch; add nightly logical backups to R2. |
| Latency complaints from Mexican users | Swap Hetzner → Fly.io `qro` Machine; keep DB region, accept ~50 ms hop. |
| Enterprise prospect requests SOC2 / HIPAA evidence | Migrate compute to AWS `mx-central-1` ECS Fargate, DB to Aurora Serverless v2 with pgvector, sign BAAs. The Compose-based architecture makes this a ~2-week port. |
| RAG corpus exceeds ~100k chunks or QPS exceeds ~20 | Move reranker to a dedicated worker (Modal, Replicate, or a second VPS) and introduce a job queue. |

---

## 6. Risks and unknowns to validate before launch

- **Neon free-tier autosuspend** can add 1–3 s cold-start latency on the first request after idle. Move to Launch tier before any real user traffic — not after.
- **Pricing drift.** All figures are 2026-Q1 list prices; verify on each vendor's pricing page before committing budget.
- **Cross-encoder memory footprint.** Confirm RSS under load; if it pushes past 2 GB, size up to CPX31 (4 vCPU / 8 GB) for headroom — still <$20/mo.
- **Patient consent UX.** The cross-border data-transfer consent must appear in the intake flow, not buried in TOS — this is the actual LFPDPPP control, not the cloud region choice.
- **Backup ownership.** Even with managed Postgres, run an independent nightly `pg_dump` to your own R2/B2 bucket. Vendor lock-in on backups is a real business-continuity risk.
- **OpenAI/Anthropic egress.** API calls leave whichever region you're in. Latency to Anthropic's US endpoints from Mexico is fine (<100 ms); not a deciding factor.
