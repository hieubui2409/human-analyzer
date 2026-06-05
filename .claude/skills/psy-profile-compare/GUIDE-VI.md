# psy:profile-compare — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn muốn hiểu bộ ba: Tại sao Nhân vật A và Nhân vật B hoạt động như một dyad, nhưng Nhân vật C cảm thấy như một kẻ ngoài cuộc? Bạn đọc tất cả ba tệp phong cách gắn bó riêng biệt, nhưng song song rõ ràng hơn. Kỹ năng này kéo phong cách gắn bó từ cả ba, hiển thị bảng, và cho thấy: Nhân vật A = an toàn (nền tảng Nhân vật B), Nhân vật B = lo lắng (cần nền tảng), Nhân vật C = sợ hãi-tránh (đẩy và kéo). Mẫu đó giải thích động lực của họ.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Một chiều, tất cả nhân vật**: Bạn chọn một phần (core-wounds, defense-mechanisms, v.v.), kỹ năng trích xuất nó từ tất cả các mục tiêu, và hiển thị chúng song song để bạn thấy các mẫu, tương phản, chồng chéo.
- **Đầu ra dựa trên bảng**: Bảng Markdown với các phát hiện chính trên mỗi hàng. Sạch sẽ, có thể quét, dễ dàng tham chiếu trong lập kế hoạch nội dung.
- **Khám phá chiều**: Các chiều có sẵn ánh xạ tới tệp thực tế (`defense-mechanisms` → `psychology/defense-mechanisms.md`; `relationships/hieu` → `relationships/hieu.md`).

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `psy:profile-compare --dimension defense-mechanisms` — xem tất cả ba, phát hiện mẫu.

**Cặp cụ thể:** `psy:profile-compare --dimension attachment-style --characters hieu,hoa` — tập trung hẹp.

**Chiều phức tạp:** `psy:profile-compare --dimension formulation --characters hieu,hoa,chien` — các mẫu tâm lý sâu nhất.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Phân tích mẫu dyadic

> Bạn: "Tại sao mối quan hệ Nhân vật A và Nhân vật B hoạt động, nhưng Nhân vật C cảm thấy bị bỏ rơi?"
> Kỹ năng: `psy:profile-compare --dimension attachment-style`
> → Bảng cho thấy: Nhân vật A (an toàn), Nhân vật B (lo lắng-chế độ), Nhân vật C (sợ hãi-tránh). Insight: an toàn + lo lắng thường ổn định; sợ hãi-tránh = không thể đoán trước. Đề xuất: nỗi sợ bỏ rơi của Nhân vật C kích hoạt khi anh ấy cảm thấy bị loại trừ.

### Trường hợp sử dụng: Tương phản cơ chế phòng thủ

> Bạn: "Họ đối phó với căng thẳng khác nhau như thế nào?"
> Kỹ năng: `psy:profile-compare --dimension defense-mechanisms --characters hieu,hoa,chien`
> → Nhân vật A: thăng hoa, hài hước, chăm sóc. Nhân vật B: phép chiếu, hợp lý hóa. Nhân vật C: giải rã, tự trách. Đầu ra: bảng + cái nhìn sâu về lý do xung đột leo thang (hiểu lầm cách mỗi người đối phó).

### Trường hợp sử dụng: So sánh tệp mối quan hệ

> Bạn: "Mỗi nhân vật nhận thức mối quan hệ của họ với Nhân vật A như thế nào?"
> Kỹ năng: `psy:profile-compare --dimension relationships/hieu`
> → Kéo `relationships/hieu.md` từ hồ sơ của Nhân vật B và Nhân vật C. So sánh cách mỗi người mô tả mối quan hệ. Làm nổi bật các hiệp hội và bất hòa.

## 5. Cảnh báo quan trọng

- **Các tệp mỏng = so sánh mỏng**: Nếu tệp chiều là thưa thớt (10 dòng), so sánh sẽ là tóm tắt. Chạy psy:health-check trước tiên để đo độ phong phú của tệp.
- **Các tệp mối quan hệ qua các nhân vật được khám phá động**: Nếu bạn yêu cầu `relationships/hieu`, kỹ năng tìm thấy nó trong các thư mục của nhân vật khác tự động.
- **Không phải là kiểm tra tính nhất quán**: Đây là quan sát (sự khác biệt là gì?) không xác thực (điều này có nhất quán không?). Để xác thực, sử dụng psy:crossref.
- **Đầu ra JSON thân thiện với máy**: Nếu bạn đang đưa vào công cụ khác, hãy sử dụng `--json` để xuất ra có cấu trúc.
