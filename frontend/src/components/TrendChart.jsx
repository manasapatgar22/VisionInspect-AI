import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend
} from "recharts";

function TrendChart({ data }) {
  return (
    <div className="chart-container">
      {data?.length === 0 ? (
        <div className="chart-empty">
          No trend data available.
        </div>
      ) : (
        <ResponsiveContainer
          width="100%"
          height={280}
        >
          <LineChart data={data}>
            <CartesianGrid
              strokeDasharray="3 3"
              vertical={false}
            />

            <XAxis
              dataKey="date"
              tick={{ fontSize: 11 }}
            />

            <YAxis
              allowDecimals={false}
            />

            <Tooltip />

            <Legend />

            <Line
              type="monotone"
              dataKey="PASS"
              stroke="#16a34a"
              strokeWidth={3}
              dot={{ r: 4 }}
            />

            <Line
              type="monotone"
              dataKey="FAIL"
              stroke="#dc2626"
              strokeWidth={3}
              dot={{ r: 4 }}
            />

            <Line
              type="monotone"
              dataKey="REVIEW"
              stroke="#eab308"
              strokeWidth={3}
              dot={{ r: 4 }}
            />
          </LineChart>
        </ResponsiveContainer>
      )}
    </div>
  );
}

export default TrendChart;