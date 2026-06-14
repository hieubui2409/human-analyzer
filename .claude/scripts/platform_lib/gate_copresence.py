"""gate_copresence — CO-PRESENCE static check for GATE-<UPPER> tokens.

Distinct from context-budget-gauge.cjs (runtime session tokens). This is an
offline, deterministic authored-doc integrity check: every GATE-<UPPER> token
referenced in a skill SKILL.md or its references/*.md must have a full-prose
<GATE-X>…</GATE-X> definition reachable in either (a) the always-on layer
(gates-and-anti-rationalization.md) or (b) the skill's own files.

GATE_RE matches strict GATE-<UPPER> form only — no lowercase, no mid-word match
(so MITIGATE-X and HARD-GATE-X are both correctly excluded).  Shape derived from
the sibling context_footprint.py in product-spec (read-only reference), adapted
to this repo's line-based measurement and single always-on source.
"""
from __future__ import annotations

import re
from pathlib import Path

# Matches GATE-<UPPER> tokens only.  Negative lookbehind: no preceding alpha,
# digit, or dash — excludes MITIGATE-X (alpha before G) and HARD-GATE-X
# (dash before G in the compound token).  Suffix must start with A-Z and end
# on A-Z or 0-9 (trailing dash excluded).
GATE_RE = re.compile(
    r"(?<![A-Za-z0-9-])GATE-(?P<suffix>[A-Z](?:[A-Z0-9-]*[A-Z0-9])?)"
)

# Matches a full-prose home: <GATE-X>…</GATE-X> XML tag block.
_HOME_TAG_RE = re.compile(
    r"<GATE-(?P<name>[A-Z][A-Z0-9-]*[A-Z0-9]|[A-Z])>.*?</GATE-(?P=name)>",
    re.DOTALL,
)


def gate_names(text: str) -> set[str]:
    """All GATE-<UPPER> tokens referenced in text, canonical form."""
    return {"GATE-" + m.group("suffix") for m in GATE_RE.finditer(text)}


def home_gates(text: str) -> set[str]:
    """GATEs that have a full-prose <GATE-X>…</GATE-X> home in text."""
    return {"GATE-" + m.group("name") for m in _HOME_TAG_RE.finditer(text)}


def check_copresence(skill_dirs: list[Path], always_on_text: str) -> list[str]:
    """Return sorted list of failure strings for orphaned GATE references.

    For each skill dir: collect all GATE tokens referenced anywhere in
    SKILL.md + references/*.md; assert each has a home in the always-on
    layer OR in that skill's own files.  A same-file <GATE-X> definition
    satisfies the pointer in the same file (no false positives on
    self-contained skills).
    """
    always_homes = home_gates(always_on_text)
    failures: list[str] = []

    for sk in skill_dirs:
        files: list[Path] = []
        smd = sk / "SKILL.md"
        if smd.is_file():
            files.append(smd)
        ref_dir = sk / "references"
        if ref_dir.is_dir():
            files.extend(sorted(ref_dir.glob("*.md")))

        texts = {f: f.read_text(encoding="utf-8") for f in files}
        skill_homes = set()
        for t in texts.values():
            skill_homes |= home_gates(t)
        reachable = always_homes | skill_homes

        for f, t in texts.items():
            for g in gate_names(t):
                if g not in reachable:
                    failures.append(
                        f"{sk.name}/{f.name}: pointer to {g} has no reachable full-prose home"
                    )

    return sorted(set(failures))
