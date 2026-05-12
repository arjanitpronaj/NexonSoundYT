export function getBackendUrl(): string {
  const configured = process.env.API_URL || process.env.NEXT_PUBLIC_API_URL;
  if (configured) {
    return configured.replace(/\/$/, "");
  }
  if (process.env.NODE_ENV === "development") {
    return "http://localhost:8000";
  }
  return "https://nexonsoundyt.onrender.com";
}
