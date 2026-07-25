# QA Report — Sprint 13 (US-DIARY-AUTH-PROD)

**Date:** 2026-07-16  
**Owner:** QA Agent  
**Branch / PR:** `cursor/sprint-13-diary-auth-prod-exec-2591` / [#11](https://github.com/andresviverosw/holisticare/pull/11)  
**Scope:** US-DIARY-AUTH-PROD  

## Verdict

**PASS — ready for Planning Agent backlog closeout / merge**

No blocking defects. Patient diary auth works via single-use invite when `ALLOW_DEV_AUTH=false`.

## Acceptance criteria (pass/fail)

| AC | Result | Evidence |
|----|--------|----------|
| Clinician create invite → one-time token + hash stored | **PASS** | `test_create_invite_201_returns_token_once`; service hash test |
| Redeem valid invite → patient JWT with `exp` | **PASS** | `test_redeem_invite_200_returns_patient_jwt_with_exp` |
| Reuse invite → 410 | **PASS** | `test_redeem_invite_410_when_already_used` |
| Expired invite → 410 | **PASS** | `test_redeem_invite_410_when_expired` |
| Redeem works with `ALLOW_DEV_AUTH=false` | **PASS** | `test_redeem_invite_available_when_dev_auth_disabled` |
| Expired patient JWT → 401 on diary | **PASS** | `test_expired_patient_jwt_rejected_on_protected_route` |
| Login `?invite=` → `/diario` | **PASS** | Playwright sprint13 redeem test |
| Dashboard Invitar al diario + copyable link | **PASS** | Playwright create-invite test |
| Role redirects unchanged | **PASS** | Sprint 12 e2e regression (3/3) |
| Dev-login still gated | **PASS** | Existing auth tests + redeem-when-disabled |

## Commands run

```bash
pytest tests/test_diary_invite*.py tests/test_auth_dev_login.py -q   # 17 passed
cd frontend && npm test -- --run                                     # 44 passed
npm run lint && npm run build                                        # clean
npx playwright test e2e/sprint13-diary-invite.spec.js \
  e2e/sprint12-patient-diary.spec.js                                 # 5 passed
```

## Risks / residual

| Risk | Severity | Note |
|------|----------|------|
| Invite link leak until redeem/expiry | Medium | TTL + single-use + hash-at-rest |
| Clinician login still needs prod path | Medium | `US-AUTH-CLINICIAN-PROD` |
| Tokens without `exp` still accepted | Low | `US-AUTH-JWT-HARDEN` |
| Existing DBs need `patient_diary_invites` DDL | Medium | Apply `infra/init.sql` fragment / migrate |

## Handoff

- Backlog item ID: US-DIARY-AUTH-PROD
- Scope: Invite create/redeem + patient JWT `exp` + SPA
- Acceptance criteria: **PASS**
- Test evidence: commands above
- Risks/issues: clinician prod auth + compose overlay follow-ons
- Next owner: **Planning Agent**
