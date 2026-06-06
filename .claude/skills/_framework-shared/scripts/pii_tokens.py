"""Shared PII token set + placeholder mapping for the doc masker (mask_doc_names) and the
whole-pack scanner (scan_pack_pii).

NAME-FREE BY CONTRACT: this file ships in the pack and contains ZERO real names — every token loads
at runtime from the pack-excluded characters.yaml / pii-tokens.yaml. When those files are absent (a
toolkit-only consumer pack), the loaders return [] so both dependents become no-ops / skip cleanly.

Two consumers, two needs:
  * load_tokens()  — the MASKER set: per character the display name + multi-word full names →
    "Nhân vật {A,B,…}" / "Character {A,B,…}", the kebab slug → synthetic "character-{a,b,…}", plus
    org/program/location extras. The masker replaces these in doc PROSE (word-boundary, case-sensitive).
  * scan_tokens()  — the SCANNER set: only the COLLISION-FREE tokens (kebab slugs + multi-word full
    names + extras, incl. lower-cased extras). It deliberately OMITS bare display names (Nhân vật B, Nhân vật C,
    Nhân vật A) because those are everyday Vietnamese words — a whole-pack grep on them would storm with
    false positives (peace, strategy, filial piety). The scanner therefore hard-gates only on forms
    that cannot collide with ordinary text; bare display names are masked best-effort, not gated.
"""
import unicodedata
from pathlib import Path


def _asciifold(s: str) -> str:
    """Strip Vietnamese diacritics to the bare ASCII form (Đ/đ → D/d). Used so the diacritic-free
    rendering of a multi-word full name (the natural form on a non-VN keyboard) is gated/masked too."""
    base = "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c))
    return base.replace("Đ", "D").replace("đ", "d")


def _default_profiles_dir() -> Path:
    # _framework-shared/scripts/pii_tokens.py -> repo root is parents[4]
    return Path(__file__).resolve().parents[4] / "docs" / "profiles"


def _load_roster(profiles_dir=None):
    """Return (roster_dict, extras_list) from the pack-excluded corpus, or ({}, []) when absent."""
    try:
        import yaml
    except ImportError:
        return {}, []
    pdir = Path(profiles_dir) if profiles_dir else _default_profiles_dir()
    roster_path = pdir / "characters.yaml"
    roster = {}
    if roster_path.exists():
        roster = (yaml.safe_load(roster_path.read_text(encoding="utf-8")) or {}).get("characters") or {}
    extras = []
    extras_path = pdir / "pii-tokens.yaml"
    if extras_path.exists():
        data = yaml.safe_load(extras_path.read_text(encoding="utf-8")) or {}
        extras = data.get("extra") or []
    return roster, extras


def load_tokens(profiles_dir=None):
    """MASKER set: ``[(token, placeholder_vi, placeholder_en), ...]`` sorted longest-token-first.

    Per character: display + multi-word full names → "Nhân vật {L}"/"Character {L}"; kebab slug →
    synthetic "character-{l}". Plus pii-tokens.yaml extras. [] when the roster is absent.
    """
    roster, extras = _load_roster(profiles_dir)
    out = []
    for i, (slug, info) in enumerate(roster.items()):
        info = info or {}
        letter = chr(ord("A") + i)
        prose_vi, prose_en = f"Nhân vật {letter}", f"Character {letter}"
        synth = f"character-{letter.lower()}"

        names = []
        display = info.get("display")
        if display:
            names.append(display)
        names += [a for a in info.get("aliases", []) if " " in a]  # full names only
        # Gate/mask the diacritic-free rendering of each multi-word full name too (collision-free).
        names += [_asciifold(a) for a in names if " " in a and _asciifold(a) != a]
        for tok in names:
            out.append((tok, prose_vi, prose_en))
        out.append((slug, synth, synth))

    for extra in extras:
        tok = extra.get("token")
        if tok:
            out.append((tok, extra.get("placeholder_vi", tok), extra.get("placeholder_en", tok)))

    seen, deduped = set(), []
    for row in out:
        if row[0] not in seen:
            seen.add(row[0])
            deduped.append(row)
    deduped.sort(key=lambda t: len(t[0]), reverse=True)
    return deduped


def tokens_only(profiles_dir=None):
    """The raw MASKER token list (what the masker targets). [] when the roster is absent."""
    return [t[0] for t in load_tokens(profiles_dir)]


def scan_tokens(profiles_dir=None):
    """SCANNER set: collision-free forbidden tokens, matched case-sensitively by the pack scanner.

    Includes kebab slugs + multi-word full-name aliases + extras (and each extra's lower-case form,
    so an org/place baked into a filename is still caught). OMITS bare display names — they collide
    with everyday Vietnamese words and cannot be a clean whole-pack grep gate. [] when roster absent.
    """
    roster, extras = _load_roster(profiles_dir)
    out = []
    for slug, info in roster.items():
        info = info or {}
        out.append(slug)
        fulls = [a for a in info.get("aliases", []) if " " in a]  # multi-word full names only
        out += fulls
        out += [_asciifold(a) for a in fulls if _asciifold(a) != a]  # diacritic-free full names too
    for extra in extras:
        tok = extra.get("token")
        if tok:
            out.append(tok)
            if tok.lower() != tok:
                out.append(tok.lower())
    # De-dup, longest-first (so a full name matches before any substring).
    return sorted(set(out), key=len, reverse=True)


def roster_present(profiles_dir=None) -> bool:
    """True if the roster DATA file exists on disk (regardless of whether it parses).

    Lets the scanner distinguish a toolkit-only consumer pack (file genuinely absent → skip is safe)
    from a release/source build where characters.yaml is present but produced ZERO tokens (yaml missing
    or unparsed) — the latter must fail closed rather than pass vacuously."""
    pdir = Path(profiles_dir) if profiles_dir else _default_profiles_dir()
    return (pdir / "characters.yaml").exists()
