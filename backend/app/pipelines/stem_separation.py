"""Stem separation using Demucs."""
import os
import subprocess
from pathlib import Path
from typing import Dict, Optional, Callable


def separate_stems(
    input_path: str,
    output_dir: str,
    model_name: str = "htdemucs",
    device: Optional[str] = None,
    progress_callback: Optional[Callable[[int, str], None]] = None,
) -> Dict[str, str]:
    """Separate audio into stems using Demucs."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    if progress_callback:
        progress_callback(10, "Starting stem separation...")

    cmd = ["python", "-m", "demucs", "-n", model_name, "-o", output_dir, input_path]
    if device:
        cmd.extend(["-d", device])

    try:
        subprocess.run(cmd, check=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Demucs failed: {e.stderr.decode()}")

    if progress_callback:
        progress_callback(90, "Processing complete")

    # Find output files
    input_name = Path(input_path).stem
    stems_dir = Path(output_dir) / model_name / input_name

    stems = {}
    for stem_name in ["vocals", "drums", "bass", "other"]:
        stem_path = stems_dir / f"{stem_name}.wav"
        if stem_path.exists():
            stems[stem_name] = str(stem_path)

    if progress_callback:
        progress_callback(100, "Done")

    return stems
