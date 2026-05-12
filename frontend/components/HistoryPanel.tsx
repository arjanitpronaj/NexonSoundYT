"use client";

import Image from "next/image";
import { motion } from "framer-motion";

import { formatTimestamp, statusLabel } from "@/utils/format";
import type { HistoryEntry } from "@/utils/types";

interface HistoryPanelProps {
  items: HistoryEntry[];
  onClear: () => void;
}

export function HistoryPanel({ items, onClear }: HistoryPanelProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel rounded-3xl p-5"
    >
      <div className="mb-4 flex items-center justify-between gap-3">
        <motion.div initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }}>
          <h3 className="text-lg font-semibold">History</h3>
          <p className="text-sm text-[var(--muted)]">Stored locally in your browser via localStorage.</p>
        </motion.div>
        <button
          type="button"
          onClick={onClear}
          className="rounded-2xl border border-[var(--border)] px-3 py-2 text-xs font-medium"
        >
          Clear history
        </button>
      </div>

      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="scrollbar-thin max-h-[420px] space-y-3 overflow-y-auto pr-1"
      >
        {items.length === 0 ? (
          <p className="rounded-2xl border border-dashed border-[var(--border)] px-4 py-8 text-center text-sm text-[var(--muted)]">
            Completed downloads will appear here.
          </p>
        ) : (
          items.map((item) => (
            <article key={item.id} className="flex gap-3 rounded-2xl border border-[var(--border)] bg-white/30 p-3 dark:bg-slate-950/30">
              <div className="relative h-16 w-28 overflow-hidden rounded-xl bg-slate-900/10">
                {item.thumbnail ? (
                  <Image src={item.thumbnail} alt={item.title} fill className="object-cover" sizes="112px" unoptimized />
                ) : null}
              </div>
              <div className="min-w-0 flex-1">
                <p className="truncate font-medium">{item.title}</p>
                <p className="text-xs text-[var(--muted)]">
                  {item.format.toUpperCase()} • {item.quality} • {statusLabel(item.status)}
                </p>
                <p className="text-xs text-[var(--muted)]">{formatTimestamp(item.completed_at)}</p>
              </div>
            </article>
          ))
        )}
      </motion.div>
    </motion.section>
  );
}
