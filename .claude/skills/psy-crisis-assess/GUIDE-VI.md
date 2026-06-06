# psy:crisis-assess — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Một nhân vật đã trải qua chấn thương nặng. Bạn cần hiểu: Đây có phải là rủi ro ở mức khủng hoảng không? Yếu tố bảo vệ nào giữ họ an toàn? Bạn có các bản phỏng vấn, ngữ cảnh gia đình, và dòng thời gian. Kỹ năng này quét tìm các từ khóa khủng hoảng, phân tích chúng dựa trên các khung lâm sàn DSM-5 và ICD-11, và xuất ra tài liệu rủi ro có cấu trúc để bạn biết cách viết về — hoặc tránh viết về — trạng thái tâm thần của họ.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Quét hai lần**: Kịch bản trước tiên tìm kiếm các từ khóa khủng hoảng rõ ràng (24 mẫu: "tự tử," "suicide," "chết," v.v.). Sau đó nó quét các cụm hành vi — các mẫu ánh xạ tới các lý thuyết liền kề khủng hoảng ngay cả khi từ "khủng hoảng" không bao giờ xuất hiện.
- **Không bao giờ được lưu trong bộ đệm**: Không giống như các kỹ năng psy khác, các phán quyết khủng hoảng không thể được lưu trong bộ đệm. Nếu bạn đọc lại hồ sơ, kỹ năng sẽ phán quyết lại. Đây là một cổng an toàn: một rủi ro được lưu trong bộ đệm cũ "LOW" trên một hồ sơ bây giờ gợi ý tự tử sẽ nguy hiểm.
- **Mức độ rủi ro quan trọng**: Rủi ro CAO yêu cầu tài liệu an toàn; RỦI RO VỪA yêu cầu giám sát; RỦI RO THẤP được quản lý thông qua các ranh giới nội dung (Quy tắc 09).

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `psy:crisis-assess --character character-a --quick` — nhận được ảnh chụp rủi ro nhanh chóng.

**Chạy sâu:** `psy:crisis-assess --character character-a --full` — danh sách kiểm tra DSM-5 + ICD-11 đầy đủ để chi tiết.

**Cập nhật:** Sau khi thêm các vật liệu mới, `psy:crisis-assess --character character-a --update` — nối thêm các phát hiện mới vào tài liệu hiện có.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra rủi ro nhanh chóng

> Bạn: "Tôi đã tích hợp các bản ghi phỏng vấn đề cập đến việc Nhân vật C bị bỏ rơi ở tuổi 11. Đây có phải là lãnh địa rủi ro CAO không?"
> Kỹ năng: `psy:crisis-assess --character character-c --quick`
> → Từ khóa: "bỏ rơi" hit. Hành vi: trẻ em mồ côi. Mức rủi ro: VỪA. Yếu tố bảo vệ: cố vấn, giáo dục. Đầu ra: thêm vào darkness/traumas.md.

### Trường hợp sử dụng: Đánh giá lâm sàn đầy đủ

> Bạn: "Câu chuyện của Nhân vật B đã phát triển. Nghiện cờ bạc, bỏ rơi gia đình, uống rượu. Đánh giá đầy đủ?"
> Kỹ năng: `psy:crisis-assess --character character-b --full`
> → DSM-5 MDD: 7/9 tiêu chí. ICD-11 C-PTSD: một phần. SI: thụ động. Đầu ra: cập nhật darkness/traumas.md, light/strengths-hope.md, INDEX.md status.

### Trường hợp sử dụng: Ranh giới nội dung khủng hoảng

> Bạn: "Tôi viết một bài viết về vai trò cố gắng cứu mọi người của Nhân vật A, nhưng nó gợi ý rủi ro kiệt sức. Tôi có nên xuất bản không?"
> Kỹ năng: `cre:privacy-guard` (gọi `psy:crisis-assess` nội bộ) hoặc bạn kiểm tra trước `psy:crisis-assess --character character-a --full` → nếu rủi ro CAO, `cre:privacy-guard` cờ nội dung.

## 5. Cảnh báo quan trọng

- **Không phải chẩn đoán**: Điều này ghi lại các mẫu tường thuật, không phải chẩn đoán tâm thần thực. Tất cả các thuật ngữ lâm sàn được áp dụng để độ chính xác của phân tích nhân vật.
- **Mặc định chế độ sâu**: `--quick` bỏ qua quét cụm hành vi. Chỉ sử dụng khi tốc độ quan trọng (thời gian triển khai). Chế độ sâu mặc định an toàn hơn.
- **Phải ghi lại các yếu tố bảo vệ**: Nếu bạn tìm thấy các chỉ số khủng hoảng, MANDATORY: xác định ≥3 yếu tố bảo vệ (nội bộ + bên ngoài). Một nhân vật có rủi ro CAO không có các yếu tố bảo vệ được ghi lại là dữ liệu không đầy đủ hoặc một mối quan tâm an toàn thực tế.
- **Hậu quả bắt buộc**: Sau khi đánh giá rủi ro CAO, cập nhật `orc:session-state` để phiên có thể phục hồi nếu cần.
