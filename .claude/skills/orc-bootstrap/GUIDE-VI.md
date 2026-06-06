# orc:bootstrap — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bắt đầu công việc trên một dự án phức tạp, đa nhân vật có nghĩa là mang theo ~7,400 dòng dữ liệu hồ sơ trong tâm trí. Điều đó không hiệu quả và dễ gây lỗi. Bootstrap cho phép bạn tải chính xác ngữ cảnh bạn cần—từ quét INDEX nhanh 5 phút đến погружение hồ sơ đầy đủ 30 phút. Bạn kiểm soát độ sâu.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Độ sâu ngữ cảnh là một phổ.** Quick (chỉ INDEX) là nhanh nhất để nhắc nhở. Hồ sơ đầy đủ mất thời gian nhưng mang lại chính xác lâm sàng. Các hồ sơ lite (~400 dòng tổng cộng) chia sẻ sự khác biệt. Tải nhận thức ý định là thông minh: nếu bạn viết nội dung LinkedIn, bạn không cần chi tiết dòng thời gian, chỉ cần writing-voice.

**Thứ tự đọc quan trọng.** Hồ sơ được tải theo thứ tự ưu tiên—công thức trước tiên (dày đặc nhất về lâm sàng), sau đó cơ chế phòng vệ, sau đó quan hệ. Điều này đảm bảo bạn hấp thụ nội dung tín hiệu cao nhất sớm.

**Trạng thái phiên di chuyển.** Bootstrap đọc và báo cáo trạng thái phiên hiện tại của bạn (chế độ, giai đoạn, những nhân vật nào bạn đã chạm tới). Điều này giúp bạn tiếp tục mà không mất ngữ cảnh.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:bootstrap --quick` — 2-3 phút, hãy định hướng trên cả 3 nhân vật một cách thoáng nhìn.

**Phân tích sâu:** `orc:bootstrap --full` — 15-30 phút, tải tất cả. Làm điều này trước các thay đổi rủi ro cao.

**Tiêu điểm nhân vật:** `orc:bootstrap --character character-a` — 5-10 phút, tất cả tệp cho Nhân vật A chỉ.

**Chạy tốc độ:** `orc:bootstrap --lite` — 3 phút, các tóm tắt nén của cả 3 nhân vật.

**Nhận thức ý định:** `orc:bootstrap --intent "write LinkedIn post about Nhân vật B"` — tải chỉ các tệp liên quan đến nhiệm vụ đó.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Định hướng nhanh khi bắt đầu phiên

> Bạn: "Bootstrap, give me a quick overview"
>
> Kỹ năng: Tải INDEX.md cho cả 3 nhân vật, hiển thị git log của 15 lần commit cuối cùng, in trạng thái phiên (chế độ, giai đoạn, những hồ sơ nào được chạm tới). 3 phút. Bạn được định hướng.

### Trường hợp sử dụng: Tải sâu trước chỉnh sửa hồ sơ rủi ro cao

> Bạn: "I'm about to update Nhân vật B's formulation. Load everything for her."
>
> Kỹ năng: Chạy `--character character-b`, tải tất cả tệp trong thư mục của cô ấy (psychology/, relationships/, timeline/, darkness/, light/), kiểm tra các tệp lý thuyết liên quan trong references/, và hiển thị lịch sử git cụ thể của Nhân vật B. Bạn hoàn toàn được thông báo trước khi chỉnh sửa.

### Trường hợp sử dụng: Các hồ sơ lite để hiệu quả token

> Bạn: "I'm running low on context. Give me lite mode."
>
> Kỹ năng: Tải các hồ sơ lite được lưu trong bộ nhớ cache cho cả 3 nhân vật (~120-150 dòng mỗi cái, tổng cộng ~400 dòng). Nhỏ hơn nhiều so với hồ sơ đầy đủ (~7400), đủ cho hầu hết công việc.

### Trường hợp sử dụng: Tải nhận thức ý định để bỏ qua các tệp không liên quan

> Bạn: "I'm writing about Nhân vật A's writing style. Load only what's relevant."
>
> Kỹ năng: Phát hiện từ khóa "viết", tải chỉ `identity/writing-voice.md`, bỏ qua timeline/relationships/darkness, tiết kiệm token. In những gì được tải và những gì bị bỏ qua.

### Trường hợp sử dụng: Kiểm tra những gì đã thay đổi gần đây

> Bạn: "What happened in the last week?"
>
> Kỹ năng: Chạy `--recent`, hiển thị các lần commit git và thay đổi tệp từ 7 ngày cuối cùng, được lọc thành các thay đổi hồ sơ/nội dung/kế hoạch. Cách nhanh để xem công việc nào được thực hiện.

## 5. Những cảnh báo quan trọng

- **Bootstrap là chỉ đọc.** Nó không bao giờ sửa đổi tệp. Nó chỉ thu thập ngữ cảnh cho bạn.
- **Chế độ đầy đủ là token-heavy.** Tất cả 25 tệp hồ sơ × 3 nhân vật là ~7,400 dòng. Sử dụng các chế độ lite hoặc nhận thức ý định để hiệu quả.
- **Các hồ sơ lite là những tóm tắt.** Họ nén ~2,500 dòng cho mỗi nhân vật thành ~150. Hữu ích cho công việc nhanh, nhưng không phải chi tiết cấp lâm sàng.
- **Nhận thức ý định có giới hạn.** Nếu nhiệm vụ của bạn mơ hồ ("công việc trên hồ sơ"), nó có thể tải nhiều hơn cần thiết. Hãy cụ thể: "viết bài", "cập nhật dòng thời gian", "phân tích lâm sàng".
- **Lịch sử git là cố vấn.** Bootstrap hiển thị các lần commit gần đây, nhưng không thực hiện các hoạt động git. Sử dụng `/com:git` cho công việc git thực tế.
