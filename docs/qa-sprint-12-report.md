# QA Report — Sprint 12 (US-DIARY-UI-PATIENT)

**Date:** 2026-07-16  
**Owner:** QA Agent  
**Branch / PR:** `cursor/sprint-12-diary-patient-ui-2591` / [#9](https://github.com/andresviverosw/holisticare/pull/9)  
**Scope:** US-DIARY-UI-PATIENT  

## Verdict

**PASS — ready for Planning Agent backlog closeout / merge**

No blocking defects. Patient self-serve diary ships with UUID-bound JWT (dev/pilot); production IdP remains follow-on.

## Acceptance criteria (pass/fail)

| AC | Result | Evidence |
|----|--------|----------|
| `/diario` form bound to JWT UUID `sub` (read-only / copyable) | **PASS** | E2E: code shows PATIENT; `PatientDiary.jsx` uses `sub` only |
| Save → `POST /rag/diary` → history | **PASS** | E2E save + history row; reuses `diaryBuilder` |
| Invalid scores/date block API | **PASS** | `diaryBuilder.test.js` + form `validateDiaryForm` before save |
| Blank notes → `notes_es: null`; present trimmed | **PASS** | `diaryBuilder.test.js` |
| UI never offers another patient id | **PASS** | No patient-id input on `/diario` |
| Clinician on `/diario` → `/dashboard` | **PASS** | E2E redirect test; `RequirePatient` |
| Patient on `/dashboard` → `/diario` | **PASS** | E2E redirect test; `RequireClinician` |
| Dev-login patient + UUID when `ALLOW_DEV_AUTH=true` | **PASS** | `test_auth_dev_login.py` + Login patient path |
| Dev-login absent when `ALLOW_DEV_AUTH=false` | **PASS** | Existing 404 test (route not registered) |

## Commands run

```bash
cd backend && python -m pytest tests/test_auth_dev_login.py -q   # 5 passed
cd frontend && npm test -- --run                                 # 42 passed
cd frontend && npm run lint                                      # clean
cd frontend && npm run build                                     # ok
cd frontend && npx playwright test e2e/sprint12-patient-diary.spec.js  # 3 passed
```

## Risks / residual

| Risk | Severity | Note |
|------|----------|------|
| UUID-in-JWT ≠ production identity | Medium | Tracked as `US-DIARY-AUTH-PROD` |
| `ALLOW_DEV_AUTH` left on in prod | High | Ops checklist / compose prod overlay |
| Clinician-proxy vs self-report confusion | Low | Dashboard still labeled «practicante»; patient page «Mi diario» |

## Handoff

- Backlog item ID: US-DIARY-UI-PATIENT
- Scope: Patient `/diario` + patient JWT issuance (dev) + role guards
- Acceptance criteria: **PASS**
- Test evidence: commands above
- Risks/issues: production auth follow-on
- Next owner: **Planning Agent**
