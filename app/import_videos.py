"""Import videos into MySQL after extracting audio, transcribing, and tagging."""

import argparse
import os
import re
from pathlib import Path

from .database import connect
from .media import extract_audio, probe_video, transcribe_audio
from .settings import AUDIOS_DIR, PROJECT_ROOT, VIDEOS_DIR
from .tag_extraction import extract_tags


IMPORT_USERNAME = "Local Video Importer"
IMPORT_EMAIL = "local-importer@localhost"
IMPORT_CHANNEL = "Local Video Imports"
DEFAULT_CATEGORY = "Uncategorized"
VIDEO_EXTENSIONS = {".mp4", ".mov", ".mkv", ".avi", ".webm"}


def _format_filename_title(filename: str) -> str:
    spaced = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", filename)
    spaced = re.sub(r"(?<=[A-Za-z])(?=\d)", " ", spaced)
    return spaced.title()


def _format_phrase_title(phrase: str) -> str:
    connectors = {"of", "the", "and", "in", "at", "to", "for"}
    return " ".join(
        word.lower() if index and word.lower() in connectors else word.capitalize()
        for index, word in enumerate(phrase.split())
    )


def _metadata_value(metadata: dict, *keys: str) -> str | None:
    tags = metadata.get("tags", {})
    lowercase_tags = {key.lower(): value for key, value in tags.items()}
    for key in keys:
        value = lowercase_tags.get(key)
        if value and str(value).strip():
            return str(value).strip()
    return None


def _make_title(video_path: Path, metadata: dict, transcript: str, tags: list[str]) -> str:
    title = _metadata_value(metadata, "title")
    detected_phrase = next((tag for tag in tags if " " in tag), None)
    if not title and detected_phrase and len(transcript) > 300:
        title = _format_phrase_title(detected_phrase)
    return (title or _format_filename_title(video_path.stem))[:255]


def _make_description(metadata: dict, transcript: str) -> str:
    description = _metadata_value(metadata, "description", "comment")
    if description:
        return description[:2000]
    clean_transcript = " ".join(transcript.split())
    if len(clean_transcript) <= 2000:
        return clean_transcript
    return clean_transcript[:1997].rsplit(" ", 1)[0] + "..."


def _relative_path(path: Path) -> str:
    return Path(os.path.relpath(path, PROJECT_ROOT)).as_posix()


def _existing_video_paths(video_paths: list[str]) -> set[str]:
    connection = connect()
    try:
        cursor = connection.cursor()
        try:
            placeholders = ",".join(["%s"] * len(video_paths))
            cursor.execute(
                f"SELECT video_path FROM videos WHERE video_path IN ({placeholders})",
                tuple(video_paths),
            )
            return {row[0] for row in cursor.fetchall()}
        finally:
            cursor.close()
    finally:
        connection.close()


def _ensure_reference_rows(cursor) -> tuple[int, int, int]:
    cursor.execute(
        "INSERT IGNORE INTO users (username, email) VALUES (%s, %s)",
        (IMPORT_USERNAME, IMPORT_EMAIL),
    )
    cursor.execute("SELECT user_id FROM users WHERE email = %s", (IMPORT_EMAIL,))
    user_id = cursor.fetchone()[0]

    cursor.execute(
        "INSERT IGNORE INTO channels (user_id, channel_name) VALUES (%s, %s)",
        (user_id, IMPORT_CHANNEL),
    )
    cursor.execute(
        "SELECT channel_id FROM channels WHERE user_id = %s AND channel_name = %s",
        (user_id, IMPORT_CHANNEL),
    )
    channel_id = cursor.fetchone()[0]

    cursor.execute(
        "INSERT IGNORE INTO categories (category_name) VALUES (%s)",
        (DEFAULT_CATEGORY,),
    )
    cursor.execute(
        "SELECT category_id FROM categories WHERE category_name = %s",
        (DEFAULT_CATEGORY,),
    )
    category_id = cursor.fetchone()[0]
    return user_id, channel_id, category_id


