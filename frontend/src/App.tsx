import { Routes, Route, Navigate, Outlet } from "react-router-dom";
import AppLayout from "./components/AppLayout";
import LoginPage from "./pages/LoginPage";
import EmployeeListPage from "./pages/hr/EmployeeListPage";
import EmployeeFormPage from "./pages/hr/EmployeeFormPage";
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
      </Route>
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
