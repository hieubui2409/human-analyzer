# orc:agent-memory — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Hãy tưởng tượng bạn có ba tác nhân miền chuyên biệt (nhà tâm lý học, chiến lược gia nội dung, nhà phân tích tăng trưởng) làm việc trên hồ sơ nhân vật của bạn. Mỗi tác nhân học được các kiến thức từ công việc của họ—những cơ chế phòng vệ nào của nhân vật kích hoạt dưới áp lực, những móc viết nào hoạt động tốt nhất trên LinkedIn, năng lực phát triển như thế nào. Nếu không có bộ nhớ, mỗi phiên bắt đầu từ điểm không. Với bộ nhớ, họ xây dựng dựa trên những gì họ đã học. Kỹ năng này quản lý tầng học tập chung đó.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Ba tác nhân, một bộ nhớ cho mỗi tác nhân.** Mỗi tác nhân có một tệp bộ nhớ (`.claude/agent-memory/{agent-name}.md`) chứa:
- **Kiến thức về Nhân vật:** Các hiệu chỉnh cụ thể miền được học về từng nhân vật (ví dụ, "Nhân vật B's avoidance intensifies under academic pressure" cho nhà tâm lý học).
- **Các Mẫu Học:** Các mẫu tích lũy qua nhiều phiên (ví dụ, "LinkedIn vulnerability-hook + resolution structure hoạt động").
- **Anti-Patterns:** Những gì không hoạt động, vì vậy các tác nhân tránh lặp lại nó.
- **Các Mẫu Được Thăng cấp Bản năng:** Các kiến thức độ tin cậy cao được thăng cấp từ kho bản năng bởi `orc:dream`.

**Tại sao điều này quan trọng:** Các tác nhân có thể đọc bộ nhớ của họ khi bắt đầu công việc và điều chỉnh hành vi dựa trên những gì đã hoạt động trước đây. Họ ghi lại những phát hiện ở cuối. Theo thời gian, bộ nhớ phong phú và đáng tin cậy hơn.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `--show` — xem xét bộ nhớ có tồn tại và những gì bên trong nó. Có thể trống rỗng trong phiên đầu tiên.

**Lần chạy thứ hai (nếu khởi tạo):** `--seed` — khởi tạo từ hồ sơ hiện tại và bản năng độ tin cậy cao. Điều này "sơ khởi" bộ nhớ với những gì đã biết.

**Liên tục:** Các tác nhân tự nhiên đọc/ghi. Bạn không gọi kỹ năng này liên tục—chỉ khi bạn cần kiểm tra hoặc đặt lại bộ nhớ.

**Hợp nhất định kỳ:** Nếu bộ nhớ cảm thấy rải rác, `orc:dream` hợp nhất các kiến thức trùng lặp và thăng cấp các mẫu mạnh vào bộ nhớ tác nhân.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Xem những gì nhà tâm lý học đã học được về Nhân vật B

> Bạn: "Show me what the psychologist agent knows about Nhân vật B"
>
> Kỹ năng: Đọc `.claude/agent-memory/psychologist.md`, trích xuất kiến thức về Nhân vật B (ví dụ, các mẫu bổ cập, kích hoạt phòng vệ), và hiển thị chúng với thống kê bản năng. Bạn thấy hiệu chỉnh hình thành cách công việc PSY trong tương lai xử lý cô ấy.

### Trường hợp sử dụng: Khởi tạo bộ nhớ sau các cập nhật hồ sơ chính

> Bạn: "The profiles are now complete. Seed all agent memories from them."
>
> Kỹ năng: Đọc mỗi formulation.md của nhân vật (cho nhà tâm lý học), writing-voice.md (cho chiến lược gia nội dung), career-path.md (cho nhà phân tích tăng trưởng), cộng với các bản năng độ tin cậy cao. Điền vào bộ nhớ tác nhân với kiến thức cơ sở nhân vật và các mẫu. Phiên tiếp theo, các tác nhân bắt đầu được thông báo.

### Trường hợp sử dụng: Đặt lại bộ nhớ để xóa các mâu thuẫn

> Bạn: "Agent memory has contradictions. Reset and back it up."
>
> Kỹ năng: Lưu trữ bộ nhớ hiện tại vào `.claude/agent-memory/.archive/{date}/`, ghi các mẫu tươi, và xác nhận. Các tác nhân bây giờ bắt đầu với bảng trắng; kho bản năng tồn tại (hệ thống riêng biệt).

### Trường hợp sử dụng: Kiểm tra dữ liệu liên quan bản năng cho chiến lược gia nội dung

> Bạn: "What instincts are relevant to the content-strategist's work?"
>
> Kỹ năng: Lọc các bản năng theo danh mục tác nhân (viết, khán giả), hiển thị những cái có điểm số độ tin cậy, và làm nổi bật các ứng cử viên thăng cấp (kiến thức sẵn sàng để thăng cấp vào bộ nhớ tác nhân).

## 5. Những cảnh báo quan trọng

- **Bộ nhớ là tích cực, không tự động sửa chữa.** Nếu tác nhân ghi lại điều gì đó sai, nó vẫn tồn tại cho đến khi được xóa thủ công. Kỹ năng `orc:dream` xử lý dọn dẹp; dùng `--reset` để reset khó.
- **Bản năng là riêng biệt.** Bộ nhớ tác nhân là tầng được tuyển chọn, cụ thể miền. Bản năng là tầng tiến hoá, được chấm điểm. Cả hai nuôi học tập, nhưng chúng có các mục đích khác nhau.
- **Các tác nhân phải quyết định sử dụng nó.** Kỹ năng này không tự động kích hoạt. Các tác nhân cần được thiết kế để đọc bộ nhớ trước công việc và ghi sau. Đó là một công cụ có sẵn cho họ, không phải một cổng bắt buộc.
- **Chỉ ba tác nhân.** Bộ nhớ được phạm vi cho ba tác nhân miền được mã hóa cứng (nhà tâm lý học, chiến lược gia nội dung, nhà phân tích tăng trưởng). Các tác nhân khác không có tệp bộ nhớ ở đây.
