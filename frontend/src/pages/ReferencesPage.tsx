import { useEffect, useState } from "react";
import { Trash2, Copy, Check } from "lucide-react";
import AppShell from "../components/AppShell";
import { PageHeader, Card, Button, EmptyState, Spinner } from "../components/ui";
import { listReferences, deleteReference, type ReferenceEntry } from "../api/client";

export default function ReferencesPage() {
  const [references, setReferences] = useState<ReferenceEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [format, setFormat] = useState<"bibtex" | "apa">("bibtex");
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [deletingId, setDeletingId] = useState<string | null>(null);

  useEffect(() => {
    listReferences()
      .then(setReferences)
      .finally(() => setLoading(false));
  }, []);

  async function handleDelete(id: string) {
    setDeletingId(id);
    try {
      await deleteReference(id);
      setReferences((prev) => prev.filter((r) => r.id !== id));
    } finally {
      setDeletingId(null);
    }
  }

  function handleCopy(id: string, text: string) {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 1500);
  }

  function handleExportAll() {
    const content = references
      .map((r) => (format === "bibtex" ? r.bibtex_entry : r.apa_entry))
      .join(format === "bibtex" ? "\n\n" : "\n");
    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = format === "bibtex" ? "references.bib" : "references_apa.txt";
    a.click();
    URL.revokeObjectURL(url);
  }

  return (
    <AppShell>
      <PageHeader
        eyebrow="FR3 · FR4 · FR8"
        title="Reference library"
        description="Citations generated automatically for every saved paper. Export the full library in BibTeX or APA."
        action={
          references.length > 0 && (
            <div style={{ display: "flex", gap: 8 }}>
              <select value={format} onChange={(e) => setFormat(e.target.value as "bibtex" | "apa")}>
                <option value="bibtex">BibTeX</option>
                <option value="apa">APA</option>
              </select>
              <Button variant="secondary" onClick={handleExportAll}>
                Export all
              </Button>
            </div>
          )
        }
      />

      <div style={{ padding: "24px 40px 60px" }}>
        {loading && (
          <div style={{ display: "flex", justifyContent: "center", padding: 60 }}>
            <Spinner size={20} />
          </div>
        )}

        {!loading && references.length === 0 && (
          <EmptyState
            title="No references saved yet"
            description="Search for papers and click “Save reference” to build your library here."
          />
        )}

        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {references.map((ref) => {
            const entryText = format === "bibtex" ? ref.bibtex_entry : ref.apa_entry;
            return (
              <Card key={ref.id}>
                <div style={{ display: "flex", justifyContent: "space-between", gap: 16, marginBottom: 10 }}>
                  <div style={{ minWidth: 0 }}>
                    <h3 style={{ fontSize: 14.5, lineHeight: 1.4 }}>{ref.paper.title}</h3>
                    <div style={{ fontSize: 11.5, color: "var(--ink-faint)", fontFamily: "var(--mono)", marginTop: 4 }}>
                      {ref.paper.authors.split(",")[0]}
                      {ref.paper.authors.split(",").length > 1 ? ", et al." : ""} · {ref.paper.arxiv_id}
                    </div>
                  </div>
                  <button
                    onClick={() => handleDelete(ref.id)}
                    disabled={deletingId === ref.id}
                    style={{
                      background: "none",
                      border: "none",
                      color: "var(--ink-faint)",
                      padding: 4,
                      flexShrink: 0,
                      height: "fit-content",
                    }}
                    title="Remove reference"
                  >
                    {deletingId === ref.id ? <Spinner size={14} /> : <Trash2 size={14} />}
                  </button>
                </div>

                <div
                  style={{
                    background: "var(--paper)",
                    border: "1px solid var(--rule)",
                    borderRadius: 4,
                    padding: "10px 12px",
                    fontFamily: "var(--mono)",
                    fontSize: 12,
                    color: "var(--ink-soft)",
                    lineHeight: 1.6,
                    whiteSpace: "pre-wrap",
                    wordBreak: "break-word",
                    position: "relative",
                  }}
                >
                  {entryText}
                  <button
                    onClick={() => handleCopy(ref.id, entryText)}
                    style={{
                      position: "absolute",
                      top: 8,
                      right: 8,
                      background: "var(--paper-raised)",
                      border: "1px solid var(--rule-strong)",
                      borderRadius: 4,
                      padding: 5,
                      display: "flex",
                    }}
                    title="Copy to clipboard"
                  >
                    {copiedId === ref.id ? <Check size={12} color="var(--well)" /> : <Copy size={12} />}
                  </button>
                </div>
              </Card>
            );
          })}
        </div>
      </div>
    </AppShell>
  );
}
