# DECISION.md — ERP Platform Design Decisions

Autonomous design decisions made during the specification phase (2026-04-11).
Each decision includes the choice, alternatives considered, and rationale.

---

## D1: Project Structure

**Decision:** `backend/` (Django) + `frontend/` (React) at project root.

**Alternatives:**
- (a) Monorepo with shared root (chosen)
- (b) Separate repositories for backend and frontend
- (c) Django serving React via templates

**Rationale:** Standard separation that Docker builds independently. Single repo simplifies CI, version coordination, and developer onboarding. Django template approach would couple the frontend to Django's template engine, limiting React capabilities.

---

## D2: Multi-Tenancy Model

**Decision:** Shared schema with `company_id` FK on all models.

**Alternatives:**
- (a) Shared schema with row-level isolation via `company_id` (chosen)
- (b) Schema-per-tenant (PostgreSQL schemas)
- (c) Database-per-tenant

**Rationale:** 10 companies is a small tenant count. Shared schema avoids migration complexity, keeps queries simple, and allows cross-company reporting for super-admins. Schema-per-tenant adds migration overhead per company. Database-per-tenant is overkill for this scale.

---

## D3: Role System Architecture

**Decision:** Industry-specific role templates (`IndustryRoleTemplate` model) copied to per-company `Role` records on company provisioning.

**Alternatives:**
- (a) Industry-specific templates copied on provisioning (chosen)
- (b) Generic roles shared across all companies (Admin, Manager, User, Viewer)
- (c) Fully custom roles per company with no templates

**Rationale:** User explicitly requested roles based on actual job responsibilities per industry. A NovaPay CFO needs different permissions than a DentaFlow Practice Manager. Templates provide sensible defaults while allowing per-company customization after provisioning. Generic roles (b) would force all industries into the same permission structure.

---

## D4: Permission Granularity

**Decision:** 3-level permission system: module → action → entity-scope.

**Alternatives:**
- (a) 3-level (module + action + entity-scope) (chosen)
- (b) Module-level only (too coarse)
- (c) Field-level permissions in a separate table (too fine-grained)

**Rationale:**
- **Module-level:** Does the role have `access: true` for accounting? Checked by middleware.
- **Action-level:** Within accounting, can this role `create`, `update`, `approve`? Checked by DRF permission classes.
- **Entity-scope:** Which records — `company` (all), `department` (own dept), `own_record`, `assigned`? Checked by QuerySet filtering.

This provides meaningful access control without the N² complexity of field-level permission tables.

---

## D5: Field-Level Permissions

**Decision:** Handled via View config JSON (`readonly_fields`, `hidden_fields` per role level), not a separate permission table.

**Alternatives:**
- (a) View config JSON (chosen)
- (b) Separate FieldPermission model
- (c) Serializer-level field exclusion based on role

**Rationale:** The View system already defines which fields appear in forms and lists via JSON config. Adding `readonly_fields` and `hidden_fields` arrays per role level reuses existing infrastructure. A FieldPermission table would create O(fields × roles × modules) rows — explosion for 13 modules × 80 roles.

---

## D6: Dashboard Architecture

**Decision:** JSONB `dashboard_config` on the Role model with widget definitions pointing to PostgreSQL materialized views.

**Alternatives:**
- (a) JSONB config on Role model (chosen)
- (b) Hardcoded dashboard components per role
- (c) Separate Dashboard model with widget tables

**Rationale:** DB-driven dashboards allow per-role customization without code changes. The JSONB schema defines widget type, position, data source (materialized view), and display options. Each role's dashboard config is copied from the IndustryRoleTemplate on provisioning and can be customized afterward. Hardcoded components (b) would require code changes for every new role or KPI.

---

## D7: Analytics / Data Marts

**Decision:** PostgreSQL materialized views refreshed by Celery Beat. No external ETL pipeline.

**Alternatives:**
- (a) PostgreSQL materialized views (chosen)
- (b) Apache Airflow + dbt for ETL pipeline
- (c) Real-time aggregation queries (no caching)
- (d) Redis-cached aggregate queries

**Rationale:** `REFRESH MATERIALIZED VIEW CONCURRENTLY` handles the analytics needs without adding Airflow/dbt to the stack. Materialized views are refreshed hourly by Celery Beat, providing near-real-time dashboard data with zero additional infrastructure. Real-time queries (c) would be too slow for large datasets. Redis caching (d) adds key management complexity without the SQL query simplicity of materialized views.

