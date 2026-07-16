import { Link } from "react-router-dom";
import { useAuth } from "react-oidc-context";

import {
  PlusCircle,
  Ticket,
  ClipboardCheck,
  BarChart3,
  ArrowRight,
} from "lucide-react";

function QuickActions() {

  const auth = useAuth();

  const isAdmin =
    auth.user?.profile?.["cognito:groups"]?.includes("Admins");

  const actions = [];

  if (isAdmin) {

    actions.push(
      {
        title: "All Tickets",
        description: "Browse every ticket.",
        icon: <Ticket size={28} />,
        to: "/tickets",
        color: "from-emerald-500 to-green-600",
      },
      {
        title: "Pending Reviews",
        description: "Approve or reject AI responses.",
        icon: <ClipboardCheck size={28} />,
        to: "/reviews",
        color: "from-amber-500 to-orange-600",
      },
      {
        title: "Analytics",
        description: "View AI insights & metrics.",
        icon: <BarChart3 size={28} />,
        to: "/analytics",
        color: "from-purple-500 to-fuchsia-600",
      }
    );

  } else {

    actions.push(
      {
        title: "Create Ticket",
        description: "Submit a new customer support request.",
        icon: <PlusCircle size={28} />,
        to: "/create-ticket",
        color: "from-blue-500 to-indigo-600",
      },
      {
        title: "My Tickets",
        description: "View your submitted tickets.",
        icon: <Ticket size={28} />,
        to: "/my-tickets",
        color: "from-emerald-500 to-green-600",
      }
    );

  }

  return (

    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">

      <div className="mb-6">

        <p className="text-xs uppercase tracking-widest text-slate-400 font-semibold">

          Navigation

        </p>

        <h2 className="text-xl font-bold text-slate-800 mt-1">

          Quick Actions

        </h2>

      </div>

      <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-5">

        {actions.map((action) => (

          <Link

            key={action.title}

            to={action.to}

            className="group"

          >

            <div className="relative overflow-hidden rounded-2xl bg-white border border-slate-200 hover:border-transparent transition-all duration-300 hover:shadow-xl">

              <div
                className={`absolute inset-0 bg-gradient-to-r ${action.color} opacity-0 group-hover:opacity-100 transition`}
              />

              <div className="relative p-6">

                <div className="w-14 h-14 rounded-xl bg-slate-100 group-hover:bg-white/20 flex items-center justify-center mb-5 transition">

                  <div className="text-slate-700 group-hover:text-white">

                    {action.icon}

                  </div>

                </div>

                <h3 className="font-bold text-lg text-slate-800 group-hover:text-white">

                  {action.title}

                </h3>

                <p className="text-sm text-slate-500 mt-2 group-hover:text-slate-100">

                  {action.description}

                </p>

                <div className="mt-6 flex items-center gap-2 text-blue-600 font-semibold group-hover:text-white">

                  Open

                  <ArrowRight
                    size={18}
                    className="group-hover:translate-x-1 transition"
                  />

                </div>

              </div>

            </div>

          </Link>

        ))}

      </div>

    </div>

  );

}

export default QuickActions;