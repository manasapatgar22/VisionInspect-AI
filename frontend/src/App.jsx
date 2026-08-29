import { useEffect, useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [statistics, setStatistics] = useState({
    total_inspections: 0,
    passed: 0,
    failed: 0,
    critical: 0
  });

  // --- Auth state ---
  const [token, setToken] = useState(
    () => localStorage.getItem("vi_token") || ""
  );
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  const handleLogin = async (event) => {
    event.preventDefault();
    setAuthError("");
    setAuthLoading(true);

    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password })
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Login failed.");
      }

      localStorage.setItem("vi_token", data.access_token);
      setToken(data.access_token);
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("vi_token");
    setToken("");
  };
  useEffect(() => {
    fetch("/api/analytics/statistics")
      .then((response) => response.json())
      .then((data) => {
        setStatistics(data);
      })
      .catch((error) => {
        console.error(
          "Unable to load statistics:",
          error
        );
      });
  }, []);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    setFile(selectedFile);
    setResult(null);
    setError("");

    setPreview(
      URL.createObjectURL(selectedFile)
    );
  };

  const inspectImage = async () => {
    if (!file) {
      setError("Please select an image first.");
      return;
    }

    setLoading(true);
    setError("");
    setResult(null);

    try {
      const formData = new FormData();

      formData.append("file", file);

            const response = await fetch(
        "/api/inspection/inspect",
        {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`
          },
          body: formData
        }
      );

      const data = await response.json();

      if (response.status === 401) {
        handleLogout();
        throw new Error("Session expired. Please log in again.");
      }

      if (!response.ok) {
        throw new Error(
          data.detail || "Inspection failed."
        );
      }

      setResult(data);

    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // Maps a severity level string to a CSS class suffix, for badge/progress coloring.
  const severityClass = (level) => {
    if (!level) return "unknown";
    return level.toString().toLowerCase();
  };

  if (!token) {
    return (
      <div className="auth-shell">
        <div className="auth-card">
          <div className="auth-brand">
            <span className="brand-mark">VI</span>
            <div>
              <h1>VisionInspect AI</h1>
              <p>Manufacturing Quality Inspection</p>
            </div>
          </div>

          <form onSubmit={handleLogin} className="auth-form">
            <label className="field-label">Username</label>
            <input
              type="text"
              placeholder="Enter username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
            />

            <label className="field-label">Password</label>
            <input
              type="password"
              placeholder="Enter password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />

            {authError && <div className="auth-error">{authError}</div>}

            <button type="submit" disabled={authLoading} className="auth-submit">
              {authLoading ? "Signing in..." : "Sign in"}
            </button>

            <p className="auth-hint">
              No account? Register via <code>POST /api/auth/register</code> in the Swagger docs first.
            </p>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="topbar">
        <div className="brand">
          <span className="brand-mark">VI</span>
          <div>
            <h1>VisionInspect AI</h1>
            <p>AI-powered manufacturing quality inspection</p>
          </div>
        </div>

        <div className="topbar-right">
          <div className="status">
            <span className="status-dot"></span>
            System Online
          </div>
          <button onClick={handleLogout} className="logout-button">
            Log out
          </button>
        </div>
      </header>

      <section className="stats-grid">

        <div className="stat-card stat-total">
          <span>Total Inspections</span>
          <strong>{statistics.total_inspections}</strong>
        </div>

        <div className="stat-card stat-passed">
          <span>Passed</span>
          <strong>{statistics.passed}</strong>
        </div>

        <div className="stat-card stat-failed">
          <span>Failed</span>
          <strong>{statistics.failed}</strong>
        </div>

        <div className="stat-card stat-critical">
          <span>Critical</span>
          <strong>{statistics.critical}</strong>
        </div>

      </section>

      <main className="content-grid">

        <section className="upload-card">

          <h2>Product Inspection</h2>

          <p className="description">
            Upload a product image to detect manufacturing
            defects and assess quality.
          </p>

          <label className="upload-area">

            <input
              type="file"
              accept="image/*"
              onChange={handleFileChange}
            />

            <div className="upload-content">
              <div className="upload-icon">
                ↑
              </div>

              <strong>
                Choose product image
              </strong>

              <span>
                PNG, JPG or JPEG
              </span>
            </div>

          </label>

          {preview && (
            <div className="preview-section">

              <div className="image-container">

                <img
                  src={preview}
                  alt="Selected product"
                  className="inspection-image"
                />

                {result?.localization?.detected &&
                  result.localization.bounding_box && (
                    <div
                      className="defect-box"
                      style={{
                        left: `${result.localization.bounding_box.x / 256 * 100}%`,
                        top: `${result.localization.bounding_box.y / 256 * 100}%`,
                        width: `${result.localization.bounding_box.width / 256 * 100}%`,
                        height: `${result.localization.bounding_box.height / 256 * 100}%`
                      }}
                    >
                      <span>Defect</span>
                    </div>
                  )}

              </div>

              <div className="preview-info">

                <strong>{file?.name}</strong>

                <p>
                  {result
                    ? "Inspection completed"
                    : "Ready for inspection"}
                </p>

              </div>

            </div>
          )}

          <button
            className="inspect-button"
            onClick={inspectImage}
            disabled={!file || loading}
          >
            {loading
              ? "Analyzing..."
              : "Run AI Inspection"}
          </button>

          {error && (
            <div className="error">
              {error}
            </div>
          )}

        </section>

        {result ? (
          <section className="results">

            <div className="result-header">

              <div>
                <h2>Inspection Result</h2>

                <p>
                  {result.inspection.filename}
                </p>
              </div>

              <div
                className={
                  result.quality_control.decision === "FAIL"
                    ? "decision fail"
                    : "decision pass"
                }
              >
                {result.quality_control.decision}
              </div>

            </div>

            <div className="metrics">

              <div className="metric">
                <span>Defect Type</span>
                <strong>
                  {result.classification.defect_type}
                </strong>
              </div>

              <div className="metric">
                <span>Confidence</span>
                <strong>
                  {result.classification.confidence}%
                </strong>
              </div>

              <div className="metric">
                <span>Anomaly Score</span>
                <strong>
                  {result.anomaly_detection.anomaly_score}
                </strong>
              </div>

              <div className="metric">
                <span>Severity</span>
                <strong className={`severity-badge severity-${severityClass(result.severity.severity_level)}`}>
                  {result.severity.severity_level}
                </strong>
              </div>

            </div>

            <div className="severity">

              <div className="severity-title">
                <span>Severity Score</span>

                <strong>
                  {result.severity.severity_score}/100
                </strong>
              </div>

              <div className="progress">
                <div
                  className={`progress-bar progress-${severityClass(result.severity.severity_level)}`}
                  style={{
                    width: `${Math.min(
                      result.severity.severity_score,
                      100
                    )}%`
                  }}
                />
              </div>

            </div>

            <div className="recommendation">

              <span>
                Recommended Action
              </span>

              <strong>
                {result.severity.recommended_action}
              </strong>

            </div>

          </section>
        ) : (
          <section className="results results-empty">
            <div className="empty-state">
              <div className="empty-icon">⬡</div>
              <h2>Awaiting Inspection</h2>
              <p>Upload a product image and run an inspection to see results here.</p>
            </div>
          </section>
        )}

      </main>

      <footer>
        VisionInspect AI • Intelligent Quality Inspection
      </footer>

    </div>
  );
}

export default App;