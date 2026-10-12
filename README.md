# 🎬 VideoIndex — Intelligent Video Library & Transcript Search

**Organize your videos. Explore their content. Find information faster.**

VideoIndex is a full-stack video indexing application that organizes video metadata, stores records in a MySQL database, and uses AI-powered speech recognition to generate searchable transcripts. Its web interface provides a centralized library for browsing videos, exploring categories, and reading transcript content.

---

## ✨ Features

- **📚 Centralized Video Library** — Browse video records through a clean, responsive dashboard.
- **🔎 Search & Filtering** — Search video titles, descriptions, and transcripts, and filter videos by category.
- **📝 AI-Powered Transcription** — Generate text transcripts from video audio using OpenAI Whisper.
- **▶️ Video Playback** — Access and play locally stored video files through the application.
- **🗃️ MySQL Database** — Store video metadata, categories, descriptions, languages, durations, views, and transcripts.
- **⚡ REST API** — Retrieve video and category data through a FastAPI backend.
- **🎨 Modern UI** — Dark-themed React interface with video cards, dashboard statistics, and transcript panels.
- **🎵 Audio Extraction** — Use FFmpeg to extract audio from video files for transcription.

## 🖥️ Preview

The dashboard includes:

- Total video and category counts
- Video library with category filters
- Search across metadata and transcripts
- Video playback and transcript viewing
- Database-backed video records

> Add your actual application screenshot here to make the repository more visually engaging.

## 🛠️ Tech Stack

| Layer | Technologies |
|---|---|
| Frontend | React, Vite, JavaScript, CSS |
| Backend | Python, FastAPI, Uvicorn |
| Database | MySQL |
| AI / Speech Recognition | OpenAI Whisper |
| Media Processing | FFmpeg |
| API Documentation | Swagger UI / OpenAPI |
| Version Control | Git and GitHub |

## 🏗️ Architecture

```text
                 ┌──────────────────────┐
                 │   React + Vite UI    │
                 │   localhost:5173     │
                 └──────────┬───────────┘
                            │ HTTP Requests
                            ▼
                 ┌──────────────────────┐
                 │    FastAPI Backend   │
                 │   localhost:8001     │
                 └──────────┬───────────┘
                            │
                 ┌──────────┴───────────┐
                 ▼                      ▼
        ┌─────────────────┐    ┌─────────────────┐
        │   MySQL Database│    │ Media Processing│
        │ Metadata & Text │    │ FFmpeg + Whisper│
        └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```text
VideoIndex/
├── app/
│   ├── api.py              # FastAPI routes
│   ├── database.py         # MySQL connection
│   ├── import_videos.py    # Video indexing pipeline
│   ├── media.py            # Audio extraction and transcription
│   ├── settings.py         # Application settings
│   └── tag_extraction.py   # Tag extraction utilities
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── App.jsx         # Main React application
│   │   ├── App.css         # Dashboard styling
│   │   ├── index.css       # Global styles
│   │   └── main.jsx        # Frontend entry point
│   └── package.json
├── videos/                 # Local video files
├── audios/                 # Extracted audio files
├── .env.example            # Environment configuration template
├── requirements.txt        # Python dependencies
├── schema.sql              # Database schema
└── README.md
```

## ⚙️ Getting Started

### Prerequisites

Install the following before running the application:

- Python 3.12.4 or a compatible version
- Node.js and npm
- MySQL Server
- FFmpeg
- Git

### 1. Clone the repository

```bash
git clone https://github.com/aYUSHDamn/VideoIndex.git
cd VideoIndex
```

### 2. Set up the Python environment

```bash
python -m venv .venv
```

Activate the environment on Windows:

```cmd
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

### 3. Configure MySQL

Start your MySQL server and create a database. Import the schema provided in `schema.sql` into the appropriate database.

For example, using the MySQL command-line client:

```bash
mysql -u root -p
```

Then, inside MySQL:

```sql
CREATE DATABASE video_index;
EXIT;
```

Import the schema:

```cmd
mysql -u root -p video_index < schema.sql
```

**Configuration note:** Check `app/settings.py`, `app/database.py`, and `.env.example` for the exact database configuration keys expected by your version of the application.

Create your local `.env` from the provided template:

```cmd
copy .env.example .env
```

Update `.env` with your local MySQL credentials and database settings. Never commit real credentials to GitHub.

### 4. Install FFmpeg

Install FFmpeg and ensure its `bin` directory is available in your Windows `PATH`.

Verify the installation:

```bash
ffmpeg -version
```

### 5. Start the backend

From the project root, run:

```bash
python -m uvicorn app.api:app --host 127.0.0.1 --port 8001
```

The API will be available at:

- API base URL: `http://127.0.0.1:8001`
- Swagger documentation: `http://127.0.0.1:8001/docs`

Keep the backend terminal running.

### 6. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, typically:

`http://localhost:5173`

Ensure that the frontend API configuration points to the backend port `8001`:

```javascript
const API = "http://127.0.0.1:8001";
```

### 7. Index videos and generate transcripts

Place supported video files in the local `videos/` directory, then run the indexing script from the project root:

```bash
python -m app.import_videos --input-dir videos
```

The transcription pipeline uses FFmpeg to extract audio and Whisper to generate transcripts. The first Whisper model download requires an internet connection and may take time.

Check `app/import_videos.py` for the exact supported arguments and import behavior.

## 🔌 API Endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check API status |
| GET | `/api/videos` | Retrieve video records |
| GET | `/api/categories` | Retrieve available categories |

Interactive API documentation is available at `/docs` when the backend is running.

## 🔍 How It Works

1. **Indexing:** Video files are discovered by the indexing pipeline.
2. **Audio extraction:** FFmpeg extracts audio for speech recognition.
3. **Transcription:** Whisper converts speech into text.
4. **Storage:** Video metadata and transcript information are stored in MySQL.
5. **Retrieval:** FastAPI exposes video and category records through REST endpoints.
6. **Discovery:** The React interface displays the library and lets users search metadata and transcript text.

## 🔐 Configuration & Data

- Keep `.env` and other secret files out of version control.
- Do not commit private credentials, database dumps, or sensitive media.
- Video and audio assets may need to be supplied separately when setting up the project on another machine.
- Whisper models are downloaded and cached locally when required.
- The current setup is designed for local development; public deployment requires suitable database and media hosting configuration.

## 🚧 Future Enhancements

Potential improvements include:

- Timestamped transcripts with synchronized playback
- Search results highlighting matching transcript passages
- Automatic tagging and topic extraction
- Video upload and metadata management
- Transcript export and download
- Authentication and user-specific libraries
- Cloud deployment and scalable media storage

## 🎯 Project Objective

VideoIndex explores how a combination of database management, media processing, speech recognition, and full-stack web development can make video collections easier to organize and search.

Rather than treating videos as isolated files, the project creates structured records enriched with textual information, enabling more useful content discovery.

## 👨‍💻 Author

**Ayush Konar**

B.Tech — Computer Science and Engineering (Data Science)

GitHub: [@aYUSHDamn](https://github.com/aYUSHDamn)

---

*Built with React, FastAPI, MySQL, FFmpeg, and Whisper.*
