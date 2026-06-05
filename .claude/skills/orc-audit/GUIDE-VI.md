# orc:audit — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Các sự kiện định tuyến giữa các miền. Nhưng khi mã phát triển, các khai báo có thể trôi dạt: một SKILL.md nói "phát hành PSY.refresh" nhưng bảng định tuyến không mong đợi nó, hoặc ngược lại. Audit tìm thấy những mâu thuẫn này: "PSY.refresh được khai báo trong định tuyến nhưng không thể ghi lại," "MAT.integrated được phát hành nhưng không được định tuyến." Đó là một kiểm tra tính nhất quán cho hệ thống sự kiện.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**6 bất biến tính nhất quán:** routable ⊆ loggable (tất cả các sự kiện định tuyến phải được ghi lại), emits ⊆ routable (mục tiêu phát hành phải tồn tại), path-map ⊆ routable (quy tắc đường dẫn miền phải nhắm mục tiêu các sự kiện hợp lệ), v.v.

**Vi phạm cứng vs cố vấn.** Vi phạm (C1-C4) là lỗi. Cố vấn (C5-C6) là ghi chú thiết kế.

**Chỉ đọc.** Audit báo cáo phát hiện; sửa chữa là thủ công.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:audit --domain all` — kiểm tra tất cả các miền tính nhất quán.

**Lọc theo miền:** `orc:audit --domain psy` — chỉ các sự kiện PSY.

**Xem gợi ý:** `orc:audit --fix-suggestions` — nhận được gợi ý để sửa vi phạm.

**Đầu ra JSON:** `orc:audit --json` — báo cáo có cấu trúc để phân tích.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kiểm tra tính nhất quán sự kiện trước phát hành

> Bạn: "Audit all events before shipping."
>
> Kỹ năng: Quét EVENT_ROUTING, bảng SKILL.md, đăng ký Python. Báo cáo: "C1 violation: ORC.routed declared in SKILL.md ## Events but not in loggable registry." Bạn sửa: thêm ORC.routed vào các loại có thể ghi lại.

### Trường hợp sử dụng: Gỡ lỗi mismatch định tuyến

> Bạn: "PSY.refresh isn't cascading. Check audit."
>
> Kỹ năng: Báo cáo: "C5 advisory: PSY.refresh is routable but not documented in rules-12." Bạn xác minh: rules-12 được cập nhật nhưng event-routing không. Sửa bảng định tuyến.

### Trường hợp sử dụng: Kiểm tra miền cụ thể

> Bạn: "Any inconsistencies in CRE events?"
>
> Kỹ năng: Quét chỉ các khai báo sự kiện CRE. Báo cáo: "C4 violation: cre:privacy-guard declares COM.privacy event but not in loggable." Bạn thêm COM.privacy vào đăng ký có thể ghi lại.

## 5. Những cảnh báo quan trọng

- **Audit là cố vấn.** Vi phạm được báo cáo; bạn quyết định nếu chúng thực sự là vấn đề.
- **Cố vấn mang tính thông tin.** C5 (không được ghi lại) không phá vỡ bất cứ điều gì, chỉ ghi chú không đầy đủ.
- **Phạm vi: chỉ các khai báo sự kiện.** Điều này không kiểm toán logic kỹ năng, chỉ tính nhất quán sự kiện.
- **Gợi ý sửa chữa là gợi ý.** Xem xét trước khi áp dụng; một số có thể cần ngữ cảnh bạn có nhưng tập lệnh không.
