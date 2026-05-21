"""Validate project structure after profile standardization (Phases 1-7).

Tests cover:
- Profile directory structure (25 base + cross-relationship files)
- Cross-relationship file integrity (frontmatter, mirror pairs)
- paths.py constants and functions accuracy
- No orphan relationship files
- family.md split integrity (content preserved, not duplicated)
"""
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROFILES = PROJECT_ROOT / "docs" / "profiles"
SCRIPTS_DIR = PROJECT_ROOT / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

ALL_CHARS = ["character-a", "character-b", "character-c"]

EXPECTED_CROSS_RELS = {
    "character-a": ["character-b.md", "character-c.md", "network.md"],
    "character-b": ["character-a.md", "character-c.md"],
    "character-c": ["character-a.md", "character-b.md"],
}

MIRROR_PAIRS = [
    ("character-a", "character-b"),
    ("character-a", "character-c"),
    ("character-b", "character-c"),
]


class TestProfileDirectoryStructure:
    """Every character must have the 25 base profile files."""

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_25_base_files_exist(self, char):
        from platform_lib.paths import PROFILE_FILES
        cdir = PROFILES / char
        missing = [f for f in PROFILE_FILES if not (cdir / f).exists()]
        assert missing == [], f"{char} missing: {missing}"

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_relationships_dir_exists(self, char):
        assert (PROFILES / char / "relationships").is_dir()

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_family_md_still_exists(self, char):
        """family.md must still exist after split (blood family content stays)."""
        assert (PROFILES / char / "relationships" / "family.md").exists()


class TestCrossRelationshipFiles:
    """Cross-relationship files created during family.md split."""

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_expected_cross_rel_files_exist(self, char):
        expected = EXPECTED_CROSS_RELS[char]
        rel_dir = PROFILES / char / "relationships"
        for fname in expected:
            assert (rel_dir / fname).exists(), f"{char}/relationships/{fname} missing"

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_cross_rel_files_have_frontmatter(self, char):
        """Every cross-relationship file must have YAML frontmatter with 'relationship:' key."""
        for fname in EXPECTED_CROSS_RELS[char]:
            fpath = PROFILES / char / "relationships" / fname
            content = fpath.read_text(encoding="utf-8")
            assert content.startswith("---"), f"{char}/{fname} missing frontmatter"
            head = content[:500]
            assert "relationship:" in head, f"{char}/{fname} missing relationship: key"

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_cross_rel_files_have_character_key(self, char):
        """Frontmatter must include character(s): key matching the profile owner."""
        for fname in EXPECTED_CROSS_RELS[char]:
            fpath = PROFILES / char / "relationships" / fname
            head = fpath.read_text(encoding="utf-8")[:500]
            has_char = f"character: {char}" in head or f"characters:" in head
            assert has_char, f"{char}/{fname} wrong character key"

    @pytest.mark.parametrize("char1,char2", MIRROR_PAIRS)
    def test_mirror_pairs_both_exist(self, char1, char2):
        """If char1 has relationships/{char2}.md, char2 must have relationships/{char1}.md."""
        f1 = PROFILES / char1 / "relationships" / f"{char2}.md"
        f2 = PROFILES / char2 / "relationships" / f"{char1}.md"
        if f1.exists():
            assert f2.exists(), f"Mirror missing: {char1} has {char2}.md but {char2} lacks {char1}.md"
        if f2.exists():
            assert f1.exists(), f"Mirror missing: {char2} has {char1}.md but {char1} lacks {char2}.md"

    @pytest.mark.parametrize("char1,char2", MIRROR_PAIRS)
    def test_mirror_files_have_cross_reference_links(self, char1, char2):
        """Each cross-relationship file should link to its mirror."""
        f1 = PROFILES / char1 / "relationships" / f"{char2}.md"
        if f1.exists():
            content = f1.read_text(encoding="utf-8")
            assert char2 in content or any(
                alias in content for alias in [char2.split("-")[-1].title()]
            ), f"{char1}/relationships/{char2}.md should reference {char2}"


