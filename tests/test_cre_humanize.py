"""cre:humanize scan script — exit codes, --json shape, corpus rewrite-refusal, default path."""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / ".claude" / "skills" / "cre-humanize" / "scripts" / "scan-content-for-ai-tells.py"
VENV = ROOT / ".claude" / "skills" / ".venv" / "bin" / "python3"
PY = str(VENV) if VENV.exists() else sys.executable
ENV = {**__import__("os").environ, "PYTHONPATH": str(ROOT / ".claude" / "scripts")}

SLOP_VI = (
    "Trong thế giới ngày nay, không thể phủ nhận rằng công nghệ đáng chú ý là quan trọng.\n"
    "Điều này cho phép chúng ta tận dụng dữ liệu tươi một cách hiệu quả nhằm mục đích phát triển.\n"
    "Tóm lại: hy vọng bài viết này hữu ích."
)
CLEAN_VI = (
    "Sáng nay tôi dậy muộn. Cà phê nguội ngắt trên bàn, đắng và buồn.\n"
    "Tôi viết xong ba trang rồi xé đi hai. Còn lại một đoạn, đọc thấy ổn."
)


def _run(args):
    return subprocess.run([PY, str(SCRIPT)] + args, capture_output=True, text=True, env=ENV, timeout=60)


def test_exit_1_on_slop(tmp_path):
    f = tmp_path / "post.txt"
    f.write_text(SLOP_VI, encoding="utf-8")
    r = _run(["--path", str(f)])
    assert r.returncode == 1, r.stderr


def test_exit_0_on_clean(tmp_path):
    f = tmp_path / "post.txt"
    f.write_text(CLEAN_VI, encoding="utf-8")
    r = _run(["--path", str(f), "--strictness", "balanced"])
    assert r.returncode == 0, r.stdout + r.stderr


def test_json_shape(tmp_path):
    f = tmp_path / "post.txt"
    f.write_text(SLOP_VI, encoding="utf-8")
    r = _run(["--path", str(f), "--json"])
    data = json.loads(r.stdout)
    assert {"path", "strictness", "file_count", "finding_count", "files"} <= set(data)
    assert data["finding_count"] >= 1
    fnd = data["files"][0]["findings"][0]
    assert {"category", "pattern", "span", "severity", "suggestion"} <= set(fnd)


def test_corpus_rewrite_refused():
    # docs/profiles/ is the Rule-09 corpus → --rewrite must be refused (exit 2) with the corpus reason.
    corpus = ROOT / "docs" / "profiles" / "any-character"
    r = _run(["--path", str(corpus), "--rewrite", "--json"])
    assert r.returncode == 2, r.stdout + r.stderr
    data = json.loads(r.stdout)
    assert data["refused"] is True and data["reason"] == "rule09_corpus_no_rewrite"


def test_non_assets_rewrite_refused(tmp_path):
    # rewrite is an assets/-only allowlist → a non-assets, non-corpus path is also refused (exit 2).
    f = tmp_path / "post.txt"
    f.write_text(SLOP_VI, encoding="utf-8")
    r = _run(["--path", str(f), "--rewrite", "--json"])
    assert r.returncode == 2, r.stdout + r.stderr
    assert json.loads(r.stdout)["reason"] == "rewrite_assets_only"


def _load_mod(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / ".claude" / "scripts"))
    spec.loader.exec_module(mod)
    return mod


def test_rewrite_allowlist_is_assets_only():
    mod = _load_mod("scan_ai_tells_allow")
    from platform_lib.paths import ASSETS, PROFILES
    assert mod.rewrite_allowed(ASSETS / "facebook" / "x") is True
    assert mod.rewrite_allowed(PROFILES / "any" / "INDEX.md") is False  # corpus
    assert mod.rewrite_allowed(ROOT / "plans" / "x.txt") is False        # outside assets/


def test_default_path_is_assets():
    mod = _load_mod("scan_ai_tells_default")
    from platform_lib.paths import ASSETS
    assert str(ASSETS).endswith("assets")
    assert mod.is_corpus_path(ASSETS) is False


def test_strictness_from_preference(tmp_path, monkeypatch):
    spec = importlib.util.spec_from_file_location("scan_ai_tells2", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(ROOT / ".claude" / "scripts"))
    spec.loader.exec_module(mod)
    # explicit wins over preference
    assert mod.resolve_strictness("high") == "high"
    # falls back to a valid enum value when not explicit
    assert mod.resolve_strictness(None) in {"high", "balanced", "conservative"}
