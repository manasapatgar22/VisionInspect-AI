import { UserCircle } from "lucide-react";

function Profile({ user }) {
  const role =
    user?.role === "factory_supervisor"
      ? "Factory Supervisor"
      : "Quality Engineer";

  return (
    <div>
      <div className="page-heading">
        <div>
          <h1>Profile</h1>
          <p>Your VisionInspect-AI account information.</p>
        </div>
      </div>

      <section className="panel profile-card">
        <UserCircle size={70} />

        <div>
          <h2>{user?.username}</h2>
          <p>{user?.email}</p>

          <span className="role-pill">
            {role}
          </span>
        </div>
      </section>
    </div>
  );
}

export default Profile;