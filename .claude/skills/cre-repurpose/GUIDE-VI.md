# cre:repurpose — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã công bố một bài đăng LinkedIn về hành trình hướng dẫn của Nhân vật A. Nó đã thực hiện tốt. Bây giờ bạn muốn tiếp cận cộng đồng Twitter (định dạng thread) và Instagram. Thay vì viết lại từ đầu 3 lần, bạn cung cấp cho kỹ năng này bài đăng LinkedIn → nó trích xuất thông điệp cốt lõi → thích ứng với Twitter (các đoạn 280 ký tự, có thể trích dẫn), sau đó riêng biệt thích ứng với Instagram (định dạng caption, hashtag, emoji). Mỗi thích ứng tôn trọng bằng chứng và giọng điệu của nguồn. Khác với `cre:multiplatform`: cái này hoạt động sau khi công bố (1→1), multiplatform là lúc tạo (1→N gốc từ một khái niệm).

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Thích ứng vs. Tạo:**

- `cre:multiplatform`: "Đây là một góc nhìn. Tạo 5 bản gốc từ đầu — một cho mỗi nền tảng."
- `cre:repurpose`: "Đây là một bài đăng đã công bố. Thích ứng nó với một nền tảng khác."

**Luồng công việc thích ứng:**

1. **Đọc nội dung nguồn** (post.md từ tệp hoặc mới nhất từ nền tảng)
2. **Trích xuất thông điệp cốt lõi** — tinh túy (câu chuyện, hiểu biết, hành động gọi)
3. **Thích ứng**: điều chỉnh cho cấu trúc, độ dài, giọng điệu, mô hình móc của nền tảng đích
4. **Xác nhận**: privacy-guard (rò rỉ?), voice-audit (drift giọng?), bằng chứng được bảo tồn
5. **Xuất ra**: gói 5 tệp tiêu chuẩn

**Quy tắc thích ứng nền tảng** sống trong `.claude/scripts/platform_lib/platform_constraints.py` (cùng mô-đun như `cre:multiplatform` — DRY).

## 3. Đường học tập

**Lần chạy đầu tiên:** Tìm một bài đăng đã công bố, thích ứng nó:
```bash
/cre:repurpose --from assets/linkedin/260526-mentorship --to twitter --character hieu
```
Đọc bài LinkedIn → trích xuất thông điệp cốt lõi ("hướng dẫn xây dựng lòng tin qua tính nhất quán") → thích ứng với định dạng thread Twitter (các đoạn 280 ký tự, có thể trích dẫn) → chạy cổng → xuất ra assets/twitter/{slug}/.

**Khi bạn phát triển:** Hãy thử `--tone override` để thay đổi giọng điệu cho nền tảng đích (ví dụ: LinkedIn chuyên nghiệp; thích ứng TikTok nên hội thoại).

**Luồng tiêu chuẩn:** Viết bài trên nền tảng chính → `cre:post-writer` → công bố → sử dụng lại cho 2-3 nền tảng phụ tuần tự.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: LinkedIn sang TikTok

> **Bạn:** "Tôi đã công bố một bài đăng LinkedIn. Bây giờ thích ứng nó cho TikTok."
>
> **Kỹ năng:** `--from assets/linkedin/260526-mentorship --to tiktok --character hieu` → đọc LinkedIn → trích xuất câu chuyện → thích ứng với kịch bản TikTok (9:16, <60 giây, móc trong 3 giây, hội thoại).
>
> **Kỹ năng:** Chạy privacy-guard + voice-audit → xuất ra assets/tiktok/{slug}/.
>
> **Bạn:** Xem xét, có thể điều chỉnh, sau đó đăng lên TikTok.

### Trường hợp sử dụng: Blog sang Twitter

> **Bạn:** "Tôi có một bài blog dạng dài. Biến nó thành một thread Twitter."
>
> **Kỹ năng:** `--from assets/blog/260526-growth-journey --to twitter` → trích xuất các hiểu biết chính → định dạng dưới dạng thread (5-8 tweet, mỗi <280 ký tự, sắp xếp hợp lý).
>
> **Bạn:** Đăng thread sang Twitter.

### Trường hợp sử dụng: Batch sử dụng lại

> **Bạn:** "Thích ứng bài LinkedIn cho Facebook, Instagram và Twitter (3 lệnh gọi)."
>
> **Kỹ năng:** 
> - `--from assets/linkedin/260526-post --to facebook`
> - `--from assets/linkedin/260526-post --to instagram`
> - `--from assets/linkedin/260526-post --to twitter`
>
> **Bạn:** 3 đầu ra, mỗi cái được thích ứng với quy chuẩn nền tảng.

## 5. Những cảnh báo quan trọng

- **Bảo tồn thông điệp cốt lõi:** Nội dung được thích ứng phải duy trì cấp độ bằng chứng của nguồn và độ chính xác lâm sàn. Không đơn giản hóa quá mức tạo ra thông tin sai lệch.
- **Một lệnh gọi = một đầu ra:** Mỗi lệnh gọi tạo một nền tảng đích. Đối với N nền tảng, gọi N lần (hoặc sử dụng `cre:multiplatform` để tạo 1→N).
- **Các cổng có thể chặn:** Nếu privacy-guard gắn cờ rò rỉ hoặc voice-audit phát hiện drift, thích ứng được giữ. Điều tra và sửa chữa nguồn.
- **Tính toàn vẹn cấp độ bằng chứng:** Nếu nguồn sử dụng bằng chứng T1, phiên bản được thích ứng không được hạ cấp xuống T5 suy đoán.
- **Ngưỡng quyền riêng tư khác nhau theo nền tảng:** Blog cho phép; LinkedIn nghiêm ngặt. Cùng một nội dung có thể PASS trên blog, THẤT BẠI trên LinkedIn.

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:multiplatform` — tạo 1→N gốc (lúc tạo, không phải sau khi công bố)
- `cre:post-writer` — tạo nền tảng duy nhất
- `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` — cổng xác nhận
- Quy tắc 03 (quy trình nội dung), Quy tắc 14 (sự kiện CRE)
