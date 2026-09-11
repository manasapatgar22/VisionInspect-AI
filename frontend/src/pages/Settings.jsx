function Settings() {
  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Settings</h1>
          <p>
            Configure your VisionInspect-AI workspace.
          </p>
        </div>
      </div>

      <section className="panel settings-card">
        <h2>Inspection Preferences</h2>

        <div className="setting-row">
          <div>
            <strong>Image Quality Analysis</strong>
            <p>
              Analyze sharpness, brightness, contrast
              and resolution during inspection.
            </p>
          </div>

          <span className="enabled-pill">
            Enabled
          </span>
        </div>

        <div className="setting-row">
          <div>
            <strong>AI Anomaly Detection</strong>
            <p>
              ResNet18 feature-distance anomaly
              detection.
            </p>
          </div>

          <span className="enabled-pill">
            Enabled
          </span>
        </div>

        <div className="setting-row">
          <div>
            <strong>Severity Assessment</strong>
            <p>
              Automated quality risk and severity
              scoring.
            </p>
          </div>

          <span className="enabled-pill">
            Enabled
          </span>
        </div>
      </section>
    </div>
  );
}

export default Settings;