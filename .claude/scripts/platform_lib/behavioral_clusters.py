"""Behavioral cluster detection: HYBRID approach (regex pre-filter + LLM deep scan).

Phase 1 (deterministic): Regex patterns catch low-hanging behavioral descriptions.
Phase 2 (heuristic): Plain-text behavioral DESCRIPTIONS catalog + extracted text sections
    → output for LLM semantic matching.

Scripts call Phase 1 for fast pre-filter. Skills call Phase 2 catalog for LLM prompt.

Usage:
    # Phase 1: regex pre-filter (script)
    from platform_lib.behavioral_clusters import scan_file_for_behavioral_clusters
    # Phase 2: LLM catalog (skill)
    from platform_lib.behavioral_clusters import BEHAVIORAL_DESCRIPTIONS, extract_sections_for_llm_review
"""
import re
from pathlib import Path
from typing import Optional

BEHAVIORAL_CLUSTERS: dict[str, list[str]] = {
    # --- Negotiation & Behavioral Economics ---
    "anchoring": [
        r"(?:neo|anchor).*(?:giá|value|price|mức)",
        r"hệ số.*(?:thưởng|bonus|đánh giá)",
        r"(?:gửi|show|tiết lộ).*(?:payslip|bảng lương|evidence).*(?:trước|first|before)",
        r"(?:con số|number|data).*(?:đầu tiên|first|initial).*(?:ấn tượng|impression)",
    ],
    "loss-aversion": [
        r"(?:sợ|fear|afraid).*(?:mất|lose|losing).*(?:người|ứng viên|candidate|deal)",
        r"counter[\s-]?offer",
        r"(?:giữ|retain|keep).*(?:nhân viên|employee|người)",
        r"(?:rủi ro|risk).*(?:mất|lose|losing)",
    ],
    "commitment-trap": [
        r"(?:đã|already).*(?:đầu tư|invest|process|cam kết|commit)",
        r"(?:không thể|can't|cannot).*(?:quay lại|go back|reverse|đảo ngược)",
        r"(?:buộc|forced|obligated).*(?:bảo vệ|protect|defend).*(?:deal|quyết định)",
        r"foot[\s-]?in[\s-]?the[\s-]?door",
    ],
    "sunk-cost-fallacy": [
        r"(?:đã bỏ|spent|invested).*(?:thời gian|time|effort|công sức)",
        r"(?:phí|waste|lãng phí).*(?:nếu|if).*(?:dừng|stop|bỏ|quit)",
        r"(?:tiếp tục|continue|keep going).*(?:dù|despite|although).*(?:không|not)",
    ],
    "fomo": [
        r"(?:sợ|fear|afraid).*(?:bỏ lỡ|miss out|mất cơ hội)",
        r"(?:khan hiếm|scarce|rare|limited).*(?:ứng viên|candidate|cơ hội|opportunity)",
        r"(?:nhanh|fast|urgent|gấp).*(?:chốt|close|decide|quyết định)",
        r"(?:người khác|others|competitor).*(?:muốn|want|đang).*(?:giữ|retain|recruit)",
    ],
    "face-saving": [
        r"(?:giữ|save|protect|bảo vệ).*(?:mặt|face|thể diện|uy tín)",
        r"(?:không|not).*(?:mất mặt|lose face|xấu hổ|embarrass)",
        r"(?:nói giảm|understate|downplay|euphemism)",
        r"(?:sương mù|fog|ambiguous).*(?:toán|math|số|number)",
    ],
    "emotional-framing": [
        r"(?:frame|đóng khung|trình bày).*(?:cảm xúc|emotion|feeling)",
        r"(?:persona|hình ảnh|image).*(?:mệt mỏi|weary|reluctant|miễn cưỡng)",
        r"(?:oải|mệt|tired|exhausted).*(?:nhưng|but|thực ra|actually)",
        r"(?:expert|chuyên gia).*(?:bị kéo|pulled|reluctant|miễn cưỡng)",
    ],
    "rapport-engineering": [
        r"(?:xây|build|tạo).*(?:rapport|mối quan hệ|trust|tin tưởng)",
        r"(?:thân thiện|friendly|warm).*(?:tin nhắn|message|chat|response)",
        r"(?:chia sẻ|share).*(?:khó khăn|difficulty|struggle|personal)",
        r"(?:gọi điện|phone call|voice).*(?:thay|instead|thay vì).*(?:text|tin nhắn)",
    ],
    # --- Clinical Psychology (behavioral descriptions) ---
    "savior-complex": [
        r"(?:cứu|rescue|save|protect).*(?:mọi người|everyone|người khác|others)",
        r"(?:hy sinh|sacrifice).*(?:bản thân|mình|self|own)",
        r"(?:không thể|can't).*(?:ngồi yên|stand by|sit idle).*(?:khi|when|while)",
        r"(?:gánh|bear|carry).*(?:trách nhiệm|responsibility).*(?:không phải|not).*(?:của mình|theirs)",
        r"(?:lo|worry|care).*(?:cho|for).*(?:người|people|others).*(?:hơn|more than).*(?:mình|self)",
    ],
    "intellectualization": [
        r"(?:phân tích|analyze|dissect).*(?:cảm xúc|emotion|feeling|nỗi đau|pain)",
        r"(?:bảng tính|spreadsheet|data|số liệu).*(?:thay cho|instead of|thay vì).*(?:cảm|feel)",
        r"(?:logic|lý trí|rational).*(?:che|shield|mask|giấu).*(?:cảm xúc|emotion|hurt)",
        r"(?:tính toán|calculate|compute).*(?:mọi thứ|everything|all).*(?:lạnh|cold|detach)",
    ],
    "hypervigilance": [
        r"(?:đọc|read).*(?:cảm xúc|emotion|mood|tâm trạng).*(?:người|people|others)",
        r"(?:nhạy cảm|sensitive|alert).*(?:thay đổi|change|shift).*(?:giọng|tone|mood|thái độ)",
        r"(?:luôn|always).*(?:quan sát|observe|watch|đề phòng|guard)",
        r"(?:cảnh giác|vigilant|wary).*(?:dấu hiệu|sign|signal|cue)",
    ],
    "complex-ptsd": [
        r"(?:flashback|hồi tưởng|ám ảnh).*(?:lặp lại|recurring|repeated)",
        r"(?:trauma|chấn thương|sang chấn).*(?:phức tạp|complex|nhiều lần|repeated)",
        r"(?:không thể|can't|cannot).*(?:tin tưởng|trust).*(?:ai|anyone|người)",
        r"(?:trống rỗng|emptiness|void|vô nghĩa).*(?:bên trong|inside|internal)",
    ],
    "suicidal-ideation": [
        r"(?:muốn|want).*(?:biến mất|disappear|vanish|không tồn tại|not exist)",
        r"(?:không|no).*(?:lý do|reason).*(?:sống|live|continue|tiếp tục)",
        r"(?:mọi người|everyone).*(?:tốt hơn|better off).*(?:không có|without).*(?:tôi|me|mình)",
        r"(?:kết thúc|end).*(?:tất cả|everything|all|hết)",
        r"(?:mệt mỏi|tired|exhausted).*(?:sống|living|cuộc sống|life|tồn tại|existing)",
        r"(?:buông|let go|give up).*(?:xuôi|altogether|hết)",
    ],
    "existential-void": [
        r"(?:vô nghĩa|meaningless|pointless|vô ích)",
        r"(?:trống rỗng|empty|hollow|void).*(?:bên trong|inside|nội tâm)",
        r"(?:tại sao|why).*(?:sống|live|exist|tồn tại)",
        r"(?:không|no).*(?:mục đích|purpose|meaning|ý nghĩa)",
    ],
    "somatization": [
        r"(?:đau|pain|ache).*(?:không|no|without).*(?:nguyên nhân|cause|reason).*(?:thể chất|physical)",
        r"(?:cơ thể|body).*(?:phản ứng|react|respond).*(?:stress|căng thẳng|áp lực)",
        r"(?:mất ngủ|insomnia|sleepless).*(?:kéo dài|prolonged|chronic)",
        r"(?:kiệt sức|exhaustion|burnout).*(?:thể chất|physical|body)",
    ],
    "flight-response": [
        r"(?:chạy trốn|flee|escape|run away).*(?:thay vì|instead of|rather than)",
        r"(?:tránh|avoid|dodge).*(?:đối mặt|confront|face|deal with)",
        r"(?:bỏ đi|leave|walk away).*(?:khi|when).*(?:khó|difficult|conflict|xung đột)",
    ],
    "repetition-compulsion": [
        r"(?:lặp lại|repeat|pattern).*(?:mối quan hệ|relationship|hành vi|behavior)",
        r"(?:giống hệt|identical|same).*(?:lần trước|before|previous|past)",
        r"(?:vòng lặp|cycle|loop).*(?:đau|pain|toxic|tiêu cực)",
    ],
    "false-self": [
        r"(?:giấu|hide|mask|che).*(?:con người thật|true self|real self|bản thân thật)",
        r"(?:diễn|perform|act|giả).*(?:trước mặt|in front of|cho|for).*(?:người|people|others)",
        r"(?:persona|mặt nạ|mask|facade).*(?:khác|different).*(?:bên trong|inside|thật|real)",
    ],
    "covert-contracts": [
        r"(?:kỳ vọng ngầm|unspoken expectation|implicit expect)",
        r"(?:cho|give).*(?:nhưng|but).*(?:mong|hope|expect).*(?:đáp lại|reciprocate|return)",
        r"(?:thất vọng|disappointed).*(?:vì|because).*(?:không|didn't).*(?:nhận lại|receive back)",
    ],
    "secure-base": [
        r"(?:bến đỗ|safe haven|safe place|nơi an toàn)",
        r"(?:quay về|return to|come back).*(?:khi|when).*(?:khó|difficult|scared|sợ)",
        r"(?:tin tưởng|trust).*(?:luôn|always).*(?:ở đó|be there|present|có mặt)",
    ],
    "individuation": [
        r"(?:tách|separate|detach).*(?:khỏi|from).*(?:gia đình|family|mentor|người)",
        r"(?:tự|self|own).*(?:quyết định|decide|choose).*(?:không|without).*(?:phụ thuộc|depend)",
        r"(?:trưởng thành|mature|grow).*(?:ra khỏi|beyond|out of).*(?:bóng|shadow|influence)",
    ],
}

