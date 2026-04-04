import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const links = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/subjects", label: "Subjects" },
  { to: "/exams", label: "Exams" },
  { to: "/tasks", label: "Tasks" },
];

export default function Layout() {
  const { logout } = useAuth();
  const navigate = useNavigate();

  const onLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <Link to="/dashboard" className="brand">
          ExamPulse
        </Link>
        <nav className="nav-links">
          {links.map((link) => (
            <NavLink key={link.to} to={link.to} className="nav-link">
              {link.label}
            </NavLink>
          ))}
        </nav>
        <button className="btn" onClick={onLogout}>
          Logout
        </button>
      </header>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
