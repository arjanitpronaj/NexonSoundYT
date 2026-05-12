"use client";

import { motion } from "framer-motion";

import { useToast } from "@/components/ToastProvider";

const toneStyles: Record<string, string> = {
  success: "border-emerald-400/40 bg-emerald-500/10 text-emerald-700 dark:text-emerald-300",
  error: "border-rose-400/40 bg-rose-500/10 text-rose-700 dark:text-rose-300",
  info: "border-brand-400/40 bg-brand-500/10 text-brand-700 dark:text-brand-200",
};

export function ToastViewport() {
  const { toasts, dismissToast } = useToast();

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      className="pointer-events-none fixed bottom-5 right-5 z-50 flex w-full max-w-sm flex-col gap-3"
    >
      {toasts.map((toast) => (
        <motion.button
          key={toast.id}
          layout
          type="button"
          onClick={() => dismissToast(toast.id)}
          className={`pointer-events-auto glass-panel rounded-2xl border px-4 py-3 text-left text-sm shadow-glass ${toneStyles[toast.type]}`}
        >
          {toast.message}
        </motion.button>
      ))}
    </motion.div>
  );
}
