# NexonSoundYT

NexonSoundYT is a production-ready full stack YouTube downloader built for free hosting on [Vercel](https://vercel.com) (frontend) and [Render](https://render.com) (backend). Paste a YouTube URL, analyze the video, choose MP4 or MP3 output, and track downloads in real time with queue controls, browser history, and a polished dark or light UI.

For the smoothest free-tier setup, keep the GitHub repository **public** so Vercel and Render can import and auto-deploy without private-repo friction.

## Features

- MP4 video downloads with automatic best-quality detection and manual quality selection (360p through 4K)
- MP3 audio extraction with FFmpeg at 128, 192, or 320 kbps
- Embedded MP3 metadata: title, channel, upload date, and thumbnail artwork
- Pre-download analysis: title, thumbnail, duration, available qualities, and estimated size
- Real-time progress, speed, and ETA with queue, pause, resume, cancel, and parallel downloads
- Responsive SaaS-style interface with glassmorphism, Framer Motion animations, and toast notifications
- No database: browser `localStorage` for history and temporary server-side files only

## Screenshots

| Home | Queue |
| --- | --- |
| ![Home screenshot placeholder](docs/screenshots/home.png) | ![Queue screenshot placeholder](docs/screenshots/queue.png) |

| Preview | History |
| --- | --- |
| ![Preview screenshot placeholder](docs/screenshots/preview.png) | ![History screenshot placeholder](docs/screenshots/history.png) |

## Tech Stack

**Frontend**

- Next.js 15
- React
- TailwindCSS
- Framer Motion
- Axios

**Backend**

- Python FastAPI
- yt-dlp
- FFmpeg
- Uvicorn

## Project Structure

```text
NexonSoundYT/
├── backend/          # FastAPI API, yt-dlp jobs, FFmpeg processing
├── frontend/         # Next.js web app
│   ├── app/
│   │   └── api/      # Vercel proxy to the Render backend
│   ├── components/
│   ├── public/
│   ├── styles/
│   └── utils/
├── api/              # Reserved for optional edge/proxy routes
├── Dockerfile        # Root Docker build for Render
├── render.yaml
├── .env.example
└── README.md
```

## Installation

### Prerequisites

- Node.js 20+
- Python 3.12+
- FFmpeg available on your PATH

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
npm install
copy ..\.env.example .env.local
npm run dev
```

Open `http://localhost:3000`. The frontend calls the backend through `/api`, which proxies to `http://localhost:8000` in development.

## Environment Variables

| Variable | Service | Description |
| --- | --- | --- |
| `API_URL` | Vercel | Server-side backend URL used by `/api` proxy routes |
| `NEXT_PUBLIC_API_URL` | Frontend | Optional explicit backend URL override |
| `CORS_ORIGINS` | Backend | Comma-separated allowed frontend origins |
| `TEMP_DIR` | Backend | Temporary download directory |
| `MAX_PARALLEL_JOBS` | Backend | Concurrent download workers |
| `RATE_LIMIT_PER_MINUTE` | Backend | Per-IP request limit |
| `JOB_TTL_SECONDS` | Backend | Completed file retention window |
| `MAX_DOWNLOAD_RETRIES` | Backend | Automatic retry count |
| `FFMPEG_PATH` | Backend | FFmpeg executable path |
| `YTDLP_PATH` | Backend | yt-dlp executable path |
| `PORT` | Backend | Uvicorn port (Render injects this) |

## API Routes

| Method | Route | Description |
| --- | --- | --- |
| `POST` | `/analyze` | Analyze a YouTube URL |
| `POST` | `/download/mp4` | Queue an MP4 download job |
| `POST` | `/download/mp3` | Queue an MP3 download job |
| `GET` | `/status/{job_id}` | Poll job progress |
| `POST` | `/status/{job_id}/pause` | Pause a job |
| `POST` | `/status/{job_id}/resume` | Resume a paused job |
| `POST` | `/status/{job_id}/cancel` | Cancel a job |
| `GET` | `/history` | Return in-memory session history |
| `GET` | `/download/file/{job_id}` | Download the completed file |
| `GET` | `/health` | Service health check |

Interactive docs are available at `/docs` when the backend is running.

## Upload to GitHub

1. Create a **public** repository named `NexonSoundYT`.
2. Push this project to the `main` branch.

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/arjanitpronaj/NexonSoundYT.git
git push -u origin main
```

If the repository is private, Vercel and Render can still work on many plans, but public is the simplest path on free tiers.

## Deploy Backend to Render

1. Open [Render](https://render.com) and create a **Web Service** from the GitHub repository.
2. Use these settings:
   - **Root Directory:** leave empty
   - **Language / Environment:** Docker
   - **Dockerfile Path:** `Dockerfile`
   - **Instance Type:** Free
   - **Health Check Path:** `/health`
3. Add environment variable `CORS_ORIGINS` with your Vercel production URL and preview URLs, comma-separated.
4. Deploy and verify `https://your-service.onrender.com/health`.

You can also deploy with `render.yaml` using a Render Blueprint.

## Deploy Frontend to Vercel

1. Open [Vercel](https://vercel.com) and import the GitHub repository.
2. Set **Root Directory** to `frontend`.
3. Leave **Framework Preset** on **Next.js**.
4. Do not override install, build, or output settings.
5. Add environment variable `API_URL` with your Render backend URL, for example `https://nexonsoundyt.onrender.com`.
6. Deploy.

## Connect Frontend to Backend

Production flow:

1. Browser calls `https://your-vercel-app.vercel.app/api/...`
2. Vercel proxy routes forward the request to `API_URL` on Render
3. Render processes analyze/download jobs and returns progress and files

After both services are live:

1. Set `API_URL` on Vercel to the Render service URL
2. Set `CORS_ORIGINS` on Render to your Vercel domain(s)
3. Redeploy both services if you change environment variables

## GitHub

Repository: [NexonSoundYT](https://github.com/arjanitpronaj/NexonSoundYT)

## License

MIT
