"""File storage utilities."""
import uuid
import aiofiles
from pathlib import Path
from fastapi import UploadFile, HTTPException
from app.config import settings

# Allowed audio file extensions and MIME types
ALLOWED_AUDIO_EXTENSIONS = {".mp3", ".wav", ".flac", ".m4a", ".ogg", ".aac", ".wma"}
ALLOWED_AUDIO_MIMETYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/flac",
    "audio/m4a",
    "audio/mp4",
    "audio/ogg",
    "audio/aac",
    "audio/x-ms-wma",
}


def validate_audio_file(file: UploadFile) -> None:
    """Validate that the uploaded file is an allowed audio format."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        )

    # Require Content-Type header to prevent bypass
    if not file.content_type:
        raise HTTPException(
            status_code=400,
            detail="Content-Type header is required",
        )

    if file.content_type not in ALLOWED_AUDIO_MIMETYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid audio file type",
        )


async def save_upload(
    file: UploadFile,
    subdir: str,
    validate_audio: bool = True,
    max_size_mb: int | None = None,
) -> str:
    """Save an uploaded file to storage.

    Args:
        file: The uploaded file
        subdir: Subdirectory within storage path
        validate_audio: Whether to validate the file is an audio file
        max_size_mb: Maximum file size in MB (defaults to settings.max_upload_size_mb)
    """
    if validate_audio:
        validate_audio_file(file)

    effective_max_size_mb = max_size_mb or settings.max_upload_size_mb
    max_size = effective_max_size_mb * 1024 * 1024

    # Check Content-Length header first to prevent memory exhaustion
    if file.size and file.size > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {effective_max_size_mb}MB",
        )



def validate_audio_file(file: UploadFile) -> None:
    """Validate that the uploaded file is an allowed audio format."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Filename is required")

    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}",
        )

    if file.content_type and file.content_type not in ALLOWED_AUDIO_MIMETYPES:
        raise HTTPException(
            status_code=400,
            detail="Invalid audio file type",
        )


async def save_upload(
    file: UploadFile,
    subdir: str,
    validate_audio: bool = True,
    max_size_mb: int | None = None,
) -> str:
    """Save an uploaded file to storage.

    Args:
        file: The uploaded file
        subdir: Subdirectory within storage path
        validate_audio: Whether to validate the file is an audio file
        max_size_mb: Maximum file size in MB (defaults to settings.max_upload_size_mb)
    """
    if validate_audio:
        validate_audio_file(file)

    max_size = (max_size_mb or settings.max_upload_size_mb) * 1024 * 1024
    storage_path = Path(settings.storage_path) / subdir
    storage_path.mkdir(parents=True, exist_ok=True)

    ext = Path(file.filename).suffix.lower() if file.filename else ".bin"
    filename = f"{uuid.uuid4()}{ext}"
    filepath = storage_path / filename

    # Read and validate actual size (Content-Length can be spoofed)
    # Read and validate size
    content = await file.read()
    if len(content) > max_size:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {effective_max_size_mb}MB",
            detail=f"File too large. Maximum size: {settings.max_upload_size_mb}MB",
        )

    async with aiofiles.open(filepath, "wb") as f:
        await f.write(content)

    return str(filepath)


def get_file_path(relative_path: str) -> Path:
    """Get absolute path for a relative storage path."""
    return Path(settings.storage_path) / relative_path
