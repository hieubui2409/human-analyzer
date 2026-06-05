# psy:narrative-twist — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Vài tháng vào lập hồ sơ, các vật liệu mới nổi lên: mẹ kế của Nhân vật C không phải là kẻ ác — cô ấy nuôi dạy anh ấy với tình yêu thương, và câu chuyện "bỏ rơi mẹ" của Nhân vật C là sự hiểu lầm của Nhân vật C. Bạn cần sửa điều này trên 8+ tệp (dòng thời gian, tâm lý, mối quan hệ với Nhân vật A, v.v.) mà không xóa phiên bản cũ. Kỹ năng này tìm tất cả các dấu vết, đánh dấu chúng rõ ràng, và xếp tầng sự sửa chữa thông qua các nhân vật liên quan.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Bảo tồn lịch sử**: Gạch bỏ cho thấy những gì được tin tưởng/tuyên bố; ⚠️ TWIST cho thấy sự thật. Những độc giả trong tương lai nhìn thấy cả hai, hiểu sự phát triển kêu gọi.
- **Xếp tầng là bắt buộc**: Nếu câu chuyện mẹ của Nhân vật C thay đổi, nhận thức của Nhân vật A về Nhân vật C cũng thay đổi. Kỹ năng tìm thấy và cập nhật các tệp qua các nhân vật một cách đối xứng.
- **Xác thực bắt buộc**: Sau khi áp dụng một xoay chiều, psy:crossref phải xác thực rằng câu chuyện mới nhất quán. Đừng bỏ qua điều này.

## 3. Đường dẫn học tập

**Xoay chiều đầu tiên:** `psy:narrative-twist --character chien --fact "Mẹ kế bỏ rơi Nhân vật C" --truth "Mẹ kế nuôi dạy Nhân vật C từ bé" --source "P1, 2026-06-05"` — áp dụng một xoay chiều, xem xét việc xếp tầng.

**Quét xoay chiều:** `psy:narrative-twist --scan` — tìm các mâu thuẫn trong dữ liệu hiện có.

**Xoay chiều danh sách:** `psy:narrative-twist --list` — xem lại tất cả các ký hiệu TWIST trên tất cả các hồ sơ.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Xoay chiều nhân vật duy nhất

> Bạn: "Phỏng vấn cho thấy Nhân vật B không thực sự bị bỏ rơi ở tuổi 8; bố anh ấy đã thăm bí mật. Cập nhật hồ sơ."
> Kỹ năng: `psy:narrative-twist --character hoa --fact "Father abandoned family when Nhân vật B was 8" --truth "Father visited secretly, maintained contact" --source "P1, new interview"`
> → Tìm 3 lần xuất hiện trong timeline/overview.md, psychology/core-wounds.md, darkness/traumas.md. Áp dụng gạch bỏ + TWIST. Cập nhật psychology/formulation.md (lõi tính toán lại). Đầu ra báo cáo.

### Trường hợp sử dụng: Xoay chiều mối quan hệ (xếp tầng)

> Bạn: "Ngày kết nghĩa của Nhân vật A và Nhân vật B KHÔNG phải là tháng 9 năm 2025; nó thực sự là tháng 10 năm 2025. Cũng ảnh hưởng đến dòng thời gian của Nhân vật B."
> Kỹ năng: `psy:narrative-twist --character hieu --fact "Kết nghĩa with Nhân vật B: September 2025" --truth "Kết nghĩa with Nhân vật B: October 2025" --source "P1, corrected materials"`
> → Cập nhật dòng thời gian của Nhân vật A. Tự động tìm + cập nhật dòng thời gian của Nhân vật B, relationships/hieu.md. Xác thực tính đối xứng. Đề xuất: chạy psy:crossref --pair hieu hoa để xác nhận.

### Trường hợp sử dụng: Quét xoay chiều tiềm ẩn

> Bạn: "Tôi nghi ngờ có những mâu thuẫn tôi chưa giải quyết. Cái nào cần đánh dấu xoay chiều?"
> Kỹ năng: `psy:narrative-twist --scan`
> → Tìm: (1) Âm mưu mẹ kế của Nhân vật C được đánh dấu [DISPUTED]. (2) Tự hình ảnh của Nhân vật A so với mô tả của Nhân vật C. Đề xuất: áp dụng xoay chiều hoặc giải quyết bằng các vật liệu bổ sung.

## 5. Cảnh báo quan trọng

- **Nguồn là bắt buộc**: Mỗi xoay chiều cần ưu tiên P{N} + ngày. Đừng áp dụng các xoay chiều từ suy đoán.
- **Đánh dấu, không xóa**: Câu chuyện cũ vẫn ở đó (gạch bỏ). Điều này bảo tồn sự phát triển của câu chuyện cho những độc giả trong tương lai.
- **Xác thực qua các nhân vật không phải là tùy chọn**: Một xoay chiều trong hồ sơ của một nhân vật thường ảnh hưởng đến những người khác. Chạy psy:crossref sau khi áp dụng các xoay chiều.
- **Khung lâm sàn cần thiết**: Nếu xoay chiều chạm vào lõi tính hoặc công thức, diễn giải tâm lý thay đổi. Dự kiến psy:ref-audit để cờ các thay đổi.
