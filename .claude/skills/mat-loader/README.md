# mat:loader

> Ingest, classify, and normalize source materials into `docs/materials/` with MAT-compliant frontmatter (Stages 1–2 of the 5-stage pipeline).

## What it does

Receives raw source files, detects document type and character, assigns evidence tier (T1–T5) and CRAAP quality score (1–25), injects MAT frontmatter, and moves files to the materials directory. Materials must be **loaded and classified before indexing or analysis**.

## When to use

- **Trigger phrases:** "load materials", "ingest material", "new source", "mat load"
- **Position:** First stage of MAT pipeline. Run before `mat:indexer` or any psychological analysis.
- **Workflow:** User provides raw source → mat:loader normalizes → output ready for Stage 3 validation.

## Flags

| Flag | Effect |
|------|--------|
| `--list` | Inventory all materials per character with processing status (default) |
| `--character <name>` | List + summarize one character's materials |
| `--file <path>` | Load and summarize specific file |
| `--ingest <path>` | Full MAT pipeline Stages 1–2: classify, CRAAP score, inject frontmatter |
| `--extract <topic>` | Search materials for specific topic or fact |
| `--new` | Show materials added since last session |
| `--status` | Pipeline status breakdown across all materials |

## What it does NOT do

- **Does not validate** materials against profiles (that is mat:indexer's job — Rule 11).
- **Does not emit events** to trigger PSY analysis. Integration decision is LLM-driven via mat:indexer + orc:event-log (Rule 12).
- **Does not modify** profile files or reference library — domain-scoped to `docs/materials/` only.
- **Does not re-score** already-processed materials unless invoked with `--ingest` on a new file.

## See also

- **Contract:** [`SKILL.md`](./SKILL.md)
- **Guides:** [`GUIDE-EN.md`](./GUIDE-EN.md) · [`GUIDE-VI.md`](./GUIDE-VI.md)
- **Related:** `mat:indexer` (Stage 3–4) · `mat:rescore` (audit CRAAP) · `docs/rules/11-mat-pipeline.md`

---

## Tiếng Việt

### Tác dụng

Tiếp nhận tệp nguồn thô, phát hiện loại tài liệu và nhân vật, gán tầng bằng chứng (T1–T5) và điểm CRAAP (1–25), tiêm metadata MAT, và di chuyển tệp đến thư mục tài liệu. Các tài liệu phải được **tải và phân loại trước khi lập chỉ mục hoặc phân tích**.

### Khi nào sử dụng

- **Cụm từ kích hoạt:** "load materials", "ingest material", "new source", "mat load"
- **Vị trí:** Giai đoạn đầu tiên của quy trình MAT. Chạy trước `mat:indexer` hoặc bất kỳ phân tích tâm lý nào.
- **Quy trình:** Người dùng cung cấp nguồn thô → mat:loader chuẩn hóa → đầu ra sẵn sàng cho giai đoạn 3.

### Không làm gì

- **Không xác thực** tài liệu so với hồ sơ (đó là công việc của mat:indexer — Quy tắc 11).
- **Không phát hành sự kiện** để kích hoạt phân tích PSY. Quyết định tích hợp được điều khiển bởi LLM qua mat:indexer + orc:event-log (Quy tắc 12).
- **Không sửa đổi** tệp hồ sơ hoặc thư viện tham khảo — phạm vi miền chỉ `docs/materials/`.
