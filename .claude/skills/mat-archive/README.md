# mat:archive

> Filter and archive processed source materials by applying `processing_status: archived` to matched files. Maintenance operation outside the main pipeline.

## What it does

Scans `docs/materials/` for processed materials matching your filter criteria (character, date, evidence tier, processing status), shows a dry-run preview, and marks matched files as archived. Files are never deleted—only marked with `processing_status: archived`. Runs in safe dry-run mode by default.

## When to use

- **Trigger phrases:** "archive material", "remove evidence", "clean up materials", "archive old sources"
- **Position:** Maintenance operation after Stage 5. Run when you want to declutter the pipeline (e.g., old raw files, low-tier materials, confidential items you no longer need).
- **Workflow:** Specify filters (character, date, tier, status) → review preview → execute archive.

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Limit scope to one character |
| `--before-date YYYY-MM-DD` | Match files with captured_date before this date |
| `--tier <T1-T5>` | Match files with this evidence tier |
| `--status <status>` | Match files with this processing_status |
| `--dry-run` | Preview matches without modifying (default behavior) |

## What it does NOT do

- **Does not delete files.** Archiving only sets `processing_status: archived` in frontmatter. Files remain in `docs/materials/` for audit trail.
- **Does not reverse decisions.** Once archived, a material is marked as out-of-scope. Reversing requires manual frontmatter edit.
- **Does not validate** whether it's safe to archive. You must judge which materials to archive (e.g., don't archive the only evidence for a claim without reviewing consequences).
- **Does not cascade** to other domains. Archiving a material doesn't trigger profile updates. That's a separate decision.

## See also

- **Contract:** [`SKILL.md`](./SKILL.md)
- **Guides:** [`GUIDE-EN.md`](./GUIDE-EN.md) · [`GUIDE-VI.md`](./GUIDE-VI.md)
- **Related:** `mat:loader` (Stage 1–2) · `mat:indexer` (Stage 3–4) · `mat:rescore` (audit CRAAP)

---

## Tiếng Việt

### Tác dụng

Quét `docs/materials/` để tìm các tài liệu được xử lý phù hợp với tiêu chí lọc của bạn (nhân vật, ngày tháng, tầng bằng chứng, trạng thái xử lý), hiển thị bản xem trước chạy khô và đánh dấu các tệp phù hợp là được lưu trữ. Tệp không bao giờ bị xóa — chỉ được đánh dấu bằng `processing_status: archived`. Chạy ở chế độ dry-run an toàn theo mặc định.

### Khi nào sử dụng

- **Cụm từ kích hoạt:** "archive material", "remove evidence", "clean up materials", "archive old sources"
- **Vị trí:** Hoạt động bảo trì sau giai đoạn 5. Chạy khi bạn muốn dọn dẹp quy trình (ví dụ: các tệp thô cũ, tài liệu tầng thấp, các mục bảo mật bạn không còn cần).
- **Quy trình:** Chỉ định bộ lọc (nhân vật, ngày tháng, tầng, trạng thái) → xem lại bản xem trước → thực hiện lưu trữ.

### Không làm gì

- **Không xóa tệp.** Lưu trữ chỉ đặt `processing_status: archived` trong siêu dữ liệu. Tệp vẫn ở trong `docs/materials/` để theo dõi.
- **Không đảo ngược quyết định.** Sau khi lưu trữ, một tài liệu được đánh dấu là ngoài phạm vi. Đảo ngược yêu cầu chỉnh sửa siêu dữ liệu thủ công.
- **Không xác thực** có an toàn khi lưu trữ hay không. Bạn phải đánh giá tài liệu nào sẽ lưu trữ (ví dụ: đừng lưu trữ bằng chứng duy nhất cho một tuyên bố mà không xem xét các hậu quả).
- **Không tầng truyền** đến các miền khác. Lưu trữ tài liệu không kích hoạt cập nhật hồ sơ. Đó là một quyết định riêng biệt.
