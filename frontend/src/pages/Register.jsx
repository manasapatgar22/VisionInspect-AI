import { useState } from "react";
import { Factory, ArrowLeft } from "lucide-react";

function Register({
  onRegister,
  loading,
  error,
  onBack
}) {
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] =
    useState("quality_engineer");

  const submit = (e) => {
    e.preventDefault();

    onRegister({
      username,
      email,
      password,
      role
    });
  };

  return (
    <div className="auth-simple-page">
      <div className="register-card">
        <div className="register-brand">
          <Factory size={35} />
          <div>
            <strong>VisionInspect-AI</strong>
            <span>Create your account</span>
          </div>
        </div>

        <button
          className="back-button"
          onClick={onBack}
        >
          <ArrowLeft size={17} />
          Back to Login
        </button>

        <h1>Create Account</h1>

        <p>
          Register a new VisionInspect-AI user.
        </p>

        <form onSubmit={submit}>
          <label>Username</label>
          <input
            value={username}
            onChange={(e) =>
              setUsername(e.target.value)
            }
            placeholder="Enter username"
            required
          />

          <label>Email</label>
          <input
            type="email"
            value={email}
            onChange={(e) =>
              setEmail(e.target.value)
            }
            placeholder="Enter email"
            required
          />

          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) =>
              setPassword(e.target.value)
            }
            placeholder="Create password"
            required
          />

          <label>Role</label>

          <select
            value={role}
            onChange={(e) =>
              setRole(e.target.value)
            }
          >
            <option value="quality_engineer">
              Quality Engineer
            </option>

            <option value="factory_supervisor">
              Factory Supervisor
            </option>
          </select>

          {error && (
            <div className="form-error">
              {error}
            </div>
          )}

          <button
            className="primary-button"
            disabled={loading}
          >
            {loading
              ? "Creating..."
              : "Create Account"}
          </button>
        </form>
      </div>
    </div>
  );
}

export default Register;