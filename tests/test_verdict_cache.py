"""verdict_cache: content-hash keying, NEVER_CACHED safety, label-only PII guard, --fresh, pair/dep."""
import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude" / "scripts"))
from platform_lib import verdict_cache_keys as vck, paths  # noqa: E402


@pytest.fixture
def vc(tmp_path, monkeypatch):
    monkeypatch.setenv("CK_CACHE_DIR", str(tmp_path / "cache"))
    import importlib
    importlib.reload(paths)
    import platform_lib.cache_store as cs
    importlib.reload(cs)
    import platform_lib.verdict_cache as vc_mod
    importlib.reload(vc_mod)
    return vc_mod.VerdictCache()


def test_key_deterministic_and_content_sensitive():
    b1 = {"n1": "body text"}
    k1 = vck.compute_key("dim", ["n1"], b1, "vi")
    assert k1 == vck.compute_key("dim", ["n1"], b1, "vi")          # deterministic
    assert k1 != vck.compute_key("dim", ["n1"], {"n1": "edited"}, "vi")  # dirty edit → new key
    assert k1 != vck.compute_key("dim", ["n1"], b1, "en")          # lang flips key


def test_never_cached_refused():
    for chk in ("crisis_assess", "narrative_twist", "contradiction"):
        with pytest.raises(ValueError):
            vck.compute_key(chk, ["n1"], {"n1": "x"})


def test_pair_check_unordered():
    b = {"a": "x", "b": "y"}
    assert vck.compute_key("relationship_consistency", ["a", "b"], b) == \
           vck.compute_key("relationship_consistency", ["b", "a"], b)  # (A,B)==(B,A)


def test_dep_text_invalidates():
    b = {"n": "same"}
    assert vck.compute_key("dim", ["n"], b, dep_text="parent-v1") != \
           vck.compute_key("dim", ["n"], b, dep_text="parent-v2")


def test_lookup_miss_then_hit(vc):
    b = {"n1": "profile section body"}
    assert vc.lookup("dim", ["n1"], b) is None                      # cold miss
    vc.record("dim", ["n1"], b, {"label": "consistent", "score": 3})
    hit = vc.lookup("dim", ["n1"], b)
    assert hit == {"label": "consistent", "score": 3}               # warm hit


def test_fresh_forces_miss(vc):
    b = {"n1": "x"}
    vc.record("dim", ["n1"], b, {"label": "ok"})
    assert vc.lookup("dim", ["n1"], b) is not None
    assert vc.lookup("dim", ["n1"], b, fresh=True) is None          # --fresh bypass


def test_edit_invalidates_hit(vc):
    vc.record("dim", ["n1"], {"n1": "v1"}, {"label": "ok"})
    assert vc.lookup("dim", ["n1"], {"n1": "v2"}) is None           # body changed → miss


def test_never_cached_record_refused(vc):
    assert vc.record("crisis_assess", ["n1"], {"n1": "x"}, {"label": "high"}) is False


def test_pii_guard_rejects_raw_text(vc):
    b = {"n1": "x"}
    with pytest.raises(ValueError):                                 # disallowed key (raw excerpt)
        vc.record("dim", ["n1"], b, {"excerpt": "trauma: father left at birth..."})
    with pytest.raises(ValueError):                                 # non-scalar
        vc.record("dim", ["n1"], b, {"label": ["a", "b"]})
    with pytest.raises(ValueError):                                 # oversize (excerpt smuggling)
        vc.record("dim", ["n1"], b, {"note": "x" * 600})


def test_prune_gc(vc):
    vc.record("dim", ["alive"], {"alive": "a"}, {"label": "ok"})
    vc.record("dim", ["dead"], {"dead": "d"}, {"label": "ok"})
    removed = vc.prune_to(live_node_ids={"alive"})
    assert removed == 1 and vc.lookup("dim", ["dead"], {"dead": "d"}) is None