---

## D8: Anomaly Detection

**Decision:** Celery task running every 15 minutes, evaluating JSONB alert rules defined per role.

**Alternatives:**
- (a) Periodic Celery task with JSONB rules (chosen)
- (b) Database triggers
- (c) Real-time stream processing (Kafka/Flink)
- (d) Django signals on every model save

**Rationale:** Anomaly detection doesn't need sub-second latency — 15-minute checks are sufficient for business anomalies (chargeback spikes, SLA breaches, stockouts). JSONB rules on the role template make anomalies configurable per industry and role. Database triggers (b) are hard to maintain. Stream processing (c) is overkill. Django signals (d) would fire on every save, creating performance overhead.

---

## D9: Frontend State Management

**Decision:** Zustand (not Redux).

**Alternatives:**
- (a) Zustand (chosen)
- (b) Redux Toolkit
- (c) React Context + useReducer
- (d) Jotai or Recoil (atomic state)

**Rationale:** Zustand provides a minimal API with excellent TypeScript support. The ERP frontend needs global state for auth (JWT tokens, user profile), company context (active company, brand color), and module config. Redux Toolkit would work but adds boilerplate (slices, actions, reducers) without proportional benefit. React Context (c) causes unnecessary re-renders with deeply nested state.

---

## D10: View System Architecture

**Decision:** JSON-driven view configs stored in the database; React renderers consume config to render Form/List/Kanban/Pivot/Graph views.

**Alternatives:**
- (a) JSON config → React renderer (chosen, Odoo pattern)
- (b) Hard-coded React components per model
- (c) Low-code page builder

**Rationale:** This is the core Odoo pattern. View configs define which fields appear, in what order, with what labels. The same React `FormView` component renders any model's form by reading the config. This enables per-company view customization without code changes and keeps the frontend thin. Hard-coded components (b) would require a new component for every model across 13 modules.

---

## D11: Vertical Slice Ordering

**Decision:** Core → View System → Config → HR/Calendar/Inventory (parallel) → Purchasing/Sales → Accounting → Invoicing → Fleet/Projects → Manufacturing/Helpdesk → POS → Reports → Seed Data → WebSocket.

**Alternatives:**
- (a) Dependency-graph order (chosen)
- (b) Alphabetical module order
- (c) Most-used modules first

**Rationale:** The dependency graph dictates order. Accounting depends on Sales and Purchasing; Invoicing depends on Accounting; POS depends on Inventory, Sales, and Accounting. Building in dependency order means each slice can fully integrate with its dependencies immediately. Tier 1 modules (HR, Calendar, Inventory) have no inter-module dependencies and can be built in parallel.

---

## D12: Reference Industry Per Slice

**Decision:** Each slice uses the industry that exercises its most complex variant as the reference implementation.

| Slice | Reference | Why |
|-------|-----------|-----|
| Core, Accounting, Reports | NovaPay | Multi-currency, complex fee accounting |
| Views, HR, Projects | CraneStack | Rich kanban (construction phases), 200+ employees |
| Config, Calendar | DentaFlow | Most terminology overrides, chair scheduling |
| Inventory, Manufacturing, POS | TableSync | Perishable tracking, recipes as BoM, restaurant POS |
| Sales | TrustGuard | Policy lifecycle (quote → underwrite → issue) |
| Invoicing | JurisPath | Hourly billing from timesheets |
| Fleet, WebSocket | SwiftRoute | 120-driver fleet, real-time delivery updates |

**Rationale:** Testing against the most complex variant ensures the module handles simpler variants by default. If accounting works for NovaPay's multi-currency merchant fees, it handles EduPulse's simple tuition accounting.

---

## D13: Testing Approach

**Decision:** TDD mandatory. RED → GREEN → REFACTOR per slice. pytest + factory_boy (backend), vitest + @testing-library/react (frontend). 80%+ coverage target.

**Alternatives:**
- (a) TDD with factory_boy (chosen)
- (b) Test-after development
- (c) TDD with Django fixtures (JSON)

**Rationale:** User explicitly required TDD. factory_boy creates test data programmatically with relationships and overrides, far more flexible than static JSON fixtures. Coverage target of 80% ensures meaningful testing without diminishing returns on trivial code.

---

## D14: Docker Architecture

