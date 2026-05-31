import { Navigate, Route, Routes } from "react-router-dom";
import { useAuthStore } from "./stores/authStore";

import AppShell from "./components/AppShell";
import Login from "./pages/Login";
import Signup from "./pages/Signup";
import Dashboard from "./pages/Dashboard";
import Discovery from "./pages/Discovery";
import Listings from "./pages/Listings";
import Orders from "./pages/Orders";
import Stores from "./pages/Stores";
import SettingsPage from "./pages/Settings";

function RequireAuth({ children }: { children: JSX.Element }) {
  const token = useAuthStore((s) => s.accessToken);
  if (!token) return <Navigate to="/login" replace />;
  return children;
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />
      <Route
        path="/"
        element={
          <RequireAuth>
            <AppShell />
          </RequireAuth>
        }
      >
        <Route index element={<Navigate to="/discovery" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="discovery" element={<Discovery />} />
        <Route path="listings" element={<Listings />} />
        <Route path="orders" element={<Orders />} />
        <Route path="stores" element={<Stores />} />
        <Route path="settings" element={<SettingsPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
