# ERP Master Plan — Project 14: Odoo-Inspired Multi-Industry Platform

**Version:** 1.0
**Last Updated:** 2026-04-02
**Status:** Master Plan (Pre-Development)
**Project ID:** 14-ERP-Platform
**Core Agent:** ERP Core Platform
**Industry Agents:** 10 (NovaPay, MedVista, TrustGuard, UrbanNest, SwiftRoute, DentaFlow, JurisPath, TableSync, CraneStack, EduPulse)

---

## 1. EXECUTIVE SUMMARY

Project 14 is a comprehensive, multi-tenant ERP (Enterprise Resource Planning) platform inspired by Odoo's modular architecture and UI consistency. The platform serves 10 distinct industries, each with their own customized workflows, terminology, and business logic, while sharing a unified core platform and consistent visual design.

**Key Objectives:**
- Build a flexible, modular ERP system where 13 core modules (Accounting, Invoicing, Inventory, Fleet, Calendar, HR, Projects, Purchasing, Sales, Manufacturing, POS, Helpdesk, Reports/BI) adapt to industry-specific needs
- Implement an industry-agnostic core with an extensible configuration system that allows domain-specific adaptations without code duplication
- Deliver rich demo data (50-100 records per entity) for 10 industries with realistic workflows
- Deploy locally via Docker Compose for development and demonstration
- Create a scalable agent architecture: 1 core platform agent + 10 industry agents, each maintaining domain expertise

**Core Tech Stack:**
- Frontend: React 18 + TypeScript + Vite
- Backend: Django 5.x + Django REST Framework 3.15+
- Database: PostgreSQL 15+
- Message Queue: Celery 5.x + Redis
- Real-time: Django Channels (WebSocket)
- Deployment: Docker Compose (local dev)

