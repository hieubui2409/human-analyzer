# gro:milestone-tracker — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn muốn **theo dõi tiến bộ sự nghiệp của nhân vật so với các mục tiêu của họ.** Họ có đạt được chức vụ cao hơn vào 30 tuổi không? Bằng cấp vẫn đang tiến hành? Họ có trễ, đúng lịch, hay sớm? Kỹ năng này theo dõi các cột mốc — đạt được, kế hoạch, và bỏ lỡ — từ milestones.md và career-path.md. Nó làm nổi bật tỷ lệ hoàn thành, trạng thái đúng lịch, cột mốc tiếp theo dự kiến, và liệu tiến triển có phù hợp với kỳ vọng giai đoạn sự nghiệp hay không. Hữu ích để đánh giá tính hợp lý của cung cấp nhân vật, rõ ràng động lực, hoặc căng thẳng tường thuật (độ trễ mục tiêu, vượt trội).

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thu thập dữ liệu, LLM đánh giá.** Tập lệnh Python chiết xuất các mục nhập cột mốc (tên, ngày mục tiêu, ngày đạt được hoặc trạng thái). LLM sau đó đánh giá:

1. **Tỷ lệ hoàn thành:** Có bao nhiêu cột mốc đạt được vs kế hoạch?
2. **Đánh giá đúng lịch:** Các cột mốc đạt được có đạt được ngày mục tiêu không, hoặc chúng có tập hợp sớm/muộn không?
3. **Sự phù hợp giai đoạn sự nghiệp:** Với ai đó ở Exploration (tuổi 20–30), các cột mốc có tập trung vào giáo dục/khám phá không? Với Establishment (30–40), có tập trung vào vai trò/gia đình không?
4. **Cột mốc tiếp theo:** Dựa trên các cột mốc đạt được, bước tiếp theo hợp lý là gì?

**Dựa trên bằng chứng.** LLM so sánh milestones.md (kế hoạch) với identity/achievements.md (xác thực đạt được) để phát hiện tiến bộ tham vọng vs thực.

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:milestone-tracker --character <name>` — xem dòng thời gian đầy đủ (đạt được, kế hoạch, bỏ lỡ). Chú ý tỷ lệ hoàn thành và trạng thái đúng lịch.

**Tiếp theo:** `gro:milestone-tracker --all --pending-only` — tập trung vào các cột mốc kế hoạch trên cả 3 nhân vật. Xem ai có lịch trình tham vọng vs bảo thủ.

**Sâu hơn:** Tham chiếu chéo với `gro:career-path --character <name>` — dòng thời gian cột mốc có phù hợp với lộ trình sự nghiệp không? (ví dụ, ai đó ở Establishment nên đã đạt được các cột mốc giáo dục cơ bản vào lúc này).

**Khi phát triển:** Dùng dữ liệu cột mốc để đánh giá động lực nhân vật (điều khiển vs vô mục đích) hoặc căng thẳng câu chuyện (bỏ lỡ thời hạn, vượt trội, mục tiêu chuyển hướng).

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Đánh giá sự liên kết tiến bộ sự nghiệp

> **Bạn:** "gro:milestone-tracker --character character-b"
>
> **Kỹ năng:** Chiết xuất các cột mốc của Nhân vật B. Tìm thấy: Các cột mốc giáo dục đạt được đúng lịch. Thăng chức sự nghiệp sớm vượt lịch trình. Mục tiêu cố vấn gần đây vẫn chưa hoàn thành. Tổng thể: hoàn thành 70%, phía trước trong các cột mốc sự nghiệp, phía sau trong những cột mốc phát triển cá nhân.
>
> **Sử dụng:** Nhân vật B ưu tiên sự nghiệp hơn phát triển cá nhân. Hữu ích cho góc độ động lực nhân vật (tham vọng nhưng không cân bằng) hoặc cài đặt câu chuyện (áp lực xoay chiều hướng cố vấn/trả lại).

### Trường hợp sử dụng: Phát hiện các cụm cột mốc để căng thẳng tường thuật

> **Bạn:** "gro:milestone-tracker --all"
>
> **Kỹ năng:** Nhân vật A có lịch trình chặt (cột mốc 6–12 tháng riêng biệt). Nhân vật B có lịch trình lỏng (cách 1–2 năm). Nhân vật C có tiến triển dừng lại (2+ năm giữa hai cột mốc cuối cùng).
>
> **Sử dụng:** Nhân vật A có động lực áp lực cao (rủi ro kiệt sức). Nhân vật B là phương pháp luận (căng thẳng thấp hơn, tăng trưởng chậm hơn). Nhân vật C có thể bị chặn (cần kiểm tra động lực). Hữu ích cho động lực nhóm hoặc cung cấp nhân vật riêng lẻ.

## 5. Những lưu ý quan trọng

- **Thời gian cột mốc là tự báo cáo.** Độ chính xác phụ thuộc vào milestones.md và achievements.md; dữ liệu cũ hoặc mơ hồ = đánh giá không đáng tin cậy.
- **Đúng lịch là nhị phân.** Kỹ năng này cờ các cột mốc như đạt được/chưa hoàn thành/bỏ lỡ; nó không điểm "gần như ở đó" hoặc "gần gũi".
- **Không phân tích nhân quả.** Nếu một cột mốc bị bỏ lỡ, kỹ năng này cờ nó nhưng không giải thích tại sao (chặn bên ngoài, thay đổi ưu tiên cá nhân, vấn đề năng lực). Dùng PSY hoặc xem xét bối cảnh để điều đó.
- **Cột mốc tiếp theo là phỏng đoán.** LLM gợi ý các bước hợp lý tiếp theo, nhưng cuộc sống thực tế phân kỳ (cơ hội mới, sự kiện cuộc sống). Coi nó như một giả thuyết làm việc.
- **Biên giới (Rule 15):** Kỹ năng này theo dõi các cột mốc GRO chỉ (sự nghiệp, giáo dục, năng lực). Nó không theo dõi các cột mốc tâm lý (chữa lành, phát triển gắn kết, v.v.) — những cái đó thuộc lĩnh vực PSY.
