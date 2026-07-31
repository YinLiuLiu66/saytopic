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
        CREATE TABLE IF NOT EXISTS listened_recordings (
            owner_name TEXT NOT NULL,
            filename TEXT NOT NULL,
            PRIMARY KEY (owner_name, filename)
        )
        """
    )
    return connection


def _record_listen(filename: str, username: str, db_path=STATS_DB) -> int:
    with _database_connection(db_path) as connection:
        connection.execute(
            """
            INSERT OR IGNORE INTO listened_recordings (owner_name, filename)
            VALUES (?, ?)
            """,
            (username, filename),
        )
        row = connection.execute(
            "SELECT COUNT(*) FROM listened_recordings WHERE owner_name = ?",
            (username,),
        ).fetchone()
    return row[0]


def _get_listened_count(username: str, db_path=STATS_DB) -> int:
    with _database_connection(db_path) as connection:
        row = connection.execute(
            "SELECT COUNT(*) FROM listened_recordings WHERE owner_name = ?",
            (username,),
        ).fetchone()
    return row[0]


def _require_username(username: str) -> str:
    username = username.strip()
    if not username or len(username) > 40:
        raise HTTPException(
            status_code=400,
            detail="Username must be between 1 and 40 characters",
        )
    return username


def _require_audio(filename: str) -> str:
    if os.path.basename(filename) != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = os.path.join(UPLOAD_DIR, filename)
    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return file_path


@app.post("/api/upload")
async def upload_audio(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

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

    return {"url": f"/api/audio/{unique_name}", "filename": unique_name}


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    file_path = _require_audio(filename)
    ext = os.path.splitext(filename)[1].lower()
    media_type = AUDIO_MIME_TYPES.get(ext, "application/octet-stream")

    return FileResponse(file_path, media_type=media_type)


@app.post("/api/audio/{filename}/play")
async def record_audio_play(filename: str, username: str):
    _require_audio(filename)
    username = _require_username(username)
    return {"listened_count": _record_listen(filename, username)}


@app.get("/api/listening-stats")
async def get_listening_stats(username: str):
    username = _require_username(username)
    return {"listened_count": _get_listened_count(username)}


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
