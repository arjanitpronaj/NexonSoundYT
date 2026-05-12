# NexonSoundYT

NexonSoundYT is a production-ready full stack YouTube downloader built for free hosting on Vercel (frontend) and Render (backend). Paste a YouTube URL, analyze the video, choose MP4 or MP3 output, and track downloads in real time with queue controls, browser history, and polished dark or light UI.

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
│   ├── components/
│   ├── public/
│   ├── styles/
│   └── utils/
├── api/              # Reserved for optional edge/proxy routes
├── render.yaml
├── vercel.json
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

Open `http://localhost:3000` and set `NEXT_PUBLIC_API_URL=http://localhost:8000`.

## Environment Variables

| Variable | Service | Description |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | Frontend | Public backend base URL |
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

## Deployment

### Vercel (Frontend)

1. Delete the failed Vercel project if it still has custom build or output overrides.
2. Import the GitHub repository again in Vercel.
3. Set **Root Directory** to `frontend`.
4. Leave **Framework Preset** on **Next.js**.
5. In **Build and Output Settings**, turn off every override. Use only `npm install` and `npm run build`, and leave **Output Directory** empty.
6. Add `NEXT_PUBLIC_API_URL` with your Render backend URL.
7. Deploy.

### Render (Backend)

1. Create a new Web Service from this repository.
2. Use `render.yaml` or configure manually with `backend` as the root directory.
3. Build with the provided `backend/Dockerfile` so FFmpeg is installed.
4. Set `CORS_ORIGINS` to your Vercel production URL.
5. Deploy and verify `GET /health`.

## GitHub

Repository: [NexonSoundYT](https://github.com/arjanitpronaj/NexonSoundYT)

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/arjanitpronaj/NexonSoundYT.git
git push -u origin main
```

## License

MIT
