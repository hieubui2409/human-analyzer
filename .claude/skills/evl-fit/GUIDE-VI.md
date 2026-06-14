# evl:fit — Hướng dẫn

Cỗ máy quyết định mức độ phù hợp vai diễn: biến hồ sơ nhân vật thành một phán quyết CAST / CONDITIONAL / NO có trích dẫn bằng chứng.

## 1. Kỹ năng này giúp bạn điều gì

Bạn đưa vào một nhân vật (và tuỳ chọn một rubric quyết định tùy chỉnh); nó trả về một scorecard
chuẩn hoá — điểm cho từng tiêu chí (mỗi điểm kèm một tầng bằng chứng được trích dẫn), điểm trung
bình có trọng số tổng thể, một phán quyết ba dải, danh sách nổi bật những gì không thể xác minh,
và một ghi chú phủ quyết an toàn nếu phát hiện cờ rủi ro chặn. Đây là preset mỏng trên `evl:score`
được nối dây mặc định với `role-casting-fit`; dùng `--rubric` để chấm mức phù hợp với bất kỳ vai nào khác.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Rubric quyết định** — `kind: decision`, `high_stakes: true`, `min_judges: 2`. Thang điểm 0–5;
  cao hơn = phù hợp hơn. Trường `target_profile` trong rubric chỉ định spec vai diễn mà các tiêu chí
  được neo vào.
- **Dải phán quyết** — ba dải liên tiếp trên điểm trung bình có trọng số:
  - **CAST** (≥ 4.0): phù hợp mạnh, sẵn sàng cho vai diễn.
  - **CONDITIONAL** (3.0 – < 4.0): phù hợp một phần, có thể casting kèm điều kiện được nêu rõ.
  - **NO** (< 3.0): không đủ phù hợp tại thời điểm này.
  Dải được tính bởi `evl_aggregate` từ `verdict_thresholds` trong rubric — LLM không tự chọn dải.
- **Phủ quyết an toàn (safety veto)** — danh sách `red_flags` trong rubric liệt kê các tiêu chí
  mà điểm RED (0 trên thang 0–5) là chặn cứng. Với `role-casting-fit`, tiêu chí cổng là
  `safety-clearance`. Điểm RED ở đó có nghĩa là một hoặc nhiều cờ rủi ro nghiêm trọng tồn tại;
  phán quyết cuối cùng trở thành NO bất kể tổng điểm tổng hợp. Phủ quyết được **LLM thực thi**
  bằng cách kiểm tra `red_flags` sau khi thu thập điểm giám khảo — không phải bởi toán học ngưỡng.
- **Tầng bằng chứng (T1–T5)** — độ mạnh của nguồn được trích dẫn (T1 sơ cấp … T5 phụ trợ). Mọi
  điểm đều phải trích dẫn một tầng. Không trích dẫn ⇒ `[UNVERIFIED]`, bị loại khỏi tổng hợp và
  được đếm.
- **Thu thập vs. chấm** — script thu thập bằng chứng ứng viên và làm toán trọng số; **LLM** chấm
  từng tiêu chí. Script không bao giờ suy luận về điểm.
- **Hội tụ đa giám khảo** — vì `high_stakes`, kỹ năng spawn đúng `required_judges` (≥ 2) giám khảo
  cô lập đầu vào cho mỗi tiêu chí. Mỗi giám khảo chỉ thấy tiêu chí của mình + gói bằng chứng, không
  bao giờ thấy phán quyết của giám khảo khác. Hội tụ kiểm tra cả đồng thuận phán quyết (≥ 80% chia
  sẻ modal) và độ phân tán điểm (trong phạm vi 20% thang điểm). Bất đồng ⇒ `DIVERGED` + cần duyệt
  thủ công — không bao giờ tự lấy trung bình.
- **Độ phủ (coverage)** — tỉ lệ tiêu chí được xác minh; nó nằm ở tiêu đề scorecard để một đánh giá
  mỏng không thể giả dạng một đánh giá chắc chắn.

## 3. Lộ trình học tập

1. Chạy `gather` cho một nhân vật với rubric mặc định và đọc gói bằng chứng nó phát ra.
2. Đọc trường `target_profile` trong gói — nó cho bạn biết spec vai diễn nào các tiêu chí đang được neo vào.
3. Tự tay chấm hai ba tiêu chí (với trích dẫn bắt buộc) để cảm nhận kỷ luật trích dẫn.
4. Chạy `finalize` với một tệp điểm nhỏ và đọc scorecard được kết xuất — chú ý dải phán quyết và độ phủ.
5. Thử một trường hợp `safety-clearance` nên là RED và xác minh phủ quyết ghi đè tổng hợp.
6. Thử một rubric quyết định tùy chỉnh với `--rubric` để thấy cách hoán đổi `target_profile` hoạt động.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Quyết định casting thông thường

> "character-a có thể đóng vai nhà trị liệu trauma-informed không?"

Kỹ năng xác thực `role-casting-fit`, thu thập bằng chứng theo từng tiêu chí, spawn 2 giám khảo cô
lập đầu vào cho mỗi tiêu chí, hội tụ chúng, kiểm tra phủ quyết an toàn, tổng hợp, và ghi
`docs/profiles/character-a/eval/role-casting-fit.{md,json}` với phán quyết CAST / CONDITIONAL / NO.

### Trường hợp sử dụng: Phủ quyết an toàn trong thực tế

> "Chấm character-b cho vai nhà trị liệu."

Hai giám khảo độc lập trả về điểm 0 cho `safety-clearance` (RED — tình trạng rủi ro cao chưa được
điều trị). Dù trait-match, competency-match và motivational-fit đều điểm cao, LLM nêu ghi chú phủ
quyết an toàn và phán quyết cuối cùng là **NO** bất kể điểm trung bình có trọng số.

### Trường hợp sử dụng: Rubric vai diễn tùy chỉnh

> "Đánh giá mức độ phù hợp của character-a cho vai executive-coach."

Người dùng cung cấp rubric id `executive-coach-fit` với `target_profile` trỏ đến
`docs/references/role-profiles/executive-coach`. Chạy với `--rubric executive-coach-fit`. Cỗ máy
và script không phụ thuộc vai diễn — chỉ có rubric thay đổi.

### Trường hợp sử dụng: Giám khảo bất đồng

> "Chấm character-c cho vai phân tích viên."

Hai giám khảo bất đồng về `competency-match` (độ phân tán vượt ngưỡng). Kỹ năng trả về `DIVERGED`
cho tiêu chí đó với `manual_review_required: true`. Finalize bị hoãn cho đến khi con người giải quyết
bất đồng.

## 5. Những lưu ý quan trọng

- Một giám khảo không tìm được bằng chứng hỗ trợ thì PHẢI trả về `UNVERIFIED` — đừng để nó đoán.
- Phủ quyết an toàn (`red_flags`) do LLM thực thi, không phải toán học — LLM phải kiểm tra tường minh.
- `target_profile` là trường tham chiếu; kỹ năng chấm điểm đọc nó để lấy ngữ cảnh, nhưng tài liệu
  spec vai diễn thực tế phải tồn tại dưới `docs/references/` để giám khảo có thể neo vào.
- Scorecard quyết định là `cache: allow` — có thể tái sử dụng cho đến khi hồ sơ thay đổi đáng kể;
  dùng `--rescore` khi dữ liệu PSY hoặc GRO đã được cập nhật đáng kể.
- Script chạy offline; việc chấm thật diễn ra qua công cụ Agent và, với rủi ro cao, có duyệt của con người.
