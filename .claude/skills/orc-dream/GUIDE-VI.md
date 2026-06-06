# orc:dream — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Trong những tuần lễ, bộ nhớ tích lũy. Bạn nhận thấy "Nhân vật B avoids under pressure" và riêng biệt "Nhân vật B deflects with humor"—cả hai đúng, nhưng rải rác. Dream hợp nhất: hợp nhất các kiến thức liên quan, loại bỏ các kiến thức cũ (thông tin lỗi thời), tăng cường các mẫu độ tin cậy cao, và thăng cấp chúng vào bộ nhớ tác nhân để các tác nhân miền sử dụng chúng. Đó là bảo trì giữ hệ thống học tập của bạn sắc nét.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Năm giai đoạn hợp nhất:** Scan (kiểm kê), Merge (kết hợp liên quan), Prune (loại bỏ cũ), Strengthen (điền khoảng trống), Instincts (vòng đời: phân rã, lưu trữ, phân cụm, thăng cấp).

**Bộ nhớ có tín hiệu và nhiễu.** Các bản năng tốt (gia tăng 3+ lần, conf ≥0.80) trở thành bộ nhớ tác nhân. Các bản năng yếu (1-2 bằng chứng, conf <0.4, 30+ ngày) được lưu trữ. Dream tự động hóa quá trình sơ lọc này.

**Các cụm bề mặt các mẫu ẩn.** Khi các bản năng cụm (ví dụ, 4 bản năng về Nhân vật B's avoidance), dream gợi ý một mẫu cốt lõi đáng ghi lại rõ ràng.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:dream --scan` — kiểm tra sức khỏe bộ nhớ. Bao nhiêu bộ nhớ? Bao cũ? Có liên kết bị hỏng không?

**Dọn dẹp nhẹ:** `orc:dream --merge` — tìm và hợp nhất các bộ nhớ trùng lặp.

**Bảo trì nặng:** `orc:dream --full` — tất cả các giai đoạn bao gồm vòng đời bản năng (phân rã, lưu trữ, thăng cấp).

**Tiêu điểm bản năng:** `orc:dream --instincts` — chỉ xử lý vòng đời bản năng, bỏ qua các giai đoạn bộ nhớ.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kiểm tra sức khỏe bộ nhớ

> Bạn: "Is our memory system healthy?"
>
> Kỹ năng: Chạy --scan, báo cáo: 47 bộ nhớ, cũ nhất từ 60 ngày trước, 3 liên kết bị hỏng (các lý thuyết được đề cập nhưng tệp bị xóa). Bạn biết: bộ nhớ đang trở nên lớn, có các mục cũ, và có những mâu thuẫn để khắc phục.

### Trường hợp sử dụng: Hợp nhất các kiến thức trùng lặp

> Bạn: "Memories feel repetitive. Merge overlapping ones."
>
> Kỹ năng: Tìm thấy: "character-b-attachment-pattern" + "character-b-avoidance-triggers" đều mô tả Nhân vật B's attachment. Đề xuất hợp nhất thành "character-b-attachment-avoidance-dynamics". Bạn xác nhận. Dream hợp nhất và cập nhật MEMORY.md index.

### Trường hợp sử dụng: Hợp nhất đầy đủ với thăng cấp bản năng

> Bạn: "Full dream maintenance. Clean everything up."
>
> Kỹ năng: Quét, hợp nhất, cắt tỉa các bộ nhớ cũ (2+ tháng tuổi), sau đó chạy vòng đời bản năng: phân rã các bản năng độ tin cậy thấp, lưu trữ các bản năng rất cũ, cụm các bản năng hoạt động, thăng cấp 3 bản năng độ tin cậy cao lên bộ nhớ tác nhân. Báo cáo tóm tắt: hợp nhất 5 bộ nhớ, lưu trữ 2, thăng cấp 3 bản năng.

## 5. Những cảnh báo quan trọng

- **Dream đề xuất; bạn phê duyệt.** Nó không bao giờ tự động xóa. Bạn thấy trước/sau cho mỗi hợp nhất và cắt tỉa.
- **Phân rã bản năng là toán học.** Độ tin cậy dần dần giảm trừ khi được gia tăng. Nếu bạn thấy một bản năng tốt đang phân rã, gia tăng nó.
- **Phân cụm là heuristic.** Nếu phân cụm tìm thấy các mẫu sai (chồng chéo từ nhưng các bản năng không liên quan), bỏ qua gợi ý.
- **Thăng cấp không tự động thực hiện.** Dream gợi ý thăng cấp các bản năng lên bộ nhớ tác nhân; bạn vẫn phải phê duyệt và LLM ghi lại cập nhật.
