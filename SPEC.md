# Spec: ERP Platform (Project 14)

## Objective

Build an Odoo-inspired multi-tenant ERP platform serving 10 distinct industries with 13 core modules. Each industry runs on the same Django/React codebase and PostgreSQL schema with no code duplication. Differences between industries are driven entirely by configuration (terminology, field visibility, workflow labels, dashboard widgets, anomaly alerts).

**User stories:**
- As an industry CEO, I see a dashboard with KPIs relevant to my business, with anomaly alerts for metrics outside normal ranges.
- As a department manager, I access only the modules relevant to my role, with data filtered to my scope (department/own records).
- As a system admin, I configure modules, manage users and roles, and customize views per company.
- As an accountant, I create journal entries with enforced double-entry, post invoices, reconcile bank statements.
- As a warehouse manager, I track inventory with lot/serial numbers, reorder rules, and stock movements across locations.

**Success criteria:**
- All 13 modules functional with CRUD + business logic
- 10 industries configured with correct terminology, roles, and dashboards
- Multi-tenancy enforced: Company A's data never visible to Company B
- RBAC working: 80 industry-specific roles with correct permissions
- 80%+ test coverage (backend + frontend)
- Docker Compose starts all services on Apple Silicon Mac
- Each vertical slice independently demoable in browser

## Tech Stack

| Component | Technology | Version |
|-----------|-----------|---------|
| Backend | Django + Django REST Framework | 5.x + 3.15+ |
| Frontend | React + TypeScript + Vite | 18 + 5.x + 5.x |
| Database | PostgreSQL | 15+ |
| Cache/Broker | Redis | 7.x |
| Task Queue | Celery + Celery Beat | 5.x |
| Real-Time | Django Channels | 4.x |
| Auth | djangorestframework-simplejwt | latest |
| API Docs | drf-spectacular (OpenAPI 3) | latest |
| Testing (BE) | pytest + pytest-django + factory_boy + pytest-cov | latest |
| Testing (FE) | vitest + @testing-library/react | latest |
| Linting (BE) | Black + isort + flake8 + mypy | latest |
| Linting (FE) | ESLint + Prettier | latest |
| Containers | Docker + Docker Compose | latest |
| State Mgmt | Zustand | latest |
| DnD | @dnd-kit/core | latest |
| Charting | Recharts or Chart.js | latest |

## Commands

```bash
# Development
make dev              # docker-compose up --build (all 6 services)
make migrate          # docker-compose exec django python manage.py migrate
make seed             # docker-compose exec django python manage.py seed_all
make shell            # docker-compose exec django python manage.py shell_plus
make createsuperuser  # docker-compose exec django python manage.py createsuperuser

# Testing
make test             # Run pytest + vitest (both backends and frontend)
make test-backend     # docker-compose exec django pytest --cov --cov-report=term-missing
make test-frontend    # docker-compose exec react npx vitest run --coverage

# Code Quality
make lint             # Run Black + isort + flake8 (backend) + ESLint + Prettier (frontend)
make format           # Auto-format with Black + isort + Prettier
make typecheck        # mypy (backend) + tsc --noEmit (frontend)

# Build & Clean
make build            # docker-compose build
make clean            # docker-compose down -v --remove-orphans
make logs             # docker-compose logs -f
```

## Project Structure

