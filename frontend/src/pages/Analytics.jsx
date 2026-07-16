import { useState, useEffect } from "react";
import { api } from "../services/api";

import { Brain, RefreshCw } from "lucide-react";

import {
  Chart as ChartJS,
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler,
} from "chart.js";

import { Doughnut, Line } from "react-chartjs-2";

ChartJS.register(
  ArcElement,
  Tooltip,
  Legend,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Filler
);

const STATUS_BADGE = {
  NEW: "bg-blue-100 text-blue-700",
  PENDING_REVIEW: "bg-yellow-100 text-yellow-700",
  RESOLVED: "bg-green-100 text-green-700",
  REJECTED: "bg-red-100 text-red-700",
  CLOSED: "bg-slate-100 text-slate-700",
  APPROVED: "bg-green-100 text-green-700",
};

const PRIORITY_BADGE = {
  CRITICAL: "bg-red-200 text-red-800",
  HIGH: "bg-red-100 text-red-700",
  MEDIUM: "bg-yellow-100 text-yellow-700",
  LOW: "bg-green-100 text-green-700",
};

const FALLBACK_BADGE = "bg-slate-100 text-slate-600";

function CategoryRow({ label, count, total }) {
  const percent = total > 0 ? Math.round((count / total) * 100) : 0;

  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span>{label}</span>
        <span className="font-semibold">{count}</span>
      </div>

      <div className="h-2 bg-slate-200 rounded-full overflow-hidden">
        <div className="bg-blue-600 h-full" style={{ width: `${percent}%` }} />
      </div>
    </div>
  );
}

export default function Analytics() {

  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  async function fetchAnalytics() {
    try {
      const response = await api.get("/analytics");
      setAnalytics(response.data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="h-[70vh] flex items-center justify-center">
        <div className="w-10 h-10 rounded-full border-4 border-blue-600 border-t-transparent animate-spin" />
      </div>
    );
  }

  const summary = analytics?.summary || {};
  const categories = analytics?.categoryDistribution || {};
  const priorities = analytics?.priorityDistribution || {};
  const recentTickets = analytics?.recentTickets || [];

  const totalCategories = Object.values(categories).reduce(
    (a, b) => a + b,
    0
  );

  const doughnutData = {
    labels: ["Resolved", "Pending", "Rejected", "New", "Closed"],
    datasets: [
      {
        data: [
          summary.resolved || 0,
          summary.pendingReview || 0,
          summary.rejected || 0,
          summary.newTickets || 0,
          summary.closed || 0,
        ],
      },
    ],
  };

  const trendData = {
    labels: recentTickets
      .slice()
      .reverse()
      .map((_, i) => `#${i + 1}`),
    datasets: [
      {
        label: "Confidence",
        data: recentTickets
          .slice()
          .reverse()
          .map((t) => (t.confidence || 0) * 100),
        fill: true,
      },
    ],
  };

  return (
    <div className="max-w-screen-xl mx-auto px-6 py-8">

      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Analytics Dashboard
          </h1>
          <p className="text-slate-500 mt-2">
            AI-powered customer support insights
          </p>
        </div>

        <button
          onClick={() => {
            setRefreshing(true);
            fetchAnalytics();
          }}
          disabled={refreshing}
          className="flex items-center gap-2 px-5 py-3 rounded-xl bg-blue-600 hover:bg-blue-700 text-white"
        >
          <RefreshCw size={18} className={refreshing ? "animate-spin" : ""} />
          Refresh
        </button>
      </div>

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">

        {/* Doughnut */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h2 className="font-semibold text-lg mb-6">Ticket Status</h2>
          <div className="h-72 flex items-center justify-center">
            <Doughnut data={doughnutData} />
          </div>
        </div>

        {/* Categories */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h2 className="font-semibold text-lg mb-6">Category Distribution</h2>
          <div className="space-y-5">
            {Object.entries(categories).map(([label, count]) => (
              <CategoryRow
                key={label}
                label={label}
                count={count}
                total={totalCategories}
              />
            ))}
          </div>
        </div>

        {/* Priority */}
        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
          <h2 className="font-semibold text-lg mb-6">Priority Distribution</h2>
          <div className="space-y-5">
            {Object.entries(priorities).map(([label, count]) => (
              <CategoryRow
                key={label}
                label={label}
                count={count}
                total={summary.totalTickets || 1}
              />
            ))}

            <div className="pt-6 border-t">
              <div className="flex justify-between">
                <span className="text-slate-500">Average AI Confidence</span>
                <span className="font-bold text-blue-700">
                  {Math.round((summary.avgConfidence || 0) * 100)}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Confidence Trend */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6 mb-8">
        <div className="flex items-center gap-2 mb-6">
          <Brain className="text-blue-600" size={22} />
          <h2 className="text-lg font-semibold">AI Confidence Trend</h2>
        </div>

        <Line data={trendData} />
      </div>

      {/* Recent Tickets */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-lg font-semibold">Recent Tickets</h2>
          <span className="text-sm text-slate-500">
            {recentTickets.length} recent tickets
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b">
                <th className="text-left py-3 px-2 text-sm font-semibold">
                  Subject
                </th>
                <th className="text-left py-3 px-2 text-sm font-semibold">
                  Category
                </th>
                <th className="text-left py-3 px-2 text-sm font-semibold">
                  Priority
                </th>
                <th className="text-left py-3 px-2 text-sm font-semibold">
                  Status
                </th>
                <th className="text-left py-3 px-2 text-sm font-semibold">
                  Confidence
                </th>
                <th className="text-left py-3 px-2 text-sm font-semibold">
                  Created
                </th>
              </tr>
            </thead>

            <tbody>
              {recentTickets.length === 0 ? (
                <tr>
                  <td
                    colSpan={6}
                    className="text-center py-10 text-slate-500"
                  >
                    No recent tickets found.
                  </td>
                </tr>
              ) : (
                recentTickets.map((ticket) => (
                  <tr
                    key={ticket.ticketId}
                    className="border-b last:border-b-0 hover:bg-slate-50 transition"
                  >
                    <td className="py-4 px-2">
                      <div className="font-medium text-slate-900">
                        {ticket.subject}
                      </div>
                      <div className="text-xs text-slate-500 mt-1">
                        {ticket.ticketId}
                      </div>
                    </td>

                    <td className="py-4 px-2">{ticket.category || "-"}</td>

                    <td className="py-4 px-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          PRIORITY_BADGE[ticket.priority] || FALLBACK_BADGE
                        }`}
                      >
                        {ticket.priority}
                      </span>
                    </td>

                    <td className="py-4 px-2">
                      <span
                        className={`px-2 py-1 rounded-full text-xs font-semibold ${
                          STATUS_BADGE[ticket.status] || FALLBACK_BADGE
                        }`}
                      >
                        {ticket.status}
                      </span>
                    </td>

                    <td className="py-4 px-2">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-slate-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              ticket.confidence >= 0.9
                                ? "bg-green-500"
                                : ticket.confidence >= 0.75
                                ? "bg-yellow-500"
                                : "bg-red-500"
                            }`}
                            style={{
                              width: `${(ticket.confidence || 0) * 100}%`,
                            }}
                          />
                        </div>

                        <span className="text-sm font-medium">
                          {Math.round((ticket.confidence || 0) * 100)}%
                        </span>
                      </div>
                    </td>

                    <td className="py-4 px-2 text-sm text-slate-600">
                      {ticket.createdAt
                        ? new Date(ticket.createdAt).toLocaleDateString()
                        : "-"}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
