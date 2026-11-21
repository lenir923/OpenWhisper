"""A recording must never be destroyed by the silence gate.

Regression test for the 2026-09-18 failure. A laptop mic array delivers
speech at RMS 0.008-0.02 and an idle room at ~0.0007, so the 0.005
"silence" threshold sat inside the range of real speech: a genuine
dictation was classified as silence and dropped. Three things made it
unrecoverable rather than merely annoying:

  * the rejection was a log.debug the INFO-level log file never wrote,
  * the HUD went straight back to idle, so it read as a crash,
  * the gate returned *before* save_clip(), so the audio history that
    exists precisely to make a lost dictation recoverable never saw it.

Measured on the reference machine (Intel Smart Sound mic array): idle
room RMS 0.00018-0.0007, real dictations 0.0075-0.0174, peak never
above 0.26.
"""
import logging

import numpy as np
import pytest

from openwhisper.coordinator import DictationCoordinator, MIN_AUDIO_RMS
from openwhisper.protocols import AudioBuffer, CleanupResult, Transcript
from openwhisper.settings import AppSettings
from openwhisper.ui.ui_state import Phase, UIState

SR = 16_000

# Levels measured on the reference machine, not invented.
IDLE_ROOM_RMS = 0.0007       # microphone open, nobody speaking
QUIET_SPEECH_RMS = 0.004     # real speech, low-gain mic: the destroyed case
NORMAL_SPEECH_RMS = 0.012    # a typical working dictation


def _audio(rms: float, seconds: float = 3.0) -> AudioBuffer:
    """Noise scaled to an exact RMS, standing in for a recording."""
    rng = np.random.default_rng(7)
    samples = rng.standard_normal(int(seconds * SR)).astype(np.float32)
    samples *= rms / float(np.sqrt(np.mean(samples**2)))
    return AudioBuffer(samples=samples, sample_rate=SR)


class _FakeRecorder:
    def set_levels_callback(self, callback) -> None:
        self._callback = callback


class _FakeHotkey:
    on_event = None

    def register(self, hotkeys) -> None:
        pass


class _FakeSTT:
    identifier = "fake"
    is_available = True

    def __init__(self) -> None:
        self.transcribed = []

    def transcribe(self, audio, dictionary_hints):
        self.transcribed.append(audio)
        return Transcript(text="bonjour")


class _FakeCleanup:
    def run(self, text, settings):
        return CleanupResult(cleaned=text)


class _FakeInserter:
    def __init__(self) -> None:
        self.inserted = []

    def insert(self, text) -> None:
        self.inserted.append(text)


class _FakeHistory:
    def record(self, entry) -> None:
        pass


class _FakeSettingsStore:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    @property
    def settings(self) -> AppSettings:
        return self._settings


class _Harness:
    """A coordinator wired to fakes, plus what the pipeline did."""

    def __init__(self, monkeypatch, save_audio_history: bool = True) -> None:
        self.stt = _FakeSTT()
        self.inserter = _FakeInserter()
        self.ui_state = UIState()
        self.phases = []
        self.ui_state.phaseChanged.connect(
            lambda phase, message: self.phases.append((phase, message))
        )
        self.saved_clips = []
        monkeypatch.setattr(
            "openwhisper.coordinator.save_clip",
            lambda audio: self.saved_clips.append(audio) or None,
        )
        self.coordinator = DictationCoordinator(
            settings_store=_FakeSettingsStore(
                AppSettings(save_audio_history=save_audio_history)
            ),
            recorder=_FakeRecorder(),
            stt_factory=lambda: self.stt,
            cleanup_factory=_FakeCleanup,
            inserter=self.inserter,
            hotkey=_FakeHotkey(),
            history=_FakeHistory(),
            ui_state=self.ui_state,
        )

    def run(self, audio: AudioBuffer) -> None:
        # Call the pipeline body directly: the worker thread and the Qt
        # event loop are not what this test is about.
        self.coordinator._run_pipeline_inner(audio)


@pytest.fixture
def harness(monkeypatch):
    return _Harness(monkeypatch)


def test_quiet_speech_is_still_transcribed(harness):
    """The destroyed case: real speech on a low-gain mic must go through."""
    harness.run(_audio(QUIET_SPEECH_RMS))
    assert harness.stt.transcribed, (
        f"speech at RMS {QUIET_SPEECH_RMS} was discarded as silence; "
        f"threshold is {MIN_AUDIO_RMS}"
    )
    assert harness.inserter.inserted == ["bonjour"]


def test_normal_speech_is_transcribed(harness):
    harness.run(_audio(NORMAL_SPEECH_RMS))
    assert harness.stt.transcribed


def test_silence_is_not_transcribed(harness):
    """The gate must still do its job: no Whisper call on an idle room."""
    harness.run(_audio(IDLE_ROOM_RMS))
    assert not harness.stt.transcribed


def test_discarded_recording_is_still_saved_to_audio_history(harness):
    """Nothing the gate throws away may be unrecoverable."""
    harness.run(_audio(IDLE_ROOM_RMS))
    assert harness.saved_clips, "a discarded recording left no clip on disk"


def test_discarding_is_logged_at_info_or_above(harness, caplog):
    """A drop the log file never records is a drop nobody can debug."""
    with caplog.at_level(logging.INFO, logger="openwhisper.coordinator"):
        harness.run(_audio(IDLE_ROOM_RMS))
    assert caplog.records, "the recording vanished with no log line"


def test_discarding_tells_the_user(harness):
    """Going straight back to idle reads as a crash. Say something."""
    harness.run(_audio(IDLE_ROOM_RMS))
    assert Phase.error in [phase for phase, _ in harness.phases], (
        f"HUD never left idle: {harness.phases}"
    )


def test_accidental_tap_stays_quiet(harness):
    """A 0.1s press said nothing and lost nothing: no error badge."""
    harness.run(_audio(NORMAL_SPEECH_RMS, seconds=0.1))
    assert not harness.stt.transcribed
    assert Phase.error not in [phase for phase, _ in harness.phases]
