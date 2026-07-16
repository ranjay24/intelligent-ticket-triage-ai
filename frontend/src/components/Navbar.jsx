import { NavLink } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import useRole from "../auth/useRole";

const COGNITO_DOMAIN =
  "https://ap-south-1oroykyyij.auth.ap-south-1.amazoncognito.com";

const CLIENT_ID = "291fmj2slhpug74eq64e0k9vdb";

function Navbar() {

  const auth = useAuth();

  const { isAdmin } = useRole();

  const logout = () => {

    auth.removeUser();

    localStorage.removeItem("customerEmail");

    // Derive the sign-out target from wherever the app is served, so
    // logout works locally AND when deployed. This origin must be
    // listed as an Allowed sign-out URL on the Cognito app client.
    const logoutUri = window.location.origin;

    window.location.href =
      `${COGNITO_DOMAIN}/logout` +
      `?client_id=${CLIENT_ID}` +
      `&logout_uri=${encodeURIComponent(logoutUri)}`;

  };

  const navItems = isAdmin

    ? [

        {
          to: "/dashboard",
          label: "Dashboard",
          icon: "⊞",
          exact: true,
        },

        {
          to: "/tickets",
          label: "All Tickets",
          icon: "🎫",
        },

        {
          to: "/reviews",
          label: "Reviews",
          icon: "🔍",
        },

        {
          to: "/analytics",
          label: "Analytics",
          icon: "📊",
        },

      ]

    : [

        {
          to: "/customer",
          label: "Home",
          icon: "🏠",
          exact: true,
        },

        {
          to: "/my-tickets",
          label: "My Tickets",
          icon: "🎫",
        },

        {
          to: "/create-ticket",
          label: "New Ticket",
          icon: "➕",
        },

      ];

  return (

    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50">

      <div className="max-w-screen-xl mx-auto px-6 h-14 flex items-center justify-between">

        {/* Logo */}

        <div className="flex items-center gap-2">

          <div className="w-8 h-8 rounded-lg bg-blue-600 text-white flex items-center justify-center font-bold">

            AI

          </div>

          <span className="text-white font-semibold">

            TicketTriage

          </span>

        </div>

        {/* Navigation */}

        <nav className="flex items-center gap-1">

          {navItems.map((item) => (

            <NavLink
              key={item.to}
              to={item.to}
              end={item.exact}
              className={({ isActive }) =>
                `flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition ${
                  isActive
                    ? "bg-blue-600 text-white"
                    : "text-slate-300 hover:bg-slate-800 hover:text-white"
                }`
              }
            >

              <span>

                {item.icon}

              </span>

              <span>

                {item.label}

              </span>

            </NavLink>

          ))}

        </nav>

        {/* User */}

        <div className="flex items-center gap-4">

          {isAdmin && (

            <span className="px-2 py-1 rounded bg-amber-400 text-black text-xs font-bold">

              ADMIN

            </span>

          )}

          <span className="text-sm text-slate-300">

            {auth.user?.profile?.email}

          </span>

          <button
            onClick={logout}
            className="bg-red-600 hover:bg-red-700 text-white text-sm px-3 py-2 rounded-lg"
          >

            Logout

          </button>

        </div>

      </div>

    </header>

  );

}

export default Navbar;
