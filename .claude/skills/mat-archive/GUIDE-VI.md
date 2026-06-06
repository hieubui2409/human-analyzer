# mat:archive — Hướng dẫn

> Cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Theo thời gian, thư mục tài liệu của bạn đầy lên. Một số tệp cũ, bảo mật hoặc chất lượng thấp. Thay vì tích lũy lộn xộn, bạn muốn đánh dấu chúng là được lưu trữ — ngoài quy trình hoạt động, nhưng vẫn có thể kiểm toán vì các tệp không bao giờ bị xóa. mat:archive cho phép bạn áp dụng các bộ lọc thông minh (ngày tháng cũ, tầng thấp, nhân vật cụ thể, trạng thái bị dừng) và đánh dấu hàng loạt các tệp phù hợp. Bạn luôn nhận được bản xem trước chạy khô trước tiên, vì vậy bạn không bao giờ vô tình lưu trữ sai cái gì.

## 2. Khái niệm cốt lõi (mô hình tinh thần)

**Được lưu trữ không phải bị xóa.** Khi bạn lưu trữ một tài liệu, `processing_status` của nó trở thành "archived" — nó được đánh dấu là không hoạt động, nhưng tệp vẫn ở trong `docs/materials/` mãi mãi. Điều này duy trì được một dấu vết kiểm toán: bạn có thể thấy những gì tồn tại khi nào và tại sao nó được lưu trữ.

**Bộ lọc là logic AND.** Nếu bạn nói `--character character-a --before-date 2024-12-31 --tier T5`, kịch bản tìm các tệp trong đó TẤT CẢ ba điều kiện là đúng: tài liệu của Nhân vật A, trước 2024-12-31 và tầng T5. Nó không phù hợp với các tệp T1 của Nhân vật A từ năm 2025 hoặc các tệp T3 trước 2024 từ các nhân vật khác.

**Chạy khô là mặc định.** Mọi lệnh lưu trữ đều mặc định là `--dry-run`, hiển thị cho bạn những gì sẽ được lưu trữ mà không thực sự thay đổi bất cứ điều gì. Để thực hiện thay đổi, bạn phải rõ ràng loại bỏ `--dry-run` khỏi lệnh của bạn (hoặc nó được ngầm định nếu bạn rõ ràng viết mà không có cờ đó sau khi xem lại bản xem trước).

**Bạn kiểm soát ngưỡng.** mat:archive không quyết định sẽ lưu trữ gì; bạn làm. Nó chỉ áp dụng các bộ lọc của bạn. Bạn có thể lưu trữ các tài liệu cũ để giảm tiếng ồn, hoặc các tài liệu bảo mật để ngăn chặn tiếp xúc vô tình, hoặc các mục CRAAP thấp để tập trung vào bằng chứng chất lượng cao.

## 3. Đường dẫn học tập

1. **Lần chạy đầu tiên:** `mat:archive` không có bộ lọc — xem tất cả tài liệu có thể lý thuyết được lưu trữ (chỉ chế độ dry-run).
2. **Lọc theo nhân vật:** `mat:archive --character character-a --dry-run` — sẽ xảy ra điều gì nếu bạn lưu trữ chỉ tài liệu của Nhân vật A?
3. **Lọc theo tuổi:** `mat:archive --before-date 2024-06-01 --dry-run` — lưu trữ tài liệu trước tháng 6 năm 2024 (nội dung cũ).
4. **Kết hợp các bộ lọc:** `mat:archive --character character-b --tier T5 --dry-run` — chỉ các tài liệu tầng thấp của Hoà.
5. **Thực hiện:** Sau khi bạn tin tưởng bản xem trước, hãy bỏ `--dry-run` để lưu trữ thực sự.

## 4. Các trường hợp sử dụng

### Trường hợp sử dụng: Dọn sạch các tệp thô cũ
> **Bạn:** "Tôi có các bản ghi lại từ năm 2024 mà tôi không bao giờ hoàn thành việc nạp. Chúng đang chiếm dụng không gian tinh thần. Hãy lưu trữ chúng."
> 
> **Kỹ năng:** `mat:archive --before-date 2024-12-31 --status raw --dry-run`:
> ```
> Bản xem trước lưu trữ
> | Tệp | Nhân vật | Tầng | Trạng thái | Ngày tháng |
> | transcript-2024-01.md | hieu | T3 | raw | 2024-01-10 |
> | letter-2024-03.md | hoa | T5 | raw | 2024-03-15 |
> Tổng: 5 tệp sẽ được lưu trữ
> ```
> Bạn xem lại danh sách, nó trông tốt, sau đó bạn chạy lệnh tương tự **mà không có** `--dry-run`:
> - Cả 5 tệp hiện có `processing_status: archived` trong siêu dữ liệu của họ
> - Chúng biến mất khỏi danh sách quy trình hoạt động (như `mat:loader --status`)
> - Chúng vẫn ở đó nếu bạn cần khôi phục lại sau

