# mat:rescore

> Audit CRAAP scores across materials: identify missing, incomplete, or stale scores and flag for re-evaluation. Read-only maintenance operation within Stage 2.

## What it does

Scans `docs/materials/` for materials with missing CRAAP fields, partial scores, calculation errors, or raw processing status. Produces a table of materials needing re-scoring and suggests which files to re-ingest via `mat:loader --ingest`. Never modifies files—pure audit.

## When to use

- **Trigger phrases:** "rescore materials", "re-evaluate CRAAP", "update evidence tiers", "craap check", "fix scores"
- **Position:** Audit step during Stage 2 of pipeline. Run to check quality of loaded materials before Stage 3 validation.
- **Workflow:** Load materials → `mat:rescore` audit → identify gaps → re-run `mat:loader --ingest` on flagged files → re-validate.

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Limit to one character |
| `--missing-only` | Only show files with no craap_score at all |
| `--raw-only` | Only show files with processing_status: raw |
| `--json` | Output as JSON (machine-readable) |

## What it does NOT do

- **Does not rescore files.** It only identifies which files need rescoring. To actually score/re-score, run `mat:loader --ingest <file>`.
- **Does not modify** any material files — read-only audit only.
- **Does not validate** against CRAAP criteria. It just checks for missing or malformed scores; actual scoring is LLM work in mat:loader.
- **Does not recommend** which files to archive or which tiers are "too low". It reports facts; you decide action.

## See also

- **Contract:** [`SKILL.md`](./SKILL.md)
- **Guides:** [`GUIDE-EN.md`](./GUIDE-EN.md) · [`GUIDE-VI.md`](./GUIDE-VI.md)
- **Related:** `mat:loader --ingest` (re-run Stage 1–2 on flagged files) · `mat:loader --status` (pipeline overview) · `.claude/schemas/material-schema.yaml` (CRAAP schema)

---

## Tiếng Việt

### Tác dụng

Quét `docs/materials/` để tìm các tài liệu có các trường CRAAP bị thiếu, điểm không đầy đủ, lỗi tính toán hoặc trạng thái xử lý thô. Tạo bảng các tài liệu cần điểm lại và gợi ý tệp nào cần re-ingest qua `mat:loader --ingest`. Không bao giờ sửa đổi tệp — kiểm toán thuần túy.

### Khi nào sử dụng

- **Cụm từ kích hoạt:** "rescore materials", "re-evaluate CRAAP", "update evidence tiers", "craap check", "fix scores"
- **Vị trí:** Bước kiểm toán trong giai đoạn 2 của quy trình. Chạy để kiểm tra chất lượng tài liệu được tải trước khi xác thực giai đoạn 3.
- **Quy trình:** Tải tài liệu → kiểm toán `mat:rescore` → xác định khoảng trống → chạy lại `mat:loader --ingest` trên tệp được đánh dấu → xác thực lại.

### Không làm gì

- **Không điểm lại tệp.** Nó chỉ xác định tệp nào cần điểm lại. Để thực sự điểm/điểm lại, chạy `mat:loader --ingest <file>`.
- **Không sửa đổi** bất kỳ tệp tài liệu nào — chỉ kiểm toán đọc.
- **Không xác thực** so với tiêu chí CRAAP. Nó chỉ kiểm tra các điểm bị thiếu hoặc dạng sai; điểm thực tế là công việc LLM trong mat:loader.
- **Không khuyến cáo** tệp nào sẽ lưu trữ hoặc tầng nào "quá thấp". Nó báo cáo các sự kiện; bạn quyết định hành động.
