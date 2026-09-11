import {
  LayoutDashboard,
  Camera,
  History,
  BarChart3,
  FileText,
  UserCircle,
  Settings,
  LogOut,
  Factory
} from "lucide-react";

function Sidebar({
  activePage,
  setActivePage,
  role,
  onLogout
}) {
  const engineerItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: LayoutDashboard
    },
    {
      id: "inspection",
      label: "New Inspection",
      icon: Camera
    },
    {
      id: "history",
      label: "Inspection History",
      icon: History
    },
    {
      id: "analytics",
      label: "Analytics",
      icon: BarChart3
    },
    {
      id: "reports",
      label: "Reports",
      icon: FileText
    }
  ];

  const supervisorItems = [
    {
      id: "dashboard",
      label: "Dashboard",
      icon: LayoutDashboard
    },
    {
      id: "history",
      label: "Inspection History",
      icon: History
    },
    {
      id: "analytics",
      label: "Production Analytics",
      icon: BarChart3
    },
    {
      id: "reports",
      label: "Reports",
      icon: FileText
    }
  ];

  const items =
    role === "factory_supervisor"
      ? supervisorItems
      : engineerItems;

  return (
    <aside className="sidebar">
      <div className="sidebar-brand">
        <div className="brand-icon">
          <Factory size={25} />
        </div>

        <div>
          <strong>VisionInspect-AI</strong>
          <span>AI-Powered Quality Inspection</span>
        </div>
      </div>

      <nav className="sidebar-nav">
        {items.map((item) => {
          const Icon = item.icon;

          return (
            <button
              key={item.id}
              className={
                activePage === item.id
                  ? "nav-item active"
                  : "nav-item"
              }
              onClick={() => setActivePage(item.id)}
            >
              <Icon size={20} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>

      <div className="sidebar-bottom">
        <button
          className="nav-item"
          onClick={() => setActivePage("profile")}
        >
          <UserCircle size={20} />
          <span>Profile</span>
        </button>

        <button
          className="nav-item"
          onClick={() => setActivePage("settings")}
        >
          <Settings size={20} />
          <span>Settings</span>
        </button>

        <button
          className="nav-item logout-nav"
          onClick={onLogout}
        >
          <LogOut size={20} />
          <span>Logout</span>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;