# gro:compare — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn có 3 hồ sơ nhân vật và muốn hiểu **họ khác nhau và liên quan như thế nào.** Họ có ở cùng một giai đoạn sự nghiệp không? Các phong cách học tập của họ có bổ sung hay xung đột không? Ai cố vấn cho ai? Kỹ năng này so sánh song song giai đoạn sự nghiệp, phân bổ kỹ năng, phong cách học tập (Kolb), và mạng lưới cố vấn trên cả 3 nhân vật. Hữu ích để hiểu động lực dyad, thành phần nhóm, hoặc căng thẳng tường thuật.

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thu thập dữ liệu, LLM đánh giá.** Tập lệnh Python đọc tất cả 4 tệp GRO trên mỗi nhân vật (career-path, competencies, learning-profile, mentoring-map) và chiết xuất các chiều có thể so sánh. LLM sau đó tạo ra những hiểu biết:

1. **Chênh lệch giai đoạn sự nghiệp:** Ai ở Growth vs Exploration vs Establishment? Phân bổ tuổi?
2. **Phân bổ kỹ năng:** Nhân vật nào có tất cả các kỹ năng khó, cái khác là các kỹ năng mềm? Overlaps?
3. **Khả năng tương thích phong cách học tập:** Phong cách Kolb (Diverging, Assimilating, Converging, Accommodating) — họ có học cùng một cách hay khác nhau?
4. **Mạng lưới cố vấn:** Cố vấn chính là ai? Cố vấn chéo? Rủi ro cô lập?

**Không xâm phạm.** Chỉ đọc; không có sự kiện phát hành; thuần túy thông tin.

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:compare --dimension all` — xem cả 4 chiều. Quét để tìm các khoảnh khắc rõ ràng.

**Tiếp theo:** `gro:compare --dimension career` — tập trung vào giai đoạn sự nghiệp chỉ. Xác định ai là junior, mid, senior.

**Sâu hơn:** `gro:compare --dimension learning` — Phong cách Kolb. Chú ý liệu mọi người có phải là Diverging (tất cả các nhà brainstorm) hay hỗn hợp (một số thực tế, một số phản xạ).

**Khi phát triển:** `gro:compare --json` cho các bộ lập trình; `--dimension mentoring` để hiểu các mô hình chuyển giao kiến thức.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Hiểu khả năng bổ sung dyad để tạo nội dung

> **Bạn:** "gro:compare --dimension competency --json | jq '.characters | map(.top_skills)'"
>
> **Kỹ năng:** Chiết xuất các kỹ năng hàng đầu trên mỗi nhân vật. Nhân vật A có độ sâu kỹ thuật, Nhân vật B có sức mạnh giao tiếp, Nhân vật C có kinh nghiệm quản lý.
>
> **Sử dụng:** Bạn thấy các điểm mạnh bổ sung. Trong một dyad, họ có thể cố vấn cho nhau (Nhân vật A dạy Nhân vật B kỹ thuật, Nhân vật B dạy Nhân vật A giao tiếp). Hữu ích cho các góc độ nội dung cố vấn.

### Trường hợp sử dụng: Phát hiện sự không phù hợp phong cách học tập để hợp tác

> **Bạn:** "gro:compare --dimension learning"
>
> **Kỹ năng:** Nhân vật A = Converging (thực tế, giải quyết vấn đề). Nhân vật B = Diverging (trí tưởng tượng, cảm xúc). Nhân vật C = Assimilating (lôgic, lý thuyết).
>
> **Sử dụng:** Nếu họ làm việc cùng nhau, hãy mong đợi xung đột: Nhân vật A muốn giải quyết ngay bây giờ, Nhân vật B muốn brainstorm các tùy chọn, Nhân vật C muốn hiểu mô hình. Hữu ích cho các góc độ xung đột hoặc storytelling động lực nhóm.

## 5. Những lưu ý quan trọng

- **Chỉ bề mặt.** Kỹ năng này cờ các khác biệt; phân tích dyad/triad sâu sắc yêu cầu đọc các hồ sơ trực tiếp.
- **Phong cách Kolb là heuristic.** Kỹ năng learning-profile (và so sánh này) dựa vào phán đoán LLM heuristic; không phải một bài kiểm tra được xác thực.
- **Không so sánh PSY.** Kỹ năng này so sánh các chiều GRO chỉ. Để so sánh tâm lý (mô hình gắn kết, cơ chế phòng vệ, chồng chéo chấn thương), dùng `psy:profile-compare`.
- **Mạng lưới cố vấn là tĩnh.** Phản ánh mentoring-map hiện tại, không phải các mối quan hệ cố vấn tương lai giả thuyết.
