import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { ArrowLeft, Download, CheckCircle2, AlertTriangle } from "lucide-react";
import AppShell from "../components/AppShell";
import { Card, Button, Badge, Spinner } from "../components/ui";
import { useAuth } from "../auth/AuthContext";
import {
  api,
  downloadReview,
  approveReview,
  type Review,
  type GapDetectionResult,
} from "../api/client";

function renderMarkdown(md: string): string {
  // Small, deliberate subset renderer matching exactly what the backend
  // review_generator.py produces (headings, bold, bullets, paragraphs).
  const lines = md.split("\n");
  const html: string[] = [];
  for (const raw of lines) {
    const line = raw.trim();
    if (!line) continue;
    if (line.startsWith("### ")) html.push(`<h4>${line.slice(4)}</h4>`);
    else if (line.startsWith("## ")) html.push(`<h3>${line.slice(3)}</h3>`);
    else if (line.startsWith("# ")) html.push(`<h2>${line.slice(2)}</h2>`);
    else if (line.startsWith("*") && line.endsWith("*") && !line.startsWith("**")) {
      html.push(`<p class="italic-note">${line.slice(1, -1)}</p>`);
    } else if (line.startsWith("- ")) {
      html.push(`<li>${boldify(line.slice(2))}</li>`);
    } else {
      html.push(`<p>${boldify(line)}</p>`);
    }
  }
  // wrap consecutive <li> in <ul>
  const wrapped: string[] = [];
  let inList = false;
  for (const el of html) {
    if (el.startsWith("<li>")) {
      if (!inList) {
        wrapped.push("<ul>");
        inList = true;
      }
      wrapped.push(el);
    } else {
      if (inList) {
        wrapped.push("</ul>");
        inList = false;
      }
      wrapped.push(el);
    }
  }
  if (inList) wrapped.push("</ul>");
  return wrapped.join("\n");
}

function boldify(text: string): string {
  return text.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
}

export default function ReviewDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [review, setReview] = useState<Review | null>(null);
  const [gaps, setGaps] = useState<GapDetectionResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [exporting, setExporting] = useState(false);
  const [approving, setApproving] = useState(false);

  useEffect(() => {
    if (!id) return;
    api.get<Review>(`/reviews/${id}`).then(({ data }) => {
      setReview(data);
      try {
        const parsed = JSON.parse(data.gaps_json);
        if (parsed && parsed.total_papers_analyzed) setGaps(parsed);
      } catch {
        /* no gap data */
      }
      setLoading(false);
    });
  }, [id]);

  async function handleExport() {
    if (!review) return;
    setExporting(true);
    try {
      await downloadReview(review.id, review.title);
    } finally {
      setExporting(false);
    }
  }

  async function handleApprove() {
    if (!review) return;
    setApproving(true);
    try {
      const updated = await approveReview(review.id);
      setReview(updated);
    } finally {
      setApproving(false);
    }
  }

  const canApprove = user?.role === "faculty" || user?.role === "admin";

  if (loading) {
    return (
      <AppShell>
        <div style={{ display: "flex", justifyContent: "center", padding: 80 }}>
          <Spinner size={22} />
        </div>
      </AppShell>
    );
  }

  if (!review) {
    return (
      <AppShell>
        <div style={{ padding: 40 }}>Review not found.</div>
      </AppShell>
    );
  }

  return (
    <AppShell>
      <div style={{ padding: "28px 40px 60px", maxWidth: 920 }}>
        <button
          onClick={() => navigate("/reviews")}
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            background: "none",
            border: "none",
            color: "var(--ink-faint)",
            fontSize: 13,
            marginBottom: 20,
            padding: 0,
          }}
        >
          <ArrowLeft size={14} /> Back to reviews
        </button>

        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24, gap: 16 }}>
          <div>
            <div style={{ display: "flex", gap: 8, alignItems: "center", marginBottom: 8 }}>
              {review.status === "approved" ? (
                <Badge tone="well">
                  <CheckCircle2 size={10} style={{ marginRight: 3 }} />
                  approved
                </Badge>
              ) : (
                <Badge tone="neutral">draft</Badge>
              )}
              <span style={{ fontSize: 11.5, color: "var(--ink-faint)", fontFamily: "var(--mono)" }}>
                {new Date(review.created_at).toLocaleDateString()}
              </span>
            </div>
            <h1 style={{ fontSize: 24 }}>{review.title}</h1>
          </div>
          <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
            {canApprove && review.status !== "approved" && (
              <Button variant="secondary" onClick={handleApprove} disabled={approving}>
                {approving ? <Spinner size={13} /> : <CheckCircle2 size={14} />}
                Approve
              </Button>
            )}
            <Button onClick={handleExport} disabled={exporting} icon={exporting ? <Spinner size={13} /> : <Download size={14} />}>
              {exporting ? "Exporting…" : "Export .docx"}
            </Button>
          </div>
        </div>

        {gaps && gaps.candidate_gaps.length > 0 && (
          <Card style={{ marginBottom: 24, background: "var(--gap-soft)", borderColor: "var(--accent-soft)" }}>
            <div style={{ display: "flex", gap: 10, alignItems: "flex-start", marginBottom: 10 }}>
              <AlertTriangle size={15} color="var(--accent)" style={{ flexShrink: 0, marginTop: 2 }} />
              <div>
                <div style={{ fontSize: 13.5, fontWeight: 600, marginBottom: 3 }}>
                  {gaps.candidate_gaps.length} candidate research gap{gaps.candidate_gaps.length !== 1 ? "s" : ""} identified
                </div>
                <p style={{ fontSize: 12, color: "var(--ink-soft)", margin: 0, lineHeight: 1.5 }}>
                  {gaps.disclaimer}
                </p>
              </div>
            </div>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 10 }}>
              {gaps.clusters
                .filter((c) => c.flag === "under_represented")
                .slice(0, 10)
                .map((c) => (
                  <span
                    key={c.keyword}
                    style={{
                      fontFamily: "var(--mono)",
                      fontSize: 11,
                      background: "var(--paper-raised)",
                      border: "1px solid var(--accent-soft)",
                      color: "var(--accent-strong)",
                      padding: "3px 8px",
                      borderRadius: 20,
                    }}
                  >
                    {c.keyword} · {Math.round(c.coverage_ratio * 100)}%
                  </span>
                ))}
            </div>
          </Card>
        )}

        <Card style={{ padding: "36px 44px" }}>
          <article
            className="review-content"
            dangerouslySetInnerHTML={{ __html: renderMarkdown(review.content_markdown) }}
          />
        </Card>
      </div>
    </AppShell>
  );
}
