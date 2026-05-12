"use client";

import { motion } from "framer-motion";

import type { ThemeMode } from "@/utils/storage";

interface HeaderProps {
  theme: ThemeMode;
  onToggleTheme: () => void;
}

export function Header({ theme, onToggleTheme }: HeaderProps) {
  return (
    <header className="glass-panel sticky top-0 z-40 rounded-3xl px-5 py-4">
      <motion.div
        initial={{ opacity: 0, y: -8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-wrap items-center justify-between gap-4"
      >
        <motion.div
          initial={{ opacity: 0, x: -8 }}
          animate={{ opacity: 1, x: 0 }}
          className="flex items-center gap-3"
        >
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-brand-500 to-violet-500 text-lg font-bold text-white shadow-lg">
            N
          </div>
          <div>
            <p className="text-lg font-semibold tracking-tight">NexonSoundYT</p>
            <p className="text-sm text-[var(--muted)]">Professional YouTube downloader for MP4 and MP3</p>
          </div>
        </motion.div>

        <button
          type="button"
          onClick={onToggleTheme}
          className="rounded-2xl border border-[var(--border)] bg-white/40 px-4 py-2 text-sm font-medium transition hover:bg-white/70 dark:bg-slate-900/50 dark:hover:bg-slate-900/80"
        >
          {theme === "dark" ? "Light mode" : "Dark mode"}
        </button>
      </motion.div>
    </header>
  );
}
