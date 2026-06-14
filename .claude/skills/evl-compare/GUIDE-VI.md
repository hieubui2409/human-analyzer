# evl:compare — Hướng dẫn

Xếp hạng các nhân vật với nhau trên cùng một rubric, sử dụng các scorecard đã có sẵn.

## 1. Kỹ năng này giúp bạn điều gì

Bạn đưa vào một rubric id (và tùy chọn một tập hợp con nhân vật); nó trả về một bảng xếp hạng —
điểm thô của mỗi nhân vật, z-score tương đối với nhóm, phân vị, và verdict, kèm danh sách nổi bật
những ai thiếu scorecard. Không có bước LLM chấm điểm: các điểm đã tồn tại sẵn và script đọc
chúng một cách xác định.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Scorecard** — tệp JSON tại `docs/profiles/{char}/eval/{rubric-id}.json` được ghi bởi
  `evl:score`. Kỹ năng này đọc nó; không bao giờ ghi.
- **Điểm thô (raw score)** — tổng có trọng số từ scorecard, trên thang đo rubric định nghĩa
  (ví dụ 0–5). Xếp hạng luôn theo điểm thô giảm dần.
- **z-score + phân vị** — chuẩn hoá tương đối với nhóm, tính bởi `evl_normalize.normalize_cohort`.
  Bị nén khi nhóm có < 3 nhân vật (không đủ dữ liệu để chuẩn hoá có ý nghĩa); một ghi chú trong
  đầu ra giải thích lý do nén.
- **Missing (Thiếu)** — nhân vật không có scorecard cho rubric này. Được liệt kê riêng biệt, nổi
  bật. Không bao giờ được điền số 0, không bao giờ bị loại trừ ngầm.
- **Không có LLM chấm điểm** — khác với `evl:score`, không có bước giám khảo Agent-tool ở đây.
  Các con số đã tồn tại; kỹ năng này chỉ đọc và xếp hạng chúng.

## 3. Lộ trình học tập

1. Chấm điểm ít nhất hai nhân vật trên cùng một rubric bằng `evl:score`, tạo ra các tệp
   scorecard `.json` của họ.
2. Chạy `evl:compare --rubric-id <id>` và đọc bảng xếp hạng.
3. Thêm scorecard của nhân vật thứ ba để cột z-score và phân vị trở nên có ý nghĩa.
4. Thử `--json` để xem dict so sánh thô (hữu ích cho scripting downstream hoặc nội dung CRE).

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Xếp hạng tất cả nhân vật theo Big Five

> "So sánh tất cả nhân vật theo psychometric-big-five."

Kỹ năng tải `eval/psychometric-big-five.json` của mỗi nhân vật, xếp hạng theo điểm thô tổng thể,
và in bảng kèm z-score + phân vị. Ai không có scorecard sẽ xuất hiện trong khối `missing` kèm
nhắc nhở chạy `evl:score` trước.

### Trường hợp sử dụng: So sánh hẹp trên rubric phù hợp vai diễn

> "So sánh character-a và character-b theo role-casting-fit."

Kỹ năng giải quyết hai tên động qua `paths.resolve_character`, chỉ tải hai scorecard đó, và xếp
hạng chúng. Vì nhóm là 2 (< 3), z-score và phân vị bị nén kèm ghi chú — điểm thô là tín hiệu
so sánh duy nhất đáng tin cậy ở kích thước đó.

### Trường hợp sử dụng: Đầu ra dạng máy đọc được cho CRE

> "Cho tôi so sánh JSON của tất cả nhân vật theo clinical-risk-safety."

Với `--json`, script phát ra dict `compare()` thô (danh sách xếp hạng + danh sách missing) để
một kỹ năng CRE hoặc script downstream có thể phân tích kết quả mà không cần parse bảng markdown.

## 5. Những lưu ý quan trọng

- Chạy `evl:score` cho mỗi nhân vật trước khi so sánh — kỹ năng này không tự gọi scorer.
- z-score / phân vị bị nén với nhóm < 3; đây là hành vi đúng, không phải lỗi.
- Scorecard bị thiếu luôn được hiển thị — đừng bao giờ coi một hàng bị thiếu là "điểm = 0".
- Script chạy offline và không ghi gì; đầu ra so sánh là tạm thời.
- Chuỗi verdict trong bảng đến trực tiếp từ scorecard; kỹ năng này không bao giờ tự suy ra lại.
