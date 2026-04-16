# Implementation Plan: ERP Platform — All Slices (0–19)

> **Navigation:** Slices 0–1 are detailed below as the original plan. Slices 2–10 shipped using the same TDD/vertical-slice pattern (see `tasks/todo.md` for their checkpoint status and git commits `3fe3cfc` through `e1b424d`). The remaining slices (**10.5–19**) are in **Part 2** at the bottom of this file.

---

## Part 1: Original Plan (Slices 0–1) — FROZEN REFERENCE

## Overview

Break down the first two vertical slices (Docker Scaffold + Core Multi-Tenancy) into S/M-sized tasks that can each be completed in a single session. Each task follows TDD (RED → GREEN → REFACTOR) and leaves the system in a working, testable state.

**Architecture decisions:** See DECISION.md (D1–D20)
**Full spec:** See SPEC.md

---

## Dependency Graph (Slices 0–1)

```
Slice 0: Infrastructure
  Task 0.1: Docker Compose + Makefile
      │
      ├── Task 0.2: Django Project Skeleton
      │       │
      │       └── Task 0.3: Backend Smoke Tests
      │
      └── Task 0.4: React Project Skeleton
              │
              └── Task 0.5: Frontend Smoke Tests

Slice 1: Core Multi-Tenancy
  Task 1.1: TenantModel + Company + UserProfile
      │
      ├── Task 1.2: JWT Auth (login/logout/refresh)
      │       │
      │       └── Task 1.3: RBAC Models (Role, Permission, IndustryRoleTemplate)
      │               │
      │               └── Task 1.4: Middleware + DRF Permissions
      │
      ├── Task 1.5: Module System (ModuleRegistry, ModuleConfig)
      │
      └── Task 1.6: Sequence System + AuditLog + Notification
              │
              └── Task 1.7: Seed Data (10 companies + users + role templates)

  Task 1.8: Frontend Auth (Zustand + LoginForm)
      │
      └── Task 1.9: Frontend Layout (AppLayout + Navbar + Sidebar + AppSwitcher)
```

---

## Phase 1: Foundation (Slice 0) — Docker + Project Scaffold

### Task 0.1: Docker Compose + Makefile

**Description:** Create the Docker Compose infrastructure with 6 services and a Makefile for dev workflow commands. This is the foundation everything else runs on.

**Acceptance criteria:**
- [ ] `docker-compose.yml` defines 6 services: django, postgres (15-alpine), redis (7-alpine), celery-worker, celery-beat, react
- [ ] All images support arm64 (Apple Silicon)
- [ ] PostgreSQL uses named volume for data persistence
- [ ] Redis used as both cache and Celery broker
- [ ] `.env.example` contains all required environment variables
- [ ] `Makefile` has targets: dev, migrate, seed, test, test-backend, test-frontend, lint, format, typecheck, build, clean, logs, shell, createsuperuser

