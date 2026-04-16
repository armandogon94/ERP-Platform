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

- [x] **Task 3.1:** IndustryConfigTemplate model + config_service (M) — model, merge_configs, get_resolved_config, 22 tests
- [x] **Task 3.2:** YAML config files + load_industry_config command (M) — 10 YAML files, pyyaml, management command, 10 tests
- [x] **Task 3.3:** Redis cache + signal invalidation (M) — cache layer, Django signals, graceful fallback, 8 tests
- [x] **Task 3.4:** Enhanced config API GET + PATCH (M) — resolved config response, PATCH overrides, 9 tests
- [x] **Task 3.5:** Frontend hooks useModuleConfig + useTerminology (M) — Zustand store, hooks, API functions, 16 tests
- [x] **Task 3.6:** AppLayout integration — API-driven modules (S) — replace hardcoded defaults, fallback, 8 tests

### Checkpoint: Slice 3 Complete
- [x] `GET /api/v1/core/modules/{id}/config/` returns resolved 3-tier config with terminology
- [x] DentaFlow returns "Supply Room" for Warehouse, "Dental Supply" for Product
- [x] AppLayout renders API-driven modules in sidebar and app switcher
- [x] 144 backend + 99 frontend = 243 tests pass
- [x] Commit: `feat: implement Slice 3 industry config system`

---

## Phase 6: HR Module (Slice 4)

- [ ] **Task 4.1:** HR app + Employee + Department models (M) — Django app, TenantModel subclasses, migration, factories, model tests
- [ ] **Task 4.2:** LeaveRequest + Payroll models (M) — models, migration, factories, tests
- [ ] **Task 4.3:** HR API — CRUD endpoints (M) — ViewSets, serializers, URL registration under /api/v1/hr/, API tests
- [ ] **Task 4.4:** Frontend HR pages (M) — hr.ts API module, EmployeeListPage, EmployeeFormPage, App.tsx routes, tests

### Checkpoint: Slice 4 Complete
- [ ] `GET /api/v1/hr/employees/` returns company-scoped employees
- [ ] POST/PATCH/DELETE employees work with RBAC
- [ ] EmployeeListPage renders employees using ListView
- [ ] EmployeeFormPage renders form using FormView
- [ ] useTerminology used for "Employee" label (dental → "Staff Member")
- [ ] 243 + 40 = 283+ tests pass
- [ ] Commit: `feat: implement Slice 4 HR module`

---

## Upcoming Slices

Status as of 2026-04-16: **Slices 0–10 shipped** (see commits `3fe3cfc` through `e1b424d`). 628 tests passing (418 backend + 210 frontend).

See `SPEC.md §Vertical Slice Definitions` for full acceptance criteria per slice and `DECISION.md §D21–D32` for the decisions driving the remaining work. Order is fixed by D32.

### Tech-debt slices (must ship before Slice 11; see tasks/plan.md §Part 2)

**Slice 10.5 — UI tech-debt cleanup**
- [ ] 10.5.1 Include pending `InvoiceFormPage.test.tsx` in the slice's commit
- [ ] 10.5.2 QuotationFormPage tests (RED)
- [ ] 10.5.3 QuotationFormPage component + `api/sales.ts` helpers (GREEN)
- [ ] 10.5.4 Register `/sales/quotations/new` + `:id/edit` routes
- [ ] 10.5.5 Terminology retrofit tests for 11 pages (RED)
- [ ] 10.5.6 Apply `useTerminology` across 11 pages (GREEN)
- [ ] 10.5.7 Verification Gate + commit `refactor: Slice 10.5 — Quotation form, terminology retrofit`

**Slice 10.6 — Partner model**
- [ ] 10.6.1 Partner model tests (RED)
- [ ] 10.6.2 Partner model + factory + migration (GREEN)
- [ ] 10.6.3 Partner API tests (RED)
- [ ] 10.6.4 Partner ViewSet + serializer + URL at `/api/v1/core/partners/` (GREEN)
- [ ] 10.6.5 Add nullable Partner FKs to Sales/Invoicing/Purchasing (RED → GREEN)
- [ ] 10.6.6 Serializer support for Partner FK (create-time population of `customer_name`)
- [ ] 10.6.7 Data migration: backfill Partner rows from `customer_name`
- [ ] 10.6.8 Partner frontend (list + form + routes)
- [ ] 10.6.9 Partner picker in Quotation/SO/Invoice forms
- [ ] 10.6.10 Verification Gate + commit `feat: Slice 10.6 — Partner model unifies customers and vendors`