```
14-ERP-Platform/
├── SPEC.md                          # This file
├── DECISION.md                      # Design decisions log
├── CLAUDE.md                        # Project instructions for Claude
├── Makefile                         # Dev workflow commands
├── docker-compose.yml               # 6 services
├── .env.example                     # Environment template
├── .gitignore
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── pyproject.toml               # pytest + tool config
│   ├── manage.py
│   ├── conftest.py                  # Global pytest fixtures
│   │
│   ├── config/                      # Django project settings
│   │   ├── __init__.py
│   │   ├── settings/
│   │   │   ├── base.py              # Shared settings
│   │   │   ├── dev.py               # Development overrides
│   │   │   └── test.py              # Test overrides
│   │   ├── urls.py                  # Root URL config
│   │   ├── wsgi.py
│   │   ├── asgi.py                  # Django Channels
│   │   ├── celery_config.py         # Celery app factory
│   │   └── routing.py               # WebSocket routing
│   │
│   ├── core/                        # Core app (multi-tenancy, auth, RBAC)
│   │   ├── models.py                # Company, User, Role, Permission, etc.
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── middleware.py            # CompanyRoleContextMiddleware
│   │   ├── signals.py               # AuditLog signals
│   │   ├── sequence.py              # Sequence number generator
│   │   ├── config.py                # Industry config loader
│   │   ├── consumers.py             # WebSocket consumers
│   │   ├── notifications.py         # Notification utilities
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── factories.py             # factory_boy factories
│   │   ├── services/
│   │   │   └── company_provisioning.py
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── load_industry_config.py
│   │   │       ├── seed_role_templates.py
│   │   │       └── seed_all.py
│   │   └── tests/
│   │       ├── test_models.py
│   │       ├── test_views.py
│   │       ├── test_middleware.py
│   │       ├── test_config.py
│   │       └── test_consumers.py
│   │
│   ├── api/
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py              # JWT login/logout/refresh
│   │       ├── permissions.py       # ModulePermission, IsCompanyMember
│   │       ├── pagination.py        # Cursor-based pagination
│   │       ├── filters.py           # Company-scoped filtering
│   │       └── urls.py              # API URL routing
│   │
│   ├── accounting/                  # Module app
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── factories.py
│   │   └── tests/
│   │       ├── test_models.py
│   │       └── test_views.py
│   │
│   ├── invoicing/                   # Module app (same pattern)
│   ├── inventory/
│   ├── fleet/
│   ├── calendar_app/                # 'calendar' is Python stdlib
│   ├── hr/
│   ├── project/                     # 'projects' might conflict
│   ├── purchasing/
│   ├── sales/
│   ├── manufacturing/
│   ├── pos/
│   ├── helpdesk/
│   ├── reports/
│   │
│   ├── tasks/                       # Celery tasks
│   │   ├── analytics.py             # Materialized view refresh
│   │   ├── anomaly_detection.py     # Anomaly checking
│   │   ├── invoicing.py             # Recurring invoices
│   │   ├── helpdesk.py              # SLA breach checks
│   │   └── reports.py               # Scheduled report generation
│   │
│   ├── fixtures/
│   │   └── industry_role_templates.json  # 80 role templates
│   │
│   └── industries/                  # Industry configs
│       ├── novapay/
│       │   └── config/
│       │       └── modules.yaml
│       ├── medvista/
│       ├── trustguard/
│       ├── urbannest/
│       ├── swiftroute/
│       ├── dentaflow/
│       ├── jurispath/
│       ├── tablesync/
│       ├── cranestack/
│       └── edupulse/
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── index.html
│   │
│   └── src/
│       ├── main.tsx                 # Entry point
│       ├── App.tsx                  # Router shell
│       │
│       ├── api/
│       │   ├── client.ts            # Axios instance + JWT interceptor
│       │   ├── types.ts             # TypeScript interfaces
│       │   └── auth.ts              # Auth API functions
│       │
│       ├── store/
│       │   ├── authStore.ts         # Zustand: user, JWT, company
│       │   └── companyStore.ts      # Zustand: active company, modules
│       │
│       ├── hooks/
│       │   ├── useAuth.ts
│       │   ├── useCompany.ts
│       │   ├── useModuleConfig.ts
│       │   ├── useTerminology.ts
│       │   ├── useList.ts           # Generic list data fetching
│       │   ├── useForm.ts           # Generic form data fetching
│       │   ├── useAPI.ts            # CRUD wrapper
│       │   └── useNotifications.ts  # WebSocket + bell
│       │
│       ├── views/                   # Odoo-style view renderers
│       │   ├── FormView.tsx
│       │   ├── ListView.tsx
│       │   ├── KanbanView.tsx
│       │   ├── PivotView.tsx
│       │   └── GraphView.tsx
│       │
│       ├── components/
│       │   ├── layout/
│       │   │   ├── AppLayout.tsx
│       │   │   ├── TopNavbar.tsx
│       │   │   └── Sidebar.tsx
│       │   ├── module-switcher/
│       │   │   └── AppSwitcher.tsx
│       │   └── common/
│       │       ├── Button.tsx
│       │       ├── Input.tsx
│       │       ├── Select.tsx
│       │       ├── Modal.tsx
│       │       ├── Drawer.tsx
│       │       ├── Toast.tsx
│       │       ├── DatePicker.tsx
│       │       ├── Badge.tsx
│       │       ├── Breadcrumb.tsx
│       │       └── NotificationBell.tsx
│       │
│       ├── modules/                 # Per-module pages/components
│       │   ├── accounting/
│       │   ├── invoicing/
│       │   ├── inventory/
│       │   ├── fleet/
│       │   ├── calendar/
│       │   ├── hr/
│       │   ├── project/
│       │   ├── purchasing/
│       │   ├── sales/
│       │   ├── manufacturing/
│       │   ├── pos/
│       │   ├── helpdesk/
│       │   └── reports/
│       │
│       ├── pages/
│       │   ├── LoginPage.tsx
│       │   └── DashboardPage.tsx
│       │
│       └── styles/
│           ├── theme.ts             # Odoo purple + dynamic brand
│           └── globals.css
│
└── plans/                           # Planning documents (existing)
    ├── ERP-MASTER-PLAN.md
    ├── INDUSTRY-BRANDING-CONTEXT.md
    ├── RALPH-LOOP-CONFIG.md
    ├── CALENDAR-SYNC-API-SPEC.md
    └── CLAUDE-CODE-INSTANCE-PROMPTS-14.md
```

