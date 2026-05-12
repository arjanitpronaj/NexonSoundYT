"use client";

import { motion } from "framer-motion";

import { statusLabel } from "@/utils/format";
import type { QueueItem } from "@/utils/types";

interface QueuePanelProps {
  items: QueueItem[];
  onPause: (id: string) => void;
  onResume: (id: string) => void;
  onCancel: (id: string) => void;
  onClearCompleted: () => void;
}

export function QueuePanel({ items, onPause, onResume, onCancel, onClearCompleted }: QueuePanelProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-3xl p-5"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}>
          <h3 className="text-lg font-semibold">Download queue</h3>
          <p className="text-sm text-[var(--muted)]">Parallel jobs, live progress, pause, resume, and cancel.</p>
        </motion.div>
        <button
          type="button"
          onClick={onClearCompleted}
          className="rounded-2xl border border-[var(--border)] px-3 py-2 text-xs font-medium"
        >
          Clear finished
        </button>
      </div>

      <div className="scrollbar-thin max-h-[420px] space-y-3 overflow-y-auto pr-1">
        {items.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-[var(--border)] px-4 py-8 text-center text-sm text-[var(--muted)]">
            Queue is empty. Analyze a video and start a download.
          </p>
        ) : (
          items.map((item) => (
            <article key={item.id} className="rounded-2xl border border-[var(--border)] bg-white/30 p-4 dark:bg-slate-950/30">
              <motion.div
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="flex flex-wrap items-start justify-between gap-3"
              >
                <div>
                  <p className="font-medium">{item.title}</p>
                  <p className="text-xs text-[var(--muted)]">
                    {item.format.toUpperCase()} • {item.quality} • {statusLabel(item.status)}
                  </p>
                </div>
                <div className="flex gap-2">
                  <button type="button" onClick={() => onPause(item.id)} className="rounded-xl border px-3 py-1 text-xs">
                    Pause
                  </button>
                  <button type="button" onClick={() => onResume(item.id)} className="rounded-xl border px-3 py-1 text-xs">
                    Resume
                  </button>
                  <button type="button" onClick={() => onCancel(item.id)} className="rounded-xl border px-3 py-1 text-xs">
                    Cancel
                  </button>
                </div>
              </motion.div>

              <div className="mt-3 h-2 overflow-hidden rounded-full bg-slate-200 dark:bg-slate-800">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-brand-500 to-violet-500 transition-all"
                  style={{ width: `${Math.max(0, Math.min(item.progress, 100))}%` }}
                />
              </div>
              <div className="mt-2 flex flex-wrap gap-3 text-xs text-[var(--muted)]">
                <span>{item.progress.toFixed(0)}%</span>
                {item.speed ? <span>{item.speed}</span> : null}
                {item.eta ? <span>ETA {item.eta}</span> : null}
                {item.error ? <span className="text-rose-500">{item.error}</span> : null}
              </div>
            </article>
          ))
        )}
      </div>
    </motion.section>
  );
}
