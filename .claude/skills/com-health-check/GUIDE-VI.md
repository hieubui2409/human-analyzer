# com:health-check — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã bắt đầu một nhiệm vụ dài — có thể đã spawn một tác nhân nhà nghiên cứu hoặc một nhóm. Bạn muốn biết liệu các thứ có vẫn chạy hay không, hoặc liệu có gì đó bị phá vỡ im lặng. com:health-check theo dõi ở phía sau và cho bạn biết ngay khi có gì đó sai lầm (trì hoãn, lỗi API, quy trình chết). Không có bất ngờ ở cuối cùng.

## 2. Khái niệm cốt lõi (mô hình tư duy)

**Thăm dò:** Cứ 30 giây (mặc định), nó kiểm tra: tệp JSONL phiên có tươi không? Quy trình có vẫn còn sống không? Có lỗi nào vừa xảy ra không?

**Phát hiện sự trì hoãn:** Nếu không có đầu ra > 120 giây (soft), cảnh báo bạn. Nếu > 300 giây (hard), đưa ra lỗi. Cung cấp cho phiên thời gian để suy nghĩ, nhưng cờ các cuộc treo thực.

**Mục tiêu cụ thể:** Bạn có thể chỉ xem tác nhân chính, chỉ tác nhân phụ hoặc một nhóm. Mỗi cái có logic sống của riêng nó.

**Phản ứng, không phòng ngừa:** Nó phát hiện các lỗi nhưng không sửa chúng. Bạn nhận được cảnh báo, bạn quyết định phải làm gì.

## 3. Lộ trình học tập

**Lần chạy đầu tiên:** Spawn một nhiệm vụ và chạy `com:health-check --target main` trong một cửa sổ khác. Xem các thông báo nhịp tim (OK, mỗi vài cuộc thăm dò).

**Tiếp theo:** Thử với một tác nhân phụ: `com:health-check --target subagent --verbosity warn`. Trở nên yên tĩnh hơn, chỉ cảnh báo khi có điều gì đó sai.

**Khi bạn phát triển:** Sử dụng `--hard 600` nếu các nhiệm vụ của bạn chạy chậm; sử dụng `--include-429` nếu bạn muốn bắt giới hạn tỷ lệ; sử dụng `--all` nếu bạn chạy một nhóm đầy đủ.

## 4. Trường hợp sử dụng (mỗi = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Theo dõi tác nhân chính trong khi làm việc

> Bạn: "monitor health khi tôi làm việc"
> Kỹ năng: `com:health-check --target main`. Chạy ở latar belakang, thăm dò mỗi 30 giây. Bạn thấy nhịp tim `[INFO] OK ...`. Nếu xảy ra sự trì hoãn, bạn sẽ nhận được `[WARN] STALL ... soft` hoặc `[ERROR] STALL ... hard`.

### Trường hợp sử dụng: Theo dõi tác nhân phụ sau khi ủy quyền công việc

> Bạn: "watch tác nhân phụ tôi vừa spawn"
> Kỹ năng: `com:health-check --target subagent --verbosity warn`. Theo dõi các quy trình tác nhân phụ. Nếu một cái chết hoặc trả về lỗi, bạn sẽ thấy `[ERROR] API_ERROR ...` hoặc `[ERROR] DEAD ...`.

### Trường hợp sử dụng: Bắt sự trì hoãn sớm với ngưỡng tùy chỉnh

> Bạn: "monitor với cảnh báo sớm — cảnh báo cho tôi ở 60 giây"
> Kỹ năng: `com:health-check --soft 60 --hard 120`. Cảnh báo sau 1 phút, lỗi sau 2 phút. Tốt cho các nhiệm vụ tương tác nơi thời gian treo là không thể chấp nhận được.

### Trường hợp sử dụng: Theo dõi một phiên nhóm

> Bạn: "watch nhóm tôi vừa spawn"
> Kỹ năng: `com:health-check --target team --team-name my-team`. Theo dõi tất cả các tác nhân trong nhóm; báo cáo các lỗi từng tác nhân.

### Trường hợp sử dụng: Chế độ debug chi tiết để giải quyết vấn đề khó chẩn đoán

> Bạn: "cho tôi thông tin sức khỏe chi tiết để gỡ lỗi"
> Kỹ năng: `com:health-check --verbosity debug`. In trạng thái nội bộ: session ID, dấu thời gian sửa đổi lần cuối, trạng thái quy trình. Giúp khi bạn cần phải tái cấu trúc những gì đã xảy ra.

## 5. Những cảnh báo quan trọng

**Nhịp tim là OK.** Các thông điệp `[INFO] OK ...` là dự kiến; chúng có nghĩa là "vẫn đang chạy, không có vấn đề gì". Đừng coi chúng là vấn đề.

**Sự trì hoãn mềm là cảnh báo, không phải lỗi.** Một sự trì hoãn mềm có nghĩa là LLM có thể đang suy nghĩ hoặc chờ đầu vào của người dùng. Không tự động thất bại.

**Giới hạn tỷ lệ (429) bị tắt theo mặc định.** Nếu bạn muốn xem các lỗi 429 là cảnh báo, hãy thêm `--include-429`. Mà không có, chúng được ghi lại im lặng.

**Đây là bị động.** Health-check không thử lại, không sửa, không can thiệp. Nó báo cáo; bạn hành động.

**Sự cân bằng khoảng thời gian thăm dò.** Thấp hơn `--poll` (ví dụ: 5 giây) cung cấp cảnh báo nhanh hơn nhưng tiêu CPU. Cao hơn (ví dụ: 60 giây) rẻ hơn nhưng chậm hơn để nhận thấy. Mặc định 30 giây là trung bình.