## Code Style

### Python (Backend)

```python
# Models: PascalCase class names, snake_case fields
class PurchaseOrder(TenantModel):
    """Purchase order with state machine lifecycle."""
    
    class State(models.TextChoices):
        DRAFT = "draft", "Draft"
        CONFIRMED = "confirmed", "Confirmed"
        RECEIVED = "received", "Received"
        DONE = "done", "Done"
        CANCELLED = "cancelled", "Cancelled"

    name = models.CharField(max_length=64, unique=True)
    vendor = models.ForeignKey("sales.Partner", on_delete=models.PROTECT)
    state = models.CharField(max_length=20, choices=State.choices, default=State.DRAFT)
    order_date = models.DateField()
    amount_total = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    class Meta:
        db_table = "purchasing_purchase_order"
        ordering = ["-order_date"]

    def confirm(self, user):
        """Transition from draft to confirmed. Generates sequence number."""
        if self.state != self.State.DRAFT:
            raise ValidationError("Only draft orders can be confirmed.")
        self.name = get_next_sequence(self.company, "PO")
        self.state = self.State.CONFIRMED
        self.save(update_fields=["name", "state", "updated_at"])


# ViewSets: inherit from DynamicModelViewSet
class PurchaseOrderViewSet(DynamicModelViewSet):
    module_name = "purchasing"
    serializer_class = PurchaseOrderSerializer
    filterset_fields = ["state", "vendor"]
    search_fields = ["name", "vendor__name"]
    
    @action(detail=True, methods=["post"])
    def confirm(self, request, pk=None):
        order = self.get_object()
        order.confirm(request.user)
        return Response(self.get_serializer(order).data)


# Tests: use factory_boy, descriptive names
class TestPurchaseOrderConfirm:
    def test_confirm_generates_sequence_number(self, api_client, company):
        order = PurchaseOrderFactory(company=company, state="draft")
        response = api_client.post(f"/api/v1/purchasing/orders/{order.id}/confirm/")
        assert response.status_code == 200
        assert response.data["name"].startswith("PO/2026/")
    
    def test_confirm_rejects_non_draft(self, api_client, company):
        order = PurchaseOrderFactory(company=company, state="confirmed")
        response = api_client.post(f"/api/v1/purchasing/orders/{order.id}/confirm/")
        assert response.status_code == 400
```

### TypeScript (Frontend)

```typescript
// Components: PascalCase, functional, typed props
interface ListViewProps {
  modelName: string;
  viewConfig: ViewConfig;
  onRowClick?: (id: number) => void;
}

export function ListView({ modelName, viewConfig, onRowClick }: ListViewProps) {
  const { data, isLoading, pagination, sort, setSort } = useList(modelName, viewConfig);
  const { t } = useTerminology();

  if (isLoading) return <Skeleton />;

  return (
    <table>
      <thead>
        <tr>
          {viewConfig.fields.map((field) => (
            <th key={field.name} onClick={() => setSort(field.name)}>
              {t(field.label)}
              {sort.field === field.name && <SortIcon direction={sort.direction} />}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {data.map((row) => (
          <tr key={row.id} onClick={() => onRowClick?.(row.id)}>
            {viewConfig.fields.map((field) => (
              <td key={field.name}>{formatField(row[field.name], field.type)}</td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  );
}

// Hooks: camelCase, return typed objects
function useList(modelName: string, config: ViewConfig) {
  const { company } = useCompany();
  // ...implementation
}
```

