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
| Charting | Recharts (locked by D24) | latest |

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

### Shipped — Slices 0–10 (frozen reference)

As of 2026-04-16, 628 tests passing (418 backend + 210 frontend). Each was shipped in one atomic commit with all backend + frontend + tests + migrations.

| # | Module / Focus | Commit | Tests |
|---|----------------|--------|-------|
| 0 | Docker + project scaffold | `3fe3cfc` | 7 |
| 1 | Core multi-tenancy + auth + RBAC + layout | `4724a21` | 101 |
| 2 | View system (List/Form/Kanban) + component library | `ce125c3` / `8580dde` | 77 |
| 3 | Industry config (YAML → 3-tier merge → Redis cache) | `f497ca2` | 73 |
| 4 | HR — Employee, Department, LeaveRequest, Payroll | `0d6653c` | 68 |
| 5 | Calendar — Event, Resource, Attendee, Reminder, `external_uid` | `1200726` | 45 |
| 6 | Inventory — Product, StockLocation, StockMove, StockLot, ReorderRule | `569057f` | 70 |
| 7 | Purchasing — Vendor, PO, POLine, RFQ, RFQLine | `b71c0a8` | 63 |
| 8 | Sales — Quotation, SalesOrder, SalesOrderLine | `1623619` | 51 |
| 9 | Accounting — Account, Journal, JournalEntry, JournalEntryLine | `62343d6` | 59 |
| 10 | Invoicing — Invoice, InvoiceLine, CreditNote | `e1b424d` | 45 |

**Frozen:** These slices will not be modified except by the three tech-debt slices below (10.5/10.6/10.7) and by Slice 19 (polish pass).

### Remaining Tech-Debt Slices (10.5 → 10.6 → 10.7, see D31/D32)

#### Slice 10.5 — Tech-debt cleanup (UI consistency)
**Scope:**
- Commit the pending modified `frontend/src/pages/invoicing/InvoiceFormPage.test.tsx`.
- Add `frontend/src/pages/sales/QuotationFormPage.tsx` + register `/sales/quotations/new` and `/sales/quotations/:id/edit` in `App.tsx`. Its test must follow the "form page test structure" memory (`fireEvent`, `api/config` mock, `configStore.setState` beforeEach).
- Retrofit `useTerminology()` into the 11 pages currently missing it: `sales/QuotationListPage`, `sales/SalesOrderListPage`, `sales/SalesOrderFormPage`, `purchasing/VendorListPage`, `purchasing/VendorFormPage`, `purchasing/PurchaseOrderListPage`, `purchasing/PurchaseOrderFormPage`, `accounting/AccountListPage`, `accounting/JournalEntryListPage`, `accounting/JournalEntryFormPage`, `invoicing/InvoiceListPage`, `invoicing/InvoiceFormPage`.

**Acceptance:**
- New QuotationFormPage tests pass (create + edit paths).
- All 23 module pages call `useTerminology()` for user-visible labels.
- `make test` green; Preview-tab sweep shows TableSync and DentaFlow terminology swaps across all 7 modules' list headers.

**Commit:** `refactor: Slice 10.5 — Quotation form, terminology retrofit`

---

#### Slice 10.6 — Partner model
**Scope:** (see D21)
- Add `core.Partner(TenantModel)` with: `name`, `email`, `phone`, `is_customer`, `is_vendor`, `tax_id`, `payment_terms_days`, `credit_limit`, `industry_tags` (JSONB), `address_json`.
- Add `PartnerFactory`, model tests, `PartnerViewSet` with `IsCompanyMember` + `CompanyScopedFilterBackend` + `pagination_class = None`, API tests, serializer, register under `/api/v1/core/partners/`.
- Frontend: `api/partners.ts`, `PartnerListPage`, `PartnerFormPage`, routes.
- **Migrate existing FKs:** add nullable `customer = FK(Partner)` to SalesQuotation, SalesOrder, Invoice; add nullable `partner = FK(Partner)` to PurchaseOrder (alongside legacy `vendor` FK — mark vendor deprecated). Data migration: for each row with `customer_name` set, upsert a Partner (`is_customer=True` and/or `is_vendor=True`) in the same company and set the FK. Leave `customer_name` populated as denormalized display fallback.

**Acceptance:**
- `/api/v1/core/partners/` CRUD works, company-scoped.
- Creating a SalesOrder via API lets caller pass either `customer_name` (legacy) or `customer_id` (new); when `customer_id` is passed, `customer_name` is auto-populated from `partner.name`.
- Data migration reversible; downgrade leaves strings intact.
- `make test` green; Preview sweep creates a Partner, then creates a Quotation referencing that Partner, sees the name render in the list.

