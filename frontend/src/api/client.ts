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

export async function register(name: string, email: string, password: string, role: UserRole) {
  const { data } = await api.post<User>("/auth/register", { name, email, password, role });
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

export async function exportReview(reviewId: string) {
  const { data } = await api.post<Review>(`/reviews/${reviewId}/export`);
  return data;
}

export function downloadReviewUrl(reviewId: string) {
  return `${API_BASE}/reviews/${reviewId}/download`;
}

export async function approveReview(reviewId: string) {
  const { data } = await api.post<Review>(`/reviews/${reviewId}/approve`);
  return data;
}