### Key Conventions
- Python: Black (88 char line), isort (profile=black), flake8
- TypeScript: ESLint + Prettier (2-space indent, single quotes, trailing commas)
- Naming: PascalCase for classes/components, snake_case for Python vars/functions, camelCase for TS vars/functions
- Imports: absolute imports in Python (from core.models import Company), relative in TypeScript (@/components/...)
- No `any` types in TypeScript
- No print() in Python (use logging)

## Testing Strategy

### Framework & Location
- **Backend:** pytest + pytest-django + factory_boy. Tests in `{module}/tests/test_*.py`
- **Frontend:** vitest + @testing-library/react. Tests co-located: `Component.test.tsx`
- **Coverage:** 80%+ required for both backend and frontend

### Test Levels

| Level | Tool | What it tests | Where |
|-------|------|--------------|-------|
| Unit (BE) | pytest | Model methods, business logic, serializers | `{module}/tests/test_models.py` |
| API (BE) | pytest + DRF test client | Endpoints, status codes, permissions | `{module}/tests/test_views.py` |
| Integration (BE) | pytest | Cross-module workflows (invoice → accounting) | `{module}/tests/test_integration.py` |
| Component (FE) | vitest + testing-library | Component rendering, user interaction | `Component.test.tsx` |
| Hook (FE) | vitest | Custom hook behavior | `useHook.test.ts` |

### TDD Workflow (Per Slice)
1. **RED:** Write failing tests for the slice's acceptance criteria
2. **GREEN:** Implement minimum code to pass tests
3. **REFACTOR:** Clean up while tests stay green
4. **VERIFY:** Run full suite, check coverage

### Test Patterns

```python
# Backend: Use factories, test isolation, company scoping
@pytest.fixture
def company():
    return CompanyFactory(name="NovaPay", industry="fintech")

@pytest.fixture
def other_company():
    return CompanyFactory(name="MedVista", industry="healthcare")

@pytest.fixture
def api_client(company):
    user = UserFactory(company=company)
    client = APIClient()
    client.force_authenticate(user=user)
    return client

class TestCompanyIsolation:
    def test_cannot_see_other_company_data(self, api_client, company, other_company):
        ProductFactory(company=company, name="Widget")
        ProductFactory(company=other_company, name="Secret Widget")
        response = api_client.get("/api/v1/inventory/products/")
        names = [p["name"] for p in response.data["results"]]
        assert "Widget" in names
        assert "Secret Widget" not in names
```

## Boundaries

### Always Do
- Run `make test` before commits
- Filter all queries by `company_id` (multi-tenancy)
- Use parameterized queries (Django ORM handles this)
- Validate inputs at API boundary (DRF serializers)
- Write tests BEFORE implementation (TDD)
- Use conventional commit messages (feat:/fix:/test:/refactor:/docs:/chore:)
- Soft delete (set `deleted_at`, never hard delete)
- Log audit trail on model changes
- Use industry config for labels (never hardcode terminology)

### Ask First
- Database schema changes that affect existing data
- Adding new Python/npm dependencies
- Changing Docker Compose service configuration
- Modifying the RBAC permission model
- Adding new API endpoints outside the standard ViewSet pattern
- Changing the materialized view refresh schedule

### Never Do
- Commit secrets (.env, API keys, passwords)
- Hard delete records (use soft delete)
- Skip tests ("I'll add them later")
- Use `any` type in TypeScript
- Write raw SQL outside of migrations and materialized views
- Modify core module code from industry-specific agents
- Bypass RBAC checks
- Store PII in logs or error messages

## 13 Module Specifications

### Module 1: Accounting

**Entities:** Currency, Account (CoA), Journal, FiscalYear, Move (JournalEntry), MoveLine, Payment, BankStatement, BankStatementLine, Tax

