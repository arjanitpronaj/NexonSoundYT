import type { Metadata } from "next";

import { HomeClient } from "@/components/HomeClient";
import { ToastProvider } from "@/components/ToastProvider";

export const metadata: Metadata = {
  title: "NexonSoundYT | YouTube Downloader",
  description: "Download YouTube videos as MP4 or MP3 with metadata, artwork, and live progress tracking.",
  icons: {
    icon: "/favicon.svg",
  },
};

export default function HomePage() {
  return (
    <ToastProvider>
      <HomeClient />
    </ToastProvider>
  );
}