**Commit:** `feat: Slice 10.6 — Partner model unifies customers and vendors`

---

#### Slice 10.7 — Sequence auto-generation signals
**Scope:** (see D22)
- For each numbered entity, override `save()` to call `core.sequence.get_next_sequence(self.company, prefix)` when the number field is blank. Entities + prefixes:

| Model | Field | Prefix |
|-------|-------|--------|
| `invoicing.Invoice` | `invoice_number` | `INV` |
| `invoicing.CreditNote` | `credit_note_number` | `CN` |
| `purchasing.PurchaseOrder` | `po_number` | `PO` |
| `purchasing.RequestForQuote` | `rfq_number` | `RFQ` |
| `sales.SalesQuotation` | `quotation_number` | `QUO` |
| `sales.SalesOrder` | `order_number` | `SO` |
| `accounting.JournalEntry` | `reference` | `JE` |

- Format: `{PREFIX}-{YYYY}-{NNNN}` (e.g., `INV-2026-0001`).
- New unit tests per model asserting (a) blank → auto-generated, (b) pre-set → preserved, (c) concurrent saves across two companies don't collide.

**Acceptance:**
- Creating any of the above entities via API with no number field returns the entity with a sequence-formatted number.
- Existing rows with blank numbers get back-filled by a one-off migration.
- `make test` green; Preview sweep creates a new Invoice, sees `INV-2026-…` in the list.

**Commit:** `feat: Slice 10.7 — sequence auto-generation signals`

---

#### Slice 10.8 — Design system & visual layer (inserted 2026-04-16)
**Scope:** (see D33, D34, D35) — ship tokens + globals + Lucide icons + per-company `--accent` CSS variable theming. The frontend currently has **zero CSS files**; this slice adds `frontend/src/styles/tokens.css`, `frontend/src/styles/globals.css`, styled shared components (`Button`, `Input`, `Select`, `Modal`, `Badge`), styled AppLayout/TopNavbar/Sidebar/AppSwitcher, redesigned LoginPage, and per-company theming driven by `Company.brand_color`.

**Entities touched:** No new DB models. Pure frontend + a single `lucide-react` npm dep.

**Acceptance:**
- `frontend/src/styles/tokens.css` + `globals.css` imported from `main.tsx`.
- All existing 229 frontend tests still pass; ~3 new tests added for Lucide icons, `--accent` theming, and WCAG AA contrast.
- Preview sweep as `admin@tablesync.com` and `admin@novapay.com` shows visibly different brand colors (burgundy vs blue) in the topnav strip and primary buttons.
- Zero emoji icons remain in structural UI.
- Zero console errors.

**Commit:** `feat: Slice 10.8 — design system, Lucide icons, per-company theming`

---

### Remaining Module Slices (11–16)

Each of these uses the 9-step Module Scaffold Pattern (memory `feedback_module_scaffold`, locked by D28). Each slice must satisfy the Verification Gate (below) before commit. All three new tech-debt slices must ship before Slice 11.

#### Slice 11 — Fleet
**Entities:** `Vehicle` (make, model, year, license_plate, VIN, status: active/maintenance/retired, `driver = FK(Driver, null=True)`, mileage), `Driver` (name, license_number, license_expiry, phone, status: active/inactive, optional `employee = FK(hr.Employee)`), `MaintenanceLog` (vehicle FK, date, description, cost, mechanic, status: scheduled/completed/cancelled), `FuelLog` (vehicle FK, date, liters, cost_per_liter, total_cost, mileage_at_fill), `VehicleService` (vehicle FK, service_type, scheduled_date, completed_date, cost, notes).

**API:** `/api/v1/fleet/{vehicles,drivers,maintenance-logs,fuel-logs,services}/`. Filters: Vehicle by status + driver; MaintenanceLog by status + vehicle; FuelLog by vehicle.

**Frontend:** VehicleListPage + VehicleFormPage, DriverListPage + DriverFormPage, MaintenanceLogListPage, FuelLogListPage.

**Reference industry:** SwiftRoute.

---

#### Slice 12 — Projects
**Entities:** `Project` (name, code, `customer = FK(core.Partner)`, start_date, end_date, status: planned/active/on_hold/completed/cancelled, budget), `Task` (project FK, name, assignee = FK(hr.Employee), status: todo/in_progress/review/done/cancelled, priority, due_date, parent_task self-FK for subtasks), `Milestone` (project FK, name, due_date, completed), `ProjectTimesheet` (project FK, employee FK, task FK null, date, hours, billable, description).