**Key Business Logic:**
- Double-entry enforcement: sum(debits) must equal sum(credits) per Move
- Move posting is irreversible (only cancel creates reverse entry)
- Payment reconciliation matches payments to move lines
- Bank reconciliation matches statement lines to move lines
- Fiscal year lock prevents modification of posted entries
- Tax computation on invoice lines (percent or fixed)

**API Endpoints:**
- `GET/POST /api/v1/accounting/accounts/` — Chart of Accounts (tree)
- `GET/POST /api/v1/accounting/journals/`
- `GET/POST /api/v1/accounting/moves/` + `POST .../post/` + `POST .../cancel/`
- `GET/POST /api/v1/accounting/payments/` + `POST .../reconcile/`
- `GET/POST /api/v1/accounting/bank-statements/` + `POST .../reconcile/`

**Views:** List (all entities), Form (all entities), Tree (CoA)

---

### Module 2: Invoicing

**Entities:** Invoice, InvoiceLine, CreditNote, PaymentTerms, RecurringInvoice

**Key Business Logic:**
- Invoice posting creates corresponding Accounting.Move (debit receivable, credit revenue)
- Credit notes create reverse accounting entries
- Recurring invoices auto-generate via Celery Beat
- Payment terms calculate due dates
- Invoice types: out_invoice (customer), in_invoice (vendor), out_refund, in_refund

**API:** `/api/v1/invoicing/invoices/` + post/send actions, `/api/v1/invoicing/credit-notes/`, `/api/v1/invoicing/payment-terms/`

---

### Module 3: Inventory

**Entities:** ProductCategory, UnitOfMeasure, Product, StockLocation (tree), StockMove (state machine), StockLot, ReorderRule, InventoryAdjustment, InventoryAdjustmentLine

**Key Business Logic:**
- Stock levels computed from sum of confirmed StockMoves (not stored field)
- StockMove state machine: draft → assigned → confirmed → done → cancelled
- Lot tracking with serial numbers and expiry dates
- Reorder rules trigger notifications when stock drops below minimum
- Location hierarchy: warehouse → zone → bin

**API:** `/api/v1/inventory/products/` + stock_level endpoint, `/api/v1/inventory/stock-moves/` + confirm/done actions, `/api/v1/inventory/stock-locations/` (tree)

---

### Module 4: Fleet

**Entities:** VehicleCategory, Vehicle, MaintenanceSchedule, MaintenanceRecord, FuelLog, DriverAssignment (→HR.Employee), InsurancePolicy

**Key Business Logic:**
- Driver assignments link to HR.Employee records
- Maintenance schedule tracking with due date/mileage alerts
- Fuel log with cost-per-mile calculations
- Insurance policy expiry alerts

**API:** `/api/v1/fleet/vehicles/` + maintenance_history/fuel_history, `/api/v1/fleet/maintenance/`, `/api/v1/fleet/fuel-logs/`

---

### Module 5: Calendar

**Entities:** CalendarEvent, EventAttendee, Resource, ResourceAvailability, Reminder

**Key Business Logic:**
- Date range queries (events between start and end)
- Resource booking with availability conflict detection (no double-booking)
- Recurrence rules (RRULE format in JSONB)
- Attendee invitation with status tracking (pending/accepted/declined)
- Calendar sync stub endpoint for CRM integration

**API:** `/api/v1/calendar/events/?start=&end=`, `/api/v1/calendar/resources/` + availability

---

### Module 6: HR

**Entities:** Department (tree), JobPosition, Employee, EmploymentContract, LeaveType, LeaveRequest (state machine), AttendanceRecord, Timesheet

**Key Business Logic:**
- Leave request state machine: draft → submitted → approved/rejected
- Approval requires manager-level permission
- Timesheet entry with weekly grid, billable flag
- Department hierarchy (tree)
- Employee linked to Django User (nullable for non-system employees)

**API:** `/api/v1/hr/employees/`, `/api/v1/hr/leave-requests/` + approve/reject, `/api/v1/hr/timesheets/`, `/api/v1/hr/departments/`

---

### Module 7: Projects

**Entities:** Project, ProjectPhase, Task (kanban), Milestone, TaskDependency, ProjectTimesheet

