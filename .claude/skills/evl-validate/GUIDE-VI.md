# evl:validate — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

Cổng kiểm tra tính trung thực cấu trúc: chứng minh một rubric hoặc một scorecard đã hoàn thành là đáng tin cậy trước khi bất cứ thứ gì hành động dựa trên nó.

## 1. Kỹ năng này giúp bạn điều gì

Bạn vừa soạn một rubric, hoặc một scorecard vừa được trả về từ cỗ máy chấm điểm. Trước khi chấm nhân vật theo rubric đó — hoặc trước khi CRE tiêu thụ scorecard đó — bạn muốn biết: liệu nó có vững chắc về mặt cấu trúc không? Trọng số có đúng không? Các id tiêu chí có nhất quán không? Mọi điểm số có nằm trong phạm vi và được tổng hợp chính xác không?

`evl:validate` trả lời những câu hỏi đó bằng một báo cáo xác định, đại số. Không có phán xét LLM, không có mạng, không có tác dụng phụ. Nó in PASS hoặc cho bạn thấy chính xác điều gì bị hỏng và ở đâu.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Hai chế độ, một script.** Chế độ RUBRIC xác thực tệp rubric. Chế độ SCORECARD xác thực một scorecard đã hoàn thành so với rubric của nó. Cờ `--rubric` xuất hiện trong cả hai — nó luôn là ngữ cảnh bắt buộc.
- **Hình dạng vs. bất biến.** Xác thực rubric có hai lớp: JSON-Schema Draft-7 (hình dạng: enum, khóa bắt buộc, kiểu, phạm vi) và các bất biến chéo-trường mà schema không thể diễn đạt (tổng trọng số, sàn giám khảo, rail lâm sàng, phủ ngưỡng, điểm neo). Lỗi hình dạng ngắt mạch vượt qua bất biến.
- **UNMAPPED là to tiếng, không phải lúc nào cũng nghiêm trọng.** Một id tiêu chí trong scorecard không tồn tại trong rubric là UNMAPPED — một phát hiện to tiếng được in trong bảng. Nó không gây lỗi nghiêm trọng theo mặc định (rubric có thể đã được sửa đổi sau khi chấm điểm). Thêm `--strict` để biến UNMAPPED thành FAIL cứng.
- **Mã thoát là cổng.** Thoát 0 có nghĩa là tất cả các kiểm tra là PASS hoặc SKIP. Khác không có nghĩa là ít nhất một FAIL — một bước CI có thể sử dụng điều này trực tiếp.
- **Chỉ đọc, luôn luôn.** Script không bao giờ ghi bất cứ thứ gì. Mọi khắc phục là thủ công.

## 3. Lộ trình học tập

1. Chạy `--all` và đọc đầu ra: mỗi rubric in PASS hoặc danh sách lỗi. Đây là cách nhanh nhất để xác nhận thư viện rubric nhất quán.
2. Sau khi chấm điểm một nhân vật, chạy chế độ SCORECARD trên JSON kết quả. So sánh bảng kiểm tra hàng theo hàng — `aggregate_math_correct` là tiết lộ nhất; một sự không khớp ở đó có nghĩa là các điểm được lưu trữ đã bị chỉnh sửa sau khi tổng hợp.
3. Thử `--strict` trên một scorecard từ phiên bản rubric cũ hơn: các hàng UNMAPPED trở thành FAIL, bề mặt các id tiêu chí đã drifted ra ngoài đồng bộ.
4. Pipe `--json` vào `jq` để lọc lập trình: `jq '.checks[] | select(.status=="FAIL")'`.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Gating một rubric mới trước lần sử dụng đầu tiên

> "evl:validate --rubric role-casting-fit"

Kỹ năng chạy `evl_schema.validate_rubric`. Nếu trọng số miền không tổng hợp thành 1.0, hoặc một tiêu chí thiếu điểm neo giữa, lỗi được in với đường dẫn trường chính xác. Sửa → chạy lại → PASS → an toàn để chấm điểm.

### Trường hợp sử dụng: Xác minh scorecard trước khi xuất bản lên CRE

> "evl:validate --scorecard docs/profiles/character-a/eval/psychometric-big-five.json --rubric psychometric-big-five"

Registry kiểm tra chạy bảy bằng chứng. Nếu `aggregate_math_correct` là FAIL, giá trị `overall` được lưu trữ không tái tạo từ điểm tiêu chí thô — scorecard có thể đã bị chỉnh sửa thủ công sau khi hoàn thành và phải được tái tạo trước khi CRE tin tưởng nó.

### Trường hợp sử dụng: Kiểm tra rubric hàng loạt trước khi phát hành thư viện

> "evl:validate --all --json | jq '.rubrics[] | select(.valid==false)'"

Trả về chỉ các rubric không hợp lệ, mỗi cái với danh sách lỗi. Hữu ích trước khi xuất một batch rubric mới để xác nhận không có regression.

### Trường hợp sử dụng: Kiểm tra nghiêm ngặt sau khi sửa đổi rubric

> "evl:validate --scorecard <path> --rubric <revised-id> --strict"

Sau khi thêm một tiêu chí vào rubric, các scorecard hiện có sẽ có hàng UNMAPPED cho id mới. `--strict` bề mặt chúng là FAIL — scorecard phải được chấm lại để bao gồm tiêu chí mới trước khi được coi là hiện tại.

## 5. Những lưu ý quan trọng

- Chế độ RUBRIC bắt các vấn đề cấu trúc; nó không thể bắt một rubric hợp lệ về mặt cấu trúc nhưng sai về mặt nội dung (ví dụ, điểm neo được hiệu chỉnh kém). Xem xét nội dung luôn là heuristic — phán xét LLM, không phải script này.
- `aggregate_math_correct` tính lại tổng hợp từ đầu bằng `evl_aggregate.aggregate`. Nếu rubric được sửa đổi giữa chấm điểm và xác thực, việc tính lại sử dụng rubric mới — sự không khớp sẽ FAIL ngay cả khi scorecard gốc đúng. Luôn xác thực theo cùng phiên bản rubric được sử dụng để chấm điểm.
- `--all` không đệ quy: nó chỉ đọc các `docs/rubrics/*.yaml` cấp cao nhất. Bản nháp hoặc import lồng trong các thư mục con không được kiểm tra trừ khi được truyền rõ ràng qua `--rubric <path>`.
- Cấu trúc đầu ra `--json`: `{mode, verdict, rubrics: [{id, valid, errors}]}` cho chế độ RUBRIC; `{mode, verdict, checks: [{check, status, detail}]}` cho chế độ SCORECARD. `verdict` cấp cao nhất luôn là `"PASS"` hoặc `"FAIL"`.
