"use client";

import { useCallback, useEffect, useState } from "react";
import { motion } from "framer-motion";

import { DownloadButton } from "@/components/DownloadButton";
import { FormatSelector } from "@/components/FormatSelector";
import { Header } from "@/components/Header";
import { HistoryPanel } from "@/components/HistoryPanel";
import { PreviewCard } from "@/components/PreviewCard";
import { QualitySelector } from "@/components/QualitySelector";
import { QueuePanel } from "@/components/QueuePanel";
import { ToastViewport } from "@/components/ToastViewport";
import { useToast } from "@/components/ToastProvider";
import { UrlInputSection } from "@/components/UrlInputSection";
import { analyzeVideo, wakeApi } from "@/utils/api";
import { formatApiError } from "@/utils/errors";
import { useDownloadQueue } from "@/utils/queue";
import { clearHistory, loadHistory, loadTheme, saveTheme, type ThemeMode } from "@/utils/storage";
import type { AnalyzeResponse, DownloadFormat, HistoryEntry } from "@/utils/types";
import { isValidYouTubeUrl, normalizeInputUrl } from "@/utils/validators";

export function HomeClient() {
  const { pushToast } = useToast();
  const [theme, setTheme] = useState<ThemeMode>("dark");
  const [url, setUrl] = useState("");
  const [analysis, setAnalysis] = useState<AnalyzeResponse | null>(null);
  const [history, setHistory] = useState<HistoryEntry[]>([]);
  const [format, setFormat] = useState<DownloadFormat>("mp4");
  const [quality, setQuality] = useState("best");
  const [analyzing, setAnalyzing] = useState(false);
  const [starting, setStarting] = useState(false);

  const refreshHistory = useCallback(() => setHistory(loadHistory()), []);
  const { queue, enqueue, pause, resume, cancel, clearCompleted } = useDownloadQueue(pushToast, refreshHistory);

  useEffect(() => {
    const initialTheme = loadTheme();
    setTheme(initialTheme);
    document.documentElement.classList.toggle("dark", initialTheme === "dark");
    document.documentElement.classList.toggle("light", initialTheme === "light");
    setHistory(loadHistory());
    void wakeApi().catch(() => undefined);
  }, []);

  const toggleTheme = useCallback(() => {
    setTheme((current) => {
      const next = current === "dark" ? "light" : "dark";
      saveTheme(next);
      document.documentElement.classList.toggle("dark", next === "dark");
      document.documentElement.classList.toggle("light", next === "light");
      return next;
    });
  }, []);

  const handlePaste = useCallback(async () => {
    try {
      const text = await navigator.clipboard.readText();
      setUrl(normalizeInputUrl(text));
      pushToast("success", "URL pasted from clipboard");
    } catch {
      pushToast("error", "Clipboard access was denied");
    }
  }, [pushToast]);

  const handleAnalyze = useCallback(async () => {
    const normalized = normalizeInputUrl(url);
    if (!isValidYouTubeUrl(normalized)) {
      pushToast("error", "Enter a valid YouTube URL");
      return;
    }

    setAnalyzing(true);
    try {
      const result = await analyzeVideo(normalized);
      setAnalysis(result);
      setUrl(result.url);
      pushToast("success", "Video analyzed successfully");
    } catch (error) {
      pushToast("error", formatApiError(error));
      setAnalysis(null);
    } finally {
      setAnalyzing(false);
    }
  }, [pushToast, url]);

  const handleFormatChange = useCallback((nextFormat: DownloadFormat) => {
    setFormat(nextFormat);
    setQuality(nextFormat === "mp4" ? "best" : "192");
  }, []);

  const handleDownload = useCallback(() => {
    if (!analysis) {
      pushToast("error", "Analyze a video before downloading");
      return;
    }

    setStarting(true);
    enqueue({
      url: analysis.url,
      title: analysis.title,
      thumbnail: analysis.thumbnail,
      format,
      quality,
    });
    setStarting(false);
  }, [analysis, enqueue, format, pushToast, quality]);

  const handleClearHistory = useCallback(() => {
    clearHistory();
    setHistory([]);
    pushToast("info", "History cleared");
  }, [pushToast]);

  return (
    <div className={`${theme} min-h-screen`}>
      <div className="grid-bg relative min-h-screen">
        <div className="pointer-events-none absolute inset-0 bg-gradient-to-b from-brand-500/10 via-transparent to-fuchsia-500/10" />
        <main className="relative mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-6 sm:px-6 lg:px-8">
          <Header theme={theme} onToggleTheme={toggleTheme} />

          <UrlInputSection
            url={url}
            loading={analyzing}
            onChange={setUrl}
            onPaste={handlePaste}
            onAnalyze={handleAnalyze}
          />

          {analysis ? (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]"
            >
              <div className="space-y-6">
                <PreviewCard data={analysis} format={format} quality={quality} />
                <div className="grid gap-4 md:grid-cols-2">
                  <FormatSelector value={format} onChange={handleFormatChange} />
                  <QualitySelector format={format} value={quality} onChange={setQuality} />
                </div>
                <DownloadButton disabled={!analysis} loading={starting} onClick={handleDownload} />
              </div>

              <div className="space-y-6">
                <QueuePanel
                  items={queue}
                  onPause={(id) => void pause(id)}
                  onResume={(id) => void resume(id)}
                  onCancel={(id) => void cancel(id)}
                  onClearCompleted={clearCompleted}
                />
                <HistoryPanel items={history} onClear={handleClearHistory} />
              </div>
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              className="grid gap-6 lg:grid-cols-2"
            >
              <QueuePanel
                items={queue}
                onPause={(id) => void pause(id)}
                onResume={(id) => void resume(id)}
                onCancel={(id) => void cancel(id)}
                onClearCompleted={clearCompleted}
              />
              <HistoryPanel items={history} onClear={handleClearHistory} />
            </motion.div>
          )}
        </main>
      </div>
      <ToastViewport />
    </div>
  );
}
