"use client";

import Image from "next/image";
import { motion } from "framer-motion";

import { formatBytes, formatDuration } from "@/utils/format";
import type { AnalyzeResponse, DownloadFormat, VideoQuality } from "@/utils/types";

interface PreviewCardProps {
  data: AnalyzeResponse;
  format: DownloadFormat;
  quality: string;
}

const VIDEO_QUALITIES: VideoQuality[] = ["360p", "480p", "720p", "1080p", "2k", "4k", "best"];

export function PreviewCard({ data, format, quality }: PreviewCardProps) {
  const estimatedSize =
    format === "mp4"
      ? data.estimated_sizes[quality] ?? data.estimated_sizes.best
      : data.estimated_sizes.best
        ? Math.round((data.estimated_sizes.best || 0) * 0.12)
        : null;

  return (
    <motion.section
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="glass-panel overflow-hidden rounded-3xl"
    >
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="grid gap-6 p-6 lg:grid-cols-[220px_1fr]"
      >
        <div className="relative aspect-video overflow-hidden rounded-2xl bg-slate-900/10">
          {data.thumbnail ? (
            <Image
              src={data.thumbnail}
              alt={data.title}
              fill
              className="object-cover"
              sizes="220px"
              unoptimized
            />
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex h-full items-center justify-center text-sm text-[var(--muted)]"
            >
              No thumbnail
            </motion.div>
          )}
        </div>

        <div className="space-y-4">
          <div>
            <h3 className="text-2xl font-semibold leading-tight">{data.title}</h3>
            <p className="mt-2 text-sm text-[var(--muted)]">
              {data.channel} • {data.upload_date || "Unknown date"} • {formatDuration(data.duration)}
            </p>
          </div>

          <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
            <Metric label="Estimated size" value={formatBytes(estimatedSize)} />
            <Metric label="Available qualities" value={`${data.formats.length} streams`} />
            <Metric label="Selected format" value={format.toUpperCase()} />
            <Metric label="Selected quality" value={quality} />
          </div>

          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
          >
            <p className="mb-2 text-sm font-medium">Detected video qualities</p>
            <div className="flex flex-wrap gap-2">
              {VIDEO_QUALITIES.map((item) => (
                <span
                  key={item}
                  className="rounded-full border border-[var(--border)] px-3 py-1 text-xs text-[var(--muted)]"
                >
                  {item}
                  {data.estimated_sizes[item] ? ` • ${formatBytes(data.estimated_sizes[item])}` : ""}
                </span>
              ))}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </motion.section>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-2xl border border-[var(--border)] bg-white/40 px-4 py-3 dark:bg-slate-950/30">
      <p className="text-xs uppercase tracking-wide text-[var(--muted)]">{label}</p>
      <p className="mt-1 text-sm font-semibold">{value}</p>
    </div>
  );
}
