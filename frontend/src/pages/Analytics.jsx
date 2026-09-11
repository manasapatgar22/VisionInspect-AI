import TrendChart from "../components/TrendChart";
import DefectChart from "../components/DefectChart";
import SeverityChart from "../components/SeverityChart";

function Analytics({
  statistics,
  trend,
  defects,
  severity
}) {
  const total =
    statistics?.total_inspections || 0;

  const passed =
    statistics?.passed || 0;

  const failed =
    statistics?.failed || 0;

  const critical =
    statistics?.critical || 0;

  const passRate =
    total
      ? ((passed / total) * 100).toFixed(1)
      : "0.0";

  const defectRate =
    total
      ? ((failed / total) * 100).toFixed(1)
      : "0.0";

  const criticalRate =
    total
      ? ((critical / total) * 100).toFixed(1)
      : "0.0";

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Production Analytics</h1>
          <p>
            Analyze quality performance, defect
            patterns and production trends.
          </p>
        </div>
      </div>

      <div className="kpi-strip">
        <div>
          <span>Pass Rate</span>
          <strong>{passRate}%</strong>
        </div>

        <div>
          <span>Defect Rate</span>
          <strong>{defectRate}%</strong>
        </div>

        <div>
          <span>Critical Defect Rate</span>
          <strong>{criticalRate}%</strong>
        </div>

        <div>
          <span>Total Inspections</span>
          <strong>{total}</strong>
        </div>
      </div>

      <div className="analytics-grid">
        <section className="panel wide">
          <div className="panel-header">
            <div>
              <h2>Inspection Trend</h2>
              <p>
                Production quality trend over time
              </p>
            </div>
          </div>

          <TrendChart data={trend} />
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Defect Distribution</h2>
              <p>
                Most frequently detected defects
              </p>
            </div>
          </div>

          <DefectChart data={defects} />
        </section>

        <section className="panel">
          <div className="panel-header">
            <div>
              <h2>Severity Distribution</h2>
              <p>
                Manufacturing quality risk levels
              </p>
            </div>
          </div>

          <SeverityChart data={severity} />
        </section>
      </div>
    </div>
  );
}

export default Analytics;