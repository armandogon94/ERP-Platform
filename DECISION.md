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

## D21: Partner Model (Unified Customer + Vendor)

**Decision:** Introduce a unified `Partner` model in `backend/core/` (Odoo-style: one entity with `is_customer` / `is_vendor` flags). Add FK from `SalesQuotation.customer`, `SalesOrder.customer`, `Invoice.customer`, `PurchaseOrder.vendor`. Keep existing `customer_name` CharField as a denormalized display fallback during the data migration; populate from Partner name going forward.

**Alternatives:**
- (a) Unified Partner model with `is_customer`/`is_vendor` flags (chosen, Odoo pattern)
- (b) Separate Customer and Vendor models
- (c) Keep `customer_name` CharField forever (no FK)

**Rationale:** Slices 7–10 shipped with `customer_name` as a CharField and a bare `Vendor` table inside the Purchasing module. Project 14's own kickoff decisions planned a unified Partner model (referenced in SPEC.md line 619 for Sales) but it was never built. Centralizing lets us track credit limits, contact history, payment terms, industry-specific segmentation, and duplicate detection in one place. Separate models (b) duplicate columns and require synchronization when a single entity (e.g., a construction sub-contractor who both buys and supplies) plays both roles. Staying with strings (c) blocks reporting, credit workflows, and Projects/POS/Helpdesk from referencing the same customer consistently.

---

## D22: Sequence Auto-Generation Trigger

**Decision:** Auto-generate sequence numbers (INV-2026-001, PO-2026-001, SO-2026-001, QUO-2026-001, JE-2026-001, CN-2026-001) via a **`save()` override** on each numbered model that calls the existing `core.sequence.get_next_sequence(company, prefix)` helper — but **only when the number field is blank**.

**Alternatives:**
- (a) `save()` override, only when blank (chosen)
- (b) Database trigger (PostgreSQL `BEFORE INSERT`)
- (c) Explicit call at serializer/viewset `perform_create` time
- (d) Require callers to always set the number (status quo)
- (e) `pre_save` signal dispatcher in `core/signals.py`

**Rationale:** `save()` override is Python-level, visible in tests/tracebacks, and fires on every write path (API, admin, management commands, shell) — no coverage gaps. DB triggers (b) hide logic from Django and complicate migrations. Serializer-level (c) misses records created via admin/commands/shell. Status quo (d) leaves the field perpetually blank. A `pre_save` signal (e) is indistinguishable from `save()` behaviorally but adds a layer of indirection and duplicates the "if blank" guard in a distant file; keeping the logic on the model itself makes it locally reviewable.

**Implementation note (REVIEW I-14):** Earlier drafts referred to this as "signal auto-gen"; the ships implementation is pure `save()` override on each of Invoice, CreditNote, PurchaseOrder, RequestForQuote, SalesQuotation, SalesOrder, POSOrder, Ticket, JournalEntry. There is **no** `pre_save` signal wired for sequence generation. Future numbered entities should follow the same `save()` pattern — see `backend/modules/invoicing/models.py::Invoice.save` as the canonical template.

---

## D23: Pivot & Graph View Implementation

**Decision:** Build `PivotView.tsx` and `GraphView.tsx` as generic JSON-config components using the existing `ViewDefinition` model (extend `view_type` choices to include `pivot` and `graph`). Back them with a new DRF action on every module ViewSet: `GET /{model}/aggregate/?group_by=<field>&measure=<field>&op=<sum|count|avg>&filter=<...>`.

**Alternatives:**
- (a) JSON-config components + per-ViewSet `/aggregate/` action (chosen)
- (b) Separate reporting stack (Metabase / Superset embedded)
- (c) Hardcoded per-module pivot pages
- (d) Client-side aggregation over paginated list responses

**Rationale:** Reuses the Odoo-style JSON view infrastructure we already built in Slice 2 — PivotView and GraphView become two more `view_type` values, not a parallel system. A `/aggregate/` action per ViewSet inherits the existing `CompanyScopedFilterBackend` so multi-tenancy and RBAC work for free. Embedding Metabase (b) would need SSO bridging, its own auth, and would not respect our Role permissions. Hardcoded pages (c) violate the "configuration not code" principle. Client-side aggregation (d) breaks at scale and can't be filtered securely.

