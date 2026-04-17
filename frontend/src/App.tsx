import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import LoginPage from "./pages/LoginPage";
import EmployeeListPage from "./pages/hr/EmployeeListPage";
import EmployeeFormPage from "./pages/hr/EmployeeFormPage";
import EventListPage from "./pages/calendar/EventListPage";
import EventFormPage from "./pages/calendar/EventFormPage";
import ProductListPage from "./pages/inventory/ProductListPage";
import ProductFormPage from "./pages/inventory/ProductFormPage";
import VendorListPage from "./pages/purchasing/VendorListPage";
import PurchaseOrderListPage from "./pages/purchasing/PurchaseOrderListPage";
import PurchaseOrderFormPage from "./pages/purchasing/PurchaseOrderFormPage";
import QuotationListPage from "./pages/sales/QuotationListPage";
import QuotationFormPage from "./pages/sales/QuotationFormPage";
import SalesOrderListPage from "./pages/sales/SalesOrderListPage";
import SalesOrderFormPage from "./pages/sales/SalesOrderFormPage";
import AccountListPage from "./pages/accounting/AccountListPage";
import JournalEntryListPage from "./pages/accounting/JournalEntryListPage";
import JournalEntryFormPage from "./pages/accounting/JournalEntryFormPage";
import InvoiceListPage from "./pages/invoicing/InvoiceListPage";
import InvoiceFormPage from "./pages/invoicing/InvoiceFormPage";
import PartnerListPage from "./pages/partners/PartnerListPage";
import PartnerFormPage from "./pages/partners/PartnerFormPage";
import VehicleListPage from "./pages/fleet/VehicleListPage";
import VehicleFormPage from "./pages/fleet/VehicleFormPage";
import DriverListPage from "./pages/fleet/DriverListPage";
import DriverFormPage from "./pages/fleet/DriverFormPage";
import MaintenanceLogListPage from "./pages/fleet/MaintenanceLogListPage";
import FuelLogListPage from "./pages/fleet/FuelLogListPage";
import ProjectListPage from "./pages/projects/ProjectListPage";
import ProjectFormPage from "./pages/projects/ProjectFormPage";
import TaskListPage from "./pages/projects/TaskListPage";
import MilestoneListPage from "./pages/projects/MilestoneListPage";
import { useAuthStore } from "./stores/authStore";

function Home() {
  return (
    <div>
      <h1>ERP Platform</h1>
      <p>Welcome to the ERP Platform.</p>
    </div>
  );
}

function NotFound() {
  return (
    <div>
      <h1>404</h1>
      <p>Page not found.</p>
    </div>
  );
}

function ProtectedRoute() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return <AppLayout />;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<Home />} />
        <Route path="/hr/employees" element={<EmployeeListPage />} />
        <Route path="/hr/employees/new" element={<EmployeeFormPage />} />
        <Route path="/hr/employees/:id/edit" element={<EmployeeFormPage />} />
        <Route path="/calendar/events" element={<EventListPage />} />
        <Route path="/calendar/events/new" element={<EventFormPage />} />
        <Route path="/calendar/events/:id/edit" element={<EventFormPage />} />
        <Route path="/inventory/products" element={<ProductListPage />} />
        <Route path="/inventory/products/new" element={<ProductFormPage />} />
        <Route path="/inventory/products/:id/edit" element={<ProductFormPage />} />
        <Route path="/purchasing/vendors" element={<VendorListPage />} />
        <Route path="/purchasing/purchase-orders" element={<PurchaseOrderListPage />} />
        <Route
          path="/purchasing/purchase-orders/new"
          element={<PurchaseOrderFormPage />}
        />
        <Route
          path="/purchasing/purchase-orders/:id/edit"
          element={<PurchaseOrderFormPage />}
        />
        <Route path="/sales/quotations" element={<QuotationListPage />} />
        <Route path="/sales/quotations/new" element={<QuotationFormPage />} />
        <Route path="/sales/quotations/:id/edit" element={<QuotationFormPage />} />
        <Route path="/sales/orders" element={<SalesOrderListPage />} />
        <Route path="/sales/orders/new" element={<SalesOrderFormPage />} />
        <Route path="/sales/orders/:id/edit" element={<SalesOrderFormPage />} />
        <Route path="/accounting/accounts" element={<AccountListPage />} />
        <Route path="/accounting/entries" element={<JournalEntryListPage />} />
        <Route path="/accounting/entries/new" element={<JournalEntryFormPage />} />
        <Route path="/accounting/entries/:id/edit" element={<JournalEntryFormPage />} />
        <Route path="/invoicing/invoices" element={<InvoiceListPage />} />
        <Route path="/invoicing/invoices/new" element={<InvoiceFormPage />} />
        <Route path="/invoicing/invoices/:id/edit" element={<InvoiceFormPage />} />
        <Route path="/partners" element={<PartnerListPage />} />
        <Route path="/partners/new" element={<PartnerFormPage />} />
        <Route path="/partners/:id/edit" element={<PartnerFormPage />} />
        <Route path="/fleet/vehicles" element={<VehicleListPage />} />
        <Route path="/fleet/vehicles/new" element={<VehicleFormPage />} />
        <Route path="/fleet/vehicles/:id/edit" element={<VehicleFormPage />} />
        <Route path="/fleet/drivers" element={<DriverListPage />} />
        <Route path="/fleet/drivers/new" element={<DriverFormPage />} />
        <Route path="/fleet/drivers/:id/edit" element={<DriverFormPage />} />
        <Route path="/fleet/maintenance-logs" element={<MaintenanceLogListPage />} />
        <Route path="/fleet/fuel-logs" element={<FuelLogListPage />} />
        <Route path="/projects/projects" element={<ProjectListPage />} />
        <Route path="/projects/projects/new" element={<ProjectFormPage />} />
        <Route path="/projects/projects/:id/edit" element={<ProjectFormPage />} />
        <Route path="/projects/tasks" element={<TaskListPage />} />
        <Route path="/projects/milestones" element={<MilestoneListPage />} />
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