COMPILED_CLUSTERS: dict[str, list[re.Pattern]] = {
    slug: [re.compile(p, re.IGNORECASE) for p in patterns]
    for slug, patterns in BEHAVIORAL_CLUSTERS.items()
}

CRISIS_ADJACENT_SLUGS = [
    "suicidal-ideation", "existential-void", "complex-ptsd",
    "somatization", "flight-response",
]


def scan_file_for_behavioral_clusters(
    filepath: Path,
    slugs: Optional[list[str]] = None,
) -> list[dict]:
    """Scan file for behavioral cluster patterns.

    Args:
        filepath: File to scan
        slugs: If provided, only scan these theory slugs. None = scan all.

    Returns: list of {line, cluster_slug, pattern, context, source}
    """
    results = []
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return results

    target_clusters = (
        {s: COMPILED_CLUSTERS[s] for s in slugs if s in COMPILED_CLUSTERS}
        if slugs
        else COMPILED_CLUSTERS
    )

    for i, line_text in enumerate(lines, 1):
        for slug, patterns in target_clusters.items():
            for pat in patterns:
                match = pat.search(line_text)
                if match:
                    ctx_start = max(0, match.start() - 40)
                    ctx_end = min(len(line_text), match.end() + 40)
                    results.append({
                        "line": i,
                        "cluster_slug": slug,
                        "pattern": pat.pattern,
                        "context": line_text[ctx_start:ctx_end].strip(),
                        "source": "behavioral",
                    })
                    break
    return results


