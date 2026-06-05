# cre:privacy-guard — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã viết một bài đăng về hành trình hướng dẫn của Nhân vật A, nhưng trước khi bạn công bố, bạn muốn chắc chắn rằng bạn không vô tình rò rỉ tên thật của ai đó, chẩn đoán lâm sàn hoặc chi tiết gia đình bảo mật. Kỹ năng này quét bài đăng của bạn để tìm các thẻ quyền riêng tư (`[CONFIDENTIAL: Nhân vật B]`, `[PRIVATE]`), tên bị hạn chế, các thuật ngữ lâm sàn thô (mã DSM, mã ICD) và PII (số điện thoại, email). Nó xuất ra báo cáo vi phạm sạch sẽ: cái gì rò rỉ, ở đâu, mức độ nghiêm trọng. Bạn sửa chữa, chạy lại, xong.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Bốn lớp quét:**

1. **Phát hiện thẻ:** Grep cho các đánh dấu quyền riêng tư (`[PRIVATE]`, `[CONFIDENTIAL: {person}]`, `[ANONYMIZE]`, `[UNCERTAIN]`, `[DISPUTED]`). Mức độ nghiêm trọng tăng từ INFO lên CRITICAL.

2. **Phát hiện tên:** Tải tất cả các tên bị hạn chế từ siêu dữ liệu hồ sơ (identity/core.md, relationships/family.md, các tệp xuyên nhân vật, traumas.md). Grep tài sản cho những cái tên đó. Trùng khớp = CRITICAL.

3. **Phát hiện thuật ngữ lâm sàn (Lớp 1 — rõ ràng):** Tải ánh xạ lâm sàn → dân gian từ Quy tắc 02. Grep cho các mã DSM/ICD thô và các thuật ngữ lâm sàn chính thức. Trùng khớp = cao/MEDIUM theo thuật ngữ.

4. **Phát hiện thuật ngữ lâm sàn (Lớp 2 — ẩn):** LLM đọc các đoạn được gắn cờ để phát hiện ngôn ngữ lâm sàn ẩn (không phải các thuật ngữ chính thức, nhưng "quá lâm sàn cho phương tiện truyền thông xã hội"). Gợi ý paraphrase tự nhiên.

**Đầu ra:** Bảng vi phạm (tệp, dòng, loại, nội dung, mức độ) + bản án pass/fail.

## 3. Đường học tập

**Lần chạy đầu tiên:** Quét tất cả các bài đăng đã công bố:
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-privacy-guard/scripts/scan-for-privacy-violations.py --scan
```
Bạn thấy một bảng: 10 tệp được quét, 2 vi phạm tìm thấy. Dòng 15 trong assets/facebook/260413-post.md: tên "Huyền" (CRITICAL). Sửa bằng cách redact hoặc xóa câu đó.

**Khi bạn phát triển:** Hãy thử `--strict` để zero tolerance (bất kỳ thẻ nào, ngay cả `[UNCERTAIN]`, = THẤT BẠI). Tốt cho các chủ đề nhạy cảm. Chế độ mặc định cho phép `[UNCERTAIN]` trong bản nháp.

**Luồng tiêu chuẩn:** Viết bài → `cre:post-writer` gọi điều này tự động → THẤT BẠI khối; tác giả sửa chữa → chạy lại để xác nhận PASS.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Quét trước khi công bố

> **Bạn:** "Tôi đã viết một bài đăng LinkedIn. Trước khi công bố, hãy kiểm tra xem có rò rỉ không."
>
> **Kỹ năng:** `--file assets/linkedin/260526-post` → quét post.md + post.txt → "✅ Sạch sẽ — an toàn để công bố."
>
> **Bạn:** Sao chép dán post.txt sang LinkedIn.

### Trường hợp sử dụng: Kiểm toán quản lý zero tolerance

> **Bạn:** "Kiểm toán tất cả các bài đăng đã công bố với zero tolerance."
>
> **Kỹ năng:** `--audit --strict` → quét tất cả assets/ + framework dirs → tạo `plans/reports/privacy-audit-{date}.md` + JSONL log.
>
> **Bạn:** Xem xét báo cáo, giải quyết những phát hiện cao/CRITICAL.

### Trường hợp sử dụng: Kiểm tra xuyên khuôn khổ sau khi tiếp nhận tài liệu

> **Bạn:** "Vừa tiếp nhận 5 tài liệu mới. Kiểm tra xem PII có rò rỉ vào bất kỳ tài liệu nào không."
>
> **Kỹ năng:** `--cross-framework` → quét assets/ + profiles/ + materials/ + graph/ → gắn cờ bất kỳ PII không được redact nào.
>
> **Bạn:** Redact tài liệu, chạy lại.

## 5. Những cảnh báo quan trọng

- **CRITICAL luôn thất bại:** Rò rỉ thẻ, tên bị hạn chế, mã chẩn đoán bên ngoài psychology/ = THẤT BẠI không thể đàm phán.
- **MEDIUM/HIGH được gắn cờ, không phải tự động THẤT BẠI:** Các thuật ngữ lâm sàn được phát hiện; tác giả quyết định bối cảnh.
- **Lâm sàn ẩn là kinh nghiệm:** Phát hiện LLM Lớp 2 là cố vấn, không xác định. Tác giả có quyết định cuối cùng.
- **Kiểm toán CHỈ ĐỌC:** Kỹ năng này phát hiện, không bao giờ sửa chữa. Tác giả sở hữu khắc phục.
- **JSONL quản lý:** `--audit` nối vào `.claude/telemetry/privacy-audit.jsonl`. Truy vấn bằng `jq` để báo cáo tuân thủ.

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:post-writer` (gọi điều này tự động ở giai đoạn chất lượng)
- `cre:evidence-scanner` — bổ sung; đây là PII/thẻ; máy quét là cấp độ bằng chứng
- Quy tắc 09 (giao thức bảo mật), Quy tắc 02 (tham chiếu lâm sàn hiển thị không nói)
