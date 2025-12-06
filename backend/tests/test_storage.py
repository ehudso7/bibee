"""Storage utility tests."""
import pytest
from io import BytesIO
from fastapi import UploadFile, HTTPException
from app.utils.storage import validate_audio_file, ALLOWED_AUDIO_EXTENSIONS, ALLOWED_AUDIO_MIMETYPES


def create_upload_file(filename: str, content_type: str | None = None, content: bytes = b"test") -> UploadFile:
    """Create an UploadFile for testing."""
    return UploadFile(
        filename=filename,
        file=BytesIO(content),
        headers={"content-type": content_type} if content_type else {}
    )


class TestValidateAudioFile:
    """Tests for validate_audio_file function."""

    def test_valid_audio_file(self):
        """Test that valid audio files pass validation."""
        file = create_upload_file("test.mp3", "audio/mpeg")
        # Should not raise
        validate_audio_file(file)

    def test_missing_filename(self):
        """Test that files without filename are rejected."""
        file = create_upload_file("", "audio/mpeg")
        file.filename = None
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(file)
        assert exc_info.value.status_code == 400
        assert "Filename is required" in exc_info.value.detail

    def test_invalid_extension(self):
        """Test that invalid file extensions are rejected."""
        file = create_upload_file("test.exe", "audio/mpeg")
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(file)
        assert exc_info.value.status_code == 400
        assert "Invalid file type" in exc_info.value.detail

    def test_missing_content_type(self):
        """Test that files without Content-Type header are rejected."""
        file = create_upload_file("test.mp3", None)
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(file)
        assert exc_info.value.status_code == 400
        assert "Content-Type header is required" in exc_info.value.detail

    def test_invalid_content_type(self):
        """Test that invalid MIME types are rejected."""
        file = create_upload_file("test.mp3", "application/octet-stream")
        with pytest.raises(HTTPException) as exc_info:
            validate_audio_file(file)
        assert exc_info.value.status_code == 400
        assert "Invalid audio file type" in exc_info.value.detail

    @pytest.mark.parametrize("ext,mime", [
        (".mp3", "audio/mpeg"),
        (".wav", "audio/wav"),
        (".wav", "audio/x-wav"),
        (".flac", "audio/flac"),
        (".m4a", "audio/m4a"),
        (".m4a", "audio/mp4"),
        (".ogg", "audio/ogg"),
        (".aac", "audio/aac"),
        (".wma", "audio/x-ms-wma"),
    ])
    def test_all_allowed_formats(self, ext: str, mime: str):
        """Test that all allowed audio formats pass validation."""
        file = create_upload_file(f"test{ext}", mime)
        # Should not raise
        validate_audio_file(file)

    def test_case_insensitive_extension(self):
        """Test that file extensions are handled case-insensitively."""
        file = create_upload_file("test.MP3", "audio/mpeg")
        # Should not raise - extension should be lowercased
        validate_audio_file(file)
