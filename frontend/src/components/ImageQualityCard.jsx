import React from "react";
import {
  CheckCircle,
  AlertTriangle,
  XCircle,
  Camera,
  Maximize,
  Sun,
  Contrast,
  Focus
} from "lucide-react";

const formatIssue = (issue) => {
  const names = {
    low_resolution: "Low Resolution",
    blurry: "Blurry Image",
    too_dark: "Too Dark",
    overexposed: "Overexposed",
    low_contrast: "Low Contrast"
  };

  return names[issue] || issue.replaceAll("_", " ");
};

const getRatingInfo = (rating) => {
  switch (rating?.toLowerCase()) {
    case "good":
      return {
        icon: CheckCircle,
        label: "Good",
        className: "quality-good"
      };

    case "acceptable":
      return {
        icon: AlertTriangle,
        label: "Acceptable",
        className: "quality-acceptable"
      };

    case "poor":
      return {
        icon: XCircle,
        label: "Poor",
        className: "quality-poor"
      };

    default:
      return {
        icon: AlertTriangle,
        label: "Unknown",
        className: "quality-acceptable"
      };
  }
};

const Metric = ({ icon: Icon, label, value, unit = "" }) => (
  <div className="quality-metric">
    <div className="quality-metric-icon">
      <Icon size={20} />
    </div>

    <div className="quality-metric-content">
      <span>{label}</span>
      <strong>
        {value}
        {unit && <small> {unit}</small>}
      </strong>
    </div>
  </div>
);

export default function ImageQualityCard({ imageQuality }) {
  if (!imageQuality) {
    return null;
  }

  const ratingInfo = getRatingInfo(imageQuality.rating);
  const RatingIcon = ratingInfo.icon;

  const score = Number(imageQuality.quality_score ?? 0);

  const width = imageQuality.resolution?.width ?? "-";
  const height = imageQuality.resolution?.height ?? "-";

  const issues = Array.isArray(imageQuality.issues)
    ? imageQuality.issues
    : [];

  return (
    <div className="image-quality-card">

      {/* Header */}
      <div className="image-quality-header">
        <div>
          <div className="section-title-row">
            <Camera size={22} />
            <h3>Image Quality Analysis</h3>
          </div>

          <p>
            Pre-inspection analysis of the uploaded image
          </p>
        </div>

        <div className={`quality-rating ${ratingInfo.className}`}>
          <RatingIcon size={18} />
          <span>{ratingInfo.label}</span>
        </div>
      </div>

      {/* Score */}
      <div className="quality-score-section">

        <div className="quality-score-circle">
          <div className="quality-score-value">
            {score}
          </div>
          <div className="quality-score-label">
            / 100
          </div>
        </div>

        <div className="quality-score-info">
          <h4>Overall Image Quality</h4>

          <div className="quality-progress">
            <div
              className="quality-progress-fill"
              style={{
                width: `${Math.min(Math.max(score, 0), 100)}%`
              }}
            />
          </div>

          <p>
            {score >= 80
              ? "The image quality is suitable for reliable inspection."
              : score >= 50
              ? "The image is usable, but some quality limitations are present."
              : "The image quality is poor and may affect inspection reliability."}
          </p>
        </div>

      </div>

      {/* Metrics */}
      <div className="quality-metrics">

        <Metric
          icon={Maximize}
          label="Resolution"
          value={`${width} × ${height}`}
          unit="px"
        />

        <Metric
          icon={Focus}
          label="Sharpness"
          value={imageQuality.sharpness ?? "-"}
        />

        <Metric
          icon={Sun}
          label="Brightness"
          value={imageQuality.brightness ?? "-"}
        />

        <Metric
          icon={Contrast}
          label="Contrast"
          value={imageQuality.contrast ?? "-"}
        />

      </div>

      {/* Issues */}
      <div className="quality-issues">

        <h4>Detected Quality Issues</h4>

        {issues.length === 0 ? (
          <div className="no-quality-issues">
            <CheckCircle size={18} />
            <span>No image quality issues detected</span>
          </div>
        ) : (
          <div className="quality-issue-list">
            {issues.map((issue, index) => (
              <div className="quality-issue" key={index}>
                <AlertTriangle size={16} />
                <span>{formatIssue(issue)}</span>
              </div>
            ))}
          </div>
        )}

      </div>

    </div>
  );
}