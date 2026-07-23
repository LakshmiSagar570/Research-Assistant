import axios from "axios";

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("ara_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

// ---------- Types ----------

export type UserRole = "student" | "faculty" | "admin";

export interface User {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  college?: string;
  department?: string;
  created_at: string;
}

export interface Paper {
  id: string;
  arxiv_id: string;
  title: string;
  abstract: string;
  authors: string;
  link: string;
  source: string;
  categories: string;
  published: string;
  summary: string;
  added_date: string;
}

export interface ReferenceEntry {
  id: string;
  paper_id: string;
  bibtex_entry: string;
  apa_entry: string;
  created_at: string;
  paper: Paper;
}

export interface GapCluster {
  keyword: string;
  frequency: number;
  coverage_ratio: number;
  flag: "under_represented" | "well_covered";
}

export interface GapDetectionResult {
  total_papers_analyzed: number;
  clusters: GapCluster[];
  candidate_gaps: string[];
  disclaimer: string;
}

export interface Review {
  id: string;
  title: string;
  paper_ids: string;
  content_markdown: string;
  gaps_json: string;
  export_path: string;
  status: string;
  created_at: string;
}

// ---------- Auth ----------

export async function login(email: string, password: string) {
  const { data } = await api.post<{ access_token: string; user: User }>("/auth/login", {
    email,
    password,
  });
  return data;
}

export async function register(
  name: string,
  email: string,
  password: string,
  role: UserRole,
  college = "",
  department = ""
) {
  const { data } = await api.post<User>("/auth/register", {
    name,
    email,
    password,
    role,
    college,
    department,
  });
  return data;
}

export async function fetchMe() {
  const { data } = await api.get<User>("/auth/me");
  return data;
}

// ---------- Papers ----------

export async function searchPapers(query: string, maxResults = 10) {
  const { data } = await api.post<Paper[]>("/papers/search", { query, max_results: maxResults });
  return data;
}

export async function summarizePaper(paperId: string, sentenceCount = 4) {
  const { data } = await api.post<Paper>("/papers/summarize", {
    paper_id: paperId,
    sentence_count: sentenceCount,
  });
  return data;
}

export async function listPapers() {
  const { data } = await api.get<Paper[]>("/papers");
  return data;
}

// ---------- References ----------

export async function listReferences() {
  const { data } = await api.get<ReferenceEntry[]>("/references");
  return data;
}

export async function addReference(paperId: string) {
  const { data } = await api.post<ReferenceEntry>("/references", { paper_id: paperId });
  return data;
}

export async function deleteReference(referenceId: string) {
  await api.delete(`/references/${referenceId}`);
}

// ---------- Gap Detection ----------

export async function detectGaps(paperIds: string[]) {
  const { data } = await api.post<GapDetectionResult>("/gaps/detect", { paper_ids: paperIds });
  return data;
}

// ---------- Reviews ----------

export async function generateReview(title: string, paperIds: string[], includeGaps = true) {
  const { data } = await api.post<Review>("/reviews/generate", {
    title,
    paper_ids: paperIds,
    include_gap_analysis: includeGaps,
  });
  return data;
}

export async function listReviews() {
  const { data } = await api.get<Review[]>("/reviews");
  return data;
}

export async function downloadReview(reviewId: string, filename: string) {
  const response = await api.get(`/reviews/${reviewId}/download`, { responseType: "blob" });
  const url = URL.createObjectURL(new Blob([response.data]));
  const a = document.createElement("a");
  a.href = url;
  a.download = `${filename.replace(/\s+/g, "_")}.docx`;
  a.click();
  URL.revokeObjectURL(url);
}

export async function approveReview(reviewId: string) {
  const { data } = await api.post<Review>(`/reviews/${reviewId}/approve`);
  return data;
}

// ---------- Projects ----------

export interface StudentUser {
  id: string;
  name: string;
  email: string;
  college?: string;
  department?: string;
}

export interface ResearchProject {
  id: string;
  title: string;
  description: string;
  faculty_id: string;
  faculty_name: string;
  created_at: string;
  members: StudentUser[];
}

export async function listProjects() {
  const { data } = await api.get<ResearchProject[]>("/projects");
  return data;
}

export async function createProject(title: string, description: string) {
  const { data } = await api.post<ResearchProject>("/projects", { title, description });
  return data;
}

export async function listAvailableStudents() {
  const { data } = await api.get<StudentUser[]>("/projects/students");
  return data;
}

export async function addStudentToProject(projectId: string, studentEmail: string) {
  const { data } = await api.post<ResearchProject>(`/projects/${projectId}/students`, {
    student_email: studentEmail,
  });
  return data;
}

export async function removeStudentFromProject(projectId: string, studentId: string) {
  await api.delete(`/projects/${projectId}/students/${studentId}`);
}
