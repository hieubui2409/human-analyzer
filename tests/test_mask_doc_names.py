"""Doc-masker mechanism — verified with a SYNTHETIC mapping (no real names ship in this test).

The real token application is verified at runtime over actual docs + the whole-pack scan, not by
a literal test here. These cases pin the MECHANISM: prose masked, code/frontmatter/contracts protected,
word-boundary respected, idempotent.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / ".claude" / "skills" / "_framework-shared" / "scripts"))

import mask_doc_names as m  # noqa: E402

# Synthetic, longest-first. "Programme-Q" and the coined "Zeta" are NOT real names.
REPL = [("Programme-Q", "Scholarship-X"), ("Zeta", "Nhân vật A")]


# (a) prose token is masked
def test_prose_masked():
    out, n = m.mask_text("Zeta viết bài hôm nay.", REPL)
    assert out == "Nhân vật A viết bài hôm nay."
    assert n == 1


# (b) fenced code blocks are NOT protected — names in CLI-usage examples / output tables must be masked
#     too (the whole-pack scanner has no carve-out). Only frontmatter (contract) is protected (test c).
def test_code_fence_is_masked():
    text = "Trước Zeta.\n```\nrun --name Zeta\n```\nSau Zeta."
    out, n = m.mask_text(text, REPL)
    assert "run --name Nhân vật A" in out    # inside fence IS masked (example prose, not a contract)
    assert "Sau Nhân vật A." in out          # outside fence masked
    assert n == 3


# (c) YAML frontmatter (incl a SKILL trigger/contract line) is protected
def test_frontmatter_protected():
    text = "---\nname: demo\ntriggers: 'Zeta'\n---\nZeta in the body."
    out, n = m.mask_text(text, REPL)
    assert "triggers: 'Zeta'" in out        # frontmatter contract line untouched
    assert "Nhân vật A in the body." in out  # body masked
    assert n == 1


# (d) idempotent — a second pass is a no-op
def test_idempotent():
    once, _ = m.mask_text("Zeta và Zeta.", REPL)
    twice, n2 = m.mask_text(once, REPL)
    assert once == twice
    assert n2 == 0


# (e) pii_extra-style token maps to its placeholder
def test_extra_token_masked():
    out, n = m.mask_text("Học bổng Programme-Q tài trợ.", REPL)
    assert out == "Học bổng Scholarship-X tài trợ."
    assert n == 1


# (f) word-boundary: a token that is a substring of a longer word is NOT masked
def test_word_boundary():
    out, n = m.mask_text("Zetaland is not Zeta.", REPL)
    assert out == "Zetaland is not Nhân vật A."
    assert n == 1
