"""Single source of platform-native constraints — shared by cre:repurpose (1→1
adapt) and cre:multiplatform (1→N native generation).

Extracted from docs/rules/03-content-creation-pipeline.md "Platform Guidelines"
so there is no duplicate platform table across CRE skills (DRY).

Each platform carries a `privacy_threshold` (red-team R-cross, Rule-09 GRO row):
LinkedIn is strictest on employer/colleague names (professional audience overlaps
the character's real workplace); blog is most permissive (deep narrative, can
include clinical backing). multiplatform applies this per-variant before write.

Deterministic data + lookups only. No LLM, no I/O beyond scanning assets/.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from platform_lib.paths import ASSETS

# privacy_threshold scale: "strict" > "moderate" > "permissive".
# native_structure = the shape a NATIVE post takes on that platform (NOT a
# reformat of another platform's post) — drives multiplatform generation.
PLATFORMS: dict[str, dict] = {
    "linkedin": {
        "max_length": 3000,
        "hook": "First 2 lines visible before truncation",
        "hashtags": "3-5 max",
        "native_structure": "text-first; professional framing even for vulnerability; question close",
        "aspect_ratio": None,
        "privacy_threshold": "strict",  # employer/colleague names guarded
        "asset_dir": "linkedin",
    },
    "facebook": {
        "max_length": None,
        "hook": "Emotional hook in first line",
        "hashtags": "optional",
        "native_structure": "storytelling, can be raw; longer narrative ok",
        "aspect_ratio": None,
        "privacy_threshold": "moderate",
        "asset_dir": "facebook",
    },
    "instagram": {
        "max_length": 2200,
        "hook": "First line before 'more' fold",
        "hashtags": "15-20",
        "native_structure": "visual-first; caption supports image; line breaks",
        "aspect_ratio": "1:1 or 4:5 feed, 9:16 reels",
        "privacy_threshold": "moderate",
        "asset_dir": "instagram",
    },
    "tiktok": {
        "max_length": None,  # 60s script, measured in time not chars
        "hook": "3-second hook",
        "hashtags": "5-10",
        "native_structure": "9:16 vertical script; conversational, fast-paced; <1s grab",
        "aspect_ratio": "9:16",
        "privacy_threshold": "moderate",
        "asset_dir": "tiktok",
    },
    "youtube": {
        "max_length": None,
        "hook": "Intro hook + structured body",
        "hashtags": "in description",
        "native_structure": "chapters + timestamps; structured longform",
        "aspect_ratio": "16:9",
        "privacy_threshold": "moderate",
        "asset_dir": "youtube",
    },
    "twitter": {
        "max_length": 280,
        "hook": "Punchy, quotable opener",
        "hashtags": "2-3",
        "native_structure": "thread format for longer content; one idea per tweet",
        "aspect_ratio": None,
        "privacy_threshold": "moderate",
        "asset_dir": "twitter",
    },
    "blog": {
        "max_length": None,
        "hook": "Opening scene",
        "hashtags": None,
        "native_structure": "deep narrative; may include clinical backing",
        "aspect_ratio": None,
        "privacy_threshold": "permissive",
        "asset_dir": "blog",
    },
}

ALL_PLATFORMS: list[str] = list(PLATFORMS.keys())

# Alias map so callers can pass common variants.
_ALIASES = {
    "x": "twitter",
    "twitter/x": "twitter",
    "ig": "instagram",
    "fb": "facebook",
    "yt": "youtube",
    "li": "linkedin",
}


def normalize(platform: str) -> str:
    """Lowercase + resolve aliases to a canonical platform key."""
    p = platform.strip().lower()
    return _ALIASES.get(p, p)


def get_constraints(platform: str) -> dict:
    """Return the constraint dict for a platform. KeyError if unknown."""
    key = normalize(platform)
    if key not in PLATFORMS:
        raise KeyError(f"Unknown platform '{platform}'. Known: {', '.join(ALL_PLATFORMS)}")
    return {**PLATFORMS[key], "platform": key}


def active_platforms(assets_root: Path | None = None) -> list[str]:
    """Platforms the user actually publishes to = those with an existing
    assets/{platform}/ directory. Default for multiplatform (OQ-7d A)."""
    root = assets_root or ASSETS
    if not root.exists():
        return []
    present = {d.name for d in root.iterdir() if d.is_dir()}
    return [p for p in ALL_PLATFORMS if PLATFORMS[p]["asset_dir"] in present]


def resolve_platforms(spec: str | None, assets_root: Path | None = None) -> list[str]:
    """Map a --platforms spec to a platform list.
    None/'active' → active_platforms(); 'all' → ALL_PLATFORMS;
    comma/space list → normalized, validated."""
    if spec is None or spec.strip().lower() == "active":
        return active_platforms(assets_root)
    if spec.strip().lower() == "all":
        return list(ALL_PLATFORMS)
    raw = [p for p in spec.replace(",", " ").split() if p]
    out: list[str] = []
    for p in raw:
        key = normalize(p)
        if key not in PLATFORMS:
            raise KeyError(f"Unknown platform '{p}'. Known: {', '.join(ALL_PLATFORMS)}")
        if key not in out:
            out.append(key)
    return out
