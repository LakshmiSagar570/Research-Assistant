import { type ReactNode } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { Search, BookMarked, FileText, LayoutGrid, LogOut, FileSearch, FolderGit2 } from "lucide-react";
import { useAuth } from "../auth/AuthContext";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutGrid, end: true },
  { to: "/projects", label: "Research Projects", icon: FolderGit2 },
  { to: "/search", label: "Search", icon: Search },
  { to: "/references", label: "References", icon: BookMarked },
  { to: "/reviews", label: "Reviews", icon: FileText },
];

export default function AppShell({ children }: { children: ReactNode }) {
  const { user, signOut } = useAuth();
  const navigate = useNavigate();

  function handleSignOut() {
    signOut();
    navigate("/login");
  }

  return (
    <div style={{ display: "flex", minHeight: "100vh", position: "relative", zIndex: 1 }}>
      <aside
        style={{
          width: 244,
          flexShrink: 0,
          borderRight: "1px solid var(--rule)",
          background: "var(--paper-raised)",
          display: "flex",
          flexDirection: "column",
          position: "sticky",
          top: 0,
          height: "100vh",
        }}
      >
        <div style={{ padding: "28px 24px 20px" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <div
              style={{
                width: 30,
                height: 30,
                borderRadius: 4,
                background: "var(--ink)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0,
              }}
            >
              <FileSearch size={16} color="var(--paper)" strokeWidth={2} />
            </div>
            <div>
              <div style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: 15, lineHeight: 1.15 }}>
                Research
              </div>
              <div style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: 15, lineHeight: 1.15 }}>
                Assistant
              </div>
            </div>
          </div>
        </div>

        <nav style={{ padding: "8px 14px", display: "flex", flexDirection: "column", gap: 2, flex: 1 }}>
          {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
            <NavLink
              key={to}
              to={to}
              end={end}
              style={({ isActive }) => ({
                display: "flex",
                alignItems: "center",
                gap: 10,
                padding: "9px 12px",
                borderRadius: 4,
                fontSize: 13.5,
                fontWeight: 500,
                textDecoration: "none",
                color: isActive ? "var(--paper-raised)" : "var(--ink-soft)",
                background: isActive ? "var(--ink)" : "transparent",
                transition: "background 0.12s, color 0.12s",
              })}
            >
              <Icon size={16} strokeWidth={2} />
              {label}
            </NavLink>
          ))}
        </nav>

        <div style={{ padding: "14px", borderTop: "1px solid var(--rule)" }}>
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 10,
              padding: "8px 10px",
              borderRadius: 4,
            }}
          >
            <div
              style={{
                width: 28,
                height: 28,
                borderRadius: "50%",
                background: "var(--accent-soft)",
                color: "var(--accent)",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                fontSize: 12,
                fontWeight: 700,
                flexShrink: 0,
                fontFamily: "var(--serif)",
              }}
            >
              {user?.name?.[0]?.toUpperCase() ?? "?"}
            </div>
            <div style={{ minWidth: 0, flex: 1 }}>
              <div
                style={{
                  fontSize: 12.5,
                  fontWeight: 600,
                  whiteSpace: "nowrap",
                  overflow: "hidden",
                  textOverflow: "ellipsis",
                }}
              >
                {user?.name}
              </div>
              <div
                style={{
                  fontSize: 11,
                  color: "var(--ink-faint)",
                  fontFamily: "var(--mono)",
                  textTransform: "uppercase",
                  letterSpacing: "0.04em",
                }}
              >
                {user?.role}
              </div>
            </div>
            <button
              onClick={handleSignOut}
              title="Sign out"
              style={{
                background: "none",
                border: "none",
                color: "var(--ink-faint)",
                padding: 6,
                borderRadius: 4,
                display: "flex",
              }}
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      <main style={{ flex: 1, minWidth: 0 }}>{children}</main>
    </div>
  );
}
