# evl:track — Hướng dẫn

Trình theo dõi điểm theo thời gian: xem điểm rubric của một nhân vật thay đổi như thế nào giữa các lần chấm và những thay đổi hồ sơ nào trùng khớp với sự biến động đó.

## 1. Kỹ năng này giúp bạn điều gì

Bạn đưa vào một nhân vật và một rubric id; nó tải scorecard hiện tại, tìm snapshot lịch sử mới nhất,
và tính các delta — điểm tổng thể, điểm theo từng miền, verdict, và độ phủ. Nó cũng kéo các sự kiện
thay đổi hồ sơ (PSY / GRO / MAT) từ cửa sổ thời gian được yêu cầu và đặt chúng cạnh diff để bạn thấy
điều gì đã thay đổi trong hồ sơ vào khoảng thời gian điểm số thay đổi.

Script cố ý không suy luận nguyên nhân: nó chỉ kết hợp các sự kiện theo timestamp, không hơn không kém.
Bạn (hoặc LLM đọc đầu ra) quyết định liệu một domain giảm điểm và một cập nhật tệp trauma có thực sự
liên quan hay không.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Scorecard hiện tại** — tệp `.json` đang hoạt động dưới `docs/profiles/{char}/eval/` được ghi bởi
  lần chạy `evl:score` gần nhất.
- **Snapshot lịch sử** — bản sao `.json` trước đó trong `eval/history/` (được `evl:score` tự động ghi
  trước khi ghi đè tệp đang hoạt động). Trình theo dõi lấy snapshot cuối cùng theo thứ tự thời gian
  làm `prev`.
- **diff_scorecards** — so sánh số học an toàn với None: `overall_delta`, `coverage_delta`, `delta`
  theo từng miền, và `verdict_change` (một tuple `(prev, curr)` khi chuỗi verdict thay đổi, ngược lại
  là `None`).
- **attribute_changes** — kết hợp timestamp xác định: trả về mọi bản ghi sự kiện trong các luồng
  telemetry PSY / GRO / MAT mà `character` khớp và `timestamp` ≥ `--since`. Không có suy diễn.
- **Trường hợp không có lịch sử** — nếu `load_history` trả về danh sách trống, script thông báo rõ
  ràng và thoát sạch. Lần chấm điểm đầu tiên không có gì để so sánh.

## 3. Lộ trình học tập

1. Chạy `evl:score` hai lần trên cùng một nhân vật + rubric (lần chạy thứ hai lưu lần đầu vào `history/`).
2. Chạy `evl:track` và đọc tóm tắt markdown — quan sát cách `overall_delta` và các delta theo miền hiển thị.
3. Truyền `--since` với timestamp của lần chấm đầu tiên; xác nhận các sự kiện PSY / MAT liên quan xuất hiện
   trong danh sách sự kiện.
4. Truyền `--json` và đưa đầu ra vào một script theo dõi các hồi quy verdict.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kiểm tra xem một buổi phỏng vấn mới có thay đổi đánh giá Big Five không

> "Theo dõi character-a trên psychometric-big-five từ tháng trước."

Kỹ năng tải scorecard hiện tại và snapshot trước đó, tính diff, sau đó kéo các sự kiện MAT / PSY
kể từ ngày đã cho. Bạn thấy rằng miền `Openness` tăng 0,4 điểm và một bản ghi phỏng vấn T2 mới được
nạp vào ngày hôm trước khi chấm lại — một liên kết có thể nhưng chưa được xác nhận để bạn điều tra.

### Trường hợp sử dụng: Kiểm tra hồi quy verdict

> "Điểm rủi ro lâm sàng của character-b có xấu đi không?"

Diff cho thấy `verdict_change: ("PASS", "PASS_WITH_RISK")` và `overall_delta: -0,6`. Hai sự kiện
PSY refresh xuất hiện trong cửa sổ — một cập nhật `psychology/core-wounds.md` và một mục nhập trauma mới.
Script không khẳng định quan hệ nhân quả; bạn đọc cả hai sự kiện và quyết định liệu bản cập nhật lâm sàng
có biện minh cho việc chấm lại toàn bộ bằng `evl:score --rescore` hay không.

## 5. Những lưu ý quan trọng

- Trình theo dõi cần ít nhất hai lần chấm điểm để có diff. Ở lần chạy đầu tiên, hãy nhắc người dùng
  chạy `evl:score` thêm một lần sau khi bằng chứng được cập nhật, rồi mới theo dõi.
- `--since` chỉ lọc **danh sách sự kiện** — diff scorecard luôn bao gồm hiện tại so với snapshot mới nhất
  bất kể ngày since.
- Một delta `None` trong đầu ra có nghĩa là một bên bị thiếu (ví dụ: một miền được thêm vào rubric
  sau snapshot cuối cùng). Đây không phải là thay đổi bằng không — hãy coi đó là khoảng trống, không
  phải cải thiện.
- Script đọc các tệp JSONL telemetry từng dòng; một dòng không hợp lệ bị bỏ qua lặng lẽ (không phải
  lỗi), phù hợp với thiết kế của các consumers telemetry khác trong codebase này.