---

## D24: Chart Library — Recharts

**Decision:** Use **Recharts** for GraphView (bar, line, pie, area).

**Alternatives:**
- (a) Recharts (chosen)
- (b) Chart.js + react-chartjs-2
- (c) Apache ECharts
- (d) Visx / D3 from scratch

**Rationale:** Recharts is React-idiomatic (declarative JSX, no imperative refs), tree-shakable (we only bundle the chart types we use), and has sufficient coverage for our 4 chart types. Chart.js (b) uses an imperative canvas API that fights React's reconciliation. ECharts (c) is more powerful but ships ~900KB minified (our entire current frontend bundle is smaller). Visx (d) is a toolkit, not a library — too much custom code for bar/line/pie. SPEC.md line 42 already listed "Recharts or Chart.js" — this locks the choice.

---

## D25: Dashboards Scope for This Cycle

**Decision:** **Defer** the full materialized-view dashboard system (originally D6) past this cycle. Build a lightweight HomePage in Slice 19 that shows 4–6 per-company KPIs using plain Django ORM aggregates (`.aggregate(Sum(...))`, `.annotate()`), not materialized views.

**Alternatives:**
- (a) Defer MV dashboards; build ORM-aggregate HomePage in Slice 19 (chosen)
- (b) Build full materialized-view dashboards per D6 inside this cycle
- (c) Skip homepage entirely; default route goes to first module

**Rationale:** Materialized-view dashboards (D6) require: the MV SQL, Celery Beat refresh schedule per view, refresh-failure handling, and per-role dashboard_config JSON. That's ~1 full slice of infrastructure for KPIs most demos don't need. Plain ORM aggregates over the seeded data (Slice 17) are fast enough for 10 companies × demo-scale data, and the same HomePage component can later swap its data source to MVs without any UI change. This reverses D6's implementation depth but preserves its architecture — the JSONB dashboard config and materialized views remain on the roadmap, just post-cycle.

---

## D26: Industry Demo Seeding Structure

**Decision:** One idempotent `seed_<module>_demo` Django management command per module (`seed_hr_demo`, `seed_inventory_demo`, etc.), each accepting `--company <slug>` and `--reset`. A meta-command `seed_industry_demo --company <slug>` dispatches to the per-module commands that apply for that industry per `INDUSTRY-BRANDING-CONTEXT.md`.

**Alternatives:**
- (a) Per-module commands + meta-command dispatcher (chosen)
- (b) One monolithic `seed_all --company <slug>` command
- (c) YAML/JSON fixtures loaded via `loaddata`
- (d) pytest factories reused directly as a seeding entry point

**Rationale:** Per-module commands are testable in isolation (unit-test each seeder) and composable per industry subset — TableSync needs Inventory+Manufacturing+POS seeded but not Fleet. A monolithic command (b) either forces all industries into the same seed set or grows into a 1000-line switch statement. Fixtures (c) break when models evolve (common during this cycle). Using factories directly (d) couples test infrastructure to production data paths — bad. Idempotency (`--reset` flag + existence checks) makes re-running safe.

---

## D27: Calendar Sync Implementation Depth

**Decision:** Ship a **polling-only MVP** in Slice 18: `GET /api/v1/calendar/events/?updated_since=<iso8601>` and `POST /api/v1/calendar/events/` with conflict resolution by last-write-wins on `updated_at`. No webhooks. The Event model already has `external_uid` from Slice 5.

**Alternatives:**
- (a) Polling-only MVP (chosen)
- (b) Full webhook + polling fallback per CALENDAR-SYNC-API-SPEC.md
- (c) Continue deferring entirely

**Rationale:** Matches D19 (calendar sync deferred past core platform). Polling at the CRM's 5-minute cadence is enough to demonstrate bidirectional sync for 10 industry demos; the webhook path requires shared secrets, retry logic, and signing — disproportionate to the single demo use case. `external_uid` and `updated_since` are already in the Event model, so this slice is a thin API + a small polling client in CRM's direction. Fully deferring (c) leaves the sync story untold at the end of this cycle — we want at least a working polling demo.

