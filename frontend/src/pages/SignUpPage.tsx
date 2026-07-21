import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { FileSearch, ArrowRight } from "lucide-react";
import { useAuth } from "../auth/AuthContext";
import { Button } from "../components/ui";
import { register, type UserRole } from "../api/client";

export default function SignUpPage() {
  const { signIn } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<UserRole>("student");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    setLoading(true);
    try {
      await register(name, email, password, role);
      // Registration succeeded - log the user straight in rather than
      // making them re-type credentials on a separate screen.
      await signIn(email, password);
      navigate("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not create account. Try again.");
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
          <h1 style={{ fontSize: 20, marginBottom: 4 }}>Create account</h1>
          <p style={{ fontSize: 13, color: "var(--ink-soft)", margin: "0 0 24px" }}>
            Register for faculty or student research access.
          </p>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 14 }}>
            <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--ink-soft)" }}>Full name</span>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
                minLength={2}
                placeholder="Your name"
              />
            </label>
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
                minLength={6}
                placeholder="At least 6 characters"
              />
            </label>
            <label style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              <span style={{ fontSize: 12, fontWeight: 600, color: "var(--ink-soft)" }}>Role</span>
              <select value={role} onChange={(e) => setRole(e.target.value as UserRole)}>
                <option value="student">Student</option>
                <option value="faculty">Faculty</option>
              </select>
            </label>

            {error && (
              <div style={{ fontSize: 12.5, color: "var(--accent)", background: "var(--accent-soft)", padding: "8px 10px", borderRadius: 4 }}>
                {error}
              </div>
            )}

            <Button type="submit" disabled={loading} style={{ marginTop: 6, justifyContent: "center" }}>
              {loading ? "Creating account…" : "Create account"}
              {!loading && <ArrowRight size={14} />}
            </Button>
          </form>
        </div>

        <p style={{ textAlign: "center", fontSize: 13, color: "var(--ink-soft)", marginTop: 18 }}>
          Already have an account?{" "}
          <Link to="/login" style={{ color: "var(--accent)", fontWeight: 600, textDecoration: "none" }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
