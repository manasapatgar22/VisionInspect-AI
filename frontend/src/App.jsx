import { useEffect, useState } from "react";
import {
  LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

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
  const [trend, setTrend] = useState([]);
  const [defectDistribution, setDefectDistribution] = useState([]);
  const [severityDistribution, setSeverityDistribution] = useState([]);

  // --- Category state ---
  const [categories, setCategories] = useState(["bottle"]);
  const [category, setCategory] = useState("bottle");

  // --- Auth state ---
  const [token, setToken] = useState(
    () => localStorage.getItem("vi_token") || ""
  );
  const [role, setRole] = useState(
    () => localStorage.getItem("vi_role") || ""
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
      localStorage.setItem("vi_role", data.user.role);

      setToken(data.access_token);
      setRole(data.user.role);
    } catch (err) {
      setAuthError(err.message);
    } finally {
      setAuthLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("vi_token");
    localStorage.removeItem("vi_role");

    setToken("");
    setRole("");
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

  useEffect(() => {
    fetch("/api/analytics/trend")
      .then((response) => response.json())
      .then((data) => setTrend(data.trend || []))
      .catch((error) => console.error("Unable to load trend:", error));

    fetch("/api/analytics/defect-distribution")
      .then((response) => response.json())
      .then((data) => setDefectDistribution(data.distribution || []))
      .catch((error) => console.error("Unable to load defect distribution:", error));

    fetch("/api/analytics/severity-distribution")
      .then((response) => response.json())
      .then((data) => setSeverityDistribution(data.distribution || []))
      .catch((error) => console.error("Unable to load severity distribution:", error));
  }, []);

  useEffect(() => {
    fetch("/api/inspection/categories")
      .then((response) => response.json())
      .then((data) => {
        if (data.categories && data.categories.length > 0) {
          setCategories(data.categories);

          if (!data.categories.includes(category)) {
            setCategory(data.categories[0]);
          }
        }
      })
      .catch((error) => {
        console.error(
          "Unable to load categories:",
          error
        );
      });
    // eslint-disable-next-line react-hooks/exhaustive-deps
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
    if (role !== "quality_engineer") {
      setError("Only quality engineers can run inspections.");
      return;
    }
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
      formData.append("category", category);

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

  const formatCategoryLabel = (name) => {
    return name
      .split("_")
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(" ");
  };
  const SEVERITY_COLORS = {
    Critical: "#dc2626",
    High: "#ea580c",
    Medium: "#eab308",
    Low: "#16a34a",
    unknown: "#94a3b8"
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

      {role === "quality_engineer" ? (

        <main className="content-grid">

          <section className="upload-card">

            <h2>Product Inspection</h2>

            <p className="description">
              Upload a product image to detect manufacturing
              defects and assess quality.
            </p>

            <label className="field-label">Product Category</label>

            <select
              className="category-select"
              value={category}
              onChange={(e) => {
                setCategory(e.target.value);
                setResult(null);
              }}
            >
              {categories.map((name) => (
                <option key={name} value={name}>
                  {formatCategoryLabel(name)}
                </option>
              ))}
            </select>

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
                    {result.category &&
                      ` • ${formatCategoryLabel(result.category)}`}
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

                  <strong
                    className={`severity-badge severity-${severityClass(
                      result.severity.severity_level
                    )}`}
                  >
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
                    className={`progress-bar progress-${severityClass(
                      result.severity.severity_level
                    )}`}
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

                <div className="empty-icon">
                  ⬡
                </div>

                <h2>
                  Awaiting Inspection
                </h2>

                <p>
                  Upload a product image and run an inspection
                  to see results here.
                </p>

              </div>

            </section>
          )}


        </main>
      ) : (
        <main className="content-grid supervisor-view">

          <section className="analytics-card">
            <h2>Inspection Trend</h2>
            <p className="description">Daily pass / fail / review counts.</p>

            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="PASS" stroke="#16a34a" strokeWidth={2} />
                <Line type="monotone" dataKey="FAIL" stroke="#dc2626" strokeWidth={2} />
                <Line type="monotone" dataKey="REVIEW" stroke="#eab308" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </section>

          <section className="analytics-card">
            <h2>Defect Type Distribution</h2>
            <p className="description">Count of inspections by predicted defect type.</p>

            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={defectDistribution}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="defect_type" />
                <YAxis allowDecimals={false} />
                <Tooltip />
                <Bar dataKey="count" fill="#2563eb" />
              </BarChart>
            </ResponsiveContainer>
          </section>

          <section className="analytics-card">
            <h2>Severity Distribution</h2>
            <p className="description">Share of inspections by severity level.</p>

            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie
                  data={severityDistribution}
                  dataKey="count"
                  nameKey="severity_level"
                  outerRadius={100}
                  label
                >
                  {severityDistribution.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={SEVERITY_COLORS[entry.severity_level] || SEVERITY_COLORS.unknown}
                    />
                  ))}
                </Pie>
                <Tooltip />
                <Legend />
              </PieChart>
            </ResponsiveContainer>
          </section>
          <section className="analytics-card export-card">
            <h2>Production Quality Report</h2>
            <p className="description">Download the current inspection data.</p>

            <div className="export-buttons">
              <a href="/api/analytics/export/csv" className="export-button">
                Download CSV
              </a>
              <a href="/api/analytics/export/pdf" className="export-button">
                Download PDF
              </a>
            </div>
          </section>
        </main>
      )}


      <footer>
        VisionInspect AI • Intelligent Quality Inspection
      </footer>

    </div>
  );
}

export default App;