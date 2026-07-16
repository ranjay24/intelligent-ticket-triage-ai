import { useEffect, useState } from "react";
import { api } from "../services/api";

import ReviewSidebar from "../components/reviews/ReviewSidebar";
import ReviewWorkspace from "../components/reviews/ReviewWorkspace";

function Reviews() {
  const [tickets, setTickets] = useState([]);
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReviews();
  }, []);

  async function fetchReviews() {
    try {
      const response = await api.get("/reviews/pending");
      const data = response.data;

      setTickets(data);

      // Keep the currently-selected ticket if it's still pending;
      // otherwise fall back to the first one (or none).
      setSelectedTicket((prev) => {
        if (prev) {
          const stillPending = data.find(
            (t) => t.ticketId === prev.ticketId
          );
          if (stillPending) return stillPending;
        }
        return data.length > 0 ? data[0] : null;
      });
    } catch (error) {
      console.error(error);
    } finally {
      setLoading(false);
    }
  }

  if (loading) {
    return (
      <div className="flex justify-center items-center h-[70vh]">
        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-screen-2xl mx-auto px-6 py-8">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-slate-900">AI Review Center</h1>
        <p className="text-slate-500 mt-2">
          Review AI generated responses before sending them to customers.
        </p>
      </div>

      <div className="grid grid-cols-12 gap-6">
        <div className="col-span-4">
          <ReviewSidebar
            tickets={tickets}
            selectedTicket={selectedTicket}
            onSelect={setSelectedTicket}
          />
        </div>

        <div className="col-span-8">
          <ReviewWorkspace ticket={selectedTicket} refresh={fetchReviews} />
        </div>
      </div>
    </div>
  );
}

export default Reviews;
