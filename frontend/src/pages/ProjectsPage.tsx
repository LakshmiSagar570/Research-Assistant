import { useEffect, useState } from "react";
import { Plus, UserPlus, Trash2, FolderGit2, ShieldAlert, Users, GraduationCap } from "lucide-react";
import AppShell from "../components/AppShell";
import { PageHeader, Card, Button, Badge, EmptyState, Spinner } from "../components/ui";
import { useAuth } from "../auth/AuthContext";
import {
  listProjects,
  createProject,
  listAvailableStudents,
  addStudentToProject,
  removeStudentFromProject,
  type ResearchProject,
  type StudentUser,
} from "../api/client";

export default function ProjectsPage() {
  const { user } = useAuth();
  const isFaculty = user?.role === "faculty" || user?.role === "admin";

  const [projects, setProjects] = useState<ResearchProject[]>([]);
  const [availableStudents, setAvailableStudents] = useState<StudentUser[]>([]);
  const [loading, setLoading] = useState(true);

  // New Project Form State
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [creating, setCreating] = useState(false);

  // Pull Student State
  const [selectedStudentEmail, setSelectedStudentEmail] = useState<Record<string, string>>({});
  const [pullingId, setPullingId] = useState<string | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  useEffect(() => {
    loadData();
  }, []);

  async function loadData() {
    setLoading(true);
    try {
      const projList = await listProjects();
      setProjects(projList);
      if (isFaculty) {
        const studentList = await listAvailableStudents();
        setAvailableStudents(studentList);
      }
    } catch (err: any) {
      console.error("Failed to load projects", err);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreateProject(e: React.FormEvent) {
    e.preventDefault();
    if (!newTitle.trim()) return;
    setCreating(true);
    setErrorMsg(null);
    try {
      const created = await createProject(newTitle.trim(), newDesc.trim());
      setProjects((prev) => [created, ...prev]);
      setNewTitle("");
      setNewDesc("");
      setShowCreateModal(false);
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Failed to create research project");
    } finally {
      setCreating(false);
    }
  }

  async function handlePullStudent(projectId: string) {
    const studentEmail = selectedStudentEmail[projectId];
    if (!studentEmail) return;

    setPullingId(projectId);
    setErrorMsg(null);
    try {
      const updated = await addStudentToProject(projectId, studentEmail);
      setProjects((prev) => prev.map((p) => (p.id === projectId ? updated : p)));
      setSelectedStudentEmail((prev) => ({ ...prev, [projectId]: "" }));
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Failed to pull student to research project");
    } finally {
      setPullingId(null);
    }
  }

  async function handleRemoveStudent(projectId: string, studentId: string) {
    try {
      await removeStudentFromProject(projectId, studentId);
      setProjects((prev) =>
        prev.map((p) =>
          p.id === projectId
            ? { ...p, members: p.members.filter((m) => m.id !== studentId) }
            : p
        )
      );
    } catch (err: any) {
      setErrorMsg(err.response?.data?.detail || "Failed to remove student");
    }
  }

  return (
    <AppShell>
      <PageHeader
        eyebrow="SRS Chapter 4 · Faculty Research & Team Collaboration"
        title="Research Projects & Teams"
        description={
          isFaculty
            ? "Create research projects and pull students into your research teams."
            : "View research projects you have been enrolled in by Faculty advisors."
        }
        action={
          isFaculty ? (
            <Button
              icon={<Plus size={16} />}
              onClick={() => {
                setErrorMsg(null);
                setShowCreateModal(true);
              }}
            >
              New Research Project
            </Button>
          ) : undefined
        }
      />

      <div style={{ padding: "32px 40px" }}>
        {errorMsg && (
          <div
            style={{
              padding: "12px 16px",
              borderRadius: 6,
              background: "var(--accent-soft)",
              color: "var(--accent-strong)",
              fontSize: 13,
              marginBottom: 24,
              display: "flex",
              alignItems: "center",
              gap: 8,
            }}
          >
            <ShieldAlert size={16} />
            {errorMsg}
          </div>
        )}

        {!isFaculty && (
          <div
            style={{
              padding: "14px 18px",
              borderRadius: 6,
              background: "var(--paper-raised)",
              border: "1px solid var(--rule-strong)",
              marginBottom: 24,
              fontSize: 13,
              color: "var(--ink-soft)",
              display: "flex",
              alignItems: "center",
              gap: 12,
            }}
          >
            <GraduationCap size={20} color="var(--accent)" />
            <div>
              <strong>Student Role Policy:</strong> Only Faculty advisors have privileges to create research projects and pull students into teams. You can view projects assigned to you below.
            </div>
          </div>
        )}

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "64px 0" }}>
            <Spinner size={24} />
          </div>
        ) : projects.length === 0 ? (
          <EmptyState
            title={isFaculty ? "No research projects created yet" : "No enrolled research projects"}
            description={
              isFaculty
                ? "Click 'New Research Project' above to create a project and start pulling students into your research team."
                : "You have not been pulled into any research projects by Faculty advisors yet."
            }
          />
        ) : (
          <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
            {projects.map((project) => (
              <Card key={project.id} style={{ padding: 24 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
                  <div>
                    <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
                      <FolderGit2 size={20} color="var(--accent)" />
                      <h2 style={{ fontSize: 18, fontWeight: 600 }}>{project.title}</h2>
                      <Badge tone="accent">{project.members.length} Student Members</Badge>
                    </div>
                    <div style={{ fontSize: 12, color: "var(--ink-faint)", fontFamily: "var(--mono)" }}>
                      Faculty Advisor: {project.faculty_name} · Created: {new Date(project.created_at).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                {project.description && (
                  <p style={{ fontSize: 13.5, color: "var(--ink-soft)", marginBottom: 16, lineHeight: 1.5 }}>
                    {project.description}
                  </p>
                )}

                {/* Team Members Section */}
                <div
                  style={{
                    borderTop: "1px solid var(--rule)",
                    paddingTop: 16,
                    marginTop: 12,
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 6, fontSize: 13, fontWeight: 600, color: "var(--ink)", marginBottom: 10 }}>
                    <Users size={15} />
                    Research Team Members ({project.members.length})
                  </div>

                  {project.members.length === 0 ? (
                    <div style={{ fontSize: 12.5, color: "var(--ink-faint)", fontStyle: "italic", marginBottom: 12 }}>
                      No students pulled into this research project yet.
                    </div>
                  ) : (
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 10, marginBottom: 16 }}>
                      {project.members.map((member) => (
                        <div
                          key={member.id}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            padding: "6px 12px",
                            borderRadius: 20,
                            background: "var(--rule)",
                            fontSize: 12.5,
                            color: "var(--ink)",
                          }}
                        >
                          <span><strong>{member.name}</strong></span>
                          <span style={{ fontSize: 11, color: "var(--ink-faint)" }}>({member.email})</span>
                          {(member.college || member.department) && (
                            <span style={{ fontSize: 10.5, padding: "2px 6px", borderRadius: 4, background: "var(--paper-raised)", border: "1px solid var(--rule-strong)", color: "var(--accent)" }}>
                              {[member.college, member.department].filter(Boolean).join(" · ")}
                            </span>
                          )}
                          {isFaculty && (
                            <button
                              onClick={() => handleRemoveStudent(project.id, member.id)}
                              title="Remove student from research"
                              style={{
                                background: "none",
                                border: "none",
                                cursor: "pointer",
                                padding: 2,
                                color: "var(--ink-faint)",
                                display: "flex",
                              }}
                            >
                              <Trash2 size={13} />
                            </button>
                          )}
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Faculty Action: Pull Student into Research */}
                  {isFaculty && (
                    <div
                      style={{
                        display: "flex",
                        alignItems: "center",
                        gap: 10,
                        marginTop: 12,
                        paddingTop: 12,
                        borderTop: "1px dashed var(--rule)",
                      }}
                    >
                      <UserPlus size={16} color="var(--accent)" />
                      <span style={{ fontSize: 12.5, fontWeight: 600, color: "var(--ink-soft)" }}>
                        Pull Student to Research:
                      </span>
                      <select
                        value={selectedStudentEmail[project.id] || ""}
                        onChange={(e) =>
                          setSelectedStudentEmail((prev) => ({ ...prev, [project.id]: e.target.value }))
                        }
                        style={{
                          fontSize: 12.5,
                          padding: "6px 10px",
                          borderRadius: 4,
                          border: "1px solid var(--rule-strong)",
                          background: "var(--paper-raised)",
                          color: "var(--ink)",
                          minWidth: 260,
                        }}
                      >
                        <option value="">-- Select Student to Pull --</option>
                        {availableStudents
                          .filter((s) => !project.members.some((m) => m.id === s.id))
                          .map((student) => (
                            <option key={student.id} value={student.email}>
                              {student.name} ({student.email}) {student.college || student.department ? `[${[student.college, student.department].filter(Boolean).join(" - ")}]` : ""}
                            </option>
                          ))}
                      </select>
                      <Button
                        size="sm"
                        variant="secondary"
                        disabled={!selectedStudentEmail[project.id] || pullingId === project.id}
                        onClick={() => handlePullStudent(project.id)}
                      >
                        {pullingId === project.id ? "Pulling..." : "Pull Student"}
                      </Button>
                    </div>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Modal for Creating New Research Project */}
      {showCreateModal && (
        <div
          style={{
            position: "fixed",
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            background: "rgba(0, 0, 0, 0.4)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 100,
          }}
        >
          <div
            style={{
              background: "var(--paper-raised)",
              borderRadius: "var(--radius)",
              border: "1px solid var(--rule-strong)",
              padding: 28,
              width: 480,
              maxWidth: "90%",
              boxShadow: "0 12px 32px rgba(0,0,0,0.15)",
            }}
          >
            <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 16 }}>Create New Research Project</h2>
            <form onSubmit={handleCreateProject}>
              <div style={{ marginBottom: 14 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--ink-soft)", marginBottom: 4 }}>
                  Project Title *
                </label>
                <input
                  type="text"
                  required
                  placeholder="e.g., Deep Learning in Biomedical Text Summarization"
                  value={newTitle}
                  onChange={(e) => setNewTitle(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    fontSize: 13.5,
                    borderRadius: 4,
                    border: "1px solid var(--rule-strong)",
                    background: "var(--paper-raised)",
                    color: "var(--ink)",
                  }}
                />
              </div>

              <div style={{ marginBottom: 20 }}>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "var(--ink-soft)", marginBottom: 4 }}>
                  Description / Abstract
                </label>
                <textarea
                  rows={4}
                  placeholder="Outline the research scope, objectives, and assigned literature review tasks..."
                  value={newDesc}
                  onChange={(e) => setNewDesc(e.target.value)}
                  style={{
                    width: "100%",
                    padding: "8px 12px",
                    fontSize: 13.5,
                    borderRadius: 4,
                    border: "1px solid var(--rule-strong)",
                    background: "var(--paper-raised)",
                    color: "var(--ink)",
                    fontFamily: "inherit",
                    resize: "vertical",
                  }}
                />
              </div>

              <div style={{ display: "flex", justifyContent: "flex-end", gap: 10 }}>
                <Button variant="ghost" type="button" onClick={() => setShowCreateModal(false)}>
                  Cancel
                </Button>
                <Button type="submit" disabled={creating || !newTitle.trim()}>
                  {creating ? "Creating..." : "Create Project"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppShell>
  );
}
