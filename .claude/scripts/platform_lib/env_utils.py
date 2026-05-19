"""Environment variable loading and API key resolution for framework scripts."""
import os
from pathlib import Path


def load_env(project_root: Path | str | None = None) -> dict[str, str]:
    """Load .env file from project root into os.environ, return loaded pairs."""
    if project_root is None:
        from platform_lib.paths import ROOT
        project_root = ROOT
    env_path = Path(project_root) / ".env"
    loaded: dict[str, str] = {}
    if not env_path.exists():
        return loaded
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if "=" not in line:
                continue
            key, _, value = line.partition("=")
            key = key.strip()
            value = value.strip().strip("\"'")
            if key:
                os.environ.setdefault(key, value)
                loaded[key] = value
    return loaded


def get_api_key(service_name: str) -> str | None:
    """Resolve API key for a service via env var naming conventions.

    Checks in order: {SERVICE}_API_KEY, {SERVICE}_KEY, {SERVICE}_TOKEN.
    Falls back to loading .env if not found in current environment.
    """
    name_upper = service_name.upper().replace("-", "_").replace(" ", "_")
    candidates = [
        f"{name_upper}_API_KEY",
        f"{name_upper}_KEY",
        f"{name_upper}_TOKEN",
    ]
    for candidate in candidates:
        val = os.environ.get(candidate)
        if val:
            return val
    load_env()
    for candidate in candidates:
        val = os.environ.get(candidate)
        if val:
            return val
    return None
