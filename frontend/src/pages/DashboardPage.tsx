import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Search, BookMarked, FileText, ArrowRight } from "lucide-react";
import AppShell from "../components/AppShell";
import { PageHeader, Card, Button } from "../components/ui";
import { useAuth } from "../auth/AuthContext";
import { listPapers, listReferences, listReviews, type Paper, type ReferenceEntry, type Review } from "../api/client";

export default function DashboardPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [references, setReferences] = useState<ReferenceEntry[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);

  useEffect(() => {
    listPapers().then(setPapers);
    listReferences().then(setReferences);
    listReviews().then(setReviews);
  }, []);

  const stats = [
    { label: "Papers cached", value: papers.length, icon: Search, to: "/search" },
    { label: "Saved references", value: references.length, icon: BookMarked, to: "/references" },
    { label: "Reviews generated", value: reviews.length, icon: FileText, to: "/reviews" },
  ];

  return (
    <AppShell>
      <PageHeader
        eyebrow={`Welcome back, ${user?.name?.split(" ")[0] ?? ""}`}
        title="Research workspace"
        description="Search literature, manage citations, and draft structured reviews — all from one place."
      />

      <div style={{ padding: "24px 40px 60px" }}>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 16, marginBottom: 32 }}>
          {stats.map(({ label, value, icon: Icon, to }) => (
            <Card
              key={label}
              style={{ cursor: "pointer" }}
            >
              <div onClick={() => navigate(to)}>
                <div
                  style={{
                    width: 32,
                    height: 32,
                    borderRadius: 6,
                    background: "var(--accent-soft)",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    marginBottom: 14,
                  }}
                >
                  <Icon size={16} color="var(--accent)" strokeWidth={2} />
                </div>
                <div style={{ fontFamily: "var(--serif)", fontSize: 28, fontWeight: 600, lineHeight: 1 }}>
                  {value}
                </div>
                <div style={{ fontSize: 12.5, color: "var(--ink-soft)", marginTop: 6 }}>{label}</div>
              </div>
            </Card>
          ))}
        </div>

        <Card style={{ background: "var(--ink)", border: "none" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", gap: 24 }}>
            <div>
              <h2 style={{ fontSize: 17, color: "var(--paper)", marginBottom: 6 }}>
                Start a new literature search
              </h2>
              <p style={{ fontSize: 13, color: "#c9c4b4", margin: 0, maxWidth: 420 }}>
                Query arXiv, summarize abstracts, and build your reference library in a few clicks.
              </p>
            </div>
            <Button
              onClick={() => navigate("/search")}
              style={{ background: "var(--paper)", color: "var(--ink)", flexShrink: 0 }}
              icon={<ArrowRight size={14} />}
            >
              Go to search
            </Button>
          </div>
        </Card>

        {reviews.length > 0 && (
          <div style={{ marginTop: 32 }}>
            <h2 style={{ fontSize: 14, fontWeight: 600, color: "var(--ink-soft)", marginBottom: 12 }}>
              Recent reviews
            </h2>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {reviews.slice(0, 3).map((r) => (
                <Card
                  key={r.id}
                  padded={false}
                  style={{ padding: "14px 18px", cursor: "pointer" }}
                >
                  <div onClick={() => navigate(`/reviews/${r.id}`)} style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                    <span style={{ fontSize: 13.5, fontWeight: 500 }}>{r.title}</span>
                    <ArrowRight size={14} color="var(--ink-faint)" />
                  </div>
                </Card>
              ))}
            </div>
          </div>
        )}
      </div>
    </AppShell>
  );
}
