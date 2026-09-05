# Architecture — TaskFlow

> Version: 1.0.0 · Status: Design Approved
> Author: Engineering Team · Date: September 2026

This document describes the technical architecture of TaskFlow, an AI-powered project management platform. It covers the frontend stack, backend services, data layer, infrastructure, and deployment model.

---

## 1. High-Level System Design

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────────────┐  │
│  │  Web App    │  │  Mobile Web │  │  Embedded Widget (iframe)       │  │
│  │  (React 18) │  │  (PWA)      │  │  (partner integrations)          │  │
│  └──────┬──────┘  └──────┬──────┘  └─────────────────────────────────┘  │
└─────────┼────────────────┼─────────────────────────────────────────────┘
          │ HTTPS / WSS    │
          ▼                ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CDN / EDGE (AWS CloudFront)                    │
│         Static assets (JS/CSS/images)  ·  DDoS protection ·  Geo-caching │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           API GATEWAY (AWS API Gateway + Lambda@Edge)    │
│   Rate limiting (100 req/min/user) ·  Auth validation ·  Request routing  │
└─────────────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           BACKEND SERVICES (AWS ECS Fargate)             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │
│  │  API Server  │  │  Real-Time   │  │  AI Service  │  │  Notification│  │
│  │  (FastAPI)   │  │  (WebSocket  │  │  (Python +   │  │  (Celery +   │  │
│  │              │  │  + Redis)    │  │  OpenAI)     │  │  SendGrid)   │  │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬───────┘  │
│         └────────────────┴─────────────────┴─────────────────┘          │
└─────────────────────────────────────────────────────────────────────────┘
          │              │                │                 │
          ▼              ▼                ▼                 ▼
┌─────────┴────────┐ ┌──────────┴──────┐ ┌──────────┴────────┐ ┌──────┴──────┐
│  PostgreSQL 16  │ │  Redis 7       │ │  OpenAI /         │ │  S3 (files) │
│  (AWS RDS)      │ │  (ElastiCache) │ │  Anthropic APIs   │ │             │
└─────────────────┘ └───────────────┘ └───────────────────┘ └─────────────┘
```

---

## 2. Frontend — React + TypeScript

### 2.1 Technology Stack
- **Framework:** React 18 (Concurrent Features, Suspense)
- **Language:** TypeScript 5.5 (strict mode enabled)
- **Styling:** Tailwind CSS 3.4 + Headless UI components
- **State Management:** Zustand (lightweight) for global state; TanStack Query (React Query) for server-state caching
- **Routing:** React Router 6 (code-splitting per route module)
- **Real-Time:** Socket.IO client (WebSocket fallback)
- **Forms:** React Hook Form + Zod schema validation
- **Rich Editor:** TipTap / ProseMirror for task descriptions
- **Charts:** Recharts for burndown, velocity, and analytics
- **Build:** Vite 5 (esbuild), with SWC for test transforms

### 2.2 Architecture Pattern — Feature-Based Folders
```
frontend/
  src/
    features/
      auth/          # login, signup, MFA, session management
      boards/        # Kanban board, drag-drop, column config
      tasks/         # task detail, comments, attachments, subtasks
      ai/            # AI assistant UI, suggestion cards, dashboard
      notifications/ # notification center, settings
      workspace/     # org settings, members, roles
    shared/         # components, hooks, utils, types
    app/            # App router, providers, layout shells
    styles/         # global CSS, Tailwind config, theme tokens