**Decision:** 6 services in docker-compose.yml: django, postgres:15-alpine, redis:7-alpine, celery-worker, celery-beat, react.

**Alternatives:**
- (a) 6 services in single compose file (chosen)
- (b) 3 services (combine celery into django)
- (c) Kubernetes-ready with Helm charts

**Rationale:** Separate celery-worker and celery-beat services mirror production architecture and allow independent scaling. Alpine images keep containers small. Apple Silicon (arm64) images are available for all chosen base images. Kubernetes (c) is premature — Docker Compose is sufficient for local development and the user specifically requested Docker-first development.

---

## D15: API Versioning

**Decision:** URL-based `/api/v1/` prefix.

**Alternatives:**
- (a) URL-based versioning (chosen)
- (b) Header-based versioning (Accept header)
- (c) Query parameter versioning

**Rationale:** URL-based is the simplest, most visible, and what the planning docs specify. v2 can coexist at `/api/v2/` when needed. Header-based (b) is invisible in browser URL bars and harder to debug.

---

## D16: Authentication

**Decision:** JWT via djangorestframework-simplejwt. 15-minute access tokens, 7-day refresh tokens.

**Alternatives:**
- (a) JWT (simplejwt) (chosen)
- (b) Django session authentication
- (c) OAuth2 / OIDC
- (d) Token authentication (DRF TokenAuth)

**Rationale:** JWT enables stateless API authentication without server-side session storage. 15-minute access tokens limit exposure window. 7-day refresh tokens balance security with UX (no constant re-login). Session auth (b) requires sticky sessions in multi-instance deployments. OAuth2 (c) is overkill when all users are internal. DRF TokenAuth (d) requires database lookup per request.

---

## D17: Partner Model

**Decision:** Unified `Partner` model instead of separate `Customer` and `Vendor` models.

**Alternatives:**
- (a) Unified Partner model with `is_customer`/`is_supplier` flags (chosen, Odoo pattern)
- (b) Separate Customer and Vendor models
- (c) Generic ContactInfo model with polymorphic typing

**Rationale:** In real business, the same entity is often both customer and vendor (e.g., a subcontractor in CraneStack who both supplies materials and receives project payments). A unified model with `is_customer`/`is_supplier` boolean flags avoids duplicate records. This is Odoo's proven pattern. Separate models (b) would require cross-referencing to detect the same entity.

---

## D18: Soft Deletes

**Decision:** `deleted_at` timestamp on all models. Custom QueryManager filters active records by default.

**Alternatives:**
- (a) Soft delete with `deleted_at` + custom manager (chosen)
- (b) Hard deletes with audit log
- (c) Archive flag (`is_archived`)

**Rationale:** ERP data must never be permanently deleted — financial records, audit trails, and regulatory compliance require data retention. `deleted_at` timestamp enables point-in-time queries ("show me the state as of date X"). Custom QueryManager (`.objects` returns non-deleted, `.all_objects` includes deleted) keeps default queries clean. Archive flag (c) loses deletion timestamp.

---

## D19: Calendar Sync

**Decision:** Deferred to after core platform is stable. Stub endpoints only in initial implementation.

**Alternatives:**
- (a) Defer with stub endpoints (chosen)
- (b) Build full sync service from day one
- (c) Skip entirely

**Rationale:** The CALENDAR-SYNC-API-SPEC.md defines a standalone sync service between CRM (Project 13) and ERP (Project 14). Building it requires both systems to be operational. The core ERP must be stable first. Stub endpoints preserve the API contract so integration can proceed later without breaking changes.

---

## D20: Industry Frontend Routing

**Decision:** Single React app. Company selected at login. Theme and config loaded dynamically based on active company.

**Alternatives:**
- (a) Single app with dynamic theming (chosen)
- (b) 10 separate React builds (one per industry)
- (c) Micro-frontends per industry

**Rationale:** All 10 industries use the same 13 modules with the same view system. The only differences are brand color, terminology, field visibility, and workflow labels — all driven by configuration, not code. Separate builds (b) would duplicate 95% of the codebase. Micro-frontends (c) add routing and build complexity without benefit when modules are identical across industries.

---

## Decision Log

| Date | Decision | Status |
|------|----------|--------|
| 2026-04-11 | D1–D20 | Active |

All decisions are subject to revision as implementation reveals new constraints. Updates will be appended with rationale for the change.
