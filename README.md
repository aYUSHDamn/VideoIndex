# DBMS Video Transcription Pipeline

A standalone Python + MySQL project. It has no FastAPI server or backend API.

```text
video file
  -> ffprobe reads duration and optional title/description metadata
  -> ffmpeg extracts mono, 16 kHz PCM WAV audio
  -> Whisper transcribes the WAV
  -> scikit-learn extracts transcript tags
  -> Python writes video, transcript, metadata, and tags to MySQL
```

Everything for this project lives in this folder. Put videos in `videos/`; extracted WAV files are written to `audios/`.

## 1. Create the MySQL tables

Open `schema.sql` in MySQL Workbench and execute the whole script. It creates the `video_index_db` schema and the tables in the attached ER diagram:

- `users` → `channels` → `videos`
- `categories` → `videos`
- `videos` and `users` → `comments`
- `users` and `videos` → `watch_history`
- `videos` ↔ `tags` through `video_tags`

The `videos` table also has `video_path`, `audio_path`, and `transcript` fields for this pipeline. `duration` is an integer number of seconds.

To inspect imported rows in Workbench:

```sql
USE video_index_db;
SELECT * FROM videos;
```

To show readable transcript and tag data:

```sql
SELECT video_id, title, duration, language, description, transcript
FROM videos;

SELECT v.video_id, v.title, t.tag_name
FROM videos AS v
JOIN video_tags AS vt ON vt.video_id = v.video_id
JOIN tags AS t ON t.tag_id = vt.tag_id
ORDER BY v.video_id, t.tag_name;
```

To generate the ER diagram in Workbench, use **Database → Reverse Engineer**, connect to the same MySQL server, select `video_index_db`, and finish the wizard. The foreign keys in `schema.sql` define the relationships.

## 2. Configure MySQL

From this folder, copy the template and edit it with your local MySQL connection details:

```powershell
Copy-Item .env.example .env
notepad .env
```

Set the host, database name, MySQL user, and password for your local MySQL server. `.env` is ignored by Git.

## 3. Install the Python dependencies

Use the virtual environment created inside this folder:

```powershell
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Install ffmpeg separately and make sure both `ffmpeg` and `ffprobe` are on `PATH`. Whisper's first run downloads its model; the default is `base`. Change `WHISPER_MODEL` in `.env` to another Whisper model name if needed.

## 4. Add videos and import them

Copy one or more video files into `videos/`, then run this from the `dbms` folder:

```powershell
.\.venv\Scripts\python.exe -m app.import_videos
```

You can also process one file without copying it into the folder:

```powershell
.\.venv\Scripts\python.exe -m app.import_videos --video ..\videos\videoSample4.mp4
```

Or select a different input folder:

```powershell
.\.venv\Scripts\python.exe -m app.import_videos --input-dir D:\path\to\videos
```

To use the existing sample videos one level above this folder without copying them:

```powershell
.\.venv\Scripts\python.exe -m app.import_videos --input-dir ..\videos
```

The importer creates a `Local Video Importer` user, a `Local Video Imports` channel, and an `Uncategorized` category when they do not exist. It records a title from file metadata or detected transcript phrases, a description from file metadata or a transcript excerpt, language, duration, file paths, full transcript, and tag links. It skips video paths already present in MySQL so rerunning it does not duplicate rows.

Tags use TF-IDF over the videos being imported, with likely repeated title phrases ranked first. Tag extraction is a lightweight keyword heuristic; Whisper transcription quality affects tag quality.

## Project files

- `schema.sql` — MySQL schema and ER relationships.
- `app/import_videos.py` — command-line pipeline and MySQL inserts.
- `app/media.py` — ffprobe, ffmpeg audio extraction, and Whisper transcription.
- `app/tag_extraction.py` — transcript-to-keyword extraction.
- `app/database.py`, `app/settings.py` — MySQL connection and local settings.
- `.env.example` — template for local MySQL and Whisper settings.
