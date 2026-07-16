import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
  Legend,
} from "recharts";

const COLORS = [
  "#2563eb",
  "#16a34a",
  "#dc2626",
  "#f59e0b",
  "#7c3aed",
  "#0891b2",
  "#64748b",
];

function CategoryChart({ data }) {

  const chartData = Object.entries(data || {}).map(
    ([name, value]) => ({
      name,
      value,
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

            Ticket Categories

          </h2>

        </div>

      </div>

      <div className="h-80">

        <ResponsiveContainer width="100%" height="100%">

          <PieChart>

            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              cx="50%"
              cy="50%"
              outerRadius={95}
              innerRadius={55}
              paddingAngle={3}
              label
            >

              {chartData.map((entry, index) => (

                <Cell
                  key={index}
                  fill={COLORS[index % COLORS.length]}
                />

              ))}

            </Pie>

            <Tooltip />

            <Legend
              verticalAlign="bottom"
              height={40}
            />

          </PieChart>

        </ResponsiveContainer>

      </div>

      <div className="space-y-3 mt-4">

        {chartData.map((item, index) => (

          <div
            key={item.name}
            className="flex items-center justify-between"
          >

            <div className="flex items-center gap-3">

              <div
                className="w-3 h-3 rounded-full"
                style={{
                  backgroundColor:
                    COLORS[index % COLORS.length],
                }}
              />

              <span className="text-sm text-slate-700">

                {item.name}

              </span>

            </div>

            <span className="font-semibold text-slate-800">

              {item.value}

            </span>

          </div>

        ))}

      </div>

    </div>
  );
}

export default CategoryChart;