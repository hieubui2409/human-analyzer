# evl:compatibility — Hướng dẫn

Kỹ năng chấm điểm rubric dyad: chấm điểm khả năng tương thích quan hệ của một cặp nhân vật theo
các tiêu chí có phiên bản và trích dẫn bằng chứng.

## 1. Kỹ năng này giúp bạn điều gì

Bạn đưa vào hai nhân vật và (tuỳ chọn) một rubric id; nó trả về một scorecard dyad chuẩn hoá —
điểm cho từng tiêu chí (mỗi điểm kèm một tầng bằng chứng được trích dẫn), điểm tổng thể có trọng
số, một dải verdict, và một danh sách nổi bật những gì không thể xác minh. Rubric mặc định
(`relationship-compatibility`) áp dụng năm tiêu chí Gottman/ECR-R trên một miền dyadic.

Scorecard được ghi tại `docs/profiles/{char-a}/eval/relationship-compatibility--{char-b}.{md,json}`
để một nhân vật có thể giữ nhiều scorecard dyad (một cho mỗi đối tác) mà không bị xung đột tên.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Rubric dyad** — một tệp dùng chung, có phiên bản trong `docs/rubrics/` với `subject: dyad`.
  Mỗi tiêu chí mang các mốc neo (0/giữa/5), một trọng số, gợi ý bằng chứng nhắm vào tệp của CẢ
  HAI nhân vật, và một tầng bằng chứng tối thiểu.
- **Gộp bằng chứng** — script thu thập bằng chứng độc lập từ hồ sơ của từng nhân vật (mỗi bên
  giới hạn ở `MAX_CANDIDATES`) rồi hợp nhất và xếp hạng lại; không bên nào có thể lấn át bên kia.
  Mỗi đoạn trích mang trường `character` để giám khảo biết tệp đó thuộc về ai.
- **Tầng bằng chứng (T1–T5)** — độ mạnh của nguồn được trích dẫn (T1 sơ cấp … T5 phụ trợ). Mọi
  điểm đều phải trích dẫn một tầng. Không trích dẫn ⇒ `[UNVERIFIED]`, bị loại khỏi điểm và được
  đếm.
- **Thu thập vs. chấm** — script thu thập bằng chứng ứng viên và làm toán trọng số; **LLM** chấm
  từng tiêu chí. Script không bao giờ suy luận về điểm.
- **Độ phủ (coverage)** — tỉ lệ tiêu chí được xác minh; nó nằm ở tiêu đề scorecard để một đánh
  giá mỏng không thể giả dạng một đánh giá chắc chắn.

## 3. Dải verdict

| Dải | Khoảng điểm | Ý nghĩa |
|-----|-------------|---------|
| **Incompatible** | < 2.0 | Bốn Kỵ sĩ lan tràn và/hoặc gắn bó kém ổn định; nguy cơ tan vỡ cao |
| **At-Risk** | 2.0 – 3.0 | Tỉ lệ tích cực giảm / sửa chữa không nhất quán; cần can thiệp chủ động |
| **Compatible** | 3.0 – 4.0 | Mẫu xung đột có thể chấp nhận; vận hành được với nỗ lực có ý thức liên tục |
| **Highly-Compatible** | ≥ 4.0 | Nền tảng an toàn; sửa chữa nhất quán; tỉ lệ 5:1 trở lên; cặp đôi tối ưu |

## 4. Các tiêu chí (rubric relationship-compatibility)

| Tiêu chí | Trọng số | Cơ sở nghiên cứu |
|----------|----------|------------------|
| `horsemen-absence` | 0.25 | Bốn Kỵ sĩ của Gottman — khinh thường là yếu tố dự báo mạnh nhất |
| `repair-attempts` | 0.20 | Khởi đầu mềm mỏng, chấp nhận ảnh hưởng, hài hước, xoa dịu sinh lý |
| `positivity-ratio` | 0.20 | Quy tắc 5:1 của Gottman — dưới 3:1 báo hiệu tan vỡ trong vài năm |
| `attachment-pairing` | 0.20 | Thứ bậc ổn định ECR-R: An toàn×An toàn ổn định nhất; Lo lắng×Né tránh kém nhất |
| `similarity-complementarity` | 0.15 | Sự tương đồng vừa phải là tối ưu; bổ sung bù đắp khoảng trống chức năng |

## 5. Lộ trình học tập

1. Chạy `gather` cho một cặp và đọc gói bằng chứng được gộp — chú ý cách mỗi đoạn trích được
   gắn thẻ `character` để bạn có thể quy kết tín hiệu đúng chỗ.
2. Tự tay chấm hai ba tiêu chí để cảm nhận kỷ luật trích dẫn (trích nguồn + tầng, hoặc trả về
   `UNVERIFIED`).
3. Chạy `finalize` với một tệp điểm nhỏ và đọc scorecard được kết xuất.
4. So sánh tên tệp scorecard dyad (`rubric--doi-tac.md`) với mẫu scorecard đơn để xác nhận không
   có xung đột tên với scorecard đơn nhân vật.

## 6. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Chấm điểm tương thích mặc định cho một cặp

> "Chấm điểm tương thích giữa character-a và character-b."

Kỹ năng xác thực rubric `relationship-compatibility`, thu thập bằng chứng được gộp từ
`relationships/*.md` và `psychology/attachment-style.md` của cả hai hồ sơ, spawn một giám khảo
cho mỗi tiêu chí, tổng hợp, và ghi
`docs/profiles/{char-a}/eval/relationship-compatibility--{char-b}.{md,json}` kèm dải verdict và
tiêu đề độ phủ.

### Trường hợp sử dụng: Rubric dyad tuỳ chỉnh

> "Chấm character-a và character-b theo rubric dyad tuỳ chỉnh của tôi."

Truyền `--rubric <id>` trỏ đến bất kỳ `docs/rubrics/<id>.yaml` nào có khai báo `subject: dyad`.
Script xác thực kiểu rubric và báo lỗi ngay nếu không phải rubric dyad — loại rubric sai sẽ báo
lỗi to, không bao giờ chấm sai ngầm.

## 7. Những lưu ý quan trọng

- Một giám khảo không tìm được bằng chứng hỗ trợ từ bất kỳ nhân vật nào thì PHẢI trả về
  `UNVERIFIED` — đừng để nó đoán hoặc tổng hợp từ kiến thức chung.
- Tiêu chí `horsemen-absence` được chấm ngược: 5 = không có kỵ sĩ, 0 = cả bốn lan tràn. Giám
  khảo phải định hướng điểm đúng theo các mốc neo trong rubric.
- Bằng chứng từ `relationships/*.md` là nguồn chính cho hầu hết các tiêu chí; nếu các tệp đó
  thưa thớt, hãy dự kiến độ phủ thấp và nhiều dấu `[UNVERIFIED]` — đây là hành vi đúng.
- Script chạy offline; việc chấm thật diễn ra qua công cụ Agent.
- Điểm theo góc nhìn của nhân vật đầu tiên trừ khi cả hai nhân vật đều có tệp quan hệ trỏ đến
  nhau — giám khảo phải điều hoà bằng chứng không đối xứng và ghi chú lại.
