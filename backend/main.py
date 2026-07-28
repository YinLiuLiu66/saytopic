import os
import sqlite3
import uuid

from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

app = FastAPI(title="SayTopic API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://frp-off.com:23506"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
STATS_DB = os.path.join(UPLOAD_DIR, "stats.sqlite3")

ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".webm", ".ogg", ".m4a", ".wav"}
AUDIO_MIME_TYPES = {
    ".mp3": "audio/mpeg",
    ".webm": "audio/webm",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",
    ".wav": "audio/wav",
}

ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
IMAGE_MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


def _database_connection(db_path=STATS_DB):
    connection = sqlite3.connect(db_path)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS audio_stats (
            filename TEXT PRIMARY KEY,
            play_count INTEGER NOT NULL DEFAULT 0
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS recordings (
            filename TEXT PRIMARY KEY,
            owner_name TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT (
                strftime('%Y-%m-%dT%H:%M:%SZ', 'now')
            )
        )
        """
    )
    return connection


def _get_play_count(filename: str, db_path=STATS_DB) -> int:
    with _database_connection(db_path) as connection:
        row = connection.execute(
            "SELECT play_count FROM audio_stats WHERE filename = ?",
            (filename,),
        ).fetchone()
    return row[0] if row else 0


def _increment_play_count(filename: str, db_path=STATS_DB) -> int:
    with _database_connection(db_path) as connection:
        connection.execute(
            """
            INSERT INTO audio_stats (filename, play_count)
            VALUES (?, 1)
            ON CONFLICT(filename) DO UPDATE SET play_count = play_count + 1
            """,
            (filename,),
        )
        row = connection.execute(
            "SELECT play_count FROM audio_stats WHERE filename = ?",
            (filename,),
        ).fetchone()
    return row[0]


def _save_recording(filename: str, owner_name: str, db_path=STATS_DB) -> None:
    with _database_connection(db_path) as connection:
        connection.execute(
            "INSERT INTO recordings (filename, owner_name) VALUES (?, ?)",
            (filename, owner_name),
        )


def _list_recordings(owner_name: str, db_path=STATS_DB) -> list[dict]:
    with _database_connection(db_path) as connection:
        rows = connection.execute(
            """
            SELECT recordings.filename, recordings.created_at,
                   COALESCE(audio_stats.play_count, 0)
            FROM recordings
            LEFT JOIN audio_stats USING (filename)
            WHERE recordings.owner_name = ?
            ORDER BY recordings.created_at DESC
            """,
            (owner_name,),
        ).fetchall()
    return [
        {
            "filename": filename,
            "url": f"/api/audio/{filename}",
            "created_at": created_at,
            "play_count": play_count,
        }
        for filename, created_at, play_count in rows
    ]


def _require_owner_name(owner_name: str) -> str:
    owner_name = owner_name.strip()
    if not owner_name or len(owner_name) > 40:
        raise HTTPException(
            status_code=400,
            detail="Username must be between 1 and 40 characters",
        )
    return owner_name


def _require_audio(filename: str) -> str:
    if os.path.basename(filename) != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return file_path


@app.post("/api/upload")
async def upload_audio(
    file: UploadFile = File(...),
    owner_name: str = Form(...),
):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    owner_name = _require_owner_name(owner_name)
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}"
        )

    unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    content = await file.read()
    with open(file_path, "wb") as f:
        f.write(content)
    _save_recording(unique_name, owner_name)

    return {"url": f"/api/audio/{unique_name}", "filename": unique_name}


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    file_path = _require_audio(filename)
    ext = os.path.splitext(filename)[1].lower()
    media_type = AUDIO_MIME_TYPES.get(ext, "application/octet-stream")

    return FileResponse(file_path, media_type=media_type)


@app.get("/api/audio/{filename}/stats")
async def get_audio_stats(filename: str):
    _require_audio(filename)
    return {"play_count": _get_play_count(filename)}


@app.post("/api/audio/{filename}/play")
async def record_audio_play(filename: str):
    _require_audio(filename)
    return {"play_count": _increment_play_count(filename)}


@app.get("/api/recordings")
async def list_recordings(owner_name: str):
    owner_name = _require_owner_name(owner_name)
    return {"recordings": _list_recordings(owner_name)}


@app.post("/api/upload-image")
async def upload_image(file: UploadFile = File(...), audio_filename: Optional[str] = Form(None)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format. Allowed: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}"
        )

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Image too large. Maximum size: {MAX_IMAGE_SIZE // (1024 * 1024)}MB"
        )

    if audio_filename:
        base = os.path.splitext(audio_filename)[0]
        unique_name = f"{base}{ext}"
    else:
        unique_name = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, unique_name)

    with open(file_path, "wb") as f:
        f.write(content)

    return {"url": f"/api/image/{unique_name}", "filename": unique_name}


@app.api_route("/api/image/{filename}", methods=["GET", "HEAD"])
async def get_image(filename: str):
    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")

    ext = os.path.splitext(filename)[1].lower()
    media_type = IMAGE_MIME_TYPES.get(ext, "application/octet-stream")

    return FileResponse(file_path, media_type=media_type)
