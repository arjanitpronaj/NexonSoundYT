"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  cancelJob,
  downloadCompletedFile,
  getJobStatus,
  pauseJob,
  resumeJob,
  startMp3Download,
  startMp4Download,
} from "@/utils/api";
import { upsertHistory } from "@/utils/storage";
import type { AudioBitrate, DownloadFormat, QueueItem, VideoQuality } from "@/utils/types";

const MAX_PARALLEL = 3;
const POLL_INTERVAL_MS = 1200;

interface EnqueuePayload {
  url: string;
  title: string;
  thumbnail?: string | null;
  format: DownloadFormat;
  quality: string;
}

function createQueueId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `queue-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

export function useDownloadQueue(
  onToast: (type: "success" | "error" | "info", message: string) => void,
  onHistoryUpdate?: () => void,
) {
  const [queue, setQueue] = useState<QueueItem[]>([]);
  const queueRef = useRef(queue);
  const pollingRef = useRef<Record<string, number>>({});

  useEffect(() => {
    queueRef.current = queue;
  }, [queue]);

  const updateItem = useCallback((id: string, patch: Partial<QueueItem>) => {
    setQueue((current) => current.map((item) => (item.id === id ? { ...item, ...patch } : item)));
  }, []);

  const enqueue = useCallback((payload: EnqueuePayload) => {
    const item: QueueItem = {
      id: createQueueId(),
      url: payload.url,
      title: payload.title,
      thumbnail: payload.thumbnail,
      format: payload.format,
      quality: payload.quality,
      status: "queued",
      progress: 0,
      createdAt: Date.now(),
    };
    setQueue((current) => [...current, item]);
    onToast("info", `${payload.title} added to queue`);
    return item.id;
  }, [onToast]);

  const startJob = useCallback(async (item: QueueItem) => {
    try {
      updateItem(item.id, { status: "analyzing", progress: 0, error: null });
      const response =
        item.format === "mp4"
          ? await startMp4Download(item.url, item.quality as VideoQuality)
          : await startMp3Download(item.url, item.quality as AudioBitrate);
      updateItem(item.id, { jobId: response.job_id, status: "queued" });
    } catch (error) {
      const message = error instanceof Error ? error.message : "Failed to start download";
      updateItem(item.id, { status: "failed", error: message });
      onToast("error", message);
    }
  }, [onToast, updateItem]);

  const pollJob = useCallback(async (item: QueueItem) => {
    if (!item.jobId) return;
    try {
      const status = await getJobStatus(item.jobId);
      updateItem(item.id, {
        status: status.status,
        progress: status.progress,
        speed: status.speed,
        eta: status.eta,
        error: status.error,
        title: status.title || item.title,
      });

      if (status.status === "completed" && status.filename) {
        await downloadCompletedFile(item.jobId, status.filename);
        upsertHistory({
          id: item.jobId,
          url: item.url,
          title: status.title || item.title,
          format: item.format,
          quality: item.quality,
          status: status.status,
          filename: status.filename,
          completed_at: status.updated_at,
          thumbnail: item.thumbnail,
        });
        onHistoryUpdate?.();
        onToast("success", `Downloaded ${status.filename}`);
      }

      if (status.status === "failed") {
        onToast("error", status.error || "Download failed");
      }
    } catch (error) {
      const message = error instanceof Error ? error.message : "Status polling failed";
      updateItem(item.id, { status: "failed", error: message });
      onToast("error", message);
    }
  }, [onHistoryUpdate, onToast, updateItem]);

  useEffect(() => {
    const active = queue.filter(
      (item) => item.status === "downloading" || item.status === "processing" || item.status === "analyzing",
    ).length;
    const waiting = queue.filter((item) => item.status === "queued" && !item.jobId);
    const available = Math.max(0, MAX_PARALLEL - active);

    waiting.slice(0, available).forEach((item) => {
      void startJob(item);
    });
  }, [queue, startJob]);

  useEffect(() => {
    queue.forEach((item) => {
      if (!item.jobId) return;
      const isActive =
        item.status === "queued" ||
        item.status === "downloading" ||
        item.status === "processing" ||
        item.status === "paused" ||
        item.status === "analyzing";
      if (!isActive) {
        if (pollingRef.current[item.id]) {
          window.clearInterval(pollingRef.current[item.id]);
          delete pollingRef.current[item.id];
        }
        return;
      }
      if (pollingRef.current[item.id]) return;
      pollingRef.current[item.id] = window.setInterval(() => {
        const latest = queueRef.current.find((entry) => entry.id === item.id);
        if (latest) void pollJob(latest);
      }, POLL_INTERVAL_MS);
    });
  }, [pollJob, queue]);

  useEffect(() => {
    return () => {
      Object.values(pollingRef.current).forEach((timer) => window.clearInterval(timer));
      pollingRef.current = {};
    };
  }, []);

  const pause = useCallback(async (id: string) => {
    const item = queueRef.current.find((entry) => entry.id === id);
    if (!item?.jobId) return;
    const status = await pauseJob(item.jobId);
    updateItem(id, { status: status.status, progress: status.progress });
  }, [updateItem]);

  const resume = useCallback(async (id: string) => {
    const item = queueRef.current.find((entry) => entry.id === id);
    if (!item?.jobId) return;
    const status = await resumeJob(item.jobId);
    updateItem(id, { status: status.status, progress: status.progress });
  }, [updateItem]);

  const cancel = useCallback(async (id: string) => {
    const item = queueRef.current.find((entry) => entry.id === id);
    if (item?.jobId) {
      const status = await cancelJob(item.jobId);
      updateItem(id, { status: status.status, progress: status.progress });
      return;
    }
    updateItem(id, { status: "cancelled" });
  }, [updateItem]);

  const clearCompleted = useCallback(() => {
    setQueue((current) => current.filter((item) => !["completed", "cancelled", "failed"].includes(item.status)));
  }, []);

  const activeCount = useMemo(
    () => queue.filter((item) => ["queued", "downloading", "processing", "paused", "analyzing"].includes(item.status)).length,
    [queue],
  );

  return {
    queue,
    activeCount,
    enqueue,
    pause,
    resume,
    cancel,
    clearCompleted,
  };
}
