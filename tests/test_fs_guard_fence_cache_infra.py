"""Deterministic-infra tests: fs_guard write-jail, check_fence advisory scan, cache_store + cache_root.

Covers the Rule-12-derived write fence (traversal/symlink/prefix-lookalike defeat), the advisory fence
scan, and the shared content-addressed cache primitive (version miss, atomic write, prune, dirty-tree key).
"""
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude" / "scripts"))

from platform_lib import fs_guard, cache_store, paths  # noqa: E402
from platform_lib import encoding_utils  # noqa: E402


# ---------- fs_guard ----------

def test_fsguard_accepts_in_root_per_framework():
    assert fs_guard.assert_under(paths.MATERIALS / "x" / "a.md", "MAT")
    assert fs_guard.assert_under(paths.PROFILES / "c" / "INDEX.md", "PSY")
    assert fs_guard.assert_under(paths.GRAPH / "g.md", "PSY")          # PSY owns docs/graph (Rule 12 extended)
    assert fs_guard.assert_under(paths.ASSETS / "facebook" / "p.txt", "CRE")


def test_fsguard_rejects_cross_framework_write():
    with pytest.raises(fs_guard.FenceError):
        fs_guard.assert_under(paths.ASSETS / "x.txt", "MAT")           # MAT cannot write assets/
    with pytest.raises(fs_guard.FenceError):
        fs_guard.assert_under(paths.MATERIALS / "x.md", "CRE")          # CRE cannot write materials/


def test_fsguard_defeats_traversal_and_prefix_lookalike():
    with pytest.raises(fs_guard.FenceError):
        fs_guard.assert_under(paths.PROFILES / ".." / ".." / "etc" / "passwd", "PSY")
    # prefix look-alike: docs/profiles-x is NOT under docs/profiles
    lookalike = paths.PROFILES.parent / (paths.PROFILES.name + "-x") / "f.md"
    with pytest.raises(fs_guard.FenceError):
        fs_guard.assert_under(lookalike, "PSY")


def test_fsguard_defeats_symlink_escape(tmp_path, monkeypatch):
    # A symlink inside the fence pointing outside must not let a write escape.
    if not paths.PROFILES.exists():
        pytest.skip("docs/profiles absent — toolkit-only pack")
    target_outside = tmp_path / "outside"
    target_outside.mkdir()
    link = paths.PROFILES / "_tmp_escape_link_test"
    if link.is_symlink() or link.exists():
        link.unlink()
    try:
        os.symlink(target_outside, link)
        with pytest.raises(fs_guard.FenceError):
            fs_guard.assert_under(link / "x.md", "PSY")
    finally:
        if link.is_symlink():
            link.unlink()


def test_fsguard_unknown_framework_raises():
    with pytest.raises(fs_guard.FenceError):
        fs_guard.assert_under(paths.PROFILES / "x.md", "ZZZ")


# ---------- cache_store ----------

def test_content_hash_deterministic_and_reflects_body():
    assert cache_store.content_hash("abc") == cache_store.content_hash("abc")
    assert cache_store.content_hash("abc") != cache_store.content_hash("abd")  # dirty edit → new key


def test_cache_store_put_get_and_persist(tmp_path, monkeypatch):
    monkeypatch.setenv("CK_CACHE_DIR", str(tmp_path / "cache"))
    import importlib
    importlib.reload(paths)
    importlib.reload(cache_store)
    s = cache_store.CacheStore("t", committed=True)
    s.put("k1", {"verdict": "consistent", "score": 3})
    s2 = cache_store.CacheStore("t", committed=True)   # fresh load from disk
    assert s2.get("k1") == {"verdict": "consistent", "score": 3}
    assert s2.get("missing") is None


def test_cache_store_version_mismatch_is_full_miss(tmp_path, monkeypatch):
    monkeypatch.setenv("CK_CACHE_DIR", str(tmp_path / "cache"))
    import importlib
    importlib.reload(paths)
    importlib.reload(cache_store)
    cache_store.CacheStore("v", committed=True, cache_version="1").put("k", 1)
    bumped = cache_store.CacheStore("v", committed=True, cache_version="2")  # version bump
    assert bumped.get("k") is None                                          # full miss (safe)


def test_cache_store_prune_gc(tmp_path, monkeypatch):
    monkeypatch.setenv("CK_CACHE_DIR", str(tmp_path / "cache"))
    import importlib
    importlib.reload(paths)
    importlib.reload(cache_store)
    s = cache_store.CacheStore("p", committed=True)
    s.put_many({"a": 1, "b": 2, "c": 3})
    removed = s.prune(live_keys={"a", "c"})
    assert removed == 1 and s.get("b") is None and s.get("a") == 1


def test_cache_root_split_committed_vs_runtime(tmp_path, monkeypatch):
    monkeypatch.setenv("CK_CACHE_DIR", str(tmp_path / "cache"))
    import importlib
    importlib.reload(paths)
    c = paths.committed_cache_dir("x")
    r = paths.runtime_cache_dir("x")
    assert "committed" in str(c) and "runtime" in str(r) and c != r


def test_encoding_configure_is_noop_on_posix():
    # must not raise and returns nothing (a pure side-effecting console-encoding setup)
    assert encoding_utils.configure_utf8_console() is None


@pytest.fixture(autouse=True)
def _restore_paths():
    yield
    import importlib
    monkey = os.environ.pop("CK_CACHE_DIR", None)
    importlib.reload(paths)
    importlib.reload(cache_store)
