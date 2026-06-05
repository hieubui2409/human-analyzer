"""humanizer_patterns — deterministic VN+EN AI-tell scanner (the ONE taxonomy home).

Single source of the prose "AI-slop" taxonomy + structural heuristics. Character-agnostic,
no LLM, pure-stdlib. Consumed by the `cre:humanize` skill and the `cre:post-writer` /
`cre:multiplatform` gates (DRY — never re-roll the tables in a skill script).

Design split (GOLDEN RULE #4): this module GATHERS deterministically and may OVER-FLAG
(false positives are expected and acceptable); the LLM JUDGES which findings to act on and
does any rewrite. Never delegate that judgment to this script.

Taxonomy adapted from the `blader/humanizer` ruleset (MIT) + Wikipedia "Signs of AI writing"
+ the cleanmatic `humanizer-and-anti-ai-tells.md` Vietnamese word-for-word-translation tells.

Contract:
    scan(text, lang="auto", strictness="balanced") -> list[Finding]
    Finding = {category, pattern, match, span:(start,end), severity, suggestion, lang}

Categories: filler_phrase · formulaic_opener · formulaic_closer · rule_of_three ·
em_dash_overuse · hedging_density · low_burstiness.

Strictness (high | balanced | conservative) scales BOTH which phrase patterns fire (each
pattern carries a `min_tier`) AND the structural density cut-offs. Findings are guaranteed
MONOTONIC: scan(conservative) ⊆ scan(balanced) ⊆ scan(high). `low_burstiness` is high-tier
ONLY and advisory (severity "low") — VN social posts legitimately vary, so it never blocks.

Determinism: findings are returned sorted by (span_start, category) with no set-iteration
leakage, so identical input yields byte-stable output (safe to freeze as an eval golden case).
"""
import re
import statistics

# --- strictness tiers (ordered; higher rank = more aggressive, fires everything below it) ---
TIER_RANK = {"conservative": 0, "balanced": 1, "high": 2}
DEFAULT_STRICTNESS = "balanced"

# Structural density cut-offs = minimum occurrence COUNT in the text to raise the finding.
# A lower cut-off at a higher tier keeps findings monotonic (high fires with fewer hits, so
# whatever fires at conservative also fires at balanced and high).
STRICTNESS_THRESHOLDS = {
    "high":         {"rule_of_three": 1, "em_dash_overuse": 2, "hedging_density": 3},
    "balanced":     {"rule_of_three": 2, "em_dash_overuse": 4, "hedging_density": 5},
    "conservative": {"rule_of_three": 3, "em_dash_overuse": 6, "hedging_density": 8},
}
# low_burstiness: high tier only. Coefficient of variation (stdev/mean of sentence word-counts)
# below this, over a minimum sentence count, reads mechanically uniform.
BURSTINESS_CV_MAX = 0.40
BURSTINESS_MIN_SENTENCES = 5


def _p(category, lang, pattern, suggestion, min_tier, severity="medium"):
    return {"category": category, "lang": lang, "pattern": pattern,
            "suggestion": suggestion, "min_tier": min_tier, "severity": severity}


