import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { FileSearch, ArrowRight } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { Button } from "../components/ui";

export default function LoginPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("demo@college.edu");
  const [password, setPassword] = useState("demo1234");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      await signIn(email, password);
      navigate("/");
    } catch {
      setError("Incorrect email or password.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div
      style={{
        minHeight: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        padding: 24,
        position: "relative",
        zIndex: 1,
      }}
    >
      <div style={{ width: "100%", maxWidth: 380, animation: "fadeInUp 0.4s ease" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 32, justifyContent: "center" }}>
          <div
            style={{
              width: 34,
              height: 34,
              borderRadius: 5,
              background: "var(--ink)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
            }}
          >
            <FileSearch size={18} color="var(--paper)" strokeWidth={2} />
          </div>
          <div style={{ fontFamily: "var(--serif)", fontWeight: 600, fontSize: 18 }}>
            Research Assistant
          </div>
        </div>

        <div
          style={{
            background: "var(--paper-raised)",
            border: "1px solid var(--rule)",
            borderRadius: 6,
            padding: "32px 28px",
            boxShadow: "var(--shadow-raised)",
          }}
        >
          <h1 style={{ fontSize: 20, marginBottom: 4 }}>Sign in</h1>
          <p style={{ fontSize: 13, color: "var(--ink-soft)", margin: "0 0 24px" }}>
            For faculty and postgraduate research access.
          </p>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--ink-soft)" }}>Email</span>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                placeholder="you@college.edu"
              />
            </label>
            <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--ink-soft)" }}>Password</span>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                placeholder="••••••••"
              />
            </label>

            {error && (
              <div style={{ fontSize: 12.5, color: "var(--accent)", background: "var(--accent-soft)", padding: "8px 10px", borderRadius: 4 }}>
                {error}
              </div>
            )}

            <Button type="submit" disabled={loading} style={{ marginTop: 6, justifyContent: "center" }}>
              {loading ? "Signing in…" : "Sign in"}
              {!loading && <ArrowRight size={14} />}
            </Button>
          </form>
        </div>

        <p style={{ textAlign: "center", fontSize: 12, color: "var(--ink-faint)", marginTop: 18, fontFamily: "var(--mono)" }}>
          demo account — demo@college.edu / demo1234
        </p>
      </div>
    </div>
  );
}
