# CLAUDE.md — ERP Platform (Project 14)

## Project Overview

Odoo-inspired multi-tenant ERP platform serving 10 distinct industries with 13 core modules, each adaptable to industry-specific workflows through configuration. Unified architecture: all industries run on the same Django/React codebase and PostgreSQL schema with no code duplication. The platform features Odoo-style UI (form/list/kanban/pivot/graph views), module app switcher, sequence system, and all modules visible but adapted per industry.

**Estimated effort:** ~180 hours | **Agent Architecture:** 1 core platform agent + 10 industry agents (11 total)

---

## Git Commit Rules

**CRITICAL:**
```
- Commit as: Armando Gonzalez (armandogon94@gmail.com)
- Do NOT add "Co-Authored-By: Claude" or any AI co-author credits
- Use conventional commits (feat:, fix:, refactor:, docs:, test:, chore:)
- Keep commits atomic (one logical change per commit)
```

---

## Required Reading (in order)

Read ALL documents before writing code. They contain implementation-ready specs, SQL schemas, API examples, and component patterns.

| # | Document | Key Contents |
|---|----------|--------------|
| 1 | **ERP-MASTER-PLAN.md** | System architecture, 13 modules, 10 industries, port allocation, agent architecture, views, sequence system |
| 2 | **INDUSTRY-BRANDING-CONTEXT.md** | Company profiles, brand colors, user accounts, terminology per industry, CRM/ERP integration points |
| 3 | **RALPH-LOOP-CONFIG.md** | 5-pass QA framework (functional, security, performance, reference, code review), auto-fix, reporting |
| 4 | **CALENDAR-SYNC-API-SPEC.md** | Bidirectional calendar sync between CRM (Project 13) and ERP, optional webhooks/polling, iCalendar-compatible |
| 5 | **CLAUDE-CODE-INSTANCE-PROMPTS-14.md** | 11 independent agent system prompts (1 core + 10 industry-specific) |

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Backend | Django 5.x + Django REST Framework 3.15+ |
| Database | PostgreSQL 15+ |
| Task Queue | Celery 5.x + Redis |
| Real-Time | Django Channels (WebSocket) |
| Deployment | Docker Compose (local dev) |
| Testing | pytest + factory_boy (Python), vitest (React) |

---

## The 13 ERP Modules

| # | Module | Focus | Key Entities |
|---|--------|-------|--------------|
| 1 | **Accounting** | General ledger, journal entries, chart of accounts | ChartOfAccounts, Journal, JournalEntry, Payment, BankStatement |
| 2 | **Invoicing** | Customer invoices, vendor bills, recurring invoices | Invoice, InvoiceLine, CreditNote, PaymentTerms |
| 3 | **Inventory** | Products, stock locations, reorder rules, lot tracking | Product, StockLocation, StockMove, StockLot, ReorderRule |
| 4 | **Fleet** | Vehicles, maintenance, fuel, driver management | Vehicle, MaintenanceLog, FuelLog, Driver, VehicleService |
| 5 | **Calendar** | Appointments, resource booking, shift planning | Event, EventAttendee, Resource, Recurrence |
| 6 | **HR** | Payroll, leave, attendance, timesheets | Employee, Payroll, LeaveRequest, AttendanceLog, Timesheet |
| 7 | **Projects** | Tasks, milestones, timesheets, Gantt charts | Project, Task, Milestone, ProjectTimesheet |
| 8 | **Purchasing** | POs, RFQs, vendor management, receiving | PurchaseOrder, RequestForQuote, Vendor, ReceiptLine |
| 9 | **Sales** | Quotations, sales orders, pipeline, pricelists | SalesQuotation, SalesOrder, Pricelist, OpportunityStageLine |
| 10 | **Manufacturing** | Bills of materials, work orders, production costs | BillOfMaterials, WorkOrder, ProductionCost |
| 11 | **Point of Sale** | Touch-screen terminals, cash management | POSSession, POSOrder, CashMovement |
| 12 | **Helpdesk** | Support tickets, SLA tracking, knowledge base | Ticket, TicketCategory, SLAConfig, KnowledgeArticle |
| 13 | **Reports/BI** | Pivot tables, custom reports, scheduled exports | ReportTemplate, PivotDefinition, ScheduledExport |

---

## The 10 Industries

