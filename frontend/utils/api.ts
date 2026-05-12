import axios from "axios";

import type {
  AnalyzeResponse,
  AudioBitrate,
  HistoryEntry,
  JobProgress,
  VideoQuality,
} from "@/utils/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, "") || "http://localhost:8000";

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
});

export async function analyzeVideo(url: string): Promise<AnalyzeResponse> {
  const { data } = await api.post<AnalyzeResponse>("/analyze", { url });
  return data;
}

export async function startMp4Download(url: string, quality: VideoQuality): Promise<{ job_id: string }> {
  const { data } = await api.post<{ job_id: string }>("/download/mp4", { url, quality });
  return data;
}

export async function startMp3Download(url: string, bitrate: AudioBitrate): Promise<{ job_id: string }> {
  const { data } = await api.post<{ job_id: string }>("/download/mp3", {
    url,
    bitrate,
    embed_thumbnail: true,
    embed_metadata: true,
  });
  return data;
}

export async function getJobStatus(jobId: string): Promise<JobProgress> {
  const { data } = await api.get<JobProgress>(`/status/${jobId}`);
  return data;
}

export async function pauseJob(jobId: string): Promise<JobProgress> {
  const { data } = await api.post<JobProgress>(`/status/${jobId}/pause`);
  return data;
}

export async function resumeJob(jobId: string): Promise<JobProgress> {
  const { data } = await api.post<JobProgress>(`/status/${jobId}/resume`);
  return data;
}

export async function cancelJob(jobId: string): Promise<JobProgress> {
  const { data } = await api.post<JobProgress>(`/status/${jobId}/cancel`);
  return data;
}

export async function fetchServerHistory(): Promise<HistoryEntry[]> {
  const { data } = await api.get<{ items: HistoryEntry[] }>("/history");
  return data.items;
}

export function buildDownloadUrl(jobId: string): string {
  return `${API_BASE_URL}/download/file/${jobId}`;
}

export async function downloadCompletedFile(jobId: string, filename: string): Promise<void> {
  const response = await api.get(`/download/file/${jobId}`, { responseType: "blob" });
  const blobUrl = window.URL.createObjectURL(response.data);
  const anchor = document.createElement("a");
  anchor.href = blobUrl;
  anchor.download = filename;
  document.body.appendChild(anchor);
  anchor.click();
  anchor.remove();
  window.URL.revokeObjectURL(blobUrl);
}
