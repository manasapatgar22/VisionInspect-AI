import {
  ShieldAlert,
  CheckCircle2,
  AlertTriangle
} from "lucide-react";

function RiskAssessment({
  severity,
  decision,
  reason,
  defectType,
  confidence
}) {
  const level =
    severity?.severity_level || "Unknown";

  const score =
    Number(severity?.severity_score || 0);

  const isCritical = level === "Critical";
  const isHigh = level === "High";
  const isPass = decision === "PASS";

  let icon = <AlertTriangle size={24} />;

  if (isPass) {
    icon = <CheckCircle2 size={24} />;
  } else if (isCritical || isHigh) {
    icon = <ShieldAlert size={24} />;
  }

  return (
    <div
      className={`risk-card ${
        isPass
          ? "risk-pass"
          : isCritical
          ? "risk-critical"
          : isHigh
          ? "risk-high"
          : "risk-medium"
      }`}
    >
      <div className="risk-header">
        <div className="risk-icon">
          {icon}
        </div>

        <div>
          <span>Quality Risk Assessment</span>
          <strong>{level} Risk</strong>
        </div>
      </div>

      <div className="risk-grid">
        <div>
          <small>Defect Type</small>
          <strong>{defectType || "Good"}</strong>
        </div>

        <div>
          <small>Severity Score</small>
          <strong>
            {score.toFixed(1)}/100
          </strong>
        </div>

        <div>
          <small>Confidence</small>
          <strong>
            {Number(confidence || 0).toFixed(1)}%
          </strong>
        </div>

        <div>
          <small>Decision</small>
          <strong>{decision}</strong>
        </div>
      </div>

      <div className="risk-reason">
        <small>Assessment</small>
        <p>
          {reason ||
            severity?.recommended_action ||
            "Inspection completed."}
        </p>
      </div>
    </div>
  );
}

export default RiskAssessment;