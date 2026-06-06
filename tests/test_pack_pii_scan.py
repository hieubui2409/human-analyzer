"""Tests for scan_pack_pii.py — the fail-closed PII/secret gate over the built pack.

NAME-FREE: fixtures use SYNTHETIC tokens (character-z) and synthetic secret material — no real name
is hardcoded here. The one integration test asserts the REAL built pack scans clean (zero hits),
which is name-free by construction. Skips the integration assertion when pyyaml/roster is absent.
"""
import sys
from pathlib import Path

import pytest

_SHARED_SCRIPTS = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "_framework-shared" / "scripts"
if str(_SHARED_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SHARED_SCRIPTS))

import scan_pack_pii  # noqa: E402
import pii_tokens  # noqa: E402


class TestScanText:
    def test_flags_a_token(self):
        hits = scan_pack_pii.scan_text("f.md", "intro character-z outro", ["character-z"])
        assert len(hits) == 1 and "character-z" in hits[0][1]

    def test_clean_text_no_hits(self):
        assert scan_pack_pii.scan_text("f.md", "nothing forbidden here", ["character-z"]) == []

    def test_word_boundary_no_partial_match(self):
        # 'char' must NOT match inside 'charcoal' — word-boundary anchored.
        assert scan_pack_pii.scan_text("f.md", "charcoal grill", ["char"]) == []

    def test_secret_private_key_header(self):
        # Build the marker at runtime so this shipped test file does not itself contain the literal
        # secret pattern (the whole-pack scan has no carve-out — it would flag a literal here).
        marker = "-----BEGIN " + "PRIVATE KEY-----"
        hits = scan_pack_pii.scan_text("k.txt", f"x\n{marker}\n", [])
        assert any("secret" in r for _, r in hits)

    def test_secret_aws_access_key(self):
        aws = "AKIA" + "IOSFODNN7EXAMPLE"  # runtime-assembled so the literal key is not in source
        hits = scan_pack_pii.scan_text("c.env", f"AWS_KEY={aws} rest", [])
        assert any("AWS" in r for _, r in hits)

    def test_clean_has_no_secret_false_positive(self):
        assert scan_pack_pii.scan_text("note.md", "a normal sentence about keys and tokens", []) == []


class TestScanTokens:
    def test_scan_tokens_is_subset_of_masker_tokens(self):
        """Scanner set ⊆ masker set (scanner can never flag a form the masker doesn't know)."""
        scan = set(pii_tokens.scan_tokens())
        mask = set(pii_tokens.tokens_only())
        # Extras contribute a lower-cased variant to the scanner set; allow that one transform.
        assert scan <= (mask | {t.lower() for t in mask})


class TestRealPackIsClean:
    def test_built_pack_has_zero_pii_leaks(self):
        """The real, freshly built pack must scan clean — zero name/secret hard hits (no carve-out)."""
        if not pii_tokens.scan_tokens():
            pytest.skip("roster absent — toolkit-only pack, nothing to assert")
        hard_hits, _ck_warnings = scan_pack_pii.scan_pack(source_date_epoch=0)
        assert hard_hits == [], f"PII/secret leaks in built pack: {hard_hits[:10]}"
