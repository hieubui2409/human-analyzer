# psy:timeline-sync — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn cập nhật dòng thời gian của Nhân vật A bằng "kết nghĩa Sep 2025." Nhưng dòng thời gian của Nhân vật B vẫn nói "kết nghĩa Aug 2025" (hoặc thiếu mục nhập). Trước khi bạn chạy psy:crossref, kỹ năng này bắt những không phù hợp ngày: trích xuất tất cả các sự kiện từ tất cả các dòng thời gian, tìm sự kiện đề cập đến các nhân vật khác, kiểm tra chéo ngày. Đầu ra: "MISMATCH: ngày kết nghĩa khác nhau (Nhân vật A: Sep, Nhân vật B: Aug). Sửa được đề xuất: căn chỉnh đến Sep 2025 (Nhân vật A có bằng chứng vật liệu P1)."

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Trích xuất sự kiện**: Xác định. Regex tìm ngày + văn bản sự kiện. Xử lý "Sep 2025", "2025-09", "September", các biến thể.
- **Kết hợp qua các nhân vật**: Nếu dòng thời gian của Nhân vật A đề cập đến "gặp Nhân vật B" và Nhân vật B đề cập đến "gặp Nhân vật A," kỹ năng ghép cặp chúng.
- **Phân loại không phù hợp**: Ngày khác nhau → MISMATCH (ưu tiên CAO). Sự kiện trong cái này, bị mất trong cái kia → MISMATCH. Ngày trong vòng 1 tháng → MATCH (biến thể chấp nhận được, văn hóa hoặc ký ức mơ hồ).
- **Bản sửa được đề xuất**: Dựa trên dòng thời gian nhân vật nào có bằng chứng vật liệu (P1 > P2 > ngầm). Nếu cả hai có vật liệu, hãy hỏi người dùng.

## 3. Đường dẫn học tập

**Tất cả các nhân vật:** `psy:timeline-sync --all` — kiểm tra đầy đủ qua các nhân vật.

**Một nhân vật:** `psy:timeline-sync --character hieu` — chỉ dòng thời gian của Nhân vật A (không kiểm tra chéo).

**Đầu ra JSON:** `psy:timeline-sync --json` — có cấu trúc cho tự động hóa.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra đồng bộ hóa sau cập nhật

> Bạn: "Tôi cập nhật milestones.md của Nhân vật C bằng 'Scholarship X scholarship awarded Jun 2025.' Tôi có bỏ lỡ cập nhật những cái khác không?"
> Kỹ năng: `psy:timeline-sync --all`
> → Kiểm tra chéo tìm thấy: dòng thời gian của Nhân vật A có "Nhân vật C awarded Jun 2025" (từ vật liệu), milestones.md của Nhân vật C có "Jun 2025" (khớp ✓). Nhưng dòng thời gian của Nhân vật B hoàn toàn thiếu sự kiện này (Nhân vật B kết nối qua Nhân vật A). Khuyến nghị: thêm vào timeline/overview.md của Nhân vật B để hoàn chỉnh.

### Trường hợp sử dụng: Kiểm tra căn chỉnh ngày

> Bạn: "Lễ kết nghĩa: Nhân vật A nói Sep 2025, nhưng tôi không chắc Nhân vật B có khớp không."
> Kỹ năng: `psy:timeline-sync --pair hieu hoa`
> → MISMATCH: timeline/overview.md của Nhân vật A: "Sep 2025" (dòng 42). timeline/overview.md của Nhân vật B: "Aug 2025" (dòng 18). Vật liệu xác nhận Sep 2025 (P1). Khuyến nghị: cập nhật ngày của Nhân vật B thành Sep 2025.

### Trường hợp sử dụng: Xác thực trước crossref

> Bạn: "Trước khi chạy psy:crossref, tôi nên kiểm tra đồng bộ hóa dòng thời gian không?"
> Kỹ năng: `psy:timeline-sync --all`
> → Đầu ra: 15 sự kiện chung, 14 khớp, 1 không phù hợp. Khuyến nghị: sửa 1 không phù hợp, sau đó chạy psy:crossref.

## 5. Cảnh báo quan trọng

- **Khớp mờ trong ±1 tháng là chấp nhận được**: Ký ức văn hóa, mơ hồ cố ý (nhân vật nhớ "mùa hè" không phải ngày chính xác) → +/- 1 tháng OK. Vượt quá điều đó → cờ.
- **Sự kiện bị mất được cờ nhưng không phải lỗi**: Nếu dòng thời gian của Nhân vật B không đề cập đến sự kiện Nhân vật A-Nhân vật B, nó là một khoảng trống, không nhất thiết sai (Nhân vật B có thể không xem xét nó có ý nghĩa). Xem xét thủ công cần thiết.
- **Bằng chứng vật liệu hướng dẫn đề xuất**: Nếu cả hai có ngày khác nhau, bằng chứng vật liệu (nguồn P1) gợi ý tipping. Nếu cả hai mơ hồ → hỏi người dùng.
- **Kiểm tra nhân vật duy nhất không tìm thấy không phù hợp**: `--character hieu` chỉ kiểm tra dòng thời gian của Nhân vật A. Không so sánh chéo. Sử dụng `--all` hoặc `--pair` để không phù hợp.
- **Không phải là bộ kiểm tra tính nhất quán**: Điều này kiểm tra ngày chỉ. Tính nhất quán tâm lý, động lực quan hệ, sự liên kết kêu gọi → đó là psy:crossref.
