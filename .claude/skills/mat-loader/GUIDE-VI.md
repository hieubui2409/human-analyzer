# mat:loader — Hướng dẫn

> Cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn có một chồng các cuộc phỏng vấn mới, thư từ và bài báo về các nhân vật của bạn. Trước khi chúng có thể cấp cho phân tích tâm lý hoặc tạo nội dung, chúng cần siêu dữ liệu được chuẩn hóa, chấm điểm chất lượng và phân loại. mat:loader tự động hóa điều đó: bạn trỏ nó đến một tệp, nó phát hiện nó là gì, ai nó nói về, chạy kiểm tra chất lượng CRAAP, đóng dấu nó bằng tầng bằng chứng (T1–T5), và đặt nó đúng chỗ.

## 2. Khái niệm cốt lõi (mô hình tinh thần)

**Tầng bằng chứng (T1–T5):** Tài liệu của bạn có mức độ đáng tin cậy khác nhau. T1 là lời nói của chính nhân vật (độ tin cậy cao nhất); T5 là khung lý thuyết (thấp nhất). Tầng quyết định những tuyên bố nào có thể cấp cho công việc tâm lý và những gì có thể xuất hiện trong nội dung được xuất bản.

**Chấm điểm CRAAP (1–5 mỗi chiều):** Tính hiện tại, Mức độ liên quan, Cơ sở quyền lực, Độ chính xác, Mục đích. Điểm 15/25 là cổng tối thiểu để tích hợp giai đoạn 3; dưới đó, tài liệu được đánh dấu để xem xét thủ công.

**Trạng thái xử lý (trạng thái quy trình):** raw → extracted → analyzed → validated → integrated → archived. mat:loader đặt **raw**; các kỹ năng tiếp theo di chuyển tài liệu về phía trước. Bạn có thể thấy toàn bộ quy trình một cách nhanh chóng với `--status`.

**Ranh giới miền:** mat:loader không bao giờ chạm vào hồ sơ hoặc tham khảo — chỉ `docs/materials/` tồn tại trong thế giới của nó. Phân tích tâm lý xảy ra ở hạ lưu.

## 3. Đường dẫn học tập

1. **Lần chạy đầu tiên:** `mat:loader --list` — xem những gì bạn đã có. Cảm nhận loại tài liệu và các tầng.
2. **Thêm tài liệu mới:** `mat:loader --ingest ~/my-new-transcript.md` — đi bộ qua một cuộc tiếp nhận đầy đủ (phát hiện loại, nhân vật, ngày, CRAAP, tầng).
3. **Kiểm tra quy trình:** `mat:loader --status` — xem tài liệu đang tắc ở đâu (ví dụ: 5 tệp bị mắc kẹt ở "raw").
4. **Trích xuất các sự kiện:** `mat:loader --extract "gambling"` — tìm kiếm nhanh trên tất cả các tài liệu cho một chủ đề cụ thể.

## 4. Các trường hợp sử dụng

### Trường hợp sử dụng: Tiếp nhận tài liệu ban đầu
> **Bạn:** "Tôi có một bản ghi cuộc trò chuyện với Nhân vật C mà tôi đã chép lại. Vui lòng tải nó."
> 
> **Kỹ năng:** Chạy `--ingest` trên bản ghi lại:
> - Phát hiện loại: conversation_log
> - Trích xuất nhân vật: character-c
> - Quét tìm ngày tháng
> - Chạy kiểm tra CRAAP (Currency=4, Relevance=5, Authority=3, Accuracy=4, Purpose=4 → **20/25**)
> - Gán tầng bằng chứng: **T2** (quan sát được xác thực chéo)
> - Tiêm siêu dữ liệu YAML với tất cả các trường
> - Di chuyển tệp đến `docs/materials/character-c/` với tên được chuẩn hóa
> - Hiển thị cho bạn bảng tóm tắt: loại, tầng, điểm CRAAP, bước tiếp theo (mat:indexer)

### Trường hợp sử dụng: Kiểm tra trạng thái quy trình
> **Bạn:** "Trạng thái của tất cả các tài liệu của chúng ta hiện nay là gì?"
> 
> **Kỹ năng:** Chạy `--status`:
> ```
> Trạng thái   Số lượng  Tệp
> raw          5         transcript-jan.md, letter-undated.md, ...
> extracted    12        (tệp đang bay)
> validated    18        (sẵn sàng để tích hợp)
> integrated   3         (đã cấp cho tâm lý)
> ```
> Bạn thấy: 5 tệp bị mắc kẹt ở "raw" — bạn cần hoàn thành việc nạp chúng hoặc xem xét tại sao chúng bị mắc kẹt.

### Trường hợp sử dụng: Kho lưu trữ dành riêng cho nhân vật
> **Bạn:** "Hiển thị tất cả tài liệu cho Hoà."
> 
> **Kỹ năng:** Chạy `--character character-b`:
> - Liệt kê tất cả tệp có slug ký tự của Hoà
> - Nhóm theo loại (conversation_log, letter, news_article, v.v.)
> - Hiển thị phân bố tầng, điểm CRAAP, trạng thái xử lý
> - Đếm dòng, ngày sửa đổi
> - Gợi ý các điểm tắc nghẽn hoặc khoảng trống phạm vi

### Trường hợp sử dụng: Tìm kiếm nhanh các sự kiện
> **Bạn:** "Chúng ta có nắm bắt được gì về các triệu chứng lo âu của Hồ không?"
> 
> **Kỹ năng:** Chạy `--extract "anxiety"` trên tất cả các tài liệu:
> - Tìm kiếm nội dung văn bản + thẻ siêu dữ liệu
> - Trả về các dòng phù hợp với tệp nguồn + tầng bằng chứng
> - Giúp bạn thấy nếu tuyên bố đó đã được hỗ trợ bằng bằng chứng

## 5. Những cảnh báo quan trọng

**CRAAP là một cánh cổng, không phải chẩn đoán.** Điểm CRAAP thấp (ví dụ: 10/25) không có nghĩa là tài liệu sai — nó có thể là một tài khoản tay hai hoặc lỗi thời. Tùy thuộc vào ngưỡng của bạn, bạn vẫn có thể nạp nó; điểm cảnh báo nó để xem xét thủ công.

**Tầng bằng chứng không giống như chất lượng nguồn.** T1 (tuyên bố của chính nhân vật) có thể không đáng tin nếu nhân vật nói dối hoặc bị nhầm lẫn. T2 (quan sát được xác thực chéo) từ một nhà trị liệu đáng tin cậy hơn. Tầng ghi lại *loại nguồn*, không phải *sự thật*.

**Trạng thái xử lý không phải tự động.** mat:loader đặt trạng thái thành "raw" trên tiếp nhận. Di chuyển nó đến "extracted", "analyzed", "validated" hoặc "integrated" đòi hỏi hành động rõ ràng (thường là phán xét LLM sau mat:indexer hoặc xem xét thủ công).

**Không tích hợp mà không có mat:indexer.** Tài liệu được tải là không hoạt động — chúng không cấp cho phân tích tâm lý cho đến khi chúng vượt qua giai đoạn 3–4 (mat:indexer). Cánh cổng này được đặt tại chỗ để bắt các mâu thuẫn sớm (Quy tắc 11).

**Chạy khô trước khi bạn viết.** Sử dụng `--dry-run` hoặc xem lại các bảng xem trước trước khi lưu trữ hoặc cập nhật hàng loạt tài liệu. Sau khi một tệp được đánh dấu lưu trữ, nó sẽ ra khỏi quy trình hoạt động.
