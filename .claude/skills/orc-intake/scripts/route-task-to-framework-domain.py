"""Route task description to framework domain for orc:intake.

Hybrid approach: keyword pre-filter for fast deterministic routing,
with AMBIGUOUS fallback when confidence is low so LLM makes final decision.
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

CONFIDENCE_THRESHOLD = 0.5

# ADVISORY routing only — keyword sets score which DOMAIN a task belongs to; the per-domain
# `skills` lists are ILLUSTRATIVE entry points, NOT an exhaustive catalog (the LLM picks the
# final skill from the live catalog after this gathers a domain suggestion). Deliberately not
# generated from the skill dirs: this is a heuristic router, not a source of truth for which
# skills exist (see com:skill-stocktake / orc:skill-stocktake for the authoritative catalog).
DOMAIN_KEYWORDS = {
    "MAT": {
        "keywords": [
            "material", "ingest", "load", "import", "chat log", "transcript",
            "source", "evidence", "craap", "tier", "frontmatter", "raw",
            "archive", "rescore", "stale", "duplicate", "process",
            "news article", "interview", "session notes", "conversation log",
            "tài liệu", "nguồn", "nhập", "nạp", "log", "lưu trữ",
            "bản ghi", "phỏng vấn", "buổi",
        ],
        "skills": ["mat:loader", "mat:indexer", "mat:archive", "mat:rescore"],
    },
    "PSY": {
        "keywords": [
            "profile", "psychology", "formulation", "defense", "attachment",
            "archetype", "diagnostic", "trauma", "wound", "validate",
            "crossref", "reference", "clinical", "5p",
            "propagate", "cascade", "timeline", "health check",
            "completeness", "compare", "comparison", "orphan",
            "crisis", "risk", "dsm", "icd", "suicidal", "ideation",
            "symptom", "sleeping", "withdrew", "not eating",
            "arc", "growth", "trajectory", "track",
            "twist", "falsehood", "retcon", "revelation", "contradiction",
            "compress", "lite", "nén",
            "create reference", "new theory",
            "scan", "coverage", "mapping",
            "milestone", "update profile", "relationship", "sworn",
            "event", "happened", "says", "conflict",
            "family", "inheritance", "dispute",
            "khủng hoảng", "quỹ đạo", "bẻ lái",
            "tạo tài liệu", "rà soát",
            "hồ sơ", "tâm lý", "phân tích", "đánh giá", "so sánh",
        ],
        "skills": [
            "psy:crossref", "psy:ref-audit", "psy:wave", "psy:hypothesis",
            "psy:propagate", "psy:timeline-sync", "psy:health-check",
            "psy:profile-compare", "psy:ref-maintain",
            "psy:crisis-assess", "psy:arc-tracker", "psy:narrative-twist",
            "psy:profile-lite", "psy:ref-create", "psy:ref-scan",
        ],
    },
    "CRE": {
        "keywords": [
            "post", "content", "write", "create", "draft", "publish",
            "facebook", "instagram", "tiktok", "linkedin", "blog",
            "voice", "privacy", "repurpose", "media",
            "prompt", "strengthen", "leverage",
            "adapt", "cross-platform", "letter", "article",
            "campaign", "series", "trilogy",
            "tăng cường", "chuyển đổi",
            "viết", "bài", "nội dung", "đăng", "sáng tạo",
        ],
        "skills": [
            "cre:post-writer", "cre:voice-audit", "cre:privacy-guard",
            "cre:exploring", "cre:prompt-leverage", "cre:repurpose",
        ],
    },
    "GRO": {
        "keywords": [
            "career", "competency", "learning profile", "mentoring",
            "career forecast", "skill inventory", "career path",
            "career trajectory", "professional development",
            "nghề nghiệp", "năng lực", "hướng nghiệp", "phát triển",
            "kỹ năng", "mentor", "sự nghiệp",
        ],
        "skills": [
            "gro:career-path", "gro:competency-map", "gro:learning-profile",
            "gro:mentoring-track", "gro:career-forecast",
        ],
    },
    "COM": {
        "keywords": [
            "rule", "git", "commit", "push", "config", "schema",
            "validate", "standard", "convention",
            "quy tắc", "chuẩn",
        ],
        "skills": ["com:rules", "com:git"],
    },
}

# Weighted phrases: multi-word patterns score higher for disambiguation
DOMAIN_PHRASES = {
    "MAT": [
        ("ingest transcript", 3), ("new transcript", 3), ("process material", 3),
        ("chat log", 2), ("session notes", 2), ("evidence tier", 2),
        ("craap score", 3), ("duplicate material", 2), ("news article", 2),
    ],
    "PSY": [
        ("update profile", 3), ("psychological formulation", 3),
        ("attachment style", 3), ("defense mechanism", 3),
        ("timeline entry", 2), ("sworn brother", 3),
        ("cross character", 2), ("growth edge", 2),
        ("crisis protocol", 3), ("risk level", 2),
        ("suicidal ideation", 3), ("end it all", 3), ("self harm", 3),
        ("not eating", 2), ("withdrew from", 2), ("wanting to die", 3),
        ("narrative twist", 3), ("revealed falsehood", 3),
        ("partial truth", 2), ("family conflict", 2),
        ("date discrepancy", 2), ("timeline conflict", 2),
        ("profile section", 2), ("therapy breakthrough", 3),
        ("all affected", 2), ("propagation target", 2),
    ],
    "CRE": [
        ("facebook post", 3), ("linkedin article", 3), ("blog series", 3),
        ("personal letter", 2), ("social media campaign", 3),
        ("cross platform", 2), ("voice consistency", 2),
        ("write a post", 3), ("create content", 2),
    ],
    "GRO": [
        ("career path", 3), ("career analysis", 3), ("competency assessment", 3),
        ("learning profile", 3), ("career forecast", 3), ("mentoring session", 3),
        ("professional growth", 2), ("skill inventory", 2),
    ],
    "COM": [
        ("git commit", 2), ("coding standard", 2),
    ],
}


def route_task(description: str) -> dict:
    """Route task to domain using keyword + phrase matching with confidence."""
    desc_lower = description.lower()
    scores = {}

    for domain, info in DOMAIN_KEYWORDS.items():
        score = 0
        matched = []
        for kw in info["keywords"]:
            if kw in desc_lower:
                score += 1
                matched.append(kw)

        for phrase, weight in DOMAIN_PHRASES.get(domain, []):
            if phrase in desc_lower:
                score += weight
                matched.append(f"[phrase]{phrase}")

        scores[domain] = {"score": score, "matched": matched, "skills": info["skills"]}

    best_domain = max(scores, key=lambda d: scores[d]["score"])
    best_score = scores[best_domain]["score"]
    second_scores = sorted(
        [s["score"] for d, s in scores.items() if d != best_domain], reverse=True
    )
    second_best = second_scores[0] if second_scores else 0

    # Confidence: ratio of best to (best + second), with phrase bonus
    if best_score == 0:
        confidence = 0.0
    elif second_best == 0:
        confidence = min(best_score / 2.0, 1.0)
    else:
        confidence = round(best_score / (best_score + second_best), 2)

    is_ambiguous = confidence < CONFIDENCE_THRESHOLD and best_score > 0

    # Top 2 suggestions when ambiguous
    sorted_domains = sorted(scores.keys(), key=lambda d: scores[d]["score"], reverse=True)
    suggestions = []
    for d in sorted_domains[:2]:
        if scores[d]["score"] > 0:
            suggestions.append({"domain": d, "score": scores[d]["score"]})

    result_domain = best_domain if best_score > 0 else "UNKNOWN"
    if is_ambiguous:
        result_domain = "AMBIGUOUS"

    return {
        "task": description,
        "domain": result_domain,
        "confidence": round(confidence, 2),
        "score": best_score,
        "matched_keywords": scores[best_domain]["matched"],
        "suggested_skill": scores[best_domain]["skills"][0] if scores[best_domain]["skills"] else "",
        "all_scores": {d: s["score"] for d, s in scores.items()},
        "suggestions": suggestions,
        "best_domain": best_domain if best_score > 0 else "UNKNOWN",
    }


def main():
    parser = argparse.ArgumentParser(description="Route task to framework domain")
    parser.add_argument("task", nargs="?", help="Task description text")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    if args.task:
        description = args.task
    else:
        description = sys.stdin.read().strip()

    if not description:
        print("Usage: route-task-to-framework-domain.py 'task description'", file=sys.stderr)
        sys.exit(1)

    result = route_task(description)

    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return

    print(f"\n  Task: {result['task'][:80]}")
    print(f"  Domain: {result['domain']}")
    print(f"  Confidence: {result['confidence']:.0%}")
    if result["domain"] == "AMBIGUOUS":
        print(f"  ⚠ AMBIGUOUS — LLM should decide. Suggestions: {result['suggestions']}")
    print(f"  Best domain: {result['best_domain']}")
    print(f"  Suggested skill: {result['suggested_skill']}")
    print(f"  Matched: {', '.join(result['matched_keywords'])}")
    print(f"  All scores: {result['all_scores']}")


if __name__ == "__main__":
    main()