---

## D28: Module Scaffolding Pattern — Reuse, Do Not Refactor

**Decision:** For Slices 11–15 (Fleet, Projects, Manufacturing, POS, Helpdesk) use the 9-step Module Scaffold Pattern verbatim (memory `feedback_module_scaffold`), which drove Slices 4–10 with zero regressions.

**Alternatives:**
- (a) Reuse the 9-step pattern verbatim (chosen)
- (b) Refactor to a cookiecutter-style generator
- (c) Write a `manage.py scaffold_module` command

**Rationale:** The pattern is load-bearing: backend RED → GREEN → API RED → GREEN → frontend RED → GREEN → routes → commit. It produced 7 consecutive modules and an average 45 tests each without regression. Introducing a generator (b) or management command (c) now adds a meta-layer we'd have to maintain and debug — risk without reward when the remaining module count is 5. Post-cycle, generators are fair game.

---

## D29: Test Strategy — Unit + Preview Tab, No Headless E2E

**Decision:** Backend: pytest + factory_boy for models and API. Frontend: vitest + RTL (`fireEvent`, not `userEvent`). **No headless Playwright/Cypress suite.** Instead, every slice runs a Claude Code Preview tab sweep (`mcp__Claude_Preview__*`) that (1) `preview_start`s `http://localhost:14500`, (2) logs in as the industry admin most relevant to the slice, (3) navigates each new page, (4) captures `preview_screenshot` + `preview_console_logs` + `preview_network`, (5) flags visual/data bugs before the slice commits.

**Alternatives:**
- (a) Preview tab sweep per slice + unit tests (chosen)
- (b) Full Playwright E2E suite
- (c) Unit tests only, no browser verification

**Rationale:** Headless E2E doubles maintenance cost (selectors, fixtures, CI orchestration) for a platform that isn't in CI yet. The Preview tab gives us what E2E tests are meant to prove — page actually loads, console clean, network clean, data renders right, terminology swapped — without the fixture tax. Unit tests alone (c) let bugs through that only manifest with real API data (Slice 10 would have caught the missing Quotation form earlier if we'd run a preview sweep). Post-cycle, a Playwright smoke test over the 13 module list pages is a reasonable follow-up.

---

## D30: `/ship` Opt-Out for This Cycle

**Decision:** **Skip `/ship`** (shipping-and-launch skill and any production-deployment steps) for this cycle. User runs everything locally on Mac via Docker Compose; there is no staging or production environment yet.

**Alternatives:**
- (a) Skip `/ship` (chosen — explicit user instruction)
- (b) Run `/ship` at the end of the cycle

**Rationale:** User stated "no need to execute the ship skill at the end of the workflow just yet." Going through `/ship` without an environment to ship to would generate CI/CD config, container-registry steps, and secrets hygiene checks that the user would then have to unwind. When user is ready to deploy, they can run `/ship` as a standalone pass.

---

## D31: Tech-Debt Slices Before New Modules

**Decision:** Execute three small tech-debt slices (**10.5, 10.6, 10.7**) before Slice 11 begins, in this order:
1. **10.5** — Commit pending `InvoiceFormPage.test.tsx`, add missing `QuotationFormPage` + `/sales/quotations/new` and `/:id/edit` routes, retrofit `useTerminology` across the 11 pages that lack it (sales/purchasing/accounting/invoicing list+form pages).
2. **10.6** — Introduce the Partner model (D21) and migrate Sales/Invoicing/Purchasing FKs.
3. **10.7** — Wire sequence auto-generation signals (D22) for all existing numbered entities.

**Alternatives:**
- (a) Three tech-debt slices first, then 11 (chosen)
- (b) Fold tech debt into Slice 19 (polish)
- (c) Fold tech debt into each future module as encountered
- (d) Skip tech debt — ship as-is

