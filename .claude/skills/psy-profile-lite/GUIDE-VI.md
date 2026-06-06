# psy:profile-lite — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Các hồ sơ đầy đủ rất phong phú (~7.400 dòng tổng cộng cho 3 nhân vật = ~25.000 mã thông báo). Nhưng khi bạn chỉ đang phác thảo các góc độ nội dung hoặc nhanh chóng định hướng lại một nhân vật, điều đó là quá tải và đốt ngữ cảnh. Các hồ sơ lite nén từng nhân vật thành 120–150 dòng trong khi giữ những gì quan trọng: nỗi sợ hãi cốt lõi, cơ chế phòng thủ, các mối quan hệ chính, cung điểm hoạt động, các mẫu hành vi, các neo lâm sàn, tông giọng giọng nói, các sự kiện nhanh chóng. Tải tất cả 3 trong ~1.400 mã thông báo thay vì 25.000. Và bộ đệm nhớ: nếu bạn chưa sửa đổi hồ sơ nguồn kể từ lần tạo lite cuối cùng, nó sử dụng lại phiên bản lite cũ (không cần tính toán lại).

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Vô hiệu hóa nhận thức git**: Các hồ sơ lite lưu trong bộ đệm mã băm git (commit) + kiểm tra thay đổi chưa commit nguồn của họ. Nếu bạn chỉnh sửa hồ sơ, mã băm git (commit) + kiểm tra thay đổi chưa commit thay đổi, bộ đệm trở nên cũ, kỹ năng tái tạo. Không cần xóa bộ đệm thủ công.
- **Quy tắc nén**: Sự kiện vẫn chính xác; câu chuyện được nén 3x. Các lý thuyết được đề cập theo tên (không giải thích); các sự kiện dòng thời gian gần đây được ưu tiên hơn những cái cũ; giọng nói được bảo tồn ở cấp độ câu, không phải các phần toàn bộ.
- **Kiểm tra tính nhất quán trước**: Trước khi nén, kỹ năng có thể tùy chọn chạy `psy:crossref --quick` để cảnh báo nếu các hồ sơ nguồn có mâu thuẫn. Nén-đầu tiên-hỏi-câu hỏi-sau là rủi ro.

## 3. Đường dẫn học tập

**Sử dụng đầu tiên:** `psy:profile-lite --character character-a` — xem một hồ sơ lite, hiểu định dạng.

**Kiểm tra bộ đệm:** `psy:profile-lite --stats` — xem tất cả ba trạng thái + tiết kiệm kích thước.

**Làm mới sau sửa chữa:** `psy:profile-lite --refresh` — buộc tái tạo nếu bạn thủ công sửa đổi các hồ sơ mà không commit.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Sự tắc nghẽn ngân sách ngữ cảnh

> Bạn: "Tôi cần tải tất cả 3 nhân vật nhưng có mã thông báo hạn chế còn lại."
> Kỹ năng: `psy:profile-lite --all`
> → Trả về ~400 dòng tổng cộng (3 hồ sơ lite). Tải trong 1,4% ngữ cảnh thay vì 25%. Suy nghĩ góc độ nội dung nhanh được kích hoạt.

### Trường hợp sử dụng: Kiểm tra trạng thái bộ đệm

> Bạn: "Các hồ sơ lite của tôi có mới không, hay tôi cần phải tái tạo?"
> Kỹ năng: `psy:profile-lite --stats`
> → Nhân vật A: hợp lệ (2d cũ), Nhân vật B: cũ (7d, nguồn thay đổi), Nhân vật C: hợp lệ (1d). Khuyến nghị: làm mới Nhân vật B.

### Trường hợp sử dụng: Làm mới sau sửa chữa

> Bạn: "Tôi vừa thủ công sửa đổi psychology/formulation.md cho Nhân vật A. Tôi có cần làm mới lite không?"
> Kỹ năng: `psy:profile-lite --character character-a --refresh`
> → Tái tạo Nhân vật A lite từ các tệp hiện tại. Cập nhật bộ đệm. Xong.

### Trường hợp sử dụng: Tích hợp quy trình làm việc Cre

> Bạn: "Tôi sắp viết nội dung. Tải tất cả 3 nhân vật một cách hiệu quả."
> Quy trình làm việc: `cre:exploring --lite` hoặc tương tự (các kỹ năng cre gọi psy:profile-lite nội bộ)
> → Các hồ sơ lite được tải tự động. Sáng tạo nội dung tiến hành với 1% chi phí ngữ cảnh.

## 5. Cảnh báo quan trọng

- **Lite ≠ full**: Một hồ sơ lite là một công cụ định hướng nhanh chóng, không xác thực sâu. Nếu bạn cần xác minh độ chính xác lâm sàn hoặc tính nhất quán qua các nhân vật, hãy sử dụng các hồ sơ đầy đủ + psy:crossref.
- **Nén có thể ẩn sắc thái**: Một psychology/formulation.md tệp mỏng trở thành 2 dòng trong lite. Nếu một mẫu tinh tế, nó có thể bị mất. Kiểm tra `--stats` để xem số dòng; nếu một tệp nguồn là <50 dòng, lite sẽ nén nó nhiều.
- **Sửa đổi nguồn thủ công mà không commit phá hủy bộ đệm**: Nếu bạn chỉnh sửa tệp hồ sơ mà không commit, mã băm git (commit) + kiểm tra thay đổi chưa commit không thay đổi, bộ đệm vẫn cũ. Commit hoặc sử dụng `--refresh` để buộc.
- **Kiểm tra tính nhất quán trước tái tạo là tùy chọn**: Kỹ năng có thể cảnh báo nếu các hồ sơ nguồn mâu thuẫn (qua nội bộ `psy:crossref --quick`). Nếu bạn bỏ qua điều này, một nguồn cũ/mâu thuẫn nén thành lite cũ/mâu thuẫn. Lựa chọn của người dùng.
