"""Generate a reference file template with mandatory schema fields for psy:ref-create."""
import argparse
import sys


VALID_DOMAINS = [
    "personality", "developmental", "attachment", "trauma", "defense-mechanisms",
    "cognitive", "behavioral", "psychodynamic", "neuropsychology", "social",
    "cultural", "clinical", "positive-psychology", "family-systems",
]


def generate_template(theory_name: str, domain: str = "clinical", author: str = "") -> str:
    """Generate reference markdown with mandatory schema fields."""
    # Vietnamese house style: heading-validated per Rule 10 (REFERENCE_REQUIRED_SECTIONS =
    # Định nghĩa · Nguồn gốc · Cơ chế · Case Study). No YAML frontmatter — the live corpus
    # starts at the H1 title. `domain` is kept as a CLI hint only (placed in the TL;DR comment).
    citation = author or "Tác giả (Năm). *Tựa đề*. Nhà xuất bản."

    return f"""# {theory_name}

> **Định nghĩa ngắn (TL;DR)**: <một câu cô đọng nắm bắt cốt lõi lý thuyết> _(domain: {domain})_.

## 1. Định nghĩa (Definition)

- <Định nghĩa rõ ràng lý thuyết và mức liên quan tới việc lập hồ sơ nhân vật>.
- **Nguồn trích dẫn (Mandatory)**: {citation}

## 2. Nguồn gốc (Origin)

- <Lý thuyết phát sinh từ đâu / điều kiện hình thành>.

## 3. Cơ chế (Mechanism)

- **<Cơ chế 1>**: <mô tả vận hành>.
- **<Cơ chế 2>**: <mô tả vận hành>.

## 4. Case Study áp dụng vào Dự án

### <Tên nhân vật>

- **Bối cảnh / Triggers**: <tình huống kích hoạt, kèm evidence>.
- **Biểu hiện thực tế**: <hành vi quan sát được>.
- **Phân tích lâm sàng**: <diễn giải qua lăng kính lý thuyết này>.

## 5. Liên kết (Cross-References)

- [<Reference liên quan>](./<slug>.md) — <quan hệ>.
"""


def main():
    parser = argparse.ArgumentParser(description="Generate reference file template")
    parser.add_argument("theory", help="Theory name (e.g., 'Bowlby Attachment Theory')")
    parser.add_argument("--domain", "-d", default="clinical", choices=VALID_DOMAINS, help="Psychology domain")
    parser.add_argument("--author", "-a", default="", help="Primary author name")
    args = parser.parse_args()

    print(generate_template(args.theory, args.domain, args.author))


if __name__ == "__main__":
    main()