**Rationale:** Partner (D21) is used by Fleet (no — Fleet has Driver, not Customer), **but** used directly by Projects (12 → client FK), Manufacturing (13 → rarely), POS (14 → customer FK), Helpdesk (15 → reporter FK). If Partner lands after those modules ship, we do a breaking refactor across 4 modules instead of 1. Folding into Slice 19 (b) means every new module ships with known inconsistency. Per-module cleanup (c) multiplies the retrofit work. Skipping (d) bakes in inconsistency permanently. The three slices are tiny (~1–2 hours each), sequenced so dependencies flow: 10.5 first (pure FE cleanup, no DB changes), then 10.6 (new model + data migration), then 10.7 (signals, which may reference Partner-owned records).

---

## D32: Ordering of All Remaining Slices

**Decision:** Execute remaining slices in this order: **10.5 → 10.6 → 10.7 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19.**

**Alternatives:**
- (a) Tech debt → modules in CLAUDE.md table order (chosen)
- (b) Modules first, tech debt last (Slice 19)
- (c) Parallel module development

**Rationale:** Dependency chain: Partner (10.6) blocks consistent customer/client FKs in 12/14/15; sequence auto-gen (10.7) must precede 11 to avoid new modules being the 11th place to fix the same bug; Reports/BI (16) needs module data to aggregate so must come after 11–15; demo seeding (17) needs all modules to exist; calendar sync (18) needs seeded events to sync; polish (19) touches every shipped module. Reordering would break each of these preconditions. Parallel development (c) isn't viable — one developer (agent-assisted) working Docker-linearly.

---

## D33: CSS Approach — Plain CSS + CSS Variables

**Decision:** Add a `frontend/src/styles/` directory containing token and component CSS, imported once from `main.tsx`. Use **plain CSS with custom properties** (CSS variables), no Tailwind/CSS-in-JS/CSS Modules. Semantic tokens (`--color-bg`, `--space-4`, `--radius-md`, etc.) are declared on `:root` and overridden per company on `html[data-company=<slug>]` via an inline style set by AppLayout.

**Alternatives:**
- (a) Plain CSS + CSS variables (chosen)
- (b) Tailwind CSS (utility-first, new build config + PostCSS pipeline + 23 JSX files to retrofit with utilities)
- (c) CSS-in-JS (emotion / styled-components) — runtime cost, server-side-rendering complexity
- (d) CSS Modules — scoped but verbose import ceremony per component

**Rationale:** We ship 23 existing React pages and ~8 shared components that currently have **no CSS at all** — adding Tailwind would require touching every JSX file to add utility classes, doubling the diff. Plain CSS lets us style the 6 shared components (Button, Input, Select, Modal, Badge, table patterns) and the AppLayout shell once, then every page picks up the look automatically via native HTML semantics (`<table>`, `<button>`, `<form>`, `<h1>`). CSS variables give us per-company theming for free — `--accent: {brand_color}` on the html root overrides across every descendant. No new build-time dependency.

---

## D34: Visual Style — Odoo-inspired Professional Density

**Decision:** Adopt an **Odoo-inspired** visual language: dense information, purple primary accent (default `#714B67`, overridable per company), light neutral surfaces, subtle 1px borders, 2–4px shadows, system font stack headed by `-apple-system, "Segoe UI", Roboto` for cross-platform native feel. Design tokens live in `frontend/src/styles/tokens.css`.

**Alternatives:**
- (a) Odoo-inspired professional density (chosen)
- (b) iOS-style card-based with heavy shadows and large whitespace
- (c) Material Design 3 with elevation scale
- (d) Minimalist/brutalist

**Rationale:** SPEC.md §Objective opens with "Odoo-inspired multi-tenant ERP platform" — the user's reference frame is already Odoo. Dense tables and sidebar-driven navigation are load-bearing for ERP users who scan hundreds of rows. Card-heavy iOS style (b) wastes vertical space. Material Design (c) brings a Google aesthetic at odds with ERP expectations. Minimalist (d) sacrifices information density. The purple accent matches the existing `AppLayout.DEFAULT_MODULES` color `#714B67` (already Odoo brand) and pairs cleanly with per-company brand color overrides as the accent.

