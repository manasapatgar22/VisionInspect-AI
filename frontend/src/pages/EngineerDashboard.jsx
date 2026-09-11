import {
  ClipboardList,
  CheckCircle2,
  XCircle,
  ShieldAlert
} from "lucide-react";

import StatCard from "../components/StatCard";
import DefectChart from "../components/DefectChart";
import InspectionTable from "../components/InspectionTable";

function EngineerDashboard({
  statistics,
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

  const percentage = (value) =>
    total
      ? `${Math.round((value / total) * 100)}%`
      : "0%";

  return (
    <>
      <div className="page-heading">
        <div>
          <h1>Welcome, Quality Engineer!</h1>
          <p>
            Monitor product quality, run inspections
            and analyze results.
          </p>
        </div>
      </div>

      <div className="stats-grid-new">
        <StatCard
          icon={<ClipboardList />}
          value={total}
          label="Total Inspections"
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
          icon={<ShieldAlert />}
          value={critical}
          label="Critical"
          percentage={percentage(critical)}
          type="orange"
        />
      </div>

      <div className="dashboard-grid">
        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Defect Distribution</h2>
              <p>
                Distribution of detected defect types
              </p>
            </div>
          </div>

          <DefectChart data={defects} />
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Inspection Results Overview</h2>
              <p>Current quality decision distribution</p>
            </div>
          </div>

          <div className="result-overview">
            <div className="overview-number">
              <strong>{total}</strong>
              <span>Total</span>
            </div>

            <div className="overview-list">
              <div>
                <span className="legend-dot green"></span>
                Passed
                <strong>{percentage(passed)}</strong>
              </div>

              <div>
                <span className="legend-dot red"></span>
                Failed
                <strong>{percentage(failed)}</strong>
              </div>

              <div>
                <span className="legend-dot gray"></span>
                Critical
                <strong>{percentage(critical)}</strong>
              </div>
            </div>
          </div>
        </section>
      </div>

      <section className="panel recent-panel">
        <div className="panel-header">
          <div>
            <h2>Recent Inspections</h2>
            <p>
              Latest product inspection records
            </p>
          </div>
        </div>

        <InspectionTable
          inspections={inspections.slice(0, 8)}
          onView={onViewInspection}
        />
      </section>
    </>
  );
}

export default EngineerDashboard;