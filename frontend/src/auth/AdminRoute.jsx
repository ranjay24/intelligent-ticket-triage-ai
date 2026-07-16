import { Navigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import useRole from "./useRole";

function AdminRoute({ children }) {

  const auth = useAuth();

  const { isAdmin } = useRole();

  if (auth.isLoading) {

    return <div>Loading...</div>;

  }

  if (!auth.isAuthenticated) {

    return <Navigate to="/login" replace />;

  }

  if (!isAdmin) {

    return <Navigate to="/customer" replace />;

  }

  return children;

}

export default AdminRoute;