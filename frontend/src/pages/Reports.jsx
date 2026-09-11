import {
  FileText,
  Download,
  Database
} from "lucide-react";

import { getExportUrl } from "../services/api";

function Reports() {
  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Production Quality Reports</h1>
          <p>
            Export inspection results for quality
            management and manufacturing analysis.
          </p>
        </div>
      </div>

      <div className="reports-grid">
        <section className="report-card">
          <div className="report-icon">
            <FileText />
          </div>

          <div>
            <h2>Production Quality PDF</h2>

            <p>
              Management-ready summary containing
              inspection statistics and recent
              inspection records.
            </p>

            <a
              className="primary-button report-button"
              href={getExportUrl("pdf")}
              target="_blank"
              rel="noreferrer"
            >
              <Download size={17} />
              Download PDF
            </a>
          </div>
        </section>

        <section className="report-card">
          <div className="report-icon">
            <Database />
          </div>

          <div>
            <h2>Inspection Data CSV</h2>

            <p>
              Raw inspection records containing
              defect, anomaly, severity, quality and
              inspection metadata.
            </p>

            <a
              className="primary-button report-button"
              href={getExportUrl("csv")}
              target="_blank"
              rel="noreferrer"
            >
              <Download size={17} />
              Download CSV
            </a>
          </div>
        </section>
      </div>
    </div>
  );
}

export default Reports;