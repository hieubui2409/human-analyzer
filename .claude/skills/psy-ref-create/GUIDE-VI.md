# psy:ref-create — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

`psy:ref-audit --discover` cờ: "Hồ sơ của Nhân vật A mô tả 'luôn hy sinh cho người khác, bỏ qua nhu cầu của riêng mình' — đây là một mẫu, nhưng chúng tôi không có tệp lý thuyết cho nó." Bạn có thể liên kết tới "phức tạp người cứu rỗi" chung, nhưng sắc thái là kiệt sức từ lòng tốt. Kỹ năng này xây dựng một tệp tài liệu tham khảo mới (`benevolence-fatigue.md`), nghiên cứu nó trong DSM-5/ICD-11/tài liệu, viết các phần bắt buộc (định nghĩa, nguồn gốc, cơ chế, bối cảnh Việt Nam, nghiên cứu trường hợp), và tích hợp nó vào thư viện.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Lược đồ bắt buộc**: Mỗi tệp tham chiếu có 6 phần. Không có đường tắt. Điều này đảm bảo tính nhất quán và ngăn chặn các lý thuyết không hoàn thành.
- **Hỗ trợ khoa học là không thể thương lượng**: Mỗi lý thuyết PHẢI trích dẫn DSM-5, ICD-11, hoặc tài liệu được xem xét ngang hàng. Không có lý thuyết ban đầu; chúng tôi ghi lại thực tế lâm sàn, không phát minh.
- **Bối cảnh văn hóa Việt Nam là bắt buộc**: Lý thuyết này biểu hiện như thế nào trong động lực gia đình Việt Nam? Các yếu tố văn hóa quan trọng (Nhịn, hiếu thảo, tiết kiệm mặt).
- **Nghiên cứu trường hợp liên kết lý thuyết với dự án của chúng tôi**: Cho thấy cách lý thuyết này áp dụng cho một nhân vật thực sự trong kho của chúng tôi.

## 3. Đường dẫn học tập

**Xây dựng nhanh chóng:** `psy:ref-create attachment-trauma --quick` — tệp tối thiểu, điền sau.

**Tạo đầy đủ:** `psy:ref-create benevolence-fatigue --character hieu` — toàn diện với trường hợp học.

**Kỹ thuật ngược:** `psy:ref-create --from-behavior "Always helping others, never asking for help, eventual burnout"` — mô tả hành vi, kỹ năng đề xuất lý thuyết.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Điền khoảng trống được phát hiện

> Bạn: "`psy:ref-audit --discover` tìm thấy: 'Nhân vật A cho thấy sự kiệt sức từ chăm sóc nhưng không có lý thuyết nào bao gồm kiệt sức từ lòng tốt.' Tạo tài liệu tham khảo?"
> Kỹ năng: `psy:ref-create benevolence-fatigue --character hieu --quick`
> → Xây dựng tệp tham chiếu với định nghĩa + cơ chế. Đánh dấu các phần 4–6 (bối cảnh Việt Nam, nghiên cứu trường hợp, v.v.) là TODO cho việc mở rộng sau này.

### Trường hợp sử dụng: Kỹ thuật ngược từ hành vi

> Bạn: "Tôi thấy một mẫu: Nhân vật C tránh cam kết vì anh ta mong đợi bỏ rơi. Lý thuyết này là gì?"
> Kỹ năng: `psy:ref-create --from-behavior "Nhân vật C avoids commitment, expects abandonment, preemptively withdraws"`
> → Tìm kiếm tài liệu, đề xuất "sợ hãi-tránh gắn bó" (đã tồn tại) hoặc đề xuất lý thuyết mới nếu không có kết quả trùng khớp. Người dùng xác nhận.

### Trường hợp sử dụng: Tài liệu tham khảo đầy đủ với nghiên cứu trường hợp

> Bạn: "Chúng ta cần một tài liệu tham khảo đầy đủ về 'sincere misbelief' (tin rằng hình ảnh sai lệch mà người ta đã xây dựng). Tạo nó."
> Kỹ năng: `psy:ref-create sincere-misbelief --character chiến`
> → Tạo tệp với tất cả 6 phần. Định nghĩa + Freud/Jung trích dẫn. Nghiên cứu trường hợp: Kêu gọi câu chuyện mẹ kế của Nhân vật C. Cập nhật INDEX.md. Sẵn sàng sử dụng.

## 5. Cảnh báo quan trọng

- **Yêu cầu nghiên cứu**: Đừng tạo xây dựng trống. Kỹ năng giả định bạn sẽ nghiên cứu lý thuyết (hoặc nó sẽ hướng dẫn bạn). Mã ISBN DSM-5, mã ICD-11, tên tác giả quan trọng.
- **Bối cảnh văn hóa Việt Nam không phải là tùy chọn**: Mỗi lý thuyết phải giải thích cách nó xuất hiện trong văn hóa Việt Nam. Không phải "tâm lý học Anh-xứ."
- **Nghiên cứu trường hợp phải được hỗ trợ bằng bằng chứng**: Nếu tài liệu tham khảo mô tả "chấn thương bỏ rơi," nghiên cứu trường hợp phải truy tìm bằng chứng từ các vật liệu (ưu tiên P{N}), không phải suy đoán.
- **Cập nhật INDEX.md là tự động**: Kỹ năng cập nhật chỉ mục tài liệu tham khảo. Bạn không cần làm điều đó thủ công, nhưng hãy xác minh nó là chính xác.
- **Liên kết đến sau**: Tạo tài liệu tham khảo không tự động liên kết nó với các hồ sơ. Sau khi tạo, thêm thủ công `[link](../../references/{theory}.md)` nơi thích hợp, sau đó chạy `psy:ref-scan --theory {name}` để xác minh phạm vi bao phủ.
