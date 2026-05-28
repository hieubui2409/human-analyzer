"""Isolated tests for cre:evidence-scanner (Batch 6 B8).

Covers the DETERMINISTIC-GATHER layer only (GR#4): claim segmentation, tier
mapping, Rule-09 leak detection, verdict policy, exit semantics. LLM-adjudication
(does material actually support claim?) is validated separately (real-LLM pass).

Zero shared state: tmp asset dirs + tmp materials; module MATERIALS monkeypatched.
"""
import importlib.util
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

SK = PROJECT_ROOT / ".claude" / "skills" / "cre-evidence-scanner" / "scripts"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def extract_mod():
    return _load(SK / "extract-claims-from-draft.py", "ec_extract")


@pytest.fixture
def map_mod():
    return _load(SK / "map-claims-to-evidence-tiers.py", "ec_map")


# ---------- claim extraction (VN-aware) ----------

class TestExtractClaims:
    def test_sentence_segmentation(self, extract_mod):
        text = "Tôi sợ thất bại. Nhưng tôi vẫn cố gắng mỗi ngày."
        claims = extract_mod.extract_claims(text)
        assert len(claims) >= 2
        assert all("claim" in c and "line" in c and "span" in c for c in claims)

    def test_clause_split_on_connective(self, extract_mod):
        text = "Tôi học giỏi và tôi cũng chơi thể thao tốt lắm."
        claims = extract_mod.extract_claims(text)
        # "và" splits into two clause-claims
        assert len(claims) == 2

    def test_drops_hashtag_and_short(self, extract_mod):
        text = "#hashtag #another\nOK.\nĐây là một câu đủ dài để giữ lại."
        claims = extract_mod.extract_claims(text)
        texts = [c["claim"] for c in claims]
        assert not any(t.startswith("#") for t in texts)
        assert any("đủ dài" in t for t in texts)

    def test_diacritics_preserved(self, extract_mod):
        text = "Nỗi sợ bị bỏ rơi luôn hiện diện trong tâm trí."
        claims = extract_mod.extract_claims(text)
        assert "ỗ" in claims[0]["claim"]  # ố/ỗ preserved, not ASCII-folded


# ---------- Rule-09 leak detection ----------

class TestLeakDetection:
    def test_privacy_tag_is_leak(self, map_mod):
        assert map_mod.detect_leaks("Chuyện này [CONFIDENTIAL: Nhân vật B] không nên kể.")

    def test_private_tag_is_leak(self, map_mod):
        assert map_mod.detect_leaks("[PRIVATE] nội dung riêng tư")

    def test_clean_claim_no_leak(self, map_mod):
        assert map_mod.detect_leaks("Một câu hoàn toàn bình thường.") == []


# ---------- verdict policy (shared evidence_tier_permissions) ----------

class TestVerdictPolicy:
    def test_tier_verdicts(self):
        from platform_lib.evidence_tier_permissions import verdict_for_tier
        assert verdict_for_tier(1) == "PASS"
        assert verdict_for_tier(2) == "PASS"
        assert verdict_for_tier(3) == "WARN"
        assert verdict_for_tier(4) == "FAIL"
        assert verdict_for_tier(5) == "FAIL"

    def test_strict_fails_t3(self):
        from platform_lib.evidence_tier_permissions import verdict_for_tier
        assert verdict_for_tier(3, strict=True) == "FAIL"

    def test_unknown_tier_fail_closed(self):
        from platform_lib.evidence_tier_permissions import verdict_for_tier
        assert verdict_for_tier(99) == "FAIL"

    def test_worst_verdict(self):
        from platform_lib.evidence_tier_permissions import worst_verdict
        assert worst_verdict(["PASS", "WARN", "FAIL"]) == "FAIL"
        assert worst_verdict(["PASS", "WARN"]) == "WARN"
        assert worst_verdict([]) == "WARN"


# ---------- adjudication (deterministic preliminary verdict) ----------

