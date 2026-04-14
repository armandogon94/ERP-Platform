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
- [x] **Task 1.5:** Module System (M) — ModuleRegistry, ModuleConfig, Menu, API, tests
- [x] **Task 1.6:** Sequence + AuditLog + Notification (M) — Sequence generator, signals, models, tests
- [x] **Task 1.7:** Seed Data (M) — 10 companies, 50 users, 80 role templates, management commands, tests

### Checkpoint: Core Backend
- [x] 80 backend tests pass
- [x] JWT auth end-to-end
- [x] RBAC enforced (403)
- [x] Company isolation verified
- [x] Commit: `feat: implement Slice 1 core multi-tenancy system`

---

## Phase 3: Core Frontend (Slice 1 — Auth + Layout)

- [x] **Task 1.8:** Frontend Auth (M) — Zustand authStore, LoginForm, JWT interceptor, tests
- [x] **Task 1.9:** Frontend Layout (M) — AppLayout, TopNavbar, Sidebar, AppSwitcher, theme, tests

### Checkpoint: Slice 1 Complete
- [x] 80 backend + 21 frontend = 101 tests passing
- [x] Protected routes redirect to login
- [x] Brand color applied to navbar
- [x] App Switcher with module grid
- [x] Commit: `feat: implement Slice 1 core multi-tenancy system`

---

## Phase 4: View System (Slice 2 — Form/List/Kanban)

- [x] **Task 2.1:** View + Action models (M) — ViewDefinition JSONB config, migration, 11 tests
- [x] **Task 2.2:** DynamicModelViewSet (M) — Generic CRUD viewset base with filtering/ordering, 4 tests
- [x] **Task 2.3:** ListView component (M) — Sortable columns, search, record count, 9 tests
- [x] **Task 2.4:** FormView component (M) — JSON-config-driven form renderer, 14 tests
- [x] **Task 2.5:** KanbanView component (M) — Drag-and-drop columns, card rendering, 10 tests
- [x] **Task 2.6:** Component library (S) — Button, Input, Select, Modal, Badge, 29 tests

### Checkpoint: Slice 2 Complete
- [x] ListView renders from JSON config with sort/search
- [x] FormView renders from JSON config with all field types
- [x] KanbanView renders columns with drag-drop
- [x] DynamicModelViewSet provides generic CRUD
- [x] 95 backend + 83 frontend = 178 tests pass
- [x] Commit: `feat: implement Slice 2 view system`

---

## Phase 5: Industry Config System (Slice 3)

- [ ] **Task 3.1:** IndustryConfigTemplate model + config_service (M) — model, merge_configs, get_resolved_config, tests
- [ ] **Task 3.2:** YAML config files + load_industry_config command (M) — 10 YAML files, pyyaml, management command, tests
- [ ] **Task 3.3:** Redis cache + signal invalidation (M) — cache layer, Django signals, graceful fallback, tests
- [ ] **Task 3.4:** Enhanced config API GET + PATCH (M) — resolved config response, PATCH overrides, tests
- [ ] **Task 3.5:** Frontend hooks useModuleConfig + useTerminology (M) — Zustand store, hooks, API functions, tests
- [ ] **Task 3.6:** AppLayout integration — API-driven modules (S) — replace hardcoded defaults, fallback, tests

### Checkpoint: Slice 3 Complete
- [ ] `GET /api/v1/core/modules/{id}/config/` returns resolved 3-tier config with terminology
- [ ] DentaFlow returns "Supply Room" for Warehouse, "Dental Supply" for Product
- [ ] AppLayout renders API-driven modules in sidebar and app switcher
- [ ] 178 + 30 = 208+ tests pass
- [ ] Commit: `feat: implement Slice 3 industry config system`

---

## Upcoming Slices

- [ ] **Slice 3:** Industry Config System — M
- [ ] **Slices 4–6:** HR, Calendar, Inventory (parallelizable) — L, XL
- [ ] **Slices 7–8:** Purchasing, Sales — L
- [ ] **Slices 9–10:** Accounting, Invoicing — XL, L
- [ ] **Slices 11–14:** Fleet, Projects, Manufacturing, Helpdesk — M–L
- [ ] **Slices 15–19:** POS, Pivot/Graph, Reports, Seed Data, WebSocket — M–XL
