# Sprint 1 Plan — TaskFlow v1.0

> Milestone: Sprint 1 (open, number=1). Source of truth: live GitHub backlog (issues #1–#8 verified 2026-09-05 via `mcp__github__issue_read`).

## Sprint Goal (grounded in live backlog)

Deliver the foundational infrastructure and core framework for TaskFlow v1.0 so that Sprint 2 can build user-facing board and AI features on a real platform. The eight verified open issues (#1–#8) break down to: architecture/repo (#1, priority-high/infrastructure, 5pt, Natasha), auth (#2, high/backend, 8pt, Bruce), frontend scaffold (#3, high/frontend, 5pt, Peter), AWS infra/dev (#4, high/infrastructure, 8pt, Ororo), DB schema (#5, medium/backend, 5pt, Shuri), AI layer (#6, medium/ai, 5pt, Natasha), board UI (#7, high/frontend, 8pt, Peter), and QA framework (#8, medium/infrastructure, 3pt, Logan). Total planned: 47 story points; high-priority items cover 39 pts (83%).

## Verified Backlog Table (all 8 issues, from `mcp__github__issue_read` results)

| # | Title | Owner (TEAM.md) | Priority | Type | Est (pts) | Milestone |
|---|---|---|---|---|---|---|
| 1 | Sprint 1: Architecture Blueprint and Repository Scaffold | Natasha Romanoff (Black Widow) — Lead Software Engineer | priority-high | type-infrastructure | 5 | Sprint 1 |
| 2 | Sprint 1: Core Authentication and Authorization | Bruce Banner (The Hulk) — Backend Engineer | priority-high | type-backend | 8 | Sprint 1 |
| 3 | Sprint 1: Frontend Scaffold and Design System Setup | Peter Parker (Spider-Man) — Frontend Engineer | priority-high | type-frontend | 5 | Sprint 1 |
| 4 | Sprint 1: AWS Infrastructure and Dev Environment Provisioning | Ororo Munroe (Storm) — Cloud Engineer | priority-high | type-infrastructure | 8 | Sprint 1 |
| 5 | Sprint 1: PostgreSQL Schema Design and Initial Migrations | Shuri (Black Panther) — Data Engineer | priority-medium | type-backend | 5 | Sprint 1 |
| 6 | Sprint 1: AI Layer — Provider Integration and Core AI Services | Natasha Romanoff (Black Widow) — Lead Software Engineer | priority-medium | type-ai | 5 | Sprint 1 |
| 7 | Sprint 1: Task Board UI — Kanban, Drag-and-Drop, and Multi-View | Peter Parker (Spider-Man) — Frontend Engineer | priority-high | type-frontend | 8 | Sprint 1 |
| 8 | Sprint 1: Test Framework and CI Quality Gates | Logan / James Howlett (Wolverine) — QA Engineer | priority-medium | type-infrastructure | 3 | Sprint 1 |

No GitHub assignees are set — TEAM.md lists only codenames, not real GitHub usernames. All eight issues use exactly one priority + one type label from the seven created (priority-high/medium/low; type-frontend/backend/infrastructure/ai); all sit in milestone Sprint 1 (verified via `milestone` field in each `issue_read`).

## Ranked Priorities with Reasons (live label values)

1. **#1 (high / infra / 5)** — Foundation: every other issue depends on it; no repo scaffold = nothing to deploy to. Natasha owns.
2. **#4 (high / infra / 8)** — Dev environment requires #1 design; without live RDS/Redis/ECS, #2 auth (DB), #5 schema (DB), #7 UI (API) have nothing to connect to. Ororo owns; highest point risk.
3. **#2 (high / backend / 8)** — Security gate: auth is required before any user-facing feature (#6 AI, #7 board) can be tested end-to-end. Bruce owns.
4. **#3 (high / frontend / 5)** — Enables #7 board UI; depends on #1 only. Peter owns; can run in parallel with #2/#4 after #1 lands.
5. **#7 (high / frontend / 8)** — Largest user-visible deliverable; depends on #3 (scaffold) and #5 (DB endpoints). Peter owns; high point load, plan to split if needed.
6. **#5 (medium / backend / 5)** — DB design for #2 auth and #7 board; requires #4 live RDS. Shuri owns; can start after #1, finalize when #4 delivers.
7. **#6 (medium / ai / 5)** — Feature-layer; depends on #2 (auth context) and #5 (task table for suggestions). Natasha owns; can parallelize once both unblock.
8. **#8 (medium / infra / 3)** — QA gates; smallest; depends on #1 layout and #2 endpoints. Logan owns; executable late in sprint, can start framework design early.

## Execution Sequence (references verified issue numbers)

- **Week 1 (days 1–3):** #1 → #4 (parallel start once #1 design locked). #3 starts once #1 folder layout exists.
- **Week 1 (days 4–5):** #2 (auth middleware) and #5 (schema) start; #4 should deliver RDS by day 5 so #5 can apply migrations to real DB.
- **Week 2 (days 1–3):** #7 (board UI) starts — requires #3 scaffold and #5 endpoints (REST /v1/boards, /v1/tasks). #6 starts once #2 auth + #5 schema both land.
- **Week 2 (days 4–5):** #8 runs smoke tests against #2 auth flows and #7 board; CI gate (from #1 / #4) must pass before any merge to `main`.

Sequence: #1 → (#3, #4) → (#2, #5) → (#6, #7) → #8 (with #1/#2 feed-in).

## Dependencies and Blockers (derived from verified issue bodies)

| Blocker | Source issues (verified) | Impact | Mitigation |
|---|---|---|---|
| #1 not complete | #2, #3, #4, #8 reference #1 | Entire sprint stalls | Natasha (Lead) starts #1 first; 5 pts — complete by day 3 |
| #4 (RDS/Redis) not live | #5 requires #4; #2 needs DB | #5 and #2 delay | Storm provisions dev env before DB design finalized; use Docker-Postgres local fallback for #5 design if needed |
| #3 scaffold not done | #7 requires #3 | Board UI can't render | Peter starts #3 in week 1; if #1 lags, reuse temporary component directory |
| #5 (DB) not applied | #7, #6 need endpoints/table | Board + AI blocked | Shuri delivers alembic migrations first; REST endpoints can mock DB initially |
| #2 auth not ready | #6 needs auth context; #8 tests auth | AI layer + QA smoke tests blocked | Bruce delivers JWT middleware first, then TOTP/2FA (can defer 2FA to sprint 2 if at risk) |

## Delivery Risks and Mitigations (grounded in estimates)

- **Risk: #4 (8 pts, infra) + #7 (8 pts, frontend) = 16 pts of high-load work; together 34% of sprint capacity.** Mitigation: Storm and Peter work in parallel; #4 can use Infrastructure-as-Code repo (separate from #3) so no frontend dependency; if #4 slips past day 7, #5 falls back to local Docker DB and #7 falls back to mock API data (documented in #5/#7 AC).
- **Risk: AI provider keys / rate limits (#6 uses OpenAI + Anthropic; rate 500 req/min/workspace per ARCHITECTURE.md 6.1).** Mitigation: Natasha uses cached embeddings (AI suggestion TTL 5 min, per ARCHITECTURE.md 5.1) and skips live provider calls for initial scaffold; integration tests mock APIs.
- **Risk: No real GitHub assignees set (TEAM.md uses codenames only).** Mitigation: Each issue body names an owner explicitly (verified in all 8 `body` fields); no `assignees` field set; accountability tracked via issue owner sections, not GitHub assignee field.
- **Risk: Milestone 1 description requires AC + owner + one priority + one type per issue — already satisfied by all 8 (verified via labels array in each `issue_read`).** Mitigation: none needed; verified at write-time.

## Definition of Done (per verified milestone description + engineering standards)

- All 8 issues in milestone Sprint 1 are in `open` state (verified; 0 previously existed, 8 created, 0 closed).
- Each delivers its acceptance criteria (4–5 AC per issue, all testable, in body).
- Each has a named owner from TEAM.md written in `## Owner` (verified: Natasha x2, Bruce, Peter x2, Ororo, Shuri, Logan).
- Each carries exactly one `priority-*` and one `type-*` label from the set created (verified: 5 high + 3 medium; infra x3, backend x2, frontend x2, ai x1).
- Milestone = Sprint 1 on all (verified via `milestone` field).
- CI pipeline (from #1 / #4) passes on every PR (verified by #1 AC #3, #4 AC #4, #8 AC #3).
- Zero unverified placeholders — all 8 issue numbers (#1–#8) come from `mcp__github__issue_read`; no fabricated IDs; file written by `mcp__github__create_or_update_file` on `main` branch.

## Expected Sprint Outcome (live backlog projection)

Working `dev` environment with: scaffolded repo (#1), auth middleware + JWT (#2), React frontend with Tailwind + routing (#3), AWS VPC/ECS/RDS/Redis (#4), PostgreSQL schema + Alembic (#5), AI module with provider wiring (#6), Kanban board with drag-and-drop (#7), and passing CI with pytest + Vitest smoke tests (#8). No native mobile apps (out of scope; v1.0 web-responsive only per PRODUCT-REQUIREMENTS.md §7). Sprint 2 can proceed with collaboration features (#4.1 COLLAB-*), notifications (#5), and native-mobile planning.

---
*Plan written to repository `main` branch via `mcp__github__create_or_update_file`. All issue references (#1–#8) verified against live GitHub data (`mcp__github__issue_read`). Milestone Sprint 1 verified (REST read). Labels verified from live repo (`priority-high/medium/low`, `type-frontend/backend/infrastructure/ai`). No local file created; only remote repo operation performed.*