| # | Company | Industry | Brand Color | Frontend Port | API Port |
|---|---------|----------|-------------|---------------|----------|
| 1 | **NovaPay** | FinTech | #2563EB (Blue) | 14001 | 14101 |
| 2 | **MedVista** | Healthcare | #059669 (Green) | 14002 | 14102 |
| 3 | **TrustGuard** | Insurance | #1E3A5F (Navy) | 14003 | 14103 |
| 4 | **UrbanNest** | Real Estate | #D97706 (Amber) | 14004 | 14104 |
| 5 | **SwiftRoute** | Logistics | #7C3AED (Purple) | 14005 | 14105 |
| 6 | **DentaFlow** | Dental Clinic | #06B6D4 (Cyan) | 14006 | 14106 |
| 7 | **JurisPath** | Legal Firm | #166534 (Forest Green) | 14007 | 14107 |
| 8 | **TableSync** | Hospitality/Restaurant | #9F1239 (Burgundy) | 14008 | 14108 |
| 9 | **CraneStack** | Construction | #EA580C (Safety Orange) | 14009 | 14109 |
| 10 | **EduPulse** | Education | #6D28D9 (Indigo) | 14010 | 14110 |

---

## Agent Architecture

**11 total agents:**
- **1 Core Platform Agent** → Owns Django backend, React frontend, module system, views, API framework, auth, Docker infrastructure
- **10 Industry Agents** → Each owns domain expertise for one industry, implements industry-specific seed data, terminology config, workflows, demo scenarios

Communication: Core agent provides foundation APIs and module interface; industry agents build atop it without modifying core code.

---

## Key Features

- **Module System:** 13 industry-agnostic modules with extensible configuration
- **Odoo-Style Views:** Form, List, Kanban, Pivot, Graph views for all entities
- **App Switcher:** Quick navigation between modules with visual module grid
- **Sequence System:** Auto-generated sequential IDs per entity (INV-2026-001, PO-2026-005)
- **All Modules Visible:** Every industry instance has all 13 modules available, with adaptations per industry
- **Industry Configuration Loader:** Overrides terminology, fields, workflows, colors per company without code changes
- **Multi-Company Model:** company_id on all models; single DB, single app, multiple companies
- **Real-Time Notifications:** Django Channels for live updates and user notifications

---

## Port Allocation (14xxx Range)

```
Core Platform:
  Django API:              14000
  React Dev Proxy:         14500

Industry Frontends:        14001–14010 (NovaPay–EduPulse)
Industry APIs (optional):  14101–14110 (high-scale deployments)

Supporting Services:
  PostgreSQL:              5432
  Redis:                   6379
  Calendar Sync Service:   13500 (Project 13 → 14 integration)
```

---

## Calendar Sync (Optional)

Bidirectional REST API syncs calendar events between CRM (Project 13) and ERP (Project 14). Both systems work independently; sync is opt-in.

- **Design:** Minimal coupling, CalDAV-inspired, iCalendar-compatible JSON
- **Conflict Resolution:** Last-write-wins using `updated_at` ISO8601 timestamps
- **Real-Time:** Webhooks (5-sec latency) with polling fallback (5-min cycle)
- **Service:** Standalone or embedded; sync runs on port 13500

---

## Quality Standards

**Ralph Loop (5-Pass QA):**
1. **Functional** — Feature works as designed, accepts valid inputs
2. **Security** — Auth/RBAC, SQL injection, XSS, CSRF, sensitive data handling
3. **Performance** — Query optimization, N+1, caching, load testing
4. **Reference Comparison** — Odoo parity where applicable
5. **Code Review** — Style, readability, test coverage, documentation

**Python:** Black (code format), isort (import ordering), flake8 (linting), mypy (type checking)
**React:** ESLint + Prettier, vitest for unit tests, @testing-library for integration tests
**Database:** pytest + factory_boy for fixtures, Django test runner

---

## Project Structure

`backend/erp/` → Django project with `core/` (Company, User, Roles, ModuleRegistry), `modules/` (13 Django apps: accounting through reports), `api/v1/` (DRF views, serializers, filters), `tasks/` (Celery). `frontend/src/` → React with components (Form, List, Kanban, Pivot, Graph, AppSwitcher), pages, hooks, services. `plans/` → Architecture docs. Docker Compose for local dev.

---

## Important Conventions

- **Django Models:** PascalCase (e.g., `ChartOfAccounts`), DB tables: snake_case (e.g., `accounting_chartofaccounts`)
- **API Routes:** `/api/v1/{module}/{model}/` using DRF ViewSets (list, create, retrieve, update, destroy)
- **Industry Config:** YAML/JSON loaded at startup; overrides terminology, field visibility, workflows per company
- **Multi-Company:** All models include `company_id` FK to Company; queries filtered by active company
- **Authentication:** Django session + JWT for API; role-based permissions (RolePermission model)
- **Default Admin Credentials:** `admin / admin` for local development

---

## Key Commands

```bash
make dev        # Start all services (Django, PostgreSQL, Redis, Celery, React)
make migrate    # Run Django migrations
make seed       # Load demo data for all 10 industries
make test       # Run pytest + vitest + Ralph Loop
make build      # Build Docker images
make clean      # Stop and reset all services
```

---

**Status:** Master plan finalized, Phase 1 (Core Platform) starting | **Last Updated:** 2026-04-02
