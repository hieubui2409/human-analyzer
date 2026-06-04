"""Canonical GRO-domain vocabularies (Super / Kolb / Kram / Dreyfus).

Single source of truth so every gro:* gather script labels career stage, learning
style, network typology and competency level identically — eliminating the prior
divergence where gro:compare and gro:career-forecast carried *different* stage lists
and could report conflicting stages for the same character.

These are deterministic keyword vocabularies for GATHERING signals. The gro:* SKILLs
route the actual classification judgment to the LLM; the helpers below only surface
which canonical terms appear (and which appears earliest in the text) so the LLM has
the raw signal rather than a script-imposed verdict.
"""

# Donald Super's life-career stages, in canonical developmental order.
SUPER_STAGES = ["growth", "exploration", "establishment", "maintenance", "disengagement"]

# Kolb's four experiential-learning styles.
KOLB_STYLES = ["diverging", "assimilating", "converging", "accommodating"]

# Kram developmental-network typologies (Higgins & Kram).
KRAM_NETWORK_TYPES = ["receptive", "traditional", "entrepreneurial", "opportunistic"]

# Dreyfus skill-acquisition levels (1-7, extended model).
DREYFUS_LEVELS = {
    1: "Novice",
    2: "Advanced Beginner",
    3: "Competent",
    4: "Proficient",
    5: "Expert",
    6: "Master",
    7: "Practical Wisdom",
}


def mentioned_terms(text: str, vocab: list[str]) -> list[str]:
    """Return the vocab terms present in ``text``, ordered by first occurrence in the text.

    Position-based (not vocab-order-based) so the result is deterministic and reflects the
    document rather than an arbitrary list priority. De-duplicated, case-insensitive.
    """
    low = text.lower()
    hits = [(low.find(t), t) for t in vocab if t in low]
    return [t for _, t in sorted(hits)]


def earliest_term(text: str, vocab: list[str], default: str = "unknown") -> str:
    """The vocab term whose first occurrence is earliest in ``text`` (else ``default``)."""
    found = mentioned_terms(text, vocab)
    return found[0] if found else default
