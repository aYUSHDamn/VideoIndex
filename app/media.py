import json
import subprocess
from functools import lru_cache
from pathlib import Path

import whisper

from .settings import WHISPER_MODEL


def probe_video(video_path: Path) -> dict:
    result = subprocess.run(
        [
            "ffprobe", "-v", "error", "-show_entries",
            "format=duration:format_tags=title,description,comment",
            "-of", "json", str(video_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(result.stdout).get("format", {})


def extract_audio(video_path: Path, audio_path: Path) -> Path:
    video_path = Path(video_path)
    audio_path = Path(audio_path)
    if not video_path.is_file():
        raise FileNotFoundError(f"Video file not found: {video_path}")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            "ffmpeg", "-y", "-i", str(video_path), "-vn", "-ac", "1",
            "-ar", "16000", "-c:a", "pcm_s16le", str(audio_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    return audio_path


@lru_cache(maxsize=1)
def _load_whisper_model():
    return whisper.load_model(WHISPER_MODEL)


def transcribe_audio(audio_path: Path) -> tuple[str, str | None]:
    result = _load_whisper_model().transcribe(str(audio_path))
    return result["text"].strip(), result.get("language")
