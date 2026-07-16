import { useState } from "react";
import {
  Search,
  UserCircle2,
  Sparkles,
} from "lucide-react";

function confidenceColor(confidence) {

  if (confidence >= 0.90)
    return "bg-green-100 text-green-700";

  if (confidence >= 0.75)
    return "bg-amber-100 text-amber-700";

  return "bg-red-100 text-red-700";

}

function priorityColor(priority) {

  switch (priority) {

    case "CRITICAL":
      return "bg-red-200 text-red-800";

    case "HIGH":
      return "bg-red-100 text-red-700";

    case "MEDIUM":
      return "bg-yellow-100 text-yellow-700";

    case "LOW":
      return "bg-green-100 text-green-700";

    default:
      return "bg-slate-100 text-slate-600";

  }

}

export default function ReviewSidebar({

  tickets,

  selectedTicket,

  onSelect

}) {

  const [search, setSearch] = useState("");

  const filteredTickets = tickets.filter((ticket) =>

    (
      ticket.subject +
      ticket.customerEmail +
      ticket.category
    )
      .toLowerCase()
      .includes(search.toLowerCase())

  );

  return (

    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm h-[78vh] flex flex-col">

      {/* Header */}

      <div className="p-5 border-b">

        <div className="flex justify-between items-center">

          <div>

            <p className="text-xs uppercase tracking-widest text-slate-400">

              Pending Queue

            </p>

            <h2 className="text-xl font-bold text-slate-800 mt-1">

              Reviews

            </h2>

          </div>

          <div className="bg-blue-600 text-white rounded-full w-8 h-8 flex items-center justify-center text-sm font-semibold">

            {tickets.length}

          </div>

        </div>

        <div className="relative mt-5">

          <Search
            size={18}
            className="absolute left-3 top-3 text-slate-400"
          />

          <input
            value={search}
            onChange={(e) =>
              setSearch(e.target.value)
            }
            placeholder="Search tickets..."
            className="w-full pl-10 pr-4 py-2.5 border rounded-xl outline-none focus:ring-2 focus:ring-blue-500"
          />

        </div>

      </div>

      {/* Ticket List */}

      <div className="flex-1 overflow-y-auto">

        {

          filteredTickets.length === 0 ? (

            <div className="flex flex-col items-center justify-center h-full text-slate-400">

              <Sparkles
                size={36}
                className="mb-3"
              />

              No pending reviews

            </div>

          ) :

          filteredTickets.map((ticket) => (

            <button

              key={ticket.ticketId}

              onClick={() =>
                onSelect(ticket)
              }

              className={`w-full text-left border-b px-5 py-4 transition hover:bg-slate-50

              ${
                selectedTicket?.ticketId ===
                ticket.ticketId

                  ? "bg-blue-50 border-l-4 border-blue-600"

                  : ""

              }

              `}

            >

              <div className="flex justify-between items-start">

                <div className="flex gap-3">

                  <UserCircle2
                    className="text-slate-400 mt-0.5"
                    size={32}
                  />

                  <div>

                    <h3 className="font-semibold text-slate-800">

                      {ticket.subject}

                    </h3>

                    <p className="text-xs text-slate-500 mt-1">

                      {ticket.customerEmail}

                    </p>

                  </div>

                </div>

                <span
                  className={`text-xs px-2 py-1 rounded-full ${confidenceColor(
                    ticket.confidence
                  )}`}
                >

                  {Math.round(
                    ticket.confidence * 100
                  )}
                  %

                </span>

              </div>

              <div className="flex justify-between items-center mt-4">

                <span className="text-xs bg-slate-100 px-2 py-1 rounded-full">

                  {ticket.category}

                </span>

                <span
                  className={`text-xs px-2 py-1 rounded-full ${priorityColor(
                    ticket.priority
                  )}`}
                >

                  {ticket.priority}

                </span>

              </div>

            </button>

          ))

        }

      </div>

    </div>

  );

}
