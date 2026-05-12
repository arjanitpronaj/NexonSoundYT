"use client";

import { createContext, useCallback, useContext, useMemo, useState } from "react";

import type { ToastMessage } from "@/utils/types";

interface ToastContextValue {
  toasts: ToastMessage[];
  pushToast: (type: ToastMessage["type"], message: string) => void;
  dismissToast: (id: string) => void;
}

const ToastContext = createContext<ToastContextValue | null>(null);

function createToastId(): string {
  if (typeof crypto !== "undefined" && "randomUUID" in crypto) {
    return crypto.randomUUID();
  }
  return `toast-${Date.now()}`;
}

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastMessage[]>([]);

  const dismissToast = useCallback((id: string) => {
    setToasts((current) => current.filter((toast) => toast.id !== id));
  }, []);

  const pushToast = useCallback((type: ToastMessage["type"], message: string) => {
    const id = createToastId();
    setToasts((current) => [...current, { id, type, message }]);
    window.setTimeout(() => dismissToast(id), 4200);
  }, [dismissToast]);

  const value = useMemo(
    () => ({
      toasts,
      pushToast,
      dismissToast,
    }),
    [dismissToast, pushToast, toasts],
  );

  return <ToastContext.Provider value={value}>{children}</ToastContext.Provider>;
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) {
    throw new Error("useToast must be used within ToastProvider");
  }
  return context;
}
