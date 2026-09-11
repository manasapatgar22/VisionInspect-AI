import { useState } from "react";
import {
  Factory,
  Mail,
  Lock,
  Eye,
  EyeOff,
  ShieldCheck,
  BarChart3,
  Settings
} from "lucide-react";

function Login({
  onLogin,
  loading,
  error,
  onRegister
}) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] =
    useState(false);

  const submit = (e) => {
    e.preventDefault();

    onLogin(username, password);
  };

  return (
    <div className="login-page">
      <header className="login-header">
        <div className="login-brand">
          <Factory size={38} />

          <div>
            <strong>VisionInspect-AI</strong>
            <span>AI-Powered Quality Inspection</span>
          </div>
        </div>

        <nav>
          <span>Home</span>
          <span>About</span>
          <span>Contact</span>
        </nav>
      </header>

      <main className="login-main">
        <section className="login-intro">
          <h1>
            Smarter Quality
            <br />
            for a Better Tomorrow
          </h1>

          <p>
            Automated defect detection for
            manufacturing excellence
          </p>

          <div className="factory-illustration">
            <Factory size={100} strokeWidth={1.2} />
            <div className="inspection-beam"></div>
          </div>

          <div className="login-features">
            <div>
              <ShieldCheck />
              <span>Detect<br />Defects</span>
            </div>

            <div>
              <BarChart3 />
              <span>Improve<br />Quality</span>
            </div>

            <div>
              <Settings />
              <span>Increase<br />Efficiency</span>
            </div>
          </div>
        </section>

        <section className="login-card">
          <h2>Welcome Back</h2>

          <p className="login-subtitle">
            Sign in to your VisionInspect-AI account
          </p>

          <form onSubmit={submit}>
            <label>Username</label>

            <div className="input-wrapper">
              <Mail size={19} />

              <input
                type="text"
                placeholder="Enter your username"
                value={username}
                onChange={(e) =>
                  setUsername(e.target.value)
                }
                required
              />
            </div>

            <label>Password</label>

            <div className="input-wrapper">
              <Lock size={19} />

              <input
                type={
                  showPassword
                    ? "text"
                    : "password"
                }
                placeholder="Enter your password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                required
              />

              <button
                type="button"
                className="password-toggle"
                onClick={() =>
                  setShowPassword(!showPassword)
                }
              >
                {showPassword ? (
                  <EyeOff size={19} />
                ) : (
                  <Eye size={19} />
                )}
              </button>
            </div>

            {error && (
              <div className="form-error">
                {error}
              </div>
            )}

            <div className="forgot-row">
              <button
                type="button"
                onClick={() =>
                  alert(
                    "Password reset is not available in the current backend."
                  )
                }
              >
                Forgot Password?
              </button>
            </div>

            <button
              type="submit"
              className="primary-button login-button"
              disabled={loading}
            >
              {loading
                ? "Signing in..."
                : "Login"}
            </button>
          </form>

          <div className="or-divider">
            <span>OR</span>
          </div>

          <button
            className="register-button"
            onClick={onRegister}
          >
            Don't have an account?
            <strong>Register</strong>
          </button>
        </section>
      </main>

      <footer className="login-footer">
        <span>
          © 2026 VisionInspect-AI. All rights reserved.
        </span>

        <span>
          Building smarter factories with AI&nbsp; | &nbsp;
          Version 2.0
        </span>
      </footer>
    </div>
  );
}

export default Login;