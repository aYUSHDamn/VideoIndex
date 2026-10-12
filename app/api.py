
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import connect
from pathlib import Path
from fastapi.responses import FileResponse

app = FastAPI(title="Video Index API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {"message": "Video Index API is running!"}


@app.get("/api/videos")
def get_videos():
    db = None
    cursor = None
    try:
        db = connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT video_id, channel_id, category_id, title,
                   description, language, duration, views,
                   is_public, uploaded_at, transcript
            FROM videos
            ORDER BY video_id DESC
        """)
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()


@app.get("/api/categories")
def get_categories():
    db = None
    cursor = None
    try:
        db = connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT category_id, category_name FROM categories ORDER BY category_id"
        )
        return cursor.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
@app.get("/test-play")
def test_play():
    return {"message": "Playback route is registered!"}

BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = BASE_DIR / "videos"


@app.get("/api/videos/{video_id}/play")
def play_video(video_id: int):
    db = None
    cursor = None

    try:
        db = connect()
        cursor = db.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT video_path
            FROM videos
            WHERE video_id = %s AND is_public = 1
            """,
            (video_id,)
        )

        video = cursor.fetchone()

        if not video:
            raise HTTPException(
                status_code=404,
                detail="Video not found"
            )

        stored_path = video["video_path"]
        video_path = Path(stored_path)

        if not video_path.is_absolute():
            video_path = BASE_DIR / video_path

        video_path = video_path.resolve()

        # Only serve files inside the project's videos folder
        if not video_path.is_relative_to(VIDEO_DIR.resolve()):
            raise HTTPException(
                status_code=403,
                detail="Invalid video path"
            )

        if not video_path.is_file():
            raise HTTPException(
                status_code=404,
                detail="Video file missing"
            )

        return FileResponse(
            path=str(video_path),
            media_type="video/mp4"
        )

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()
