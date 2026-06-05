# psy:propagate — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn vừa cập nhật timeline/overview.md của Nhân vật A để thêm một cột mốc hướng dẫn mới với Nhân vật C. Nhưng hồ sơ của Nhân vật C cũng có một dòng thời gian, và anh ấy sẽ có cùng một sự kiện. Và tệp quan hệ Nhân vật A-Nhân vật C sẽ ghi chú sự tương tác này. Thay vì thủ công tìm kiếm trong các tệp, kỹ năng này đọc biểu đồ quan hệ, xác định Nhân vật C là "được kết nối với Nhân vật A," và nói với bạn: "Cập nhật timeline/overview.md của Nhân vật C" (ưu tiên CAO) và "Cập nhật relationships/hieu.md trong hồ sơ của Nhân vật C" (ưu tiên CAO).

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Được hướng dẫn bằng biểu đồ**: Biểu đồ quan hệ (`docs/graph/relational-dynamics.md`) xác định các nhân vật được kết nối và cách thức (sức mạnh liên kết cao/trung bình/thấp). Kỹ năng này sử dụng biểu đồ đó để phát hiện các mục tiêu xếp tầng.
- **Ánh xạ phần**: Các phần khác nhau xếp tầng khác nhau. Một thay đổi đối với relationships/family.md kích hoạt xem xét relationships/family.md của các nhân vật được kết nối và tệp relationships/{other-char}.md. Một thay đổi đối với timeline/overview.md kích hoạt xem xét dòng thời gian.
- **Kế thừa phán quyết (tùy chọn)**: Nếu một thay đổi lan rộng trên các nhân vật, bộ đệm phán quyết có thể sử dụng lại phán quyết của nhân vật nguồn cho các hàng xóm không thay đổi (kinh tế chỉ, không bao giờ an toàn). Các công cụ hạ lưu quyết định.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `psy:propagate --character hieu` — xem tất cả các mục tiêu xếp tầng sau những thay đổi Nhân vật A.

**Phần cụ thể:** `psy:propagate --character hoa --section relationships` — thu hẹp thành một xếp tầng của phần.

**Đầu ra máy:** `psy:propagate --character chien --json` — phân tích cú pháp theo chương trình để tự động hóa.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Xếp tầng nhân vật đầy đủ

> Bạn: "Tôi đã viết lại psychology/formulation.md cho Nhân vật A (giải thích nỗi sợ hãi cốt lõi). Cái nào khác cần cập nhật?"
> Kỹ năng: `psy:propagate --character hieu`
> → Phát hiện: Nhân vật B (CAO: relationships/hieu.md có thể cần cập nhật phản ánh sự hiểu biết mới), Nhân vật C (RỦI RO VỪA: dòng thời gian có thể bị ảnh hưởng nếu những nỗi sợ hãi của Nhân vật A kích hoạt các sự kiện).

### Trường hợp sử dụng: Xếp tầng cụ thể về quan hệ

> Bạn: "Family.md của Nhân vật B bây giờ nói 'bố vắng mặt,' không phải 'chết.' Cái nào xếp tầng?"
> Kỹ năng: `psy:propagate --character hoa --section relationships`
> → relationships/hieu.md của Nhân vật A sẽ ghi chú: "Bố của Nhân vật B vắng mặt, không phải chết" (ảnh hưởng cách Nhân vật A hỗ trợ Nhân vật B). Nhân vật C: không có mối quan hệ trực tiếp, bỏ qua.

### Trường hợp sử dụng: Xếp tầng dòng thời gian

> Bạn: "Thêm sự kiện kết nghĩa Oct 2025 vào dòng thời gian của Nhân vật A."
> Kỹ năng: `psy:propagate --character hieu --section timeline`
> → timeline/overview.md của Nhân vật B phải có mục nhập phù hợp (ưu tiên CAO). Cũng kiểm tra relationships/hieu.md của Nhân vật B để đề cập cột mốc.

## 5. Cảnh báo quan trọng

- **Xếp tầng là một gợi ý, không phải một lệnh**: Kỹ năng xác định các mục tiêu, nhưng bạn quyết định cái nào sẽ cập nhật. Không phải tất cả các tầng yêu cầu hành động.
- **Biểu đồ xác định các mục tiêu**: Nếu biểu đồ quan hệ không liệt kê một kết nối, xếp tầng sẽ không gợi ý. Cập nhật biểu đồ nếu bạn thêm các mối quan hệ mới.
- **Các tệp qua các nhân vật là động**: Kỹ năng khám phá tệp `relationships/{other-char}.md` động. Nếu tệp như vậy không tồn tại, xếp tầng sẽ không liệt kê nó, nhưng bạn có thể cần tạo nó.
- **Xác thực thủ công sau xếp tầng**: Sau khi cập nhật các tệp xếp tầng, chạy `psy:crossref --pair {src} {target}` để xác nhận rằng bản cập nhật là đối xứng và nhất quán.
