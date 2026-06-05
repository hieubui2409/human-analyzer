"""preferences: closed-enum guard, load→merge→save preserves keys, defaults on missing/bad."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude" / "scripts"))


@pytest.fixture
def prefs(tmp_path, monkeypatch):
    monkeypatch.setenv("CK_CACHE_DIR", str(tmp_path / "cache"))
    import importlib
    import platform_lib.paths as paths
    importlib.reload(paths)
    import platform_lib.preferences as pref
    importlib.reload(pref)
    return pref


def test_defaults_when_missing(prefs):
    assert prefs.load() == {
        "crossref_rigor": "standard",
        "cre_action_prompting": "standard",
        "humanize_strictness": "balanced",
    }


def test_humanize_strictness_default_is_balanced(prefs):
    assert prefs.load()["humanize_strictness"] == "balanced"


def test_humanize_strictness_valid_set_persists(prefs):
    prefs.set_key("humanize_strictness=high")
    assert prefs.load()["humanize_strictness"] == "high"


def test_humanize_strictness_invalid_writes_nothing(prefs):
    with pytest.raises(ValueError):
        prefs.set_key("humanize_strictness=ultra")
    assert prefs.load()["humanize_strictness"] == "balanced"  # default, no write


def test_humanize_strictness_merge_preserves_other_knobs(prefs):
    prefs.set_key("crossref_rigor=deep")
    prefs.set_key("humanize_strictness=conservative")
    got = prefs.load()
    assert got["crossref_rigor"] == "deep" and got["humanize_strictness"] == "conservative"


def test_set_and_load(prefs):
    prefs.set_key("crossref_rigor=deep")
    assert prefs.load()["crossref_rigor"] == "deep"


def test_set_preserves_other_keys(prefs):
    prefs.set_key("crossref_rigor=deep")
    prefs.set_key("cre_action_prompting=proactive")
    got = prefs.load()
    assert got["crossref_rigor"] == "deep" and got["cre_action_prompting"] == "proactive"


def test_unknown_key_raises_writes_nothing(prefs):
    with pytest.raises(ValueError):
        prefs.set_key("bogus=deep")
    assert not prefs._store_path().exists()  # nothing written


def test_out_of_enum_raises_writes_nothing(prefs):
    with pytest.raises(ValueError):
        prefs.set_key("crossref_rigor=ultra")
    assert prefs.load()["crossref_rigor"] == "standard"  # default, no write


def test_first_equals_only(prefs):
    # value may itself contain '=' (split on first only)
    with pytest.raises(ValueError):  # 'a=b' is not a valid enum value for crossref_rigor
        prefs.set_key("crossref_rigor=a=b")


def test_bad_enum_does_not_clobber_committed(prefs):
    prefs.set_key("crossref_rigor=light")
    with pytest.raises(ValueError):
        prefs.set_key("cre_action_prompting=nope")
    assert prefs.load()["crossref_rigor"] == "light"  # earlier good write survived
