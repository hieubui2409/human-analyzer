# cre:evidence-scanner — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã viết một bài đăng: "Việc hướng dẫn của tôi với Nhân vật C đã thay đổi cách tiếp cận rủi ro của anh ấy." Trước khi công bố, bạn muốn biết: Tuyên bố này có được hỗ trợ bằng bằng chứng không? Tôi có vô tình rò rỉ điều gì riêng tư không? Kỹ năng này trích xuất tuyên bố đó, tìm các tài liệu bằng chứng (T1-T5), đánh giá "chuyển đổi hướng dẫn" là PASS (được hỗ trợ bởi ghi chú phiên T1) hoặc CẢNH BÁO (diễn giải tertiary), và gắn cờ bất kỳ thẻ `[CONFIDENTIAL]` nào. Một bản án rõ ràng cho mỗi yêu cầu.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Quy trình ba lớp:**

1. **Trích xuất (xác định):** Kịch bản phân đoạn nội dung thành các yêu cầu nguyên tử (mã thông báo nhận biết VN). Một yêu cầu cho mỗi câu/ý tưởng.
2. **Thu thập (xác định):** Kịch bản thu thập các tài liệu ứng viên bằng cách trùng lặp từ khóa/thực thể, gán cấp độ, phát hiện các thẻ quyền riêng tư. Thu thập quá rộng; dương tính giả dự kiến.
3. **Quyết định (kinh nghiệm):** LLM đọc các ứng viên và quyết định "tài liệu này thực sự hỗ trợ yêu cầu không?" (CiteAudit Reasoner). Hoàn thiện PASS/CẢNH BÁO/THẤT BẠI.

**Chính sách bản án (FAIL-CLOSED):**
- Bằng chứng T1/T2 → PASS
- T3 (tertiary) → CẢNH BÁO (có thể công bố, nhưng gắn cờ để cẩn thận)
- T4/T5 (yếu) → THẤT BẠI (không công bố được nếu không có điều kiện rõ ràng)
- Rò rỉ quyền riêng tư (mã DSM thô, `[CONFIDENTIAL]`, thuật ngữ lâm sàng) → THẤT BẠI
- Không tìm thấy bằng chứng → CẢNH BÁO (không bao giờ PASS im lặng)

**Nguồn chân lý duy nhất:** `evidence_tier_permissions.py` tồn tại một lần; được nhập bởi cả kỹ năng này và `cre:post-writer`. Không trùng lặp.

## 3. Đường học tập

**Lần chạy đầu tiên:** Quét một bài đăng đã công bố:
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-evidence-scanner/scripts/map-claims-to-evidence-tiers.py \
  assets/linkedin/260526-mentorship --json
```
Bạn sẽ thấy một bảng: Yêu cầu | Cấp độ bằng chứng | Bản án. Đọc một yêu cầu CẢNH BÁO — điều đó có nghĩa là tài liệu hỗ trợ là T3 (tertiary, kém đáng tin cậy hơn), nhưng nó vẫn có thể công bố được.

**Khi bạn phát triển:** Hãy thử `--strict` để chuyển đổi tất cả T3 → THẤT BẠI (zero tolerance). Tốt cho các bài báo nghiên cứu; lỏng lẻo cho kể chuyện cá nhân nơi tác giả là nguồn T1.

**Luồng tiêu chuẩn:** `cre:post-writer` gọi điều này tự động ở Giai đoạn 6. Đối với các tài sản đã công bố, bạn có thể chạy lại nó như một cuộc kiểm toán định kỳ.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Xác nhận trước khi công bố

> **Bạn:** "Tôi đã viết một bài đăng LinkedIn về sự thay đổi sự nghiệp của Nhân vật A. Trước khi tôi nhấn công bố, hãy kiểm tra."
>
> **Kỹ năng:** `--asset assets/linkedin/260526-pivot` → trích xuất 8 yêu cầu, ánh xạ tới tài liệu, trả lại bản án. 6 PASS, 2 CẢNH BÁO (diễn giải tertiary của các tín hiệu tăng trưởng).
>
> **Bạn:** Xem xét các yêu cầu CẢNH BÁO, quyết định xem bạn có muốn đủ điều kiện hóa chúng hay viết lại.

### Trường hợp sử dụng: Kiểm toán hàng loạt với chế độ nghiêm ngặt

> **Bạn:** "Tôi cần kiểm toán 10 bài đăng đã công bố. Gắn cờ bất kỳ thứ gì không phải T1-T2."
>
> **Kỹ năng:** Vòng lặp `--asset` trên mỗi thư mục với `--strict`. Bất kỳ T3 → THẤT BẠI, thoát 1.
>
> **Bạn:** Sửa FAILs, chạy lại để xác nhận.

### Trường hợp sử dụng: Phát hiện rò rỉ quyền riêng tư

> **Bạn:** "Trước khi sử dụng lại, hãy kiểm tra xem bài đăng này có rò rỉ gì riêng tư không."
>
> **Kỹ năng:** `--asset` → chạy quét thẻ quyền riêng tư như một phần của kiểm tra bằng chứng. Gắn cờ `[CONFIDENTIAL: Hoà]` trên dòng 12 là THẤT BẠI.
>
> **Bạn:** Xóa thẻ hoặc redact yêu cầu, chạy lại.

## 5. Những cảnh báo quan trọng

- **Thu thập quá rộng cố ý:** Kịch bản thu thập nhiều tài liệu yếu; LLM loại bỏ. Dương tính giả dự kiến — đó là an toàn.
- **T3 là chủ quan:** Bằng chứng tertiary (diễn giải, tổng hợp) sống trong một vùng xám. `--strict` coi nó là không công bố được; chế độ mặc định nói "có thể công bố nhưng gắn cờ nó."
- **Không PASS im lặng:** Nếu không tìm thấy bằng chứng, bản án là CẢNH BÁO, không PASS im lặng. Tác giả phải đưa ra lựa chọn.
- **Quyền riêng tư là nhị phân:** Bất kỳ rò rỉ → THẤT BẠI. Không có đàm phán.
- **Thuật ngữ lâm sàng:** Phát hiện các mã DSM/ICD thô và từ vựng lâm sàng. Quy tắc 02 "hiển thị không nói" có nghĩa là paraphrase, không trích dẫn các thuật ngữ lâm sàng.

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:post-writer` (Giai đoạn 6 delegate)
- `cre:privacy-guard` — bổ sung; đây là cấp độ cưỡng chế mỗi yêu cầu; privacy-guard là PII rộng tài sản
- Quy tắc 09 (bảo mật), Quy tắc 02 (tham chiếu lâm sàng), Quy tắc 14 (bằng chứng CRE)
