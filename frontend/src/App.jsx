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

    if (!token) {
    return (
      <div className="app">
        <header className="header">
          <div>
            <h1>VisionInspect AI</h1>
            <p>Sign in to run an inspection</p>
          </div>
        </header>
        <form onSubmit={handleLogin} style={{ maxWidth: 320, margin: "40px auto" }}>
          <div style={{ marginBottom: 12 }}>
            <input
              type="text"
              placeholder="Username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              style={{ width: "100%", padding: 8 }}
              required
            />
          </div>
          <div style={{ marginBottom: 12 }}>
            <input
              type="password"
              placeholder="Password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              style={{ width: "100%", padding: 8 }}
              required
            />
          </div>
          {authError && <p style={{ color: "red" }}>{authError}</p>}
          <button type="submit" disabled={authLoading} style={{ width: "100%", padding: 8 }}>
            {authLoading ? "Signing in..." : "Sign in"}
          </button>
          <p style={{ fontSize: 12, marginTop: 8, color: "#666" }}>
            No account? Register via POST /api/auth/register (Swagger docs) first.
          </p>
        </form>
      </div>
    );
  }

  return (
    <div className="app">
      <button onClick={handleLogout} style={{ float: "right", margin: 8 }}>
        Log out
      </button>
      <section className="dashboard-stats">

        <div className="stat-card">
          <span>Total Inspections</span>
          <strong>
            {statistics.total_inspections}
          </strong>
        </div>

        <div className="stat-card">
          <span>Passed</span>
          <strong>
            {statistics.passed}
          </strong>
        </div>

        <div className="stat-card">
          <span>Failed</span>
          <strong>
            {statistics.failed}
          </strong>
        </div>

        <div className="stat-card">
          <span>Critical</span>
          <strong>
            {statistics.critical}
          </strong>
        </div>

      </section>

      <header className="header">
        <div>
          <h1>VisionInspect AI</h1>
          <p>
            AI-powered manufacturing quality inspection
          </p>
        </div>

        <div className="status">
          <span className="status-dot"></span>
          System Online
        </div>
      </header>

      <main className="container">

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

        {result && (
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
                <strong>
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
                  className="progress-bar"
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
        )}

      </main>

      <footer>
        VisionInspect AI • Intelligent Quality Inspection
      </footer>

    </div>
  );
}

export default App;