class TestNoOrphanRelationshipFiles:
    """Relationship files must match known characters or be network.md."""

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_no_unknown_relationship_files(self, char):
        rel_dir = PROFILES / char / "relationships"
        known = {"family.md", "network.md"} | {f"{c}.md" for c in ALL_CHARS}
        actual = {f.name for f in rel_dir.glob("*.md")} if rel_dir.exists() else set()
        unknown = actual - known
        assert unknown == set(), f"{char} has unknown relationship files: {unknown}"


class TestPathsPyAccuracy:
    """paths.py functions must reflect actual filesystem state."""

    def test_list_relationship_files_matches_filesystem(self):
        from platform_lib.paths import list_relationship_files
        for char in ALL_CHARS:
            detected = {f.name for f in list_relationship_files(char)}
            expected = set(EXPECTED_CROSS_RELS[char])
            assert detected == expected, f"{char}: detected={detected}, expected={expected}"

    def test_list_all_profile_files_count(self):
        from platform_lib.paths import list_all_profile_files
        for char in ALL_CHARS:
            total = list_all_profile_files(char)
            base_expected = 25
            cross_expected = len(EXPECTED_CROSS_RELS[char])
            assert len(total) == base_expected + cross_expected, (
                f"{char}: expected {base_expected + cross_expected}, got {len(total)}"
            )

    def test_legacy_split_map_relationships_entry(self):
        from platform_lib.paths import LEGACY_SPLIT_MAP
        assert "RELATIONSHIPS.md" in LEGACY_SPLIT_MAP
        rel_files = LEGACY_SPLIT_MAP["RELATIONSHIPS.md"]
        assert "relationships/family.md" in rel_files
        assert len(rel_files) >= 4


class TestFamilySplitIntegrity:
    """Content from family.md split must be preserved, not lost."""

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_family_md_not_empty(self, char):
        fpath = PROFILES / char / "relationships" / "family.md"
        content = fpath.read_text(encoding="utf-8")
        lines = [l for l in content.splitlines() if l.strip()]
        assert len(lines) >= 20, f"{char}/family.md too small after split ({len(lines)} lines)"

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_cross_rel_files_have_substantial_content(self, char):
        """Main cross-relationship files (not indirect) should have real content."""
        for fname in EXPECTED_CROSS_RELS[char]:
            fpath = PROFILES / char / "relationships" / fname
            content = fpath.read_text(encoding="utf-8")
            head = content[:500]
            if "relationship: indirect" in head:
                continue
            lines = [l for l in content.splitlines() if l.strip()]
            assert len(lines) >= 15, f"{char}/{fname} too sparse ({len(lines)} lines)"

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_family_md_has_cross_reference_note(self, char):
        """family.md should have a note pointing to extracted cross-relationship files."""
        content = (PROFILES / char / "relationships" / "family.md").read_text(encoding="utf-8")
        has_xref = any(
            term in content.lower()
            for term in ["xem thêm", "xem chi tiết", "cross-ref", "extracted", "tách"]
        )
        assert has_xref, f"{char}/family.md should reference extracted cross-relationship files"


class TestNoLegacyRefsInProfiles:
    """No profile file should reference old flat filenames."""

    LEGACY_NAMES = [
        "SOUL.md", "DARKNESS.md", "LIGHT.md", "CHARACTERISTIC.md",
        "WRITING-VOICE.md", "IDENTITY.md", "RELATIONSHIPS.md",
        "INSPIRATION.md", "CONVERSATION.md", "MILESTONES.md",
    ]

    @pytest.mark.parametrize("char", ALL_CHARS)
    def test_zero_legacy_refs(self, char):
        cdir = PROFILES / char
        violations = []
        for fpath in cdir.rglob("*.md"):
            content = fpath.read_text(encoding="utf-8")
            for old_name in self.LEGACY_NAMES:
                if old_name in content:
                    rel = fpath.relative_to(cdir)
                    for line_no, line in enumerate(content.splitlines(), 1):
                        if old_name in line:
                            # Skip frontmatter, source comments, or plan refs
                            if line.strip().startswith("#") or "Source:" in line:
                                continue
                            if "LEGACY" in line or "→" in line or "->" in line:
                                continue
                            violations.append(f"{rel}:{line_no}: {line.strip()[:80]}")
        assert violations == [], f"{char} has legacy refs:\n" + "\n".join(violations[:10])