**Slice 10.7 — Sequence auto-generation**
- [ ] 10.7.1 `get_next_sequence` helper tests (RED)
- [ ] 10.7.2 `get_next_sequence` helper finalize (GREEN)
- [ ] 10.7.3 Per-model `save()` override tests for 7 entities (RED)
- [ ] 10.7.4 `save()` overrides on 7 models (GREEN)
- [ ] 10.7.5 Back-fill migrations (7 modules)
- [ ] 10.7.6 Verification Gate + commit `feat: Slice 10.7 — sequence auto-generation signals`

### Remaining module slices (Module Scaffold Pattern, 9 steps)

**Slice 11 — Fleet**
- [ ] 11.1 Scaffold `backend/modules/fleet/`
- [ ] 11.2 Model tests (RED)
- [ ] 11.3 Models + factories + migration (GREEN)
- [ ] 11.4 API tests (RED)
- [ ] 11.5 Serializers + ViewSets + URL include (GREEN)
- [ ] 11.6 Frontend tests (RED)
- [ ] 11.7 API client + 6 pages (GREEN)
- [ ] 11.8 Routes in `App.tsx`
- [ ] 11.9 Preview sweep + commit `feat: implement Slice 11 Fleet module`

**Slice 12 — Projects**
- [ ] 12.1 Scaffold `backend/modules/projects/`
- [ ] 12.2 Model tests (RED)
- [ ] 12.3 Models + factories + migration (GREEN)
- [ ] 12.4 API tests incl. `/progress/` action (RED)
- [ ] 12.5 Serializers + ViewSets + actions (GREEN)
- [ ] 12.6 Frontend tests (RED)
- [ ] 12.7 API client + pages + Task Kanban (GREEN)
- [ ] 12.8 Routes in `App.tsx`
- [ ] 12.9 Preview sweep + commit `feat: implement Slice 12 Projects module`

**Slice 13 — Manufacturing**
- [ ] 13.1 Scaffold `backend/modules/manufacturing/`
- [ ] 13.2 Model tests (RED)
- [ ] 13.3 Models + factories + migration (GREEN)
- [ ] 13.4 API tests incl. `/start/` + `/complete/` actions (RED)
- [ ] 13.5 Serializers + ViewSets + actions + Inventory StockMove integration (GREEN)
- [ ] 13.6 Frontend tests (RED)
- [ ] 13.7 API client + BOM + WorkOrder pages (GREEN)
- [ ] 13.8 Routes in `App.tsx`
- [ ] 13.9 Preview sweep + commit `feat: implement Slice 13 Manufacturing module`

**Slice 14 — Point of Sale**
- [ ] 14.1 Scaffold `backend/modules/pos/`
- [ ] 14.2 Model tests (RED)
- [ ] 14.3 Models + factories + migration + `POS` prefix in sequence auto-gen (GREEN)
- [ ] 14.4 API tests incl. `/close/` action (RED)
- [ ] 14.5 Serializers + ViewSets + actions (GREEN)
- [ ] 14.6 Frontend tests (RED)
- [ ] 14.7 API client + touch-friendly pages (GREEN)
- [ ] 14.8 Routes in `App.tsx`
- [ ] 14.9 Preview sweep + commit `feat: implement Slice 14 POS module`

**Slice 15 — Helpdesk**
- [ ] 15.1 Scaffold `backend/modules/helpdesk/`
- [ ] 15.2 Model tests (RED)
- [ ] 15.3 Models + factories + migration + `TKT` prefix in sequence auto-gen (GREEN)
- [ ] 15.4 API tests incl. `/resolve/` + `/reopen/` actions (RED)
- [ ] 15.5 Serializers + ViewSets + actions (GREEN)
- [ ] 15.6 Frontend tests (RED)
- [ ] 15.7 API client + Ticket/Category/Article pages + Kanban toggle (GREEN)
- [ ] 15.8 Routes in `App.tsx`
- [ ] 15.9 Preview sweep + commit `feat: implement Slice 15 Helpdesk module`

