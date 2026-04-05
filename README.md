# ERP Platform

Modular multi-tenant Enterprise Resource Planning system with 13 core modules serving 10 industries. Unified architecture where modules adapt to industry-specific workflows through configuration — no code duplication.

[![Django 5.x](https://img.shields.io/badge/Django-5.x-092E20?logo=django&logoColor=white)](https://djangoproject.com/)
[![React 18](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://reactjs.org/)
[![PostgreSQL 15+](https://img.shields.io/badge/PostgreSQL-15+-4169E1?logo=postgresql&logoColor=white)](https://postgresql.org/)
[![Celery](https://img.shields.io/badge/Celery-5.x-37814A?logo=celery&logoColor=white)](https://docs.celeryq.dev/)

## 13 Core Modules

| Module | Description |
|--------|-------------|
| Accounting | Chart of accounts, journal entries, financial reporting |
| Invoicing | Customer invoices, vendor bills, recurring invoices |
| Inventory | Products, stock locations, reorder rules |
| Fleet | Vehicles, maintenance, fuel tracking, drivers |
| Calendar | Appointments, resource booking, shift planning |
| HR | Payroll, leave management, attendance, timesheets |
| Projects | Tasks, milestones, timesheets, Gantt charts |
| Purchasing | POs, RFQs, vendor management, receiving |
| Sales | Quotations, sales orders, pipeline, pricelists |
| Manufacturing | Bills of materials, work orders, production costs |
| Point of Sale | Touch-screen terminals, cash management |
| Helpdesk | Support tickets, SLA tracking, knowledge base |
| Reports/BI | Pivot tables, custom reports, scheduled exports |

## 10 Industry Verticals

| Company | Sector | Color | Port |
|---------|--------|-------|------|
| NovaPay | FinTech | #2563EB | 14001 |
| MedVista | Healthcare | #059669 | 14002 |
| TrustGuard | Insurance | #1E3A5F | 14003 |
| UrbanNest | Real Estate | #D97706 | 14004 |
| SwiftRoute | Logistics | #7C3AED | 14005 |
| DentaFlow | Dental | #06B6D4 | 14006 |
| JurisPath | Legal | #166534 | 14007 |
| TableSync | Hospitality | #9F1239 | 14008 |
| CraneStack | Construction | #EA580C | 14009 |
| EduPulse | Education | #6D28D9 | 14010 |

## Stack

| Component | Technology |
|-----------|-----------|
| Frontend | React 18 + TypeScript + Vite |
| Backend | Django 5.x + Django REST Framework 3.15+ |
| Database | PostgreSQL 15+ |
| Async Tasks | Celery 5.x + Redis |
| Real-Time | Django Channels (WebSocket) |
| Deployment | Docker Compose |

## Design Language

Purple/white base theme (#7C3AED) with industry-specific brand color accents in navigation. Consistent layout across all verticals: top navbar, left sidebar, main content area. Responsive and mobile-friendly.

## Quick Start

```bash
docker-compose up -d
```

## Status

Pre-development — Master plan and architecture finalized.

## License

Private
