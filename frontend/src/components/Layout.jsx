import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col">
      <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur">
        <div className="mx-auto flex h-14 max-w-4xl items-center justify-between px-4">
          <Link to="/chat" className="text-lg font-semibold text-amber-400">
            RAG Chatbot
          </Link>
          <nav className="flex items-center gap-4">
            <Link to="/chat" className="text-slate-300 hover:text-white">
              Chat
            </Link>
            {user?.role === "admin" && (
              <Link to="/admin/documents" className="text-slate-300 hover:text-white">
                Documents
              </Link>
            )}
            <span className="text-slate-500">{user?.email}</span>
            <button
              onClick={handleLogout}
              className="rounded bg-slate-700 px-3 py-1.5 text-sm text-slate-200 hover:bg-slate-600"
            >
              Logout
            </button>
          </nav>
        </div>
      </header>
      <main className="flex-1">{children}</main>
    </div>
  );
}