**API:** `/api/v1/projects/{projects,tasks,milestones,timesheets}/`. Include `@action GET /projects/{id}/progress/` returning `{total_tasks, done, hours_logged, budget_consumed_pct}`.

**Frontend:** ProjectListPage + ProjectFormPage, TaskListPage (with Kanban view option), MilestoneListPage. Task's KanbanView groups by status.

**Reference industry:** CraneStack.

---

#### Slice 13 — Manufacturing
**Entities:** `BillOfMaterials` (product FK to inventory.Product, version, active), `BOMLine` (bom FK, component FK to inventory.Product, quantity, uom), `WorkOrder` (product FK, quantity_target, quantity_done, status: draft/confirmed/in_progress/done/cancelled, start_date, end_date), `ProductionCost` (work_order FK, cost_type: material/labor/overhead, amount, notes).

**API:** `/api/v1/manufacturing/{boms,bom-lines,work-orders,costs}/`. Include `@action POST /work-orders/{id}/start/` (status → in_progress), `/complete/` (status → done, creates inventory.StockMove entries for consumed components and finished product).

**Frontend:** BOMListPage + BOMFormPage (with child lines), WorkOrderListPage + WorkOrderFormPage.

**Reference industry:** TableSync (recipes as BOMs).

---

#### Slice 14 — Point of Sale
**Entities:** `POSSession` (station: CharField, cash_on_open, cash_on_close null, opened_by FK user, opened_at, closed_at null, status: open/closed), `POSOrder` (session FK, order_number auto-seq `POS`, customer FK(core.Partner) null, subtotal, tax_amount, total, status: draft/paid/refunded), `POSOrderLine` (order FK, product FK(inventory.Product), quantity, unit_price, tax_rate, total), `CashMovement` (session FK, type: in/out, amount, reason, at_time).

**API:** `/api/v1/pos/{sessions,orders,order-lines,cash-movements}/`. Include `@action POST /sessions/{id}/close/` computing expected vs. actual cash.

**Frontend:** POSSessionListPage + POSSessionFormPage, POSOrderListPage + POSOrderFormPage (touch-friendly).

**Reference industry:** TableSync (restaurant POS).

---

#### Slice 15 — Helpdesk
**Entities:** `TicketCategory` (name, sla_hours, industry_tag), `SLAConfig` (category FK, priority: low/normal/high/urgent, response_hours, resolution_hours), `Ticket` (ticket_number auto-seq `TKT`, title, description, category FK, reporter FK(core.Partner) or FK(auth.User), assignee FK(auth.User) null, priority, status: new/assigned/in_progress/resolved/closed, created_at, resolved_at null, sla_breached bool), `KnowledgeArticle` (title, slug, body Markdown, category, published bool, tags JSONB).

**API:** `/api/v1/helpdesk/{tickets,categories,sla-configs,articles}/`. Include `@action POST /tickets/{id}/resolve/` + `/tickets/{id}/reopen/`.

**Frontend:** TicketListPage + TicketFormPage (with KanbanView by status), CategoryListPage, ArticleListPage + ArticleFormPage.

**Reference industry:** MedVista (patient support) or NovaPay (merchant support).

---

#### Slice 16 — Reports / BI (with Pivot + Graph)
**Scope:** (see D23, D24)
- Backend models: `ReportTemplate` (name, model_name, default_filters JSONB, default_group_by JSONB, default_measures JSONB, industry_tag), `PivotDefinition` (name, model_name, rows JSONB, cols JSONB, measure, aggregator), `ScheduledExport` (report FK, cron, format: pdf/csv/xlsx, recipients JSONB, last_run null).
- Extend `ViewDefinition.view_type` to include `pivot` and `graph`.
- **Generic `/aggregate/` action** on every module ViewSet: `GET /<path>/aggregate/?group_by=<field>&measure=<field>&op=<sum|count|avg>&filter=<field>__<lookup>=<value>&...`. Returns `[{group: <value>, value: <number>}, …]`. Reuses `CompanyScopedFilterBackend`.
- **Frontend:** `frontend/src/views/PivotView.tsx` (grid with row/col pivot, renders from `ViewDefinition.config`). `frontend/src/views/GraphView.tsx` (Recharts: bar/line/pie/area, config-driven). ReportBuilderPage stitches these together.

**Acceptance:**
- `/api/v1/invoicing/invoices/aggregate/?group_by=status&measure=total_amount&op=sum` returns per-status totals.
- Any `ViewDefinition` with `view_type=pivot` renders a functional pivot table for the configured model.
- Any `ViewDefinition` with `view_type=graph` renders a Recharts chart.
- Preview-tab sweep opens the Reports page, builds an invoice-by-month line chart, screenshots it.

