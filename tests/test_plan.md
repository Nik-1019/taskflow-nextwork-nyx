# TaskFlow Test Plan (Sprint 1)

Owner: Logan (QA) · Issue #8 · Scope: smoke tests for Sprint 1 deliverables.

## Backend API (FastAPI, pytest + pytest-asyncio + httpx)

| ID | Area | Test Case | Expected Result |
|---|---|---|---|
| BE-1 | AUTH-3 | Hash password with Argon2id, verify same+wrong plaintext | verify(correct)=True, verify(wrong)=False; hash starts `$argon2id$` |
| BE-2 | AUTH-7 | POST /v1/auth/login with valid creds | 200; JSON has access_token (JWT, 15m exp) and refresh_token cookie (httpOnly, Secure, SameSite=Lax) |
| BE-3 | AUTH-7 | POST /v1/auth/refresh twice with same refresh token | 1st: 200 + new token pair; 2nd: 401 (rotation invalidates prior) |
| BE-4 | AUTH-8 | 5 failed logins in 10 min for one email | 6th attempt → 423 Locked; unlock email queued |
| BE-5 | AUTH-1 | POST /v1/auth/signup with invalid email | 422 with Pydantic validation error on `email` field |
| BE-6 | Sec | Access /v1/boards without/with expired JWT | 401 Unauthorized; no board data leaked |

## Frontend (React + Vite, Vitest + Testing Library)

| ID | Area | Test Case | Expected Result |
|---|---|---|---|
| FE-1 | Render | `<LoginForm />` mounts | Email + password inputs and Submit button present with accessible labels |
| FE-2 | Hook | `useAuth()` after successful login mock | `isAuthenticated===true`, `user.email` matches, no console errors |
| FE-3 | Query | TanStack Query `useCreateTask` mutation on 500 | Optimistic card removed on rollback; error toast rendered |
| FE-4 | A11y | Tab through login page | Focus order: email → password → submit; visible focus ring on each |

## CI Gate
- PR fails if either `pytest` or `npm test` exits non-zero, or coverage < baseline.
- Lint (ruff/mypy, eslint/tsc) must pass before test stage runs.
