import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { FileText, Sparkles, ChevronRight, CheckCircle2 } from "lucide-react";
import AppShell from "../components/AppShell";
import { PageHeader, Card, Button, Badge, EmptyState, Spinner } from "../components/ui";
import {
  listPapers,
  listReviews,
  generateReview,
  type Paper,
  type Review,
} from "../api/client";

export default function ReviewsPage() {
  const navigate = useNavigate();
  const [papers, setPapers] = useState<Paper[]>([]);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([listPapers(), listReviews()])
      .then(([p, r]) => {
        setPapers(p);
        setReviews(r);
      })
      .finally(() => setLoading(false));
  }, []);

  function toggle(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  async function handleGenerate() {
    if (!title.trim() || selected.size === 0) return;
    setGenerating(true);
    setError(null);
    try {
      const review = await generateReview(title, Array.from(selected), true);
      navigate(`/reviews/${review.id}`);
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Could not generate review. Try again.");
    } finally {
      setGenerating(false);
    }
  }

  return (
    <AppShell>
      <PageHeader
        eyebrow="FR5 · FR6 · FR8"
        title="Literature reviews"
        description="Select papers from your library to generate a structured draft with thematic grouping and candidate gap analysis."
      />

      <div style={{ padding: "24px 40px 60px", display: "grid", gridTemplateColumns: "1fr 380px", gap: 28 }}>
        {/* Left: paper picker */}
        <div>
          <h2 style={{ fontSize: 14, fontWeight: 600, color: "var(--ink-soft)", marginBottom: 12 }}>
            Select papers ({selected.size} chosen)
          </h2>

          {loading && (
            <div style={{ display: "flex", justifyContent: "center", padding: 40 }}>
              <Spinner size={20} />
            </div>
          )}

          {!loading && papers.length === 0 && (
            <EmptyState
              title="No papers available yet"
              description="Search and save at least two papers before generating a review."
            />
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {papers.map((paper) => {
              const isSelected = selected.has(paper.id);
              return (
                <Card
                  key={paper.id}
                  padded={false}
                  style={{
                    padding: "14px 16px",
                    cursor: "pointer",
                    borderColor: isSelected ? "var(--accent)" : "var(--rule)",
                    background: isSelected ? "var(--accent-soft)" : "var(--paper-raised)",
                  }}
                >
                  <label style={{ display: "flex", gap: 12, cursor: "pointer", alignItems: "flex-start" }}>
                    <input
                      type="checkbox"
                      checked={isSelected}
                      onChange={() => toggle(paper.id)}
                      style={{ marginTop: 3, width: 15, height: 15, padding: 0, accentColor: "var(--accent)" }}
                    />
                    <div style={{ minWidth: 0, flex: 1 }}>
                      <div style={{ fontSize: 13.5, fontWeight: 500, lineHeight: 1.4 }}>{paper.title}</div>
                      <div style={{ fontSize: 11.5, color: "var(--ink-faint)", fontFamily: "var(--mono)", marginTop: 4 }}>
                        {paper.categories.split(",")[0]?.trim()} · {paper.published?.slice(0, 10)}
                      </div>
                    </div>
                  </label>
                </Card>
              );
            })}
          </div>
        </div>

        {/* Right: generator panel + existing reviews */}
        <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
          <Card>
            <h3 style={{ fontSize: 13.5, marginBottom: 12 }}>Generate new review</h3>
            <input
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              placeholder="Review title, e.g. Survey of DNS-based Threat Detection"
              style={{ width: "100%", marginBottom: 10 }}
            />
            {selected.size > 0 && selected.size < 2 && (
              <p style={{ fontSize: 11.5, color: "var(--ink-faint)", margin: "0 0 10px" }}>
                Select at least 2 papers to enable gap analysis.
              </p>
            )}
            {error && (
              <p style={{ fontSize: 12, color: "var(--accent)", margin: "0 0 10px" }}>{error}</p>
            )}
            <Button
              onClick={handleGenerate}
              disabled={!title.trim() || selected.size === 0 || generating}
              style={{ width: "100%", justifyContent: "center" }}
              icon={generating ? <Spinner size={13} /> : <Sparkles size={14} />}
            >
              {generating ? "Generating…" : "Generate review"}
            </Button>
          </Card>

          <div>
            <h3 style={{ fontSize: 13, fontWeight: 600, color: "var(--ink-soft)", marginBottom: 10 }}>
              Past reviews
            </h3>
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {reviews.length === 0 && (
                <p style={{ fontSize: 12.5, color: "var(--ink-faint)" }}>None generated yet.</p>
              )}
              {reviews.map((r) => (
                <Card
                  key={r.id}
                  padded={false}
                  style={{ padding: "12px 14px", cursor: "pointer" }}
                >
                  <a
                    href={`/reviews/${r.id}`}
                    onClick={(e) => {
                      e.preventDefault();
                      navigate(`/reviews/${r.id}`);
                    }}
                    style={{ textDecoration: "none", color: "inherit", display: "flex", alignItems: "center", gap: 10 }}
                  >
                    <FileText size={14} color="var(--ink-faint)" style={{ flexShrink: 0 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 500, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {r.title}
                      </div>
                      <div style={{ display: "flex", gap: 6, marginTop: 4, alignItems: "center" }}>
                        {r.status === "approved" ? (
                          <Badge tone="well">
                            <CheckCircle2 size={10} style={{ marginRight: 3 }} />
                            approved
                          </Badge>
                        ) : (
                          <Badge tone="neutral">draft</Badge>
                        )}
                      </div>
                    </div>
                    <ChevronRight size={14} color="var(--ink-faint)" style={{ flexShrink: 0 }} />
                  </a>
                </Card>
              ))}
            </div>
          </div>
        </div>
      </div>
    </AppShell>
  );
}
