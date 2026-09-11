import {
  Package,
  CheckCircle2,
  XCircle,
  AlertTriangle
} from "lucide-react";

import StatCard from "../components/StatCard";
import TrendChart from "../components/TrendChart";
import DefectChart from "../components/DefectChart";
import InspectionTable from "../components/InspectionTable";

function SupervisorDashboard({
  statistics,
  trend,
  defects,
  inspections,
  onViewInspection
}) {
  const total =
    statistics?.total_inspections || 0;

  const passed =
    statistics?.passed || 0;

  const failed =
    statistics?.failed || 0;

  const critical =
    statistics?.critical || 0;

  const review =
    Math.max(
      0,
      total - passed - failed
    );

  const percentage = (value) =>
    total
      ? `${Math.round((value / total) * 100)}%`
      : "0%";

  return (
    <>
      <div className="page-heading supervisor-heading">
        <div>
          <h1>Welcome, Factory Supervisor!</h1>
          <p>
            Track overall production quality,
            monitor defects and ensure operational
            efficiency.
          </p>
        </div>

        <div className="dashboard-date">
          Live Production Data
        </div>
      </div>

      <div className="stats-grid-new">
        <StatCard
          icon={<Package />}
          value={total}
          label="Total Products Inspected"
          type="blue"
        />

        <StatCard
          icon={<CheckCircle2 />}
          value={passed}
          label="Passed"
          percentage={percentage(passed)}
          type="green"
        />

        <StatCard
          icon={<XCircle />}
          value={failed}
          label="Failed"
          percentage={percentage(failed)}
          type="red"
        />

        <StatCard
          icon={<AlertTriangle />}
          value={review}
          label="Needs Review"
          percentage={percentage(review)}
          type="orange"
        />
      </div>

      <div className="supervisor-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Production Quality Trend</h2>
              <p>
                Daily PASS, FAIL and REVIEW activity
              </p>
            </div>
          </div>

          <TrendChart data={trend} />
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Defect Category Distribution</h2>
              <p>
                Manufacturing defect categories
              </p>
            </div>
          </div>

          <DefectChart data={defects} />
        </section>
      </div>

      <section className="panel recent-panel">
        <div className="panel-header">
          <div>
            <h2>Recent Inspections — All Production</h2>
            <p>
              Latest quality inspection records
            </p>
          </div>
        </div>

        <InspectionTable
          inspections={inspections.slice(0, 10)}
          onView={onViewInspection}
        />
      </section>
    </>
  );
}

export default SupervisorDashboard;