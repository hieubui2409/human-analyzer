# evl:standardize — Hướng dẫn

Preset đánh giá tâm trắc học: biến hồ sơ nhân vật thành một scorecard có trích dẫn bằng chứng cho Big Five · Dark Triad · Attachment, kèm phân ổ gắn bó và cờ Dark Triad elevated.

## 1. Kỹ năng này giúp bạn điều gì

Bạn đưa vào một nhân vật (và tùy chọn một rubric thay thế); nó trả về một scorecard tâm trắc
học đầy đủ — điểm cho từng tiêu chí (mỗi điểm kèm một tầng bằng chứng được trích dẫn), tổng
hợp theo miền và tổng thể, một verdict, và một danh sách nổi bật những gì không thể xác minh.
Ngoài scorecard thô, nó còn thêm hai tóm tắt lâm sàng do LLM diễn giải:

- **Phân ổ gắn bó (attachment quadrant)** — ánh xạ điểm subscale `attachment-anxiety` và
  `attachment-avoidance` từ ECR-R lên một trong bốn phong cách: Secure (An toàn), Preoccupied
  (Lo âu), Dismissing-Avoidant (Né tránh-Phủ nhận), hoặc Fearful-Avoidant (Né tránh-Sợ hãi).
- **Cờ Dark Triad elevated** — đặt `dark_triad_elevated: true` nếu bất kỳ subscale SD3 nào
  (`narcissism`, `machiavellianism`, `psychopathy`) đạt điểm ≥ 4, nêu rõ trait nào bị elevated
  kèm một ghi chú lâm sàng ngắn.

Đây là `evl:score` với `--rubric psychometric-big-five` đặt sẵn. Tham số rubric là tùy chọn;
chỉ ghi đè nếu bạn có một rubric tâm trắc học khác.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Bộ đánh giá (battery)** — ba khối công cụ trong một rubric: Big Five (OCEAN theo BFI-2 /
  NEO PI-R), Dark Triad (subscale SD3), và Attachment (ECR-R hai chiều). Tất cả được chấm trên
  thang 0–5 với các mốc neo hành vi.
- **Tầng bằng chứng (T1–T5)** — độ mạnh của nguồn được trích dẫn (T1 sơ cấp … T5 phụ trợ).
  Mọi điểm tiêu chí đều phải trích dẫn một tầng. Không trích dẫn ⇒ `[UNVERIFIED]`, bị loại
  khỏi điểm và được đếm.
- **Thu thập vs. chấm** — script thu thập bằng chứng ứng viên và làm toán trọng số; **LLM**
  chấm từng tiêu chí. Script không bao giờ suy luận về điểm.
- **Phân ổ gắn bó** — suy ra từ hai trục điểm (anxiety, avoidance), mỗi trục ngưỡng tại 2.5
  giữa thang. LLM viết nội dung diễn giải; phép tính ngưỡng được nêu rõ ở đây (không trong
  script) để LLM có thể kiểm tra mình đang áp dụng đúng quadrant.
- **Dark Triad elevated** — một cờ ngưỡng đơn giản (bất kỳ subscale ≥ 4 = elevated). LLM nêu
  tên trait và viết ghi chú lâm sàng; script không đánh giá điều này.
- **Chuẩn hoá z-score** — rubric chỉ định `normalization: z_score`. Điều này cần ≥ 3 nhân vật
  có scorecard đã hoàn tất cho cùng một rubric. Nếu cohort nhỏ hơn, bước chuẩn hoá bị nén lại
  và điểm thô được sử dụng, kèm một ghi chú hiển thị trên scorecard.
- **Độ phủ (coverage)** — tỉ lệ tiêu chí được xác minh; nó nằm ở tiêu đề scorecard để một
  đánh giá mỏng không thể giả dạng một đánh giá chắc chắn.

## 3. Lộ trình học tập

1. Chạy `gather` cho một nhân vật và đọc gói bằng chứng — ba khối, mười một tiêu chí.
2. Tự tay chấm hai ba tiêu chí (một từ mỗi khối) để cảm nhận kỷ luật trích dẫn.
3. Chạy `finalize` với một tệp điểm nhỏ và đọc scorecard được kết xuất.
4. Tự tay viết diễn giải phân ổ gắn bó từ hai điểm subscale.
5. Kiểm tra các subscale Dark Triad và tập viết ghi chú cờ elevation.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Bộ tâm trắc học đầy đủ với rubric mặc định

