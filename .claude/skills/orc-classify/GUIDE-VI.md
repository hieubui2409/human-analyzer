# orc:classify — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Không phải tất cả công việc đều có rủi ro như nhau. Chỉnh sửa dòng thời gian của Nhân vật A là đơn giản. Cập nhật công thức của Nhân vật B với tâm lý học mới rủi ro hơn—nó ảnh hưởng đến sự nhất quán lâm sàng. Thay đổi khung động quan hệ đa nhân vật là rủi ro nhất. Classify cho bạn biết trước: "đây là high_risk, vì vậy lập kế hoạch cho phù hợp." Nó tiết kiệm cho bạn từ việc khám phá các vấn đề muộn.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Ba chế độ rủi ro:** tiny (nhanh, ma sát thấp), normal (cần chăm sóc vừa phải), high_risk (lễ nghi đầy đủ cần thiết). Mỗi chế độ có các bước lễ nghi khác nhau và chiến lược chứng minh.

**Các cổng cứng kích hoạt high_risk ngay lập tức.** Nếu bạn đang thay đổi sự nhất quán đa nhân vật, tham chiếu lâm sàng, dòng thời gian, hoặc nội dung công khai với tên thật, nó là high_risk trước khi đếm cờ.

**Cờ tích lũy.** Thậm chí nếu không có cổng cứng, 4+ cờ = high_risk. Ví dụ: chỉnh sửa tâm lý hồ sơ + chủ đề nhạy cảm + tham chiếu đa nhân vật = 3 cờ = bình thường. Thêm một cái nữa, nó trở thành high_risk.

**Lễ nghi tỷ lệ.** Tiny = tự kiểm tra nhanh. Normal = dàn bài + tham chiếu chéo. High_risk = bootstrap đầy đủ + kế hoạch + kiểm tra hồ sơ + kiểm tra lâm sàng.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:classify "write a LinkedIn post about Nhân vật A"` — chế độ tiny. Nhanh, không cần lễ nghi.

**Nhiệm vụ bình thường:** `orc:classify "update Nhân vật B's psychology/attachment-style.md"` — chế độ bình thường. Yêu cầu dàn bài + kiểm tra tham chiếu chéo.

**Nhiệm vụ rủi ro cao:** `orc:classify "add new relationship between Nhân vật A and Nhân vật C"` — chế độ high_risk. Lễ nghi đầy đủ.

**Chế độ tự động:** `orc:classify --auto` — cho phép nó suy luận từ diff git.

**Kiểm tra hiện tại:** `orc:classify --show` — xem chế độ nào bạn đang ở hiện tại.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Phân loại nhanh cho nhiệm vụ đơn giản

> Bạn: "Classify: write a quick post about Nhân vật A's mentoring philosophy"
>
> Kỹ năng: Phát hiện "viết bài" → Công việc Tạo Nội dung. Đếm cờ: sự nhất quán giọng viết (cờ 11). Tổng: 1 cờ = chế độ tiny. Đầu ra: "Tiny mode. Tự kiểm tra nhanh về âm điệu/độ chính xác. Sẵn sàng triển khai."

### Trường hợp sử dụng: Nhiệm vụ chế độ bình thường với lễ nghi

> Bạn: "Classify: update Nhân vật B's timeline with a new milestone"
>
> Kỹ năng: Phát hiện "cập nhật dòng thời gian" → Cập nhật Hồ sơ. Đếm cờ: liên tục dòng thời gian (cổng cứng — kích hoạt high_risk). Đầu ra: "High_risk mode. Lễ nghi cần thiết: bootstrap đầy đủ, kế hoạch, tham chiếu chéo dòng thời gian giữa các nhân vật, kiểm tra lâm sàng."

### Trường hợp sử dụng: Tự động phân loại từ thay đổi git gần đây

> Bạn: "Classify --auto"
>
> Kỹ năng: Đọc diff git, thấy thay đổi trong psychology/ + relationships/, phát hiện các tệp đa nhân vật. Đếm: chỉnh sửa tâm lý hồ sơ (cờ 1) + tham chiếu đa nhân vật (cờ 6) = 2 cờ = chế độ bình thường. Đầu ra: "Normal mode. Chạy dàn bài + kiểm tra tham chiếu chéo."

### Trường hợp sử dụng: Kiểm tra phân loại hiện tại

> Bạn: "Show me the current classification"
>
> Kỹ năng: Đọc state.json, hiển thị chế độ, giai đoạn, và các bước lễ nghi đã được gán trong phiên này.

## 5. Những cảnh báo quan trọng

- **Phân loại là cố vấn.** Nó khuyến nghị lễ nghi, nhưng bạn quyết định có tuân theo hay không. Nếu bạn bỏ qua các bước được khuyến nghị về high_risk và có gì đó bị hỏng, đó là lỗi của bạn.
- **Chế độ tự động là heuristic.** Nó suy luận từ diff git và tên nhánh, điều này có thể bỏ lỡ ngữ cảnh. Nếu không chắc chắn, mô tả nhiệm vụ một cách rõ ràng.
- **Lễ nghi không phải là đảm bảo sự chính xác.** Lễ nghi high_risk (bootstrap đầy đủ, xem xét lâm sàng, kiểm tra tham chiếu chéo) làm giảm rủi ro, nhưng không loại bỏ nó.
- **Phân loại lại nếu phạm vi thay đổi.** Nếu bạn bắt đầu với "bài viết nhanh" nhưng thêm nội dung đa nhân vật giữa chừng, chạy lại phân loại. Nó nhanh.
