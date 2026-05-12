"use client";

import { motion } from "framer-motion";

import type { DownloadFormat } from "@/utils/types";

interface FormatSelectorProps {
  value: DownloadFormat;
  onChange: (value: DownloadFormat) => void;
}

export function FormatSelector({ value, onChange }: FormatSelectorProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-3xl p-5"
    >
      <p className="text-sm font-medium">Format</p>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-3 grid grid-cols-2 gap-3"
      >
        {(["mp4", "mp3"] as DownloadFormat[]).map((format) => (
          <button
            key={format}
            type="button"
            onClick={() => onChange(format)}
            className={`rounded-2xl border px-4 py-3 text-sm font-semibold transition ${
              value === format
                ? "border-brand-500 bg-brand-500/15 text-brand-700 dark:text-brand-200"
                : "border-[var(--border)] hover:bg-white/50 dark:hover:bg-slate-900/50"
            }`}
          >
            {format.toUpperCase()}
          </button>
        ))}
      </motion.div>
    </motion.div>
  );
}
