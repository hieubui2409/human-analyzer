"""Pack: byte-identical reproducibility + non-removable safety filter (no secrets/PII shipped)."""
import io
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "pack"))
import safety_filter  # noqa: E402
import build_pack  # noqa: E402


def test_two_builds_byte_identical():
    a, b = io.BytesIO(), io.BytesIO()
    sha_a = build_pack.build(a, source_date_epoch=0)
    sha_b = build_pack.build(b, source_date_epoch=0)
    assert a.getvalue() == b.getvalue(), "tar.gz not byte-identical across builds"
    assert sha_a == sha_b


def test_safety_filter_drops_secrets_and_pii():
    drop = [
        ".env", "x/.env.local", "a/credentials.json", "k/server.key", "c/cert.pem",
        "docs/profiles/character-a/INDEX.md", "docs/materials/x/raw.md", "docs/graph/relational-dynamics.md",
        ".claude/telemetry/gateguard-audit.jsonl", ".claude/cache/runtime/x/cache.json",
        ".git/config", "a/__pycache__/x.pyc",
    ]
    for p in drop:
        d, rule = safety_filter.is_dropped(p)
        assert d, f"should drop {p}"


def test_safety_filter_keeps_env_example_and_toolkit():
    for keep in [".env.example", "x/.env.example", ".claude/scripts/platform_lib/paths.py",
                 ".claude/skills/psy-crossref/SKILL.md", "docs/rules/12-orc-orchestration.md"]:
        d, _ = safety_filter.is_dropped(keep)
        assert not d, f"should keep {keep}"


def test_tarball_contains_no_dropped_path():
    buf = io.BytesIO()
    build_pack.build(buf, source_date_epoch=0)
    buf.seek(0)
    with tarfile.open(fileobj=buf, mode="r:gz") as tar:
        names = tar.getnames()
    assert "MANIFEST.json" in names
    for n in names:
        if n == "MANIFEST.json":
            continue
        dropped, rule = safety_filter.is_dropped(n)
        assert not dropped, f"tarball ships a dropped path {n} ({rule})"
    # spot: real character corpus must NOT be present
    assert not any(n.startswith("docs/profiles/") for n in names)
    assert not any(n.startswith("docs/materials/") for n in names)


def test_gzip_mtime_zero():
    buf = io.BytesIO()
    build_pack.build(buf, source_date_epoch=0)
    head = buf.getvalue()[:8]
    assert head[4:8] == b"\x00\x00\x00\x00", "gzip header mtime must be 0 for reproducibility"
