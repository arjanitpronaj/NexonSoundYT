"use client";

import { motion } from "framer-motion";

interface UrlInputSectionProps {
  url: string;
  loading: boolean;
  onChange: (value: string) => void;
  onPaste: () => void;
  onAnalyze: () => void;
}

export function UrlInputSection({ url, loading, onChange, onPaste, onAnalyze }: UrlInputSectionProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-3xl p-6"
    >
      <div className="flex flex-col gap-4">
        <div>
          <h2 className="text-xl font-semibold">Paste a YouTube URL</h2>
          <p className="mt-1 text-sm text-[var(--muted)]">
            Analyze the video first, then choose MP4 or MP3 with your preferred quality.
          </p>
        </div>

        <div className="flex flex-col gap-3 lg:flex-row">
          <input
            value={url}
            onChange={(event) => onChange(event.target.value)}
            placeholder="https://www.youtube.com/watch?v=..."
            className="w-full rounded-2xl border border-[var(--border)] bg-white/70 px-4 py-3 text-sm outline-none ring-brand-500 transition focus:ring-2 dark:bg-slate-950/50"
          />
          <motion.button
            whileTap={{ scale: 0.98 }}
            type="button"
            onClick={onPaste}
            className="rounded-2xl border border-[var(--border)] px-4 py-3 text-sm font-medium transition hover:bg-white/70 dark:hover:bg-slate-900/70"
          >
            Paste
          </motion.button>
          <motion.button
            whileTap={{ scale: 0.98 }}
            type="button"
            onClick={onAnalyze}
            disabled={loading}
            className="rounded-2xl bg-gradient-to-r from-brand-500 to-violet-500 px-5 py-3 text-sm font-semibold text-white shadow-lg transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? "Analyzing..." : "Analyze"}
          </motion.button>
        </div>
      </div>
    </motion.section>
  );
}
