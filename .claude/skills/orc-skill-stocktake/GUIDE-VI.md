# orc:skill-stocktake — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Theo thời gian, các kỹ năng tích lũy. Một số chồng chéo. Một số trở nên lỗi thời. Stocktake kiểm tra danh mục: đếm mỗi khung, phát hiện chồng chéo (ví dụ, hai kỹ năng làm điều tương tự), xác định khoảng cách (chức năng bị thiếu), và gán các phán quyết (KEEP cái này, CONSOLIDATE cái kia, RETIRE cái kia). Đó là bảo trì cho chính hệ thống kỹ năng.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Ba tầng kiểm tra:** Quick Scan (đếm + siêu dữ liệu), Full Stocktake (chồng chéo/khoảng cách + phán quyết LLM), Conformance (chất lượng mã + cấu trúc).

**Phán quyết là cố vấn.** CONSOLIDATE hoặc RETIRE là khuyến nghị, không bao giờ tự động thực hiện. Bạn quyết định.

**Bảo vệ kỹ năng mới.** Các kỹ năng < 3 lần commit cũ được gắn thẻ NEW. "Không sử dụng" không có nghĩa là "không được sử dụng" cho các kỹ năng mới; chỉ các tín hiệu chồng chéo quan trọng.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:skill-stocktake --quick` — xem số lượng kỹ năng và khoảng cách siêu dữ liệu.

**Kiểm tra sâu:** `orc:skill-stocktake --full` — phân tích chồng chéo/khoảng cách + phán quyết LLM.

**Kiểm tra phù hợp:** `orc:skill-stocktake --conformance` — kích thước mã, cấu trúc, chất lượng tham chiếu.

**Lọc theo khung:** `orc:skill-stocktake --full --framework orc` — chỉ các kỹ năng ORC.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kiểm tra sức khỏe danh mục nhanh

> Bạn: "Quick scan the skill catalog for drift."
>
> Kỹ năng: Đếm: ORC 17, PSY 16, CRE 9, GRO 8, MAT 4, COM 4 (phù hợp với CLAUDE.md). Báo cáo: 2 `description` frontmatter bị thiếu, 1 tham chiếu mồ côi. Bạn biết: danh mục đồng bộ, khoảng cách siêu dữ liệu nhỏ để khắc phục.

### Trường hợp sử dụng: Full stocktake cho phát hiện chồng chéo

> Bạn: "Are any ORC skills duplicates?"
>
> Kỹ năng: Phân tích: `orc:domain-router` và `orc:cascade` cả hai xử lý định tuyến sự kiện. Phán quyết: KEEP cả hai (bổ sung: router = phát hiện từ-diff, cascade = truy tìm sự kiện rõ ràng). Bạn xác nhận: không cần hợp nhất.

### Trường hợp sử dụng: Kiểm tra phù hợp trước phát hành

> Bạn: "Check skill conformance before shipping."
>
> Kỹ năng: Quét tất cả các kỹ năng: orc-bootstrap là 340 dòng (WARN: 200-line threshold), orc-council có tham chiếu lồng (FAIL: cần chia). Báo cáo trạng thái phù hợp mỗi kỹ năng. Bạn biết phải sửa gì trước phát hành.

## 5. Những cảnh báo quan trọng

- **Chồng chéo ≠ nhân đôi.** Các kỹ năng có tên tương tự có thể bổ sung. Phán quyết LLM là gọi đánh giá.
- **Chế độ tự động có giới hạn.** Script over-gather các ứng cử viên chồng chéo; LLM lọc dương tính giả.
- **Ngoại lệ kỹ năng mới.** Các kỹ năng < 3 lần commit cũ không bao giờ bị loại bỏ vì "không sử dụng".
- **Phù hợp là cố vấn.** Khuyến nghị ENHANCE là những cải tiến, không phải những cản trở.
