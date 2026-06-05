# gro:competency-map — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn đang hỏi: **Nhân vật này thực sự có thể làm gì, và tốt đến mức nào?** Kỹ năng này lập kế hoạch tất cả các kỹ năng từ growth/competencies.md và xếp hạng mỗi kỹ năng trên **thang Dreyfus 7 cấp độ** (Novice → Advanced Beginner → Competent → Proficient → Expert → Master → Practical Wisdom). Nó làm nổi bật những điểm mạnh (Level 4+), lỗ hổng (Level 1–2), và cơ hội. Hữu ích để hiểu khả năng nhân vật, nhu cầu cố vấn, hoặc khả năng tin cậy câu chuyện.

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thu thập dữ liệu, LLM đánh giá.** Tập lệnh Python chiết xuất tên kỹ năng, mức Dreyfus (từ competencies.md), và bằng chứng (thành tựu, vật liệu, lịch sử sự nghiệp). LLM sau đó đánh giá:

1. **Độ tin cậy mức Dreyfus:** Là mức 5 (Expert) được hỗ trợ bằng bằng chứng? Hay bị tuyên bố quá mức?
2. **Phân bổ kỹ năng:** Nhân vật có chuyên môn sâu trong một lĩnh vực, nông trong nhiều lĩnh vực, hay cân bằng?
3. **Lộ trình tăng trưởng:** Các lỗ hổng có gần đây (có thể sửa chữa) hay mãn tính (cấu trúc)?

**Bằng chứng quan trọng.** Một kỹ năng được xếp hạng Level 3 (Competent) không có nhãn bằng chứng được cờ; một với trích dẫn thành tựu là có tin cậy.

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:competency-map --character <name>` — xem tất cả các kỹ năng và mức Dreyfus của chúng. Quét các phần điểm mạnh (4+) và lỗ hổng (1–2).

**Tiếp theo:** `gro:competency-map --gaps-only` — tập trung vào các khu vực yếu. Nhân vật sẽ cần phải học điều gì để tiến bộ?

**Sâu hơn:** `gro:competency-map --character <name> --json` — truy cập lập trình cho phân tích hạ lưu (learning-profile, career-forecast).

**Khi phát triển:** So sánh trên các nhân vật (`gro:compare --dimension competency`) để phát hiện các sức mạnh bổ sung.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Đánh giá sự sẵn sàng cho một bước chuyển sự nghiệp

> **Bạn:** "gro:competency-map --character hieu"
>
> **Kỹ năng:** Chiết xuất tất cả các kỹ năng của Nhân vật A. Tìm: Lĩnh vực kỹ thuật ở Level 4–5 (Expert). Quản lý dự án ở Level 2 (Advanced Beginner). Giao tiếp ở Level 3 (Competent).
>
> **Sử dụng:** Nhân vật A sẵn sàng lãnh đạo một dự án kỹ thuật nhưng sẽ đấu tranh quản lý các nhóm đa chức năng. Hữu ích cho căng thẳng tường thuật (thăng chức tham vọng, cạnh tăng trưởng) hoặc góc độ cố vấn (cần huấn luyện giao tiếp).

### Trường hợp sử dụng: Xác định cơ hội tăng trưởng cho nội dung

> **Bạn:** "gro:competency-map --all --gaps-only"
>
> **Kỹ năng:** Trả về kỹ năng Level 1–2 trên cả 3 nhân vật. Cả ba đều yếu trong Phân tích dữ liệu. Nhân vật B và Nhân vật C thiếu Nói chuyện công khai.
>
> **Sử dụng:** Phát hiện các chủ đề tăng trưởng chung (cung cấp học tập tập thể, cơ hội cố vấn ngang hàng) hoặc các lỗ hổng riêng lẻ (Nhân vật B lo sợ nói chuyện công khai — góc độ tâm lý).

## 5. Những lưu ý quan trọng

- **Mức Dreyfus là heuristic.** LLM phán xét mức từ bằng chứng; đây là suy đoán có giáo dục, không phải một bài kiểm tra kỹ năng được xác thực.
- **Chất lượng bằng chứng hướng dẫn độ chính xác.** Nếu competencies.md liệt kê "Python" không có chi tiết, sự tự tin là thấp. Chi tiết (dự án, chứng chỉ, năm) tăng sự tự tin.
- **Định nghĩa kỹ năng khác nhau.** "Quản lý dự án" với một nhân vật có thể là "điều phối nhiệm vụ" với một nhân vật khác. LLM cố gắng bình thường hóa nhưng có thể phân loại sai.
- **Không phân tích rào cản học tập.** Nếu một lỗ hổng tồn tại, kỹ năng này cờ nó nhưng không giải thích tại sao (rào cản tâm lý, sự không phù hợp phong cách học tập, ràng buộc bên ngoài). Dùng lĩnh vực PSY để điều đó.