class TestAdjudicate:
    def _claim(self, text):
        return {"claim": text, "line": 1, "span": [0, len(text)]}

    def test_leak_claim_fails(self, map_mod):
        r = map_mod.adjudicate_claim(self._claim("[CONFIDENTIAL: Nhân vật B] bí mật"), [], strict=False)
        assert r["verdict"] == "FAIL" and r["reason"] == "rule09_leak"

    def test_no_evidence_warns_never_pass(self, map_mod):
        r = map_mod.adjudicate_claim(self._claim("Câu không có nguồn nào cả."), [], strict=False)
        assert r["verdict"] == "WARN" and r["reason"] == "no_evidence_detected"

    def test_t1_material_passes(self, map_mod):
        mats = [{"file": "m.md", "tier": 1, "confidentiality": "public",
                 "_kw": {"thất", "bại", "vượt"}}]
        r = map_mod.adjudicate_claim(self._claim("Hành trình vượt qua thất bại lớn."), mats, strict=False)
        assert r["verdict"] == "PASS" and r["evidence_tier"] == "T1"

    def test_t5_material_fails(self, map_mod):
        mats = [{"file": "m.md", "tier": 5, "confidentiality": "public",
                 "_kw": {"tin", "đồn", "nghe"}}]
        r = map_mod.adjudicate_claim(self._claim("Theo tin đồn nghe được hôm qua."), mats, strict=False)
        assert r["verdict"] == "FAIL"

    def test_private_material_downgrades_pass_to_warn(self, map_mod):
        mats = [{"file": "m.md", "tier": 1, "confidentiality": "private",
                 "_kw": {"chuyện", "riêng", "gia"}}]
        r = map_mod.adjudicate_claim(self._claim("Chuyện riêng của gia đình anh ấy."), mats, strict=False)
        assert r["verdict"] == "WARN" and r["reason"] == "confidential_material"


# ---------- end-to-end scan + exit semantics ----------

class TestScanEndToEnd:
    def _mk_material(self, mdir, name, category, conf="public", title="thất bại vượt qua"):
        mdir.mkdir(parents=True, exist_ok=True)
        (mdir / name).write_text(
            f"---\nmaterial_id: x\nsource_category: {category}\n"
            f"confidentiality: {conf}\ntitle: {title}\n---\nbody\n", encoding="utf-8")

    def test_clean_draft_exit0(self, map_mod, tmp_path, monkeypatch):
        mats = tmp_path / "materials" / "test-alpha"
        self._mk_material(mats, "primary.md", "primary")
        monkeypatch.setattr(map_mod, "MATERIALS", tmp_path / "materials")
        monkeypatch.setattr(map_mod, "ALL_CHARS", ["test-alpha"])
        monkeypatch.setattr(map_mod, "CHAR_DISPLAY", {"test-alpha": "Alpha"})
        monkeypatch.setattr(map_mod, "resolve_character", lambda n: n)
        asset = tmp_path / "asset"
        asset.mkdir()
        (asset / "post.txt").write_text("Hành trình vượt qua thất bại to lớn.", encoding="utf-8")
        res = map_mod.scan(asset, "test-alpha", strict=False)
        assert res["overall_verdict"] in ("PASS", "WARN")  # no FAIL → exit 0

    def test_leak_draft_fails(self, map_mod, tmp_path, monkeypatch):
        monkeypatch.setattr(map_mod, "MATERIALS", tmp_path / "materials")
        monkeypatch.setattr(map_mod, "ALL_CHARS", ["test-alpha"])
        monkeypatch.setattr(map_mod, "CHAR_DISPLAY", {"test-alpha": "Alpha"})
        monkeypatch.setattr(map_mod, "resolve_character", lambda n: n)
        asset = tmp_path / "asset"
        asset.mkdir()
        (asset / "post.txt").write_text("Bí mật [CONFIDENTIAL: Beta] bị lộ ra ngoài.", encoding="utf-8")
        res = map_mod.scan(asset, "test-alpha", strict=False)
        assert res["overall_verdict"] == "FAIL"

    def test_missing_draft_errors(self, map_mod, tmp_path):
        res = map_mod.scan(tmp_path / "nonexistent", None, strict=False)
        assert "error" in res
