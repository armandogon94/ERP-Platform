# Implementation Plan: ERP Platform — Slices 0 & 1

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
