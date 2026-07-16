import { useEffect, useState } from "react";
import { useAuth } from "react-oidc-context";

import { api } from "../services/api";

import {
  Ticket,
  Clock3,
  CheckCircle2,
  AlertTriangle,
} from "lucide-react";

import KpiCard from "../components/dashboard/KpiCard";
import AiConfidenceCard from "../components/dashboard/AiConfidenceCard";
import RecentTicketsTable from "../components/dashboard/RecentTicketsTable";
import QuickActions from "../components/dashboard/QuickActions";

function Dashboard() {

  const auth = useAuth();

  const isAdmin =
    auth.user?.profile?.["cognito:groups"]?.includes("Admins");

  const [loading, setLoading] = useState(true);

  const [analytics, setAnalytics] = useState({
    summary: {
      totalTickets: 0,
      newTickets: 0,
      pendingReview: 0,
      approved: 0,
      rejected: 0,
      avgConfidence: 0,
    },
    categoryDistribution: {},
    priorityDistribution: {},
    recentTickets: [],
  });

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {

    try {

      const response = await api.get("/analytics");

      setAnalytics(response.data);

    } catch (error) {

      console.error(error);

    } finally {

      setLoading(false);

    }

  };

  if (loading) {

    return (

      <div className="flex justify-center items-center h-[70vh]">

        <div className="w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />

      </div>

    );

  }

  const summary = analytics.summary;

  return (

    <div className="max-w-screen-2xl mx-auto px-6 py-8">

      {/* Hero */}

      <div className="rounded-3xl bg-gradient-to-r from-slate-900 via-blue-900 to-indigo-900 p-8 text-white mb-8 shadow-xl">

        <p className="uppercase tracking-[0.3em] text-blue-200 text-xs">

          AI Powered Customer Support

        </p>

        <h1 className="text-4xl font-bold mt-3">

          Intelligent Ticket Triage Dashboard

        </h1>

        <p className="text-blue-100 mt-4 max-w-2xl">

          Monitor AI ticket classification, review pending approvals,
          customer issues, and system performance from one dashboard.

        </p>

      </div>

      {/* KPI Cards */}

      <div className="grid lg:grid-cols-4 gap-6 mb-8">

        <KpiCard
          title="Total Tickets"
          value={summary.totalTickets}
          color="text-blue-600"
          trend="All tickets"
          icon={<Ticket size={30} />}
        />

        <KpiCard
          title="New Tickets"
          value={summary.newTickets}
          color="text-orange-500"
          trend="Awaiting processing"
          icon={<Clock3 size={30} />}
        />

        <KpiCard
          title="Approved"
          value={summary.approved}
          color="text-green-600"
          trend="AI approved"
          icon={<CheckCircle2 size={30} />}
        />

        <KpiCard
          title="Pending Review"
          value={summary.pendingReview}
          color="text-red-600"
          trend="Need attention"
          trendUp={false}
          icon={<AlertTriangle size={30} />}
        />

      </div>

      {/* AI Confidence */}

      <div className="mb-8">

        <AiConfidenceCard
          confidence={summary.avgConfidence}
        />

      </div>

      {/* Recent Tickets */}

      {isAdmin && (

        <div className="mb-8">

          <RecentTicketsTable
            tickets={analytics.recentTickets}
          />

        </div>

      )}

      {/* Quick Actions */}

      <QuickActions />

    </div>

  );

}

export default Dashboard;