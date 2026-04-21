# Phase 6 - Deployment and Ops Runbook

## Document control

- Owner:
- Contributors:
- Version:
- Last updated:
- Status: `[ ]` Draft `[~]` In progress `[x]` Complete

## 1. Objective

Define repeatable deployment, monitoring, incident response, backup, and maintenance procedures for HolistiCare.

## 2. Environments and infrastructure

| Environment | Purpose | Region | Stack | Access model |
|-------------|---------|--------|-------|--------------|
| Dev |  |  |  |  |
| Staging |  |  |  |  |
| Prod |  |  |  |  |

## 3. Release process

1. Build artifacts
2. Run quality gates
3. Deploy to staging
4. Validate smoke tests
5. Approve production deployment
6. Post-deploy verification

## 4. Deployment checklist

- [ ] Configuration and secrets validated
- [ ] If **`NUTRITION_SAFETY_TERMS_PATH`** is set (clinic-specific nutrition safety synonym JSON, US-RAG-004), the file is present in the runtime filesystem, schema-valid, and mounted or baked into the image as intended; the API will not start if the file is missing or invalid (same contract as local development; see `setup.md` §4.2.1).
- [ ] Database migrations reviewed
- [ ] Backward compatibility check complete
- [ ] Rollback plan confirmed
- [ ] Monitoring dashboards ready

## 5. Runtime operations

### 5.1 Service health

- API health endpoints:
- Worker health:
- Queue health:
- DB and vector index health:

### 5.2 Observability

- Logs:
- Metrics:
- Traces:
- Alert thresholds:

## 6. Incident response

### Severity model

- Sev-1:
- Sev-2:
- Sev-3:

### Incident workflow

1. Detect and classify
2. Contain impact
3. Diagnose root cause
4. Recover services
5. Document postmortem

## 7. Backup, restore, and disaster recovery

- Backup frequency:
- Retention:
- Restore procedure:
- Recovery time objective (RTO):
- Recovery point objective (RPO):

## 8. Security operations

- Secrets management:
- Key rotation:
- Vulnerability scanning:
- Access review cadence:

### HolistiCare (repository-specific)

- **Dependency and static scans in CI:** GitHub Actions job `security-audit` runs `pip-audit`, `bandit`, and `npm audit` (see `.github/workflows/ci.yml`). It is **blocking** unless repository variable **`SECURITY_AUDIT_ADVISORY=true`** is set for triage. Documented in `docs/README.md` and `09-security-audit-and-todos.md`.
- **Dev auth:** Production and shared staging must keep **`ALLOW_DEV_AUTH=false`** (or unset). The dev-login route must not exist in those environments (`POST /auth/dev-login` → **404**). See `09-security-audit-and-todos.md` checklist.
- **Image rebuilds:** When `backend/requirements.txt` changes, production pipelines should rebuild the backend image (not only rely on bind mounts). Local analogue: `docs/setup.md` section 3.2.

## 9. Data governance operations

- Retention enforcement:
- Deletion workflows:
- Consent revocation handling:
- Audit evidence collection:

## 10. Cost and capacity management

- Capacity baseline:
- Scaling policy:
- Monthly cost tracking:
- Optimization actions:

### HolistiCare future deployment plan (post-pilot)

Source notes:
- `../holisticare_deployment_analysis.md`
- `../holisticare_deployment_quickstart.md`

Planned implementation slices:
1. Production runtime split:
   - Add `docker-compose.prod.yml` with backend + reverse proxy only.
   - Keep frontend on static hosting and move database to managed Postgres with pgvector.
2. Security and auth hardening:
   - Enforce `ALLOW_DEV_AUTH=false` in production.
   - Lock `CORS_ORIGINS` to production frontend domain.
   - Confirm TLS-only DB connectivity (`sslmode=require`).
3. Operability baseline:
   - Add independent daily `pg_dump` backup to object storage.
   - Add uptime probe and error monitoring.
   - Document and run restore drill.
4. Compliance readiness:
   - Add explicit cross-border data-transfer consent in intake flow.
   - Maintain vendor DPA checklist and status.
   - Validate durable audit logs for generation and approval actions.
5. Cost/scale gates:
   - Track monthly infrastructure and model API spend.
   - Define triggers to scale compute or migrate to stricter managed cloud footprint.

## 11. Maintenance calendar

- Dependency updates:
- Model and prompt reviews:
- Compliance audits:
- Runbook drills:

## Completion checklist

- [ ] Deployment process tested end-to-end
- [ ] Rollback and restore drills completed
- [ ] Monitoring and alerts operational
- [ ] Incident workflow validated
- [ ] Security and governance tasks scheduled