---

## D35: Icon Library — Lucide React

**Decision:** Replace emoji icons (currently used in `AppLayout.DEFAULT_SIDEBAR_ITEMS` for modules: 💰 📄 📦 etc.) with **Lucide React** (`lucide-react` npm package). Add a single mapping `{ moduleName → LucideIcon }`. Keep an emoji fallback for modules whose API-returned icon string is unrecognized.

**Alternatives:**
- (a) Lucide React (chosen)
- (b) Heroicons (Tailwind's default)
- (c) Material Icons / Material Symbols
- (d) Keep emoji

**Rationale:** Per ui-ux-pro-max "common rules for professional UI": emoji as structural icons is the #1 anti-pattern. They render inconsistently across OS versions, can't be color-themed via CSS, and can't be sized with design tokens. Lucide is tree-shakable (we bundle only the ~15 icons we use), has a consistent 1.5–2px stroke width, and is React-idiomatic (`<Warehouse />` not `<svg>...</svg>`). Heroicons is fine but its outlined/solid split means twice as many imports for the same coverage. Material Symbols requires loading a variable font (~200KB). Emoji (d) is the current state and looks unprofessional per user feedback 2026-04-16.

---

## D37: AuditLog Retention and Offload Strategy

**Decision:** Run `trim_audit_log --days 90` nightly to cap table growth.
Defer Celery-based async offload of audit writes until observable load
warrants it.

**Alternatives:**
- (a) Synchronous writes + nightly retention trim (chosen — MVP)
- (b) Async via Celery task queue + retention trim
- (c) Append-only table partitioned by month with drop-old-partition policy
- (d) No retention (status quo before this decision)

**Rationale:** Review C-6 flagged AuditLog as unbounded-growth risk.
(a) addresses the growth half with one management command (`python
manage.py trim_audit_log --days 90`); register in django-celery-beat's
`PeriodicTask` table or cron. (b) requires a broker-queued task per
TenantModel save which is ~2ms added to every write path — not worth it
until p50 write latency becomes a bottleneck. (c) is correct for truly
large deployments (>10M audit rows) but adds partition maintenance
complexity the current scale doesn't need. (d) is the pre-REVIEW state.

**Scale thresholds for upgrading:**
- Move to (b) when synchronous audit INSERTs add >5ms to p95 write latency.
- Move to (c) when the table exceeds 10M rows (post-trim).

---

## D36: Denormalized Customer Snapshot on Invoice/Sales

**Decision:** Keep `customer_name` and `customer_email` CharFields on
`Invoice`, `SalesQuotation`, and `SalesOrder` alongside the canonical
`customer` Partner FK. `save()` backfills the denormalized fields from
the FK when blank; explicit values are respected.

**Alternatives:**
- (a) Drop the CharFields, always JOIN via `customer.name` (strict normalization)
- (b) Keep CharFields as intentional denormalization with save() sync (chosen)
- (c) Eventual consistency — update CharFields on Partner.save via signal

**Rationale:** Three concrete reasons to keep the denormalization —
(1) **Performance:** list views render without a Partner JOIN, critical
at scale. (2) **Historical integrity:** the name-at-issue-time is
preserved even if the Partner is later renamed, matching Odoo's
`commercial_partner` snapshot pattern. (3) **One-off customers:**
invoices can be issued without creating a Partner record (cash sale,
walk-in, etc.).

Option (a) is textbook-correct but loses (2) and (3). Option (c) is
tempting but the sync direction is actually wrong — an invoice's
customer_name should NOT change when the Partner is renamed (think
audit trail). Closing REVIEW I-10 by affirming the intentional
denormalization.

---

## Decision Log

| Date | Decision | Status |
|------|----------|--------|
| 2026-04-11 | D1–D20 | Active |
| 2026-04-16 | D21–D32 | Active |
| 2026-04-16 | D33–D35 | Active |
| 2026-04-17 | D36 | Active |
| 2026-04-17 | D37 | Active |

All decisions are subject to revision as implementation reveals new constraints. Updates will be appended with rationale for the change.
