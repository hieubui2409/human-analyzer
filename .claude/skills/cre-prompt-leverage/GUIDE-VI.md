# cre:prompt-leverage — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn có một bài tóm tắt sơ bộ: "Viết một bài đăng LinkedIn về hành trình hướng dẫn của Nhân vật A." Đó là mơ hồ. Kỹ năng này biến nó thành một prompt thực thi chi tiết: trích xuất các mô hình giọng điệu của Nhân vật A ("phân tích, hình ảnh dày đặc, phòng vệ intelecualization"), lý thuyết lâm sàn để tham chiếu (lý thuyết gắn kết, tư duy phát triển), ràng buộc LinkedIn (3000 ký tự, móc đầu tiên, không spam hashtag), sự kiện hồ sơ cụ thể (DOB, trạng thái hiện tại, mối quan hệ chính), và cờ nhạy cảm (không tên gia đình thật, xác nhận dòng thời gian). Kết quả: một prompt cụ thể đến mức mà `cre:post-writer` biết chính xác phải làm gì.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Năm lớp tăng cường được áp dụng tuần tự:**

1. **Khóa giọng điệu:** Trích xuất các mô hình ngôn ngữ từ `identity/writing-voice.md` + `psychology/defense-mechanisms.md`. Giọng điệu, từ vựng, phép ẩn dụ định kỳ, anti-pattern (nhân vật không bao giờ nói).

2. **Độ chính xác lâm sàn:** Xác định các lý thuyết liên quan từ bài tóm tắt. Đọc `docs/references/{theory}.md`. Trích xuất các thuật ngữ chính, ứng dụng sai lầm phổ biến, ghi chú khả năng tiếp cận. Bảo vệ chống rò rỉ từ vựng lâm sàn.

3. **Định dạng nền tảng:** Ánh xạ ràng buộc nền tảng (LinkedIn: 3000 ký tự, văn bản-đầu tiên, móc trong 2 dòng; TikTok: 9:16, <60 giây, hội thoại). Thêm vào prompt.

4. **Tham chiếu chéo hồ sơ:** Liệt kê các tệp để đọc (identity/core.md, relationships/, timeline/). Thêm ràng buộc thực tế (DOB, trạng thái hiện tại, sự kiện chính, chính sách cấp độ bằng chứng).

5. **Quét nhạy cảm:** Xác định các tham chiếu chấn thương, tên thật, thuật ngữ lâm sàn. Thêm hướng dẫn và ràng buộc xử lý.

**Đầu ra:** Prompt được tăng cường + danh sách kiểm tra trước khi đọc + danh sách kiểm tra chất lượng để xác nhận.

## 3. Đường học tập

**Lần chạy đầu tiên (độc lập):**
```bash
/cre:prompt-leverage "Viết một bài đăng LinkedIn về sự tăng trưởng trong khẳng định của Nhân vật A"
```
Đầu ra: prompt được tăng cường với tất cả 5 lớp + "Đọc trước: identity/core.md, psychology/growth-edges.md, identity/writing-voice.md" + "Xác minh: assertiveness_unlock là bằng chứng T1 (ghi chú phiên)?"

**Khi bạn phát triển:** Hãy thử `--from-context` để đọc CONTEXT.md từ khám phá. Tất cả 5 lớp được áp dụng dựa trên các quyết định bị khóa.

**Luồng tiêu chuẩn:** Khám phá → khóa quyết định (CONTEXT.md) → prompt-leverage (tăng cường) → post-writer (viết).

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Tăng cường độc lập

> **Bạn:** `/cre:prompt-leverage Viết một bài blog về mối quan hệ của Nhân vật B với cờ bạc`
>
> **Kỹ năng:** Áp dụng 5 lớp → xuất ra: "Gốc: Viết một bài blog... | Được tăng cường: [full prompt với giọng của Nhân vật B, lý thuyết công thức văn hóa, ràng buộc blog, sự kiện gia đình, độ nhạy cảm với chấn thương cờ bạc]"
>
> **Bạn:** Sao chép prompt được tăng cường → cung cấp cho `cre:post-writer`.

### Trường hợp sử dụng: Từ khám phá

> **Bạn:** Đã khám phá, khóa CONTEXT.md. Bây giờ: `/cre:prompt-leverage --from-context`
>
> **Kỹ năng:** Trích xuất quyết định từ CONTEXT.md → áp dụng 5 lớp → xuất ra prompt được tăng cường.
>
> **Bạn:** Xác minh danh sách trước khi đọc, sau đó `cre:post-writer --from-context`.

## 5. Những cảnh báo quan trọng

- **Các lớp là cộng dồn:** Mỗi lớp thêm ràng buộc; ràng buộc hơn = clarity tốt hơn cho LLM, nhưng không phải lúc nào cũng là nội dung "tốt hơn".
- **Danh sách trước khi đọc là cố vấn:** Các tệp để đọc trước khi viết. Tác giả nên skim hoặc đọc đầy đủ theo ngân sách thời gian.
- **Các thuật ngữ lâm sàn được bảo vệ:** Lớp 2 cảnh báo về từ vựng lâm sàn; tác giả quyết định khi tham chiếu lâm sàn OK.
- **Không tự động xác nhận:** Prompt được tăng cường hoàn chỉnh hơn, không được chứng nhận chính xác. Post-writer vẫn xác nhận.
- **Tích hợp Context.md:** Nếu quyết định CONTEXT.md mơ hồ, prompt được tăng cường phản ánh điều đó. Khám phá kỹ lưỡng để có kết quả tốt nhất.

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:exploring` — tạo ra CONTEXT.md
- `cre:post-writer` — sử dụng nội bộ (Lớp 2) để tăng cường prompt
- Quy tắc 03 (quy trình nội dung), Quy tắc 02 (tham chiếu lâm sàn)