# --- phrase taxonomy (filler / openers / closers), VN + EN ------------------------------
# `min_tier` = lowest strictness at which the pattern fires. Clear tells fire at
# "conservative" (all tiers); riskier-FP single-word vocab gated to "balanced"+.
_PHRASES = [
    # ---- Vietnamese filler / translationese (calques) ----
    _p("filler_phrase", "vi", r"đáng chú ý là", 'bỏ — vào thẳng ý', "conservative", "high"),
    _p("filler_phrase", "vi", r"điều quan trọng cần lưu ý", "bỏ — nói thẳng điều quan trọng", "conservative", "high"),
    _p("filler_phrase", "vi", r"không thể phủ nhận rằng", "bỏ — khẳng định thẳng", "conservative", "high"),
    _p("filler_phrase", "vi", r"đảm bảo (rằng|là)", "→ 'để chắc chắn' / 'cho chắc'", "conservative"),
    _p("filler_phrase", "vi", r"nhằm mục đích|với mục đích", "→ 'để'", "conservative"),
    _p("filler_phrase", "vi", r"điều này cho phép|việc này giúp", "→ 'nhờ đó' / 'như vậy'", "conservative"),
    _p("filler_phrase", "vi", r"(nó|điều này) (đóng vai trò|hoạt động) như", "→ 'là' / 'làm'", "conservative"),
    _p("filler_phrase", "vi", r"một cách\s+\S+", "bỏ 'một cách', viết thẳng tính từ", "balanced"),
    _p("filler_phrase", "vi", r"dữ liệu tươi|quét tươi|làm tươi", "→ 'số liệu mới nhất' / 'quét lại từ đầu'", "balanced"),
    _p("filler_phrase", "vi", r"trải nghiệm gốc|đường gốc", "→ 'ứng dụng riêng' / 'trải nghiệm trên app'", "balanced"),
    # ---- Vietnamese overused vocabulary ----
    _p("filler_phrase", "vi", r"\btận dụng\b|\btối ưu hóa\b|\bmạnh mẽ\b|\bliền mạch\b|\btoàn diện\b",
       "dùng từ cụ thể đúng nghĩa, đừng sáo rỗng", "balanced", "low"),
    # ---- Vietnamese formulaic openers ----
    _p("formulaic_opener", "vi", r"(?m)^\s*Trong (thế giới ngày nay|thời đại số|bối cảnh hiện nay)",
       "mở bài bằng chi tiết cụ thể, không sáo", "conservative", "high"),
    _p("formulaic_opener", "vi", r"(?m)^\s*Có thể nói rằng", "vào thẳng luận điểm", "conservative"),
    # ---- Vietnamese formulaic closers ----
    _p("formulaic_closer", "vi", r"(?m)^\s*(Tóm lại|Nhìn chung)[,:]", "kết bằng một sự thật/bước cụ thể", "conservative"),
    _p("formulaic_closer", "vi", r"(?m)^\s*Cuối cùng nhưng không kém phần quan trọng",
       "bỏ — sáo rỗng dịch máy", "conservative", "high"),
    _p("formulaic_closer", "vi", r"Hy vọng (bài viết|nội dung) này", "bỏ câu chốt khách sáo", "balanced"),
    # ---- English filler / hedged constructions ----
    _p("filler_phrase", "en", r"it'?s worth noting( that)?", "drop — state it", "conservative", "high"),
    _p("filler_phrase", "en", r"it is important to note( that)?", "drop — state it", "conservative", "high"),
    _p("filler_phrase", "en", r"in order to", "→ 'to'", "conservative"),
    _p("filler_phrase", "en", r"due to the fact that", "→ 'because'", "conservative"),
    _p("filler_phrase", "en", r"at this point in time", "→ 'now'", "conservative"),
    _p("filler_phrase", "en", r"has the ability to", "→ 'can'", "conservative"),
    _p("filler_phrase", "en", r"not only\b.+?\bbut also", "state the point as one clause", "balanced"),
    _p("filler_phrase", "en", r"\b(serves|stands|acts) as\b|\bboasts\b", "→ 'is' / 'has'", "balanced"),
    # ---- English overused AI vocabulary ----
    _p("filler_phrase", "en",
       r"\b(delve|leverage|tapestry|testament|underscore|pivotal|showcase|foster|garner|"
       r"intricate|seamless|robust|vibrant|nestled|realm|groundbreaking)\b",
       "swap for a concrete, specific word", "balanced", "low"),
    # ---- English formulaic openers ----
    _p("formulaic_opener", "en", r"(?mi)^\s*In (today'?s world|the world of|the realm of|an era of)",
       "open with a concrete detail", "conservative", "high"),
    _p("formulaic_opener", "en", r"(?mi)^\s*When it comes to", "go straight to the point", "conservative"),
    _p("formulaic_opener", "en", r"(?mi)^\s*(let'?s dive in|without further ado|here'?s what you need to know)",
       "just say the thing (signposting)", "conservative"),
    # ---- English formulaic closers ----
    _p("formulaic_closer", "en", r"(?mi)^\s*(in conclusion|all in all|at the end of the day|last but not least)",
       "close with a fact or next step", "conservative"),
    _p("formulaic_closer", "en", r"the future looks bright", "→ a specific fact / next step", "balanced"),
]

for _e in _PHRASES:
    _e["_re"] = re.compile(_e["pattern"], re.IGNORECASE | re.UNICODE)

# --- structural heuristics --------------------------------------------------------------
# Triad "X, Y, and Z" / VN "X, Y và Z" — rule-of-three overuse.
_TRIAD_RE = re.compile(
    r"\b[\wÀ-ỹ]+\s*,\s*[\wÀ-ỹ]+\s*,?\s+(?:and|or|và|hoặc)\s+[\wÀ-ỹ]+\b",
    re.IGNORECASE | re.UNICODE)
