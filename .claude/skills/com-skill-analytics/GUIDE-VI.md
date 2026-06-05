# com:skill-analytics — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn có 58 kỹ năng khung lan rộng trên 6 miền. Một số được sử dụng rộng rãi, một số bị hỏng, một số chi phí token. Trước khi phát hành, sau khi thêm một script, hoặc khi theo dõi một lỗi kỳ lạ, bạn muốn một ảnh chụp sức khỏe nhanh: những kỹ năng nào bị hỏng? Cái gì phụ thuộc vào cái gì? Những nền tảng nào chưa đăng trong vài tuần? Tác nhân phụ đáng tin cậy như thế nào? com:skill-analytics cung cấp cho bạn 11 ống kính khác nhau để trả lời những câu hỏi này.

## 2. Khái niệm cốt lõi (mô hình tư duy)

**11 ống kính quan sát:** Mỗi ống kính trả lời một câu hỏi — sức khỏe cơ sở hạ tầng (S2), biểu đồ phụ thuộc (P3), tương tác kỹ năng (P4), mô hình sử dụng (S1), khoảng cách bảo hiểm (S4), nhịp độ nội dung (M5), bảng điều khiển thống nhất (M1), sức khỏe bộ nhớ (M6), độ tin cậy tác nhân phụ (M3), pháp y (P1), chuỗi quy trình (S5).

**Chia tách xác định:** Script thu thập (cú pháp, nhập, số liệu). LLM đánh giá (mô-đun không sử dụng này có chết hay hoãn không? Kỹ năng mồ côi có ý định không?). Script quá cờ; con người lọc.

**Quan sát chỉ đọc:** Thu thập dữ liệu đo từ xa, đếm, cấu trúc. Không bao giờ sửa đổi mã. Sử dụng cho chẩn đoán, không phải điều trị.

**Phạm vi = chỉ các khung của dự án:** Theo dõi kỹ năng mat, psy, cre, gro, orc, com. Bỏ qua ck (công cụ nhà phát triển được người dùng gọi).

## 3. Lộ trình học tập

**Lần chạy đầu tiên:** `com:skill-analytics --health`. Quét tất cả các kỹ năng để tìm lỗi cú pháp, nhập bị hỏng, vấn đề perf. Tốn 30 giây. Đường cơ sở tốt.

**Tiếp theo:** Thử `--dashboard`. Nhận được tất cả 11 ống kính cùng một lúc, tạo ra một bảng đèn giao thông màu sắc. Một trang, sức khỏe toàn bộ dự án.

**Khi bạn phát triển:** Sử dụng `--deps` để ánh xạ các mô-đun quan trọng; `--coverage` để tìm các lần kích hoạt trùng lặp; `--reliability` để theo dõi các lỗi tác nhân phụ theo thời gian; `--forensics --all-sessions` để tái cấu trúc những gì đã xảy ra trong các phiên trước.

## 4. Trường hợp sử dụng (mỗi = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Tìm một script bị hỏng nhanh chóng

> Bạn: "kỹ năng nào bị hỏng?"
> Kỹ năng: `com:skill-analytics --health`. Quét cú pháp với `ast`, bash `-n`, nhập. Báo cáo `psy:crossref/scripts/validate.py — SyntaxError: line 42`. Bạn sửa nó, chạy lại.

### Trường hợp sử dụng: Sức khỏe dự án nhìn một cái nhìn

> Bạn: "give me the health dashboard"
> Kỹ năng: `com:skill-analytics --dashboard`. Tạo ra bảng tóm tắt đèn giao thông: xanh = lành mạnh, vàng = cảnh báo, đỏ = bị hỏng. Hiển thị sức khỏe, bảo hiểm, bộ nhớ, độ tin cậy, nội dung trên mỗi kỹ năng. Một trang, sẵn sàng quyết định.

### Trường hợp sử dụng: Ánh xạ phụ thuộc và tìm các mô-đun quan trọng

> Bạn: "những mô-đun nào là quan trọng?"
> Kỹ năng: `com:skill-analytics --deps --critical`. Xây dựng biểu đồ nhập, cờ mô-đun với ≥20 fan-in. Báo cáo: `platform_lib/telemetry.py — 23 importers — CRITICAL`. Bạn biết cái này là cần thiết.

### Trường hợp sử dụng: Theo dõi độ tin cậy của tác nhân phụ theo thời gian

> Bạn: "how reliable are subagents?"
> Kỹ năng: `com:skill-analytics --reliability --days 30`. Quét nhật ký lỗi, đếm thành công/api_error/timeout trên mỗi loại tác nhân. Báo cáo: `researcher — 87% success, 10% timeout, 3% api_error`. Xu hướng cho thấy liệu có gì đó đang suy giảm không.

### Trường hợp sử dụng: Tìm kỹ năng không sử dụng hoặc giá trị thấp

> Bạn: "những kỹ năng nào mà chúng tôi không bao giờ sử dụng?"
> Kỹ năng: `com:skill-analytics --usage --tokens`. Đếm các cuộc gọi trên mỗi kỹ năng + chi phí token. Báo cáo: `gro:career-path — 2 invocations, 850 tokens/call — candidate for decommission?`. LLM sau đó quyết định xem nó có thực sự chết hay chỉ hoãn lại.

### Trường hợp sử dụng: Kiểm toán sức khỏe của đường dẫn nội dung

> Bạn: "are we posting regularly?"
> Kỹ năng: `com:skill-analytics --content --since 2026-04-01`. Đếm bài đăng trên mỗi nền tảng, phát hiện ngày đăng bài cuối cùng, khoảng cách nhịp độ. Báo cáo: `facebook — last post 2026-05-10, 3 posts in 30 days, cadence OK | linkedin — no posts since 2026-03-15 — INACTIVE`.

## 5. Những cảnh báo quan trọng

**Quá cờ bằng thiết kế.** Một mô-đun được báo cáo "không sử dụng" (0 nhập trực tiếp) có thể vẫn còn sống thông qua tự nhập `__init__.py`. Script chỉ báo cáo số lượng thô; LLM diễn giải.

**Đây là chẩn đoán, không phải điều trị.** Health-check cờ một script bị hỏng; bạn sửa nó. Workflow-chains hiển thị độ lệch từ các tài liệu định tuyến; bạn quyết định xem chúng có ý định hay drift.

**Pháp y cần bảng điểm.** `--forensics` tái cấu trúc các phiên từ các tệp siêu dữ liệu JSONL. Nếu một phiên không có siêu dữ liệu, pháp y không đầy đủ.

**Phạm vi là các khung, không phải ck.** Nếu bạn yêu cầu `--deps` trên toàn bộ dự án và tự hỏi tại sao các kỹ năng ck bị thiếu, đó là bằng thiết kế. Điều này theo dõi 58 kỹ năng dự án, không phải 200+ kỹ năng ck.

**Kiểm tra sức khỏe bộ nhớ là dry-run theo mặc định.** Sử dụng `--memory --fix` để xem những gì sẽ được làm sạch; `--memory --fix --apply` để thực sự viết. Không bao giờ tự động xóa mà không có `--apply`.