**Reference industry:** NovaPay (financial reports), TableSync (food cost pivot).

---

### Platform Slices (17–19)

#### Slice 17 — Industry demo seeding (see D26)
Per-module `seed_<module>_demo --company <slug> [--reset]` commands for each of the 13 modules. Meta-command `seed_industry_demo --company <slug>` reads per-industry module subset from `INDUSTRY-BRANDING-CONTEXT.md` and dispatches. Idempotent. Adds 10–30 sample records per module per company.

**Acceptance:** `docker compose run --rm django python manage.py seed_industry_demo --company dentaflow` produces a browseable demo dataset across Calendar, Inventory, HR, Invoicing with DentaFlow terminology.

---

#### Slice 18 — Calendar polling sync (see D27)
**Endpoints:**
- `GET /api/v1/calendar/events/?updated_since=<iso8601>` — returns events updated after timestamp, includes `external_uid` and `updated_at`.
- `POST /api/v1/calendar/events/` — upsert by `external_uid`; LWW on `updated_at`.
- `POST /api/v1/calendar/events/bulk/` — accepts array for 5-min polling batches.

**Acceptance:** A separate client script can fetch, mutate, and push back events; conflict resolution verified via test that mutates on both sides and asserts LWW outcome.

---

#### Slice 19 — Polish pass
- `ErrorBoundary.tsx` wrapping all routes, `Skeleton.tsx` for list loading, `EmptyState.tsx` for empty tables, `Breadcrumbs.tsx` derived from router.
- Per-company theming: CSS custom properties from `Company.brand_color` (accent + accent-fg + accent-hover) applied at AppLayout mount.
- WebSocket notifications: Django Channels consumer on `/ws/notifications/`, frontend `useNotifications` hook + bell badge. Triggers: new Ticket, new Invoice, StockMove done.
- Audit log timeline page at `/settings/audit-log`.
- Lightweight HomePage with 4–6 ORM-aggregate KPIs per active industry (no materialized views — see D25).

**Acceptance:** `make test` green + manual Preview sweep of all 10 industry admin logins shows correct brand color, 13 modules visible, no console errors, notification bell works.

---

### Verification Gate (non-negotiable for every slice)

Before committing any slice:
1. `docker compose run --rm django python -m pytest --tb=short -q` — all green (including new tests).
2. `docker compose run --rm react npx vitest run --reporter=verbose` — all green.
3. **Preview tab sweep** (`mcp__Claude_Preview__*` tools):
   - `preview_start http://localhost:14500`
   - Log in as the slice's reference-industry admin
   - Navigate to each new page; `preview_screenshot`, `preview_console_logs`, `preview_network`
   - Zero console errors; zero 4xx/5xx; data renders correctly; terminology override visible
4. `git log -1 --format="%an %ae"` shows `Armando Gonzalez <armandogon94@gmail.com>`, no Co-Authored-By.
5. One atomic commit per slice with conventional-commit prefix.

---

## Success Criteria

**Cycle-level (what must be true when Slices 10.5–19 all ship):**

1. `make clean && make dev` starts all 6 services on Apple Silicon Mac in under 3 minutes.
2. `make migrate && make seed && docker compose run --rm django python manage.py seed_industry_demo --company dentaflow` produces a browseable demo.
3. Logging in as `admin@<company>.com / admin` for each of the 10 industries loads that company's brand color in the navbar, its 13-module AppSwitcher, and its terminology overrides (e.g., DentaFlow sidebar says "Supply Room" not "Warehouse").
4. Every one of the 13 modules has a List page, Form page (for primary entities), and at least one Kanban/Pivot/Graph view where useful.
5. Creating any numbered entity via API with a blank number returns a sequence-formatted number (`INV-2026-0001`, `PO-2026-0001`, etc.).
6. Sales/Invoicing/Purchasing/Projects/POS/Helpdesk all reference `core.Partner` (customer or vendor), not ad-hoc string columns.
7. Reports module renders at least one functional pivot and one functional Recharts graph over real seeded data.
8. Calendar sync: two separate processes polling `?updated_since` end up eventually-consistent with LWW.
9. Company A's data never visible to Company B (tested by cross-company assertions in every module's test suite).
10. Role-based access: a user without a given module's `access: true` receives 403 from that module's list endpoint.
11. `make test` passes with ≥80% coverage on both backend and frontend.
12. No Co-Authored-By trailer in any commit since `e1b424d`.

## Open Questions

None — all design decisions documented in DECISION.md (D1–D32). If implementation reveals new constraints, decisions will be appended with rationale.
