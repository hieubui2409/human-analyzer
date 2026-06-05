# orc:graph — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đang khám phá hồ sơ của Nhân vật B và muốn hiểu: những lý thuyết nào áp dụng cho cô ấy? những nhân vật khác nào tương tác với cô ấy? những tài liệu nào đề cập đến cô ấy? Graph truy vấn biểu đồ kiến thức (dẫn xuất từ markdown) và hiển thị tất cả các tệp được kết nối. Giống như một công cụ tìm kiếm tệp cho các quan hệ.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Biểu đồ kiến thức = kề markdown-dẫn xuất.** Các tệp và liên kết rõ ràng của chúng tạo nên các nút và cạnh. Không toàn diện (bỏ lỡ các nội dung văn bản), nhưng nhanh chóng và có thể truy vấn.

**Hops = khoảng cách.** 1 hop = các tệp riêng của Nhân vật B. 2 hops = các tệp trích dẫn Nhân vật B + các tệp Nhân vật B trích dẫn.

**Biểu đồ có thể loại bỏ được.** Được xây dựng lại một cách lười biếng; luôn đồng bộ với markdown vì nó dẫn xuất tươi.

## 3. Đường dẫn học tập

**Truy vấn một nhân vật:** `orc:graph query character-a --hops 2` — Nhân vật A và các tệp liên quan.

**Truy vấn một lý thuyết:** `orc:graph query savior-complex --hops 1 --types profile` — những hồ sơ nào trích dẫn lý thuyết này.

**Kiểm tra sức khỏe:** `orc:graph stats` — bao nhiêu nút/cạnh, theo loại.

**Xác thực:** `orc:graph validate` — tìm mồ côi, tham chiếu bị thiếu.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Tìm các tệp liên quan đến một nhân vật

> Bạn: "Show me everything related to Nhân vật B."
>
> Kỹ năng: Truy vấn biểu đồ: Nhân vật B (1 hop) = 25 tệp hồ sơ của cô ấy. Nhân vật B (2 hops) = các lý thuyết cô ấy trích dẫn + các nhân vật cô ấy được liên kết + các tài liệu đề cập đến cô ấy. Bạn thấy toàn bộ mạng lưới quan hệ.

### Trường hợp sử dụng: Tìm những hồ sơ nào trích dẫn một lý thuyết

> Bạn: "Which characters reference attachment theory?"
>
> Kỹ năng: Truy vấn: nút lý thuyết "attachment-style" → cạnh vào từ các hồ sơ. Hiển thị: Nhân vật B, Nhân vật A, Nhân vật C tất cả đều trích dẫn nó. Bạn biết những hồ sơ nào để xem xét tính nhất quán.

### Trường hợp sử dụng: Kiểm tra sức khỏe biểu đồ

> Bạn: "Is the knowledge graph healthy?"
>
> Kỹ năng: Thống kê: 127 nút, 234 cạnh, 8 mồ côi (tệp không thể tiếp cận), 2 tham chiếu bị thiếu (các tệp trích dẫn các lý thuyết bị xóa). Bạn biết: hầu như lành mạnh, nhưng 8 mồ côi cần điều tra.

## 5. Những cảnh báo quan trọng

- **Biểu đồ là cố vấn, không toàn diện.** Các kịch bản quét văn bản (psy:ref-scan) có thẩm quyền cho "lý thuyết này được sử dụng ở đâu."
- **Biểu đồ bỏ lỡ văn bản tiếng Việt.** Lý thuyết được đề cập trong bình luận tiếng Việt? Biểu đồ sẽ không thấy nó. Sử dụng quét văn bản để hoàn chỉnh.
- **1 hop ≠ tất cả tệp.** Tại hops=1, bạn chỉ nhận được tệp riêng của một nhân vật. Tăng hops để đạt đến các quan hệ.
- **Xây dựng lại là tự động.** Nếu markdown đã thay đổi, biểu đồ re-dẫn xuất trên truy vấn tiếp theo. Không cần đồng bộ thủ công.
