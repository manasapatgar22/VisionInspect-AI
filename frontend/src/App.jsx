import { useEffect, useState } from "react";

import Login from "./pages/Login";
import Register from "./pages/Register";
import EngineerDashboard from "./pages/EngineerDashboard";
import SupervisorDashboard from "./pages/SupervisorDashboard";
import NewInspection from "./pages/NewInspection";
import InspectionHistory from "./pages/InspectionHistory";
import InspectionResult from "./pages/InspectionResult";
import Analytics from "./pages/Analytics";
import Reports from "./pages/Reports";
import Profile from "./pages/Profile";
import Settings from "./pages/Settings";

import Sidebar from "./components/Sidebar";
import Topbar from "./components/Topbar";

import {
  login,
  registerUser,
  getStatistics,
  getTrend,
  getDefectDistribution,
  getSeverityDistribution,
  getHistory
} from "./services/api";

function App() {
  const [token, setToken] = useState(
    () =>
      localStorage.getItem("vi_token") || ""
  );

  const [user, setUser] = useState(() => {
    const saved =
      localStorage.getItem("vi_user");

    return saved
      ? JSON.parse(saved)
      : null;
  });

  const [page, setPage] =
    useState("dashboard");

  const [authScreen, setAuthScreen] =
    useState("login");

  const [authLoading, setAuthLoading] =
    useState(false);

  const [authError, setAuthError] =
    useState("");

  const [statistics, setStatistics] =
    useState({
      total_inspections: 0,
      passed: 0,
      failed: 0,
      critical: 0
    });

  const [trend, setTrend] =
    useState([]);

  const [defects, setDefects] =
    useState([]);

  const [severity, setSeverity] =
    useState([]);

  const [inspections, setInspections] =
    useState([]);

  const [inspectionResult, setInspectionResult] =
    useState(null);

  const [inspectionPreview, setInspectionPreview] =
    useState(null);

  const [loadingData, setLoadingData] =
    useState(false);

  useEffect(() => {
    if (!token) return;

    loadDashboardData();
  }, [token]);

  async function loadDashboardData() {
    setLoadingData(true);

    try {
      const [
        stats,
        trendData,
        defectData,
        severityData,
        historyData
      ] = await Promise.all([
        getStatistics(),
        getTrend(),
        getDefectDistribution(),
        getSeverityDistribution(),
        getHistory(100)
      ]);

      setStatistics(stats);
      setTrend(trendData.trend || []);
      setDefects(
        defectData.distribution || []
      );
      setSeverity(
        severityData.distribution || []
      );
      setInspections(
        historyData.inspections || []
      );
    } catch (error) {
      console.error(
        "Unable to load dashboard data:",
        error
      );
    } finally {
      setLoadingData(false);
    }
  }

  async function handleLogin(
    username,
    password
  ) {
    setAuthLoading(true);
    setAuthError("");

    try {
      const data = await login(
        username,
        password
      );

      localStorage.setItem(
        "vi_token",
        data.access_token
      );

      localStorage.setItem(
        "vi_user",
        JSON.stringify(data.user)
      );

      localStorage.setItem(
        "vi_role",
        data.user.role
      );

      setToken(data.access_token);
      setUser(data.user);
      setPage("dashboard");
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleRegister(
    userData
  ) {
    setAuthLoading(true);
    setAuthError("");

    try {
      await registerUser(userData);

      setAuthScreen("login");
      setAuthError(
        "Registration successful. Please log in."
      );
    } catch (error) {
      setAuthError(error.message);
    } finally {
      setAuthLoading(false);
    }
  }

  function handleLogout() {
    localStorage.removeItem("vi_token");
    localStorage.removeItem("vi_user");
    localStorage.removeItem("vi_role");

    setToken("");
    setUser(null);
    setInspectionResult(null);
    setInspectionPreview(null);
    setPage("dashboard");
  }

  function handleInspectionResult(
    result,
    preview
  ) {
    setInspectionResult(result);
    setInspectionPreview(preview);
    setPage("result");

    loadDashboardData();
  }

  function handleViewInspection(record) {
    /*
     * Historical records contain analytics data but
     * the current backend does not persist the original
     * uploaded image. Therefore history opens the
     * available record details in a lightweight view.
     */

    setInspectionResult({
      inspection: {
        filename: record.filename
      },
      category: record.category,
      anomaly_detection: {
        anomaly_score: record.anomaly_score
      },
      classification: {
        defect_type: record.defect_type,
        confidence: record.confidence
      },
      severity: {
        severity_score:
          record.severity_score,
        severity_level:
          record.severity_level
      },
      quality_control: {
        decision: record.decision,
        reason:
          "Historical inspection record."
      },
      localization: {
        detected: false,
        bounding_box: null,
        defect_area_percent: 0
      },
      image_quality: {
        score:
          record.image_quality_score,
        rating:
          record.image_quality_rating,
        issues:
          record.image_quality_issues || []
      }
    });

    setInspectionPreview(null);
    setPage("result");
  }

  if (!token) {
    if (authScreen === "register") {
      return (
        <Register
          onRegister={handleRegister}
          loading={authLoading}
          error={authError}
          onBack={() => {
            setAuthScreen("login");
            setAuthError("");
          }}
        />
      );
    }

    return (
      <Login
        onLogin={handleLogin}
        loading={authLoading}
        error={authError}
        onRegister={() => {
          setAuthScreen("register");
          setAuthError("");
        }}
      />
    );
  }

  function renderPage() {
    if (page === "dashboard") {
      if (
        user?.role ===
        "factory_supervisor"
      ) {
        return (
          <SupervisorDashboard
            statistics={statistics}
            trend={trend}
            defects={defects}
            inspections={inspections}
            onViewInspection={
              handleViewInspection
            }
          />
        );
      }

      return (
        <EngineerDashboard
          statistics={statistics}
          defects={defects}
          inspections={inspections}
          onViewInspection={
            handleViewInspection
          }
        />
      );
    }

    if (page === "inspection") {
      return (
        <NewInspection
          token={token}
          onResult={handleInspectionResult}
        />
      );
    }

    if (page === "history") {
      return (
        <InspectionHistory
          inspections={inspections}
          onView={handleViewInspection}
        />
      );
    }

    if (page === "result") {
      return (
        <InspectionResult
          result={inspectionResult}
          preview={inspectionPreview}
          onBack={() =>
            setPage("history")
          }
          onNewInspection={() => {
            setInspectionResult(null);
            setInspectionPreview(null);
            setPage("inspection");
          }}
        />
      );
    }

    if (page === "analytics") {
      return (
        <Analytics
          statistics={statistics}
          trend={trend}
          defects={defects}
          severity={severity}
        />
      );
    }

    if (page === "reports") {
      return <Reports />;
    }

    if (page === "profile") {
      return <Profile user={user} />;
    }

    if (page === "settings") {
      return <Settings />;
    }

    return null;
  }

  return (
    <div className="application-shell">
      <Sidebar
        activePage={page}
        setActivePage={setPage}
        role={user?.role}
        onLogout={handleLogout}
      />

      <div className="main-area">
        <Topbar user={user} />

        <main className="page-content">
          {loadingData && (
            <div className="loading-line">
              Updating production data...
            </div>
          )}

          {renderPage()}
        </main>

        <footer className="app-footer">
          <span>
            © 2026 VisionInspect-AI
          </span>

          <span>
            AI-Powered Manufacturing Quality
            Inspection
          </span>
        </footer>
      </div>
    </div>
  );
}

export default App;