**Key Business Logic:**
- Task kanban with state machine: todo → in_progress → review → done
- Task dependencies (finish-to-start, start-to-start)
- Milestone tracking with completion status
- Budget vs. actual hours from timesheets
- Billable timesheet entries

**API:** `/api/v1/projects/projects/` + tasks/milestones/timesheets/budget_summary, `/api/v1/projects/tasks/`

---

### Module 8: Purchasing

**Entities:** PurchaseOrder (sequence), PurchaseOrderLine, RequestForQuote, PurchaseAgreement, ReceiptRecord, ReceiptLine

**Key Business Logic:**
- PO lifecycle: draft → confirm (generates sequence) → receive → done
- Confirming PO creates pending StockMoves in Inventory
- Receiving creates done StockMoves and updates stock levels
- RFQ workflow: create → send → record response
- Vendor performance tracking

**API:** `/api/v1/purchasing/orders/` + confirm/receive, `/api/v1/purchasing/vendors/`, `/api/v1/purchasing/rfqs/`

**Integration:** Purchasing → Inventory (stock moves on receive)

---

### Module 9: Sales

**Entities:** Pricelist, PricelistItem, Quotation (sequence), QuotationLine, SalesOrder (sequence), SalesOrderLine, SalesCommission

**Key Business Logic:**
- Quotation lifecycle: draft → send → confirm (creates SalesOrder)
- Sales order lifecycle: confirmed → delivered (creates outbound StockMoves) → done
- Pricelist engine: computes price based on customer, quantity, date
- Commission tracking per salesperson

**API:** `/api/v1/sales/quotations/` + confirm, `/api/v1/sales/orders/` + deliver, `/api/v1/sales/pricelists/` + price endpoint

**Integration:** Sales → Inventory (stock moves on deliver), Sales → Accounting (via Invoicing)

**Note:** Uses unified Partner model instead of separate Customer/Vendor (see DECISION.md D17).

---

### Module 10: Manufacturing

**Entities:** WorkCenter, BillOfMaterials, BOMLine, Routing, RoutingStep, ManufacturingOrder (sequence), WorkOrder, ProductionCost

**Key Business Logic:**
- BOM defines components needed to produce a finished product
- MO start consumes component stock (creates inbound StockMoves)
- MO complete adds finished product to stock
- Work order tracking per routing step per work center
- Production cost tracking (material, labor, overhead)

**API:** `/api/v1/manufacturing/boms/` + cost_estimate, `/api/v1/manufacturing/orders/` + confirm/start/complete, `/api/v1/manufacturing/work-orders/`

**Integration:** Manufacturing → Inventory (consume components, add finished product)

---

### Module 11: Point of Sale

**Entities:** POSStation, PaymentMethod, POSSession, POSOrder, POSOrderLine, POSPayment, CashMovement, ReceiptTemplate

**Key Business Logic:**
- Session management: open (with cash count) → close (with count, compute difference)
- Touch-optimized order entry (distinct UI from FormView)
- Multi-payment support (split cash + card)
- Order creates StockMoves (inventory deduction) + Accounting.Move (revenue)
- Receipt generation

**API:** `/api/v1/pos/sessions/` + open/close, `/api/v1/pos/orders/` (single POST with lines + payment)

**Integration:** POS → Inventory → Accounting

---

### Module 12: Helpdesk

**Entities:** TicketCategory, SLAConfig, Ticket (state machine), TicketComment, KnowledgeArticle

**Key Business Logic:**
- Ticket lifecycle: new → assigned → in_progress → resolved → closed
- SLA tracking with auto-calculated deadlines based on category config
- SLA breach detection via Celery task
- Internal notes vs. customer replies
- Knowledge base with search

**API:** `/api/v1/helpdesk/tickets/` + assign/resolve/close, `/api/v1/helpdesk/knowledge/`

---

### Module 13: Reports / BI

**Entities:** ReportTemplate, ReportDefinition, PivotDefinition, GraphDefinition, ScheduledReport, ExportJob

**Key Business Logic:**
- Custom report builder (select model, fields, filters, grouping)
- Pre-built templates: P&L, Balance Sheet, Aging Analysis, Inventory Turnover
- Export to PDF, Excel, CSV (async via Celery)
- Scheduled reports (daily/weekly/monthly, auto-email)
- Pivot tables with drill-down
- Graph views (bar, line, pie, area)

