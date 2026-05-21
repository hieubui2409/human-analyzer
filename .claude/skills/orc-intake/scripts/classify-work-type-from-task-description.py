#!/usr/bin/env python3
"""Extract signals from a task description for LLM-based work type classification.

This script GATHERS deterministic signals only. It does NOT classify or recommend routes.
The LLM reads these signals and makes the classification decision.
"""
import argparse
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'scripts'))
from platform_lib.paths import ALL_CHARS, CHAR_DISPLAY
from platform_lib.formatters import print_json

ACTION_KEYWORDS = {
    "write": ["write", "draft", "create post", "compose", "viết", "tạo bài", "soạn"],
    "update": ["update", "edit", "revise", "modify", "cập nhật", "sửa", "chỉnh"],
    "create": ["create", "add", "new", "tạo mới", "thêm", "build"],
    "research": ["research", "analyze", "investigate", "study", "nghiên cứu", "phân tích", "tìm hiểu"],
    "fix": ["fix", "debug", "repair", "sửa lỗi", "patch"],
    "review": ["review", "audit", "check", "validate", "xem xét", "kiểm tra", "verify"],
    "plan": ["plan", "design", "architect", "lên kế hoạch", "outline"],
    "ingest": ["ingest", "import", "load", "nhập", "extract"],
    "explain": ["explain", "giải thích", "what is", "how does", "mô tả"],
    "delete": ["delete", "remove", "xóa", "bỏ"],
    "compare": ["compare", "diff", "so sánh", "contrast"],
    "publish": ["publish", "deploy", "release", "đăng", "xuất bản"],
}

OBJECT_KEYWORDS = {
    "post": ["post", "content", "caption", "bài viết", "bài đăng", "script", "nội dung"],
    "profile": ["profile", "character", "hồ sơ", "nhân vật", "soul", "darkness",
                 "light", "identity", "characteristic", "relationships", "milestones",
                 "achievements", "index.md", "writing-voice", "timeline"],
    "arc": ["arc", "growth", "trajectory", "hành trình", "storyline", "narrative", "transformation"],
    "theory": ["theory", "reference", "clinical", "lý thuyết", "ref ", "refs",
               "ref-create", "psychology", "tâm lý", "clinical term"],
    "material": ["material", "transcript", "letter", "source", "tài liệu", "thư",
                 "nhật ký", "phỏng vấn", "log-", "conversation", "chat"],
    "plan": ["plan", "phase", "kế hoạch", "roadmap"],
    "audit": ["audit", "validate", "consistency", "cross-check", "kiểm tra", "gap"],
    "crisis": ["crisis", "risk", "suicide", "self-harm", "khủng hoảng", "tự hại"],
    "privacy": ["privacy", "confidential", "real name", "tên thật", "bảo mật"],
    "voice": ["voice", "tone", "giọng", "writing style"],
}

PLATFORMS = ["facebook", "linkedin", "instagram", "tiktok", "youtube", "twitter", "blog"]

URGENCY_MARKERS = ["urgent", "asap", "now", "immediately", "gấp", "ngay", "khẩn",
                    "deadline", "today", "tonight", "hôm nay", "tối nay"]

MULTI_STEP_MARKERS = ["then", "after that", "and also", "rồi", "sau đó", "đồng thời",
                       "step 1", "step 2", "first", "second", "next"]

CHARACTER_ALIASES = {
    "hiếu": "character-a", "hieu": "character-a", "Nhân vật ẩn danh": "character-a",
    "hòa": "character-b", "hoa": "character-b",
    "chiến": "character-c", "chien": "character-c", "Nhân vật ẩn danh": "character-c",
}


def extract_matched(text: str, keyword_map: dict) -> list[dict]:
    text_lower = text.lower()
    matches = []
    for category, keywords in keyword_map.items():
        hits = [k for k in keywords if k in text_lower]
        if hits:
            matches.append({"category": category, "matched_keywords": hits})
    return matches


def extract_characters(text: str) -> list[str]:
    text_lower = text.lower()
    found = []
    for slug in ALL_CHARS:
        display = CHAR_DISPLAY[slug].lower()
        short = slug.split("-")[-1]
        if display in text_lower or short in text_lower:
            if slug not in found:
                found.append(slug)
    for alias, slug in CHARACTER_ALIASES.items():
        if alias in text_lower and slug not in found:
            found.append(slug)
    return found


def extract_platforms(text: str) -> list[str]:
    text_lower = text.lower()
    return [p for p in PLATFORMS if p in text_lower]


def extract_file_references(text: str) -> list[str]:
    return re.findall(r'[\w\-/]+\.(?:md|txt|json|py|sh)', text)


def extract_skill_mentions(text: str) -> list[str]:
    return re.findall(r'lucas:\w[\w-]*', text)


def extract_urgency(text: str) -> list[str]:
    text_lower = text.lower()
    return [m for m in URGENCY_MARKERS if m in text_lower]


def extract_multi_step(text: str) -> list[str]:
    text_lower = text.lower()
    return [m for m in MULTI_STEP_MARKERS if m in text_lower]


def count_sentences(text: str) -> int:
    return len(re.split(r'[.!?।\n]+', text.strip()))


def main():
    parser = argparse.ArgumentParser(
        description="Extract signals from task description (gathering only, no classification)")
    parser.add_argument("--task", required=True, help="Task description text")
    args = parser.parse_args()

    task = args.task
    signals = {
        "task": task,
        "actions": extract_matched(task, ACTION_KEYWORDS),
        "objects": extract_matched(task, OBJECT_KEYWORDS),
        "characters": extract_characters(task),
        "platforms": extract_platforms(task),
        "file_references": extract_file_references(task),
        "skill_mentions": extract_skill_mentions(task),
        "urgency_markers": extract_urgency(task),
        "multi_step_markers": extract_multi_step(task),
        "word_count": len(task.split()),
        "sentence_count": count_sentences(task),
        "has_question_mark": "?" in task,
        "has_vietnamese": bool(re.search(r'[àáảãạăắằẳẵặâấầẩẫậèéẻẽẹêếềểễệìíỉĩịòóỏõọôốồổỗộơớờởỡợùúủũụưứừửữựỳýỷỹỵđ]', task)),
        "char_count_mentioned": len(extract_characters(task)),
    }
    print_json(signals)


if __name__ == "__main__":
    main()
