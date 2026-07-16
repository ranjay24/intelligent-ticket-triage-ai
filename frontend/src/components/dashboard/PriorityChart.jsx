import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Cell,
} from "recharts";

const COLORS = {
  CRITICAL: "#991b1b",
  HIGH: "#dc2626",
  MEDIUM: "#f59e0b",
  LOW: "#16a34a",
  Unknown: "#64748b",
};

function PriorityChart({ data }) {

  const chartData = Object.entries(data || {}).map(
    ([priority, count]) => ({
      priority,
      count,
    })
  );

  return (

    <div className="bg-white rounded-2xl border border-slate-200 shadow-sm p-6">

      <div className="flex items-center justify-between mb-5">

        <div>

          <p className="text-xs uppercase tracking-widest text-slate-400 font-semibold">

            Analytics

          </p>

          <h2 className="text-xl font-bold text-slate-800 mt-1">

            Priority Distribution

          </h2>

        </div>

      </div>

      <div className="h-80">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <BarChart
            data={chartData}
          >

            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="priority"
            />

            <YAxis
              allowDecimals={false}
            />

            <Tooltip />

            <Bar
              dataKey="count"
              radius={[10, 10, 0, 0]}
            >

              {

                chartData.map((entry) => (

                  <Cell
                    key={entry.priority}
                    fill={
                      COLORS[entry.priority] ||
                      COLORS.Unknown
                    }
                  />

                ))

              }

            </Bar>

          </BarChart>

        </ResponsiveContainer>

      </div>

      <div className="grid grid-cols-3 gap-4 mt-5">

        {

          chartData.map((item) => (

            <div
              key={item.priority}
              className="text-center bg-slate-50 rounded-xl py-3"
            >

              <div
                className="w-3 h-3 rounded-full mx-auto mb-2"
                style={{
                  backgroundColor:
                    COLORS[item.priority] ||
                    COLORS.Unknown,
                }}
              />

              <p className="text-xs text-slate-500 uppercase">

                {item.priority}

              </p>

              <h3 className="text-2xl font-bold text-slate-800 mt-1">

                {item.count}

              </h3>

            </div>

          ))

        }

      </div>

    </div>

  );

}

export default PriorityChart;
