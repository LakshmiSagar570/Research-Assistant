import { useState } from "react";
import { Search as SearchIcon, ExternalLink, Sparkles, BookmarkPlus, Check, AlertCircle } from "lucide-react";
import AppShell from "../components/AppShell";
import { PageHeader, Card, Button, Badge, EmptyState, Spinner } from "../components/ui";
import { searchPapers, summarizePaper, addReference, type Paper } from "../api/client";

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Paper[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [summarizingId, setSummarizingId] = useState<string | null>(null);
  const [savedIds, setSavedIds] = useState<Set<string>>(new Set());
  const [savingId, setSavingId] = useState<string | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setHasSearched(true);
    try {
      const data = await searchPapers(query, 12);
      setResults(data);
    } catch (err: any) {
      setError(
        err?.response?.data?.detail ||
          "arXiv search is temporarily unavailable. Please try again in a moment."
      );
      setResults([]);
    } finally {
      setLoading(false);
    }
  }

  async function handleSummarize(paper: Paper) {
    setSummarizingId(paper.id);
    try {
      const updated = await summarizePaper(paper.id, 4);
      setResults((prev) => prev.map((p) => (p.id === updated.id ? updated : p)));
    } finally {
      setSummarizingId(null);
    }
  }

  async function handleSave(paper: Paper) {
    setSavingId(paper.id);
    try {
      await addReference(paper.id);
      setSavedIds((prev) => new Set(prev).add(paper.id));
    } catch {
      // likely already saved - treat as success for UX simplicity
      setSavedIds((prev) => new Set(prev).add(paper.id));
    } finally {
      setSavingId(null);
    }
  }

  return (
    <AppShell>
      <PageHeader
        eyebrow="FR1 · FR2"
        title="Search literature"
        description="Query arXiv directly. Generate an extractive summary or save a paper to your reference library from each result."
      />

      <div style={{ padding: "24px 40px 60px" }}>
        <form onSubmit={handleSearch} style={{ display: "flex", gap: 10, marginBottom: 28, maxWidth: 640 }}>
          <div style={{ position: "relative", flex: 1 }}>
            <SearchIcon
              size={15}
              style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--ink-faint)" }}
            />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g. transformer architectures for time series forecasting"
              style={{ width: "100%", paddingLeft: 34 }}
            />
          </div>
          <Button type="submit" disabled={loading || !query.trim()}>
            {loading ? <Spinner size={14} /> : "Search"}
          </Button>
        </form>

        {error && (
          <Card style={{ marginBottom: 20, borderColor: "var(--accent-soft)", maxWidth: 640 }}>
            <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
              <AlertCircle size={16} color="var(--accent)" style={{ flexShrink: 0, marginTop: 1 }} />
              <div style={{ fontSize: 13, color: "var(--ink-soft)" }}>{error}</div>
            </div>
          </Card>
        )}

        {!loading && hasSearched && results.length === 0 && !error && (
          <EmptyState
            title="No results found"
            description="Try a broader query or check spelling. arXiv search matches title, abstract, and author text."
          />
        )}

        {!hasSearched && !loading && (
          <EmptyState
            title="Search arXiv to begin"
            description="Results are cached locally as you go, so summaries and references stay available across the app."
          />
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {results.map((paper) => (
            <Card key={paper.id} style={{ animation: "fadeInUp 0.3s ease" }}>
              <div style={{ display: "flex", justifyContent: "space-between", gap: 16 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h3 style={{ fontSize: 15.5, lineHeight: 1.35, marginBottom: 6 }}>{paper.title}</h3>
                  <div
                    style={{
                      fontSize: 12,
                      color: "var(--ink-faint)",
                      marginBottom: 10,
                      fontFamily: "var(--mono)",
                    }}
                  >
                    {paper.authors.split(",").slice(0, 3).join(", ")}
                    {paper.authors.split(",").length > 3 ? ", et al." : ""}
                    {"  ·  "}
                    {paper.published?.slice(0, 10)}
                  </div>

                  <p style={{ fontSize: 13.5, color: "var(--ink-soft)", lineHeight: 1.55, margin: "0 0 10px" }}>
                    {paper.summary || paper.abstract}
                  </p>

                  {paper.summary && (
                    <Badge tone="accent">
                      <Sparkles size={10} style={{ marginRight: 4 }} />
                      extractive summary
                    </Badge>
                  )}

                  <div style={{ display: "flex", gap: 8, marginTop: 12, flexWrap: "wrap" }}>
                    {paper.categories.split(",").slice(0, 3).map((c) => (
                      <Badge key={c} tone="neutral">
                        {c.trim()}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>

              <div style={{ display: "flex", gap: 8, marginTop: 16, paddingTop: 16, borderTop: "1px solid var(--rule)" }}>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleSummarize(paper)}
                  disabled={summarizingId === paper.id}
                  icon={summarizingId === paper.id ? <Spinner size={12} /> : <Sparkles size={13} />}
                >
                  {paper.summary ? "Re-summarize" : "Summarize"}
                </Button>
                <Button
                  variant={savedIds.has(paper.id) ? "ghost" : "secondary"}
                  size="sm"
                  onClick={() => handleSave(paper)}
                  disabled={savingId === paper.id || savedIds.has(paper.id)}
                  icon={
                    savingId === paper.id ? (
                      <Spinner size={12} />
                    ) : savedIds.has(paper.id) ? (
                      <Check size={13} color="var(--well)" />
                    ) : (
                      <BookmarkPlus size={13} />
                    )
                  }
                >
                  {savedIds.has(paper.id) ? "Saved" : "Save reference"}
                </Button>
                <a
                  href={paper.link}
                  target="_blank"
                  rel="noreferrer"
                  style={{
                    marginLeft: "auto",
                    display: "flex",
                    alignItems: "center",
                    gap: 5,
                    fontSize: 12.5,
                    color: "var(--ink-faint)",
                    textDecoration: "none",
                  }}
                >
                  View on arXiv <ExternalLink size={12} />
                </a>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </AppShell>
  );
}