```

### 2.3 Key Design Decisions
- **Server-State Caching:** TanStack Query with 5-minute stale time, background refetch on window focus
- **Optimistic Updates:** All mutations (move, edit, assign) update the UI immediately; rollback on error
- **Code Splitting:** Route-level lazy loading; bundle target < 250KB initial chunk
- **Accessibility:** ARIA-compliant dropdowns, modal focus traps, keyboard shortcuts documented
- **PWA:** Service worker (Workbox) with offline board view; install prompt on supported browsers

### 2.4 Performance Targets
| Metric | Target |
|---|---|
| First Contentful Paint (FCP) | < 1.0s |
| Largest Contentful Paint (LCP) | < 1.5s |
| Time to Interactive | < 2.0s |
| Total JS bundle (initial) | < 250KB gzipped |

---

## 3. Backend — Python + FastAPI

### 3.1 Technology Stack
- **Language:** Python 3.12
- **Web Framework:** FastAPI (ASGI, async-first)
- **Data Validation:** Pydantic v2 (strict mode, custom validators)
- **ORM:** SQLAlchemy 2.0 (async via `asyncpg`)
- **Migrations:** Alembic 1.13 (autogenerate + manual review)
- **Task Queue:** Celery 5.3 (Redis broker, PostgreSQL result backend)
- **WebSocket:** Python `websockets` + Redis pub/sub for multi-node sync
- **Testing:** pytest + pytest-asyncio + httpx + Factory Boy
- **Lint / Format:** Ruff (replaces flake8, pyupgrade, isort), Black, mypy (strict)

### 3.2 Service Structure (Modular Monolith — v1.0)
```
backend/
  app/
    main.py              # FastAPI app factory, middleware, exception handlers
    config.py            # Pydantic-settings, env-based config
    db/                  # SQLAlchemy engine, session manager, connection pooling
    api/                 # Route modules (REST endpoints, versioned v1/)
    core/                # Auth, security, caching, email, logging, AI clients
    services/            # Business logic (tasks, boards, notifications, AI)
    models/              # SQLAlchemy declarative base + table definitions
    schemas/             # Pydantic request/response models (separated from DB)
    workers/             # Celery tasks (notifications, AI async, exports)
  tests/
  alembic/
  requirements/
    base.txt, dev.txt, prod.txt
