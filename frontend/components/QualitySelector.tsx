"use client";

import { motion } from "framer-motion";

import type { AudioBitrate, DownloadFormat, VideoQuality } from "@/utils/types";

const VIDEO_OPTIONS: VideoQuality[] = ["360p", "480p", "720p", "1080p", "2k", "4k", "best"];
const AUDIO_OPTIONS: AudioBitrate[] = ["128", "192", "320"];

interface QualitySelectorProps {
  format: DownloadFormat;
  value: string;
  onChange: (value: string) => void;
}

export function QualitySelector({ format, value, onChange }: QualitySelectorProps) {
  const options = format === "mp4" ? VIDEO_OPTIONS : AUDIO_OPTIONS;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-3xl p-5"
    >
      <p className="text-sm font-medium">{format === "mp4" ? "Video quality" : "MP3 bitrate"}</p>
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="mt-3 flex flex-wrap gap-2"
      >
        {options.map((option) => {
          const label = format === "mp4" ? option : `${option} kbps`;
          return (
            <button
              key={option}
              type="button"
              onClick={() => onChange(option)}
              className={`rounded-full border px-4 py-2 text-sm transition ${
                value === option
                  ? "border-brand-500 bg-brand-500/15 text-brand-700 dark:text-brand-200"
                  : "border-[var(--border)] hover:bg-white/50 dark:hover:bg-slate-900/50"
              }`}
            >
              {label}
            </button>
          );
        })}
      </motion.div>
    </motion.div>
  );
}
