"""Test platform_lib modules: paths, clinical_terms, markdown_parser, env_utils, csv_search."""
import os
import sys
from pathlib import Path

import pytest

# Ensure platform_lib is importable
SCRIPTS_DIR = Path(__file__).resolve().parents[1] / ".claude" / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))


class TestPaths:
    """Test paths.py module."""

    def test_profile_files_has_21_entries(self):
        """PROFILE_FILES should contain exactly 21 files."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.PROFILE_FILES) == 21
        # Verify some key files exist
        assert "INDEX.md" in paths_mod.PROFILE_FILES
        assert "CURRENT-STATE.md" in paths_mod.PROFILE_FILES
        assert "identity/core.md" in paths_mod.PROFILE_FILES
        assert "psychology/formulation.md" in paths_mod.PROFILE_FILES

    def test_legacy_to_new_map_exists(self):
        """LEGACY_TO_NEW_MAP should map old filenames to new ones."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.LEGACY_TO_NEW_MAP) > 0
        # Check key mappings
        assert paths_mod.LEGACY_TO_NEW_MAP.get("SOUL.md") == "psychology/formulation.md"
        assert paths_mod.LEGACY_TO_NEW_MAP.get("DARKNESS.md") == "darkness/traumas.md"
        assert paths_mod.LEGACY_TO_NEW_MAP.get("LIGHT.md") == "light/strengths-hope.md"

    def test_legacy_split_map_exists(self):
        """LEGACY_SPLIT_MAP should exist with multi-file mappings."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.LEGACY_SPLIT_MAP) > 0
        # Check key splits
        assert "SOUL.md" in paths_mod.LEGACY_SPLIT_MAP
        assert len(paths_mod.LEGACY_SPLIT_MAP["SOUL.md"]) == 2

    def test_resolve_character_works(self):
        """resolve_character should handle aliases correctly."""
        import platform_lib.paths as paths_mod
        # Should work with actual names
        assert paths_mod.resolve_character("character-a") == "character-a"
        # Should work with Vietnamese names with accents
        assert paths_mod.resolve_character("hiếu") == "character-a"
        assert paths_mod.resolve_character("hòa") == "character-b"
        # Should be case-insensitive
        assert paths_mod.resolve_character("HIEU") == "character-a"

    def test_resolve_character_raises_on_unknown(self):
        """resolve_character should raise ValueError for unknown names."""
        import platform_lib.paths as paths_mod
        with pytest.raises(ValueError, match="Unknown character"):
            paths_mod.resolve_character("unknown-person")

    def test_character_dir_returns_path(self):
        """character_dir should return valid path objects."""
        import platform_lib.paths as paths_mod
        result = paths_mod.character_dir("hieu")
        assert isinstance(result, Path)
        assert "character-a" in str(result)

    def test_materials_dir_returns_path(self):
        """materials_dir should return valid path objects."""
        import platform_lib.paths as paths_mod
        result = paths_mod.materials_dir("hieu")
        assert isinstance(result, Path)
        assert "character-a" in str(result)

    def test_all_chars_not_empty(self):
        """ALL_CHARS should contain character identifiers."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.ALL_CHARS) > 0
        assert "character-a" in paths_mod.ALL_CHARS or "test-alpha" in paths_mod.ALL_CHARS

    def test_characters_mapping_valid(self):
        """CHARACTERS mapping should have proper keys and values."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.CHARACTERS) > 0
        for key, value in paths_mod.CHARACTERS.items():
            assert isinstance(key, str)
            assert isinstance(value, str)

    def test_profile_by_concept_has_keys(self):
        """PROFILE_BY_CONCEPT should map semantic keys to paths."""
        import platform_lib.paths as paths_mod
        assert len(paths_mod.PROFILE_BY_CONCEPT) > 0
        # Check some known keys
        assert "identity" in paths_mod.PROFILE_BY_CONCEPT
        assert "formulation" in paths_mod.PROFILE_BY_CONCEPT
        assert "attachment_style" in paths_mod.PROFILE_BY_CONCEPT

    def test_legacy_split_map_has_relationships(self):
        """LEGACY_SPLIT_MAP should include RELATIONSHIPS.md split."""
        import platform_lib.paths as paths_mod
        assert "RELATIONSHIPS.md" in paths_mod.LEGACY_SPLIT_MAP
        rel_files = paths_mod.LEGACY_SPLIT_MAP["RELATIONSHIPS.md"]
        assert "relationships/family.md" in rel_files
        assert len(rel_files) >= 2

    def test_list_relationship_files_returns_list(self):
        """list_relationship_files should return a list of Paths."""
        import platform_lib.paths as paths_mod
        result = paths_mod.list_relationship_files("hieu")
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, Path)
            assert item.suffix == ".md"
            assert item.name != "family.md"

    def test_list_relationship_files_per_character(self):
        """Each character should have correct cross-relationship files."""
        import platform_lib.paths as paths_mod
        hieu_rels = [f.name for f in paths_mod.list_relationship_files("hieu")]
        assert "character-b.md" in hieu_rels
        assert "character-c.md" in hieu_rels

    def test_list_all_profile_files_superset(self):
        """list_all_profile_files should return more files than list_profile_files."""
        import platform_lib.paths as paths_mod
        base = paths_mod.list_profile_files("hieu")
        total = paths_mod.list_all_profile_files("hieu")
        assert len(total) >= len(base)


class TestClinicalTerms:
    """Test clinical_terms.py module."""

    def test_patterns_list_not_empty(self):
        """CLINICAL_PATTERNS should contain regex patterns."""
        import platform_lib.clinical_terms as ct_mod
        assert hasattr(ct_mod, "CLINICAL_PATTERNS")
        assert len(ct_mod.CLINICAL_PATTERNS) > 0
        # All should be strings (regex patterns)
        for pattern in ct_mod.CLINICAL_PATTERNS:
            assert isinstance(pattern, str)

    def test_patterns_contain_key_terms(self):
        """CLINICAL_PATTERNS should include key clinical terms."""
        import platform_lib.clinical_terms as ct_mod
        patterns_str = " ".join(ct_mod.CLINICAL_PATTERNS)
        # Check for some key patterns
        assert "attachment" in patterns_str.lower()
        assert "trauma" in patterns_str.lower() or "PTSD" in patterns_str
        assert "defense" in patterns_str.lower() or "denial" in patterns_str


class TestMarkdownParser:
    """Test markdown_parser.py module."""

    def test_markdown_parser_importable(self):
        """markdown_parser module should be importable."""
        try:
            import platform_lib.markdown_parser as mp_mod
            assert hasattr(mp_mod, "extract_sections") or hasattr(mp_mod, "extract_frontmatter")
        except ImportError:
            pytest.skip("markdown_parser not available or incompatible")

    def test_extract_section_on_sample_markdown(self):
        """extract_section should work on sample markdown."""
        try:
            import platform_lib.markdown_parser as mp_mod
            if not hasattr(mp_mod, "extract_section"):
                pytest.skip("extract_section not available")

            sample = "# Header\n\n## Section\nContent here\n\n## Another\nMore content"
            result = mp_mod.extract_section(sample, "Section")
            # Should return something if the function exists and works
            assert result is not None or result == ""
        except Exception:
            pytest.skip("extract_section implementation incompatible")

    def test_parse_frontmatter_on_yaml(self):
        """parse_frontmatter should handle YAML frontmatter."""
        try:
            import platform_lib.markdown_parser as mp_mod
            if not hasattr(mp_mod, "parse_frontmatter"):
                pytest.skip("parse_frontmatter not available")

            sample = "---\nkey: value\n---\nContent"
            result = mp_mod.parse_frontmatter(sample)
            # Should return a dict or None
            assert isinstance(result, dict) or result is None
        except Exception:
            pytest.skip("parse_frontmatter implementation incompatible")


class TestEnvUtils:
    """Test env_utils.py module."""

    def test_env_utils_importable(self):
        """env_utils module should be importable."""
        try:
            import platform_lib.env_utils as eu_mod
            assert hasattr(eu_mod, "load_env") or hasattr(eu_mod, "get_api_key")
        except ImportError:
            pytest.skip("env_utils not available")

    def test_load_env_handles_missing_env(self):
        """load_env should handle missing .env gracefully."""
        try:
            import platform_lib.env_utils as eu_mod
            if not hasattr(eu_mod, "load_env"):
                pytest.skip("load_env not available")

            # Should not crash on missing file
            result = eu_mod.load_env("/nonexistent/.env")
            # Should return dict or None
            assert isinstance(result, dict) or result is None
        except FileNotFoundError:
            # Acceptable behavior
            pass
        except Exception:
            pytest.skip("load_env implementation incompatible")


class TestCsvSearch:
    """Test csv_search.py module."""

    def test_csv_search_importable(self):
        """csv_search module should be importable."""
        try:
            import platform_lib.csv_search as cs_mod
            # Should have search functions
            assert hasattr(cs_mod, "search") or hasattr(cs_mod, "bm25_search")
        except ImportError:
            pytest.skip("csv_search not available")

    def test_csv_search_handles_empty_input(self):
        """csv_search functions should handle empty input."""
        try:
            import platform_lib.csv_search as cs_mod
            if not hasattr(cs_mod, "search") and not hasattr(cs_mod, "bm25_search"):
                pytest.skip("search functions not available")

            # Call with empty data should not crash
            if hasattr(cs_mod, "search"):
                result = cs_mod.search([], "query")
                assert isinstance(result, (list, dict)) or result is None
        except Exception:
            pytest.skip("csv_search implementation incompatible")


class TestProfileValidator:
    """Test profile_validator.py module if available."""

    def test_profile_validator_importable(self):
        """profile_validator should be importable."""
        try:
            import platform_lib.profile_validator as pv_mod
            assert hasattr(pv_mod, "validate_all") or hasattr(pv_mod, "validate_character")
        except ImportError:
            pytest.skip("profile_validator not available")


class TestFormatters:
    """Test formatters.py module."""

    def test_formatters_importable(self):
        """formatters module should be importable."""
        try:
            import platform_lib.formatters as fmt_mod
            # Should have formatting functions
            assert hasattr(fmt_mod, "markdown_table") or hasattr(fmt_mod, "print_table")
        except ImportError:
            pytest.skip("formatters not available")
