"""Long recordings must be split under Groq's request-size limit.

Regression test for the HTTP 413 "request_too_large" failure: a 20 min
or 1 h dictation encodes to a WAV larger than Groq's ~25 MB cap, so the
whole transcription was dropped. We now split into sequential chunks that
each stay under the limit, losslessly.
"""
import numpy as np

from openwhisper.stt.groq_provider import (
    GROQ_MAX_REQUEST_BYTES,
    _float32_to_wav_bytes,
    _split_for_upload,
)

SR = 16_000


def _wav_size(samples: np.ndarray, sample_rate: int = SR) -> int:
    return len(_float32_to_wav_bytes(samples, sample_rate))


def test_short_audio_stays_single_chunk():
    samples = np.zeros(5 * SR, dtype=np.float32)  # 5 seconds
    chunks = _split_for_upload(samples, SR)
    assert len(chunks) == 1
    assert np.array_equal(chunks[0], samples)


def test_twenty_minute_recording_splits_under_limit():
    # 20 min of 16 kHz/16-bit WAV is ~38 MB, over the 25 MB Groq limit.
    samples = np.zeros(20 * 60 * SR, dtype=np.float32)
    assert _wav_size(samples) > GROQ_MAX_REQUEST_BYTES  # precondition: would 413

    chunks = _split_for_upload(samples, SR)

    assert len(chunks) >= 2
    for c in chunks:
        assert len(c) > 0
        assert _wav_size(c) <= GROQ_MAX_REQUEST_BYTES
    # Lossless: stitching the chunks reproduces the original exactly.
    assert np.array_equal(np.concatenate(chunks), samples)


def test_one_hour_recording_splits_and_loses_nothing():
    samples = np.zeros(60 * 60 * SR, dtype=np.float32)
    chunks = _split_for_upload(samples, SR)
    assert len(chunks) >= 4
    for c in chunks:
        assert _wav_size(c) <= GROQ_MAX_REQUEST_BYTES
    assert sum(len(c) for c in chunks) == len(samples)
