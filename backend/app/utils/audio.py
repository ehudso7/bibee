"""Audio processing utilities."""
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path


def get_audio_duration(file_path: str) -> float:
    y, sr = librosa.load(file_path, sr=None, duration=60)
    return librosa.get_duration(y=y, sr=sr)


def load_audio(file_path: str, sr: int = 44100) -> tuple:
    y, orig_sr = librosa.load(file_path, sr=sr, mono=False)
    if y.ndim == 1:
        y = np.stack([y, y])
    return y, sr


def save_audio(audio: np.ndarray, file_path: str, sr: int = 44100):
    Path(file_path).parent.mkdir(parents=True, exist_ok=True)
    if audio.ndim == 2:
        audio = audio.T
    sf.write(file_path, audio, sr)


def normalize_audio(audio: np.ndarray, target_db: float = -3.0) -> np.ndarray:
    rms = np.sqrt(np.mean(audio**2))
    if rms > 0:
        target_rms = 10 ** (target_db / 20)
        audio = audio * (target_rms / rms)
    return np.clip(audio, -1.0, 1.0)
