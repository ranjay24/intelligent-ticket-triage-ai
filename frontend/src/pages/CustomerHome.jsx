import { Link } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import {
  PlusCircle,
  FolderOpen,
  ArrowRight,
  Clock,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

function greeting() {
  const h = new Date().getHours();
  if (h < 12) return "Good morning";
  if (h < 18) return "Good afternoon";
  return "Good evening";
}

function firstName(email = "") {
  const local = email.split("@")[0] || "";
  if (!local) return "";
  return local.charAt(0).toUpperCase() + local.slice(1);
}

function CustomerHome() {
  const auth = useAuth();
  const email = auth.user?.profile?.email || "";
  const name = firstName(email);

  return (
    <div className="max-w-5xl mx-auto px-6 py-10">

      {/* ---- Hero ---- */}
      <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-indigo-950 to-slate-900 text-white p-10">

        <div className="pointer-events-none absolute -top-20 -right-16 w-80 h-80 rounded-full bg-cyan-500/20 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-24 -left-16 w-80 h-80 rounded-full bg-indigo-600/25 blur-3xl" />

        <p className="relative text-xs uppercase tracking-widest text-indigo-200">
          Support portal
        </p>

        <h1 className="relative text-3xl font-bold mt-3">
          {greeting()}
          {name ? `, ${name}` : ""}.
        </h1>

        <p className="relative text-slate-300 mt-3 max-w-md">
          Submit a request and get an AI-drafted reply in seconds. Anything
          sensitive is reviewed by a person before it reaches you.
        </p>

        {email && (
          <p className="relative text-sm text-slate-400 mt-6">
            Signed in as {email}
          </p>
        )}
      </div>

      {/* ---- Actions ---- */}
      <div className="grid md:grid-cols-2 gap-6 mt-8">

        <Link
          to="/create-ticket"
          className="group bg-white rounded-2xl border border-slate-200 p-7 hover:border-blue-300 hover:shadow-lg transition"
        >
          <div className="w-12 h-12 rounded-xl bg-blue-50 text-blue-600 flex items-center justify-center">
            <PlusCircle size={26} />
          </div>

          <h2 className="text-lg font-semibold text-slate-900 mt-5">
            Create a ticket
          </h2>

          <p className="text-slate-500 mt-2 text-sm">
            Describe your issue and let AI handle the first response.
          </p>

          <div className="mt-5 flex items-center gap-2 text-blue-600 font-medium text-sm">
            Start now
            <ArrowRight
              size={16}
              className="group-hover:translate-x-1 transition"
            />
          </div>
        </Link>

        <Link
          to="/my-tickets"
          className="group bg-white rounded-2xl border border-slate-200 p-7 hover:border-emerald-300 hover:shadow-lg transition"
        >
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center">
            <FolderOpen size={26} />
          </div>

          <h2 className="text-lg font-semibold text-slate-900 mt-5">
            My tickets
          </h2>

          <p className="text-slate-500 mt-2 text-sm">
            Track the status and replies on everything you've submitted.
          </p>

          <div className="mt-5 flex items-center gap-2 text-emerald-600 font-medium text-sm">
            View tickets
            <ArrowRight
              size={16}
              className="group-hover:translate-x-1 transition"
            />
          </div>
        </Link>
      </div>

      {/* ---- Reassurance row ---- */}
      <div className="grid sm:grid-cols-3 gap-4 mt-8">

        <div className="flex items-start gap-3 bg-white rounded-xl border border-slate-200 p-5">
          <Clock size={20} className="text-blue-600 mt-0.5" />
          <div>
            <p className="font-medium text-slate-800 text-sm">Fast first reply</p>
            <p className="text-xs text-slate-500 mt-1">
              Drafted automatically in seconds.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 bg-white rounded-xl border border-slate-200 p-5">
          <Sparkles size={20} className="text-indigo-600 mt-0.5" />
          <div>
            <p className="font-medium text-slate-800 text-sm">Smart routing</p>
            <p className="text-xs text-slate-500 mt-1">
              Categorized and prioritized for you.
            </p>
          </div>
        </div>

        <div className="flex items-start gap-3 bg-white rounded-xl border border-slate-200 p-5">
          <ShieldCheck size={20} className="text-emerald-600 mt-0.5" />
          <div>
            <p className="font-medium text-slate-800 text-sm">Human-checked</p>
            <p className="text-xs text-slate-500 mt-1">
              Sensitive requests reviewed by a person.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default CustomerHome;
