# cre:post-writer — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn muốn viết một bài đăng về hành trình hướng dẫn của Nhân vật A trên LinkedIn. Bạn có thể bắt đầu với một màn hình trống, nhưng điều đó chậm và rủi ro. Kỹ năng này hỏi "Ai? Cái gì? Nền tảng? Giọng điệu?" → tải hồ sơ giọng điệu của Nhân vật A → tăng cường prompt của bạn với ràng buộc nền tảng, bảo vệ lâm sàn, và sự kiện hồ sơ → tạo bản nháp → tự động kiểm tra xem nó có hỗ trợ cấp độ bằng chứng, tính nhất quán giọng điệu, và rò rỉ quyền riêng tư không → xuất ra gói 5 tệp sẵn sàng sản xuất. Bạn xem xét, có thể điều chỉnh, sau đó thủ công đăng bài.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Quy trình 7 giai đoạn:**

1. **Cổng giọng điệu cũ:** Kiểm tra xem hồ sơ có đủ tươi để viết không. Nếu tài liệu mới hơn lần PSY cuối cùng làm mới → dữ liệu giọng điệu là cũ; chặn hoặc cảnh báo.
2. **Tải bối cảnh:** Tải hồ sơ nhẹ của nhân vật (5 giây), trích xuất giọng điệu, công thức, mô hình phòng vệ.
3. **Tăng cường prompt:** Áp dụng 5 lớp — khóa giọng điệu, độ chính xác lâm sàn, định dạng nền tảng, tham chiếu chéo hồ sơ, quét nhạy cảm.
4. **Tạo bản nháp:** LLM viết gốc cho nền tảng + loại nội dung (reality/fiction/analysis/letter).
5. **Cổng bắt buộc:** Chạy evidence-scanner (T1-T2 duy nhất?), voice-audit (tone match?), privacy-guard (leak?). THẤT BẠI khối.
6. **Kiểm tra canh chỉnh hồ sơ:** Tính nhất quán thực tế, tâm lý, mối quan hệ vs. hồ sơ. Sửa chữa mâu thuẫn.
7. **Danh sách kiểm tra chất lượng:** Ràng buộc nền tảng được đáp ứng? Nhạy cảm được tôn trọng? Prompt hình ảnh an toàn?

**Đầu ra:** `assets/{platform}/{YYMMDD}-{slug}/` với post.md, post.txt, prompt.txt, image-prompts.txt, README.md.

## 3. Đường học tập

**Lần chạy đầu tiên (tương tác):**
```bash
/cre:post-writer
# Q1: Nhân vật? → Nhân vật A
# Q2: Nền tảng? → LinkedIn
# Q3: Loại? → Reality
# Q4: Chủ đề? → Hướng dẫn Nhân vật C qua sự không chắc chắn
# Q5: Góc nhìn cụ thể? → Cách tính nhất quán xây dựng lòng tin
```
Kỹ năng tạo bản nháp → chạy cổng → xuất ra assets/linkedin/{date}-{slug}/ → bạn xem xét post.txt, có thể điều chỉnh, sau đó thủ công đăng.

**Khi bạn phát triển:** Hãy sử dụng `cre:exploring` trước → khóa quyết định → `cre:post-writer --from-context`. Luồng công việc nhanh hơn, tất cả các quyết định được ghi chép trong CONTEXT.md.

**Luồng tiêu chuẩn:** Khám phá (7 Q&A) → tăng cường prompt (5 lớp tự động) → tạo → cổng → xuất.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Chế độ tương tác

> **Bạn:** `/cre:post-writer`
>
> **Kỹ năng:** Hỏi Q1-Q5, tải bối cảnh, tạo bản nháp, chạy cổng, xuất ra assets/.
>
> **Bạn:** Xem xét post.txt, thủ công sao chép dán sang LinkedIn.

### Trường hợp sử dụng: Từ CONTEXT.md

> **Bạn:** Đã khám phá, khóa quyết định trong CONTEXT.md. Bây giờ: `/cre:post-writer --from-context`
>
> **Kỹ năng:** Bỏ qua Q1-Q5 (đọc CONTEXT.md), đi thẳng tới tạo.
>
> **Bạn:** Nhanh hơn, quyết định đã được ghi chép.

### Trường hợp sử dụng: Chế độ nhanh (bỏ qua tải hồ sơ)

> **Bạn:** `/cre:post-writer Thư gửi Nhân vật C --character hieu --platform blog --type letter --quick`
>
> **Kỹ năng:** Không tải lại hồ sơ nhẹ (sử dụng bối cảnh phiên), nhanh hơn.
>
> **Bạn:** Tốt khi bạn đã tải bối cảnh trong cùng một phiên.

### Trường hợp sử dụng: Batch với khám phá

> **Bạn:** Nhiều bài đăng được lên kế hoạch. Khám phá một lần, viết nhiều lần.
>
> **Kỹ năng:** 
> - `/cre:exploring` (Q1-Q7, khóa CONTEXT.md)
> - `/cre:post-writer --from-context` (viết bài 1)
> - `/cre:exploring --reset` (khám phá chủ đề mới, CONTEXT.md mới)
> - `/cre:post-writer --from-context` (viết bài 2)
>
> **Bạn:** Luồng công việc hàng loạt, tất cả quyết định được ghi chép.

## 5. Những cảnh báo quan trọng

- **Cổng giọng điệu cũ bắt buộc:** Nếu tài liệu tích hợp > PSY lần cuối cùng làm mới, giọng điệu không đồng bộ với hồ sơ. Chạy `cre:voice-audit --character <name>` để kiểm tra độ nghiêm trọng drift.
- **Các cổng có thể thất bại:** Bằng chứng THẤT BẠI (yêu cầu T4-T5) hoặc quyền riêng tư THẤT BẠI (phát hiện rò rỉ) khối đầu ra. Sửa chữa và chạy lại; đừng buộc qua.
- **CONTEXT.md là tùy chọn:** Chế độ tương tác hoạt động độc lập. Nhưng khám phá trước = quyết định tốt hơn (ghi chép trong CONTEXT.md).
- **Post.txt sẵn sàng sao chép dán:** post.md là markdown; post.txt là văn bản thuần túy để dán nền tảng trực tiếp. Sử dụng post.txt.
- **Prompt hình ảnh là cố vấn:** Tạo hình ảnh không nằm trong phạm vi; kịch bản xuất prompt cho công cụ bên ngoài (ví dụ: Midjourney, Replicate).

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:exploring` — khám phá có cấu trúc (tạo CONTEXT.md)
- `cre:prompt-leverage` — gọi nội bộ (5 lớp tăng cường)
- `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` — cổng bắt buộc
- `cre:multiplatform` — tạo 1→N (sử dụng post-writer nội bộ cho mỗi nền tảng)
- Quy tắc 03 (quy trình nội dung), Quy tắc 09 (bảo mật), Quy tắc 14 (bằng chứng CRE)
