# mat:rescore — Hướng dẫn

> Cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Khi bạn tải tài liệu vào quy trình MAT, mỗi tài liệu sẽ nhận được điểm CRAAP (Tính hiện tại, Mức độ liên quan, Cơ sở quyền lực, Độ chính xác, Mục đích). Nhưng các tệp được tải trong vội vã, và một số có thể có các trường bị thiếu, điểm không đầy đủ hoặc lỗi toán học (ví dụ: tổng = 5+4+3+2+1 = 15, nhưng siêu dữ liệu nói 14). mat:rescore kiểm toán tất cả tài liệu của bạn và bề mặt những tài liệu cần sửa. Nó không sửa chúng — bạn quyết định tệp nào sẽ chạy lại qua `mat:loader --ingest` để nhận điểm tươi.

## 2. Khái niệm cốt lõi (mô hình tinh thần)

**CRAAP là một cánh cổng chất lượng, không phải một nhãn.** Điểm dưới 15/25 vẫn có thể là bằng chứng hữu ích; nó chỉ có nghĩa là tài liệu ở mức chất lượng biên giới và yêu cầu xem xét thêm. Rescore xác định tài liệu nào thiếu điểm hoàn toàn hoặc có điểm không đầy đủ — bản kiểm toán chính nó là trung lập.

**Kích hoạt Rescore (khi cần rescore):**
- Tệp không có khóa `craap_score` (không bao giờ điểm).
- Một hoặc nhiều trường (tính hiện tại, mức độ liên quan, cơ sở quyền lực, độ chính xác, mục đích) là null hoặc thiếu.
- Trường `total` không khớp với tổng các trường riêng lẻ (lỗi toán).
- Tệp vẫn ở `processing_status: raw` (không bao giờ di chuyển qua tiếp nhận).
- Tệp không có siêu dữ liệu YAML (không tuân thủ MAT).

**Kịch bản thu thập; bạn phán xét.** Công việc của mat:rescore là kiểm toán thuần túy: tìm và liệt kê. Nó không khuyến cáo lưu trữ, không xếp hạng chất lượng, không quyết định tích hợp. Nó chỉ nói "những N tệp này cần điểm." Bạn sau đó quyết định có nên re-ingest chúng, để chúng như cũ (nếu bạn chấp nhận rủi ro) hay lưu trữ chúng.

**Kiểm toán với phạm vi nhân vật:** Theo mặc định, mat:rescore kiểm tra tất cả các nhân vật. Bạn có thể thu hẹp nó thành một với `--character <name>` nếu bạn đang làm dọn dẹp nhắm mục tiêu.

## 3. Đường dẫn học tập

1. **Kiểm toán đầy đủ:** `mat:rescore` — xem tất cả tài liệu cần rescore trên tất cả các nhân vật.
2. **Xem bản tóm tắt:** Quét bảng "Materials Needing Rescore" và phân tích "Summary by Character".
3. **Thu hẹp theo nhân vật:** `mat:rescore --character character-a` — chỉ vấn đề của Nhân vật A.
4. **Tập trung vào khoảng trống quan trọng:** `mat:rescore --missing-only` — chỉ các tệp có không CRAAP (ưu tiên cao nhất).
5. **Tập trung vào trạng thái thô:** `mat:rescore --raw-only` — chỉ các tệp bị mắc kẹt ở "raw" (không bao giờ xử lý).
6. **Hành động:** Đối với các tệp được đánh dấu, chạy `mat:loader --ingest <file>` để điểm lại chúng.

## 4. Các trường hợp sử dụng

### Trường hợp sử dụng: Kiểm toán ban đầu sau tải hàng loạt
> **Bạn:** "Tôi vừa tải 50 tài liệu. Chúng có tất cả được điểm đúng không?"
> 
> **Kỹ năng:** `mat:rescore`:
> ```
> Tài liệu cần rescore
> | Tệp | Nhân vật | Lý do | Trạng thái hiện tại | Điểm hiện tại |
> | transcript-jan.md | hieu | missing craap_score | raw | — |
> | letter-old.md | hoa | partial (authority=null) | extracted | 12/25 |
> | interview-2025.md | chien | total ≠ sum (says 20, is 19) | validated | 20/25 |
> Tổng: 12 tài liệu cần rescore
> ```
> Bạn thấy: 12 tệp có vấn đề. 1 hoàn toàn thiếu điểm, 1 có điểm không đầy đủ, 1 có lỗi toán.