def get_clusters_for_theory(slug: str) -> list[str]:
    """Return raw pattern strings for a given theory slug."""
    return BEHAVIORAL_CLUSTERS.get(slug, [])


def get_all_slugs() -> list[str]:
    """Return all theory slugs with behavioral clusters defined."""
    return list(BEHAVIORAL_CLUSTERS.keys())


# ============================================================
# Phase 2: LLM Behavioral Description Catalog
# Plain-text descriptions for LLM semantic matching.
# NOT regex — these are prompts for LLM to evaluate.
# ============================================================

BEHAVIORAL_DESCRIPTIONS: dict[str, dict[str, str]] = {
    "savior-complex": {
        "vi": "Người luôn cảm thấy có trách nhiệm cứu/giúp người khác, hy sinh bản thân quá mức, không thể ngồi yên khi thấy ai khó khăn, gánh trách nhiệm không phải của mình, lo cho người khác hơn lo cho mình.",
        "en": "Compulsive need to rescue/help others, excessive self-sacrifice, inability to stand by when others struggle, taking on responsibilities that aren't theirs, caring for others more than self.",
    },
    "intellectualization": {
        "vi": "Biến mọi cảm xúc thành phân tích logic, dùng data/bảng tính thay cho cảm nhận, nói về nỗi đau bằng giọng khách quan lạnh lùng, tránh chạm vào cảm xúc thật bằng cách tư duy hệ thống.",
        "en": "Converting emotions into logical analysis, using data/spreadsheets instead of feelings, discussing pain in detached objective tone, avoiding real emotions through systematic thinking.",
    },
    "hypervigilance": {
        "vi": "Đọc cảm xúc người khác cực nhanh, nhạy cảm với thay đổi giọng nói/thái độ, luôn quan sát xung quanh, đề phòng trước dấu hiệu nguy hiểm, phát triển từ môi trường gia đình bất ổn.",
        "en": "Reading others' emotions rapidly, sensitivity to tone/attitude shifts, constant environmental scanning, anticipating danger signs, developed from unstable family environment.",
    },
    "complex-ptsd": {
        "vi": "Flashback lặp lại, không thể tin tưởng ai, cảm giác trống rỗng bên trong, khó điều chỉnh cảm xúc, cảm giác bản thân bị hỏng/khác biệt, từ sang chấn kéo dài hoặc lặp lại.",
        "en": "Recurring flashbacks, inability to trust, inner emptiness, emotional dysregulation, feeling fundamentally broken/different, from prolonged or repeated trauma.",
    },
    "suicidal-ideation": {
        "vi": "Muốn biến mất, không muốn tồn tại, cảm thấy mọi người tốt hơn nếu không có mình, muốn kết thúc tất cả, mệt mỏi với việc sống, muốn buông xuôi, cảm giác đời là gánh nặng.",
        "en": "Wanting to disappear, not wanting to exist, feeling others are better off without you, wanting to end everything, tired of living, wanting to give up, life as a burden.",
    },
    "existential-void": {
        "vi": "Cảm giác vô nghĩa, trống rỗng bên trong, không biết tại sao mình sống, không có mục đích, mọi thứ đều vô ích, đặt câu hỏi về ý nghĩa sự tồn tại.",
        "en": "Feeling of meaninglessness, inner emptiness, not knowing why one lives, no purpose, everything is pointless, questioning the meaning of existence.",
    },
    "anchoring": {
        "vi": "Đưa thông tin giá trị cao trước để tạo mốc so sánh, gửi hệ số/thành tích trước khi nói con số cụ thể, tạo ấn tượng đầu tiên định hướng toàn bộ thảo luận sau đó.",
        "en": "Presenting high-value information first to set comparison anchor, showing coefficients/achievements before specific numbers, creating first impressions that steer all subsequent discussion.",
    },
    "loss-aversion": {
        "vi": "Kích hoạt nỗi sợ mất ở đối phương, nhắc đến counter-offer/cạnh tranh, tạo cảm giác khan hiếm, khiến đối phương sợ mất cơ hội hơn là đánh giá khách quan.",
        "en": "Triggering fear of loss in counterpart, mentioning counter-offers/competition, creating scarcity perception, making counterpart fear losing opportunity more than objectively evaluating.",
    },
    "commitment-trap": {
        "vi": "Để đối phương đầu tư dần (thời gian, effort, uy tín) vào deal, mỗi bước nhỏ tăng cam kết, đến khi muốn dừng thì chi phí đảo ngược quá cao, biến người đánh giá thành người bảo vệ deal.",
        "en": "Letting counterpart incrementally invest (time, effort, reputation), each small step increases commitment, reversal cost becomes too high, evaluator becomes deal advocate.",
    },
    "sunk-cost-fallacy": {
        "vi": "Tiếp tục đầu tư vì đã đầu tư trước đó, không thể bỏ phí thời gian/công sức đã bỏ ra, kéo dài process đủ lâu để tích lũy chi phí chìm, tâm lý 'đã đến đây rồi thì phải hoàn thành'.",
        "en": "Continuing investment because of prior investment, can't waste time/effort already spent, prolonging process to accumulate sunk costs, 'we've come this far' mentality.",
    },
    "fomo": {
        "vi": "Sợ bỏ lỡ cơ hội, cảm giác khan hiếm, người khác cũng muốn giữ/tuyển người này, phải quyết định nhanh nếu không sẽ mất, urgency không có deadline thật.",
        "en": "Fear of missing opportunity, scarcity perception, others also want to retain/recruit this person, must decide quickly or lose out, urgency without real deadline.",
    },
    "face-saving": {
        "vi": "Nói giảm/nói vòng để bảo vệ thể diện đối phương, không để ai cảm thấy thua, dùng con số mập mờ thay vì chính xác, giao tiếp gián tiếp qua kênh riêng tư.",
        "en": "Understating/indirect communication to protect others' face, ensuring no one feels they lost, using ambiguous numbers instead of precise ones, communicating through private channels.",
    },
    "emotional-framing": {
        "vi": "Xây dựng persona cụ thể (mệt mỏi, miễn cưỡng, expert bị kéo đi) để điều hướng cảm xúc đối phương, hiển thị cảm xúc có chủ đích thay vì cảm xúc thật.",
        "en": "Constructing specific persona (weary, reluctant, expert being pulled away) to steer counterpart's emotions, displaying intentional emotions instead of real ones.",
    },
    "rapport-engineering": {
        "vi": "Xây dựng mối quan hệ tin tưởng có hệ thống qua các giai đoạn (warmth → similarity → vulnerability → trust lock), biến người đánh giá thành đồng minh.",
        "en": "Systematically building trust relationship through phases (warmth → similarity → vulnerability → trust lock), transforming evaluator into ally.",
    },
    "false-self": {
        "vi": "Che giấu con người thật, diễn vai trước mặt người khác, persona khác hoàn toàn với bên trong, mang mặt nạ phù hợp với từng hoàn cảnh.",
        "en": "Hiding true self, performing for others, persona completely different from inner self, wearing masks appropriate for each situation.",
    },
    "covert-contracts": {
        "vi": "Kỳ vọng ngầm không nói ra khi cho đi, cho nhưng mong được đáp lại, thất vọng khi người khác không nhận ra 'hợp đồng' chưa bao giờ được ký.",
        "en": "Unspoken expectations when giving, giving while expecting reciprocation, disappointment when others don't recognize a 'contract' that was never signed.",
    },
    "repetition-compulsion": {
        "vi": "Lặp lại pattern cũ trong mối quan hệ mới, rơi vào cùng kiểu xung đột/đau khổ, vô thức tái tạo động lực gia đình cũ.",
        "en": "Repeating old patterns in new relationships, falling into same conflict/suffering type, unconsciously recreating old family dynamics.",
    },
    "secure-base": {
        "vi": "Có nơi/người quay về khi khó khăn, tin tưởng ai đó sẽ luôn ở đó, cảm giác an toàn để khám phá thế giới.",
        "en": "Having a place/person to return to when struggling, trusting someone will always be there, feeling safe enough to explore the world.",
    },
    "individuation": {
        "vi": "Tách ra khỏi ảnh hưởng của gia đình/mentor, tự đưa ra quyết định không phụ thuộc, trưởng thành ra khỏi bóng của người khác.",
        "en": "Separating from family/mentor influence, making independent decisions, growing beyond others' shadow.",
    },
    "somatization": {
        "vi": "Đau cơ thể không có nguyên nhân thể chất, cơ thể phản ứng khi stress, mất ngủ kéo dài, kiệt sức thể chất từ áp lực tâm lý.",
        "en": "Physical pain without physical cause, body reacting to stress, prolonged insomnia, physical exhaustion from psychological pressure.",
    },
    "flight-response": {
        "vi": "Chạy trốn thay vì đối mặt, tránh xung đột, bỏ đi khi khó khăn, rút lui khỏi tình huống căng thẳng.",
        "en": "Fleeing instead of confronting, avoiding conflict, leaving when things get hard, withdrawing from tense situations.",
    },
}


