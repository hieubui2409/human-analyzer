# psy:hypothesis — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đang lập kế hoạch cho cung điểm của Nhân vật C. Nếu anh ấy nhận được học bổng Scholarship X, bạn muốn tưởng tượng: Anh ấy sẽ ăn mừng không? Đóng băng? Suy ngẫm về "được may mắn"? Kỹ năng này đọc hồ sơ của anh ấy — nỗi sợ hãi cốt lõi của anh ấy (bỏ rơi), cơ chế phòng thủ của anh ấy (tự nghi ngờ, hợp lý hóa), phong cách gắn bó của anh ấy (lo lắng), các kích hoạt của anh ấy — và dự đoán cách anh ấy sẽ phản ứng, từng bước: ngay lập tức 0–24h, đối phó ngắn hạn, quỹ đạo dài hạn.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Được hướng dẫn bằng hồ sơ**: Dự đoán neo vào các mẫu được ghi lại từ psychology/formulation.md, darkness/traumas.md, light/strengths-hope.md. Không được phát minh — được bắt nguồn.
- **Ba độ sâu**: Nông là 3–5 dòng đầu tiên (nhanh). Sâu bao gồm các giai đoạn ngay lập tức/ngắn hạn/dài hạn + lý do lâm sàn + tính năng ghi điểm tự tin. Lâm sàn thêm các tác động DSM-5/ICD-11 + mức độ rủi ro + bối cảnh văn hóa.
- **Đa nhân vật**: Các tình huống không tồn tại trong sự cô lập. Nếu Nhân vật A kiệt sức, Nhân vật B sẽ phản ứng như thế nào? Nhân vật C cảm thấy bị bỏ rơi lại không? Kỹ năng này có thể theo dõi việc xếp tầng.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `psy:hypothesis --character character-c --scenario "Nhân vật C gets Scholarship X scholarship" --depth shallow` — kiểm tra cảm giác nhanh chóng.

**Lặn sâu:** `psy:hypothesis --character character-a --scenario "Nhân vật B's father returns after 10 years" --depth deep` — phân tích phong phú.

**Đa nhân vật:** `psy:hypothesis --character character-a --scenario "Nhân vật A admits he can't mentor Nhân vật C anymore" --multi` — xem tác động xếp tầng.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Lập kế hoạch cung điểm nhanh chóng

> Bạn: "Điều gì xảy ra nếu Nhân vật B mất việc ngày mai?"
> Kỹ năng: `psy:hypothesis --character character-b --scenario "Nhân vật B loses his job" --depth shallow`
> → Ngay lập tức: hoảng loạn tài chính + khủng hoảng bản sắc (công việc = giá trị). Đối phó: cờ bạc hoặc uống rượu. Gắn bó: bám vào Nhân vật A. Tự tin: CAO.

### Trường hợp sử dụng: Sáng tạo nội dung

> Bạn: "Nhân vật A vừa hướng dẫn Nhân vật C vượt qua một kỳ thi. Vibe của anh ấy là gì?"
> Kỹ năng: `psy:hypothesis --character character-a --scenario "Mentoring Nhân vật C to exam success" --depth deep`
> → Ngay lập tức: nhẹ nhõm + kích hoạt người cứu rỗi. Ngắn hạn: tăng gấp đôi hướng dẫn (xác nhận giá trị). Dài hạn: tăng trưởng nhưng rủi ro quá tải. Lưu ý lâm sàn: phức tạp người cứu rỗi được kích hoạt; giám sát kiệt sức.

### Trường hợp sử dụng: Tác động xếp tầng

> Bạn: "Mối quan hệ Nhân vật B và Nhân vật A vỡ. Điều gì xảy ra với Nhân vật C?"
> Kỹ năng: `psy:hypothesis --character character-b --scenario "Sworn brother relationship breaks with Nhân vật A" --multi`
> → Nhân vật B: tàn phá + tự trách. Nhân vật A: tội lỗi + rút lui bảo vệ. Nhân vật C: cố vấn mồ côi + kích hoạt bỏ rơi lại. Đề xuất: Rủi ro khủng hoảng CAO.

## 5. Cảnh báo quan trọng

- **Tính năng ghi điểm tự tin là heuristic**: CAO = phù hợp với 3+ mẫu được thiết lập. TRUNG BÌNH = 1–2 mẫu, một số không chắc chắn. THẤP = tình huống mới, dữ liệu hạn chế. Tin tưởng CAO/TRUNG BÌNH hơn THẤP.
- **Không phải là một bảo đảm**: Con người thực sự bất ngờ. Một dự đoán với tự tin CAO vẫn có thể không xảy ra.
- **Dự đoán lâm sàn cần theo dõi**: Nếu `--depth clinical` nước ngoài nguy cơ khủng hoảng, chạy `psy:crisis-assess` để tài liệu chính thức.
- **Tình huống phải cụ thể**: Mơ hồ ("điều gì đó xấu xảy ra") tạo ra dự đoán mơ hồ. Các tình huống cụ thể ("bỏ rơi bởi người cố vấn") neo các dự đoán tốt hơn.
