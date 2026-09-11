import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend
} from "recharts";

const COLORS = {
  Critical: "#dc2626",
  High: "#ea580c",
  Medium: "#eab308",
  Low: "#16a34a",
  unknown: "#94a3b8"
};

function SeverityChart({ data }) {
  const chartData = (data || []).map((item) => ({
    name: item.severity_level || "unknown",
    value: item.count
  }));

  return (
    <div className="chart-container">
      {chartData.length === 0 ? (
        <div className="chart-empty">
          No severity data available.
        </div>
      ) : (
        <ResponsiveContainer
          width="100%"
          height={280}
        >
          <PieChart>
            <Pie
              data={chartData}
              dataKey="value"
              nameKey="name"
              innerRadius={65}
              outerRadius={100}
              paddingAngle={3}
            >
              {chartData.map((entry) => (
                <Cell
                  key={entry.name}
                  fill={
                    COLORS[entry.name] ||
                    COLORS.unknown
                  }
                />
              ))}
            </Pie>

            <Tooltip />
            <Legend />
          </PieChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default SeverityChart;