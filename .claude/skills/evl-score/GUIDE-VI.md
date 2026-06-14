# evl:score — Hướng dẫn

Cỗ máy chấm điểm rubric tổng quát: biến hồ sơ nhân vật thành một scorecard có trích dẫn bằng chứng.

## 1. Kỹ năng này giúp bạn điều gì

Bạn đưa vào một nhân vật và một rubric; nó trả về một scorecard chuẩn hoá — điểm cho từng tiêu chí
(mỗi điểm kèm một tầng bằng chứng được trích dẫn), tổng hợp theo miền và tổng thể, một verdict, và một
danh sách nổi bật những gì không thể xác minh. Đây là cỗ máy mà các kỹ năng EVL chuyên biệt
(`standardize`, `fit`, `compatibility`) bọc lại với một rubric định sẵn.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Rubric** — một tệp dùng chung, có phiên bản, độc lập với nhân vật, nằm ở `docs/rubrics/`. Mỗi tiêu
  chí mang các mốc neo (0/giữa/5), một trọng số, một gợi ý bằng chứng, và một tầng bằng chứng tối thiểu.
- **Tầng bằng chứng (T1–T5)** — độ mạnh của nguồn được trích dẫn (T1 sơ cấp … T5 phụ trợ). Mọi điểm đều
  phải trích dẫn một tầng. Không trích dẫn ⇒ `[UNVERIFIED]`, bị loại khỏi điểm và được đếm.
- **Thu thập vs. chấm** — script thu thập bằng chứng ứng viên và làm toán trọng số; **LLM** chấm từng
  tiêu chí. Script không bao giờ suy luận về điểm.
- **Hội tụ (convergence)** — rubric rủi ro cao chạy ≥2 giám khảo độc lập; nếu họ bất đồng thì kết quả là
  `DIVERGED` và con người quyết định — không bao giờ tự lấy trung bình.
- **Độ phủ (coverage)** — tỉ lệ tiêu chí được xác minh; nó nằm ở tiêu đề scorecard để một đánh giá mỏng
  không thể giả dạng một đánh giá chắc chắn.

## 3. Lộ trình học tập

1. Chạy `gather` cho một nhân vật + rubric và đọc gói bằng chứng nó phát ra.
2. Tự tay chấm hai ba tiêu chí để cảm nhận kỷ luật trích dẫn.
3. Chạy `finalize` với một tệp điểm nhỏ và đọc scorecard được kết xuất.
4. Thử một rubric lâm sàng để thấy verdict ba trạng thái + dấu `cache: never` cần đánh giá lại.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Chấm nhân vật theo bộ Big Five

> "Chấm character-a theo psychometric-big-five."

Kỹ năng xác thực rubric, thu thập bằng chứng theo từng nét tính cách, spawn một giám khảo cho mỗi tiêu
chí, tổng hợp, và ghi `docs/profiles/character-a/eval/psychometric-big-five.{md,json}` kèm tiêu đề độ phủ.

### Trường hợp sử dụng: Sàng lọc rủi ro lâm sàng rủi ro cao

> "Chạy rubric rủi ro lâm sàng trên character-b."

Vì rubric là `high_stakes` với `min_judges: 2`, kỹ năng spawn hai giám khảo cô lập đầu vào cho mỗi tiêu
chí và hội tụ chúng; một bất đồng sẽ được gắn cờ để duyệt thủ công. Verdict là ba trạng thái
(PASS / PASS_WITH_RISK / BLOCKED) và không bao giờ được cache.

## 5. Những lưu ý quan trọng

- Một giám khảo không tìm được bằng chứng hỗ trợ thì PHẢI trả về `UNVERIFIED` — đừng để nó đoán.
- Scorecard lâm sàng có tính thời điểm; luôn `--rescore`, đừng dùng lại một verdict rủi ro cũ.
- Chuẩn hoá z-score cần ≥3 nhân vật; dưới mức đó nó bị nén lại kèm ghi chú (dùng điểm thô).
- Script chạy offline; việc chấm thật diễn ra qua công cụ Agent và, với rủi ro cao, có duyệt của con người.
