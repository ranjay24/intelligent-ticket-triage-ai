import { useAuth } from "react-oidc-context";
import {
  Quote,
  ArrowRight,
  ShieldCheck,
  Loader2,
} from "lucide-react";

function Login() {
  const auth = useAuth();

  const redirecting =
    auth.isLoading || auth.activeNavigator === "signinRedirect";

  return (
    <div className="min-h-screen grid lg:grid-cols-2 bg-slate-50">

      {/* ---- Brand panel (desktop only) ---- */}
      <div className="hidden lg:flex relative flex-col justify-between overflow-hidden bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-white p-12">

        {/* ambient gradient orbs */}
        <div className="pointer-events-none absolute -top-24 -left-24 w-96 h-96 rounded-full bg-indigo-600/30 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-32 -right-16 w-96 h-96 rounded-full bg-cyan-500/20 blur-3xl" />

        {/* logo */}
        <div className="relative flex items-center gap-2">
          <div className="w-9 h-9 rounded-lg bg-blue-600 flex items-center justify-center font-bold">
            AI
          </div>
          <span className="font-semibold text-lg">TicketTriage</span>
        </div>

        {/* pull-quote — the hero */}
        <div className="relative max-w-lg">
          <Quote
            size={56}
            className="text-cyan-300/40 mb-4 -ml-1"
            strokeWidth={1.5}
          />

          <blockquote className="text-4xl font-bold leading-snug tracking-tight">
            The best support ticket is{" "}
            <span className="bg-gradient-to-r from-cyan-300 to-indigo-300 bg-clip-text text-transparent">
               the one your customer never
            </span>{" "}
            has to chase..
          </blockquote>

          <p className="mt-8 text-sm text-slate-400 tracking-wide uppercase">
            The principle behind TicketTriage
          </p>
        </div>

        {/* footer note grounded in the real safety design */}
        <div className="relative flex items-center gap-2 text-sm text-slate-400">
          <ShieldCheck size={16} className="text-emerald-400" />
          A human approves every refund, password reset, and critical issue.
        </div>
      </div>

      {/* ---- Sign-in panel ---- */}
      <div className="flex items-center justify-center p-6">
        <div className="w-full max-w-sm">

          {/* logo (shown on mobile, where the brand panel is hidden) */}
          <div className="flex items-center gap-2 mb-10 lg:hidden">
            <div className="w-9 h-9 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold">
              AI
            </div>
            <span className="font-semibold text-lg text-slate-900">
              TicketTriage
            </span>
          </div>

          <h2 className="text-2xl font-bold text-slate-900">Sign in</h2>
          <p className="text-slate-500 mt-2">
            Use your organization account to continue.
          </p>

          {auth.error && (
            <div className="mt-6 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg px-4 py-3">
              Couldn't start sign-in. Please try again.
            </div>
          )}

          <button
            onClick={() => auth.signinRedirect()}
            disabled={redirecting}
            className="mt-8 w-full flex items-center justify-center gap-2 bg-blue-600 hover:bg-blue-700 disabled:opacity-60 text-white font-medium px-5 py-3 rounded-xl transition focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
          >
            {redirecting ? (
              <>
                <Loader2 size={18} className="animate-spin" />
                Redirecting…
              </>
            ) : (
              <>
                Continue with Cognito
                <ArrowRight size={18} />
              </>
            )}
          </button>

          <p className="mt-6 text-xs text-slate-400 text-center">
            Secured by AWS Cognito. You'll be redirected to sign in.
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;