> "Chạy bộ tâm trắc học cho character-a."

Kỹ năng xác thực `psychometric-big-five`, thu thập bằng chứng cho cả 11 tiêu chí, spawn một
giám khảo cho mỗi tiêu chí, tổng hợp, và ghi
`docs/profiles/character-a/eval/psychometric-big-five.{md,json}`. Sau khi finalize, LLM đọc
`attachment-anxiety` (ví dụ 3.8) và `attachment-avoidance` (ví dụ 1.2) → phong cách
Preoccupied. Các subscale Dark Triad đều < 4 → `dark_triad_elevated: false`.

### Trường hợp sử dụng: Ghi đè rubric tâm trắc học tuỳ chỉnh

> "Standardize character-b dùng rubric my-custom-psychometric."

Truyền `--rubric my-custom-psychometric`. Script giải quyết rubric từ `docs/rubrics/` đúng như
`evl:score` làm. Các bước phân ổ gắn bó và Dark Triad chỉ áp dụng khi scorecard đã hoàn tất
chứa các criterion id tương ứng; nếu không có, các bước đó được bỏ qua kèm một ghi chú.

### Trường hợp sử dụng: Chấm lại sau sự kiện PSY.refresh

> "Chạy lại bộ tâm trắc học cho character-a — hồ sơ đã được cập nhật."

Dùng `--rescore` để bỏ qua scorecard đã cache. Luôn chấm lại khi `PSY.refresh` được phát sau
một thay đổi hồ sơ đáng kể.

## 5. Bảng tham chiếu phân ổ gắn bó

| Anxiety \ Avoidance | Thấp (< 2.5) | Cao (≥ 2.5) |
|---------------------|--------------|-------------|
| **Thấp (< 2.5)** | Secure (An toàn) | Dismissing-Avoidant (Né tránh-Phủ nhận) |
| **Cao (≥ 2.5)** | Preoccupied (Lo âu) | Fearful-Avoidant (Né tránh-Sợ hãi) |

LLM diễn giải quadrant trong 2–4 câu, trích dẫn hai điểm subscale và ít nhất một nguồn bằng
chứng (theo `file:line`) từ scorecard. Nhãn quadrant không có điểm được trích dẫn là không
chấp nhận được.

## 6. Quy tắc cờ Dark Triad elevation

- Kiểm tra điểm `narcissism`, `machiavellianism`, `psychopathy` từ scorecard đã hoàn tất.
- Nếu **bất kỳ** điểm nào ≥ 4: viết `dark_triad_elevated: true`, nêu tên trait, viết một câu
  ghi chú lâm sàng trích dẫn điểm subscale và nguồn bằng chứng của nó.
- Nếu **không có** điểm nào ≥ 4: viết `dark_triad_elevated: false` và một câu tóm tắt hồ sơ
  dưới ngưỡng lâm sàng (ví dụ: "Tất cả subscale SD3 đều dưới ngưỡng lâm sàng (cao nhất:
  machiavellianism 2.8)").
- Không bao giờ suy ra cờ từ tiêu chí chưa được xác minh — nếu một subscale là `[UNVERIFIED]`,
  nêu rõ rằng không thể đánh giá elevation cho trait đó.

## 7. Những lưu ý quan trọng

- Một giám khảo không tìm được bằng chứng hỗ trợ thì PHẢI trả về `UNVERIFIED` — đừng để nó
  đoán.
- Chuẩn hoá z-score bị nén lại dưới cohort 3 nhân vật; dùng điểm thô kèm ghi chú hiển thị.
  Không được tự tạo ra một điểm đã chuẩn hoá.
- Phân ổ gắn bó và cờ Dark Triad được LLM viết SAU khi finalize, chỉ từ điểm đã xác minh.
  Không bao giờ diễn giải từ tiêu chí chưa xác minh.
- Script chạy offline; việc chấm thật diễn ra qua công cụ Agent.
