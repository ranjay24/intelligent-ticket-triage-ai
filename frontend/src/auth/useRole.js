import { useAuth } from "react-oidc-context";

export default function useRole() {
  const auth = useAuth();

  const groups =
    auth.user?.profile?.["cognito:groups"] || [];

  const isAdmin = groups.includes("Admins");

  return {
    groups,
    isAdmin,
  };
}