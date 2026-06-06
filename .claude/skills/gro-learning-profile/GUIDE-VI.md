# gro:learning-profile — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn muốn hiểu **nhân vật học tập tốt nhất như thế nào.** Họ có brainstorm (Diverging), phân tích (Assimilating), giải quyết vấn đề (Converging), hay nhảy vào và làm (Accommodating)? Kỹ năng này lập hồ sơ phong cách học tập bằng **Chu kỳ Học tập Trải nghiệm của Kolb** — một khung ánh xạ cách mọi người thích thu thập thông tin (Concrete Experience vs Abstract Conceptualization) và xử lý nó (Reflective Observation vs Active Experimentation). Hữu ích để hiểu các mô hình phát triển nhân vật, cá nhân hóa nội dung, hoặc động lực nhóm.

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thu thập dữ liệu, LLM đánh giá.** Tập lệnh Python chiết xuất dữ liệu học tập (các phương pháp học tập, lý lịch giáo dục, các mô hình thu thập kiến thức từ growth/learning-profile.md và vật liệu). LLM sau đó gán một phong cách Kolb chủ đạo:

1. **Diverging (CE + RO):** trí tưởng tượng, cảm xúc, nhà brainstorm; thích suy ngẫm, thảo luận nhóm
2. **Assimilating (AC + RO):** lôgic, phân tích, những nhà xây dựng lý thuyết; thích bài giảng, đọc, mô hình
3. **Converging (AC + AE):** thực tế, người giải quyết vấn đề, tập trung kỹ thuật; thích thử nghiệm, thực hành
4. **Accommodating (CE + AE):** thực hành, những người chấp nhận rủi ro, những người làm; thích các dự án thực tế, thử trước

**Hầu hết mọi người đều hỗn hợp.** LLM xác định các phong cách chủ đạo + thứ cấp, sau đó lưu ý các lỗ hổng chu kỳ (ví dụ, "mạnh trong Concrete Experience nhưng yếu trong Reflective Observation").

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:learning-profile --character <name>` — xem phong cách Kolb chủ đạo và điểm mạnh/lỗ hổng của chu kỳ. Quét "Ý nghĩa phong cách nội dung" để tìm hiểu cá nhân hóa.

**Tiếp theo:** `gro:learning-profile --all` — so sánh phong cách học tập trên cả 3 nhân vật. Ai học cùng một cách? Ai phân kỳ?

**Sâu hơn:** Tham chiếu chéo với `gro:competency-map --gaps-only` — nếu ai đó có khoảng trống kỹ năng, phong cách học tập của họ có giải thích nó không? (ví dụ, người học Converging có thể gặp khó khăn với các kỹ năng nặng về lý thuyết).

**Khi phát triển:** Dùng phong cách Kolb để khung nội dung CRE cho từng nhân vật (Diverging → những gợi ý mở; Assimilating → giải thích được hỗ trợ bằng nghiên cứu; Converging → giải quyết vấn đề từng bước; Accommodating → các kịch bản thực tế).

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Cá nhân hóa nội dung cho phong cách học tập của nhân vật

> **Bạn:** "gro:learning-profile --character character-b"
>
> **Kỹ năng:** Tìm thấy Nhân vật B là Diverging (trí tưởng tượng, suy ngẫm). Yêu thích brainstorming, không thích các quy trình cứng nhắc. Lỗ hổng chu kỳ: yếu trong Active Experimentation (không nhảy vào hành động dễ dàng).
>
> **Sử dụng:** Khung nội dung cho Nhân vật B là khám phá mở (không phải các bước quy định). Dùng những móc cảm xúc, các quan điểm đa dạng. Tránh ngôn ngữ "chỉ làm đi". Hữu ích cho cá nhân hóa CRE hoặc cách tiếp cận cố vấn.

### Trường hợp sử dụng: Phát hiện sự không phù hợp phong cách học tập để xung đột

> **Bạn:** "gro:learning-profile --all"
>
> **Kỹ năng:** Nhân vật A = Converging (thực tế, giải quyết vấn đề). Nhân vật B = Diverging (trí tưởng tượng, suy ngẫm). Nhân vật C = Assimilating (phân tích).
>
> **Sử dụng:** Nếu họ hợp tác trong học tập (ví dụ, onboarding), hãy mong đợi xung đột: Nhân vật A muốn giải quyết nhanh, Nhân vật B muốn khám phá các tùy chọn, Nhân vật C muốn hiểu hệ thống. Hữu ích cho storytelling xung đột hoặc nội dung động lực nhóm.

## 5. Những lưu ý quan trọng

- **Kolb là sở thích, không phải khả năng.** Một người học Diverging có thể làm công việc thực hành; họ chỉ thích không làm. Hữu ích để hiểu các vùng thoải mái, không phải những hạn chế.
- **Phân loại Kolb là heuristic.** LLM suy ra phong cách từ dữ liệu học tập; không phải một bài kiểm tra được xác thực. Coi nó là một giả thuyết làm việc, không phải sự thật.
- **Lỗ hổng chu kỳ có thể phản ánh bối cảnh, không phải phong cách.** Nếu ai đó có Active Experimentation yếu, nó có thể là lỗ hổng phong cách học tập HOẶC thiếu cơ hội (công việc không cho phép thực hành). LLM cố gắng phân biệt nhưng có thể bỏ lỡ bối cảnh.
- **Không suy luận lĩnh vực PSY.** Phong cách học tập là sở thích nhận thức; nó KHÔNG giải thích các rào cản tâm lý (lo lắng, chấn thương, gắn kết). Dùng lĩnh vực PSY để điều đó.
