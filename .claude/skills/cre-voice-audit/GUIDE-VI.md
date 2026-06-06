# cre:voice-audit — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã công bố 5 bài trong tháng quá về Nhân vật A. Đọc lại chúng, một bài cảm thấy không đúng — chính thức hơn, lâm sàn hơn, so với giọng điệu thông thường của anh ấy. Kỹ năng này đọc `identity/writing-voice.md` của anh ấy (hồ sơ giọng điệu có cấu trúc), sau đó kiểm toán từng bài trong 5 bài của bạn chống lại nó. Kết quả: gắn cờ bài nào drift, loại drift (gãy giọng, không khớp từ vựng, ngôn ngữ lâm sàn ẩn), mức độ. Không viết lại — chỉ rõ ràng nơi tính nhất quán bị trượt.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Kích thước hồ sơ giọng điệu (từ identity/writing-voice.md):**

Hồ sơ của Nhân vật A liệt kê: nhịp điệu câu (trung bình, bao quát), nén (vừa phải), đăng ký cảm xúc (mặc định phân tích, phạm vi hẹp), ngân hàng hình ảnh (tâm lý + tăng trưởng), lệnh cấm cứng (không bao giờ nói X, Y), cổng phòng vệ (intelecualization biểu hiện dưới dạng dày đặc, chi tiết), bổ sung tăng trưởng (các cung gần đây thay đổi giọng).

**Phát hiện drift:**

1. **Gãy giọng điệu:** Bài viết sử dụng chính thức khi giọng điệu là hội thoại (hoặc ngược lại) — MỨC CAO
2. **Không khớp từ vựng:** Bài viết sử dụng các từ mà nhân vật sẽ không bao giờ sử dụng (lệnh cấm cứng bị vi phạm) — TRUNG BÌNH
3. **Gãy nhân vật:** Nội dung mâu thuẫn với quan điểm được thiết lập của nhân vật — MỨC CAO
4. **Thích ứng quá mức nền tảng:** Nội dung được sử dụng lại mất giọng điệu gốc — TRUNG BÌNH
5. **Rò rỉ lâm sàn:** Các thuật ngữ lâm sàn thô trong nội dung giọng điệu nhân vật — MỨC CAO

**Verdict cache:** Các bản án giọng điệu cho mỗi tài sản khóa trên hash nội dung. Tài sản không thay đổi = không có re-judge (hiệu quả token). `--fresh` buộc re-judge.

## 3. Đường học tập

**Lần chạy đầu tiên:**
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-voice-audit/scripts/audit-published-content-for-voice-drift.py \
  --character character-a
```
Đầu ra: báo cáo kiểm toán. 5 bài được quét. Bài 3 (LinkedIn hướng dẫn) được gắn cờ: "Giọng điệu quá chính thức (vs. mặc định hội thoại). Từ vựng: 'khung công tác giáo dục' — Nhân vật A tránh thuật ngữ giáo dục chính thức." Mức độ: TRUNG BÌNH.

**Khi bạn phát triển:** Hãy thử `--report` để tạo một báo cáo đầy đủ được lưu sang `plans/reports/`. Sử dụng `--fresh` khi bạn đã chỉnh sửa một bài và muốn tái kiểm toán.

**Luồng tiêu chuẩn:** Công bố bài → voice-audit tự động chạy (thông qua post-writer Giai đoạn 5) → nếu PASS, xong; nếu drift CAO, tác giả chỉnh sửa lại.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra tính nhất quán hàng loạt

> **Bạn:** "Tôi đã công bố 10 bài trong tháng này. Xác minh tất cả chúng nghe giống như Nhân vật A."
>
> **Kỹ năng:** `--character character-a` → quét tất cả các bài Nhân vật A trong assets/ → "9 PASS (nhất quán), 1 TRUNG BÌNH (giọng điệu quá chính thức trên post_5)."
>
> **Bạn:** Xem xét post_5, có thể viết lại mở đầu để phù hợp với giọng điệu.

### Trường hợp sử dụng: Kiểm tra giọng điệu đa nền tảng

> **Bạn:** "Các bài trên LinkedIn nghe khác so với TikTok. Đó là thích ứng nền tảng hay drift giọng điệu?"
>
> **Kỹ năng:** `--platform linkedin` → kiểm tra chỉ LinkedIn. `--platform tiktok` → kiểm tra chỉ TikTok. So sánh báo cáo.
>
> **Bạn:** Nếu LinkedIn là PASS và TikTok là CẢNH BÁO (không khớp giọng), bài TikTok cần căn chỉnh giọng điệu.

### Trường hợp sử dụng: Kiểm toán bài viết duy nhất

> **Bạn:** "Tôi vừa sử dụng lại bài LinkedIn sang blog. Kiểm tra xem giọng điệu có giữ được không."
>
> **Kỹ năng:** `--file assets/blog/260526-repurposed-post` → kiểm toán bài đó duy nhất.
>
> **Kỹ năng:** "PASS — giọng điệu nhất quán với nguồn LinkedIn + giọng hội thoại blog được phép."

## 5. Những cảnh báo quan trọng

- **Verdict cache dựa trên nội dung:** Cùng một tài sản = không có re-judge. Nếu bạn chỉnh sửa bài, verdict cũ (sử dụng `--fresh`).
- **Drift là kinh nghiệm, không phải tuyệt đối:** Kiểm toán giọng điệu dựa trên LLM; các trường hợp biên giới yêu cầu xét xử con người.
- **Mức độ là cố vấn:** Drift CAO không tự động chặn; tác giả quyết định hành động.
- **Nhận biết nền tảng:** Giọng điệu hội thoại TikTok được mong đợi (không phải drift); giọng điệu hội thoại LinkedIn có thể là drift (tùy thuộc vào hồ sơ nhân vật).
- **Các cơ chế phòng vệ quan trọng:** Các cơ chế phòng vệ hoạt động của nhân vật hình thành giọng điệu (ví dụ: intelecualization của Nhân vật A → ngôn ngữ dày đặc, chi tiết KHÔNG phải drift; đó là xác thực).

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- Verdict cache: [`verdict-cache-contract.md`](../_framework-shared/references/verdict-cache-contract.md)
- `cre:post-writer` (gọi điều này tự động ở Giai đoạn 5)
- `cre:repurpose`, `cre:multiplatform` (sử dụng cái này để xác nhận theo biến thể)
- Quy tắc 02 (tham chiếu lâm sàn hiển thị không nói), Quy tắc 03 (quy trình nội dung)
