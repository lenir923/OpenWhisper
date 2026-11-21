"""Tests for the text-insertion method dispatch.

These cover the platform-agnostic logic in BaseInserter (paste vs
clipboard-only vs direct typing, plus the typing fallback) and the Windows
UTF-16 splitting helper used by direct typing.
"""
from __future__ import annotations

import sys

import pytest

from openwhisper.platform import base_inserter
from openwhisper.platform.base_inserter import BaseInserter, InsertionMethod


class FakeInserter(BaseInserter):
    """Records what the base class asks the platform to do."""

    def __init__(self, supports_typing: bool = True, **kwargs):
        # No clipboard restore by default → no background thread in tests.
        kwargs.setdefault("restore_clipboard", False)
        super().__init__(**kwargs)
        self._supports_typing = supports_typing
        self.pastes = 0
        self.typed: list[str] = []

    @property
    def _platform_name(self) -> str:
        return "fake"

    def _send_paste(self) -> None:
        self.pastes += 1

    def _send_key(self, key: str) -> None:  # pragma: no cover - unused here
        pass

    def _type_text(self, text: str) -> None:
        if not self._supports_typing:
            raise NotImplementedError
        self.typed.append(text)


@pytest.fixture
def copied(monkeypatch):
    """Capture clipboard writes without touching the real clipboard."""
    writes: list[str] = []
    monkeypatch.setattr(base_inserter.pyperclip, "copy", writes.append)
    monkeypatch.setattr(base_inserter.pyperclip, "paste", lambda: "")
    return writes


def test_paste_method_copies_and_pastes(copied):
    ins = FakeInserter(use_clipboard=True)
    ins.insert("hello")
    assert copied == ["hello"]
    assert ins.pastes == 1
    assert ins.typed == []


def test_clipboard_only_copies_without_paste(copied):
    ins = FakeInserter(insertion_method=InsertionMethod.clipboard)
    ins.insert("hello")
    assert copied == ["hello"]
    assert ins.pastes == 0
    assert ins.typed == []


def test_type_method_types_and_skips_clipboard(copied):
    ins = FakeInserter(insertion_method=InsertionMethod.type)
    ins.insert("héllo")
    assert ins.typed == ["héllo"]
    assert copied == []          # text never hits the clipboard
    assert ins.pastes == 0


def test_type_method_falls_back_to_paste_when_unsupported(copied):
    ins = FakeInserter(insertion_method=InsertionMethod.type, supports_typing=False)
    ins.insert("hello")
    assert ins.typed == []
    assert copied == ["hello"]   # fell back to clipboard + paste
    assert ins.pastes == 1


def test_insertion_method_setter_switches_behavior(copied):
    ins = FakeInserter(use_clipboard=True)
    assert ins.insertion_method == InsertionMethod.paste
    ins.insertion_method = InsertionMethod.type
    ins.insert("switch")
    assert ins.typed == ["switch"]
    assert ins.pastes == 0


def test_empty_text_is_a_noop(copied):
    ins = FakeInserter(insertion_method=InsertionMethod.type)
    ins.insert("")
    assert ins.typed == []
    assert copied == []


@pytest.mark.skipif(sys.platform != "win32", reason="Windows typing helper")
def test_utf16_code_units_handles_accents_and_surrogates():
    from openwhisper.platform.windows import _utf16_code_units

    assert _utf16_code_units("a") == [0x0061]
    assert _utf16_code_units("é") == [0x00E9]      # BMP accent, single unit
    assert _utf16_code_units("😀") == [0xD83D, 0xDE00]  # surrogate pair
