import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Navbar from "./components/Navbar";

import Dashboard from "./pages/Dashboard";
import Tickets from "./pages/Tickets";
import Reviews from "./pages/Reviews";
import Analytics from "./pages/Analytics";
import TicketDetails from "./pages/TicketDetails";
import CreateTicket from "./pages/CreateTicket";
import Login from "./pages/Login";
import CustomerHome from "./pages/CustomerHome";

import ProtectedRoute from "./auth/ProtectedRoute";
import AdminRoute from "./auth/AdminRoute";
import useRole from "./auth/useRole";

function HomeRedirect() {
  const { isAdmin } = useRole();

  if (isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <Navigate to="/customer" replace />;
}

function App() {
  return (
    <BrowserRouter>
      <div className="flex flex-col min-h-screen bg-slate-50">
        <Routes>
          <Route path="/login" element={<Login />} />

          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <>
                  <Navbar />

                  <main className="flex-1">
                    <Routes>
                      <Route path="/" element={<HomeRedirect />} />

                      <Route
                        path="/dashboard"
                        element={
                          <AdminRoute>
                            <Dashboard />
                          </AdminRoute>
                        }
                      />

                      <Route path="/customer" element={<CustomerHome />} />

                      <Route path="/create-ticket" element={<CreateTicket />} />

                      <Route path="/my-tickets" element={<Tickets />} />
                      <Route
                        path="/tickets"
                        element={
                          <AdminRoute>
                            <Tickets />
                          </AdminRoute>
                        }
                      />

                      <Route
                        path="/tickets/:ticketId"
                        element={<TicketDetails />}
                      />

                      <Route
                        path="/reviews"
                        element={
                          <AdminRoute>
                            <Reviews />
                          </AdminRoute>
                        }
                      />

                      <Route
                        path="/analytics"
                        element={
                          <AdminRoute>
                            <Analytics />
                          </AdminRoute>
                        }
                      />
                    </Routes>
                  </main>
                </>
              </ProtectedRoute>
            }
          />
        </Routes>
      </div>
    </BrowserRouter>
  );
}

export default App;