**Design Language:**
- Odoo-inspired UI: purple/white base theme (purple: #7C3AED)
- Company brand color accent in top navigation bar and sidebar (color varies per industry)
- Consistent layout: top navbar, left sidebar, main content area
- Responsive design; mobile-friendly forms and lists

---

## 2. INDUSTRY PORTFOLIO

### 2.1 Industry Definitions & Brand Colors

| # | Company Name | Sector | Brand Color | Port | Focus Areas |
|---|---|---|---|---|---|
| 1 | **NovaPay** | FinTech | #2563EB (Blue) | 14001/14101 | Payment processing, merchant fees, multi-currency accounting |
| 2 | **MedVista** | Healthcare | #059669 (Green) | 14002/14102 | Patient records, insurance reimbursement, ambulance fleet, lab orders |
| 3 | **TrustGuard** | Insurance | #1E3A5F (Navy) | 14003/14103 | Policy sales pipeline, claims processing, SLA tracking |
| 4 | **UrbanNest** | Real Estate | #D97706 (Amber) | 14004/14104 | Property sales pipeline, lease agreements, tenant management |
| 5 | **SwiftRoute** | Logistics | #7C3AED (Purple) | 14005/14105 | Delivery fleet, route optimization, driver management, fuel tracking |
| 6 | **DentaFlow** | Dental Clinic | #06B6D4 (Cyan) | 14006/14106 | Patient appointments, insurance co-pay billing, lab orders, equipment management |
| 7 | **JurisPath** | Legal Firm | #166534 (Forest Green) | 14007/14107 | Legal cases as projects, hourly billing, retainers, court date scheduling |
| 8 | **TableSync** | Restaurant/Hospitality | #9F1239 (Burgundy) | 14008/14108 | POS, kitchen production (recipes as BoM), split billing, staff shifts, tips |
| 9 | **CraneStack** | Construction | #EA580C (Safety Orange) | 14009/14109 | Construction projects, material purchasing, site equipment, heavy fleet, cost accounting |
| 10 | **EduPulse** | Education | #6D28D9 (Indigo) | 14010/14110 | Class schedules, semester planning, student records, campus bookstore POS |

### 2.2 Port Allocation (14xxx Range)

```
Core Platform:
  ERP Core API (Django):           14000
  ERP Core Frontend (React):       14500 (development proxy)

Industry Frontends:
  NovaPay Frontend:                14001
  MedVista Frontend:               14002
  TrustGuard Frontend:             14003
  UrbanNest Frontend:              14004
  SwiftRoute Frontend:             14005
  DentaFlow Frontend:              14006
  JurisPath Frontend:              14007
  TableSync Frontend:              14008
  CraneStack Frontend:             14009
  EduPulse Frontend:               14010

Industry API Instances (Optional for high-scale):
  NovaPay API:                     14101
  MedVista API:                    14102
  TrustGuard API:                  14103
  UrbanNest API:                   14104
  SwiftRoute API:                  14105
  DentaFlow API:                   14106
  JurisPath API:                   14107
  TableSync API:                   14108
  CraneStack API:                  14109
  EduPulse API:                    14110

Supporting Services:
  PostgreSQL:                      5432
  Redis:                           6379
```

---

## 3. MODULE SYSTEM ARCHITECTURE

The ERP platform is built around 13 core modules that are installed into every industry instance. Each module is industry-agnostic at the core, but supports industry-specific configuration and terminology via the module configuration system.

### 3.1 Module Definitions

#### **Module 1: Accounting**
**Purpose:** General ledger, chart of accounts, journal entries, bank reconciliation, financial reporting.

**Core Entities:**
- Chart of Accounts (COA) — organized by type (asset, liability, equity, revenue, expense)
- Journals — journal types (sales, purchase, bank, cash, general)
- Journal Entries (Moves & Move Lines) — double-entry accounting
- Payments — incoming/outgoing payments
- Bank Statements — bank reconciliation
- Taxes — tax definitions and rates
- Fiscal Years — period management

**Industry Adaptations:**
- **NovaPay**: Multi-currency support, merchant fee accounting (commission income as revenue), interchange tracking
- **MedVista**: Insurance reimbursement accounting (third-party payers), deductible tracking
- **CraneStack**: Project cost accounting (costs allocated to construction phases)
- **EduPulse**: Budget management (enrollment-driven revenue forecasting)

---

#### **Module 2: Invoicing/Billing**
**Purpose:** Customer invoices, vendor bills, payment tracking, credit notes, recurring invoices.

**Core Entities:**
- Invoice (customer invoices & vendor bills — unified model)
- Invoice Lines — line items with taxes
- Credit Notes — returns and adjustments
- Payment Terms — payment conditions (net 30, 2/10, etc.)
- Recurring Invoices — templates for automatic generation
- Payment Records — links invoices to payments

**Industry Adaptations:**
- **DentaFlow**: Insurance co-pay billing (split invoice: patient portion + insurance portion)
- **JurisPath**: Hourly billing (time entries drive line items), retainer management (monthly draws against retainer)
- **TableSync**: Split billing (multiple diners per check), tip tracking and distribution
- **UrbanNest**: Lease invoices (recurring, property-based)

---

#### **Module 3: Inventory/Warehouse**
**Purpose:** Products, stock locations, warehouse operations, lot/serial tracking, reorder rules.

**Core Entities:**
- Products — inventory items with SKU, UOM, reorder point
- Product Categories — hierarchical organization
- Stock Locations — warehouse zones, bins, physical locations
- Stock Moves — inventory transactions (receipt, delivery, internal transfer)
- Stock Lots — lot/batch tracking for expiry or traceability
- Reorder Rules — automatic purchase order triggers
- Inventory Adjustments — stock counts and discrepancies

**Industry Adaptations:**
- **DentaFlow**: Rename to "Supply Room" (dental supplies, materials)
- **TableSync**: Rename to "Pantry/Kitchen" (food inventory, ingredients)
- **CraneStack**: Rename to "Materials Yard" (construction materials, equipment)
- **MedVista**: Pharma tracking (controlled substances, lot expiry, NDC codes)

---

#### **Module 4: Fleet Management**
**Purpose:** Vehicles/equipment, maintenance schedules, fuel/cost tracking, driver assignments.

**Core Entities:**
- Fleet Vehicles — vehicle master (make, model, VIN, registration, insurance)
- Vehicle Categories — vehicle types (car, truck, van, motorcycle, equipment)
- Maintenance Schedules — preventive maintenance (oil change, inspections)
- Maintenance Records — performed maintenance, costs, technician
- Fuel/Expense Logs — fuel purchases, mileage, cost per mile
- Driver Assignments — assignments of drivers to vehicles
- Insurance Policies — vehicle insurance tracking

**Industry Adaptations:**
- **SwiftRoute**: Core delivery fleet; route optimization, driver efficiency metrics
- **CraneStack**: Heavy equipment (excavators, cranes, scaffolding); site equipment tracking
- **MedVista**: Ambulance fleet; emergency vehicle scheduling
- **DentaFlow**: Rename to "Equipment Management" (dental chairs, compressors, sterilizers)

---

#### **Module 5: Calendar/Scheduling**
**Purpose:** Appointments, resource booking, room/space reservations, shift planning, availability.

**Core Entities:**
- Calendar Events — appointments, meetings, bookings
- Event Types — categorization (appointment, meeting, event, shift)
- Resources — rooms, equipment, personnel available for booking
- Resource Availability — time slots, working hours, blackout dates
- Shift Templates — recurring shift patterns (nursing schedules, restaurant shifts)
- Attendees — people/resources linked to events
- Reminders — notification triggers

**Special Feature:** Support optional sync with Project 13 CRM calendar via **CalDAV-style REST API** (`POST /api/v1/calendar/sync/`, `GET /api/v1/calendar/events/`).

**Industry Adaptations:**
- **DentaFlow**: Patient appointments (appointment slots, chair availability, hygienist scheduling)
- **JurisPath**: Court dates (docket integration), client consultations, attorney availability
- **TableSync**: Table reservations (table capacity, time slots), staff shift planning
- **EduPulse**: Class schedules (room allocation, instructor assignment), semester planning
- **MedVista**: Ambulance shifts, patient appointment slots

---

#### **Module 6: HR/Employees**
**Purpose:** Employee records, departments, job positions, contracts, attendance, leave, payroll prep.

**Core Entities:**
- Employees — employee master (name, contact, start date, salary, manager)
- Departments — organizational hierarchy
- Job Positions — job titles with compensation bands
- Employment Contracts — contract type, start/end date, terms
- Attendance Records — clock in/out, daily attendance
- Leave Types — vacation, sick, unpaid, etc.
- Leave Requests — employee leave applications with approval workflow
- Payroll — salary structure, deductions, tax setup
- Timesheets — hours worked (feeds into Project Management and Invoicing)

**Industry Adaptations:**
- **All 10 industries** use HR, but terminology adjusts:
  - **DentaFlow**: "Dental Hygienists", "Lab Technicians" as job titles
  - **CraneStack**: "Site Foremen", "Heavy Equipment Operators", "Safety Officers" as job titles
  - **JurisPath**: "Senior Attorney", "Associate", "Paralegal" job hierarchy
  - **EduPulse**: "Faculty", "Adjunct", "Department Chairs", "Teaching Assistants"

---

#### **Module 7: Project Management**
**Purpose:** Projects, tasks, milestones, timesheets, Gantt charts, burndown tracking.

**Core Entities:**
- Projects — project master with budget, deadline, owner
- Project Phases — sub-projects or phases
- Tasks — work items with status, owner, deadline
- Milestones — key dates with deliverables
- Timesheets — time logged per task per employee (integrates with HR, Invoicing)
- Task Dependencies — predecessor/successor relationships
- Gantt Data — calculated timeline for visualization

**Industry Adaptations:**
- **CraneStack**: Construction projects with phases (foundation, framing, finishing), site management
- **JurisPath**: Legal cases as projects, client matters with time tracking for billing
- **EduPulse**: Semester planning as projects, course delivery with milestones (midterm, final)
- **UrbanNest**: Property development as projects
- **MedVista**: Clinical trial projects

---

#### **Module 8: Purchasing**
**Purpose:** Purchase orders, vendor management, RFQs, purchase agreements, receiving.

**Core Entities:**
- Vendors — supplier master (contact, terms, currency, payment method)
- Purchase Orders (POs) — purchase requisitions and orders
- RFQs — request for quotation with vendor responses
- Purchase Agreements — framework agreements for recurring purchases
- PO Lines — line items on purchase orders
- Receipt Records — goods received against PO
- Vendor Performance — tracking on-time delivery, quality, pricing

**Industry Adaptations:**
- **CraneStack**: Material purchasing (concrete, rebar, lumber, equipment rentals)
- **TableSync**: Food supply ordering (perishable, daily orders)
- **DentaFlow**: Dental supply ordering (amalgam, composite, instruments)
- **MedVista**: Pharmaceutical purchasing, medical device ordering
- **EduPulse**: Textbook and supplies purchasing

---

#### **Module 9: Sales**
**Purpose:** Quotations, sales orders, customer management, pipeline, pricelists, discounts.

**Core Entities:**
- Customers — customer master (contact, credit limit, territory, industry)
- Quotations — sales proposals with line items, expiry
- Sales Orders (SOs) — confirmed customer orders
- Pricelists — customer-specific or category-specific pricing
- Discounts — volume, temporal, customer-level discounts
- Sales Pipeline — opportunity tracking, funnel visibility
- Sales Commissions — commission structure per salesperson

**Industry Adaptations:**
- **NovaPay**: Merchant onboarding as "sales" (SMBs signing up for payment processing)
- **UrbanNest**: Property sales pipeline (listing, showing, offer, close)
- **TrustGuard**: Policy sales (quote → underwriting → issued policy)
- **JurisPath**: Engagement letters as quotations, case intake as sales
- **EduPulse**: Course registration as sales orders, tuition pricing

---

#### **Module 10: Manufacturing/Production**
**Purpose:** Bills of materials, manufacturing orders, work orders, work centers, routing.

**Core Entities:**
- Bills of Materials (BoMs) — ingredient/component lists with quantities
- Work Centers — production stations with capacity, cost per hour
- Routings — production steps with work center assignments
- Manufacturing Orders (MOs) — production runs with start/completion
- Work Orders — tasks within a manufacturing order
- BoM Versions — historical tracking of recipe changes
- Production Costs — actual vs. standard costs

**Industry Adaptations:**
- **TableSync**: "Kitchen Production" (recipes as BoMs, ingredients, cooking steps)
- **CraneStack**: "Construction Production" (material assembly on-site, equipment setup)
- **DentaFlow**: "Lab Orders" (dental lab fabrication — crowns, bridges, dentures as custom manufacturing)
- **MedVista**: Pharmaceutical compounding as manufacturing
- **EduPulse**: Course development/curriculum creation as "production"

---

#### **Module 11: Point of Sale (POS)**
**Purpose:** Touch-screen POS interface, order management, payment processing, receipt printing, cash management.

**Core Entities:**
- POS Stations — physical or virtual POS terminals
- POS Sessions — cash drawer operations, shift tracking
- POS Orders — transactions (linked to Sales Orders)
- POS Order Lines — items sold
- Payment Methods — cash, card, gift card, etc.
- Cash Drawer Operations — opening balance, cash-in, cash-out, close balance
- Receipt Templates — layout and content for printed/emailed receipts

**Industry Adaptations:**
- **TableSync**: Restaurant POS (multi-course orders, table management, split checks, tip handling)
- **DentaFlow**: Patient checkout (co-pay collection, insurance balance billing)
- **EduPulse**: Campus bookstore POS (textbooks, merchandise)
- **MedVista**: Pharmacy POS (prescription sales, insurance claims)

---

#### **Module 12: Helpdesk/Tickets**
**Purpose:** Support tickets, SLA tracking, customer portal, knowledge base, escalation.

**Core Entities:**
- Support Tickets — customer support requests
- Ticket Categories — categorization (billing, technical, complaint, feature request)
- Ticket Assignments — assignment to support agents
- SLA Policies — response time, resolution time targets
- Ticket Comments — internal notes and customer replies
- Knowledge Base Articles — self-service troubleshooting
- Customer Portal — self-service ticket submission and tracking

**Industry Adaptations:**
- **All 10 industries** use Helpdesk for internal or customer-facing support
- **NovaPay**: Merchant support (payment failures, reconciliation issues)
- **MedVista**: Patient support (appointment questions, billing inquiries)
- **JurisPath**: Client communication (case updates, document requests)

---

#### **Module 13: Reports/BI**
**Purpose:** Pivot tables, graph views, custom report builder, scheduled reports, export (PDF/Excel).

**Core Entities:**
- Report Definitions — saved reports with filters, grouping, aggregations
- Report Templates — pre-built templates per module (P&L, aging report, inventory turnover)
- Scheduled Reports — recurring report generation and email delivery
- Graph Definitions — chart configurations (bar, line, pie, area)
- Pivot Definitions — multi-dimensional analysis setup
- Export Jobs — scheduled exports to external systems

**Industry Adaptations:**
- **Each module** feeds data to BI; industry-specific report templates pre-loaded
- **Accounting**: P&L, Balance Sheet, Cash Flow, Tax Reports, Aging Analysis
- **Sales**: Pipeline Report, Win/Loss Analysis, Customer Lifetime Value
- **Inventory**: Turnover Analysis, Stockout Reports, Reorder Recommendations
- **HR**: Headcount by Department, Turnover Analysis, Compensation Analysis
- **Project**: Gantt Views, Budget vs. Actual, Burndown Charts

---

## 4. DATABASE SCHEMA — COMPREHENSIVE TABLE DEFINITIONS

### 4.1 Core Framework Tables

All tables include `created_at`, `updated_at`, and `deleted_at` (soft delete) timestamps for audit purposes. Primary keys are `id` (UUID or auto-increment). Foreign keys are indexed.

#### **companies**
```
Table: core_company
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  name                  VARCHAR(255) NOT NULL UNIQUE
  slug                  VARCHAR(255) NOT NULL UNIQUE (lowercase, kebab-case)
  brand_color           VARCHAR(7) NOT NULL (hex color, e.g., #2563EB)
  description           TEXT
  industry              VARCHAR(100) NOT NULL (enum: fintech, healthcare, insurance, real_estate, logistics, dental, legal, hospitality, construction, education)
  is_active             BOOLEAN DEFAULT TRUE
  subscription_tier     VARCHAR(50) DEFAULT 'standard' (free, starter, standard, enterprise)
  config_json           JSONB (industry-specific configuration)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  deleted_at            TIMESTAMP NULL
Indexes:
  idx_company_slug
  idx_company_industry
  idx_company_active
```

#### **users**
```
Table: auth_user (extended Django User)
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  username              VARCHAR(150) NOT NULL UNIQUE
  email                 VARCHAR(254) NOT NULL UNIQUE
  password_hash         VARCHAR(255) NOT NULL (bcrypt)
  first_name            VARCHAR(150)
  last_name             VARCHAR(150)
  is_staff              BOOLEAN DEFAULT FALSE
  is_superuser          BOOLEAN DEFAULT FALSE
  is_active             BOOLEAN DEFAULT TRUE
  date_joined           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  last_login            TIMESTAMP NULL
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(username)
  UNIQUE(email)
```

#### **user_profiles**
```
Table: core_user_profile
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  user_id               BIGINT NOT NULL FOREIGN KEY -> auth_user
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  phone                 VARCHAR(20)
  avatar_url            VARCHAR(500)
  department            VARCHAR(100)
  job_title             VARCHAR(100)
  timezone              VARCHAR(50) DEFAULT 'UTC'
  language              VARCHAR(10) DEFAULT 'en'
  preferences_json      JSONB (UI preferences, notification settings)
  is_company_admin      BOOLEAN DEFAULT FALSE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_user_profile_user_company (user_id, company_id)
  idx_user_profile_is_admin
```

#### **roles**
```
Table: core_role
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(100) NOT NULL
  description           TEXT
  is_system             BOOLEAN DEFAULT FALSE (system roles: Admin, User, Manager cannot be deleted)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, name)
  idx_role_company
```

#### **permissions**
```
Table: core_permission
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  codename              VARCHAR(100) NOT NULL UNIQUE
  name                  VARCHAR(255) NOT NULL
  description           TEXT
  module                VARCHAR(100) NOT NULL (e.g., 'accounting', 'invoicing')
  action                VARCHAR(50) NOT NULL (e.g., 'create', 'read', 'update', 'delete', 'approve')
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_permission_module_action
```

#### **role_permissions**
```
Table: core_role_permission
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  role_id               BIGINT NOT NULL FOREIGN KEY -> core_role
  permission_id         BIGINT NOT NULL FOREIGN KEY -> core_permission
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(role_id, permission_id)
  idx_role_permission_role
```

#### **user_roles**
```
Table: core_user_role
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  user_id               BIGINT NOT NULL FOREIGN KEY -> auth_user
  role_id               BIGINT NOT NULL FOREIGN KEY -> core_role
  assigned_at           TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  assigned_by_user_id   BIGINT FOREIGN KEY -> auth_user
Indexes:
  UNIQUE(user_id, role_id)
  idx_user_role_user
```

#### **modules** (Installed Module Registry)
```
Table: core_module
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(100) NOT NULL (e.g., 'accounting', 'invoicing')
  display_name          VARCHAR(150) NOT NULL (e.g., 'Accounting')
  description           TEXT
  icon                  VARCHAR(50) (FontAwesome or custom icon name)
  is_installed          BOOLEAN DEFAULT TRUE
  is_visible            BOOLEAN DEFAULT TRUE
  sequence              INT DEFAULT 0 (menu order)
  version               VARCHAR(20) DEFAULT '1.0.0'
  installed_at          TIMESTAMP
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, name)
  idx_module_company_installed
```

#### **module_configurations** (Industry-Specific Settings)
```
Table: core_module_config
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  module_id             BIGINT NOT NULL FOREIGN KEY -> core_module
  key                   VARCHAR(255) NOT NULL (e.g., 'terminology.inventory_label')
  value                 TEXT (JSON or plain text)
  value_type            VARCHAR(50) (string, integer, boolean, json)
  description           TEXT (for documentation)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, module_id, key)
  idx_module_config_lookup (company_id, module_id, key)
```

Example configurations:
```json
{
  "company_id": 1,
  "module_id": 3,  // Inventory module
  "key": "terminology.primary_location_label",
  "value": "Supply Room",  // For DentaFlow
  "value_type": "string"
}

{
  "company_id": 8,  // TableSync
  "module_id": 10,  // Manufacturing
  "key": "terminology.bom_label",
  "value": "Recipe",
  "value_type": "string"
}
```

#### **menus** (Navigation Menu Items, Tree Structure)
```
Table: core_menu
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  module_id             BIGINT FOREIGN KEY -> core_module
  parent_id             BIGINT FOREIGN KEY -> core_menu (self-referential, for hierarchy)
  name                  VARCHAR(255) NOT NULL
  label                 VARCHAR(255) NOT NULL (user-facing label)
  icon                  VARCHAR(50)
  sequence              INT DEFAULT 0 (sort order)
  action_type           VARCHAR(50) NOT NULL (enum: menu, view, report, url)
  action_value          VARCHAR(500) (e.g., route path or URL)
  required_permissions  TEXT (comma-separated permission codenames)
  is_visible            BOOLEAN DEFAULT TRUE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_menu_company_module
  idx_menu_parent
```

#### **views** (Form/List/Kanban/Pivot/Graph View Definitions)
```
Table: core_view
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  module_id             BIGINT NOT NULL FOREIGN KEY -> core_module
  model_name            VARCHAR(100) NOT NULL (e.g., 'invoice', 'product')
  view_type             VARCHAR(50) NOT NULL (enum: form, list, kanban, pivot, graph, calendar, search)
  name                  VARCHAR(255) NOT NULL
  sequence              INT DEFAULT 0
  config_json           JSONB NOT NULL (view configuration)
  is_default            BOOLEAN DEFAULT FALSE
  created_by_user_id    BIGINT FOREIGN KEY -> auth_user
  is_custom             BOOLEAN DEFAULT FALSE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, module_id, model_name, view_type, is_default)
  idx_view_model
```

**View Config JSON Schema (Example for Form View):**
```json
{
  "view_type": "form",
  "title": "Invoice Form",
  "fields": [
    {
      "name": "number",
      "label": "Invoice Number",
      "type": "char",
      "required": true,
      "readonly": true
    },
    {
      "name": "partner_id",
      "label": "Customer",
      "type": "many2one",
      "required": true,
      "relation": "res_partner"
    },
    {
      "name": "invoice_date",
      "label": "Invoice Date",
      "type": "date",
      "required": true
    },
    {
      "name": "line_ids",
      "label": "Invoice Lines",
      "type": "one2many",
      "relation": "invoice_line",
      "relation_field": "invoice_id",
      "views": [
        {
          "view_type": "tree",
          "columns": ["product_id", "quantity", "unit_price", "amount"]
        }
      ]
    }
  ],
  "layout": "vertical",
  "groups": [
    {
      "name": "general",
      "string": "General Information",
      "fields": ["number", "partner_id", "invoice_date"]
    }
  ]
}
```

#### **actions** (Server Actions, Window Actions, Report Actions)
```
Table: core_action
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  type                  VARCHAR(50) NOT NULL (enum: server_action, window_action, report_action, url_action)
  model_name            VARCHAR(100) (target model for action)
  method_name           VARCHAR(100) (Python method for server action)
  action_config_json    JSONB (action-specific configuration)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_action_company_type
```

#### **sequences** (Auto-Numbering/Sequencing)
```
Table: core_sequence
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  prefix                VARCHAR(20) (e.g., 'INV', 'PO', 'SO')
  suffix                VARCHAR(20) (optional)
  next_number           BIGINT DEFAULT 1
  step                  BIGINT DEFAULT 1
  padding               INT DEFAULT 0 (number of zero-padding digits)
  use_date_range        BOOLEAN DEFAULT TRUE (reset annually)
  year_field            VARCHAR(50) (typically 'created_at' year)
  last_reset            TIMESTAMP
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_sequence_company_prefix
```

Example: Sequence for invoices in NovaPay
```
prefix='INV', suffix=NULL, next_number=1, padding=5, use_date_range=TRUE
→ Generated numbers: INV/2026/00001, INV/2026/00002, ..., INV/2026/00100
```

#### **attachments** (File Storage Metadata)
```
Table: core_attachment
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  file_path             VARCHAR(500) NOT NULL (S3 or local path)
  file_size             BIGINT (bytes)
  mime_type             VARCHAR(100)
  model_name            VARCHAR(100) NOT NULL
  model_id              BIGINT NOT NULL (foreign key to target model)
  created_by_user_id    BIGINT FOREIGN KEY -> auth_user
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_attachment_model (model_name, model_id)
  idx_attachment_company
```

#### **audit_log** (Change Tracking — Django Signals)
```
Table: core_audit_log
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  user_id               BIGINT FOREIGN KEY -> auth_user
  model_name            VARCHAR(100) NOT NULL
  model_id              BIGINT NOT NULL
  action                VARCHAR(50) NOT NULL (enum: create, update, delete)
  old_values_json       JSONB (before values for updates)
  new_values_json       JSONB (after values for updates)
  change_description    TEXT
  ip_address            VARCHAR(50)
  timestamp             TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_audit_log_model (model_name, model_id)
  idx_audit_log_user_timestamp (user_id, timestamp)
  idx_audit_log_company
```

#### **notifications** (In-App Notification System)
```
Table: core_notification
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  recipient_user_id     BIGINT NOT NULL FOREIGN KEY -> auth_user
  title                 VARCHAR(255) NOT NULL
  message               TEXT NOT NULL
  notification_type     VARCHAR(50) (enum: info, warning, error, success)
  related_model         VARCHAR(100)
  related_model_id      BIGINT
  action_url            VARCHAR(500)
  is_read               BOOLEAN DEFAULT FALSE
  read_at               TIMESTAMP NULL
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_notification_user_read (recipient_user_id, is_read)
```

#### **settings** (Key-Value System Settings)
```
Table: core_setting
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT FOREIGN KEY -> core_company (NULL = global)
  key                   VARCHAR(255) NOT NULL
  value                 TEXT
  value_type            VARCHAR(50) (string, integer, boolean, json)
  description           TEXT
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, key)
```

---

### 4.2 Module-Specific Tables: Accounting

#### **account_account** (Chart of Accounts)
```
Table: accounting_account
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  code                  VARCHAR(20) NOT NULL (account number)
  name                  VARCHAR(255) NOT NULL
  account_type          VARCHAR(50) NOT NULL (enum: asset, liability, equity, revenue, expense, other)
  account_category      VARCHAR(100) NOT NULL (subcategory within type)
  parent_id             BIGINT FOREIGN KEY -> accounting_account (hierarchical)
  currency_id           BIGINT FOREIGN KEY -> currency (default company currency)
  is_reconcile          BOOLEAN DEFAULT FALSE (bank/payable accounts)
  deprecated            BOOLEAN DEFAULT FALSE
  sequence              INT DEFAULT 0
  active_from           DATE
  active_to             DATE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, code)
  idx_account_type
  idx_account_parent
  idx_account_active
```

#### **account_journal** (Journal Types)
```
Table: accounting_journal
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  code                  VARCHAR(20) NOT NULL
  journal_type          VARCHAR(50) NOT NULL (enum: sale, purchase, bank, cash, general)
  currency_id           BIGINT FOREIGN KEY -> currency
  default_account_id    BIGINT FOREIGN KEY -> accounting_account
  is_active             BOOLEAN DEFAULT TRUE
  sequence              INT DEFAULT 0
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, code)
  idx_journal_type
```

#### **account_move** (Journal Entries, Invoices — Unified)
```
Table: accounting_move
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL (e.g., 'INV/2026/0001')
  move_type             VARCHAR(50) NOT NULL (enum: entry, in_invoice, out_invoice, in_refund, out_refund)
  journal_id            BIGINT NOT NULL FOREIGN KEY -> accounting_journal
  date                  DATE NOT NULL
  ref                   VARCHAR(255) (reference number, e.g., PO number)
  state                  VARCHAR(50) NOT NULL (enum: draft, posted, posted_locked, cancelled)
  partner_id            BIGINT FOREIGN KEY -> res_partner
  currency_id           BIGINT FOREIGN KEY -> currency
  narration             TEXT (memo/description)
  sequence_number       INT (original sequence in journal)
  amount_total          DECIMAL(15, 2) (denormalized for performance)
  amount_tax            DECIMAL(15, 2)
  amount_untaxed        DECIMAL(15, 2)
  is_locked             BOOLEAN DEFAULT FALSE
  posted_by_user_id     BIGINT FOREIGN KEY -> auth_user
  posted_at             TIMESTAMP
  created_by_user_id    BIGINT FOREIGN KEY -> auth_user
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_move_company_date
  idx_move_journal_date
  idx_move_state
  idx_move_partner
```

#### **account_move_line** (Journal Entry Lines)
```
Table: accounting_move_line
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  move_id               BIGINT NOT NULL FOREIGN KEY -> accounting_move
  account_id            BIGINT NOT NULL FOREIGN KEY -> accounting_account
  partner_id            BIGINT FOREIGN KEY -> res_partner
  debit                 DECIMAL(15, 2) DEFAULT 0
  credit                DECIMAL(15, 2) DEFAULT 0
  amount_currency       DECIMAL(15, 2) (in foreign currency if applicable)
  currency_id           BIGINT FOREIGN KEY -> currency
  description           VARCHAR(255)
  is_reconciled         BOOLEAN DEFAULT FALSE
  reconcile_model       VARCHAR(100)
  reconcile_model_id    BIGINT
  sequence              INT DEFAULT 0
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_move_line_move
  idx_move_line_account
  idx_move_line_partner
  idx_move_line_reconciled
```

#### **account_payment** (Payments)
```
Table: accounting_payment
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  partner_id            BIGINT NOT NULL FOREIGN KEY -> res_partner
  partner_bank_id       BIGINT FOREIGN KEY -> res_partner_bank (bank account)
  payment_type          VARCHAR(50) NOT NULL (enum: inbound, outbound)
  partner_type          VARCHAR(50) NOT NULL (enum: customer, supplier)
  payment_method        VARCHAR(50) NOT NULL (enum: check, wire, card, cash, ach)
  amount                DECIMAL(15, 2) NOT NULL
  currency_id           BIGINT FOREIGN KEY -> currency
  payment_date          DATE NOT NULL
  state                  VARCHAR(50) NOT NULL (enum: draft, posted, sent, reconciled, cancelled)
  journal_id            BIGINT NOT NULL FOREIGN KEY -> accounting_journal
  move_id               BIGINT FOREIGN KEY -> accounting_move
  is_matched            BOOLEAN DEFAULT FALSE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_payment_company_date
  idx_payment_partner
  idx_payment_state
  idx_payment_journal
```

#### **account_bank_statement** (Bank Reconciliation)
```
Table: accounting_bank_statement
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  journal_id            BIGINT NOT NULL FOREIGN KEY -> accounting_journal
  name                  VARCHAR(255) NOT NULL
  statement_date        DATE NOT NULL
  begin_balance         DECIMAL(15, 2)
  end_balance           DECIMAL(15, 2)
  currency_id           BIGINT FOREIGN KEY -> currency
  state                  VARCHAR(50) NOT NULL (enum: open, pending, done, cancelled)
  is_complete           BOOLEAN DEFAULT FALSE
  reconciled_line_count INT DEFAULT 0
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_bank_statement_journal_date
  idx_bank_statement_state
```

#### **account_bank_statement_line** (Bank Statement Line Items)
```
Table: accounting_bank_statement_line
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  statement_id          BIGINT NOT NULL FOREIGN KEY -> accounting_bank_statement
  sequence              INT DEFAULT 0
  date                  DATE NOT NULL
  amount                DECIMAL(15, 2)
  partner_id            BIGINT FOREIGN KEY -> res_partner
  description           TEXT
  reference             VARCHAR(255)
  is_reconciled         BOOLEAN DEFAULT FALSE
  reconciliation_move_id BIGINT FOREIGN KEY -> accounting_move
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_statement_line_statement
  idx_statement_line_reconciled
```

#### **account_tax** (Tax Definitions)
```
Table: accounting_tax
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  code                  VARCHAR(50)
  tax_type              VARCHAR(50) NOT NULL (enum: percent, fixed)
  rate                  DECIMAL(5, 2) (percentage, e.g., 8.5 for 8.5%)
  tax_account_id        BIGINT NOT NULL FOREIGN KEY -> accounting_account
  base_account_id       BIGINT FOREIGN KEY -> accounting_account
  is_active             BOOLEAN DEFAULT TRUE
  effective_from        DATE
  effective_to          DATE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_tax_company
  idx_tax_active
```

#### **account_fiscal_year** (Fiscal Period Management)
```
Table: accounting_fiscal_year
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(50) NOT NULL (e.g., 'FY 2026')
  code                  VARCHAR(20)
  start_date            DATE NOT NULL
  end_date              DATE NOT NULL
  is_locked             BOOLEAN DEFAULT FALSE
  locked_at             TIMESTAMP
  locked_by_user_id     BIGINT FOREIGN KEY -> auth_user
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, name)
  idx_fiscal_year_dates
```

---

### 4.3 Module-Specific Tables: Invoicing

#### **invoicing_invoice** (Customer Invoices & Vendor Bills — Unified)
```
Table: invoicing_invoice
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  move_id               BIGINT FOREIGN KEY -> accounting_move (link to accounting entry)
  name                  VARCHAR(255) NOT NULL (e.g., 'INV-2026-001')
  invoice_type          VARCHAR(50) NOT NULL (enum: out_invoice, in_invoice, out_refund, in_refund)
  partner_id            BIGINT NOT NULL FOREIGN KEY -> res_partner
  partner_shipping_id   BIGINT FOREIGN KEY -> res_partner (alternate ship-to)
  currency_id           BIGINT FOREIGN KEY -> currency
  invoice_date          DATE NOT NULL
  due_date              DATE
  payment_terms_id      BIGINT FOREIGN KEY -> payment_terms
  ref                   VARCHAR(255) (vendor reference for bills)
  state                  VARCHAR(50) NOT NULL (enum: draft, posted, sent, accepted, cancel)
  fiscal_year_id        BIGINT FOREIGN KEY -> accounting_fiscal_year
  amount_untaxed        DECIMAL(15, 2)
  amount_tax            DECIMAL(15, 2)
  amount_total          DECIMAL(15, 2)
  amount_paid           DECIMAL(15, 2) DEFAULT 0
  balance_due           DECIMAL(15, 2)
  is_overdue            BOOLEAN DEFAULT FALSE
  tax_id                BIGINT FOREIGN KEY -> accounting_tax (default tax)
  narration             TEXT
  created_by_user_id    BIGINT FOREIGN KEY -> auth_user
  posted_by_user_id     BIGINT FOREIGN KEY -> auth_user
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_invoice_company_date
  idx_invoice_partner
  idx_invoice_state
  idx_invoice_due_date
```

#### **invoicing_invoice_line** (Line Items)
```
Table: invoicing_invoice_line
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  invoice_id            BIGINT NOT NULL FOREIGN KEY -> invoicing_invoice
  product_id            BIGINT FOREIGN KEY -> product (NULL = service/description-only)
  description           TEXT NOT NULL
  quantity              DECIMAL(10, 4) NOT NULL DEFAULT 1
  uom_id                BIGINT NOT NULL FOREIGN KEY -> unit_of_measure
  unit_price            DECIMAL(12, 2) NOT NULL
  discount_percentage   DECIMAL(5, 2) DEFAULT 0
  amount_before_tax     DECIMAL(15, 2)
  tax_id                BIGINT FOREIGN KEY -> accounting_tax
  amount_tax            DECIMAL(15, 2)
  amount_total          DECIMAL(15, 2)
  sequence              INT DEFAULT 0
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_invoice_line_invoice
  idx_invoice_line_product
```

#### **invoicing_credit_note** (Returns/Adjustments)
```
Table: invoicing_credit_note
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  original_invoice_id   BIGINT NOT NULL FOREIGN KEY -> invoicing_invoice
  move_id               BIGINT FOREIGN KEY -> accounting_move
  number                VARCHAR(255) NOT NULL
  date                  DATE NOT NULL
  reason                VARCHAR(255) NOT NULL (enum: return, discount, adjustment, damage)
  amount_before_tax     DECIMAL(15, 2)
  amount_tax            DECIMAL(15, 2)
  amount_total          DECIMAL(15, 2)
  state                  VARCHAR(50) NOT NULL (enum: draft, posted, cancelled)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_credit_note_invoice
  idx_credit_note_date
```

#### **invoicing_payment_terms** (Payment Conditions)
```
Table: invoicing_payment_terms
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL (e.g., 'Net 30', '2/10 Net 30')
  description           TEXT
  is_default            BOOLEAN DEFAULT FALSE
  number_of_days        INT (standard days to pay, e.g., 30)
  is_active             BOOLEAN DEFAULT TRUE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, name)
  idx_payment_terms_default
```

#### **invoicing_recurring_invoice** (Templates for Automatic Generation)
```
Table: invoicing_recurring_invoice
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  partner_id            BIGINT NOT NULL FOREIGN KEY -> res_partner
  frequency             VARCHAR(50) NOT NULL (enum: weekly, monthly, quarterly, yearly)
  next_invoice_date     DATE NOT NULL
  last_generated_date   DATE
  is_active             BOOLEAN DEFAULT TRUE
  template_json         JSONB (invoice template: lines, taxes, terms)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_recurring_invoice_partner_active
  idx_recurring_invoice_next_date
```

---

### 4.4 Module-Specific Tables: Inventory

#### **inventory_product** (Inventory Items)
```
Table: inventory_product
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  sku                   VARCHAR(100) NOT NULL
  name                  VARCHAR(255) NOT NULL
  category_id           BIGINT NOT NULL FOREIGN KEY -> inventory_product_category
  description           TEXT
  product_type          VARCHAR(50) NOT NULL (enum: consumable, service, storable)
  uom_id                BIGINT NOT NULL FOREIGN KEY -> unit_of_measure
  purchase_uom_id       BIGINT FOREIGN KEY -> unit_of_measure
  cost_price            DECIMAL(12, 2)
  list_price            DECIMAL(12, 2)
  is_active             BOOLEAN DEFAULT TRUE
  reorder_point         DECIMAL(10, 2) (quantity trigger for PO)
  reorder_qty           DECIMAL(10, 2) (quantity to order)
  lead_time_days        INT (supplier lead time)
  is_serialized         BOOLEAN DEFAULT FALSE (lot/serial tracking)
  has_expiry            BOOLEAN DEFAULT FALSE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, sku)
  idx_product_category
  idx_product_active
```

#### **inventory_product_category** (Hierarchical Organization)
```
Table: inventory_product_category
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  parent_id             BIGINT FOREIGN KEY -> inventory_product_category
  description           TEXT
  is_active             BOOLEAN DEFAULT TRUE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_category_company
  idx_category_parent
```

#### **inventory_stock_location** (Warehouse Zones, Bins)
```
Table: inventory_stock_location
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  parent_id             BIGINT FOREIGN KEY -> inventory_stock_location (hierarchy)
  location_type         VARCHAR(50) NOT NULL (enum: warehouse, zone, bin, shelf, rack)
  barcode               VARCHAR(100)
  is_active             BOOLEAN DEFAULT TRUE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_location_company
  idx_location_parent
```

#### **inventory_stock_move** (Inventory Transactions)
```
Table: inventory_stock_move
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  product_id            BIGINT NOT NULL FOREIGN KEY -> inventory_product
  location_from_id      BIGINT NOT NULL FOREIGN KEY -> inventory_stock_location
  location_to_id        BIGINT NOT NULL FOREIGN KEY -> inventory_stock_location
  move_type             VARCHAR(50) NOT NULL (enum: receipt, delivery, internal_transfer, inventory_adjustment)
  quantity_ordered      DECIMAL(10, 2)
  quantity_done         DECIMAL(10, 2)
  uom_id                BIGINT NOT NULL FOREIGN KEY -> unit_of_measure
  reference_document    VARCHAR(100) (PO/SO/Work Order number)
  reference_model       VARCHAR(100) (model_name: purchasing_order, sales_order, etc.)
  reference_model_id    BIGINT
  state                  VARCHAR(50) NOT NULL (enum: draft, assigned, confirmed, done, cancelled)
  date                  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_stock_move_product
  idx_stock_move_location
  idx_stock_move_reference
  idx_stock_move_state
```

#### **inventory_stock_lot** (Lot/Batch & Serial Tracking)
```
Table: inventory_stock_lot
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  product_id            BIGINT NOT NULL FOREIGN KEY -> inventory_product
  lot_number            VARCHAR(100) NOT NULL
  serial_number         VARCHAR(100)
  expiry_date           DATE
  manufacture_date      DATE
  quantity_on_hand      DECIMAL(10, 2)
  is_blocked            BOOLEAN DEFAULT FALSE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, product_id, lot_number)
  idx_stock_lot_expiry
```

#### **inventory_reorder_rule** (Automatic PO Triggers)
```
Table: inventory_reorder_rule
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  product_id            BIGINT NOT NULL FOREIGN KEY -> inventory_product
  location_id           BIGINT NOT NULL FOREIGN KEY -> inventory_stock_location
  vendor_id             BIGINT NOT NULL FOREIGN KEY -> res_partner
  min_quantity          DECIMAL(10, 2) NOT NULL (reorder point)
  max_quantity          DECIMAL(10, 2) NOT NULL (quantity to order to)
  qty_multiple          DECIMAL(10, 2) DEFAULT 1 (order in multiples)
  lead_time             INT (days)
  is_active             BOOLEAN DEFAULT TRUE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, product_id, location_id)
  idx_reorder_rule_vendor
```

#### **inventory_adjustment** (Stock Counts & Discrepancies)
```
Table: inventory_adjustment
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  date                  DATE NOT NULL
  adjustment_type       VARCHAR(50) NOT NULL (enum: physical_count, discrepancy)
  state                  VARCHAR(50) NOT NULL (enum: draft, in_progress, done, cancelled)
  notes                  TEXT
  created_by_user_id    BIGINT FOREIGN KEY -> auth_user
  approved_by_user_id   BIGINT FOREIGN KEY -> auth_user
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_adjustment_company_date
  idx_adjustment_state
```

#### **inventory_adjustment_line** (Individual Adjustment Items)
```
Table: inventory_adjustment_line
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  adjustment_id         BIGINT NOT NULL FOREIGN KEY -> inventory_adjustment
  product_id            BIGINT NOT NULL FOREIGN KEY -> inventory_product
  location_id           BIGINT NOT NULL FOREIGN KEY -> inventory_stock_location
  expected_quantity     DECIMAL(10, 2)
  counted_quantity      DECIMAL(10, 2)
  difference            DECIMAL(10, 2)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_adjustment_line_adjustment
```

---

### 4.5 Module-Specific Tables: Fleet Management

#### **fleet_vehicle** (Vehicle Master)
```
Table: fleet_vehicle
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(255) NOT NULL
  license_plate         VARCHAR(50) NOT NULL UNIQUE
  vin                   VARCHAR(20) UNIQUE
  make                  VARCHAR(100)
  model                 VARCHAR(100)
  year                  INT
  vehicle_type_id       BIGINT NOT NULL FOREIGN KEY -> fleet_vehicle_category
  acquisition_date      DATE
  acquisition_value     DECIMAL(15, 2)
  registration_date     DATE
  registration_expiry   DATE
  is_active             BOOLEAN DEFAULT TRUE
  is_available          BOOLEAN DEFAULT TRUE
  current_mileage       DECIMAL(10, 2)
  fuel_type             VARCHAR(50) (enum: gasoline, diesel, electric, hybrid)
  fuel_capacity         DECIMAL(8, 2) (liters or gallons)
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, license_plate)
  idx_vehicle_type
  idx_vehicle_active
```

#### **fleet_vehicle_category** (Vehicle Types)
```
Table: fleet_vehicle_category
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  name                  VARCHAR(100) NOT NULL (car, truck, van, motorcycle, equipment)
  description           TEXT
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  UNIQUE(company_id, name)
```

#### **fleet_maintenance_schedule** (Preventive Maintenance)
```
Table: fleet_maintenance_schedule
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  vehicle_id            BIGINT NOT NULL FOREIGN KEY -> fleet_vehicle
  service_type          VARCHAR(100) NOT NULL (enum: oil_change, tire_rotation, inspection, brakes, fluids)
  due_mileage           DECIMAL(10, 2)
  due_date              DATE
  interval_months       INT
  notes                  TEXT
  is_active             BOOLEAN DEFAULT TRUE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_maintenance_schedule_vehicle_due
```

#### **fleet_maintenance_record** (Performed Maintenance)
```
Table: fleet_maintenance_record
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  vehicle_id            BIGINT NOT NULL FOREIGN KEY -> fleet_vehicle
  schedule_id           BIGINT FOREIGN KEY -> fleet_maintenance_schedule
  date                  DATE NOT NULL
  mileage               DECIMAL(10, 2)
  service_type          VARCHAR(100)
  description           TEXT
  cost                  DECIMAL(12, 2)
  parts_cost            DECIMAL(12, 2)
  labor_cost            DECIMAL(12, 2)
  performed_by          VARCHAR(255) (technician name or vendor)
  invoice_number        VARCHAR(255)
  created_by_user_id    BIGINT FOREIGN KEY -> auth_user
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_maintenance_record_vehicle_date
  idx_maintenance_record_mileage
```

#### **fleet_fuel_log** (Fuel & Expense Tracking)
```
Table: fleet_fuel_log
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  vehicle_id            BIGINT NOT NULL FOREIGN KEY -> fleet_vehicle
  date                  DATE NOT NULL
  mileage               DECIMAL(10, 2)
  quantity_liters       DECIMAL(8, 2)
  unit_price            DECIMAL(10, 4)
  total_cost            DECIMAL(12, 2)
  fuel_type             VARCHAR(50)
  vendor                VARCHAR(255)
  odometer_reading      DECIMAL(10, 2)
  mpg_calculated        DECIMAL(6, 2)
  created_by_user_id    BIGINT FOREIGN KEY -> auth_user
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_fuel_log_vehicle_date
  idx_fuel_log_mpg_calc
```

#### **fleet_driver_assignment** (Driver-to-Vehicle Assignment)
```
Table: fleet_driver_assignment
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  driver_id             BIGINT NOT NULL FOREIGN KEY -> hr_employee
  vehicle_id            BIGINT NOT NULL FOREIGN KEY -> fleet_vehicle
  assignment_start      DATE NOT NULL
  assignment_end        DATE
  is_primary_driver     BOOLEAN DEFAULT FALSE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_driver_assignment_vehicle_dates
  idx_driver_assignment_driver
```

#### **fleet_insurance_policy** (Vehicle Insurance Tracking)
```
Table: fleet_insurance_policy
Columns:
  id                    BIGINT PRIMARY KEY AUTO_INCREMENT
  company_id            BIGINT NOT NULL FOREIGN KEY -> core_company
  vehicle_id            BIGINT NOT NULL FOREIGN KEY -> fleet_vehicle
  policy_number         VARCHAR(100) NOT NULL
  provider_name         VARCHAR(255)
  coverage_type         VARCHAR(100) (comprehensive, collision, liability)
  premium_amount        DECIMAL(12, 2)
  premium_frequency     VARCHAR(50) (monthly, quarterly, annual)
  policy_start_date     DATE
  policy_expiry_date    DATE
  deductible            DECIMAL(12, 2)
  is_active             BOOLEAN DEFAULT TRUE
  created_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
  updated_at            TIMESTAMP DEFAULT CURRENT_TIMESTAMP
Indexes:
  idx_insurance_vehicle_expiry
```

---

## 5. SYSTEM ARCHITECTURE

### 5.1 Technology Stack Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     FRONTEND LAYER (React 18)                    │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Industry-Specific UI (10 instances)                     │   │
│  │  - NovaPay (14001), MedVista (14002), etc.              │   │
│  │  - Shared ERP Core Components                            │   │
│  │  - Responsive, TypeScript, Vite                          │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (HTTP/REST, JWT Auth)
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY & DRF LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Django REST Framework ViewSets                          │   │
│  │  /api/v1/{module}/{model}/ routes                        │   │
│  │  - Serializers, Filters, Pagination                      │   │
│  │  - Multi-tenant Filtering (by company_id)                │   │
│  │  - JWT Authentication & Permissions                      │   │
│  │  - OpenAPI/Swagger (drf-spectacular)                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│  ERP Core API Port: 14000                                        │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (ORM)
┌─────────────────────────────────────────────────────────────────┐
│                  DJANGO ORM & BUSINESS LOGIC                     │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Core Models & Signals (Users, Companies, Modules, etc.) │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  13 Module Apps (each with models & signals)      │  │   │
│  │  │  - Accounting, Invoicing, Inventory, Fleet, etc.  │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  │  ┌────────────────────────────────────────────────────┐  │   │
│  │  │  Industry Configuration System                     │  │   │
│  │  │  - Module Config (terminology, defaults)           │  │   │
│  │  │  - Industry Agents (10x) override behavior         │  │   │
│  │  └────────────────────────────────────────────────────┘  │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓ (psycopg2)
┌─────────────────────────────────────────────────────────────────┐
│                  PostgreSQL 15+ Database                         │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Multi-tenant schema (all data, one DB)                 │   │
│  │  - Core tables (companies, users, modules, etc.)        │   │
│  │  - 13 Module table groups                               │   │
│  │  - Audit logs, attachments, settings                    │   │
│  │  - JSONB for flexible configs                           │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Port: 5432                                                      │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    ASYNCHRONOUS TASK QUEUE                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Celery 5.x + Redis                                      │   │
│  │  - Async task execution (report generation, emails)      │   │
│  │  - Celery Beat: scheduled tasks (recur. invoices, etc.)  │   │
│  │  - Redis: broker & result backend                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│  Redis Port: 6379                                                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                    REAL-TIME COMMUNICATION                       │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  Django Channels + Redis                                 │   │
│  │  - WebSocket support for notifications, live updates    │   │
│  │  - Group messaging (e.g., all users in company)         │   │
│  │  - Chat, presence, collaborative editing (future)       │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Docker Compose Service Topology

```yaml
version: '3.9'

services:
  postgres:
    image: postgres:15-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_DB: erp_platform
      POSTGRES_USER: erp_user
      POSTGRES_PASSWORD: secure_dev_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - erp_network

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - erp_network

  django_api:
    build: ./core/backend
    command: >
      sh -c "python manage.py migrate &&
             python manage.py create_demo_data &&
             gunicorn config.wsgi:application --bind 0.0.0.0:14000 --workers 4"
    ports:
      - "14000:14000"
    environment:
      DEBUG: "False"
      SECRET_KEY: "django-insecure-demo-key-change-in-production"
      DATABASE_URL: "postgresql://erp_user:secure_dev_password@postgres:5432/erp_platform"
      REDIS_URL: "redis://redis:6379/0"
      ALLOWED_HOSTS: "localhost,127.0.0.1,django_api"
      CSRF_TRUSTED_ORIGINS: "http://localhost:14500,http://localhost:14001,..."
    depends_on:
      - postgres
      - redis
    networks:
      - erp_network
    volumes:
      - ./core/backend:/app

  celery_worker:
    build: ./core/backend
    command: celery -A config worker -l info
    environment:
      DATABASE_URL: "postgresql://erp_user:secure_dev_password@postgres:5432/erp_platform"
      REDIS_URL: "redis://redis:6379/0"
    depends_on:
      - postgres
      - redis
      - django_api
    networks:
      - erp_network
    volumes:
      - ./core/backend:/app

  celery_beat:
    build: ./core/backend
    command: celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
    environment:
      DATABASE_URL: "postgresql://erp_user:secure_dev_password@postgres:5432/erp_platform"
      REDIS_URL: "redis://redis:6379/0"
    depends_on:
      - postgres
      - redis
      - django_api
    networks:
      - erp_network
    volumes:
      - ./core/backend:/app

  react_frontend:
    build: ./core/frontend
    command: npm run dev
    ports:
      - "14500:5173"  # Vite dev server
    environment:
      VITE_API_URL: "http://localhost:14000"
    depends_on:
      - django_api
    networks:
      - erp_network
    volumes:
      - ./core/frontend:/app
      - /app/node_modules

  # Industry-specific frontends (example: NovaPay)
  novapay_frontend:
    build: ./industries/novapay/frontend
    command: npm run dev
    ports:
      - "14001:5173"
    environment:
      VITE_API_URL: "http://localhost:14000"
      VITE_COMPANY_SLUG: "novapay"
    depends_on:
      - django_api
    networks:
      - erp_network
    volumes:
      - ./industries/novapay/frontend:/app

  # ... (repeat for MedVista, TrustGuard, ... all 10 industries)

  medvista_frontend:
    build: ./industries/medvista/frontend
    command: npm run dev
    ports:
      - "14002:5173"
    environment:
      VITE_API_URL: "http://localhost:14000"
      VITE_COMPANY_SLUG: "medvista"
    depends_on:
      - django_api
    networks:
      - erp_network

  # ... continue for all 10 industries

volumes:
  postgres_data:
  redis_data:

networks:
  erp_network:
    driver: bridge
```

### 5.3 API Route Structure (DRF ViewSets)

All routes follow RESTful conventions with multi-tenant filtering:

```
Base: /api/v1/

ACCOUNTING MODULE:
  GET    /accounting/accounts/                      # List all accounts (filtered by company)
  POST   /accounting/accounts/                      # Create account
  GET    /accounting/accounts/{id}/                 # Get account details
  PATCH  /accounting/accounts/{id}/                 # Update account
  DELETE /accounting/accounts/{id}/                 # Delete (soft delete via audit)

  GET    /accounting/journals/
  POST   /accounting/journals/
  GET    /accounting/journals/{id}/

  GET    /accounting/moves/                         # All journal entries
  POST   /accounting/moves/                         # Create entry
  GET    /accounting/moves/{id}/
  PATCH  /accounting/moves/{id}/
  POST   /accounting/moves/{id}/post/               # Custom action: post entry

  GET    /accounting/move_lines/                    # Filter by move_id

  GET    /accounting/payments/
  POST   /accounting/payments/
  PATCH  /accounting/payments/{id}/
  POST   /accounting/payments/{id}/reconcile/       # Custom: reconcile payment

  GET    /accounting/bank_statements/
  POST   /accounting/bank_statements/
  GET    /accounting/bank_statements/{id}/reconcile/ # Reconciliation interface

  GET    /accounting/taxes/
  POST   /accounting/taxes/

  GET    /accounting/fiscal_years/

INVOICING MODULE:
  GET    /invoicing/invoices/                       # Unified: in_invoice + out_invoice
  POST   /invoicing/invoices/
  GET    /invoicing/invoices/{id}/
  PATCH  /invoicing/invoices/{id}/
  POST   /invoicing/invoices/{id}/post/
  POST   /invoicing/invoices/{id}/send/             # Email invoice

  GET    /invoicing/invoice_lines/
  POST   /invoicing/invoice_lines/

  GET    /invoicing/credit_notes/
  POST   /invoicing/credit_notes/

  GET    /invoicing/payment_terms/
  POST   /invoicing/payment_terms/

  GET    /invoicing/recurring_invoices/
  POST   /invoicing/recurring_invoices/

INVENTORY MODULE:
  GET    /inventory/products/
  POST   /inventory/products/
  GET    /inventory/products/{id}/

  GET    /inventory/product_categories/
  POST   /inventory/product_categories/

  GET    /inventory/stock_locations/
  POST   /inventory/stock_locations/

  GET    /inventory/stock_moves/
  POST   /inventory/stock_moves/
  PATCH  /inventory/stock_moves/{id}/
  POST   /inventory/stock_moves/{id}/confirm/
  POST   /inventory/stock_moves/{id}/done/

  GET    /inventory/stock_lots/
  POST   /inventory/stock_lots/

  GET    /inventory/reorder_rules/
  POST   /inventory/reorder_rules/

  GET    /inventory/adjustments/
  POST   /inventory/adjustments/

FLEET MODULE:
  GET    /fleet/vehicles/
  POST   /fleet/vehicles/
  GET    /fleet/vehicles/{id}/

  GET    /fleet/maintenance_schedules/
  POST   /fleet/maintenance_schedules/

  GET    /fleet/maintenance_records/
  POST   /fleet/maintenance_records/

  GET    /fleet/fuel_logs/
  POST   /fleet/fuel_logs/

  GET    /fleet/driver_assignments/
  POST   /fleet/driver_assignments/

CALENDAR MODULE:
  GET    /calendar/events/
  POST   /calendar/events/
  GET    /calendar/events/{id}/
  PATCH  /calendar/events/{id}/
  DELETE /calendar/events/{id}/

  GET    /calendar/resources/
  POST   /calendar/resources/

  GET    /calendar/sync/                            # CalDAV-style sync endpoint
  POST   /calendar/sync/                            # Create/update events from CRM

HR MODULE:
  GET    /hr/employees/
  POST   /hr/employees/
  GET    /hr/employees/{id}/

  GET    /hr/departments/
  POST   /hr/departments/

  GET    /hr/job_positions/
  POST   /hr/job_positions/

  GET    /hr/employment_contracts/
  POST   /hr/employment_contracts/

  GET    /hr/attendance_records/
  POST   /hr/attendance_records/

  GET    /hr/leave_types/
  POST   /hr/leave_types/

  GET    /hr/leave_requests/
  POST   /hr/leave_requests/
  PATCH  /hr/leave_requests/{id}/approve/
  PATCH  /hr/leave_requests/{id}/reject/

  GET    /hr/timesheets/
  POST   /hr/timesheets/

PROJECT MODULE:
  GET    /projects/projects/
  POST   /projects/projects/
  GET    /projects/projects/{id}/

  GET    /projects/tasks/
  POST   /projects/tasks/
  PATCH  /projects/tasks/{id}/

  GET    /projects/milestones/
  POST   /projects/milestones/

  GET    /projects/timesheets/
  POST   /projects/timesheets/

PURCHASING MODULE:
  GET    /purchasing/vendors/
  POST   /purchasing/vendors/
  GET    /purchasing/vendors/{id}/

  GET    /purchasing/orders/
  POST   /purchasing/orders/
  GET    /purchasing/orders/{id}/
  PATCH  /purchasing/orders/{id}/confirm/

  GET    /purchasing/rfqs/
  POST   /purchasing/rfqs/

  GET    /purchasing/agreements/
  POST   /purchasing/agreements/

SALES MODULE:
  GET    /sales/customers/
  POST   /sales/customers/
  GET    /sales/customers/{id}/

  GET    /sales/quotations/
  POST   /sales/quotations/
  POST   /sales/quotations/{id}/confirm/

  GET    /sales/sales_orders/
  POST   /sales/sales_orders/

  GET    /sales/pricelists/
  POST   /sales/pricelists/

MANUFACTURING MODULE:
  GET    /manufacturing/boms/
  POST   /manufacturing/boms/

  GET    /manufacturing/work_centers/
  POST   /manufacturing/work_centers/

  GET    /manufacturing/manufacturing_orders/
  POST   /manufacturing/manufacturing_orders/
  PATCH  /manufacturing/manufacturing_orders/{id}/start/
  PATCH  /manufacturing/manufacturing_orders/{id}/complete/

POS MODULE:
  GET    /pos/stations/
  POST   /pos/stations/

  GET    /pos/sessions/
  POST   /pos/sessions/
  POST   /pos/sessions/{id}/close/

  GET    /pos/orders/
  POST   /pos/orders/

  GET    /pos/payment_methods/
  POST   /pos/payment_methods/

HELPDESK MODULE:
  GET    /helpdesk/tickets/
  POST   /helpdesk/tickets/
  GET    /helpdesk/tickets/{id}/
  PATCH  /helpdesk/tickets/{id}/

  POST   /helpdesk/tickets/{id}/comments/

  GET    /helpdesk/knowledge_base/
  POST   /helpdesk/knowledge_base/

REPORTS MODULE:
  GET    /reports/definitions/
  POST   /reports/definitions/
  GET    /reports/definitions/{id}/execute/         # Generate report

  GET    /reports/templates/

  GET    /reports/scheduled_reports/
  POST   /reports/scheduled_reports/

CORE PLATFORM:
  GET    /core/companies/
  POST   /core/companies/
  GET    /core/companies/{id}/

  GET    /core/users/
  POST   /core/users/
  GET    /core/users/{id}/

  GET    /core/modules/
  GET    /core/modules/{id}/config/                 # Get module configuration
  PATCH  /core/modules/{id}/config/                 # Update module configuration

  GET    /core/permissions/

  GET    /core/settings/
  PATCH  /core/settings/{key}/

  GET    /core/audit_logs/

  GET    /core/notifications/
  PATCH  /core/notifications/{id}/read/

  POST   /auth/login/                               # JWT authentication
  POST   /auth/logout/
  POST   /auth/refresh/                             # Refresh JWT token
```

### 5.4 Authentication & Authorization

**JWT Authentication Flow:**
1. User logs in with username/password → `/auth/login/`
2. Server validates and returns `{ access_token, refresh_token }`
3. Client includes `Authorization: Bearer <access_token>` in all API requests
4. Middleware extracts JWT, validates signature, loads user and company context
5. All API queries automatically filtered by `company_id` from user's profile

**Permission Model (RBAC):**
- Roles (Admin, Manager, User, custom roles per company)
- Permissions (module.action, e.g., 'accounting.create_invoice', 'invoicing.post_invoice')
- Role-Permission assignments
- User-Role assignments
- All DRF ViewSets check permissions before allowing CRUD operations

**Default Demo Credentials:**
```
Username: admin
Password: admin
Company: All (or select at login)
```

---

## 6. MODULE SYSTEM & INDUSTRY ADAPTATION MECHANISM

### 6.1 Core Module Architecture

Each of the 13 modules is a Django app with:

```
<module_name>/
├── models.py           # Django ORM models (inherited in DB)
├── serializers.py      # DRF serializers for API
├── views.py            # DRF ViewSets & custom actions
├── urls.py             # URL routing for module
├── admin.py            # Django admin customization
├── signals.py          # Django signals (hooks for audit, cascading deletes)
├── forms.py            # Django forms (if server-rendered pages exist)
├── templates/          # HTML templates (minimal, mostly JSON/API)
├── tests/
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_serializers.py
│   └── factories.py    # factory_boy for test data
├── migrations/         # Django migrations
├── apps.py             # Django app config
└── __init__.py
```

### 6.2 Industry-Specific Configuration System

**Problem**: How do 10 industries use the same 13 modules with different terminology and workflows?

**Solution**: **Module Configuration Registry** + **Agent-Based Customization**

#### **Configuration Hierarchy:**

```
GLOBAL DEFAULT (hard-coded in Python)
  ↓ (overridden by)
INDUSTRY CONFIG (core_module_config table)
  ↓ (overridden by)
USER PREFERENCES (per-user settings)
```

#### **Example: Inventory Module Terminology**

**Global Default:**
```python
# inventory/config.py
INVENTORY_CONFIG = {
    "primary_location_label": "Warehouse",
    "primary_location_icon": "building",
    "reorder_label": "Reorder Point",
    "product_alias": "Product",
    "product_uom_alias": "Unit of Measure",
}
```

**DentaFlow (Dental Clinic) Override:**
```json
// In core_module_config table
{
  "company_id": 6,  // DentaFlow
  "module_id": 3,   // Inventory
  "key": "terminology.primary_location_label",
  "value": "Supply Room"
},
{
  "company_id": 6,
  "module_id": 3,
  "key": "terminology.product_alias",
  "value": "Dental Material"
}
```

**TableSync (Restaurant) Override:**
```json
{
  "company_id": 8,   // TableSync
  "module_id": 3,    // Inventory
  "key": "terminology.primary_location_label",
  "value": "Kitchen / Pantry"
},
{
  "company_id": 8,
  "module_id": 3,
  "key": "terminology.product_alias",
  "value": "Ingredient"
}
```

#### **Python Function to Get Configuration:**

```python
# core/config.py
from django.core.cache import cache
from core.models import ModuleConfig

def get_module_config(company_id, module_id, key, default=None):
    """
    Retrieve module configuration with caching.

    Hierarchy:
    1. Check user preference (if provided)
    2. Check industry override (core_module_config)
    3. Return global default
    """
    cache_key = f"module_config:{company_id}:{module_id}:{key}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    try:
        config = ModuleConfig.objects.get(
            company_id=company_id,
            module_id=module_id,
            key=key
        )
        value = config.value
    except ModuleConfig.DoesNotExist:
        # Try global config
        from inventory.config import get_default_config
        value = get_default_config(key, default)

    cache.set(cache_key, value, timeout=3600)
    return value

# Usage in views/serializers:
primary_location_label = get_module_config(
    request.user.profile.company_id,
    inventory_module_id,
    "terminology.primary_location_label",
    default="Warehouse"
)
```

#### **React Component Usage:**

```typescript
// components/InventoryLocations.tsx
import { useModuleConfig } from '@/hooks/useModuleConfig';

export function InventoryLocations() {
  const primaryLocationLabel = useModuleConfig(
    'inventory',
    'terminology.primary_location_label'
  );

  return (
    <div>
      <h2>{primaryLocationLabel}</h2>
      {/* ... */}
    </div>
  );
}
```

### 6.3 Industry Agents & Domain Customization

**Agent Architecture:**
- **1 ERP Core Platform Agent**: Maintains the core platform, multi-tenancy, module system, deployment
- **10 Industry Agents** (one per company): Each handles domain-specific features, demo data, and workflows

**Industry Agent Responsibilities:**

For **NovaPay (FinTech):**
- Generate demo data: 50+ merchants, 100+ transactions, multi-currency scenarios
- Configure accounting: merchant fee recognition, interchange income
- Workflows: merchant onboarding as "sales", payment reconciliation
- Custom reports: merchant dashboard, chargeback tracking

For **MedVista (Healthcare):**
- Generate demo data: 50+ patients, 100+ appointments, lab results, insurance claims
- Configure calendar: patient appointment slots, insurance validation
- Workflows: patient intake → diagnosis → treatment → billing (insurance + copay)
- Custom reports: patient aged receivables, insurance claim status

For **TableSync (Restaurant):**
- Generate demo data: menus, inventory, recipes (as BoM), orders
- Configure manufacturing: recipes as bills of materials
- Workflows: order entry → kitchen production → POS → payment
- Custom reports: food cost %, recipe profitability, table turnover

**Domain-Specific Logic via Model Managers:**

```python
# sales/models.py

class QuotationManager(models.Manager):
    def filter_by_company(self, company):
        return self.filter(company=company)

class Quotation(models.Model):
    # ... fields ...
    objects = QuotationManager()

    @property
    def workflow_state_label(self):
        """Return human-readable state based on industry config."""
        config = get_module_config(
            self.company.id,
            MODULE_SALES,
            'quotation_state_labels'
        )
        return config.get(self.state, self.state)

    def can_transition_to(self, next_state):
        """Check if state transition is allowed (may vary by industry)."""
        allowed_transitions = get_module_config(
            self.company.id,
            MODULE_SALES,
            'quotation_transitions'
        )
        return next_state in allowed_transitions.get(self.state, [])
```

### 6.4 Demo Data Generation Strategy

Each industry agent generates 50-100+ records per main entity to populate the system with realistic data.

**Example: NovaPay Demo Data Seeder**

```python
# industries/novapay/management/commands/seed_novapay_data.py

from django.core.management.base import BaseCommand
from factory_boy import factories
from core.models import Company
from invoicing.models import Invoice, InvoiceLine
from accounting.models import Account, Move, MoveLine
from sales.models import Customer, Quotation

class Command(BaseCommand):
    def handle(self, *args, **options):
        company = Company.objects.get(slug='novapay')

        # Create chart of accounts
        self.create_chart_of_accounts(company)

        # Create customers (merchants)
        merchants = self.create_merchants(company, count=50)

        # Create sales quotations
        quotations = self.create_quotations(company, merchants, count=30)

        # Create invoices (merchant fee invoices)
        invoices = self.create_invoices(company, merchants, count=100)

        # Create accounting entries
        self.create_accounting_entries(company, invoices)

        self.stdout.write(
            self.style.SUCCESS(
                f'Seeded NovaPay with {len(merchants)} merchants, '
                f'{len(quotations)} quotations, {len(invoices)} invoices'
            )
        )

    def create_chart_of_accounts(self, company):
        """Create NovaPay-specific chart of accounts."""
        Account.objects.get_or_create(
            company=company,
            code='1000',
            defaults={'name': 'Cash', 'account_type': 'asset'}
        )
        Account.objects.get_or_create(
            company=company,
            code='4100',
            defaults={'name': 'Merchant Processing Revenue', 'account_type': 'revenue'}
        )
        Account.objects.get_or_create(
            company=company,
            code='4200',
            defaults={'name': 'Interchange Income', 'account_type': 'revenue'}
        )
        Account.objects.get_or_create(
            company=company,
            code='5100',
            defaults={'name': 'Merchant Commissions', 'account_type': 'expense'}
        )
        # ... more accounts

    def create_merchants(self, company, count=50):
        """Generate 50 merchant accounts."""
        merchants = []
        for i in range(count):
            merchant = Customer.objects.create(
                company=company,
                name=f"Merchant {i+1}",
                email=f"merchant{i+1}@novapay.example.com",
                credit_limit=50000.00
            )
            merchants.append(merchant)
        return merchants

    def create_invoices(self, company, merchants, count=100):
        """Generate 100 merchant fee invoices."""
        invoices = []
        for i in range(count):
            merchant = merchants[i % len(merchants)]
            invoice = Invoice.objects.create(
                company=company,
                invoice_type='out_invoice',
                partner=merchant,
                invoice_date=datetime.date.today(),
                due_date=datetime.date.today() + datetime.timedelta(days=30)
            )
            # Add invoice line (merchant fee)
            InvoiceLine.objects.create(
                invoice=invoice,
                description='Monthly Processing Fees',
                quantity=1,
                unit_price=Decimal(str(random.randint(500, 5000)))
            )
            invoices.append(invoice)
        return invoices

    # ... more methods
```

---

## 7. PROJECT STRUCTURE

```
14-ERP-Platform/
│
├── core/                                    # Core ERP Platform
│   ├── backend/                             # Django Backend
│   │   ├── config/
│   │   │   ├── settings.py                  # Django settings (multi-tenancy, middleware)
│   │   │   ├── urls.py                      # Root URL routing
│   │   │   ├── wsgi.py                      # WSGI entrypoint
│   │   │   ├── asgi.py                      # ASGI for Django Channels
│   │   │   └── celery_config.py             # Celery task configuration
│   │   │
│   │   ├── core/                            # Core app (users, companies, modules)
│   │   │   ├── models.py                    # User, Company, Module, Permission models
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py                   # Audit logging via Django signals
│   │   │   ├── config.py                    # get_module_config() function
│   │   │   └── management/commands/
│   │   │       └── create_demo_data.py      # Initialize demo data for all industries
│   │   │
│   │   ├── accounting/                      # Accounting Module
│   │   │   ├── models.py                    # Account, Journal, Move, Payment, Tax
│   │   │   ├── serializers.py
│   │   │   ├── views.py                     # AccountViewSet, JournalViewSet, etc.
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── invoicing/                       # Invoicing/Billing Module
│   │   │   ├── models.py                    # Invoice, InvoiceLine, CreditNote
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── inventory/                       # Inventory/Warehouse Module
│   │   │   ├── models.py                    # Product, StockLocation, StockMove, Lot
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── config.py                    # Default config (primary_location_label, etc.)
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── fleet/                           # Fleet Management Module
│   │   │   ├── models.py                    # Vehicle, MaintenanceRecord, FuelLog
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── calendar_app/                    # Calendar/Scheduling Module
│   │   │   ├── models.py                    # CalendarEvent, Resource, Attendee
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── calendar_sync.py             # CalDAV-style API for Project 13 CRM sync
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── hr/                              # Human Resources Module
│   │   │   ├── models.py                    # Employee, Department, LeaveRequest, Timesheet
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── project/                         # Project Management Module
│   │   │   ├── models.py                    # Project, Task, Milestone, Timesheet
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── purchasing/                      # Purchasing Module
│   │   │   ├── models.py                    # Vendor, PurchaseOrder, RFQ, Receipt
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── sales/                           # Sales Module
│   │   │   ├── models.py                    # Customer, Quotation, SalesOrder, Pricelist
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── manufacturing/                   # Manufacturing/Production Module
│   │   │   ├── models.py                    # BillOfMaterials, WorkCenter, ManufacturingOrder
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── pos/                             # Point of Sale Module
│   │   │   ├── models.py                    # POSStation, POSSession, POSOrder
│   │   │   ├── serializers.py
│   │   │   ├── views.py                     # Touch-screen optimized endpoints
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── helpdesk/                        # Helpdesk/Support Tickets Module
│   │   │   ├── models.py                    # SupportTicket, TicketComment, KnowledgeBaseArticle
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── reports/                         # Reports/BI Module
│   │   │   ├── models.py                    # ReportDefinition, GraphDefinition, ScheduledReport
│   │   │   ├── serializers.py
│   │   │   ├── views.py
│   │   │   ├── urls.py
│   │   │   ├── report_builders.py           # Logic for pivot, graph, export
│   │   │   ├── signals.py
│   │   │   └── tests/
│   │   │
│   │   ├── templates/                       # Django HTML templates (minimal)
│   │   │   └── base.html
│   │   │
│   │   ├── static/
│   │   │   └── css/
│   │   │       └── base.css
│   │   │
│   │   ├── manage.py
│   │   ├── requirements.txt
│   │   ├── pytest.ini
│   │   ├── .env.example
│   │   └── Dockerfile
│   │
│   ├── frontend/                            # React Frontend
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── Common/
│   │   │   │   │   ├── TopNavbar.tsx         # Odoo-style purple navbar with brand color
│   │   │   │   │   ├── Sidebar.tsx           # Module navigation sidebar
│   │   │   │   │   └── LoginForm.tsx
│   │   │   │   │
│   │   │   │   ├── Module Components/
│   │   │   │   │   ├── AccountingForm.tsx
│   │   │   │   │   ├── InvoiceList.tsx
│   │   │   │   │   ├── InventoryTable.tsx
│   │   │   │   │   └── ... (components for each module)
│   │   │   │
│   │   │   ├── modules/                     # Module-specific logic
│   │   │   │   ├── accounting/
│   │   │   │   │   ├── AccountList.tsx
│   │   │   │   │   ├── JournalEntryForm.tsx
│   │   │   │   │   └── ...
│   │   │   │   ├── invoicing/
│   │   │   │   ├── inventory/
│   │   │   │   └── ... (all 13 modules)
│   │   │   │
│   │   │   ├── views/                       # View renderers (Form, List, Kanban, Pivot)
│   │   │   │   ├── FormView.tsx
│   │   │   │   ├── ListView.tsx
│   │   │   │   ├── KanbanView.tsx
│   │   │   │   ├── PivotView.tsx
│   │   │   │   └── GraphView.tsx
│   │   │   │
│   │   │   ├── hooks/
│   │   │   │   ├── useAuth.ts
│   │   │   │   ├── useCompany.ts
│   │   │   │   ├── useAPI.ts                # Axios wrapper for DRF API
│   │   │   │   ├── useModuleConfig.ts       # Get industry-specific config
│   │   │   │   └── useNotifications.ts
│   │   │   │
│   │   │   ├── theme/
│   │   │   │   ├── colors.ts                # Brand colors per industry
│   │   │   │   ├── globals.css
│   │   │   │   └── odoo-theme.css
│   │   │   │
│   │   │   ├── api/
│   │   │   │   ├── client.ts                # Axios instance with auth
│   │   │   │   ├── endpoints.ts             # API endpoint definitions
│   │   │   │   └── types.ts                 # TypeScript types for all models
│   │   │   │
│   │   │   ├── App.tsx                      # Main app component
│   │   │   ├── main.tsx                     # Entry point
│   │   │   └── index.css
│   │   │
│   │   ├── public/
│   │   │   └── index.html
│   │   │
│   │   ├── package.json
│   │   ├── vite.config.ts
│   │   ├── tsconfig.json
│   │   ├── Dockerfile
│   │   └── .env.example
│   │
│   └── docker-compose.yml                   # Full stack orchestration
│
├── industries/                              # Industry-Specific Implementations
│   ├── novapay/
│   │   ├── frontend/                        # NovaPay React app (variant of core)
│   │   │   ├── src/
│   │   │   │   ├── App.tsx                  # Override theme, navigation
│   │   │   │   └── theme/
│   │   │   │       └── colors.ts            # #2563EB blue
│   │   │   ├── package.json
│   │   │   ├── vite.config.ts
│   │   │   └── Dockerfile
│   │   │
│   │   └── management/
│   │       └── commands/
│   │           └── seed_novapay_data.py     # 50+ merchants, 100+ invoices
│   │
│   ├── medvista/
│   │   ├── frontend/
│   │   │   ├── src/
│   │   │   │   ├── App.tsx
│   │   │   │   └── theme/
│   │   │   │       └── colors.ts            # #059669 green
│   │   │   ├── package.json
│   │   │   ├── vite.config.ts
│   │   │   └── Dockerfile
│   │   │
│   │   └── management/
│   │       └── commands/
│   │           └── seed_medvista_data.py    # 50+ patients, appointments, lab results
│   │
│   ├── trustguard/
│   │   ├── frontend/
│   │   └── management/
│   │       └── commands/
│   │           └── seed_trustguard_data.py
│   │
│   ├── urbannest/
│   │   ├── frontend/
│   │   └── management/
│   │
│   ├── swiftroute/
│   │   ├── frontend/
│   │   └── management/
│   │
│   ├── dentaflow/
│   │   ├── frontend/
│   │   └── management/
│   │
│   ├── jurispath/
│   │   ├── frontend/
│   │   └── management/
│   │
│   ├── tablesync/
│   │   ├── frontend/
│   │   └── management/
│   │
│   ├── cranestack/
│   │   ├── frontend/
│   │   └── management/
│   │
│   ├── edupulse/
│   │   ├── frontend/
│   │   └── management/
│   │
│   ├── industry_config.py                   # Shared industry configuration logic
│   └── base_agent_tasks.py                  # Common tasks for all industry agents
│
└── plans/
    ├── ERP-MASTER-PLAN.md                   # This file
    ├── MODULE-DETAILS.md                    # Detailed module specifications
    ├── API-SPECIFICATION.md                 # OpenAPI/Swagger specs
    ├── DEPLOYMENT-GUIDE.md                  # Docker & local dev setup
    ├── DATABASE-SCHEMA.md                   # Full SQL schema with indexes
    ├── INDUSTRY-CUSTOMIZATION-GUIDE.md      # How to add new industries
    └── TESTING-STRATEGY.md                  # Unit, integration, E2E test plan
```

---

## 8. NAMING CONVENTIONS & CODE STANDARDS

### 8.1 Python/Django Conventions

**Models:** PascalCase (Django convention)
```python
class AccountAccount(models.Model):
    pass

class InvoicingInvoice(models.Model):
    pass

class InventoryProduct(models.Model):
    pass
```

**Database Tables:** snake_case (auto-generated by Django from models)
```
accounting_account
invoicing_invoice
inventory_product
```

**Functions/Methods:** snake_case (PEP 8)
```python
def get_module_config(company_id, module_id, key):
    pass

def create_demo_data(company):
    pass

def validate_invoice_state_transition(invoice, next_state):
    pass
```

**Constants:** UPPER_SNAKE_CASE
```python
INVOICE_STATES = ['draft', 'posted', 'sent', 'accepted', 'cancelled']
DEFAULT_TAX_RATE = Decimal('8.5')
MODULE_ACCOUNTING = 'accounting'
```

**Formatting:** Black, isort, flake8
```bash
black ./core/backend
isort ./core/backend
flake8 ./core/backend
```

### 8.2 React/TypeScript Conventions

**Components:** PascalCase
```typescript
export function InvoiceForm() { ... }
export function InventoryLocations() { ... }
export function DashboardCard() { ... }
```

**Hooks:** camelCase with `use` prefix
```typescript
function useAuth() { ... }
function useModuleConfig(module: string, key: string) { ... }
function useAPI() { ... }
```

**Types/Interfaces:** PascalCase
```typescript
interface Invoice {
  id: number;
  number: string;
  amount_total: number;
}

type InvoiceState = 'draft' | 'posted' | 'cancelled';
```

**Constants:** UPPER_SNAKE_CASE
```typescript
const API_BASE_URL = process.env.VITE_API_URL;
const MAX_FILE_SIZE_MB = 10;
```

**Formatting:** Prettier, ESLint
```bash
npx prettier --write ./core/frontend/src
npx eslint ./core/frontend/src --fix
```

### 8.3 API Conventions (Django REST Framework)

**Endpoints:** kebab-case with REST verbs
```
GET    /api/v1/accounting/accounts/
POST   /api/v1/accounting/accounts/
GET    /api/v1/accounting/accounts/{id}/
PATCH  /api/v1/accounting/accounts/{id}/
POST   /api/v1/accounting/accounts/{id}/post/          # Custom action
POST   /api/v1/accounting/bank-statements/{id}/reconcile/
```

**Response Format (JSON):**
```json
{
  "id": 123,
  "company_id": 1,
  "number": "INV/2026/0001",
  "invoice_type": "out_invoice",
  "partner_id": 456,
  "invoice_date": "2026-04-02",
  "due_date": "2026-05-02",
  "amount_untaxed": 1000.00,
  "amount_tax": 85.00,
  "amount_total": 1085.00,
  "state": "draft",
  "created_at": "2026-04-02T10:30:00Z",
  "updated_at": "2026-04-02T10:30:00Z"
}
```

---

## 9. DEPLOYMENT & ENVIRONMENT SETUP

### 9.1 Local Development with Docker Compose

**Prerequisites:**
- Docker & Docker Compose (v2.0+)
- Git
- (Optional) Python 3.12 for IDE/linting

**Setup:**
```bash
# Clone repository
git clone https://github.com/company/14-erp-platform.git
cd 14-ERP-Platform

# Copy environment files
cp core/backend/.env.example core/backend/.env
cp core/frontend/.env.example core/frontend/.env

# Build and start services
docker-compose up --build

# Wait for Django to be ready
docker-compose exec django_api python manage.py migrate
docker-compose exec django_api python manage.py create_demo_data

# Access application
# Core ERP: http://localhost:14500
# NovaPay: http://localhost:14001
# MedVista: http://localhost:14002
# ... etc
```

### 9.2 Environment Variables

**core/backend/.env:**
```
DEBUG=False
SECRET_KEY=your-secret-key-here-change-in-production
DATABASE_URL=postgresql://erp_user:password@postgres:5432/erp_platform
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:14500,http://localhost:14001,http://localhost:14002
DJANGO_SETTINGS_MODULE=config.settings
```

**core/frontend/.env:**
```
VITE_API_URL=http://localhost:14000
VITE_API_TIMEOUT=30000
```

---

## 10. QUALITY ASSURANCE & TESTING

### 10.1 Testing Strategy

**Unit Tests (pytest + factory_boy):**
- Test each model's validation logic, custom methods
- Test serializers (input validation, transformation)
- Test business logic functions (accounting journal entry posting, invoice state transitions)

**Integration Tests:**
- Test API endpoints with various user roles and permissions
- Test multi-tenant filtering (company_id isolation)
- Test module configuration overrides
- Test signals (audit logging, cascade deletes)

**E2E Tests (Cypress or Playwright):**
- Test complete workflows: login → invoice creation → posting → reporting
- Test UI across industries to ensure theme/terminology changes work
- Test permission-based visibility

**Code Quality Tools:**
```bash
# Python
pytest ./core/backend --cov=core/backend
mypy ./core/backend --strict
black --check ./core/backend
flake8 ./core/backend
pylint ./core/backend

# React/TypeScript
npm run test
npm run lint
npm run type-check
```

### 10.2 Demo Data Validation

Before release, verify each industry has:
- 50-100 records per main entity
- Realistic workflows (e.g., draft → posted → sent for invoices)
- Proper relationships (customer → invoices → payments → accounting entries)
- Industry-specific terminology applied (e.g., "Supply Room" for DentaFlow inventory)

---

## 11. FUTURE ENHANCEMENTS (Post-MVP)

1. **Industry-Specific Mobile Apps** (React Native) for each company
2. **Advanced Reporting & BI** (integration with Metabase or custom dashboards)
3. **AI/ML Features** (predictive analytics, anomaly detection in financial data)
4. **Third-Party Integrations** (Shopify, Stripe, Quickbooks sync via webhooks)
5. **Workflow Automation** (business rules engine for approvals, state transitions)
6. **Advanced Permissions** (field-level security, row-level security)
7. **Data Export/Import** (CSV, Excel, EDI support)
8. **Audit Trail Visualization** (timeline view of all changes to a record)
9. **Blockchain/Immutable Ledger** (for healthcare/legal/financial use cases)
10. **Industry-Specific KPI Dashboards** (finance, operations, HR metrics per industry)

---

## 12. SUCCESS METRICS & KPIs

**Development Metrics:**
- All 13 modules fully implemented with CRUD operations
- 10 industries with demo data (50-100 records each)
- 95%+ test coverage
- Zero critical security vulnerabilities (OWASP top 10)

**Performance Metrics:**
- API response time < 200ms (p95)
- Page load time < 2s (p95)
- Concurrent users supported: 100+ via Docker Compose
- Database query time < 100ms (p95)

**User Experience Metrics:**
- Consistent UI/UX across all industries
- Theme/terminology customization working per company
- Accessibility score (WCAG 2.1 AA) >= 90

---

## 13. GLOSSARY & KEY TERMS

- **ERP**: Enterprise Resource Planning — integrated software for business operations
- **Module**: Self-contained feature area (Accounting, Invoicing, etc.)
- **Company/Tenant**: An industry instance (NovaPay, MedVista, etc.)
- **Module Configuration**: Industry-specific overrides (terminology, workflow defaults)
- **Odoo-Style**: Purple/white theme, sidebar navigation, form/list/kanban views
- **Multi-Tenancy**: Single database serves multiple companies with row-level isolation
- **DRF**: Django REST Framework — REST API framework for Django
- **ViewSet**: DRF class providing CRUD endpoints for a model
- **Serializer**: DRF class for input validation and JSON transformation
- **Signal**: Django hook for events (pre_save, post_save, pre_delete)
- **Audit Log**: Record of who changed what and when
- **Celery**: Task queue for async operations
- **Channels**: Django extension for WebSocket support

---

**END OF ERP MASTER PLAN**

---

*Document Maintained by: ERP Core Platform Agent*
*Last Review: 2026-04-02*
*Next Review Scheduled: 2026-05-02*
