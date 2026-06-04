#!/usr/bin/env python3
"""Cross-platform console encoding for framework scripts.

The framework writes UTF-8 (Vietnamese diacritics throughout profiles/materials). On Windows the
default console codepage is cp1252, which raises UnicodeEncodeError when a script prints diacritics.
This reconfigures stdout/stderr to UTF-8 on Windows only — a no-op everywhere else.

Scope note: file reads/writes already pass `encoding="utf-8"` inline across the codebase (the uniform
convention); this module deliberately does NOT wrap them — it owns only the console-stream fix, which
cannot be expressed inline at every print site.
"""

import sys


def configure_utf8_console() -> None:
    """Reconfigure stdout/stderr to UTF-8 on Windows (cp1252 → utf-8). No-op on POSIX."""
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace")
            sys.stderr.reconfigure(encoding="utf-8", errors="replace")
        except AttributeError:
            pass  # Python < 3.7 has no reconfigure; nothing safe to do.
