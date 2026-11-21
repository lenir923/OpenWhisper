"""On-disk ring buffer of the last few recorded audio clips.

The live dictation history is in-memory only, and the transcription
pipeline can occasionally drop a clip (a long upload that hangs, a
transient API failure). Persisting the raw audio of the last N
recordings means any lost dictation can be recovered by re-transcribing
the saved WAV.

Gated behind the `save_audio_history` setting (off by default). The clip
is written BEFORE transcription, so it survives even when the pipeline
fails afterwards.
"""
from __future__ import annotations

import io
import wave
from datetime import datetime
from pathlib import Path
from typing import Optional

import numpy as np

from ..config import audio_history_dir
from ..logging_setup import get_logger
from ..protocols import AudioBuffer

log = get_logger("audio.clip_store")

# How many recent clips to keep on disk. Older ones are pruned.
MAX_CLIPS = 10


def _float32_to_wav_bytes(samples: np.ndarray, sample_rate: int) -> bytes:
    """Encode a mono Float32 array to a 16-bit PCM WAV blob."""
    if samples.dtype != np.float32:
        samples = samples.astype(np.float32, copy=False)
    clipped = np.clip(samples, -1.0, 1.0)
    int16 = (clipped * 32767.0).astype(np.int16)
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # int16 = 2 bytes
        wav.setframerate(sample_rate)
        wav.writeframes(int16.tobytes())
    return buf.getvalue()


def save_clip(audio: AudioBuffer, max_clips: int = MAX_CLIPS) -> Optional[Path]:
    """Persist one recording to the audio-history dir and prune to max_clips.

    Returns the path written, or None on any failure. Never raises, so the
    dictation pipeline is never broken by a disk problem.
    """
    try:
        if audio.samples.size == 0:
            return None
        directory = audio_history_dir()
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
        path = directory / f"clip_{stamp}.wav"
        path.write_bytes(_float32_to_wav_bytes(audio.samples, audio.sample_rate))
        _prune(directory, max_clips)
        log.info("Saved audio clip (%.1fs): %s", audio.duration, path.name)
        return path
    except Exception as exc:  # never break the pipeline over a saved clip
        log.warning("Could not save audio clip: %s", exc)
        return None


def save_transcript(clip_path: Path, raw_transcript: str, final_text: str) -> None:
    """Write the transcript next to its clip as a .txt sidecar. Best-effort."""
    try:
        if final_text == raw_transcript:
            body = final_text
        else:
            body = f"{final_text}\n\n--- transcript brut ---\n{raw_transcript}"
        clip_path.with_suffix(".txt").write_text(body, encoding="utf-8")
    except Exception as exc:
        log.warning("Could not save clip transcript: %s", exc)


def _prune(directory: Path, max_clips: int) -> None:
    """Keep only the newest max_clips WAVs (and their .txt sidecars)."""
    if max_clips <= 0:
        return
    clips = sorted(directory.glob("clip_*.wav"), key=lambda p: p.stat().st_mtime)
    for old in clips[:-max_clips]:
        try:
            old.unlink()
            old.with_suffix(".txt").unlink(missing_ok=True)
        except OSError:
            pass
