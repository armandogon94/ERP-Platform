# ERP Platform — Task List

## Phase 1: Foundation (Slice 0 — Docker + Scaffold)

- [x] **Task 0.1:** Docker Compose + Makefile (S) — docker-compose.yml with 6 services, Makefile, .env.example
- [x] **Task 0.2:** Django Project Skeleton (M) — Dockerfile, settings, URLs, Celery, requirements
- [x] **Task 0.3:** Backend Smoke Tests (S) — conftest.py, test_api_root_returns_200
- [x] **Task 0.4:** React Project Skeleton (M) — Dockerfile, Vite, TypeScript, Axios client, Router
- [x] **Task 0.5:** Frontend Smoke Tests (S) — App.test.tsx, vitest config

### Checkpoint: Slice 0
- [x] `make dev` starts all 6 services
- [x] Django at :14000, React at :14500
- [x] `make test` passes both suites (4 backend + 3 frontend)
- [x] Commit: `feat: scaffold Docker infrastructure with Django + React + Celery`

---

## Phase 2: Core Backend (Slice 1 — Models + Auth + RBAC)

- [x] **Task 1.1:** TenantModel + Company + UserProfile (M) — abstract base, models, factories, tests
- [x] **Task 1.2:** JWT Auth endpoints (M) — login, logout, refresh, serializers, tests
- [x] **Task 1.3:** RBAC Models (M) — Role, Permission, IndustryRoleTemplate, provisioning service, tests
- [x] **Task 1.4:** Middleware + DRF Permissions (M) — CompanyRoleContextMiddleware, ModulePermission, tests
- [ ] **Task 1.5:** Module System (M) — ModuleRegistry, ModuleConfig, Menu, API, tests
- [ ] **Task 1.6:** Sequence + AuditLog + Notification (M) — Sequence generator, signals, models, tests
- [ ] **Task 1.7:** Seed Data (M) — 10 companies, 50 users, 80 role templates, management commands, tests

### Checkpoint: Core Backend
- [ ] 40+ backend tests pass
- [ ] JWT auth end-to-end
- [ ] RBAC enforced (403)
- [ ] Company isolation verified
- [ ] Commit: `feat: core backend with companies, auth, RBAC, sequences, and seed data`

---

## Phase 3: Core Frontend (Slice 1 — Auth + Layout)

- [ ] **Task 1.8:** Frontend Auth (M) — Zustand authStore, LoginForm, JWT interceptor, tests
- [ ] **Task 1.9:** Frontend Layout (M) — AppLayout, TopNavbar, Sidebar, AppSwitcher, theme, tests

### Checkpoint: Slice 1 Complete
- [ ] Login as admin@novapay.com → blue-branded dashboard
- [ ] Login as admin@dentaflow.com → cyan-branded dashboard
- [ ] App Switcher shows 13 modules
- [ ] 403 on unauthorized module access
- [ ] Commit: `feat: core frontend with login, layout, app switcher, and theming`

---

## Upcoming Slices (to be broken down after Slice 1)

- [ ] **Slice 2:** View System (Form/List/Kanban) — XL, break into tasks after Slice 1
- [ ] **Slice 3:** Industry Config System — M
- [ ] **Slices 4–6:** HR, Calendar, Inventory (parallelizable) — L, XL
- [ ] **Slices 7–8:** Purchasing, Sales — L
- [ ] **Slices 9–10:** Accounting, Invoicing — XL, L
- [ ] **Slices 11–14:** Fleet, Projects, Manufacturing, Helpdesk — M–L
- [ ] **Slices 15–19:** POS, Pivot/Graph, Reports, Seed Data, WebSocket — M–XL
