"""Isolated tests for cre:multiplatform (Batch 7 C1) + shared platform_constraints.

Covers the DETERMINISTIC layer (GR#4): platform resolution, native-brief scaffolding,
per-platform privacy threshold, dry-run no-write. LLM native COPY writing + the
per-variant gates (evidence-scanner/voice-audit/privacy-guard) are validated by their
own skills. Zero shared state: tmp assets root.
"""
import importlib.util
import json
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

SK = PROJECT_ROOT / ".claude" / "skills" / "cre-multiplatform" / "scripts"


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def gen_mod():
    return _load(SK / "generate-native-variants-for-platforms.py", "c1_gen")


@pytest.fixture
def pc():
    from platform_lib import platform_constraints
    return platform_constraints


# ── platform_constraints (shared module, DRY) ─────────────────────────────────
class TestPlatformConstraints:
    def test_aliases_normalize(self, pc):
        assert pc.normalize("x") == "twitter"
        assert pc.normalize("IG") == "instagram"
        assert pc.normalize("FB") == "facebook"

    def test_linkedin_privacy_strict(self, pc):
        assert pc.get_constraints("linkedin")["privacy_threshold"] == "strict"

    def test_blog_privacy_permissive(self, pc):
        assert pc.get_constraints("blog")["privacy_threshold"] == "permissive"

    def test_unknown_platform_raises(self, pc):
        with pytest.raises(KeyError):
            pc.get_constraints("myspace")

    def test_resolve_all_returns_seven(self, pc):
        assert len(pc.resolve_platforms("all")) == 7

    def test_resolve_list_validates_and_dedupes(self, pc):
        assert pc.resolve_platforms("linkedin, linkedin, tiktok") == ["linkedin", "tiktok"]

    def test_resolve_active_scans_assets_root(self, pc, tmp_path):
        (tmp_path / "linkedin").mkdir()
        (tmp_path / "blog").mkdir()
        active = pc.resolve_platforms("active", assets_root=tmp_path)
        assert set(active) == {"linkedin", "blog"}

    def test_resolve_active_empty_when_no_dirs(self, pc, tmp_path):
        assert pc.resolve_platforms("active", assets_root=tmp_path) == []


# ── native-variant scaffolding (deterministic) ────────────────────────────────
class TestScaffold:
    def test_dry_run_writes_nothing(self, gen_mod, tmp_path):
        out = gen_mod.generate("an angle", "260526-s", "all", "", assets_root=tmp_path, dry_run=True)
        assert out["variant_count"] == 7
        assert all(not v["scaffolded"] for v in out["variants"])
        assert list(tmp_path.iterdir()) == []  # nothing written

    def test_scaffold_creates_package(self, gen_mod, tmp_path):
        out = gen_mod.generate("an angle", "260526-s", "linkedin", "test-alpha",
                               assets_root=tmp_path, dry_run=False)
        vdir = tmp_path / "linkedin" / "260526-s"
        assert (vdir / "brief.json").exists()
        assert (vdir / "post.md").exists()
        assert (vdir / "images").is_dir()

    def test_brief_carries_native_constraints(self, gen_mod, tmp_path):
        gen_mod.generate("angle", "s", "tiktok", "", assets_root=tmp_path)
        brief = json.loads((tmp_path / "tiktok" / "s" / "brief.json").read_text(encoding="utf-8"))
        assert brief["aspect_ratio"] == "9:16"
        assert brief["privacy_threshold"] == "moderate"
        assert "cre:evidence-scanner" in brief["gates_required"]

    def test_linkedin_brief_is_strict(self, gen_mod, tmp_path):
        gen_mod.generate("angle", "s", "linkedin", "", assets_root=tmp_path)
        brief = json.loads((tmp_path / "linkedin" / "s" / "brief.json").read_text(encoding="utf-8"))
        assert brief["privacy_threshold"] == "strict"

    def test_existing_post_not_overwritten(self, gen_mod, tmp_path):
        vdir = tmp_path / "blog" / "s"
        (vdir / "images").mkdir(parents=True)
        (vdir / "post.md").write_text("HUMAN WRITTEN COPY", encoding="utf-8")
        gen_mod.generate("angle", "s", "blog", "", assets_root=tmp_path)
        assert (vdir / "post.md").read_text(encoding="utf-8") == "HUMAN WRITTEN COPY"

    def test_source_path_read_into_brief(self, gen_mod, tmp_path):
        src = tmp_path / "src.md"
        src.write_text("original post body", encoding="utf-8")
        gen_mod.generate(str(src), "s", "facebook", "", assets_root=tmp_path)
        brief = json.loads((tmp_path / "facebook" / "s" / "brief.json").read_text(encoding="utf-8"))
        assert "source_text" in brief["source"]
