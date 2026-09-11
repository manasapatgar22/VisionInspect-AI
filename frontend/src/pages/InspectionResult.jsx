import {
  ArrowLeft,
  Download,
  RefreshCcw,
  CheckCircle2,
  XCircle
} from "lucide-react";

import RiskAssessment from "../components/RiskAssessment";
import StatusBadge from "../components/StatusBadge";
import ImageQualityCard from "../components/ImageQualityCard";

function InspectionResult({
  result,
  preview,
  onBack,
  onNewInspection
}) {
  if (!result) {
    return null;
  }

  const classification =
    result.classification || {};

  const severity =
    result.severity || {};

  const quality =
    result.quality_control || {};

  const localization =
    result.localization || {};

  const box =
    localization.bounding_box;

  return (
    <div>
      <div className="result-top">
        <button
          className="back-link"
          onClick={onBack}
        >
          <ArrowLeft size={17} />
          Back to History
        </button>

        <div className="result-actions">
          <button
            className="secondary-button"
            onClick={() =>
              window.open(
                "/api/analytics/export/pdf",
                "_blank"
              )
            }
          >
            <Download size={17} />
            Download Report
          </button>

          <button
            className="primary-button"
            onClick={onNewInspection}
          >
            <RefreshCcw size={17} />
            Inspect Another Image
          </button>
        </div>
      </div>

      <div className="page-heading">
        <div>
          <h1>Inspection Result</h1>
          <p>
            Detailed analysis result for the inspected
            product image.
          </p>
        </div>

        <StatusBadge
          status={quality.decision}
        />
      </div>

      <div className="result-grid">
        <section className="panel image-result-panel">
          <h2>Original Image</h2>

          {preview ? (
            <div className="result-image-container">
              <img
                src={preview}
                alt="Inspected product"
              />

              {box && (
                <div
                  className="result-defect-box"
                  style={{
                    left: `${box.x}px`,
                    top: `${box.y}px`,
                    width: `${box.width}px`,
                    height: `${box.height}px`
                  }}
                >
                  <span>
                    {classification.defect_type}
                  </span>
                </div>
              )}
            </div>
          ) : (
            <div className="no-image">
              Image preview unavailable
            </div>
          )}
        </section>

        <section className="panel">
          <h2>Inspection Details</h2>

          <div className="detail-list">
            <div>
              <span>Filename</span>
              <strong>
                {result.inspection?.filename}
              </strong>
            </div>

            <div>
              <span>Product Category</span>
              <strong>
                {result.category}
              </strong>
            </div>

            <div>
              <span>Predicted Class</span>
              <strong>
                {classification.defect_type}
              </strong>
            </div>

            <div>
              <span>Confidence</span>
              <strong>
                {Number(
                  classification.confidence || 0
                ).toFixed(2)}
                %
              </strong>
            </div>

            <div>
              <span>Severity</span>
              <strong>
                {severity.severity_level}
              </strong>
            </div>

            <div>
              <span>Severity Score</span>
              <strong>
                {Number(
                  severity.severity_score || 0
                ).toFixed(2)}
              </strong>
            </div>

            <div>
              <span>Anomaly Score</span>
              <strong>
                {Number(
                  result.anomaly_detection
                    ?.anomaly_score || 0
                ).toFixed(4)}
              </strong>
            </div>

          </div>
        </section>

        {/* Image Quality Analysis */}
        <div className="result-full-width">
          <ImageQualityCard
            imageQuality={result?.image_quality}
          />
        </div>

        <section className="panel">
          <h2>Defect Information</h2>

          <div className="defect-info">
            <div>
              <span>Defect Type</span>
              <strong>
                {classification.defect_type}
              </strong>
            </div>

            <div>
              <span>Localization</span>
              <strong>
                {localization.detected
                  ? "Defect localized"
                  : "No localization"}
              </strong>
            </div>

            <div>
              <span>Defect Area</span>
              <strong>
                {Number(
                  localization.defect_area_percent ||
                  0
                ).toFixed(2)}
                %
              </strong>
            </div>
          </div>

          <div
            className={`interpretation ${quality.decision === "PASS"
                ? "interpretation-pass"
                : "interpretation-fail"
              }`}
          >
            {quality.decision === "PASS" ? (
              <CheckCircle2 size={22} />
            ) : (
              <XCircle size={22} />
            )}

            <div>
              <strong>
                Result Interpretation
              </strong>

              <p>
                {quality.reason ||
                  severity.recommended_action}
              </p>
            </div>
          </div>
        </section>

        <RiskAssessment
          severity={severity}
          decision={quality.decision}
          reason={quality.reason}
          defectType={classification.defect_type}
          confidence={classification.confidence}
        />
      </div>
    </div>
  );
}

export default InspectionResult;