"""platform_lib — shared utilities for the framework skills.

Auto-imports the telemetry module so every script that imports ``platform_lib``
gets I4 script-execution metrics with no per-script boilerplate. Telemetry
no-ops under ``CK_TELEMETRY_DISABLED`` / pytest, so this import is side-effect-free
during tests. Kept in a try/except so a telemetry hiccup never breaks imports.
"""
try:  # never let telemetry wiring break a normal platform_lib import
    from . import telemetry as telemetry  # noqa: F401
except Exception:  # pragma: no cover - defensive
    pass
