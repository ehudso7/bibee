"""File storage utilities."""
import os
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile
from app.config import settings


async def save_upload(file: UploadFile, subdir: str) -> str:
    storage_path = Path(settings.storage_path) / subdir
    storage_path.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix if file.filename else ".bin"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = storage_path / filename

    async with aiofiles.open(filepath, "wb") as f:
        content = await file.read()
        await f.write(content)

    return str(filepath)


def get_file_path(relative_path: str) -> Path:
    return Path(settings.storage_path) / relative_path
