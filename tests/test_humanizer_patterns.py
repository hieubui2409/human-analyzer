"""humanizer_patterns: VN+EN AI-tell taxonomy + structural heuristics, monotonic + deterministic."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / ".claude" / "scripts"))

from platform_lib import humanizer_patterns as hp

# --- fixtures ---------------------------------------------------------------------------
SLOP_VI = (
    "Trong thế giới ngày nay, không thể phủ nhận rằng công nghệ đáng chú ý là quan trọng.\n"
    "Điều này cho phép chúng ta tận dụng dữ liệu tươi một cách hiệu quả nhằm mục đích phát triển.\n"
    "Sản phẩm nhanh, mạnh mẽ và toàn diện. Nó đóng vai trò như một trợ lý đắc lực.\n"
    "Tóm lại: hy vọng bài viết này hữu ích."
)
SLOP_EN = (
    "In today's world, it's worth noting that this groundbreaking tool is pivotal.\n"
    "We leverage a rich tapestry of data in order to delve into the intricate landscape.\n"
    "It serves as a robust, seamless, and vibrant solution that boasts power.\n"
    "In conclusion, the future looks bright."
)
# Hand-clean human sample (VN): varied sentence length, no tells, no em-dashes, low hedging.
CLEAN_VI = (
    "Sáng nay tôi dậy muộn. Cà phê nguội ngắt trên bàn, đắng và buồn.\n"
    "Tôi viết xong ba trang rồi xé đi hai. Còn lại một đoạn, đọc thấy ổn.\n"
    "Chiều mưa. Tôi ra ban công đứng nhìn, không nghĩ gì cả."
)


def _cats(findings):
    return {f["category"] for f in findings}


# (a)(b) phrase tells fire on slop fixtures
def test_flags_vietnamese_filler_and_openers():
    f = hp.scan(SLOP_VI, lang="vi", strictness="balanced")
    cats = _cats(f)
    assert "filler_phrase" in cats
    assert "formulaic_opener" in cats
    assert "formulaic_closer" in cats


def test_flags_english_filler_and_vocab():
    f = hp.scan(SLOP_EN, lang="en", strictness="balanced")
    matches = " ".join(x["match"].lower() for x in f)
    assert "filler_phrase" in _cats(f)
    assert "delve" in matches or "leverage" in matches or "tapestry" in matches


# (c) structural heuristics each fire on a crafted sample
def test_rule_of_three_fires():
    text = "Nhanh, gọn và rẻ. Đẹp, bền, và tốt. Vui, khỏe và an. Sạch, xanh và mát."
    f = hp.scan(text, lang="vi", strictness="balanced")
    assert "rule_of_three" in _cats(f)


def test_em_dash_overuse_fires():
    text = "A — b — c — d — e — f are here."
    f = hp.scan(text, strictness="balanced")
    assert "em_dash_overuse" in _cats(f)


def test_hedging_density_fires():
    text = "It might perhaps possibly maybe arguably could seem to appear somewhat relatively true."
    f = hp.scan(text, lang="en", strictness="balanced")
    assert "hedging_density" in _cats(f)


def test_low_burstiness_high_tier_only():
    # six sentences of identical length → cv ~ 0 → fires at high, NOT at balanced.
    uniform = " ".join(["aa bb cc dd ee."] * 6)
    assert "low_burstiness" in _cats(hp.scan(uniform, strictness="high"))
    assert "low_burstiness" not in _cats(hp.scan(uniform, strictness="balanced"))
    assert "low_burstiness" not in _cats(hp.scan(uniform, strictness="conservative"))


# (d) hand-clean human sample → 0 findings at balanced
def test_clean_sample_zero_findings_at_balanced():
    assert hp.scan(CLEAN_VI, lang="vi", strictness="balanced") == []


# (e) monotonic: conservative ⊆ balanced ⊆ high
def _keyset(findings):
    return {(f["category"], f["span"]) for f in findings}


@pytest.mark.parametrize("text", [SLOP_VI, SLOP_EN])
def test_strictness_monotonic(text):
    c = _keyset(hp.scan(text, strictness="conservative"))
    b = _keyset(hp.scan(text, strictness="balanced"))
    h = _keyset(hp.scan(text, strictness="high"))
    assert c <= b <= h


# (f) determinism: same input → byte-identical output
def test_determinism_repeated_runs():
    a = hp.scan(SLOP_VI)
    b = hp.scan(SLOP_VI)
    assert a == b
    # sorted by (span_start, category)
    keys = [(f["span"][0], f["category"]) for f in a]
    assert keys == sorted(keys)


# (g) span offsets valid (real slices of the text)
@pytest.mark.parametrize("text", [SLOP_VI, SLOP_EN])
def test_span_offsets_valid(text):
    for f in hp.scan(text, strictness="high"):
        s, e = f["span"]
        assert 0 <= s <= e <= len(text)
        if f["match"]:
            assert text[s:e] == f["match"]


def test_bad_strictness_falls_back_to_balanced():
    assert hp.scan(SLOP_VI, strictness="bogus") == hp.scan(SLOP_VI, strictness="balanced")
