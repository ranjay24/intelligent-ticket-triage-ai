import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../services/api";
import useRole from "../auth/useRole";
import { useAuth } from "react-oidc-context";

const STATUS_STYLES = {
  NEW: "bg-blue-50 text-blue-700",
  PENDING_REVIEW: "bg-amber-50 text-amber-700",
  RESOLVED: "bg-green-50 text-green-700",
  REJECTED: "bg-red-50 text-red-700",
  CLOSED: "bg-slate-100 text-slate-600",
  // Legacy rows created before the lifecycle change
  APPROVED: "bg-green-50 text-green-700",
};

const PRIORITY_STYLES = {
  CRITICAL: "bg-red-100 text-red-800",
  HIGH: "bg-red-50 text-red-700",
  MEDIUM: "bg-amber-50 text-amber-700",
  LOW: "bg-slate-100 text-slate-500",
};

function Badge({ label, styleMap }) {
  const cls = styleMap[label] ?? "bg-slate-100 text-slate-600";

  return (
    <span
      className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-medium ${cls}`}
    >
      {label || "—"}
    </span>
  );
}

function Tickets() {
  const navigate = useNavigate();
  const auth = useAuth();
  const { isAdmin } = useRole();

  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!auth.isLoading && auth.isAuthenticated) {
      fetchTickets();
    }
  }, [auth.isLoading, auth.isAuthenticated, isAdmin]);

  async function fetchTickets() {
    try {
      setLoading(true);
      setError("");

      const endpoint = isAdmin ? "/tickets" : "/my-tickets";

      const response = await api.get(endpoint);

      setTickets(Array.isArray(response.data) ? response.data : []);
    } catch (err) {
      console.error(err);
      setError("Unable to load tickets.");
      setTickets([]);
    } finally {
      setLoading(false);
    }
  }

  const filteredTickets = tickets.filter((ticket) => {
    const text = [
      ticket.subject,
      ticket.category,
      ticket.priority,
      ticket.status,
    ]
      .join(" ")
      .toLowerCase();

    return text.includes(search.toLowerCase());
  });

  if (loading) {
    return (
      <div className="flex justify-center items-center h-72">
        <div className="flex flex-col items-center gap-3">
          <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-slate-500">Loading tickets...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-6xl mx-auto mt-10">
        <div className="bg-red-50 border border-red-200 rounded-xl p-6 text-red-700">
          {error}
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-8">

      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            {isAdmin ? "All Tickets" : "My Tickets"}
          </h1>

          <p className="text-slate-500 mt-1">
            {filteredTickets.length} ticket(s)
          </p>
        </div>

        <div className="flex gap-3">
          <input
            type="text"
            placeholder="Search tickets..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="border rounded-lg px-4 py-2 w-72"
          />

          {!isAdmin && (
            <Link
              to="/create-ticket"
              className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2 rounded-lg"
            >
              + New Ticket
            </Link>
          )}
        </div>
      </div>

      {filteredTickets.length === 0 ? (
        <div className="bg-white rounded-2xl border border-slate-200 p-16 text-center">
          <div className="text-6xl">🎫</div>

          <h2 className="text-2xl font-semibold mt-6">No Tickets Found</h2>

          <p className="text-slate-500 mt-2">
            {isAdmin
              ? "There are currently no tickets available."
              : "You haven't created any support tickets yet."}
          </p>

          {!isAdmin && (
            <Link
              to="/create-ticket"
              className="inline-block mt-6 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-xl"
            >
              Create Ticket
            </Link>
          )}
        </div>
      ) : (
        <div className="bg-white rounded-2xl border border-slate-200 overflow-hidden">
          <table className="min-w-full">
            <thead className="bg-slate-50">
              <tr>
                <th className="text-left px-6 py-4 text-sm font-semibold">
                  Subject
                </th>
                <th className="text-left px-6 py-4 text-sm font-semibold">
                  Category
                </th>
                <th className="text-left px-6 py-4 text-sm font-semibold">
                  Priority
                </th>
                <th className="text-left px-6 py-4 text-sm font-semibold">
                  Status
                </th>
                <th className="text-left px-6 py-4 text-sm font-semibold">
                  Created
                </th>
              </tr>
            </thead>

            <tbody>
              {filteredTickets.map((ticket) => (
                <tr
                  key={ticket.ticketId}
                  onClick={() => navigate(`/tickets/${ticket.ticketId}`)}
                  className="cursor-pointer hover:bg-slate-50 border-t"
                >
                  <td className="px-6 py-4 font-medium">{ticket.subject}</td>

                  <td className="px-6 py-4">{ticket.category || "—"}</td>

                  <td className="px-6 py-4">
                    <Badge label={ticket.priority} styleMap={PRIORITY_STYLES} />
                  </td>

                  <td className="px-6 py-4">
                    <Badge label={ticket.status} styleMap={STATUS_STYLES} />
                  </td>

                  <td className="px-6 py-4 text-slate-500">
                    {ticket.createdAt
                      ? new Date(ticket.createdAt).toLocaleString()
                      : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

export default Tickets;
