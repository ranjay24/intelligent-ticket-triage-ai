import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "react-oidc-context";
import { api } from "../services/api";

const inputCls =
  "w-full text-sm px-3 py-2.5 border border-slate-200 rounded-lg bg-white text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition";

const labelCls = "block text-sm font-medium text-slate-700 mb-1.5";

function CreateTicket() {
  const auth = useAuth();

  const [formData, setFormData] = useState({
    subject: "",
    description: "",
  });

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setSubmitting(true);
    setError(null);

    try {
      const email = auth.user?.profile?.email;

      // Used by the /my-tickets request (via the api interceptor)
      localStorage.setItem("customerEmail", email);

      await api.post("/tickets", {
        ...formData,
        customerEmail: email,
      });

      // Go to the customer's own list, not /tickets (admin-only route)
      navigate("/my-tickets");

    } catch (err) {
      setError(
        err.response?.data?.message ||
          err.message ||
          "Failed to create ticket."
      );
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-8">
      <div className="max-w-2xl">

        <div className="mb-7">
          <h1 className="text-xl font-semibold text-slate-900">
            Create Ticket
          </h1>

          <p className="text-sm text-slate-500 mt-1">
            Logged in as{" "}
            <span className="font-medium text-blue-600">
              {auth.user?.profile?.email}
            </span>
          </p>
        </div>

        <form
          onSubmit={handleSubmit}
          className="bg-white border border-slate-200 rounded-xl p-6 space-y-5"
        >

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 text-sm px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          <div>
            <label className={labelCls}>Subject</label>

            <input
              type="text"
              name="subject"
              value={formData.subject}
              onChange={handleChange}
              placeholder="Brief description of the issue"
              className={inputCls}
              required
            />
          </div>

          <div>
            <label className={labelCls}>Description</label>

            <textarea
              name="description"
              value={formData.description}
              onChange={handleChange}
              rows={6}
              placeholder="Describe the issue in detail..."
              className={`${inputCls} resize-none`}
              required
            />
          </div>

          <div className="bg-blue-50 border border-blue-100 rounded-lg px-4 py-3 flex items-start gap-2">
            <span className="text-blue-500 mt-0.5">ℹ</span>

            <p className="text-xs text-blue-700">
              Once submitted, AI will classify the ticket, assign priority,
              detect sentiment, retrieve knowledge base articles and generate a
              draft response automatically.
            </p>
          </div>

          <div className="flex gap-3 pt-1">

            <button
              type="submit"
              disabled={submitting}
              className="bg-blue-600 text-white text-sm font-medium px-5 py-2.5 rounded-lg hover:bg-blue-700 disabled:opacity-40 transition"
            >
              {submitting ? "Submitting..." : "Create Ticket"}
            </button>

            <button
              type="button"
              onClick={() => navigate("/my-tickets")}
              className="text-sm font-medium px-5 py-2.5 rounded-lg border border-slate-200 text-slate-600 hover:bg-slate-50 transition"
            >
              Cancel
            </button>

          </div>
        </form>
      </div>
    </div>
  );
}

export default CreateTicket;
