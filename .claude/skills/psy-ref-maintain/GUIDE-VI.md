# psy:ref-maintain — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Theo thời gian, bạn tạo các tệp tài liệu tham khảo. Một số được sử dụng nhiều (attachment-theory được trích dẫn trong các hồ sơ của Nhân vật A + Nhân vật B + Nhân vật C). Những cái khác hết hạn không được sử dụng (bạn tạo dissociation.md một lần, nhưng nó không xuất hiện trong tệp tâm lý của bất kỳ nhân vật nào). Kỹ năng này quét toàn bộ thư viện tài liệu tham khảo, đếm trích dẫn theo lý thuyết, và nói với bạn: "Những 5 lý thuyết này là mồ côi (không có trích dẫn). Chúng có thực sự không áp dụng, hay chúng ta sẽ liên kết chúng? Những 3 lý thuyết này có trong INDEX.md nhưng các tệp của chúng không tồn tại." Đó là một kiểm tra sức khỏe để giữ thư viện ở tình trạng tốt.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Đếm trích dẫn**: Đối với mỗi tệp tham chiếu, kỹ năng quét tất cả các tệp hồ sơ tìm kiếm tên lý thuyết. Nếu tìm thấy N lần → được trích dẫn. Nếu tìm thấy 0 lần → mồ côi.
- **Tính nhất quán của chỉ mục**: Mỗi lý thuyết trong `docs/references/INDEX.md` có thực sự có mặt dưới dạng tệp không? Ngược lại: tất cả các tệp tham chiếu có xuất hiện trong INDEX.md không?
- **Tuân thủ lược đồ**: Mỗi tệp tham chiếu sẽ có các phần bắt buộc (định nghĩa, nguồn gốc, cơ chế, bối cảnh Việt Nam, nghiên cứu trường hợp, trích dẫn). Thiếu các phần = vi phạm lược đồ.
- **Khoảng trống phạm vi**: Tất cả 3 nhân vật sẽ tham chiếu ít nhất một lý thuyết trên mỗi danh mục (phòng thủ, gắn bó, chấn thương)? Nếu Nhân vật C thiếu "lý thuyết chấn thương," cờ nó.

## 3. Đường dẫn học tập

**Kiểm tra sức khỏe đầy đủ:** `psy:ref-maintain` — xem kiểm tra đầy đủ.

**Chỉ mồ côi:** `psy:ref-maintain --orphans-only` — tập trung vào các lý thuyết không được sử dụng.

**Chỉ khoảng trống:** `psy:ref-maintain --gaps-only` — xem nhân vật nào cần phạm vi lý thuyết lớn hơn.

**JSON để sắp xếp công cụ:** `psy:ref-maintain --json` — phân tích cú pháp cho các quy trình dọn dẹp tự động.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra thư viện định kỳ

> Bạn: "Đã 3 tháng kể từ khi chúng tôi thêm lý thuyết. Thư viện có khỏe không?"
> Kỹ năng: `psy:ref-maintain`
> → Tổng lý thuyết: 62. Hoạt động (3+ trích dẫn): 42. Sử dụng (1-2 trích dẫn): 15. Mồ côi: 5. Khoảng trống chỉ mục: 2 lý thuyết thiếu từ INDEX.md. Vi phạm lược đồ: 3 tệp thiếu phần bối cảnh văn hóa Việt Nam. Khuyến nghị: liên kết mồ côi nếu áp dụng, lưu trữ nếu không, sửa INDEX.md, lược đồ hoàn thành cho 3 tệp.

### Trường hợp sử dụng: Tìm các lý thuyết mồ côi

> Bạn: "Những lý thuyết nào chúng tôi tạo nhưng không bao giờ sử dụng?"
> Kỹ năng: `psy:ref-maintain --orphans-only`
> → cognitive-dissonance.md (0 trích dẫn), existential-void.md (0), learned-helplessness.md (0), role-confusion.md (0), shame-based-identity.md (0). Khuyến nghị: Xem xét từng cái. Một số có thể là ngách (áp dụng cho Nhân vật C chỉ khi hồ sơ được cập nhật). Một số sẽ được lưu trữ.

### Trường hợp sử dụng: Khoảng trống phạm vi (trước khi xác thực)

> Bạn: "Trước khi chạy psy:crossref, chúng tôi có đủ phạm vi lý thuyết không?"
> Kỹ năng: `psy:ref-maintain --gaps-only`
> → Nhân vật A: Cơ chế phòng thủ ✓, Gắn bó ✓, Chấn thương ✓, Năm Big ✗. Nhân vật B: Tất cả được bao phủ ✓. Nhân vật C: Cơ chế phòng thủ ✗, Chấn thương ✓, Gắn bó ✓. Khuyến nghị: Thêm tài liệu tham khảo Big Five cho Nhân vật A, tài liệu tham khảo cơ chế phòng thủ cho Nhân vật C.

## 5. Cảnh báo quan trọng

- **Mồ côi không phải lúc nào cũng có nghĩa là xóa**: Một lý thuyết có thể là ngách, áp dụng chỉ khi một nhân vật thay đổi. Thay vì xóa, gắn thẻ hoặc ghi chú lý do tồn tại của nó.
- **INDEX.md được duy trì thủ công**: Kỹ năng kiểm tra nó nhưng không tự động sửa. Bạn xem xét và thêm thủ công các mục bị mất.
- **Đếm trích dẫn chỉ khớp chính xác**: Nếu một lý thuyết được đề cập gián tiếp ("tương tự như lý thuyết gắn bó") nó có thể không đếm. Xem xét thủ công được khuyến nghị cho các trường hợp biên.
- **Vi phạm lược đồ cần sự phán xét của con người**: Nếu một tệp thiếu phần bối cảnh văn hóa Việt Nam, nó được cờ, nhưng bạn quyết định nếu nó thực sự bị mất hay chỉ cần mở rộng.
- **Khoảng trống phạm vi là hướng dẫn, không phải luật pháp**: Một nhân vật có thể không cần tài liệu tham khảo "Big Five" rõ ràng nếu công thức tâm lý bao gồm tính cách ngầm. Cờ là thông tin.
