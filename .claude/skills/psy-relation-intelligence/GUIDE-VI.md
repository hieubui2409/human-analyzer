# psy:relation-intelligence — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn muốn viết nội dung về mối quan hệ kết nghĩa của Nhân vật A và Nhân vật B. Thay vì nhìn vào màn hình trắng, kỹ năng này khai thác biểu đồ quan hệ của họ: trích xuất sự kiện từ cả hai hồ sơ (cuộc gặp, sự kiện, trích dẫn, cột mốc GRO), xếp hạng chúng theo tầng bằng chứng (vật liệu P1 = cao nhất, tâm lý ngầm = thấp hơn), kiểm tra các thẻ bảo mật (PRIVATE, CONFIDENTIAL, ANONYMIZE), và đề xuất các góc độ: "Lễ kết nghĩa như một điểm chuyển mình" (bằng chứng CAO, sự liên kết 0,9, sự đồng ý OPEN) so với "Lỗi yếu của Nhân vật B trong cuộc khủng hoảng cờ bạc" (bằng chứng TRUNG BÌNH, lo ngại về ranh giới khủng hoảng, sự đồng ý REVIEW). Bạn nhận được các góc độ được xếp hạng sẵn sàng cho cre:post-writer, không phải dữ liệu thô.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Lọc ba tầng**: (1) Trích xuất các sự kiện với các tầng bằng chứng. (2) Kiểm tra các thẻ bảo mật + các ký hiệu khủng hoảng. (3) LLM tổng hợp các góc độ; kịch bản xếp hạng chúng.
- **Sự đồng ý là thất bại kín**: Bất kỳ sự kiện BLOCKED (thẻ PRIVATE hoặc ký hiệu khủng hoảng) nào cũng làm mất sạch góc độ. Các góc độ bị chặn chìm xuống dưới cùng của thứ hạng, được cờ ⛔, không bao giờ được thả một cách im lặng.
- **Ngữ nghĩa nhân vật chính**: Mỗi góc độ có một nhân vật POV (tập trung kêu gọi lớn nhất). cre:post-writer chỉ tải giọng nói của nhân vật đó; nhân vật khác xuất hiện khi được mô tả bởi nhân vật chính (Quy tắc A2: tính xác thực của giọng nói).
- **Ranh giới chấn thương**: darkness/traumas.md không bao giờ được đọc vào dữ liệu góc độ. Sự tồn tại được ghi chú như siêu dữ liệu, nhưng chi tiết được loại trừ. Cổng an toàn.

## 3. Đường dẫn học tập

**Một dyad:** `psy:relation-intelligence --dyad hieu hoa` — xem các góc độ được xếp hạng cho anh em kết nghĩa.

**Tất cả dyad:** `psy:relation-intelligence --all` — khai thác tất cả các cặp cùng một lúc.

**Ghi đè POV:** `psy:relation-intelligence --dyad hoa chien --character character-b` — quan điểm của Nhân vật B về hướng dẫn Nhân vật C.

**Với tín hiệu biểu đồ:** `psy:relation-intelligence --dyad hieu chien --graph-signal` — làm giàu với KG nếu có sẵn.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Khai thác góc độ dyadic

> Bạn: "Những góc độ nội dung nào tồn tại giữa Nhân vật A và Nhân vật B?"
> Kỹ năng: `psy:relation-intelligence --dyad hieu hoa`
> → Đầu ra:
> - ★★★ **"The Kết Nghĩa Turning Point"** | chính: Nhân vật A | sự đồng ý: OPEN | sự liên kết: 0,92 | bằng chứng: vật liệu P1 + cả hai dòng thời gian
> - ★★★ **"Supporting Through Crisis"** | chính: Nhân vật B | sự đồng ý: REVIEW (đề cập cờ bạc, cần cổng độ nhạy) | sự liên kết: 0,85
> - ★★ **"Unequal Sacrifice"** | chính: Nhân vật A | sự đồng ý: OPEN | sự liên kết: 0,78 | lưu ý: Nhân vật A cho nhiều hơn nhận được
> → cre:post-writer tải góc độ OPEN hàng đầu trước tiên.

### Trường hợp sử dụng: Góc độ hướng dẫn qua các nhân vật

> Bạn: "Câu chuyện nội dung nào xung quanh Nhân vật A hướng dẫn Nhân vật C?"
> Kỹ năng: `psy:relation-intelligence --dyad hieu chien`
> → Các góc độ hàng đầu: "F15 Scholarship Journey" (Nhân vật C's POV, ăn mừng cột mốc), "Mentor's Burden" (Nhân vật A's POV, ghi chú rủi ro kiệt sức). Cả hai OPEN để xuất bản.

### Trường hợp sử dụng: Tất cả dyad cùng một lúc

> Bạn: "Những góc độ nội dung nào tồn tại trên tất cả ba nhân vật?"
> Kỹ năng: `psy:relation-intelligence --all --json`
> → JSON: liệt kê tất cả 3 dyad × các góc độ được xếp hạng. Kịch bản xử lý để tự động hóa hạ lưu (lựa chọn góc độ, định tuyến giọng nói, v.v.).

## 5. Cảnh báo quan trọng

- **Gợi ý nhân vật chính có thể ghi đè được**: Kỹ năng đề xuất Nhân vật A là "chính" (cạnh nhiều hơn), nhưng bạn có thể đặt `--character character-b` để lật quan điểm. Thay đổi giọng nói nào tải trong cre:post-writer.
- **Các góc độ REVIEW cần quyết định**: Các góc độ được đánh dấu REVIEW có các vấn đề sự đồng ý biên giới. Trước khi xuất bản, hãy xác nhận: điều này có thể xuất bản được không, hay chúng tôi nên ẩn danh / khung lại?
- **Ranh giới chấn thương là nghiêm ngặt**: darkness/traumas.md không bao giờ được phân tích cú pháp cho dữ liệu góc độ. Nếu một góc độ có vẻ như rò rỉ chi tiết chấn thương, điều tra — có thể là lỗi hoặc dữ liệu trong tệp sai.
- **Các tầng bằng chứng thông báo xếp hạng, không cổng**: Bằng chứng P1 xếp hạng cao hơn, nhưng một góc độ P3 có thể được xuất bản nếu sự đồng ý là OPEN. Tầng là tín hiệu độ tin cậy, không cổng phê duyệt.
- **Tín hiệu biểu đồ là cải tiến tùy chọn**: KG (biểu đồ kiến thức) làm giàu các cạnh nếu có sẵn; mà không có nó, kỹ năng sử dụng các tệp quan hệ trực tiếp. Cả hai đường dẫn làm việc.
