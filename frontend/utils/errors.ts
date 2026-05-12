import axios from "axios";

export function formatApiError(error: unknown): string {
  if (axios.isAxiosError(error)) {
    const detail = error.response?.data?.detail;
    if (typeof detail === "string" && detail.trim()) {
      return detail;
    }
    if (Array.isArray(detail) && detail.length > 0) {
      return detail.map((item) => item?.msg || "Request failed").join(", ");
    }
    if (error.code === "ECONNABORTED") {
      return "The server took too long to respond. Try again in a moment.";
    }
    if (error.message === "Network Error") {
      return "Could not reach the API. Wait for Render to wake up, then try again.";
    }
    if (error.response?.status) {
      return `Request failed with status ${error.response.status}.`;
    }
    return error.message;
  }

  if (error instanceof Error) {
    return error.message;
  }

  return "Something went wrong.";
}
