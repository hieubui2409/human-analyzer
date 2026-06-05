# mat:indexer

> Cross-reference materials against profiles, detect contradictions, verify evidence tiers, and track coverage gaps (Stages 3–4 of the 5-stage pipeline). **Integration gate before analysis.**

## What it does

Validates loaded materials by scanning for factual claims, comparing them against existing profile data, and flagging contradictions by severity. Produces a coverage map showing which profile sections lack evidence. After Stage 3 script output, LLM judges whether each material is ready for integration (Stage 4); if yes, emits `MAT.integrated` event to trigger PSY analysis.

## When to use

- **Trigger phrases:** "index materials", "cross-reference", "contradiction check", "validate materials", "mat index"
- **Position:** Runs after `mat:loader` (Stage 1–2). Must complete before materials feed psychology analysis (Rule 11).
- **Workflow:** Loaded materials → Stage 3 validation (detect contradictions, verify tiers) → Stage 4 LLM judgment → emit event or flag for review.

## Flags

| Flag | Effect |
|------|--------|
| `--all` | Full cross-reference for all characters (default) |
| `--character <name>` | Cross-reference one character's materials vs profile |
| `--contradictions` | Show only contradictions (skip coverage/stale) |
| `--coverage` | Evidence coverage gaps per profile section |
| `--stale` | Find materials stuck at raw/extracted for >7 days |

## What it does NOT do

- **Does not auto-integrate** materials. Integration is an LLM judgment step (Stage 4) after reviewing contradictions. Script gathers; LLM judges (Rule 11).
- **Does not emit events automatically.** After Stage 3 script output, the LLM invokes `orc:event-log` to emit `MAT.integrated` or `MAT.contradiction` events (Rule 12).
- **Does not modify profile files** — only flags what profile sections need updating. Reads profiles, never writes to them.
- **Does not delete or archive materials.** That is `mat:archive`'s job. This skill only updates `processing_status` field in frontmatter.

## See also

- **Contract:** [`SKILL.md`](./SKILL.md)
- **Guides:** [`GUIDE-EN.md`](./GUIDE-EN.md) · [`GUIDE-VI.md`](./GUIDE-VI.md)
- **Related:** `mat:loader` (Stage 1–2) · `mat:archive` (archival) · `docs/rules/11-mat-pipeline.md` · `docs/rules/12-orc-orchestration.md`

---

## Tiếng Việt

### Tác dụng

Xác thực tài liệu được tải bằng cách quét để tìm các tuyên bố thực tế, so sánh chúng với dữ liệu hồ sơ hiện có và đánh dấu các mâu thuẫn theo mức độ nghiêm trọng. Tạo bản đồ phạm vi cho thấy những phần hồ sơ nào thiếu bằng chứng. Sau đầu ra kịch bản giai đoạn 3, LLM đánh giá xem liệu mỗi tài liệu có sẵn sàng để tích hợp (giai đoạn 4) hay không; nếu có, phát hành sự kiện `MAT.integrated` để kích hoạt phân tích PSY.

### Khi nào sử dụng

- **Cụm từ kích hoạt:** "index materials", "cross-reference", "contradiction check", "validate materials", "mat index"
- **Vị trí:** Chạy sau `mat:loader` (giai đoạn 1–2). Phải hoàn thành trước khi tài liệu cấp cho phân tích tâm lý (Quy tắc 11).
- **Quy trình:** Tài liệu được tải → xác thực giai đoạn 3 (phát hiện mâu thuẫn, xác minh tầng) → phán xét LLM giai đoạn 4 → phát hành sự kiện hoặc đánh dấu để xem xét.

### Không làm gì

- **Không tự động tích hợp** tài liệu. Tích hợp là bước phán xét LLM (giai đoạn 4) sau khi xem lại các mâu thuẫn. Kịch bản thu thập; LLM phán xét (Quy tắc 11).
- **Không phát hành sự kiện tự động.** Sau đầu ra kịch bản giai đoạn 3, LLM gọi `orc:event-log` để phát hành các sự kiện `MAT.integrated` hoặc `MAT.contradiction` (Quy tắc 12).
- **Không sửa đổi tệp hồ sơ** — chỉ đánh dấu các phần hồ sơ nào cần cập nhật. Đọc hồ sơ, không bao giờ ghi vào chúng.
- **Không xóa hoặc lưu trữ tài liệu.** Đó là công việc của `mat:archive`. Kỹ năng này chỉ cập nhật trường `processing_status` trong siêu dữ liệu.