**Slice 16 — Reports/BI + Pivot + Graph**
- [ ] 16.1 Install `recharts`
- [ ] 16.2 Scaffold `backend/modules/reports/`
- [ ] 16.3 Model tests + extend `ViewDefinition.view_type` (RED)
- [ ] 16.4 Models + factories + migration (GREEN)
- [ ] 16.5 `/aggregate/` endpoint tests (RED)
- [ ] 16.6 `AggregationMixin` with whitelist of aggregatable fields (GREEN)
- [ ] 16.7 Apply mixin to 8+ existing ViewSets
- [ ] 16.8 Frontend tests — PivotView, GraphView, ReportBuilderPage (RED)
- [ ] 16.9 Implement PivotView + GraphView (Recharts) + ReportBuilderPage (GREEN)
- [ ] 16.10 Report module list/form pages + routes
- [ ] 16.11 Preview sweep + commit `feat: implement Slice 16 Reports BI + Pivot + Graph`

### Platform slices

**Slice 17 — Industry demo seeding**
- [ ] 17.1 Shared test harness for seed commands (RED)
- [ ] 17.2 Implement 7 seed commands for shipped modules (GREEN)
- [ ] 17.3 Implement 5 seed commands for Slice 11–15 modules (GREEN)
- [ ] 17.4 Implement `seed_reports_demo`
- [ ] 17.5 Meta-command tests (RED)
- [ ] 17.6 Implement `seed_industry_demo --company <slug>` + industry→modules map (GREEN)
- [ ] 17.7 Preview sweep + commit `feat: implement Slice 17 industry demo seeding`

**Slice 18 — Calendar polling sync**
- [ ] 18.1 `updated_since` filter tests (RED)
- [ ] 18.2 `updated_since` filter implementation (GREEN)
- [ ] 18.3 Upsert-by-`external_uid` with LWW tests (RED)
- [ ] 18.4 Upsert + LWW implementation (GREEN)
- [ ] 18.5 `/events/bulk/` tests (RED)
- [ ] 18.6 Bulk endpoint implementation (GREEN)
- [ ] 18.7 Document polling contract in `docs/CALENDAR-SYNC-POLLING.md`
- [ ] 18.8 Manual round-trip verification + commit `feat: implement Slice 18 calendar polling sync`

**Slice 19 — Polish pass**
- [ ] 19.1 ErrorBoundary / Skeleton / EmptyState / Breadcrumbs tests (RED)
- [ ] 19.2 Implement those four components (GREEN)
- [ ] 19.3 Wire into AppLayout + list pages
- [ ] 19.4 Per-company theming test (RED)
- [ ] 19.5 CSS custom properties from `brand_color` (GREEN)
- [ ] 19.6 Channels consumer test (RED)
- [ ] 19.7 `/ws/notifications/` consumer + post_save signals (GREEN)
- [ ] 19.8 `useNotifications` hook test (RED)
- [ ] 19.9 Hook + `NotificationBell` in TopNavbar (GREEN)
- [ ] 19.10 AuditLogTimelinePage test (RED)
- [ ] 19.11 AuditLogTimelinePage component (GREEN)
- [ ] 19.12 HomePage KPI tests (RED)
- [ ] 19.13 `/api/v1/core/home-kpis/` + HomePage (GREEN)
- [ ] 19.14 Cross-industry preview sweep + commit `feat: implement Slice 19 polish pass`

### Verification gate (every slice, non-negotiable)
1. `docker compose run --rm django python -m pytest --tb=short -q` green.
2. `docker compose run --rm react npx vitest run --reporter=verbose` green.
3. Claude Code Preview tab sweep (`mcp__Claude_Preview__*`) — load each new page, screenshot, console-logs, network — zero errors.
4. Single atomic commit, author `Armando Gonzalez <armandogon94@gmail.com>`, **no Co-Authored-By**.