### Trường hợp sử dụng: Bản tóm tắt theo nhân vật
> **Bạn:** "Tài liệu của nhân vật nào là ít hoàn thành nhất?"
> 
> **Kỹ năng:** `mat:rescore` tạo ra bản tóm tắt:
> ```
> | Nhân vật | Tổng | Cần rescore | % Sạch |
> | hieu | 20 | 3 | 85% |
> | hoa | 18 | 8 | 56% |
> | chien | 25 | 1 | 96% |
> ```
> Bạn thấy: tài liệu của Hoà chỉ sạch 56%. Bạn có thể ưu tiên rescore tệp của Hoà.

### Trường hợp sử dụng: Tìm khoảng trống quan trọng
> **Bạn:** "Chỉ hiển thị tài liệu không bao giờ được điểm."
> 
> **Kỹ năng:** `mat:rescore --missing-only`:
> ```
> | Tệp | Nhân vật | Lý do | Trạng thái |
> | transcript-undated.md | hieu | missing craap_score | raw |
> | conversation-log.md | hoa | missing craap_score | extracted |
> Tổng: 2 tài liệu có không CRAAP
> ```
> Bạn thấy: 2 tệp có khoảng trống điểm hoàn toàn. Đây là ưu tiên cao nhất vì không có thông tin chất lượng nào cả.

### Trường hợp sử dụng: Dọn sạch tài liệu thô
> **Bạn:** "Tôi có tài liệu cũ bị mắc kẹt ở trạng thái 'raw'. Chúng có điểm CRAAP hoàn chỉnh không?"
> 
> **Kỹ năng:** `mat:rescore --raw-only`:
> - Liệt kê tất cả tài liệu có `processing_status: raw`
> - Đánh dấu cái nào có CRAAP không đầy đủ hoặc thiếu
> - Gợi ý: hoặc kết thúc rescoring chúng bằng `mat:loader --ingest`, hoặc sử dụng `mat:archive --status raw` để loại bỏ

### Trường hợp sử dụng: Xuất JSON cho công cụ
> **Bạn:** "Tôi muốn tích hợp kết quả rescore vào bảng điều khiển tùy chỉnh. JSON vui lòng."
> 
> **Kỹ năng:** `mat:rescore --json`:
> ```json
> {
>   "materials_needing_rescore": [
>     {
>       "file": "transcript-jan.md",
>       "character": "hieu",
>       "reason": "missing craap_score",
>       "current_status": "raw",
>       "current_score": null
>     }
>   ],
>   "summary_by_character": [ ... ]
> }
> ```
> Bạn đưa điều này đến các kịch bản của riêng bạn.

## 5. Những cảnh báo quan trọng

**Cờ Rescore hoạt động, không thất bại.** Tệp cần rescore không bị hỏng — nó chỉ cần chú ý. Một số trường hợp là tầm thường (lỗi toán trong trường tổng); những trường hợp khác đòi hỏi tái đọc tài liệu và chạy lại CRAAP. Không phải tất cả các tệp được đánh dấu cần hành động ngay lập tức.

**Thiếu điểm ≠ tài liệu xấu.** Nếu tệp không có điểm CRAAP, nó có thể là hoàn toàn mới (chưa được điểm) hoặc tải lên trước khi hệ thống điểm bắt buộc. Nó không tự động chất lượng thấp; nó chỉ chưa được đánh giá chính thức. Bạn quyết định có điểm nó, để nó không được điểm hay lưu trữ nó.

**Điểm một phần có thể cứu vãn được.** Nếu tệp có 4 trên 5 trường CRAAP nhưng thiếu "authority," bạn thường có thể re-ingest nó với `mat:loader --ingest` để điền khoảng trống, thay vì coi tệp là không sử dụng được.

**Rescore không tàn phá.** Chạy `mat:rescore` không bao giờ thay đổi tài liệu của bạn. Nó là báo cáo thuần túy. Ngay cả khi bạn thấy 30 tệp được đánh dấu, bạn có thể bỏ qua chúng và tiếp tục làm việc — không có hậu quả tự động.

**Rescore không thay thế phán xét của con người.** Một số tài liệu có thể có điểm CRAAP thấp nhưng lại không thể cincredibly quý giá cho bối cảnh. Những cái khác có thể có điểm cao nhưng tỏ ra không đáng tin cậy. Điểm là công cụ kiểm toán, không phải từ cuối cùng.