def _save_videos(items: list[dict]) -> int:
    connection = connect()
    try:
        cursor = connection.cursor()
        try:
            _, channel_id, category_id = _ensure_reference_rows(cursor)
            for item in items:
                cursor.execute(
                    """INSERT INTO videos
                       (channel_id, category_id, title, description, language,
                        duration, video_path, audio_path, transcript)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                    (
                        channel_id,
                        category_id,
                        item["title"],
                        item["description"],
                        item["language"],
                        item["duration_seconds"],
                        item["video_path"],
                        item["audio_path"],
                        item["transcript"],
                    ),
                )
                video_id = cursor.lastrowid
                for tag_name in item["tags"]:
                    cursor.execute(
                        "INSERT IGNORE INTO tags (tag_name) VALUES (%s)", (tag_name,)
                    )
                    cursor.execute(
                        "SELECT tag_id FROM tags WHERE tag_name = %s", (tag_name,)
                    )
                    tag_id = cursor.fetchone()[0]
                    cursor.execute(
                        "INSERT IGNORE INTO video_tags (video_id, tag_id) VALUES (%s, %s)",
                        (video_id, tag_id),
                    )
            connection.commit()
            return len(items)
        except Exception:
            connection.rollback()
            raise
        finally:
            cursor.close()
    finally:
        connection.close()


def _collect_videos(input_dir: Path, explicit_video: Path | None) -> list[Path]:
    if explicit_video is not None:
        if not explicit_video.is_file():
            raise FileNotFoundError(f"Video not found: {explicit_video}")
        return [explicit_video.resolve()]
    if not input_dir.is_dir():
        raise FileNotFoundError(f"Video folder not found: {input_dir}")
    return sorted(
        path.resolve()
        for path in input_dir.iterdir()
        if path.is_file() and path.suffix.lower() in VIDEO_EXTENSIONS
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-dir", type=Path, default=VIDEOS_DIR)
    parser.add_argument("--video", type=Path, help="import one video file")
    args = parser.parse_args()

    video_paths = _collect_videos(args.input_dir, args.video)
    if not video_paths:
        print(f"No video files found in {args.input_dir}")
        print("Copy videos into the dbms/videos folder, then run this command again.")
        return

    relative_paths = [_relative_path(path) for path in video_paths]
    existing = _existing_video_paths(relative_paths)
    new_videos = [
        (path, relative)
        for path, relative in zip(video_paths, relative_paths)
        if relative not in existing
    ]
    if not new_videos:
        print("All videos in this input are already in MySQL; nothing to import.")
        return

    processed = []
    for video_path, relative_video_path in new_videos:
        print(f"Processing {video_path.name}: extracting audio at 16 kHz...", flush=True)
        audio_path = AUDIOS_DIR / f"{video_path.stem}.wav"
        metadata = probe_video(video_path)
        audio_path = extract_audio(video_path, audio_path)
        transcript, language = transcribe_audio(audio_path)
        if not transcript:
            raise RuntimeError(f"Whisper returned an empty transcript for {video_path.name}")

        duration = round(float(metadata["duration"]))
        processed.append(
            {
                "source": video_path,
                "metadata": metadata,
                "video_path": relative_video_path,
                "audio_path": _relative_path(audio_path),
                "duration_seconds": duration,
                "transcript": transcript,
                "language": language,
            }
        )

    tag_lists = extract_tags([item["transcript"] for item in processed])
    for item, tags in zip(processed, tag_lists):
        item["title"] = _make_title(item["source"], item["metadata"], item["transcript"], tags)
        item["description"] = _make_description(item["metadata"], item["transcript"])
        item["tags"] = tags

    inserted = _save_videos(processed)
    for item in processed:
        print(
            f"Saved {item['title']} | {item['duration_seconds']} seconds | "
            f"language={item['language']} | tags={item['tags']}"
        )
    print(f"Imported {inserted} video(s) into MySQL.")


if __name__ == "__main__":
    main()