def extract_sections_for_llm_review(
    filepath: Path,
    section_size: int = 5,
) -> list[dict]:
    """Extract text sections from a file for LLM heuristic review.

    Returns chunks of {section_start, section_end, text} for LLM to evaluate
    against BEHAVIORAL_DESCRIPTIONS catalog.
    """
    try:
        lines = filepath.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return []

    sections = []
    for i in range(0, len(lines), section_size):
        chunk = lines[i:i + section_size]
        text = "\n".join(chunk).strip()
        if text and len(text) > 20:
            sections.append({
                "file": filepath.name,
                "section_start": i + 1,
                "section_end": min(i + section_size, len(lines)),
                "text": text,
            })
    return sections


def build_llm_prompt_for_deep_scan(
    sections: list[dict],
    slugs: Optional[list[str]] = None,
) -> str:
    """Build a structured prompt for LLM to match sections against behavioral descriptions.

    Returns a prompt string that skills can inject into their LLM evaluation step.
    """
    target_descs = (
        {s: BEHAVIORAL_DESCRIPTIONS[s] for s in slugs if s in BEHAVIORAL_DESCRIPTIONS}
        if slugs
        else BEHAVIORAL_DESCRIPTIONS
    )

    catalog_lines = []
    for slug, desc in target_descs.items():
        catalog_lines.append(f"- **{slug}**: {desc['vi']}")

    sections_text = []
    for sec in sections[:40]:
        sections_text.append(
            f"[{sec['file']}:{sec['section_start']}-{sec['section_end']}]\n{sec['text']}"
        )

    return (
        "## Behavioral Theory Catalog\n\n"
        + "\n".join(catalog_lines)
        + "\n\n## Profile Sections to Evaluate\n\n"
        + "\n\n---\n\n".join(sections_text)
        + "\n\n## Instructions\n\n"
        "For each section, identify which behavioral theories are IMPLICITLY described "
        "(behavior matches description but formal term is NOT used). "
        "Output: [{file, line_range, theory_slug, evidence_quote, confidence: high/medium/low}].\n"
        "Skip sections with no implicit matches. Only report medium+ confidence."
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Behavioral cluster scanner")
    parser.add_argument("--test", action="store_true", help="Run self-test")
    parser.add_argument("--file", type=str, help="Scan a specific file")
    parser.add_argument("--slugs", nargs="*", help="Filter to specific theory slugs")
    args = parser.parse_args()

    if args.test:
        test_lines = [
            "Nhân vật A luôn cứu mọi người xung quanh dù họ không nhờ",
            "Anh gửi hệ số thưởng 1.68x trước khi nói lương",
            "Bích sợ mất ứng viên nên chiến đấu nội bộ",
            "Nhân vật A muốn biến mất khỏi cuộc sống",
            "Anh phân tích cảm xúc bằng bảng tính thay cho cảm nhận thật",
            "Tôi thấy trống rỗng bên trong, vô nghĩa",
            "Normal text without any behavioral patterns here.",
        ]
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False, encoding="utf-8") as f:
            f.write("\n".join(test_lines))
            tmp = Path(f.name)
        hits = scan_file_for_behavioral_clusters(tmp)
        tmp.unlink()
        print(f"Self-test: {len(hits)} behavioral hits from {len(test_lines)} lines")
        for h in hits:
            print(f"  L{h['line']} [{h['cluster_slug']}]: {h['context']}")
        expected_min = 5
        if len(hits) >= expected_min:
            print(f"PASS ({len(hits)} >= {expected_min})")
        else:
            print(f"FAIL ({len(hits)} < {expected_min})")
            exit(1)
    elif args.file:
        hits = scan_file_for_behavioral_clusters(Path(args.file), args.slugs)
        for h in hits:
            print(f"L{h['line']} [{h['cluster_slug']}] {h['context']}")
        print(f"\nTotal: {len(hits)} behavioral hits")
