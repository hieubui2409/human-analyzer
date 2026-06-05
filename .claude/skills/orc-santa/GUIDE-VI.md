# orc:santa — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Các thay đổi rủi ro cao (cập nhật hồ sơ, nội dung nhạy cảm) cần kỹ lưỡng. Hai nhà phê bình độc lập bắt các vấn đề người khác có thể bỏ lỡ. Nhà phê bình A tập trung vào độ chính xác cụ thể miền. Nhà phê bình B tập trung vào sự nhất quán. Họ không thấy phản hồi của nhau, vì vậy cả hai không neo vào quan điểm của nhau. Nếu cả hai vượt qua, bạn vận chuyển. Nếu bất kỳ ai thất bại, bạn sửa và xem xét lại.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Cách ly cấp đầu vào.** Mỗi nhà phê bình chỉ nhận được các tệp mục tiêu + báo cáo kiểm tra trước. Không có lịch sử phiên, không có đầu ra của nhà phê bình khác. Điều này ngăn chặn sự thiên vị neo.

**Hai nhà phê bình, hai ống kính.** Nhà phê bình A (chuyên gia miền) kiểm tra độ chính xác. Nhà phê bình B (chuyên gia sự nhất quán) kiểm tra các tham chiếu chéo và mâu thuẫn.

**Tối đa 2 vòng.** Kiểm tra vòng 1 → sửa vấn đề → kiểm tra vòng 2 với các tác nhân tươi. Nếu vòng 2 vẫn có vấn đề, tăng cấp cho người dùng.

## 3. Đường dẫn học tập

**Kiểm tra đầu tiên:** `orc:santa --review docs/profiles/character-b/psychology/ --framework psy --scope full`. Hai nhà phê bình kiểm tra, xuất PASS hoặc FAIL.

**Sửa vấn đề:** Giải quyết tất cả các vấn đề từ cả hai nhà phê bình.

**Kiểm tra lại:** Vòng 2 tự động chạy với các tác nhân tươi (không có bộ nhớ vòng 1). Cả hai phải vượt qua.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kiểm tra chỉnh sửa hồ sơ sau phân loại high_risk

> Bạn: "High_risk classification for Nhân vật B's psychology update. Run Santa."
>
> Kỹ năng: Nhà phê bình A (Độ chính xác Lâm sàng): "DSM-5 codes valid? 5P formulation consistent? Attachment patterns match theory?" Nhà phê bình B (Sự nhất quán Đa nhân vật): "Dates match across characters? Relationship dynamics bidirectional? No contradictions?" Cả hai xuất PASS hoặc liệt kê vấn đề. Bạn sửa nếu cần.

### Trường hợp sử dụng: Vòng 2 sau khi sửa vấn đề

> Bạn: "I fixed the issues. Re-review please."
>
> Kỹ năng: Sinh ra Nhà phê bình A' + B' tươi (không có ngữ cảnh vòng 1), cùng kiểm tra trước, kiểm tra lại. Nếu cả hai vượt qua, "SHIP ✅". Nếu bất kỳ ai thất bại lại, tùy chọn tăng cấp được hiển thị.

## 5. Những cảnh báo quan trọng

- **Santa được khuyến nghị, không bắt buộc.** orc:classify gợi ý cho high_risk; bạn có thể bỏ qua.
- **Kiểm tra dùng token.** 2 tác nhân con mỗi vòng × 2 vòng tối đa = 4 tác nhân con. Dùng cho rủi ro cao genuinely.
- **Tăng cấp sau vòng 2.** Không vòng 3 tự động. Nếu vấn đề vẫn tiếp diễn, người dùng quyết định: sửa thủ công, ghi đè vận chuyển, hoặc bỏ.
- **Phạm vi ảnh hưởng chi phí.** `full` = tất cả tệp (đắt tiền), `changes` = chỉ thay đổi git (rẻ), `ref` = thay đổi + tham chiếu chéo (trung bình).
