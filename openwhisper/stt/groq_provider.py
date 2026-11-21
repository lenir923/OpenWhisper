"""Cloud speech-to-text via Groq's OpenAI-compatible audio endpoint.

Why Groq: `whisper-large-v3-turbo` runs at ~216x realtime on Groq's
inference hardware, so a 5-second dictation typically finalizes in
well under a second — closing most of the gap with commercial
dictation tools while still costing roughly nothing ($0.04/hour).

We encode our in-memory Float32 samples to a 16-bit PCM WAV and POST
it as multipart/form-data using `httpx`.
"""
from __future__ import annotations

import io
import threading
import wave
from typing import Callable, List, Optional, Union

import httpx
import numpy as np

from ..errors import ApiKeyMissing, TranscriptionFailed
from ..logging_setup import get_logger
from ..protocols import AudioBuffer, Transcript

log = get_logger("stt.groq")


GROQ_ENDPOINT = "https://api.groq.com/openai/v1/audio/transcriptions"
DEFAULT_MODEL = "whisper-large-v3-turbo"

# Groq's audio endpoint rejects requests above ~25 MB (free tier) with
# HTTP 413 "request_too_large", which silently dropped any recording over
# ~13 min. We keep a safety margin and split longer recordings into
# sequential chunks that each stay under the cap. WAV here is 16-bit mono,
# so bytes ~= 44-byte header + 2 * samples.
GROQ_MAX_REQUEST_BYTES = 24 * 1024 * 1024  # 24 MB, under Groq's 25 MB cap
_WAV_HEADER_BYTES = 44
_WAV_BYTES_PER_SAMPLE = 2
# Also cap each chunk by wall-clock so a single upload stays small and quick
# even on a slow connection (10 min @ 16 kHz ~= 19 MB).
MAX_CHUNK_SECONDS = 600


