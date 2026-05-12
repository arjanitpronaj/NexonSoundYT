export type VideoQuality = "360p" | "480p" | "720p" | "1080p" | "2k" | "4k" | "best";
export type AudioBitrate = "128" | "192" | "320";
export type DownloadFormat = "mp4" | "mp3";
export type JobStatus =
  | "queued"
  | "analyzing"
  | "downloading"
  | "processing"
  | "completed"
  | "failed"
  | "cancelled"
  | "paused";

export interface FormatInfo {
  quality: string;
  ext: string;
  filesize?: number | null;
  filesize_approx?: number | null;
  vcodec?: string | null;
  acodec?: string | null;
  fps?: number | null;
  height?: number | null;
  width?: number | null;
}

export interface AnalyzeResponse {
  url: string;
  title: string;
  channel: string;
  upload_date?: string | null;
  duration: number;
  thumbnail?: string | null;
  description?: string | null;
  view_count?: number | null;
  formats: FormatInfo[];
  estimated_sizes: Record<string, number | null>;
}

export interface JobProgress {
  job_id: string;
  status: JobStatus;
  progress: number;
  speed?: string | null;
  eta?: string | null;
  downloaded_bytes?: number | null;
  total_bytes?: number | null;
  filename?: string | null;
  error?: string | null;
  retries?: number;
  format?: string | null;
  quality?: string | null;
  title?: string | null;
  created_at: number;
  updated_at: number;
}

export interface HistoryEntry {
  id: string;
  url: string;
  title: string;
  format: string;
  quality: string;
  status: JobStatus;
  filename?: string | null;
  completed_at?: number | null;
  thumbnail?: string | null;
}

export interface QueueItem {
  id: string;
  jobId?: string;
  url: string;
  title: string;
  thumbnail?: string | null;
  format: DownloadFormat;
  quality: string;
  status: JobStatus;
  progress: number;
  speed?: string | null;
  eta?: string | null;
  error?: string | null;
  createdAt: number;
}

export interface ToastMessage {
  id: string;
  type: "success" | "error" | "info";
  message: string;
}
