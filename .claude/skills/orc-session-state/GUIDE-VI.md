# orc:session-state — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn tiếp tục một phiên từ giờ hoặc ngày hôm trước. Bạn đang làm gì? Những hồ sơ nào bạn đã chạm tới? Chế độ công việc là gì (tiny/normal/high_risk)? Trạng thái phiên nhớ. Nó cũng theo dõi các sự kiện miền đang chờ, các nạp vào hoạt động trong MAT, và nhân vật nào bạn tập trung vào. Điều này cho phép bạn nhặt lên giữa dự án mà không cần đọc lại mọi thứ.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Trạng thái JSON liên tục.** `.claude/session-state/state.json` giữ tất cả siêu dữ liệu phiên. Các móc tự động cập nhật nó khi công việc xảy ra (trên SessionStart, Stop, và khi các sự kiện miền kích hoạt).

**Theo dõi nhận thức khung.** Trạng thái phiên theo dõi những miền nào hoạt động (MAT/PSY/CRE/GRO), những nhân vật nào được chạm tới, các sự kiện đang chờ, và các đường ống hoạt động.

**Lưu trữ lịch sử.** Khi bạn `--archive`, trạng thái hiện tại được lưu vào markdown được dấu thời gian. Hữu ích để nhìn lại những gì bạn đã hoàn thành.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:session-state --show` — xem trạng thái hiện tại.

**Cuối phiên:** `orc:session-state --archive` — lưu tiến trình trước khi dừng.

**Trước `/compact`:** `orc:session-state --compact-digest` — ghi tóm tắt được giới hạn để ngữ cảnh khung tồn tại nén.

**Nếu bị hỏng:** `orc:session-state --reset` — xóa trạng thái (giữ lưu trữ).

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kiểm tra tiến trình phiên

> Bạn: "What's the current session state?"
>
> Kỹ năng: Hiển thị: Mode=normal, Phase=creating, Branch=claude/features/hoa-psychology, Profiles touched=[character-b], Content created=[assets/linkedin/260605-post/], Decisions=[Nhân vật B attachment decision], Harness delta=3 files. Bạn thấy: tập trung vào Nhân vật B, tạo nội dung, rủi ro bình thường, 3 thay đổi harness.

### Trường hợp sử dụng: Lưu trữ phiên trước khi dừng

> Bạn: "Archive the session, I'm stopping."
>
> Kỹ năng: Lưu trạng thái hiện tại vào `.claude/session-state/archive/260605-1430.md`, đặt lại state.json thành mặc định. Lịch sử phiên được bảo toàn; phiên tiếp theo bắt đầu tươi.

### Trường hợp sử dụng: Ghi tóm tắt nhỏ gọn trước `/compact`

> Bạn: "Save a compact digest before compressing context."
>
> Kỹ năng: Chạy `--compact-digest`, ghi `.claude/session-state/compact-digest.json` với top-5 sự kiện gần đây mỗi miền. Khi tiếp tục, `orc:bootstrap` re-injects cái này để ngữ cảnh khung tồn tại nén.

## 5. Những cảnh báo quan trọng

- **Trạng thái là siêu dữ liệu tích cực.** Thay đổi state.json không sửa đổi hồ sơ; chúng là ghi chú về những gì xảy ra.
- **Lưu trữ là chỉ đọc.** Các lưu trữ cũ giúp bạn hiểu lịch sử; chúng không tự động khôi phục.
- **Các móc tự động cập nhật trạng thái.** Bạn hiếm khi cần thủ công cập nhật trạng thái; các móc xử lý hầu hết các cập nhật.
- **Tóm tắt nhỏ gọn có giới hạn kích thước.** Giữ ≤8 KB để nó không làm bại công việc nén ngữ cảnh.
