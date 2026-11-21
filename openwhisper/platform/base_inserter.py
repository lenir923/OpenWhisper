"""Base class for platform-specific text insertion.

Provides a template method pattern for clipboard-based text insertion
that is shared across all platforms.
"""
from __future__ import annotations

import threading
import time
from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional

import pyperclip

from ..logging_setup import get_logger
from ..protocols import TextInsertionProvider

# Timing constants (security: minimize clipboard exposure)
CLIPBOARD_SETTLE_DELAY = 0.05  # Time for clipboard to be ready (increased for modern apps)
PASTE_COMPLETE_DELAY = 0.08   # Time for paste to complete (increased for modern apps)
CLIPBOARD_RESTORE_DELAY = 0.10  # Delay before restoring to ensure paste completes


class InsertionMethod(str, Enum):
    """How transcribed text reaches the focused application.

    - ``paste``: write to clipboard, then simulate Ctrl+V (fast, the default).
      Fails in terminals, where paste is Ctrl+Shift+V rather than Ctrl+V.
    - ``clipboard``: write to clipboard only; the user pastes manually.
    - ``type``: synthesize the characters as keystrokes, bypassing the
      clipboard entirely. Works in terminals and renders accents regardless
      of keyboard layout, at the cost of being slower on long text.
    """
    paste = "paste"
    clipboard = "clipboard"
    type = "type"


class BaseInserter(TextInsertionProvider, ABC):
    """Base class for text insertion via clipboard + paste simulation.

    Subclasses must implement:
    - _send_paste(): Platform-specific paste command (Ctrl+V or Cmd+V)
    - _send_key(key): Platform-specific key press
    """

    def __init__(
        self,
        restore_clipboard: bool = True,
        use_clipboard: bool = True,
        insertion_method: Optional[InsertionMethod] = None,
    ):
        self._restore = restore_clipboard
        self._use_clipboard = use_clipboard
        # ``insertion_method`` wins when given; otherwise we derive it from the
        # legacy ``use_clipboard`` flag so existing callers keep their behavior.
        if insertion_method is not None:
            self._method = insertion_method
        else:
            self._method = (
                InsertionMethod.paste if use_clipboard else InsertionMethod.clipboard
            )
        self._lock = threading.Lock()
        self._log = get_logger(f"platform.{self._platform_name}.insertion")

    @property
    @abstractmethod
    def _platform_name(self) -> str:
        """Platform name for logging (e.g., 'windows', 'linux', 'macos')."""
        ...

    @property
    def restore_clipboard(self) -> bool:
        return self._restore

    @restore_clipboard.setter
    def restore_clipboard(self, value: bool) -> None:
        self._restore = value

    @property
    def insertion_method(self) -> InsertionMethod:
        return self._method

    @insertion_method.setter
    def insertion_method(self, value: InsertionMethod) -> None:
        self._method = value

    @abstractmethod
    def _send_paste(self) -> None:
        """Send the platform-specific paste command."""
        ...

    @abstractmethod
    def _send_key(self, key: str) -> None:
        """Send a platform-specific key press."""
        ...

    def _type_text(self, text: str) -> None:
        """Type ``text`` as synthesized keystrokes, without the clipboard.

        Platforms that support direct typing override this. The default
        raises so :meth:`insert` can fall back to clipboard paste on
        platforms where typing is not implemented yet.
        """
        raise NotImplementedError

    def insert(self, text: str) -> None:
        """Insert text at the cursor position.

        Uses the configured :class:`InsertionMethod`: direct typing bypasses
        the clipboard; paste / clipboard-only go through it.
        """
        if not text:
            return

        with self._lock:
            self._log.info(
                "insert: starting (%d chars, method=%s)", len(text), self._method.value
            )

            method = self._method

            # Direct-typing mode: synthesize keystrokes, never touch the clipboard.
            if method == InsertionMethod.type:
                try:
                    self._type_text(text)
                    self._log.info("insert: typed directly")
                    return
                except NotImplementedError:
                    self._log.warning(
                        "Direct typing unsupported on %s — falling back to paste",
                        self._platform_name,
                    )
                    # Fall back to a real clipboard paste so the text is still
                    # inserted (clipboard-only would leave it unpasted).
                    method = InsertionMethod.paste

            # Save clipboard if needed
            previous: Optional[str] = None
            if self._restore:
                try:
                    previous = pyperclip.paste()
                except Exception:
                    pass

            # Write to clipboard
            pyperclip.copy(text)
            self._log.info("insert: clipboard write ok")

            if method == InsertionMethod.paste:
                time.sleep(CLIPBOARD_SETTLE_DELAY)
                self._send_paste()
                self._log.info("insert: paste sent")
                time.sleep(PASTE_COMPLETE_DELAY)

            # Restore clipboard in background thread (non-blocking)
            if previous is not None:
                self._schedule_clipboard_restore(previous)

    def _schedule_clipboard_restore(self, previous: str) -> None:
        """Restore clipboard content in a background thread."""
        def _restore() -> None:
            time.sleep(CLIPBOARD_RESTORE_DELAY)
            try:
                pyperclip.copy(previous)
            except Exception:
                pass
        threading.Thread(target=_restore, daemon=True).start()

    def press_key(self, key: str) -> None:
        """Press a special key."""
        self._send_key(key)