_EM_DASH_RE = re.compile(r"[—–]|(?<=\s)--(?=\s)")  # em dash, en dash, spaced double-hyphen
_HEDGE_RE = re.compile(
    r"\b(perhaps|maybe|arguably|possibly|might|could|seems|appears|relatively|somewhat)\b"
    r"|(có thể|có lẽ|dường như|hình như|phần nào|tương đối|khá là)",
    re.IGNORECASE | re.UNICODE)
_SENTENCE_SPLIT_RE = re.compile(r"[.!?…]+\s+|\n+")


def _fires(pattern_min_tier: str, strictness: str) -> bool:
    return TIER_RANK[strictness] >= TIER_RANK[pattern_min_tier]


def _split_sentences(text: str) -> list[str]:
    return [s.strip() for s in _SENTENCE_SPLIT_RE.split(text) if s.strip()]


def _scan_phrases(text: str, langs: set[str], strictness: str) -> list[dict]:
    out = []
    for e in _PHRASES:
        if e["lang"] not in langs or not _fires(e["min_tier"], strictness):
            continue
        for m in e["_re"].finditer(text):
            out.append({
                "category": e["category"], "pattern": e["pattern"], "match": m.group(0),
                "span": (m.start(), m.end()), "severity": e["severity"],
                "suggestion": e["suggestion"], "lang": e["lang"],
            })
    return out


def _structural_finding(category, occurrences, count, threshold, severity, suggestion):
    """Raise one finding for a structural category when count >= threshold; anchor the span
    on the FIRST occurrence so the span is a real, stable slice of the text."""
    if count < threshold or not occurrences:
        return None
    first = occurrences[0]
    return {
        "category": category, "pattern": category, "match": first[2],
        "span": (first[0], first[1]), "severity": severity,
        "suggestion": f"{suggestion} ({count} hits)", "lang": "neutral",
    }


def _scan_structural(text: str, strictness: str) -> list[dict]:
    out = []
    th = STRICTNESS_THRESHOLDS[strictness]

    triads = [(m.start(), m.end(), m.group(0)) for m in _TRIAD_RE.finditer(text)]
    f = _structural_finding("rule_of_three", triads, len(triads), th["rule_of_three"],
                            "medium", "break forced triples; vary the grouping")
    if f:
        out.append(f)

    dashes = [(m.start(), m.end(), m.group(0)) for m in _EM_DASH_RE.finditer(text)]
    f = _structural_finding("em_dash_overuse", dashes, len(dashes), th["em_dash_overuse"],
                            "medium", "replace em/en dashes with period, comma, colon or parens")
    if f:
        out.append(f)

    hedges = [(m.start(), m.end(), m.group(0)) for m in _HEDGE_RE.finditer(text)]
    f = _structural_finding("hedging_density", hedges, len(hedges), th["hedging_density"],
                            "low", "cut excess hedging; commit to the claim")
    if f:
        out.append(f)

    # low_burstiness: high tier only, advisory.
    if strictness == "high":
        sentences = _split_sentences(text)
        counts = [len(s.split()) for s in sentences]
        if len(counts) >= BURSTINESS_MIN_SENTENCES:
            mean = statistics.mean(counts)
            cv = (statistics.pstdev(counts) / mean) if mean else 0.0
            if cv < BURSTINESS_CV_MAX:
                out.append({
                    "category": "low_burstiness", "pattern": "low_burstiness", "match": "",
                    "span": (0, 0), "severity": "low",
                    "suggestion": f"uniform sentence length (cv={cv:.2f}); vary short vs long",
                    "lang": "neutral",
                })
    return out


def scan(text: str, lang: str = "auto", strictness: str = DEFAULT_STRICTNESS) -> list[dict]:
    """Scan `text` for AI-tells. Deterministic, no LLM. Returns findings sorted by
    (span_start, category). `lang` ∈ {auto, vi, en}; `strictness` ∈ {high, balanced, conservative}.

    `auto` over-gathers (scans both VN and EN phrase tables); pass an explicit `lang` to
    restrict. Structural heuristics are language-neutral and always run."""
    if strictness not in TIER_RANK:
        strictness = DEFAULT_STRICTNESS
    if lang == "auto":
        langs = {"vi", "en"}
    elif lang in ("vi", "en"):
        langs = {lang}
    else:
        langs = {"vi", "en"}

    findings = _scan_phrases(text, langs, strictness) + _scan_structural(text, strictness)
    # Total-order sort key so byte-stability is structural, not reliant on stable-sort +
    # insertion order (two distinct patterns can share span_start + category).
    findings.sort(key=lambda f: (f["span"][0], f["span"][1], f["category"], f["pattern"]))
    return findings