**API:** `/api/v1/reports/definitions/` + execute, `/api/v1/reports/exports/` + download, `/api/v1/reports/pivot/`, `/api/v1/reports/graph/`

---

## 10 Industry Configurations

### Industry Matrix

| # | Company | Industry | Brand Color | Ports (FE/API) | Reference Modules |
|---|---------|----------|-------------|----------------|-------------------|
| 1 | NovaPay | FinTech | #2563EB | 14001/14101 | Accounting, Reports |
| 2 | MedVista | Healthcare | #059669 | 14002/14102 | Calendar, HR |
| 3 | TrustGuard | Insurance | #1E3A5F | 14003/14103 | Sales |
| 4 | UrbanNest | Real Estate | #D97706 | 14004/14104 | Sales, Calendar |
| 5 | SwiftRoute | Logistics | #7C3AED | 14005/14105 | Fleet, WebSocket |
| 6 | DentaFlow | Dental | #06B6D4 | 14006/14106 | Config, Calendar |
| 7 | JurisPath | Legal | #166534 | 14007/14107 | Invoicing, Projects |
| 8 | TableSync | Restaurant | #9F1239 | 14008/14108 | Inventory, Manufacturing, POS |
| 9 | CraneStack | Construction | #EA580C | 14009/14109 | Views, HR, Projects |
| 10 | EduPulse | Education | #6D28D9 | 14010/14110 | Calendar, Sales |

### Terminology Examples (per industry)

| Generic Term | NovaPay | MedVista | DentaFlow | TableSync | CraneStack |
|-------------|---------|----------|-----------|-----------|------------|
| Customer | Merchant | Patient | Patient | Guest | Client |
| Product | Service Plan | Treatment | Procedure | Menu Item | Material |
| Invoice | Settlement Statement | Patient Bill | Treatment Invoice | Guest Check | Progress Bill |
| Warehouse | — | Supply Room | Supply Room | Kitchen/Pantry | Laydown Yard |
| Employee | — | Provider | Practitioner | Staff | Crew Member |
| Project | — | Treatment Plan | Treatment Plan | Event | Job Site |

---

## Role System (80 Industry-Specific Roles)

### Architecture

**5 Role Levels:**
- L1 Operational — Day-to-day tasks, own records only
- L2 Supervisor — Team oversight, department scope
- L3 Manager — Department authority, full CRUD in owned modules
- L4 Director — Cross-department visibility, budget approval
- L5 Executive — Full company access, financials, settings

**Permission Model (3 layers):**
1. **Module-level:** Does role have `access: true` for this module? (middleware check)
2. **Action-level:** Which CRUD+custom actions allowed? (DRF permission check)
3. **Entity-scope:** Which records visible? company/department/own_record/assigned (QuerySet filter)

**Implementation:** IndustryRoleTemplate model stores templates per industry. On company creation, templates are copied to company-specific Role records with expanded Permission FK rows.

### Role Summary (8 per industry)

**NovaPay (FinTech):** CEO, CFO, Chief Risk Officer, VP Sales, Compliance Officer, Account Manager, Risk Analyst, Support Agent

**MedVista (Healthcare):** CEO, Chief Medical Officer, CFO, Clinic Director, Department Chief, Physician, Nurse, Billing Specialist

**TrustGuard (Insurance):** CEO, Chief Actuary, Chief Claims Officer, VP Underwriting, Regional Manager, Claims Adjuster, Underwriter, Agent

**UrbanNest (Real Estate):** CEO, COO, Broker, Transaction Coordinator, Marketing Manager, Listing Agent, Buyer Agent, Property Manager

**SwiftRoute (Logistics):** CEO, COO, Regional Manager, Dispatch Manager, Warehouse Manager, Driver, Customer Success, Fleet Coordinator

**DentaFlow (Dental):** Practice Owner, Practice Manager, Clinical Director, Dentist, Hygienist, Insurance Coordinator, Receptionist, Dental Assistant

**JurisPath (Legal):** Managing Partner, Senior Partner, Associate, Of Counsel, Paralegal, Billing Coordinator, Office Manager, Legal Secretary

