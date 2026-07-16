import { Navigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { useEffect } from "react";

function ProtectedRoute({ children }) {
  const auth = useAuth();

  useEffect(() => {
    if (auth.isAuthenticated && auth.user?.profile?.email) {
      localStorage.setItem(
        "customerEmail",
        auth.user.profile.email
      );
    }
  }, [auth.isAuthenticated, auth.user]);

  if (auth.isLoading) {
    return <div>Loading...</div>;
  }

  if (!auth.isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

export default ProtectedRoute;
