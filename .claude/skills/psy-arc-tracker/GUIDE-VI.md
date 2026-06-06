# psy:arc-tracker — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Ba tháng trước, bạn chạy `psy:hypothesis` trên Nhân vật C: "Nếu Nhân vật C nhận được học bổng Scholarship X, anh ấy sẽ cảm thấy xác thực nhưng sau đó nghi ngờ bản thân." Bây giờ đã ba tháng sau. Nhân vật C có thực sự nhận được học bổng không? Nếu vậy, anh ấy có cảm thấy xác thực và sau đó nghi ngờ, như dự đoán không? Kỹ năng này đọc hồ sơ hiện tại của anh ấy, trích xuất các tín hiệu tăng trưởng, và so sánh chúng với dự đoán giả thuyết từ ba tháng trước. Điểm: độ chính xác dự đoán 85%. Nó cũng theo dõi: Cột mốc "nhận học bổng" của Nhân vật C được đánh dấu ACHIEVED? Coping của anh ấy đang trở nên lành mạnh hơn hay tránh tránh hơn? Quỹ đạo: GROWTH hoặc PLATEAU?

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Trích xuất quỹ đạo**: Đọc các chỉ báo tâm lý (cơ chế ứng phó phát triển, mẫu khủng hoảng, yếu tố bảo vệ, sự kiện dòng thời gian). Phân loại là GROWTH (thay đổi tích cực), PLATEAU (ổn định), REGRESSION (thay đổi tiêu cực).
- **Theo dõi cột mốc**: So sánh `milestones.md` với dòng thời gian thực tế. Các cột mốc có đúng lịch không? Bị bỏ lỡ?
- **So sánh giả thuyết**: Nếu bạn có dự đoán trước đó, kỹ năng này khác hồ sơ hiện tại. Dự đoán có thực hiện đúng không? Điểm độ chính xác.
- **Mức độ tự tin**: Dựa trên sự phong phú của dữ liệu. Bằng chứng đầy đủ = CAO. Hồ sơ thưa thớt = độ tự tin THẤP.

## 3. Đường dẫn học tập

**Quỹ đạo tăng trưởng:** `psy:arc-tracker --character character-c --trajectory` — đánh giá giai đoạn tăng trưởng hiện tại.

**Xem xét cột mốc:** `psy:arc-tracker --character character-a --milestones` — kiểm tra tiến trình trên các cột mốc có kế hoạch.

**Xác thực giả thuyết:** `psy:arc-tracker --character character-b --compare 2026-03-15` — dự đoán tháng 3 có giữ được không?

**Báo cáo đầy đủ:** `psy:arc-tracker --character hều --trajectory --milestones --report` — toàn diện.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra quỹ đạo tăng trưởng

> Bạn: "Nhân vật A ở đâu trong cung điểm của anh ấy ngay bây giờ?"
> Kỹ năng: `psy:arc-tracker --character character-a --trajectory`
> → Chỉ báo: cơ chế ứng phó thích ứng hơn (thăng hoa, hài hước luôn lành mạnh). Mẫu khủng hoảng: khủng hoảng cờ bạc được giải quyết, không có tập phút cấp tính mới. Yếu tố bảo vệ: mối quan hệ hướng dẫn tăng cường. Quỹ đạo: GROWTH (độ tự tin: CAO). Giai đoạn tăng trưởng: "Phục hồi + tái tham gia vào hướng dẫn."

### Trường hợp sử dụng: Xem xét cột mốc

> Bạn: "Nhân vật C có đạt được các cột mốc chúng tôi đặt ra không?"
> Kỹ năng: `psy:arc-tracker --character character-c --milestones`
> → Cột mốc: "Vượt qua phỏng vấn Scholarship X" (Mar 2025) → ACHIEVED ✓ (bằng chứng: dòng thời gian). "Nhận quyết định học bổng" (Jun 2025) → IN_PROGRESS (dự kiến 2 tuần). "Bắt đầu học" (Sep 2025) → NOT_STARTED (giữ chỗ). Dự báo: 2/3 đúng lịch.

### Trường hợp sử dụng: Xác thực giả thuyết

> Bạn: "Ba tháng trước tôi dự đoán Nhân vật B sẽ xoắn nếu bố anh ấy gọi. Điều đó có xảy ra không?"
> Kỹ năng: `psy:arc-tracker --character character-b --compare 2026-03-01`
> → Dự đoán: liên lạc cha → bất ổn tâm lý → leo thang uống rượu. Thực tế: cha liên lạc (mục nhập dòng thời gian), Nhân vật B ứng phó thông qua hướng dẫn (hỗ trợ Nhân vật A). Độ chính xác dự đoán: 40% (mong đợi xoắn, có thích ứng). Insight: bảo vệ từ Nhân vật A đã thay đổi kết quả.

## 5. Cảnh báo quan trọng

- **Quỹ đạo là quan sát, không quy định**: GROWTH không có nghĩa là "chữa khỏi." Cao nguyên không phải là thất bại. Hồi thoái có thể là cần thiết (xử lý chấn thương yêu cầu một số hồi thoái).
- **Cột mốc so với độ trôi thực tế**: Một cột mốc có thể lỗi thời (đặt 1 năm trước, điều kiện thay đổi). Xem xét thủ công cần thiết.
- **So sánh giả thuyết cần dự đoán rõ ràng**: Nếu bạn không có báo cáo psy:hypothesis được lưu, `--compare` sẽ không hoạt động. Dự đoán lưu trữ với ngày.
- **Hồ sơ thưa thớt = độ tự tin thấp**: Nếu psychology/formulation.md có 10 dòng, tín hiệu tăng trưởng là mỏng. Quỹ đạo độ tự tin cao cần hồ sơ giàu.
- **Tăng trưởng là bối cảnh**: Một nhân vật có thể cho thấy GROWTH trong điều chỉnh cảm xúc nhưng REGRESSION trong tham gia học tập. Kỹ năng đánh giá toàn bộ, nhưng bạn đọc sắc thái.
