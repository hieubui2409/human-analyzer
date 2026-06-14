# evl:rubric-import — Hướng dẫn

Cổng nhập framework bên ngoài: biến một công cụ đánh giá của bên thứ ba thành bản thảo rubric chuẩn hoá, được đánh dấu thiếu sót, sẵn sàng cho người dùng xem xét.

## 1. Kỹ năng này giúp bạn điều gì

Bạn đưa vào một framework bên ngoài — bộ trắc nghiệm tâm lý, bản tóm tắt tuyển vai, mô hình năng lực, hoặc bộ sàng lọc lâm sàng — dưới dạng tệp, văn bản dán vào, hoặc URL cần lấy. Kỹ năng phân tích văn bản thô thành danh sách tiêu chí rời, dựng khung rubric chuẩn hoá với chỗ trống TODO rõ ràng ở những trường không có cơ sở để điền, spawn sub-agent `evl-rubric-importer` để đề xuất ánh xạ ngữ nghĩa, tái xác thực đề xuất đó, và tuỳ chọn ghi bản thảo YAML ra `docs/rubrics/imported/`. Bản thảo không thể được chấm điểm cho đến khi `evl:validate` thông qua — điều đó đòi hỏi mọi thiếu sót phải được con người bổ sung đầy đủ.

## 2. Các khái niệm cơ bản (mô hình tư duy)

- **Phân tích vs. ánh xạ** — phân tích cú pháp (tất định, script) trích xuất cấu trúc từ văn bản thô. Ánh xạ (LLM sub-agent, cô lập đầu vào) đề xuất tiêu chí nào trong nguồn ngoài tương ứng với tiêu chí chuẩn nào, với trọng số và mốc neo nào. Hai bước này tách biệt để cấu trúc được phát minh không bao giờ trộn lẫn với cấu trúc tất định.
- **Thiếu sót là kết quả trung thực** — một tiêu chí không có cơ sở để xác định trọng số hay mốc neo sẽ vào `_import_gaps`, không vào rubric với giá trị đoán mò. Bản thảo nhiều thiếu sót là chính xác và trung thực; bản thảo được điền im lặng sẽ tạo ra điểm số giả mạo sau này.
- **Cô lập đầu vào** — sub-agent `evl-rubric-importer` chỉ thấy văn bản ngoài + schema chuẩn + kết quả phân tích. Không có dữ liệu nhân vật, không có rubric anh em. Điều này ngăn ô nhiễm chéo và giữ cho đề xuất ánh xạ có thể xem xét được.
- **Dấu hiệu bản thảo** — mọi rubric được nhập đều bắt đầu ở `version: 0.0.0` và `status: draft`. Nó bị chặn không được chấm điểm cho đến khi con người nâng cấp và `evl:validate` thông qua.
- **Không có mạng trong script** — lấy URL luôn là lệnh gọi WebFetch ở cấp độ skill. Script chạy offline và tất định.

## 3. Lộ trình học tập

1. Chạy `--input` trên một tệp markdown hai phần đơn giản (không có `--write`) và đọc YAML bản thảo cùng danh sách thiếu sót được in ra stdout.
2. Thử `--fmt freeform` trên một danh sách dấu đầu dòng thuần để xem cách phân tích freeform hoạt động.
3. Dùng `--write` để tạo bản thảo, sau đó mở `docs/rubrics/imported/<id>.yaml` và tự tay điền `weight`, `anchors`, và `min_tier` cho một tiêu chí.
4. Chạy `evl:validate` trên bản thảo đã điền để thấy gì thông qua và gì vẫn bị chặn.
5. Thử URL: lấy trang bằng WebFetch trong skill, dẫn văn bản qua `--stdin`, quan sát xem parser khôi phục được bao nhiêu cấu trúc và những gì rơi vào `_unclassified`.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Nhập mô hình năng lực dạng markdown

> "Nhập tệp markdown mô hình năng lực này dưới dạng rubric quyết định với id leadership-eval."

Kỹ năng đọc tệp, gọi script để phân tích và dựng khung, spawn agent nhập để đề xuất trọng số và mốc neo cho mỗi năng lực, tái xác thực đề xuất, và in YAML bản thảo kèm danh sách thiếu sót. Nếu người dùng yêu cầu ghi, `--write` tạo ra `docs/rubrics/imported/leadership-eval.yaml`.

### Trường hợp sử dụng: Nhập bộ trắc nghiệm tâm lý được dán vào

> "Đây là mô tả bộ Big Five — chuyển nó thành rubric tâm lý."

Kỹ năng nhận văn bản được dán qua `--stdin`, chọn `--kind psychometric`, chạy phân tích+dựng khung, spawn agent nhập, và trả về bản thảo + thiếu sót. Các thiếu sót (thường là mốc neo thang đo còn thiếu cho mỗi khía cạnh) được liệt kê rõ ràng để con người biết chính xác cần điền gì.

### Trường hợp sử dụng: Lấy và nhập framework công khai từ URL

> "Lấy https://example.org/clinical-screen và nhập nó dưới dạng rubric lâm sàng."

Kỹ năng gọi WebFetch (không phải script) để lấy văn bản trang, sau đó dẫn kết quả đến script qua `--stdin` với `--kind clinical --source "https://example.org/clinical-screen"`. Xuất xứ được nhúng vào `_source` để bản thảo có thể truy vết được.

## 5. Những lưu ý quan trọng

- Agent nhập đề xuất; cổng tái xác thực quyết định. Một đề xuất có thiện chí nhưng không thể được căn cứ trong văn bản nguồn phải vào `gaps`, không vào `mapping`.
- Không chỉnh sửa tệp bản thảo trong khi script đang chạy — ghi là nguyên tử (một lệnh `write_text` duy nhất) nhưng các chỉnh sửa đồng thời sẽ xung đột.
- Một rubric `version: 0.0.0` đã thông qua `evl:validate` nên được nâng lên `version: 1.0.0` trước lần chấm điểm sản xuất đầu tiên để thiết lập đường cơ sở xuất xứ sạch.
- Đầu vào freeform tạo ra phân tích mỏng nhất (một tiêu chí mỗi dòng không trống); ưu tiên markdown hoặc JSON/YAML khi nguồn có cấu trúc phân cấp.
- `--source` không được xác thực — cung cấp URL chuẩn hoặc chuỗi trích dẫn để bản thảo có thể kiểm tra được lâu sau khi phiên nhập kết thúc.
