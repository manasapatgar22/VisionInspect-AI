import {
  Bell,
  ChevronDown
} from "lucide-react";

function Topbar({ user }) {
  const roleLabel =
    user?.role === "factory_supervisor"
      ? "Factory Supervisor"
      : "Quality Engineer";

  return (
    <header className="topbar-new">
      <div className="mobile-brand">
        VisionInspect-AI
      </div>

      <div className="topbar-actions">
        <button className="notification-button">
          <Bell size={21} />
          <span className="notification-dot"></span>
        </button>

        <div className="user-menu">
          <div className="avatar">
            {user?.username?.charAt(0)?.toUpperCase() || "Q"}
          </div>

          <div className="user-details">
            <strong>{roleLabel}</strong>
            <span>{user?.username || "User"}</span>
          </div>

          <ChevronDown size={17} />
        </div>
      </div>
    </header>
  );
}

export default Topbar;