**Verification:**
- [ ] `docker-compose config` validates without errors
- [ ] `make dev` starts all 6 services (may fail on Django/React not existing yet — that's OK)

**Dependencies:** None

**Files created:**
- `docker-compose.yml`
- `Makefile`
- `.env.example`

**Scope:** Small (3 files)

---

### Task 0.2: Django Project Skeleton

**Description:** Create the Django project structure with split settings, URL routing, Celery configuration, and all dependencies. The Django app should start and respond to requests inside Docker.

**Acceptance criteria:**
- [ ] `backend/Dockerfile` builds successfully (Python 3.12 slim, multi-stage)
- [ ] `backend/requirements.txt` includes: Django 5.x, djangorestframework, djangorestframework-simplejwt, django-filter, django-cors-headers, django-environ, celery, redis, channels, drf-spectacular, psycopg2-binary, factory-boy, pytest-django, pytest-cov, black, isort, flake8
- [ ] `backend/pyproject.toml` configures pytest, black, isort, flake8
- [ ] `backend/config/settings/base.py` loads env vars via django-environ, configures DRF defaults (pagination, auth, renderers), Celery, Channels
- [ ] `backend/config/settings/dev.py` extends base with DEBUG=True, CORS_ALLOW_ALL
- [ ] `backend/config/settings/test.py` extends base with test-specific overrides (in-memory channels, faster password hasher)
- [ ] `backend/config/urls.py` includes `/api/v1/` namespace and drf-spectacular schema/swagger URLs
- [ ] `backend/config/celery_config.py` creates Celery app with autodiscover
- [ ] `backend/manage.py` exists and works

**Verification:**
- [ ] `docker-compose up django` → Django starts without errors
- [ ] `curl http://localhost:14000/api/v1/` returns 200 (or DRF browsable API root)
- [ ] `docker-compose exec django python manage.py check` passes

**Dependencies:** Task 0.1

**Files created:**
- `backend/Dockerfile`
- `backend/requirements.txt`
- `backend/pyproject.toml`
- `backend/manage.py`
- `backend/config/__init__.py`
- `backend/config/settings/__init__.py`
- `backend/config/settings/base.py`
- `backend/config/settings/dev.py`
- `backend/config/settings/test.py`
- `backend/config/urls.py`
- `backend/config/wsgi.py`
- `backend/config/asgi.py`
- `backend/config/celery_config.py`

**Scope:** Medium (13 files)

---

### Task 0.3: Backend Smoke Tests

**Description:** Write the first backend test — a smoke test proving Django serves a 200 at the API root and pytest runs inside Docker.

**TDD approach:**
1. RED: Write `test_api_root_returns_200` — it should fail if no URL is mapped
2. GREEN: Ensure `/api/v1/` is routed (already done in 0.2, so test should pass)
3. REFACTOR: Clean up conftest.py fixtures

**Acceptance criteria:**
- [ ] `backend/conftest.py` provides `db`, `api_client` fixtures
- [ ] `backend/core/__init__.py` and `backend/core/apps.py` exist (Django app stub)
- [ ] Test `test_api_root_returns_200` passes
- [ ] `make test-backend` runs pytest inside Docker and reports results

**Verification:**
- [ ] `make test-backend` → all tests pass, coverage reported

**Dependencies:** Task 0.2

**Files created:**
- `backend/conftest.py`
- `backend/core/__init__.py`
- `backend/core/apps.py`
- `backend/core/tests/__init__.py`
- `backend/core/tests/test_smoke.py`

**Scope:** Small (5 files)

---

### Task 0.4: React Project Skeleton

**Description:** Create the React 18 + TypeScript + Vite project with initial dependencies, API client setup, and router shell.

**Acceptance criteria:**
- [ ] `frontend/Dockerfile` builds successfully (Node 20 alpine)
- [ ] `frontend/package.json` includes: react 18, react-dom, react-router-dom, typescript, vite, vitest, @testing-library/react, @testing-library/jest-dom, axios, zustand, eslint, prettier
- [ ] `frontend/vite.config.ts` proxies `/api` to Django at port 14000
- [ ] `frontend/tsconfig.json` with strict mode, path aliases (@/ → src/)
- [ ] `frontend/index.html` with root div
- [ ] `frontend/src/main.tsx` renders App
- [ ] `frontend/src/App.tsx` with React Router shell (placeholder routes)
- [ ] `frontend/src/api/client.ts` creates Axios instance with base URL and JWT interceptor stub

**Verification:**
- [ ] `docker-compose up react` → Vite dev server starts on port 14500
- [ ] Browser at `http://localhost:14500` shows React app
- [ ] `docker-compose exec react npx tsc --noEmit` passes

**Dependencies:** Task 0.1

**Files created:**
- `frontend/Dockerfile`
- `frontend/package.json`
- `frontend/vite.config.ts`
- `frontend/tsconfig.json`
- `frontend/index.html`
- `frontend/src/main.tsx`
- `frontend/src/App.tsx`
- `frontend/src/api/client.ts`
- `frontend/src/api/types.ts`
- `frontend/.eslintrc.cjs`
- `frontend/.prettierrc`

**Scope:** Medium (11 files)

---

### Task 0.5: Frontend Smoke Tests

**Description:** Write the first frontend test — a smoke test proving the App component renders without crashing.

**TDD approach:**
1. RED: Write `App.test.tsx` with `renders without crashing` test
2. GREEN: Ensure App renders (already done in 0.4)
3. REFACTOR: Set up vitest config properly

**Acceptance criteria:**
- [ ] `frontend/src/App.test.tsx` smoke test passes
- [ ] `frontend/vitest.config.ts` or inline vitest config in vite.config.ts
- [ ] `frontend/src/test-setup.ts` imports @testing-library/jest-dom
- [ ] `make test-frontend` runs vitest inside Docker and reports results

**Verification:**
- [ ] `make test-frontend` → all tests pass
- [ ] `make test` → runs both backend and frontend tests

**Dependencies:** Task 0.4

**Files created:**
- `frontend/src/App.test.tsx`
- `frontend/src/test-setup.ts`

**Scope:** Small (2 files)

---

### Checkpoint: Slice 0 Complete

- [ ] `make dev` starts all 6 Docker services on Apple Silicon
- [ ] Django serves 200 at `http://localhost:14000/api/v1/`
- [ ] React serves at `http://localhost:14500`
- [ ] `make test` runs both pytest and vitest, all pass
- [ ] `make lint` runs Black + isort + flake8 + ESLint + Prettier
- [ ] Celery worker connects to Redis and logs "ready"
- [ ] PostgreSQL accepts connections
- [ ] Commit: `feat: scaffold Docker infrastructure with Django + React + Celery`

---

## Phase 2: Core Backend (Slice 1, Backend) — Models + Auth + RBAC

### Task 1.1: TenantModel + Company + UserProfile Models

**Description:** Create the foundational models for multi-tenancy. TenantModel is the abstract base class that all module models will inherit from. Company is the tenant root. UserProfile extends Django's User.

**TDD approach:**
1. RED: Write tests for Company creation, UserProfile linking, TenantModel company_id filtering, soft delete
2. GREEN: Implement models
3. REFACTOR: Extract common patterns

**Acceptance criteria:**
- [ ] `TenantModel` abstract base class with: `company` FK, `created_at`, `updated_at`, `deleted_at` (soft delete), `created_by`, `updated_by`
- [ ] `SoftDeleteManager` that filters `deleted_at__isnull=True` by default
- [ ] `Company` model with: `name`, `slug`, `brand_color`, `industry` (choice field for 10 industries), `is_active`, `config_json` (JSONB)
- [ ] `UserProfile` model with: `user` (OneToOne to Django User), `company` FK, `phone`, `department`, `job_title`, `timezone`, `language`, `is_company_admin`
- [ ] Factory classes: `CompanyFactory`, `UserFactory` (creates User + UserProfile)
- [ ] Migration runs cleanly

**Verification:**
- [ ] `make test-backend` → 6+ tests pass (Company CRUD, UserProfile creation, soft delete, company isolation)
- [ ] `make migrate` → migration applies without errors

**Dependencies:** Task 0.3

**Files created/modified:**
- `backend/core/models.py` (new)
- `backend/core/managers.py` (new — SoftDeleteManager)
- `backend/core/factories.py` (new)
- `backend/core/tests/test_models.py` (new)
- `backend/core/migrations/0001_initial.py` (auto-generated)

**Scope:** Medium (5 files)

---

### Task 1.2: JWT Authentication Endpoints

**Description:** Implement login, logout, and token refresh using djangorestframework-simplejwt. Users authenticate with email + password and receive JWT access/refresh tokens.

**TDD approach:**
1. RED: Write tests — login returns tokens, invalid creds return 401, refresh returns new access token, expired token returns 401
2. GREEN: Configure simplejwt, create auth views and serializers
3. REFACTOR: Clean up URL routing

**Acceptance criteria:**
- [ ] `POST /api/v1/auth/login/` accepts `{email, password}`, returns `{access, refresh, user: {id, email, first_name, last_name}, company: {id, name, brand_color, industry}}`
- [ ] `POST /api/v1/auth/refresh/` accepts `{refresh}`, returns `{access}`
- [ ] `POST /api/v1/auth/logout/` blacklists the refresh token
- [ ] Access token lifetime: 15 minutes; Refresh token: 7 days
- [ ] Invalid credentials return 401 with clear error message
- [ ] User serializer includes company info from UserProfile

**Verification:**
- [ ] `make test-backend` → 6+ new tests pass
- [ ] Manual test: `curl -X POST http://localhost:14000/api/v1/auth/login/ -d '{"email":"...","password":"..."}'` returns tokens

**Dependencies:** Task 1.1

**Files created/modified:**
- `backend/api/__init__.py` (new)
- `backend/api/v1/__init__.py` (new)
- `backend/api/v1/auth.py` (new)
- `backend/api/v1/urls.py` (new)
- `backend/core/serializers.py` (new)
- `backend/core/tests/test_auth.py` (new)
- `backend/config/urls.py` (modified — add api.v1 include)

**Scope:** Medium (7 files)

---

### Task 1.3: RBAC Models — Role, Permission, IndustryRoleTemplate

**Description:** Create the role-based access control models. IndustryRoleTemplate stores pre-defined roles per industry (80 total). When a company is created, templates are copied into company-specific Role records.

**TDD approach:**
1. RED: Test role creation, permission assignment, template copying on company provisioning, JSONB permission schema validation
2. GREEN: Implement models and provisioning service
3. REFACTOR: Extract provisioning into service module

**Acceptance criteria:**
- [ ] `Role` model: `company` FK, `name`, `description`, `is_system`, `role_level` (operational/supervisor/manager/director/executive), `template` FK, `dashboard_config` JSONB, `anomaly_alerts` JSONB
- [ ] `Permission` model: `codename` (e.g., `accounting.read`), `name`, `module`, `action`
- [ ] `RolePermission` model: `role` FK, `permission` FK (unique together)
- [ ] `UserRole` model: `user` FK, `role` FK
- [ ] `IndustryRoleTemplate` model: `industry`, `role_slug`, `role_name`, `role_level`, `module_permissions` JSONB, `dashboard_config` JSONB, `anomaly_alerts` JSONB (unique together: industry, role_slug)
- [ ] `provision_company_roles(company)` function copies templates to company-specific roles
- [ ] Factories: `RoleFactory`, `PermissionFactory`, `IndustryRoleTemplateFactory`

**Verification:**
- [ ] `make test-backend` → 8+ new tests pass (model creation, provisioning copies templates, permissions expand correctly, JSONB schema works)

**Dependencies:** Task 1.1

**Files modified:**
- `backend/core/models.py` (add Role, Permission, RolePermission, UserRole, IndustryRoleTemplate)
- `backend/core/services/__init__.py` (new)
- `backend/core/services/company_provisioning.py` (new)
- `backend/core/factories.py` (add RoleFactory, etc.)
- `backend/core/tests/test_models.py` (add RBAC tests)
- `backend/core/tests/test_provisioning.py` (new)
- `backend/core/migrations/0002_rbac.py` (auto-generated)

**Scope:** Medium (7 files)

---

### Task 1.4: Middleware + DRF Permission Classes

**Description:** Create the CompanyRoleContextMiddleware that injects company and permission context into every request, and the DRF permission classes that enforce RBAC at the API level.

**TDD approach:**
1. RED: Test middleware injects company_id, test permission class returns 403 for unauthorized, test entity-scope filtering
2. GREEN: Implement middleware and permission classes
3. REFACTOR: Optimize permission lookups with prefetch

**Acceptance criteria:**
- [ ] `CompanyRoleContextMiddleware` extracts company from JWT-authenticated user's UserProfile, injects `request.company`, `request.company_id`, `request.roles`, `request.permissions` (set of codenames), `request.role_level`, `request.dashboard_config`
- [ ] `ModulePermission` DRF permission class checks `{module}.{action}` against `request.permissions`
- [ ] `IsCompanyMember` permission class verifies user belongs to the active company
- [ ] `IsCompanyAdmin` permission class checks `is_company_admin` on UserProfile
- [ ] `CompanyScopedFilterBackend` auto-filters querysets by `company_id`
- [ ] Unauthenticated requests bypass middleware (no crash)

**Verification:**
- [ ] `make test-backend` → 8+ new tests pass
- [ ] Test: authenticated user without `accounting.read` permission gets 403 on accounting endpoints
- [ ] Test: user from Company A cannot access Company B's data

**Dependencies:** Tasks 1.2, 1.3

**Files created/modified:**
- `backend/core/middleware.py` (new)
- `backend/api/v1/permissions.py` (new)
- `backend/api/v1/filters.py` (new)
- `backend/core/tests/test_middleware.py` (new)
- `backend/core/tests/test_permissions.py` (new)
- `backend/config/settings/base.py` (add middleware to MIDDLEWARE list)

**Scope:** Medium (6 files)

---

### Checkpoint: Core Auth + RBAC

- [ ] All backend tests pass (20+ tests)
- [ ] JWT auth works end-to-end (login → access → refresh)
- [ ] RBAC enforced (403 on unauthorized module access)
- [ ] Multi-tenancy enforced (Company A data invisible to Company B users)
- [ ] Commit: `feat: core multi-tenancy with JWT auth and RBAC`

---

### Task 1.5: Module System — ModuleRegistry + ModuleConfig

**Description:** Create the module registry that tracks which modules are installed per company, and the config system that stores per-company module settings.

**TDD approach:**
1. RED: Test module listing for a company, config retrieval with hierarchy, module visibility
2. GREEN: Implement models and ViewSet
3. REFACTOR: Add caching for config lookups

**Acceptance criteria:**
- [ ] `ModuleRegistry` model: `company` FK, `name`, `display_name`, `icon`, `is_installed`, `is_visible`, `sequence` (display order), `color`
- [ ] `ModuleConfig` model: `company` FK, `module` FK, `key`, `value` (TextField), `value_type` (string/int/bool/json)
- [ ] `Menu` model: `company` FK, `module` FK, `parent` (self-FK), `name`, `label`, `icon`, `sequence`, `url`
- [ ] `GET /api/v1/core/modules/` returns installed modules for authenticated user's company
- [ ] `GET /api/v1/core/modules/{id}/config/` returns merged config
- [ ] Module list respects permissions (modules the user can't access are marked but not hidden — Odoo pattern)

**Verification:**
- [ ] `make test-backend` → 5+ new tests pass
- [ ] API returns correct module list for NovaPay vs DentaFlow

**Dependencies:** Task 1.4

**Files modified:**
- `backend/core/models.py` (add ModuleRegistry, ModuleConfig, Menu)
- `backend/core/serializers.py` (add ModuleSerializer, ConfigSerializer)
- `backend/core/views.py` (new — ModuleViewSet)
- `backend/core/urls.py` (new — core URL routing)
- `backend/core/factories.py` (add ModuleFactory)
- `backend/core/tests/test_modules.py` (new)
- `backend/core/migrations/0003_modules.py` (auto-generated)

**Scope:** Medium (7 files)

---

### Task 1.6: Sequence System + AuditLog + Notification

**Description:** Create the sequence number generator (INV/2026/00001), audit logging via Django signals, and the notification model.

**TDD approach:**
1. RED: Test sequence generation (format, thread-safety), audit log creation on model save, notification creation
2. GREEN: Implement Sequence model with select_for_update, signals, Notification model
3. REFACTOR: Ensure thread-safety test is robust

**Acceptance criteria:**
- [ ] `Sequence` model: `company` FK, `prefix`, `suffix`, `next_number`, `step`, `padding`, `use_date_range`, `reset_period`
- [ ] `get_next_sequence(company, prefix)` returns formatted string (e.g., `PO/2026/00001`), uses `select_for_update()` for thread safety
- [ ] `AuditLog` model: `company` FK, `user` FK, `model_name`, `model_id`, `action` (create/update/delete), `old_values` JSONB, `new_values` JSONB, `ip_address`, `timestamp`
- [ ] Django signals `post_save` and `post_delete` create AuditLog entries automatically for TenantModel subclasses
- [ ] `Notification` model: `recipient` FK, `title`, `message`, `notification_type`, `is_read`, `action_url`, `related_model`, `related_id`
- [ ] `Setting` model: `company` FK (nullable for global), `key`, `value`, `value_type`

**Verification:**
- [ ] `make test-backend` → 8+ new tests pass
- [ ] Sequence test: concurrent calls produce sequential numbers (no duplicates)
- [ ] Saving a Company creates an AuditLog entry

**Dependencies:** Task 1.1

**Files created/modified:**
- `backend/core/sequence.py` (new)
- `backend/core/signals.py` (new)
- `backend/core/models.py` (add Sequence, AuditLog, Notification, Setting)
- `backend/core/apps.py` (connect signals in ready())
- `backend/core/factories.py` (add SequenceFactory)
- `backend/core/tests/test_sequence.py` (new)
- `backend/core/tests/test_signals.py` (new)
- `backend/core/migrations/0004_sequence_audit.py` (auto-generated)

**Scope:** Medium (8 files)

---

### Task 1.7: Seed Data — Companies + Users + Role Templates

**Description:** Create seed data for all 10 companies with default users and the 80 industry-specific role templates. This makes the platform immediately usable for demo purposes.

**TDD approach:**
1. RED: Test seed command runs, correct company count, correct user count, correct role template count
2. GREEN: Implement management commands and fixture data
3. REFACTOR: Validate JSON fixture completeness

**Acceptance criteria:**
- [ ] `python manage.py seed_companies` creates 10 companies (NovaPay through EduPulse) with correct brand colors, industries, and slugs
- [ ] Each company gets 5 default users: admin, ceo, manager, user, viewer (all with password `demo123`)
- [ ] `fixtures/industry_role_templates.json` contains 80 role templates (8 per industry) with full `module_permissions`, `dashboard_config`, and `anomaly_alerts` JSONB
- [ ] `python manage.py seed_role_templates` loads fixtures and provisions roles for all companies
- [ ] 13 default Permission records created (one per module × CRUD actions = ~65 permissions)
- [ ] 13 default ModuleRegistry records per company

**Verification:**
- [ ] `make test-backend` → 4+ new tests pass (seed commands run, counts correct)
- [ ] `make seed` → runs both commands successfully
- [ ] `python manage.py shell -c "Company.objects.count()"` returns 10

**Dependencies:** Tasks 1.3, 1.5, 1.6

**Files created:**
- `backend/core/management/__init__.py`
- `backend/core/management/commands/__init__.py`
- `backend/core/management/commands/seed_companies.py`
- `backend/core/management/commands/seed_role_templates.py`
- `backend/core/management/commands/seed_all.py`
- `backend/fixtures/industry_role_templates.json`
- `backend/core/tests/test_seed.py`

**Scope:** Medium (7 files)

---

### Checkpoint: Core Backend Complete

- [ ] All backend tests pass (40+ tests)
- [ ] 10 companies seeded with brand colors and industries
- [ ] 50 users (5 per company) with role assignments
- [ ] 80 industry-specific role templates loaded
- [ ] JWT auth works
- [ ] RBAC enforced at API level
- [ ] Sequence generation works
- [ ] Audit logging active
- [ ] Commit: `feat: core backend with companies, auth, RBAC, sequences, and seed data`

---

## Phase 3: Core Frontend (Slice 1, Frontend)

### Task 1.8: Frontend Auth — Zustand Store + Login Flow

**Description:** Implement the authentication flow on the frontend: Zustand store for auth state, login API call, JWT token management, and the LoginPage component.

**TDD approach:**
1. RED: Test LoginForm renders email + password fields, submits calls API, stores tokens
2. GREEN: Implement store and component
3. REFACTOR: Extract API calls

**Acceptance criteria:**
- [ ] `authStore.ts` (Zustand): stores `user`, `accessToken`, `refreshToken`, `company`; actions: `login(email, password)`, `logout()`, `refreshToken()`
- [ ] `api/auth.ts`: `loginAPI(email, password)` calls `POST /api/v1/auth/login/`
- [ ] `api/client.ts`: Axios interceptor adds `Authorization: Bearer <token>` to all requests; on 401, attempts refresh
- [ ] `pages/LoginPage.tsx`: email + password form, submit button, error display, redirects to dashboard on success
- [ ] Login form validates: email required, password required
- [ ] On successful login, user and company data are stored

**Verification:**
- [ ] `make test-frontend` → 4+ tests pass
- [ ] Test: LoginForm renders, fills fields, submits, calls mock API
- [ ] Test: authStore.login() stores tokens and user data

**Dependencies:** Tasks 0.5, 1.2

**Files created:**
- `frontend/src/store/authStore.ts`
- `frontend/src/api/auth.ts`
- `frontend/src/pages/LoginPage.tsx`
- `frontend/src/pages/LoginPage.test.tsx`
- `frontend/src/store/authStore.test.ts`
- `frontend/src/api/client.ts` (modified — add JWT interceptor)

**Scope:** Medium (6 files)

---

### Task 1.9: Frontend Layout — AppLayout + Navbar + Sidebar + AppSwitcher

**Description:** Build the main application layout: Odoo-style top navbar with company branding, sidebar with module navigation, and the app switcher grid.

**TDD approach:**
1. RED: Test TopNavbar renders company name and brand color, AppSwitcher renders module grid, Sidebar renders module links
2. GREEN: Implement components
3. REFACTOR: Extract theme utilities

**Acceptance criteria:**
- [ ] `companyStore.ts` (Zustand): stores `activeCompany`, `modules`; actions: `fetchModules()`
- [ ] `AppLayout.tsx`: wraps pages with TopNavbar + Sidebar + content area
- [ ] `TopNavbar.tsx`: Odoo-style purple bar (#7C3AED) with company accent color, company name, user menu (profile, logout), notification bell placeholder
- [ ] `Sidebar.tsx`: module list from `companyStore.modules`, active module highlighted, collapse toggle
- [ ] `AppSwitcher.tsx`: grid of module icons (like Odoo's app drawer), opens as overlay, click navigates to module
- [ ] `DashboardPage.tsx`: placeholder landing page with company name and brand color
- [ ] `theme.ts`: Odoo purple base, dynamic brand color CSS variables
- [ ] `globals.css`: base styles, CSS variables for theming
- [ ] React Router routes: `/login` → LoginPage, `/` → DashboardPage (protected)
- [ ] Protected route redirects to `/login` if not authenticated

**Verification:**
- [ ] `make test-frontend` → 6+ tests pass
- [ ] Browser: login as admin@novapay.com → see blue-branded navbar with "NovaPay"
- [ ] Browser: click app switcher → see module grid
- [ ] Browser: sidebar shows module list
- [ ] Unauthenticated access to `/` redirects to `/login`

**Dependencies:** Task 1.8

**Files created:**
- `frontend/src/store/companyStore.ts`
- `frontend/src/components/layout/AppLayout.tsx`
- `frontend/src/components/layout/TopNavbar.tsx`
- `frontend/src/components/layout/Sidebar.tsx`
- `frontend/src/components/module-switcher/AppSwitcher.tsx`
- `frontend/src/pages/DashboardPage.tsx`
- `frontend/src/styles/theme.ts`
- `frontend/src/styles/globals.css`
- `frontend/src/App.tsx` (modified — add routes)
- `frontend/src/components/layout/TopNavbar.test.tsx`
- `frontend/src/components/module-switcher/AppSwitcher.test.tsx`

**Scope:** Medium-Large (11 files, but mostly small components)

---

### Checkpoint: Slice 1 Complete

- [ ] All tests pass (40+ backend, 10+ frontend)
- [ ] `make dev` → all services running
- [ ] Browser: navigate to `http://localhost:14500`
- [ ] Login as `admin@novapay.com` / `demo123` → see NovaPay-branded dashboard
- [ ] Login as `admin@dentaflow.com` / `demo123` → see DentaFlow-branded dashboard (different color)
- [ ] App Switcher shows 13 modules
- [ ] API endpoints reject unauthorized access (403)
- [ ] Company isolation verified (NovaPay admin can't see DentaFlow data)
- [ ] Commit: `feat: core frontend with login, layout, app switcher, and theming`

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Docker build slow on Apple Silicon | Medium | Use arm64-native images (alpine), multi-stage builds, .dockerignore |
| factory_boy + pytest overhead | Low | Use `--reuse-db` flag, transaction-per-test isolation |
| 80 role templates is a large JSON fixture | Medium | Generate programmatically with a script, validate with tests |
| JWT refresh interceptor complexity | Medium | Start with simple interceptor, add retry logic incrementally |
| Vite proxy to Django in Docker | Low | Use Docker network DNS (service name as host) |

---

## Skills Used Per Task

| Task | Primary Skill | Supporting Skills |
|------|---------------|-------------------|
| 0.1–0.5 | `incremental-implementation` | `source-driven-development` |
| 1.1 | `test-driven-development` | `incremental-implementation` |
| 1.2 | `test-driven-development` | `api-and-interface-design` |
| 1.3 | `test-driven-development` | `security-and-hardening` |
| 1.4 | `test-driven-development` | `security-and-hardening` |
| 1.5 | `test-driven-development` | `incremental-implementation` |
| 1.6 | `test-driven-development` | `incremental-implementation` |
| 1.7 | `incremental-implementation` | — |
| 1.8 | `test-driven-development` | `frontend-ui-engineering` |
| 1.9 | `test-driven-development` | `frontend-ui-engineering` |

---

# Part 2: Remaining Slices (10.5 → 19)

**Scope:** 12 slices. Every slice is a thin vertical slice (model → serializer → API → React → tests). Every slice commits atomically. Every slice passes the Verification Gate (`SPEC.md §Verification Gate`) before commit.

**Order is locked by DECISION.md D32:** 10.5 → 10.6 → 10.7 → 11 → 12 → 13 → 14 → 15 → 16 → 17 → 18 → 19.

**Module Scaffold Pattern (applies verbatim to Slices 11–15, D28):**

| Step | Phase | Description |
|------|-------|-------------|
| 1 | — | Backend directory scaffold (`backend/modules/<name>/` with `apps.py`, `models.py`, `migrations/`, `tests/`) |
| 2 | RED | Write failing model tests (`test_models.py`) — run via Docker pytest |
| 3 | GREEN | Implement models + factories + add to `INSTALLED_APPS` + `makemigrations` |
| 4 | RED | Write failing API tests (`test_api.py`) |
| 5 | GREEN | Implement serializers + viewsets + `urls.py` + include in `api/v1/urls.py` |
| 6 | RED | Write failing frontend tests (`{Entity}ListPage.test.tsx`, `{Entity}FormPage.test.tsx`) with `api/config` mock and `configStore.setState` boilerplate |
| 7 | GREEN | Implement `api/<name>.ts` client + `{Entity}ListPage.tsx` + `{Entity}FormPage.tsx` (with `useTerminology`) |
| 8 | — | Register routes in `frontend/src/App.tsx` |
| 9 | VERIFY | Full suite green + Preview-tab sweep + atomic commit |

**TDD ordering rule:** Every implementation task (`GREEN`) must be preceded by a failing-test task (`RED`) for the same unit. Never skip RED.

**Verification Gate per slice (non-negotiable):**
1. `docker compose run --rm django python -m pytest --tb=short -q` → green
2. `docker compose run --rm react npx vitest run --reporter=verbose` → green
3. Preview-tab sweep (`mcp__Claude_Preview__*`): login as reference-industry admin → navigate each new page → `preview_screenshot` + `preview_console_logs` + `preview_network` → zero console errors, zero 4xx/5xx, terminology override visible
4. Single atomic commit, author `Armando Gonzalez <armandogon94@gmail.com>`, **no Co-Authored-By**

---

## Slice 10.5 — Tech-debt cleanup (UI consistency)

**Description:** Clear accumulated frontend tech debt before starting new modules. Add the missing Quotation form page, commit the uncommitted InvoiceFormPage test, and retrofit `useTerminology()` across the 11 pages that still use hard-coded labels. Ref D31.

**Dependency:** None (must land first).

**Reference industry:** Any — TableSync is a good terminology smoke-test target.

**Scope:** M (~12 files)

### Task 10.5.1 — Commit pending InvoiceFormPage.test.tsx
**RED → GREEN:** No new tests. The file is modified in git status; inspect diff, ensure it passes locally, include in the slice's final commit.
- **Acceptance:** `git status` shows no modified tracked files after the slice's commit; `docker compose run --rm react npx vitest run src/pages/invoicing/` green.
- **Files:** `frontend/src/pages/invoicing/InvoiceFormPage.test.tsx`
- **Size:** XS

### Task 10.5.2 — QuotationFormPage tests (RED)
**RED:** Create `frontend/src/pages/sales/QuotationFormPage.test.tsx` following the memory-documented form-page test structure (mock `api/config`, `api/sales`, reset `configStore`, use `fireEvent`). Tests required:
- "New Quotation" heading renders on `/sales/quotations/new`
- "Edit Quotation" heading + pre-fill on `/sales/quotations/:id/edit`
- `createQuotationApi` called when submitting a new form
- `updateQuotationApi` called with `(id, payload)` when submitting edit
- **Acceptance:** Run `vitest` → all four tests FAIL (no component yet).
- **Files:** new `frontend/src/pages/sales/QuotationFormPage.test.tsx`
- **Size:** S

### Task 10.5.3 — QuotationFormPage component (GREEN)
**GREEN:** Implement `frontend/src/pages/sales/QuotationFormPage.tsx` mirroring `SalesOrderFormPage.tsx` pattern: `useParams().id` → isEdit, `EMPTY_FORM` state, `useEffect` pre-fill, `handleChange`/`handleSubmit` → create or update → navigate. Add `createQuotationApi`/`updateQuotationApi`/`fetchQuotationItemApi` to `frontend/src/api/sales.ts` if missing.
- **Acceptance:** Tests from 10.5.2 pass.
- **Files:** `frontend/src/pages/sales/QuotationFormPage.tsx`, `frontend/src/api/sales.ts`
- **Size:** S

### Task 10.5.4 — Register Quotation routes
- Add `<Route path="/sales/quotations/new" element={<QuotationFormPage />} />` and `.../:id/edit` in `App.tsx`. Update `QuotationListPage`'s "New" button + per-row edit link to these routes.
- **Acceptance:** Clicking "New Quotation" in the browser reaches the form; editing a row opens it pre-filled.
- **Files:** `frontend/src/App.tsx`, `frontend/src/pages/sales/QuotationListPage.tsx`
- **Size:** XS

### Task 10.5.5 — Terminology retrofit tests (RED)
**RED:** For each of the 11 pages listed below, add a test that mounts the page with a `configStore.setState({ terminology: {Invoice: "Merchant Bill"} })` and asserts the overridden label renders. (One test per page is enough; don't test all override permutations.)

Pages to retrofit: `sales/QuotationListPage`, `sales/SalesOrderListPage`, `sales/SalesOrderFormPage`, `purchasing/VendorListPage`, `purchasing/VendorFormPage`, `purchasing/PurchaseOrderListPage`, `purchasing/PurchaseOrderFormPage`, `accounting/AccountListPage`, `accounting/JournalEntryListPage`, `accounting/JournalEntryFormPage`, `invoicing/InvoiceListPage`, `invoicing/InvoiceFormPage`.

- **Acceptance:** 11 new tests, each FAILING (pages still hard-code labels).
- **Files:** 11 updated `.test.tsx` files (one per page).
- **Size:** M

### Task 10.5.6 — Apply `useTerminology` across 11 pages (GREEN)
**GREEN:** For each page, `import { useTerminology } from "@/hooks/useTerminology"`, destructure `const { t } = useTerminology()`, replace hard-coded strings like `"Invoice"` with `t("Invoice")`, `"Customer"` with `t("Customer")`, etc. Preserve non-label strings (placeholders, button copy) unless they map to a terminology key.
- **Acceptance:** All tests from 10.5.5 pass. No regressions in existing tests.
- **Files:** 11 updated `.tsx` files (one per page listed above).
- **Size:** M

### Task 10.5.7 — Verification Gate + commit
- Run full pytest + vitest suites.
- Preview-tab sweep: login as `admin@tablesync.com` → Sales/Purchasing/Accounting/Invoicing list pages → confirm TableSync terminology (e.g., "Guest" for customer, "Menu Item" for product) appears in column headers.
- Commit: `refactor: Slice 10.5 — Quotation form, terminology retrofit, commit pending test`

### Checkpoint: Slice 10.5
- [ ] `git status` clean after commit
- [ ] 11 pages call `useTerminology()`
- [ ] QuotationFormPage accessible at `/sales/quotations/new` and `:id/edit`
- [ ] Preview sweep green with TableSync overrides visible

---

## Slice 10.6 — Partner model (D21)

**Description:** Introduce unified `core.Partner` (Odoo pattern) with `is_customer`/`is_vendor` flags. Add nullable FKs from `sales.SalesQuotation`, `sales.SalesOrder`, `invoicing.Invoice`, `purchasing.PurchaseOrder`. Data-migrate existing rows' `customer_name` into Partner records. Keep `customer_name` populated as denormalized display fallback.

**Dependency:** Slice 10.5 merged.

**Reference industry:** NovaPay (has both customers and vendors in the same dataset).

**Scope:** L (~15 files)

### Task 10.6.1 — Partner model tests (RED)
- Test: create Partner, `__str__`, `is_customer`/`is_vendor` flags, unique-per-company name+tax_id constraint, company isolation.
- **Files:** new `backend/core/tests/test_partner_model.py`
- **Size:** S

### Task 10.6.2 — Partner model + factory + migration (GREEN)
- Add `Partner(TenantModel)` in `backend/core/models.py` with fields per SPEC.md §Slice 10.6.
- Add `PartnerFactory` in `backend/core/factories.py` with `skip_postgeneration_save = True`.
- `makemigrations core`.
- **Acceptance:** Tests from 10.6.1 pass.
- **Files:** `backend/core/models.py`, `backend/core/factories.py`, new migration
- **Size:** S

### Task 10.6.3 — Partner API tests (RED)
- Test: list (company-scoped), create, retrieve, update, delete; cross-company isolation returns 404.
- **Files:** new `backend/core/tests/test_partner_api.py`
- **Size:** S

### Task 10.6.4 — Partner ViewSet + serializer + URL (GREEN)
- Add `PartnerSerializer` to `backend/core/serializers.py`.
- Add `PartnerViewSet` (IsCompanyMember + CompanyScopedFilterBackend + `pagination_class = None`, `perform_create` sets company).
- Register at `/api/v1/core/partners/` in `backend/api/v1/urls.py` or `backend/core/urls.py`.
- **Acceptance:** Tests from 10.6.3 pass.
- **Files:** `backend/core/serializers.py`, `backend/core/views.py`, `backend/core/urls.py`
- **Size:** S

### Task 10.6.5 — Add nullable Partner FKs to existing models (RED → GREEN)
- **RED:** Tests in each of `sales/tests/`, `invoicing/tests/`, `purchasing/tests/` asserting that the new FK field exists, accepts a Partner from the same company, rejects a Partner from another company.
- **GREEN:** Add `customer = models.ForeignKey("core.Partner", null=True, blank=True, on_delete=models.PROTECT, related_name="+")` to `SalesQuotation`, `SalesOrder`, `Invoice`. Add `partner = models.ForeignKey("core.Partner", null=True, blank=True, on_delete=models.PROTECT, related_name="+")` to `PurchaseOrder` (keep existing `vendor` FK; mark deprecated in comments).
- `makemigrations`.
- **Files:** `backend/modules/sales/models.py`, `backend/modules/sales/tests/test_models.py`, `backend/modules/invoicing/models.py`, `backend/modules/invoicing/tests/test_models.py`, `backend/modules/purchasing/models.py`, `backend/modules/purchasing/tests/test_models.py`, 3 new migrations
- **Size:** M

### Task 10.6.6 — Serializer support for Partner FK (GREEN)
- SalesQuotation/SalesOrder/Invoice/PurchaseOrder serializers accept either `customer_id` (new) or `customer_name` (legacy). When `customer_id` is passed, populate `customer_name` from `partner.name` in `validate()` or `create()`.
- API tests verifying both paths.
- **Files:** 4 updated serializer modules + their test modules
- **Size:** M

### Task 10.6.7 — Data migration: string → Partner
- Django data migration `RunPython` upserting a Partner for each distinct `(company, customer_name)` tuple across SalesQuotation/SalesOrder/Invoice, setting `is_customer=True`. Similarly for Purchasing vendors: since Purchasing already has a Vendor table, copy each Vendor into Partner with `is_vendor=True` and link `PurchaseOrder.partner`.
- Reverse migration clears FK but leaves Partner records (safe rollback).
- **Files:** new migration in `backend/core/migrations/`
- **Size:** M

### Task 10.6.8 — Partner frontend (RED → GREEN)
- **RED:** `PartnerListPage.test.tsx` + `PartnerFormPage.test.tsx` following form-page pattern.
- **GREEN:** `frontend/src/api/partners.ts`, `PartnerListPage.tsx`, `PartnerFormPage.tsx`, routes in `App.tsx` at `/partners`, `/partners/new`, `/partners/:id/edit`. Sidebar link under a "Contacts" section.
- **Files:** 5 new files + `App.tsx`
- **Size:** M

### Task 10.6.9 — Quotation/Order/Invoice forms accept Partner picker
- **RED:** Update existing form-page tests to assert a `<select>` for Partner appears alongside `customer_name`.
- **GREEN:** Add a `<select>` populated by `fetchPartnersApi({is_customer: true})` on SalesQuotation, SalesOrder, Invoice forms. Selecting updates both `customer_id` and `customer_name`. Typing in `customer_name` directly still works (legacy path).
- **Files:** `sales/QuotationFormPage.tsx`, `sales/SalesOrderFormPage.tsx`, `invoicing/InvoiceFormPage.tsx` + tests
- **Size:** M

### Task 10.6.10 — Verification Gate + commit
- Preview sweep: as NovaPay admin, create a Partner, then a Quotation selecting that Partner from the dropdown, see their name on the list.
- Commit: `feat: Slice 10.6 — Partner model unifies customers and vendors`

### Checkpoint: Slice 10.6
- [ ] `/api/v1/core/partners/` CRUD works
- [ ] SalesQuotation/SalesOrder/Invoice/PurchaseOrder all expose `customer_id`/`partner_id`
- [ ] Data migration populated Partners for all existing rows
- [ ] PartnerListPage + PartnerFormPage live at `/partners/*`
- [ ] `make test` green; preview sweep green

---

## Slice 10.7 — Sequence auto-generation signals (D22)

**Description:** Auto-generate `INV-2026-0001`-style numbers for all numbered entities via `save()` override that calls `core.sequence.get_next_sequence(self.company, prefix)` when the field is blank. Back-fill existing blank rows via migration.

**Dependency:** Slice 10.6 merged (no hard dep, but keeps sequencing story tight).

**Reference industry:** NovaPay.

**Scope:** M (~10 files)

### Task 10.7.1 — Sequence helper tests (RED)
- Test `core.sequence.get_next_sequence(company, prefix)` directly: produces `{PREFIX}-{YYYY}-{0001}`, increments per-company-per-prefix, never collides across companies, year rolls over.
- **Files:** extend `backend/core/tests/test_sequence.py` (or create if missing)
- **Size:** S

### Task 10.7.2 — Sequence helper finalize (GREEN)
- Ensure `get_next_sequence` exists and matches format. If not, implement using a `Sequence` model row per `(company, prefix, year)` with a `SELECT … FOR UPDATE` under an atomic transaction.
- **Files:** `backend/core/sequence.py` (or wherever helper lives) + its tests
- **Size:** S

### Task 10.7.3 — Per-model `save()` override tests (RED)
For each of the 7 numbered entities, one test:
- Create with blank number → number set to `{PREFIX}-{YYYY}-0001`.
- Create with pre-set number `"MANUAL-1"` → number preserved.
- Two back-to-back creates → second gets `…-0002`.
- Two different companies each get their own `…-0001`.

Entities: `invoicing.Invoice` (`INV`), `invoicing.CreditNote` (`CN`), `purchasing.PurchaseOrder` (`PO`), `purchasing.RequestForQuote` (`RFQ`), `sales.SalesQuotation` (`QUO`), `sales.SalesOrder` (`SO`), `accounting.JournalEntry` (`JE`).

- **Files:** add to each module's `test_models.py`
- **Size:** M

### Task 10.7.4 — `save()` overrides (GREEN)
- Each of the 7 models: override `save()` to call `get_next_sequence` when the number field is blank, before `super().save()`.
- **Files:** 7 model files
- **Size:** M

### Task 10.7.5 — Back-fill migration
- Django data migration iterating blank-numbered rows per company and assigning sequence numbers (preserving `created_at` order for stable numbering).
- **Files:** one migration per module (7 migrations)
- **Size:** S

### Task 10.7.6 — Preview sweep + commit
- As NovaPay admin: create a new Invoice, Quotation, SO, PO, JE via the UI — all show auto-generated numbers.
- Commit: `feat: Slice 10.7 — sequence auto-generation signals`

### Checkpoint: Slice 10.7
- [ ] All 7 numbered entities auto-generate numbers on blank save
- [ ] Existing blank rows back-filled
- [ ] `make test` green; preview sweep shows `INV-2026-…` etc.

---

## Slice 10.8 — Design system & visual layer

**Description:** Ship the design system and visual layer so every page looks polished before more modules land. See D33 (plain CSS + variables), D34 (Odoo-inspired), D35 (Lucide icons). Discovered 2026-04-16 when Slice 10.5 preview revealed the frontend has zero CSS files — every page is raw HTML. Adding this now prevents 6 more module slices (11–16) from compounding the problem.

**Why this slice is inserted here:** The next slice (11 Fleet) ships ~6 more pages, and Slices 12–16 ship ~30 more. Every new page should land on top of the design system, not before it — otherwise each future slice pays the retrofit cost again. 10.6 (Partner) and 10.7 (Sequence) don't ship new visible-UI pages, but they also benefit because the Partner CRUD pages will use the new component styles.

**Dependency:** Slice 10.5 merged (uses the now-consistent useTerminology / page markup that 10.5 unified).

**Reference industries:** Preview sweep hits `admin@tablesync.com` (hospitality terminology + burgundy brand color `#9F1239`) and `admin@novapay.com` (fintech + blue `#2563EB`) to prove per-company theming works.

**Scope:** L (~20 files)

### Tasks

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 10.8.1 | Install `lucide-react` | — | XS |
| 10.8.2 | Design tokens `frontend/src/styles/tokens.css` (colors, spacing 4/8/12/16/24/32/48, radius sm/md/lg, shadows, type scale 12/14/16/18/24/32, font stack) | GREEN | S |
| 10.8.3 | Reset + globals `frontend/src/styles/globals.css` (modern-normalize, body/html, focus-visible, base rules for `<table>`/`<form>`/`<h1>`/`<label>`) | GREEN | S |
| 10.8.4 | Import both CSS files from `frontend/src/main.tsx` | GREEN | XS |
| 10.8.5 | Style shared UI (`Button`, `Input`, `Select`, `Modal`, `Badge`) via `frontend/src/components/ui/ui.css`; JSX unchanged | GREEN | M |
| 10.8.6 | Style `AppLayout` shell (topnav + sidebar grid) via `AppLayout.css` targeting existing class names | GREEN | S |
| 10.8.7 | Style `TopNavbar` (accent strip via `var(--accent)`, hamburger, logout) | GREEN | S |
| 10.8.8 | Style `Sidebar` (active highlight) + `AppSwitcher` (4-col grid, brand dot, hover lift) | GREEN | S |
| 10.8.9 | **RED** test: AppLayout asserts Lucide `<svg>` present instead of emoji for sidebar entries | RED | S |
| 10.8.10 | Replace emoji icons in `DEFAULT_SIDEBAR_ITEMS`, `modulesToSidebarItems`, `AppSwitcher` with Lucide components via new `frontend/src/components/moduleIcons.tsx` mapping | GREEN | M |
| 10.8.11 | Style `LoginPage` — centered card on gradient, visible focus rings | GREEN | S |
| 10.8.12 | Add `.page-header` + table base rules in globals so every ListPage inherits the look | GREEN | S |
| 10.8.13 | Add `.form-stack` / `.form-field` rules in globals so every FormPage inherits the look | GREEN | S |
| 10.8.14 | **RED** test for per-company theming — `AppLayout.test.tsx` seeds authStore with `brand_color: "#9F1239"`, asserts `document.documentElement.style.getPropertyValue("--accent") === "#9F1239"` | RED | S |
| 10.8.15 | Implement theming — `AppLayout` useEffect reads `authStore.company.brand_color` and sets `--accent` on html root | GREEN | S |
| 10.8.16 | **RED** a11y tests: `frontend/src/styles/contrast.test.ts` verifies token pairs meet WCAG AA 4.5:1 using a tiny inline luminance helper | RED | S |
| 10.8.17 | Tune tokens until contrast tests pass | GREEN | S |
| 10.8.18 | Preview sweep: login as `admin@tablesync.com` then `admin@novapay.com`, screenshot Login / Home / Sales Orders list / Quotation form; verify zero console errors and visibly different brand colors | VERIFY | M |
| 10.8.19 | Full vitest + pytest green + commit `feat: Slice 10.8 — design system, Lucide icons, per-company theming` | VERIFY | S |

### Checkpoint: Slice 10.8
- [ ] `tokens.css` + `globals.css` imported from main.tsx
- [ ] Button/Input/Select/Modal/Badge visibly styled
- [ ] AppLayout shell looks professional
- [ ] Lucide icons replace emojis
- [ ] LoginPage redesigned with centered card
- [ ] `--accent` CSS var driven by active company's `brand_color`
- [ ] TableSync (burgundy) and NovaPay (blue) visibly differ at login + logged-in header
- [ ] 229+ frontend tests green (plus ~3 new tests for theming + icons + contrast)
- [ ] Zero console errors in preview sweep
- [ ] Commit `feat: Slice 10.8 — design system, Lucide icons, per-company theming`

---

## Slice 11 — Fleet module (Module Scaffold Pattern)

**Description:** Track vehicles, drivers, maintenance, fuel, and services. Reference industry SwiftRoute.

**Dependency:** Slice 10.7 merged.

**Entities:** `Vehicle`, `Driver`, `MaintenanceLog`, `FuelLog`, `VehicleService` (see SPEC.md §Slice 11).

**Scope:** L (~22 files)

Follow the 9-step Module Scaffold Pattern exactly. Task breakdown:

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 11.1 | Scaffold `backend/modules/fleet/` (apps.py, models.py stub, migrations/, tests/) | — | XS |
| 11.2 | Model tests for Vehicle, Driver, MaintenanceLog, FuelLog, VehicleService (creation, `__str__`, FKs, uniqueness, company isolation) | RED | M |
| 11.3 | Implement 5 models + factories + `INSTALLED_APPS` += `modules.fleet` + `makemigrations fleet` | GREEN | M |
| 11.4 | API tests — for each of 5 endpoints: list/create/retrieve/update/delete + filters (Vehicle by status+driver; MaintenanceLog by status+vehicle; FuelLog by vehicle) + cross-company isolation | RED | M |
| 11.5 | Serializers + ViewSets (`IsCompanyMember` + `CompanyScopedFilterBackend` + `pagination_class = None` + `perform_create` sets company) + `backend/modules/fleet/urls.py` + include in `backend/api/v1/urls.py` at `fleet/` | GREEN | M |
| 11.6 | Frontend tests — `VehicleListPage.test.tsx`, `VehicleFormPage.test.tsx`, `DriverListPage.test.tsx`, `DriverFormPage.test.tsx`, `MaintenanceLogListPage.test.tsx`, `FuelLogListPage.test.tsx` (mock `api/config`, reset `configStore`, use `fireEvent`, use `useTerminology`) | RED | M |
| 11.7 | `frontend/src/api/fleet.ts` + 6 page components (lists use `useTerminology`, forms handle create+edit) | GREEN | M |
| 11.8 | Register routes in `App.tsx`: `/fleet/vehicles`, `/fleet/vehicles/new`, `/fleet/vehicles/:id/edit`, same pattern for drivers; list-only routes for maintenance and fuel logs | — | XS |
| 11.9 | Preview sweep (SwiftRoute admin: create Driver, create Vehicle assigning that Driver, log maintenance, log fuel — all visible in lists with SwiftRoute terminology) + full suite green + commit `feat: implement Slice 11 Fleet module` | VERIFY | S |

### Checkpoint: Slice 11
- [ ] 5 Fleet models migrated
- [ ] 5 endpoints under `/api/v1/fleet/`
- [ ] 6 frontend pages routed
- [ ] Preview sweep clean for SwiftRoute admin
- [ ] Commit `feat: implement Slice 11 Fleet module`

---

## Slice 12 — Projects module (Module Scaffold Pattern + Kanban + Partner FK)

**Description:** Project management with kanban-able Tasks, Milestones, and Timesheets. Uses Partner FK for client. Reference industry CraneStack.

**Dependency:** Slice 11 merged.

**Entities:** `Project` (with `customer = FK(core.Partner)`), `Task` (parent_task self-FK), `Milestone`, `ProjectTimesheet` (see SPEC.md §Slice 12).

**Scope:** L (~22 files)

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 12.1 | Scaffold `backend/modules/projects/` | — | XS |
| 12.2 | Model tests (4 entities, Task self-FK, Project-Partner FK, company isolation) | RED | M |
| 12.3 | Implement models + factories + `INSTALLED_APPS` + migration | GREEN | M |
| 12.4 | API tests + `@action GET /projects/{id}/progress/` returning aggregates | RED | M |
| 12.5 | Serializers + ViewSets + `/progress/` action + URL registration | GREEN | M |
| 12.6 | Frontend tests — ProjectListPage/FormPage, TaskListPage (with Kanban toggle), MilestoneListPage | RED | M |
| 12.7 | API client + page components; Task page uses existing `KanbanView.tsx` component grouped by status | GREEN | M |
| 12.8 | Routes in `App.tsx`: `/projects/projects`, `/new`, `/:id/edit`, `/projects/tasks`, `/projects/milestones` | — | XS |
| 12.9 | Preview sweep (CraneStack admin: create Project assigned to a Partner "client", create Tasks, drag across kanban, log Timesheet) + commit `feat: implement Slice 12 Projects module` | VERIFY | S |

### Checkpoint: Slice 12
- [ ] Project FK to Partner works
- [ ] Task Kanban drag-drop changes status
- [ ] `/projects/progress/` returns aggregates
- [ ] Commit `feat: implement Slice 12 Projects module`

---

## Slice 13 — Manufacturing module (Module Scaffold Pattern + Inventory integration)

**Description:** Bills of materials, work orders, and production cost. Integrates with Inventory (consume components, produce finished goods). Reference industry TableSync (BOMs = recipes).

**Dependency:** Slice 12 merged.

**Entities:** `BillOfMaterials`, `BOMLine`, `WorkOrder`, `ProductionCost` (see SPEC.md §Slice 13).

**Scope:** L (~24 files)

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 13.1 | Scaffold `backend/modules/manufacturing/` | — | XS |
| 13.2 | Model tests (4 entities, BOMLine references `inventory.Product`, WorkOrder status transitions, company isolation) | RED | M |
| 13.3 | Implement models + factories + migration | GREEN | M |
| 13.4 | API tests: CRUD for 4 entities + `@action POST /work-orders/{id}/start/` (validates status=draft→in_progress) + `/complete/` (creates `StockMove` rows for each BOMLine consumed and for finished product) | RED | M |
| 13.5 | Serializers + ViewSets + actions + URL include | GREEN | M |
| 13.6 | Frontend tests — BOMListPage, BOMFormPage (with child BOMLines inline), WorkOrderListPage, WorkOrderFormPage, "Start" / "Complete" buttons invoke actions | RED | M |
| 13.7 | API client + page components | GREEN | M |
| 13.8 | Routes in `App.tsx`: `/manufacturing/boms`, `/manufacturing/work-orders` + edit | — | XS |
| 13.9 | Preview sweep (TableSync admin: create Recipe BOM with 3 ingredient lines, create WorkOrder, Start, Complete, verify StockMoves appear in Inventory) + commit `feat: implement Slice 13 Manufacturing module` | VERIFY | S |

### Checkpoint: Slice 13
- [ ] WorkOrder completion creates correct StockMoves in Inventory
- [ ] BOM form supports adding/removing lines inline
- [ ] Commit `feat: implement Slice 13 Manufacturing module`

---

## Slice 14 — Point of Sale module (Module Scaffold Pattern + Partner FK + Sequence + Inventory integration)

**Description:** POS sessions, orders with lines, cash movements. Uses Partner FK for customer. Reference industry TableSync.

**Dependency:** Slice 13 merged.

**Entities:** `POSSession`, `POSOrder`, `POSOrderLine`, `CashMovement` (see SPEC.md §Slice 14).

**Scope:** L (~22 files)

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 14.1 | Scaffold `backend/modules/pos/` | — | XS |
| 14.2 | Model tests (Session open/close, Order uses Partner FK, OrderLine references inventory.Product, CashMovement types, company isolation) | RED | M |
| 14.3 | Implement models + factories + migration; POSOrder uses Slice 10.7 sequence auto-gen with prefix `POS` | GREEN | M |
| 14.4 | API tests: CRUD + `@action POST /sessions/{id}/close/` computing cash variance + POSOrder create with nested lines in one POST | RED | M |
| 14.5 | Serializers + ViewSets + actions + URL include | GREEN | M |
| 14.6 | Frontend tests — POSSessionListPage, POSSessionFormPage, POSOrderListPage, POSOrderFormPage | RED | M |
| 14.7 | API client + pages (form is touch-friendly with big buttons) | GREEN | M |
| 14.8 | Routes in `App.tsx`: `/pos/sessions`, `/pos/orders` + edit | — | XS |
| 14.9 | Preview sweep (TableSync admin: open session with $100 cash, create order with 3 menu items, close session, verify variance) + commit `feat: implement Slice 14 POS module` | VERIFY | S |

### Checkpoint: Slice 14
- [ ] Session close computes variance correctly
- [ ] POSOrder number auto-generates (`POS-2026-…`)
- [ ] Commit `feat: implement Slice 14 POS module`

---

## Slice 15 — Helpdesk module (Module Scaffold Pattern + Kanban)

**Description:** Support tickets with SLA tracking and a knowledge base. Ticket status runs on a Kanban. Reference industry MedVista (patient support) or NovaPay (merchant support).

**Dependency:** Slice 14 merged.

**Entities:** `TicketCategory`, `SLAConfig`, `Ticket` (with auto-seq `TKT` per Slice 10.7 pattern, reporter = FK Partner or User, assignee = User), `KnowledgeArticle` (see SPEC.md §Slice 15).

**Scope:** L (~22 files)

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 15.1 | Scaffold `backend/modules/helpdesk/` | — | XS |
| 15.2 | Model tests (4 entities, Ticket sequence, SLA deadline computation, company isolation) | RED | M |
| 15.3 | Implement models + factories + migration; add `TKT` prefix to sequence auto-gen list | GREEN | M |
| 15.4 | API tests: CRUD + `@action POST /tickets/{id}/resolve/` + `/reopen/` + filter by status/category/assignee | RED | M |
| 15.5 | Serializers + ViewSets + actions + URL include | GREEN | M |
| 15.6 | Frontend tests — CategoryListPage, TicketListPage (with Kanban toggle), TicketFormPage, ArticleListPage, ArticleFormPage | RED | M |
| 15.7 | API client + pages; TicketListPage has kanban/list toggle using existing `KanbanView.tsx` | GREEN | M |
| 15.8 | Routes in `App.tsx`: `/helpdesk/tickets`, `/helpdesk/categories`, `/helpdesk/articles` + edit routes | — | XS |
| 15.9 | Preview sweep (MedVista admin: create Category with SLA, open Ticket, assign, resolve, verify timestamps) + commit `feat: implement Slice 15 Helpdesk module` | VERIFY | S |

### Checkpoint: Slice 15
- [ ] Ticket auto-generates `TKT-…` number
- [ ] Ticket Kanban toggle works
- [ ] Resolve action sets `resolved_at`
- [ ] Commit `feat: implement Slice 15 Helpdesk module`

---

## Slice 16 — Reports / BI + Pivot + Graph views (D23, D24)

**Description:** Build the reporting surface that's been deferred since Slice 2: `PivotView.tsx` and `GraphView.tsx` generic renderers + a new `/aggregate/` DRF action on every module ViewSet + ReportTemplate / PivotDefinition / ScheduledExport models for saved reports.

**Dependency:** Slice 15 merged (needs all modules shipping first to have data to aggregate).

**Scope:** XL (~28 files) — largest slice. Consider splitting if it runs long; see "Split option" below.

### Tasks

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 16.1 | Install `recharts` frontend dep (`package.json` + lock) | — | XS |
| 16.2 | Scaffold `backend/modules/reports/` | — | XS |
| 16.3 | Model tests: ReportTemplate, PivotDefinition, ScheduledExport (creation, company isolation, default filters JSONB) | RED | S |
| 16.4 | Models + factories + migration + extend `ViewDefinition.view_type` choices to include `pivot` and `graph` | GREEN | S |
| 16.5 | Shared `/aggregate/` mixin for ViewSets — TDD: backend test asserting `/api/v1/invoicing/invoices/aggregate/?group_by=status&measure=total_amount&op=sum` returns `[{group:…, value:…}]`, respects company-scoping, rejects invalid fields | RED | M |
| 16.6 | Implement `AggregationMixin` with Django `values(group_by).annotate(Sum/Count/Avg(measure))`, validate fields against serializer-declared aggregatable set, inherit `CompanyScopedFilterBackend` | GREEN | M |
| 16.7 | Apply mixin to existing module ViewSets (Invoice, Sales, PO, JournalEntry, Product, Ticket, WorkOrder, etc.) — one commit-worth of wiring with a shared abstract viewset base | GREEN | M |
| 16.8 | Frontend tests — `PivotView.test.tsx`, `GraphView.test.tsx`, `ReportBuilderPage.test.tsx` (render from config, call aggregate endpoint, render values / Recharts bars) | RED | M |
| 16.9 | Implement `PivotView.tsx` (HTML table with row/col drilldown from JSON config), `GraphView.tsx` (Recharts `BarChart`/`LineChart`/`PieChart`/`AreaChart` switched on config.chart_type), `ReportBuilderPage.tsx` (picks model, group_by, measure, view type) | GREEN | L |
| 16.10 | Report module list/form pages (existing pattern) + routes `/reports`, `/reports/builder` | RED → GREEN | M |
| 16.11 | Preview sweep (NovaPay admin: open Reports, build "Invoices by Status" pivot + bar chart, save as template, reload) + commit `feat: implement Slice 16 Reports BI + Pivot + Graph` | VERIFY | S |

**Split option (only if slice exceeds 1 day):** Split into 16A (aggregate endpoint + PivotView + ReportBuilderPage) and 16B (GraphView + ScheduledExport + ReportTemplate CRUD). Both must ship before Slice 17.

### Checkpoint: Slice 16
- [ ] `/aggregate/` action works on at least 8 existing ViewSets
- [ ] PivotView + GraphView render from `ViewDefinition` configs
- [ ] Preview sweep shows functional pivot and bar chart
- [ ] Commit `feat: implement Slice 16 Reports BI + Pivot + Graph`

---

## Slice 17 — Industry demo seeding (D26)

**Description:** Per-module `seed_<module>_demo` commands + a meta-command `seed_industry_demo --company <slug>` that dispatches based on `INDUSTRY-BRANDING-CONTEXT.md`. Idempotent (`--reset` flag). Produces 10–30 records per module per company.

**Dependency:** Slice 16 merged (all modules must exist).

**Scope:** L (~18 files)

### Tasks

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 17.1 | Shared test harness: `backend/core/tests/test_seed_commands.py` asserts each `seed_<module>_demo --company <slug>` creates N records and is idempotent on re-run | RED | S |
| 17.2 | Implement `seed_hr_demo`, `seed_inventory_demo`, `seed_calendar_demo`, `seed_sales_demo`, `seed_purchasing_demo`, `seed_invoicing_demo`, `seed_accounting_demo` (7 commands covering shipped modules) | GREEN | M |
| 17.3 | Implement `seed_fleet_demo`, `seed_projects_demo`, `seed_manufacturing_demo`, `seed_pos_demo`, `seed_helpdesk_demo` (5 commands for Slices 11–15 modules) | GREEN | M |
| 17.4 | Implement `seed_reports_demo` (creates sample ReportTemplate + PivotDefinition rows) | GREEN | S |
| 17.5 | Test for meta-command `seed_industry_demo --company <slug>` reading industry → module subset mapping | RED | S |
| 17.6 | Implement meta-command; mapping table lives in `backend/core/industry_modules.py` (derived from INDUSTRY-BRANDING-CONTEXT §module subsets per industry) | GREEN | S |
| 17.7 | Preview sweep (run `seed_industry_demo --company dentaflow` then login as admin@dentaflow.com; confirm Employees, Products, Appointments, Invoices all seeded with DentaFlow terminology) + commit `feat: implement Slice 17 industry demo seeding` | VERIFY | S |

### Checkpoint: Slice 17
- [ ] Each of 13 module commands idempotent
- [ ] Meta-command composes correctly per industry
- [ ] Preview sweep shows rich demo data for at least 3 industries
- [ ] Commit `feat: implement Slice 17 industry demo seeding`

---

## Slice 18 — Calendar polling sync (D27)

**Description:** Enable bidirectional calendar sync via polling. `external_uid` already exists on Event from Slice 5.

**Dependency:** Slice 17 merged (easier to test with seeded events).

**Scope:** M (~10 files)

### Tasks

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 18.1 | API tests — `GET /api/v1/calendar/events/?updated_since=<iso8601>` returns events updated after the timestamp, includes `external_uid`; respects company isolation | RED | S |
| 18.2 | Implement `updated_since` filter in `EventViewSet.get_queryset` (already partially scoped in Slice 5 — verify + extend) | GREEN | S |
| 18.3 | API tests — `POST /api/v1/calendar/events/` upserts by `external_uid` with last-write-wins on `updated_at`; test LWW: same event submitted twice, older version wins when older `updated_at` | RED | S |
| 18.4 | Implement upsert-by-external_uid in `EventViewSet.create` + LWW logic | GREEN | S |
| 18.5 | API tests — `POST /api/v1/calendar/events/bulk/` accepts array of up to 500 events, returns per-item status | RED | S |
| 18.6 | Implement `@action(detail=False, methods=["post"]) def bulk` on EventViewSet | GREEN | S |
| 18.7 | Document the sync contract in `docs/CALENDAR-SYNC-POLLING.md` (links to CALENDAR-SYNC-API-SPEC.md for full design) | — | XS |
| 18.8 | Manual verification: use `curl` or a scratch Python script to round-trip an event between two companies; verify LWW. Commit `feat: implement Slice 18 calendar polling sync` | VERIFY | S |

### Checkpoint: Slice 18
- [ ] Two-way sync via `/events/` + `/events/bulk/` works
- [ ] LWW conflict resolution verified via test
- [ ] Commit `feat: implement Slice 18 calendar polling sync`

---

## Slice 19 — Polish pass (D25)

**Description:** UI polish, per-company theming, WebSocket notifications, audit log timeline, lightweight HomePage with ORM-aggregate KPIs. Final slice of this cycle.

**Dependency:** Slice 18 merged.

**Scope:** XL (~25 files) — same caveat as Slice 16; split if needed into 19A (UI polish + theming) and 19B (WebSocket + audit UI + HomePage).

### Tasks

| # | Task | Phase | Scope |
|---|------|-------|-------|
| 19.1 | Frontend tests for `ErrorBoundary.tsx`, `Skeleton.tsx`, `EmptyState.tsx`, `Breadcrumbs.tsx` | RED | S |
| 19.2 | Implement those four shared components in `frontend/src/components/` | GREEN | S |
| 19.3 | Wrap `App.tsx` routes in `<ErrorBoundary>`; replace ad-hoc `<div>Loading...</div>` with `<Skeleton />` in list pages; replace empty tables with `<EmptyState />`; add `<Breadcrumbs />` to AppLayout | GREEN | M |
| 19.4 | Test for per-company theming: mounting `AppLayout` with `Company.brand_color = "#EA580C"` sets `document.documentElement.style.setProperty('--accent', …)` | RED | S |
| 19.5 | Apply CSS custom properties (`--accent`, `--accent-fg`, `--accent-hover`) from brand color; update `globals.css` so all primary buttons/links use them | GREEN | S |
| 19.6 | Test for WebSocket notification consumer: connecting to `/ws/notifications/` with a JWT, then creating a Ticket for the connected user's company, results in a websocket event | RED | S |
| 19.7 | Django Channels consumer at `/ws/notifications/`, routing in `config/routing.py`, signal handlers on `Ticket` / `Invoice` / `StockMove` post_save | GREEN | M |
| 19.8 | Frontend test for `useNotifications()` hook: connects, receives event, updates bell badge count | RED | S |
| 19.9 | `useNotifications` hook + `NotificationBell` in TopNavbar | GREEN | M |
| 19.10 | Test for `AuditLogTimelinePage` at `/settings/audit-log` — renders most recent AuditLog entries for active company, filters by entity type | RED | S |
| 19.11 | Implement `AuditLogTimelinePage.tsx` + route | GREEN | S |
| 19.12 | Test for HomePage KPIs: renders 4–6 ORM-aggregate tiles per industry (e.g., "Open Invoices", "Pending Tickets", "Low Stock Items") — tiles come from a `/api/v1/core/home-kpis/` endpoint | RED | S |
| 19.13 | Implement `/api/v1/core/home-kpis/` returning per-industry KPI list (computed from ORM aggregates, no materialized views — D25) + `HomePage.tsx` at `/` | GREEN | M |
| 19.14 | Preview sweep across all 10 industry admins: brand color correct, HomePage KPIs correct, AppSwitcher shows 13 modules, notification bell works, audit log populated, no console errors. Commit `feat: implement Slice 19 polish pass` | VERIFY | M |

### Checkpoint: Slice 19 / Cycle complete
- [ ] All 10 industry admins log in cleanly with correct branding
- [ ] Every one of 13 modules has functional List + Form pages
- [ ] Pivot and Graph reports render from seeded data
- [ ] Sequence numbers auto-generate on every numbered entity
- [ ] Partner FK consistently used across Sales/Invoicing/Purchasing/Projects/POS/Helpdesk
- [ ] `make test` green with ≥80% coverage
- [ ] Commit `feat: implement Slice 19 polish pass` (final commit of this cycle)
- [ ] Ready for `/review` (Phase E of the approved plan — NOT `/ship`, per D30)

---

## Part 2 — Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Partner data migration (10.6.7) damages existing prod-ish data | High | Test migration on `docker compose down -v && up && migrate && seed` fresh DB first; include reverse migration; commit before running on any live branch |
| Sequence signals (10.7) clobber user-supplied numbers during import | Medium | Guard clause: only auto-gen when field is blank; test asserts pre-set numbers preserved |
| `/aggregate/` endpoint (16.6) opens query injection via `group_by` param | High — security | Whitelist: each ViewSet declares `aggregatable_fields` list; reject other values with 400; unit-test rejects non-whitelisted |
| Recharts bundle size balloons frontend | Low | Tree-shake: import only `BarChart`, `LineChart`, `PieChart`, `AreaChart` + their children; check bundle with `vite build --report` at Slice 16 end |
| WebSocket infrastructure (19.7) flaky under Docker ASGI config | Medium | Django Channels already in tech stack; test with `pytest-asyncio` + Channels test client; if complex, scope 19 to HTTP polling fallback first and add WS later |
| Seed command idempotency bugs cause dupes on re-run | Medium | Every seeder checks `get_or_create` or `update_or_create` keyed on `(company, natural_key)`; tests verify re-run yields same count |

---

## Part 2 — Skills Used Per Slice

| Slice | Primary Skill | Supporting Skills |
|-------|---------------|-------------------|
| 10.5 | `incremental-implementation` | `test-driven-development`, `frontend-ui-engineering` |
| 10.6 | `test-driven-development` | `api-and-interface-design`, `security-and-hardening` (FK cross-company access) |
| 10.7 | `test-driven-development` | `incremental-implementation` |
| 11–15 | `incremental-implementation` | `test-driven-development`, `source-driven-development`, `frontend-ui-engineering` |
| 16 | `test-driven-development` | `api-and-interface-design`, `security-and-hardening` (whitelist fields), `frontend-ui-engineering` |
| 17 | `incremental-implementation` | `test-driven-development` |
| 18 | `test-driven-development` | `api-and-interface-design` |
| 19 | `incremental-implementation` | `test-driven-development`, `frontend-ui-engineering`, `security-and-hardening` (WS auth) |

---

## Parallelization Notes

- **Do NOT parallelize across slices.** D32 orders them by dependency; each slice modifies shared files (`App.tsx`, `INSTALLED_APPS`, `api/v1/urls.py`). Running two slices in parallel would merge-conflict.
- **Within a slice, sequential order is the 9-step pattern.** No parallel sub-tasks.
- **Acceptable parallelism:** Writing frontend tests (RED step) while backend is still being implemented is fine since they touch different files.

---

## Open Questions for this plan

None. All design decisions are in DECISION.md (D1–D32). If a slice uncovers new constraints, append a new Decision and update this plan.
