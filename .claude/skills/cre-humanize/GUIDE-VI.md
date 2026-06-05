# cre:humanize — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp gì cho bạn

Bạn viết một bài (thường nhờ LLM) và đọc thấy "sai sai" — mượt quá, đều quá, đầy những "it's
worth noting", "trong thế giới ngày nay", cấu trúc bộ-ba gượng ép và dấu gạch ngang dài.
`cre:humanize` định vị các dấu vết đó một cách tất định, rồi (tùy chọn) để LLM viết lại văn cho
giống người viết. Nó không quan tâm bài có giống giọng một nhân vật cụ thể hay không — chỉ quan
tâm bài có nghe ra giọng người hay không.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Script gom, LLM phán.** Bộ quét là tất định và có thể gắn cờ dư. Nó tạo ra danh sách việc;
  LLM mới quyết định sửa gì. Đừng bao giờ để script "tự quyết".
- **Một nhà chứa taxonomy.** Mọi dấu vết nằm trong `platform_lib/humanizer_patterns.py`. Kỹ năng
  này và các cổng `cre:post-writer` / `cre:multiplatform` đều import nó. Không có danh sách trùng.
- **Độ nghiêm là một nút vặn.** `conservative ⊆ balanced ⊆ high`. `low_burstiness` chỉ kích hoạt
  ở mức `high` và chỉ mang tính tư vấn (không bao giờ chặn) — bài mạng xã hội tiếng Việt nhịp điệu
  vốn đa dạng.
- **Viết lại là tùy chọn, một lần, và chạy lại cổng.** Viết lại làm thay đổi văn bản `assets/`,
  nên các cổng bằng chứng / bảo mật / giọng phải chạy lại trên bản mới. Nếu cổng nào FAIL thì GIỮ
  lại và báo cáo — không tự viết lại vòng nữa. Corpus (profiles/materials) chỉ gắn cờ (Rule 09).

## 3. Lộ trình học

Lần đầu: quét một bản nháp → đọc các phát hiện. Tiếp theo: chỉnh `--strictness`, hoặc đặt một lần
preference `humanize_strictness`. Khi quen: gắn nó làm cổng làm-mềm trước `cre:voice-audit`, và để
`cre:post-writer` / `cre:multiplatform` gọi nó theo từng bản nháp/biến thể.

## 4. Tình huống dùng (mỗi cái = một đoạn hội thoại mẫu)

### Tình huống: định vị dấu vết trong bản nháp
> Bạn: "bài này nghe như AI viết, tìm dấu vết giúp"
> Kỹ năng: chạy `scan-content-for-ai-tells.py --path <nháp>`, in từng phát hiện kèm category, mức
> độ, vị trí và gợi ý cụ thể. Exit 1 nghĩa là có dấu vết.

### Tình huống: làm mềm và viết lại một asset
> Bạn: "humanize và viết lại assets/facebook/260413-slug"
> Kỹ năng: quét với `--rewrite`, LLM viết lại đoạn bị gắn cờ tại chỗ, rồi chạy lại
> `cre:evidence-scanner` → `cre:privacy-guard` → `cre:voice-audit`. Một lượt; cổng FAIL → GIỮ lại.

### Tình huống: chỉ gắn cờ một hồ sơ (không viết lại)
> Bạn: "kiểm tra docs/profiles/... xem có dấu vết AI không"
> Kỹ năng: quét và báo cáo. `--rewrite` ở đây bị từ chối (exit 2) — corpus không bao giờ tự viết
> lại (Rule 09). Bạn nhận danh sách việc; mọi chỉnh sửa là quyết định của con người/PSY.

## 5. Lưu ý quan trọng

- Bộ quét cố tình gắn cờ dư — coi phát hiện là ứng viên, không phải phán quyết.
- `low_burstiness` chỉ mang tính tư vấn và chỉ ở mức `high`; đừng chặn vì nó.
- Script không bao giờ sửa văn bản; viết lại là việc của LLM và phải chạy lại các cổng an toàn.
- Đây KHÔNG phải khớp giọng, kiểm bằng chứng, hay quét bảo mật — đó là các kỹ năng riêng.
