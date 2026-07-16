import { AuthProvider } from "react-oidc-context";

// Derive the redirect from wherever the app is actually served, so
// login works locally (http://localhost:5173) AND when deployed,
// without hardcoding one URL. An env var can still override it.
// NOTE: every origin you use (localhost + your deployed URL) must be
// listed as an Allowed callback / sign-out URL on the Cognito app client.
const redirectUri =
  import.meta.env.VITE_REDIRECT_URI || window.location.origin;

const cognitoAuthConfig = {
  authority:
    "https://cognito-idp.ap-south-1.amazonaws.com/ap-south-1_OrOyKyyij",

  client_id:
    "291fmj2slhpug74eq64e0k9vdb",

  redirect_uri: redirectUri,

  post_logout_redirect_uri: redirectUri,

  response_type: "code",

  scope: "openid email",
};

export default function CognitoProvider({ children }) {
  return (
    <AuthProvider {...cognitoAuthConfig}>
      {children}
    </AuthProvider>
  );
}
