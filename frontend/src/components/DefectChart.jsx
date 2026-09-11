import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from "recharts";

function DefectChart({ data }) {
  const chartData = (data || []).map((item) => ({
    name: item.defect_type || "Unknown",
    count: item.count
  }));

  return (
    <div className="chart-container">
      {chartData.length === 0 ? (
        <div className="chart-empty">
          No defect data available.
        </div>
      ) : (
        <ResponsiveContainer
          width="100%"
          height={280}
        >
          <BarChart data={chartData}>
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="name"
              tick={{ fontSize: 12 }}
            />

            <YAxis
              allowDecimals={false}
              tick={{ fontSize: 12 }}
            />

            <Tooltip />

            <Bar
              dataKey="count"
              radius={[5, 5, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default DefectChart;