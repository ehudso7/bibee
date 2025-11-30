"""Audio mixing pipeline."""
import numpy as np
import librosa
import soundfile as sf
from pathlib import Path
from typing import Optional, Callable


def mix_tracks(
    instrumental_path: str,
    vocal_path: str,
    output_path: str,
    vocal_level: float = 0.0,
    reverb_amount: float = 0.2,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> str:
    """Mix instrumental and vocal tracks."""
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    if progress_callback:
        progress_callback(10, "Loading tracks...")

    # Load audio
    instrumental, sr = librosa.load(instrumental_path, sr=44100, mono=False)
    vocal, _ = librosa.load(vocal_path, sr=44100, mono=False)

    if instrumental.ndim == 1:
        instrumental = np.stack([instrumental, instrumental])
    if vocal.ndim == 1:
        vocal = np.stack([vocal, vocal])

    if progress_callback:
        progress_callback(30, "Adjusting levels...")

    # Adjust vocal level (dB)
    vocal_gain = 10 ** (vocal_level / 20)
    vocal = vocal * vocal_gain

    if progress_callback:
        progress_callback(50, "Mixing...")

    # Match lengths
    min_len = min(instrumental.shape[1], vocal.shape[1])
    instrumental = instrumental[:, :min_len]
    vocal = vocal[:, :min_len]

    # Mix
    mixed = instrumental + vocal

    # Normalize
    max_val = np.max(np.abs(mixed))
    if max_val > 0.95:
        mixed = mixed * (0.95 / max_val)

    if progress_callback:
        progress_callback(80, "Saving...")

    # Save
    sf.write(output_path, mixed.T, sr)

    if progress_callback:
        progress_callback(100, "Done")

    return output_path
