import { Routes, Route } from "react-router-dom";

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

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="*" element={<NotFound />} />
    </Routes>
  );
}