class GroqWhisperProvider:
    identifier = "groq"

    def __init__(
        self,
        api_key: Union[str, Callable[[], str]],
        model: str = DEFAULT_MODEL,
        languages: Optional[List[str]] = None,
        # Large chunks (up to ~19 MB) need more than 30 s to upload on a
        # slow connection, otherwise httpx raises a write timeout.
        timeout: float = 120.0,
        on_usage: Optional[Callable[[float], None]] = None,
    ):
        # Security: Support callback-based key retrieval to minimize time
        # the API key is held in memory. If a string is passed, we still
        # validate it but prefer callback-based usage.
        if callable(api_key):
            self._key_provider: Optional[Callable[[], str]] = api_key
            # Validate the key is available
            test_key = api_key()
            if not test_key:
                raise ApiKeyMissing("Groq API key is empty")
        else:
            if not api_key:
                raise ApiKeyMissing("Groq API key is empty")
            # For backwards compatibility, wrap static key in a lambda
            self._key_provider = lambda: api_key
        self.model = model
        self.languages: List[str] = list(languages) if languages else ["en"]
        # A pooled connection that died during sleep / Wi-Fi change made the
        # next request hang until the full timeout (~150 s observed on the
        # first dictation after a pause). Fail fast on connect/read and keep
        # idle connections only briefly; _post_wav retries once on a fresh one.
        self._timeout = httpx.Timeout(timeout, connect=5.0, read=30.0, pool=5.0)
        self._client = self._new_client()
        self._load_error: Optional[str] = None
        self._lock = threading.Lock()
        self._on_usage = on_usage
        self._closed = False

    def _new_client(self) -> httpx.Client:
        # Security: Explicitly verify TLS certificates (defense in depth)
        limits = httpx.Limits(max_keepalive_connections=2, keepalive_expiry=20)
        try:
            return httpx.Client(
                timeout=self._timeout, http2=True, verify=True, limits=limits
            )
        except Exception:
            # h2 not installed: HTTP/1.1 with keep-alive
            return httpx.Client(timeout=self._timeout, verify=True, limits=limits)

    def _reset_client(self) -> None:
        try:
            self._client.close()
        except Exception:
            pass
        self._client = self._new_client()

    def __del__(self) -> None:
        self.close()

    def close(self) -> None:
        """Close the HTTP client and release resources."""
        if self._closed:
            return
        self._closed = True
        try:
            self._client.close()
        except Exception:
            pass

    @property
    def is_available(self) -> bool:
        return self._load_error is None

    def warmup(self) -> None:
        """No-op: Groq is a stateless HTTP endpoint, nothing to preload."""
        return

    def transcribe(self, audio: AudioBuffer, dictionary_hints: List[str]) -> Transcript:
        if audio.samples.size == 0:
            return Transcript(text="")

        forced_language = self.languages[0] if len(self.languages) == 1 else None

        data: dict[str, str] = {
            "model": self.model,
            # Plain text is ~10x smaller than JSON on the wire and we
            # only need the text here.
            "response_format": "text",
            "temperature": "0",
        }
        if forced_language:
            data["language"] = forced_language
        if dictionary_hints:
            # Groq's /audio/transcriptions accepts an OpenAI-style prompt
            # that biases decoding toward the listed terms.
            data["prompt"] = "Vocabulary: " + ", ".join(dictionary_hints[:64])

        # Security: Fetch key just-in-time to minimize memory exposure
        api_key = self._key_provider() if self._key_provider else ""
        if not api_key:
            raise ApiKeyMissing("Groq API key is not available")
        headers = {"Authorization": f"Bearer {api_key}"}
        del api_key  # Security: clear from local scope immediately after use

        # A single recording over Groq's size cap returns HTTP 413 and would
        # be dropped whole, so split long audio into sequential chunks and
        # stitch the transcripts back together.
        chunks = _split_for_upload(audio.samples, audio.sample_rate)
        parts: List[str] = []
        for chunk in chunks:
            wav_bytes = _float32_to_wav_bytes(chunk, audio.sample_rate)
            part = self._post_wav(wav_bytes, data, headers)
            if part:
                parts.append(part)

        self._load_error = None
        if self._on_usage is not None:
            try:
                self._on_usage(audio.duration)
            except Exception:  # pragma: no cover
                pass

        text = " ".join(parts).strip()
        log.info(
            "Groq transcribed %.2fs in %d chunk(s) (%d chars)",
            audio.duration,
            len(chunks),
            len(text),
        )
        return Transcript(
            text=text,
            confidence=1.0 if text else 0.0,
        )

    def _post_wav(self, wav_bytes: bytes, data: dict, headers: dict) -> str:
        """POST one WAV blob to Groq and return its transcript text."""
        resp = None
        last_exc: Optional[Exception] = None
        for attempt in range(2):
            files = {"file": ("audio.wav", wav_bytes, "audio/wav")}
            try:
                with self._lock:
                    resp = self._client.post(
                        GROQ_ENDPOINT, headers=headers, data=data, files=files
                    )
                break
            except httpx.TransportError as exc:
                # Stale pooled connection or network blip: retry once on a
                # brand-new connection instead of waiting on a dead socket.
                last_exc = exc
                log.warning("Groq request failed (attempt %d): %r", attempt + 1, exc)
                with self._lock:
                    self._reset_client()
            except Exception as exc:
                last_exc = exc
                break
        if resp is None:
            self._load_error = str(last_exc)
            raise TranscriptionFailed(f"Groq request failed: {last_exc}") from last_exc

        if resp.status_code != 200:
            body = resp.text[:300]
            self._load_error = f"HTTP {resp.status_code}"
            raise TranscriptionFailed(f"Groq HTTP {resp.status_code}: {body}")

        if data.get("response_format") == "text":
            return resp.text.strip()
        # Fallback parse if we ever switch response_format back to json.
        try:
            return ((resp.json() or {}).get("text", "") or "").strip()
        except Exception:
            return ""


def _max_chunk_samples(sample_rate: int) -> int:
    """Largest sample count whose 16-bit mono WAV stays under the size cap,
    also bounded by MAX_CHUNK_SECONDS so each upload is small and quick."""
    by_bytes = (GROQ_MAX_REQUEST_BYTES - _WAV_HEADER_BYTES) // _WAV_BYTES_PER_SAMPLE
    by_time = int(MAX_CHUNK_SECONDS * sample_rate)
    return max(1, min(by_bytes, by_time))


def _split_for_upload(samples: np.ndarray, sample_rate: int) -> List[np.ndarray]:
    """Split a recording into sequential chunks that each encode to a WAV
    blob under Groq's request-size limit. Short audio returns a single
    chunk; concatenating the chunks reproduces the original samples exactly.
    """
    max_samples = _max_chunk_samples(sample_rate)
    if len(samples) <= max_samples:
        return [samples]
    return [samples[i : i + max_samples] for i in range(0, len(samples), max_samples)]


def _float32_to_wav_bytes(samples: np.ndarray, sample_rate: int) -> bytes:
    """Encode a mono Float32 array to a 16-bit PCM WAV blob."""
    if samples.dtype != np.float32:
        samples = samples.astype(np.float32, copy=False)
    # Clip then scale to int16.
    clipped = np.clip(samples, -1.0, 1.0)
    int16 = (clipped * 32767.0).astype(np.int16)

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # int16 = 2 bytes
        wav.setframerate(sample_rate)
        wav.writeframes(int16.tobytes())
    return buf.getvalue()