```

### 3.3 Authentication & Authorization
- **JWT:** Access token (15 min) + refresh token (30 days, httpOnly cookie, Secure, SameSite=Lax)
- **Password Hashing:** Argon2id (time_cost=3, memory_cost=65536, parallelism=4)
- **RBAC:** Workspace-level roles — Owner, Admin, Editor, Viewer, Guest
- **Scopes:** Fine-grained permissions on boards, tasks, and AI settings per workspace

### 3.4 API Design Principles
- RESTful resource URLs (`/v1/workspaces/{id}/boards/{id}/tasks`)
- JSON:API-style pagination (`limit`, `cursor` based, not offset)
- Request/response schemas in Pydantic; auto-generated OpenAPI docs
- Rate limits: 100 req/min/user, 2,000/min/workspace, 10/min/AI endpoint
- Versioning: `/v1/` with sunset policy documented

---

## 4. Database — PostgreSQL 16

### 4.1 Schema Design (Key Tables)

**Workspaces** (`workspaces`)
- `id` UUID PK · `name` (varchar 100) · `slug` (unique) · `plan_tier` (free/pro/enterprise) · `settings` (JSONB) · `created_at` / `updated_at`

**Users** (`users`)
- `id` UUID PK · `email` (unique, indexed) · `password_hash` · `mfa_secret` · `email_verified` · `timezone` · `locale`

**Workspace Members** (`workspace_members`)
- `id` UUID PK · `workspace_id` FK · `user_id` FK · `role` (enum) · `joined_at` · `invited_by`

**Boards** (`boards`)
- `id` UUID PK · `workspace_id` FK · `name` · `type` (kanban/scrum/custom) · `columns` (JSONB array) · `wip_limits` (JSONB) · `is_template`

**Tasks** (`tasks`)
- `id` UUID PK · `board_id` FK · `assignee_id` FK · `title` · `description` (text) · `status` · `priority` · `due_at` · `label_ids` (array) · `parent_task_id` (self-FK) · `custom_fields` (JSONB) · `ai_suggestions` (JSONB)

**Comments** (`task_comments`)
- `id` UUID PK · `task_id` FK · `user_id` FK · `content` (text) · `parent_comment_id` (threading) · `mentions` (array of UUIDs)

**Notifications** (`notifications`)
- `id` UUID PK · `user_id` FK · `type` (enum) · `payload` (JSONB) · `read_at` · `delivered_at` · `channel` (in_app/email/push/slack)

**Audit Log** (`audit_logs`)
- `id` UUID PK · `actor_id` · `target_type` · `target_id` · `action` · `changes` (JSONB) · `ip_address` · `user_agent`

### 4.2 Indexing Strategy
- **B-tree:** `users(email)`, `workspaces(slug)`, `boards(workspace_id)`, `tasks(board_id, status)`, `notifications(user_id, read_at)`
- **GIN:** `tasks(label_ids)`, `tasks(custom_fields)`, `workspaces(settings)`, `audit_logs(changes)`
- **Partial:** `tasks(due_at)` where `due_at IS NOT NULL`; `notifications(delivered_at)` where `read_at IS NULL`

### 4.3 Performance Expectations
- Board load (100 tasks): < 200ms
- Full-text search (10,000 tasks): < 300ms (PostgreSQL tsvector + GIN)
- Complex query (filtered + sorted): < 500ms
- Concurrent write load (100 users): no deadlocks (row-level locking + optimistic concurrency)

### 4.4 Backup & Recovery
- **RDS automated:** Daily snapshots, 35-day retention
- **Point-in-time recovery:** 5-minute intervals, 35 days
- **Cross-region:** Read replicas in `us-west-2`, `eu-central-1`
- **Encryption:** AWS KMS (AES-256 at rest, TLS 1.3 in transit)

---

## 5. Cache & Real-Time — Redis 7

### 5.1 Usage Patterns
| Pattern | Key Structure | TTL | Purpose |
|---|---|---|---|
| User session | `session:{jwt_sub}` | 15 min | Auth state |
| Board state | `board:{id}:state` | 60 sec | Real-time board snapshot |
| AI suggestions | `ai:{user_id}:{task_id}` | 5 min | Cached AI results |
| Rate limits | `rl:{user_id}` | Rolling 1 min | Request throttling |
| Search cache | `search:{hash}` | 10 min | Query results |
| Pub/Sub | `channel:{board_id}` | Persistent | WebSocket broadcast |

### 5.2 Real-Time Sync Architecture
- Each board creates a Redis pub/sub channel (`channel:{board_id}`)
- All connected clients subscribe to the channel via WebSocket
- Server publishes change events (task moved, comment added, presence update)
- Multi-node deployment uses Redis as the shared message bus (no sticky sessions required)

---

## 6. AI Layer

### 6.1 Providers
- **Primary:** OpenAI GPT-4o (fast, high-quality reasoning)
- **Secondary:** Anthropic Claude 3 Sonnet (long-context tasks)
- **Embeddings:** OpenAI `text-embedding-3-small` (768 dims) for similarity search
- **Rate limits:** 500 req/min per workspace on AI endpoints

### 6.2 AI Services (Python)
- **Task Suggestions:** Analyze board context + user history → rank priorities + recommend assignee
- **Risk Detection:** Predict milestone miss probability using historical velocity data
- **Description Generation:** Generate structured descriptions from 2-3 sentence briefs
- **Standup Digest:** Summarize yesterday's board changes + current blockers
- **Duplicate Detection:** Embedding similarity over task descriptions (threshold 0.92)

### 6.3 Data Privacy
- All AI requests include `user` context with workspace isolation
- No task content is retained by provider APIs (zero-retention contracts)
- All AI calls logged to audit table (not for training, for compliance)

---

## 7. Infrastructure — AWS

### 7.1 Compute (ECS Fargate)
- **Service Type:** Fargate (serverless containers, no EC2 management)
- **Configuration:** 2 vCPU / 4 GB RAM per task; minimum 2 tasks always running
- **Auto-scaling:** Target 70% CPU / 60% memory; scale out 2-10 tasks; scale in 5 min cooldown
- **Region:** `us-east-1` (primary), `us-west-2` (DR), `eu-central-1` (EU data residency)

### 7.2 Storage
- **RDS PostgreSQL:** Multi-AZ, 100 GB SSD (gp3), automated backups
- **S3 Buckets:**
  - `taskflow-uploads-{env}` — user attachments (encrypted, versioning)
  - `taskflow-logs-{env}` — application logs (lifecycle 90 days → Glacier)
- **ElastiCache (Redis):** Cluster mode disabled; 2 shards, 2 replicas per shard

### 7.3 Networking
- **VPC:** 3-tier (public / private / database) with Network ACLs
- **ALB:** Application Load Balancer with WAF, TLS 1.3, health checks
- **Security Groups:** Least-privilege (only ALB → ECS; ECS → RDS/Redis on specific ports)
- **PrivateSubnets:** ECS tasks, RDS, ElastiCache; no public IP

### 7.4 Security
- **Encryption:** At rest (KMS) + in transit (TLS 1.3)
- **Secrets:** AWS Secrets Manager (DB passwords, API keys, JWT secrets)
- **WAF:** Rate-based rules (100 req/min), geo-blocking (optional), SQLi/XSS patterns
- **CloudTrail:** All API and console actions logged; 1 year retention
- **IAM:** Service roles per component (no long-lived credentials in code)

### 7.5 CI / CD (GitHub Actions)
- **Build:** Docker image build → push to ECR (tagged by commit SHA + `latest`)
- **Test:** pytest suite (unit + integration) + Lighthouse audit; must pass 100% before deploy
- **Deploy:** ECS service update with rolling deployment (10% traffic shift, 2 min health check)
- **Rollback:** Previous image tagged `rollback-{version}`; restore in < 3 minutes

---

## 8. Monitoring & Observability

| System | Tool | Purpose |
|---|---|---|
| Metrics | Datadog / AWS CloudWatch | CPU, memory, DB connections, API latency |
| Logs | CloudWatch Logs + Datadog | Structured JSON; 90-day retention; alert rules |
| Tracing | AWS X-Ray | End-to-end request traces across services |
| Alerting | PagerDuty / Slack | Critical: service down, DB replication lag, AI provider outage |
| Uptime | Status page + synthetic checks | 99.9% SLA; 4-hour RTO for critical failures |

---

## 9. Deployment Model

### 9.1 Environments
| Env | Purpose | Infrastructure |
|---|---|---|
| `dev` | Feature development | Single Fargate task, local RDS (Docker), mock AI |
| `staging` | QA + demo | 2 Fargate tasks, mirrored RDS (refresh from prod nightly), real AI keys |
| `prod` | Customer-facing | 2-10 Fargate tasks (auto), multi-AZ RDS, full WAF, all integrations |

### 9.2 Data Residency
- US customers: `us-east-1`
- EU customers: `eu-central-1` (workspaces forced to EU region at creation)
- No cross-region data replication by default (user-configurable)

---

## 10. Non-Functional Requirements

| Category | Requirement |
|---|---|
| **Availability** | 99.9% uptime (43.8 min/mo max downtime) |
| **Scalability** | 100K users / 1M tasks; horizontal scale to 10 Fargate tasks |
| **Latency** | API p95 < 300ms; real-time sync < 500ms; board load < 2s |
| **Durability** | RDS backups 35 days; S3 versioning 90 days; no unrecoverable data loss |
| **Security** | SOC 2 Type II (target Q2 2027); GDPR; encryption everywhere |
| **Compliance** | Data export (GDPR Article 20) within 30 days of request |

---

## 11. Technology Decisions Log

| Decision | Choice | Rationale | Alternative Considered |
|---|---|---|---|
| Frontend framework | React 18 | Ecosystem, concurrent features, team expertise | Vue 3 (rejected: smaller hiring pool) |
| Backend framework | FastAPI | Async native, auto-docs, Pydantic validation | Django / Flask (rejected: sync-first, heavy ORM) |
| Database | PostgreSQL 16 | ACID, JSONB, full-text, mature ecosystem | MongoDB (rejected: consistency needs) |
| Cache / Pub-Sub | Redis 7 | Fast, multi-pattern (cache + pub/sub + rate limit) | Memcached (rejected: no pub/sub) |
| Container platform | AWS Fargate | No server management, fine-grained scaling | EKS / EC2 (rejected: operational overhead) |
| AI Provider | OpenAI + Anthropic | Best reasoning, cost-effective at scale | Self-hosted Llama (rejected: ops overhead) |
| State management | Zustand | Minimal, no re-renders, TypeScript-first | Redux / MobX (rejected: boilerplate) |

---

*This architecture is designed for the v1.0 release. Post-launch, we will evolve through user feedback, load-testing results, and security audits — with a targeted v1.1 that introduces native mobile apps, enhanced analytics, and a plugin marketplace.*
