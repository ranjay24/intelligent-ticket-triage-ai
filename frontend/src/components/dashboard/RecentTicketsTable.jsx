import { Link } from "react-router-dom";
import {
  Paperclip,
  Clock,
  ArrowRight,
} from "lucide-react";

const STATUS_STYLES = {
  NEW: "bg-blue-100 text-blue-700",
  PENDING_REVIEW: "bg-yellow-100 text-yellow-700",
  RESOLVED: "bg-green-100 text-green-700",
  REJECTED: "bg-red-100 text-red-700",
  CLOSED: "bg-slate-100 text-slate-700",
  // Legacy rows created before the lifecycle change
  APPROVED: "bg-green-100 text-green-700",
};

const PRIORITY_STYLES = {
  CRITICAL: "bg-red-200 text-red-800",
  HIGH: "bg-red-100 text-red-700",
  MEDIUM: "bg-yellow-100 text-yellow-700",
  LOW: "bg-green-100 text-green-700",
};

const FALLBACK_BADGE = "bg-slate-100 text-slate-600";

function formatDate(date) {
  if (!date) return "-";
  return new Date(date).toLocaleString();
}

function avatar(email = "") {
  return email.charAt(0).toUpperCase();
}

function RecentTicketsTable({ tickets }) {

  return (

    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm">

      <div className="flex justify-between items-center px-6 py-5 border-b">

        <div>

          <p className="text-xs uppercase tracking-widest text-slate-400 font-semibold">

            Live Activity

          </p>

          <h2 className="text-xl font-bold text-slate-800 mt-1">

            Recent Tickets

          </h2>

        </div>

        <Link
          to="/tickets"
          className="text-blue-600 text-sm font-semibold hover:text-blue-700 flex items-center gap-2"
        >
          View All

          <ArrowRight size={16} />

        </Link>

      </div>

      <div className="overflow-x-auto">

        <table className="w-full">

          <thead>

            <tr className="bg-slate-50">

              <th className="text-left px-6 py-4 text-xs uppercase tracking-wider text-slate-400">

                Customer

              </th>

              <th className="text-left px-4 py-4 text-xs uppercase tracking-wider text-slate-400">

                Subject

              </th>

              <th className="text-left px-4 py-4 text-xs uppercase tracking-wider text-slate-400">

                Category

              </th>

              <th className="text-left px-4 py-4 text-xs uppercase tracking-wider text-slate-400">

                Priority

              </th>

              <th className="text-left px-4 py-4 text-xs uppercase tracking-wider text-slate-400">

                Status

              </th>

              <th className="text-left px-4 py-4 text-xs uppercase tracking-wider text-slate-400">

                Created

              </th>

              <th className="text-center px-4 py-4 text-xs uppercase tracking-wider text-slate-400">

                Files

              </th>

            </tr>

          </thead>

          <tbody>

            {tickets.length === 0 ? (

              <tr>

                <td
                  colSpan="7"
                  className="py-16 text-center text-slate-400"
                >

                  No Recent Tickets

                </td>

              </tr>

            ) : (

              tickets.map((ticket) => (

                <tr
                  key={ticket.ticketId}
                  className="border-t hover:bg-blue-50 transition"
                >

                  <td className="px-6 py-4">

                    <div className="flex items-center gap-3">

                      <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold">

                        {avatar(ticket.customerEmail)}

                      </div>

                      <div>

                        <p className="font-semibold text-slate-800">

                          {ticket.customerEmail}

                        </p>

                      </div>

                    </div>

                  </td>

                  <td className="px-4 py-4 font-medium text-slate-700">

                    <Link
                      to={`/tickets/${ticket.ticketId}`}
                      className="hover:text-blue-600"
                    >

                      {ticket.subject}

                    </Link>

                  </td>

                  <td className="px-4 py-4">

                    <span className="bg-slate-100 px-3 py-1 rounded-full text-sm">

                      {ticket.category}

                    </span>

                  </td>

                  <td className="px-4 py-4">

                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${PRIORITY_STYLES[ticket.priority] || FALLBACK_BADGE}`}
                    >

                      {ticket.priority}

                    </span>

                  </td>

                  <td className="px-4 py-4">

                    <span
                      className={`px-3 py-1 rounded-full text-xs font-semibold ${STATUS_STYLES[ticket.status] || FALLBACK_BADGE}`}
                    >

                      {ticket.status}

                    </span>

                  </td>

                  <td className="px-4 py-4">

                    <div className="flex items-center gap-2 text-slate-500 text-sm">

                      <Clock size={15} />

                      {formatDate(ticket.createdAt)}

                    </div>

                  </td>

                  <td className="px-4 py-4 text-center">

                    {ticket.attachments?.length > 0 ? (

                      <Paperclip
                        size={18}
                        className="text-blue-600 inline"
                      />

                    ) : (

                      "-"

                    )}

                  </td>

                </tr>

              ))

            )}

          </tbody>

        </table>

      </div>

    </div>

  );

}

export default RecentTicketsTable;
