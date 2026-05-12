"use client";

import { motion } from "framer-motion";

interface DownloadButtonProps {
  disabled: boolean;
  loading: boolean;
  onClick: () => void;
}

export function DownloadButton({ disabled, loading, onClick }: DownloadButtonProps) {
  return (
    <motion.button
      whileTap={{ scale: disabled ? 1 : 0.98 }}
      type="button"
      onClick={onClick}
      disabled={disabled || loading}
      className="w-full rounded-3xl bg-gradient-to-r from-brand-500 via-violet-500 to-fuchsia-500 px-6 py-4 text-base font-semibold text-white shadow-xl transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
    >
      {loading ? "Starting download..." : "Start download"}
    </motion.button>
  );
}