**TableSync (Restaurant):** Owner, General Manager, Head Chef, Sous Chef, FOH Manager, Bar Manager, Server, Line Cook

**CraneStack (Construction):** President, VP Construction, Project Manager, Superintendent, Estimator, Safety Officer, Procurement Manager, Equipment Operator

**EduPulse (Education):** Head of School, Academic Dean, CFO, Campus Director, Department Head, Teacher, Registrar, Admissions Director

---

## Data Architecture

### Materialized Views

| View Name | Source Modules | Purpose | Refresh |
|-----------|---------------|---------|---------|
| mv_monthly_revenue | Invoicing | Revenue trends per company | 60min |
| mv_ar_aging | Invoicing | Accounts receivable aging buckets | 60min |
| mv_inventory_stock_levels | Inventory | Current stock with reorder alerts | 60min |
| mv_employee_attendance | HR | Attendance summary by department | 60min |
| mv_helpdesk_sla | Helpdesk | SLA compliance per category | 60min |
| mv_delivery_performance | Inventory (SwiftRoute) | On-time delivery percentage | 60min |
| mv_food_cost_analysis | Manufacturing (TableSync) | Recipe cost vs. menu price | 60min |
| mv_billable_hours | HR (JurisPath) | Attorney utilization rates | 60min |

### Anomaly Detection

Celery task runs every 15 minutes. Anomaly rules defined in JSONB on role templates.

**Key anomalies per industry:**
- NovaPay: Chargeback rate >1.5%, Fraud score >80
- MedVista: No-show rate >15%, Incomplete charts >48hrs
- TrustGuard: Loss ratio >70%, Reserve shortfall
- UrbanNest: Listing >60 days without offer, Transaction stuck >45 days
- SwiftRoute: On-time rate <97%, Unassigned shipments >10
- DentaFlow: Collection rate <90%, Unfilled slots >20%
- JurisPath: Realization rate <85%, Unbilled WIP >$50K
- TableSync: Food cost >32%, Labor >30% of revenue
- CraneStack: OSHA incident, Project >10% over budget
- EduPulse: Enrollment decline >3%, Tuition delinquency >60 days

---

## API Contracts

### Standard Response Format

```json
{
  "count": 42,
  "next": "/api/v1/inventory/products/?cursor=abc123",
  "previous": null,
  "results": [
    {
      "id": 1,
      "company_id": 1,
      "name": "Widget",
      "created_at": "2026-04-11T10:00:00Z",
      "updated_at": "2026-04-11T10:00:00Z"
    }
  ]
}
```

### Error Response Format

```json
{
  "detail": "You do not have permission to perform this action.",
  "code": "permission_denied"
}
```

### Authentication

```
POST /api/v1/auth/login/
  Body: {"email": "user@novapay.com", "password": "demo123"}
  Response: {"access": "eyJ...", "refresh": "eyJ...", "user": {...}, "company": {...}}

POST /api/v1/auth/refresh/
  Body: {"refresh": "eyJ..."}
  Response: {"access": "eyJ..."}
```

---

## Vertical Slice Definitions

See the approved plan at `.claude/plans/precious-tickling-comet.md` for complete slice definitions including:
- 19 slices with dependency ordering
- What gets built per slice (models, APIs, frontend, tests)
- Definition of Done per slice
- Reference industry per slice
- Suggested build prompts per slice

---

## Success Criteria

1. `docker-compose up --build` starts all 6 services on Apple Silicon Mac
2. Login as admin@novapay.com → see NovaPay-branded dashboard with correct KPIs
3. Login as admin@dentaflow.com → see DentaFlow-branded dashboard with different KPIs
4. All 13 modules accessible from App Switcher
5. CRUD operations work for all module entities via Form and List views
6. Kanban drag-drop updates entity state
7. Company A's data never visible when logged into Company B
8. Role-based access: user without module permission gets 403
9. Sequence system generates INV/2026/00001 format IDs
10. Invoice posting creates corresponding accounting journal entry
11. PO receiving creates inventory stock moves
12. `make test` passes with 80%+ coverage on both backend and frontend
13. `make seed` populates all 10 industries with demo data

## Open Questions

None — all design decisions documented in DECISION.md. If implementation reveals new constraints, decisions will be updated.
