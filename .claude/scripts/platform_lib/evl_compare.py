"""Cross-character comparison on one rubric (deterministic ranking + normalization).

Loads each character's scorecard for a rubric, ranks by raw overall, and attaches
peer-relative z / percentile via evl_normalize so scores compare fairly. A character
without a scorecard is reported in `missing` (loud) — never dropped silently and
never imputed as zero.
"""
from platform_lib import paths
from platform_lib.evl_normalize import normalize_cohort
from platform_lib.evl_tracker import load_current
from platform_lib.formatters import markdown_table


def _fmt(n) -> str:
    return "—" if n is None else (f"{n:g}" if isinstance(n, (int, float)) else str(n))


def compare(rubric_id: str, characters=None) -> dict:
    characters = characters if characters is not None else list(paths.ALL_CHARS)
    cards, missing = {}, []
    for char in characters:
        card = load_current(char, rubric_id)
        if card is None:
            missing.append(char)
        else:
            cards[char] = card

    stats = normalize_cohort(rubric_id, {c: cards[c].get("overall") for c in cards})
    ranked = [{"character": c, "raw": stats[c]["raw"], "z": stats[c]["z"],
               "percentile": stats[c]["percentile"], "note": stats[c]["note"],
               "verdict": cards[c].get("verdict")} for c in cards]
    # rank by raw desc; characters with no overall sort last (None → -inf surrogate)
    ranked.sort(key=lambda r: (r["raw"] is None, -(r["raw"] or 0)))
    return {"rubric_id": rubric_id, "ranked": ranked, "missing": missing}


def render_comparison(comparison: dict) -> str:
    rows = [[str(i), r["character"], _fmt(r["raw"]),
             _fmt(round(r["z"], 2) if isinstance(r["z"], (int, float)) else None),
             _fmt(round(r["percentile"]) if isinstance(r["percentile"], (int, float)) else None),
             _fmt(r["verdict"])]
            for i, r in enumerate(comparison["ranked"], 1)]
    out = [f"# Comparison — {comparison['rubric_id']}", "",
           markdown_table(["Rank", "Character", "Raw", "z", "Percentile", "Verdict"], rows)]
    if comparison["missing"]:
        out += ["", f"**Missing scorecards:** {', '.join(comparison['missing'])} "
                "(not scored on this rubric — excluded from the cohort)."]
    return "\n".join(out) + "\n"
