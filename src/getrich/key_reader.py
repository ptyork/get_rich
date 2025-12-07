from __future__ import annotations

from typing import Protocol, runtime_checkable
import os
import sys

IS_WINDOWS = sys.platform == "win32"

if IS_WINDOWS:
    import msvcrt
else:  # POSIX
    import termios
    import tty


@runtime_checkable
class KeyReader(Protocol):
    """Protocol for objects that yield individual key events."""

    def __enter__(self) -> "KeyReader": ...

    def __exit__(self, exc_type, exc, tb) -> bool: ...

    def read_key(self) -> str: ...


class _WindowsKeyReader:
    """Windows console keyboard reader using msvcrt."""

    KEY_MAP = {
        "H": "UP_ARROW",
        "P": "DOWN_ARROW",
        "M": "RIGHT_ARROW",
        "K": "LEFT_ARROW",
        "G": "HOME",
        "O": "END",
        "I": "PAGE_UP",
        "Q": "PAGE_DOWN",
        "S": "DELETE",
        "R": "INSERT",
    }

    def __enter__(self) -> "_WindowsKeyReader":
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        return False

    def read_key(self) -> str:
        ch = msvcrt.getwch()
        if ch in ("\r", "\n"):
            return "ENTER"
        if ch == "\x1b":
            return "ESC"
        if ch in ("\x08", "\x7f"):
            return "BACKSPACE"
        if ch == "\x03":
            return "CTRL_C"
        if ch == " ":
            return "SPACE"
        if ch in ("\x00", "\xe0"):
            code = msvcrt.getwch()
            return self.KEY_MAP.get(code, "")
        return ch


class _PosixKeyReader:
    """POSIX terminal keyboard reader using termios/tty."""

    _ESC_MAP = {
        b"[A": "UP_ARROW",
        b"[B": "DOWN_ARROW",
        b"[C": "RIGHT_ARROW",
        b"[D": "LEFT_ARROW",
        b"[H": "HOME",
        b"[F": "END",
        b"[1~": "HOME",
        b"[4~": "END",
        b"[5~": "PAGE_UP",
        b"[6~": "PAGE_DOWN",
        b"[3~": "DELETE",
        b"[2~": "INSERT",
        b"[11~": "F1",
        b"[12~": "F2",
        b"[13~": "F3",
        b"[14~": "F4",
        b"[15~": "F5",
        b"[17~": "F6",
        b"[18~": "F7",
        b"[19~": "F8",
        b"[20~": "F9",
        b"[21~": "F10",
        b"[23~": "F11",
        b"[24~": "F12",
        b"OP": "F1",
        b"OQ": "F2",
        b"OR": "F3",
        b"OS": "F4",
        b"OH": "HOME",
        b"OF": "END",
    }

    def __init__(self, esc_timeout: float = 0.01):
        self.esc_timeout = esc_timeout
        self.fd = sys.stdin.fileno()
        self._old_settings = None

    def __enter__(self) -> "_PosixKeyReader":
        self._old_settings = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        if self._old_settings is not None:
            termios.tcsetattr(self.fd, termios.TCSADRAIN, self._old_settings)
        return False

    def read_key(self) -> str:
        import select

        ch = os.read(self.fd, 1)
        if not ch:
            return ""

        key = ch.decode("utf-8", errors="ignore")

        if key == "\x1b":
            rlist, _, _ = select.select([self.fd], [], [], self.esc_timeout)
            if rlist:
                seq = bytearray(os.read(self.fd, 1))
                while select.select([self.fd], [], [], self.esc_timeout)[0]:
                    seq.extend(os.read(self.fd, 1))

                seq_bytes = bytes(seq)
                mapped = self._ESC_MAP.get(seq_bytes)
                if mapped:
                    return mapped
            return "ESC"

        if key == "\x7f":
            return "BACKSPACE"
        if key == "\x08":
            return "DELETE"
        if key in ("\r", "\n"):
            return "ENTER"
        if key == "\x03":
            return "CTRL_C"
        if key == " ":
            return "SPACE"
        return key


def get_key_reader(esc_timeout: float = 0.01) -> KeyReader:
    """Return a platform-appropriate key reader."""
    if IS_WINDOWS:
        return _WindowsKeyReader()
    return _PosixKeyReader(esc_timeout=esc_timeout)