### Trường hợp sử dụng: Lưu trữ tài liệu độ tin cậy thấp
> **Bạn:** "Chúng ta có rất nhiều tài liệu T5 (lý thuyết). Chúng ta nên tập trung vào bằng chứng T1–T3. Lưu trữ tất cả nội dung T5."
> 
> **Kỹ năng:** `mat:archive --tier T5 --dry-run`:
> - Liệt kê tất cả tài liệu được gán tầng T5 trên tất cả các nhân vật
> - Hiển thị số lượng: ví dụ: 12 tệp sẽ được lưu trữ
> - Bạn xác nhận, bỏ `--dry-run`, xong

### Trường hợp sử dụng: Lưu trữ dành riêng cho nhân vật
> **Bạn:** "Hồ sơ của Hoà đã hoàn thành. Tôi không cần thêm bằng chứng cho cô ấy. Lưu trữ tất cả tài liệu được xác thực của cô ấy để dọn sạch không gian làm việc."
> 
> **Kỹ năng:** `mat:archive --character character-b --status validated --dry-run`:
> - Hiển thị tất cả tài liệu của Hoà ở trạng thái "validated" (hoàn thành giai đoạn 4)
> - Bạn thấy: 18 tệp
> - Sau khi lưu trữ, chúng vẫn tồn tại nhưng sẽ không làm lộn xộn đầu ra `mat:loader --list`

### Trường hợp sử dụng: Dọn dẹp bảo mật (nếu hệ thống gắn thẻ mở rộng)
> **Bạn:** "Một số tài liệu là bảo mật. Tôi không muốn chúng xuất hiện trong tạo nội dung. Lưu trữ chúng."
> 
> **Kỹ năng:** (Trong tương lai, nếu các cờ bảo mật được lập chỉ mục):
> `mat:archive --confidentiality restricted --dry-run`
> - Hiển thị tất cả tài liệu được gắn thẻ là bị giới hạn
> - Bạn lưu trữ chúng và `cre:privacy-guard` sẽ không xem xét chúng (ranh giới miền được tôn trọng)

## 5. Những cảnh báo quan trọng

**Hãy suy nghĩ trước khi lưu trữ.** Sau khi lưu trữ, một tài liệu được đánh dấu là ngoài phạm vi. Nếu nó chứa bằng chứng duy nhất cho một tuyên bố chính, lưu trữ nó có nghĩa là mất bằng chứng đó khỏi hồ sơ hoạt động. Xem lại các phụ thuộc trước khi cam kết.

**Chạy khô là mạng an toàn của bạn.** Luôn chạy với `--dry-run` trước. Nếu bản xem trước trông sai, chỉ cần không thực hiện phiên bản không khô. Không có hình phạt cho chạy khô không thành công.

**Được lưu trữ không phải quên.** Lưu trữ không phải xóa. Tệp vẫn ở trong lịch sử git, siêu dữ liệu được cập nhật, và nếu sau này bạn cần phục hồi một tài liệu, bạn có thể thủ công thay đổi `processing_status: archived` trở lại `validated` hoặc bất cứ gì là thích hợp.

**Bộ lọc không tầng truyền.** Lưu trữ một tài liệu không cập nhật hồ sơ hoặc kích hoạt bất kỳ sự kiện hạ lưu nào. Nếu một tài liệu đang hỗ trợ một tuyên bố chính trong hồ sơ, lưu trữ nó không cập nhật hồ sơ. Bạn quản lý điều đó riêng biệt.

**Không khôi phục mà không có git.** Nếu bạn vô tình lưu trữ tệp sai và muốn hoàn tác, bạn có thể (a) thủ công chỉnh sửa siêu dữ liệu YAML hoặc (b) hoàn nguyên lệnh cam kết git. Không có lệnh "unarchive" tích hợp.

**Hoạt động hàng loạt mạnh mẽ nhưng có rủi ro.** Lưu trữ 20 tệp cùng một lúc là nhanh. Hãy chắc chắn rằng các bộ lọc của bạn là đúng trước khi bạn thực hiện.
