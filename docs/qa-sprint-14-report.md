# QA Report — Sprint 14 (US-AUTH-CLINICIAN-PROD)

**Date:** 2026-07-16  
**Owner:** QA Agent  
**Branch / PR:** `cursor/sprint-14-clinician-auth-exec-2591` / [#13](https://github.com/andresviverosw/holisticare/pull/13)  
**Scope:** US-AUTH-CLINICIAN-PROD  

## Verdict

**PASS — ready for Planning Agent backlog closeout / merge**

No blocking defects. Clinicians can sign in with username/password when `ALLOW_DEV_AUTH=false`.

## Acceptance criteria (pass/fail)

| AC | Result | Evidence |
|----|--------|----------|
| Seeded clinician correct password → JWT with role, sub, exp | **PASS** | `test_password_login_200_returns_jwt_with_exp` |
| Wrong password / unknown user → 401 generic | **PASS** | `test_password_login_401_wrong_password` |
| Inactive user → 401 | **PASS** | `test_password_login_401_inactive_user` |
| Login works with `ALLOW_DEV_AUTH=false` | **PASS** | `test_password_login_available_when_dev_auth_disabled` |
| Seed idempotent | **PASS** | `test_create_or_update_user_updates_existing` + seed CLI tests |
| Passwords hashed only | **PASS** | `test_hash_and_verify_password_roundtrip` / create stores hash |
| SPA password form → `/dashboard` | **PASS** | Playwright sprint14 |
| Patient invite + redirects unchanged | **PASS** | Sprint 13 e2e regression |
| Dev-login still gated | **PASS** | auth_dev_login + login-when-disabled test |

## Commands run

```bash
pytest tests/test_user_service.py tests/test_auth_password_login.py \
  tests/test_seed_clinician.py tests/test_auth_dev_login.py \
  tests/test_diary_invite_api.py -q    # 24 passed
cd frontend && npm test -- --run       # 44 passed
npm run lint && npm run build          # clean
npx playwright test e2e/sprint14-clinician-login.spec.js \
  e2e/sprint13-diary-invite.spec.js e2e/clinician-smoke.spec.js  # 8 passed
```

## Risks / residual

| Risk | Severity | Note |
|------|----------|------|
| Weak seed password | High | Ops must set strong env password; never commit |
| Brute-force on `/auth/login` | Medium | Follow-on rate limit |
| Existing DBs need `app_users` DDL | Medium | Documented in setup/user guide |
| passlib unused; bcrypt direct | Low | Intentional (passlib×bcrypt5 incompatibility) |

## Handoff

- Backlog item ID: US-AUTH-CLINICIAN-PROD
- Scope: app_users + bcrypt + POST /auth/login + seed + Login SPA
- Acceptance criteria: **PASS**
- Test evidence: commands above
- Risks/issues: rate limit / compose overlay follow-ons
- Next owner: **Planning Agent**
