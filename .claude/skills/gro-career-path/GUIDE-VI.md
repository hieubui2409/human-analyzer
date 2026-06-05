# gro:career-path — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn đang xây dựng hồ sơ nhân vật và muốn hiểu **sự liên kết sự nghiệp** của họ. Họ bắt đầu từ đâu? Những quyết định nào định hình họ? Họ có đang trên một lộ trình ổn định hay ở một điểm uốn cong? Kỹ năng này thu thập lịch sử sự nghiệp sự thật, dòng thời gian, và các quyết định chính của họ, sau đó phân tích thông qua hai khung: **Super's Life-Career Rainbow** (giai đoạn: Growth, Exploration, Establishment, Maintenance, Disengagement) và **SCCT** (Social Cognitive Career Theory — tự hiệu năng, kỳ vọng kết quả, mục tiêu cá nhân). Nó làm nổi bật chất lượng quyết định, yếu tố rủi ro, và cơ hội phát triển.

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thu thập dữ liệu, LLM đánh giá.** Tập lệnh Python chiết xuất dữ liệu sự nghiệp (lịch sử vai trò, ngày, lương nếu có sẵn, các quyết định chính). LLM sau đó áp dụng hai lĩnh vực đánh giá:

1. **Super's Life-Career Rainbow:** xác định giai đoạn nào nhân vật đang ở (tuổi, ổn định vai trò, các dấu hiệu khám phá kể câu chuyện). Tuổi + mô hình vai trò → giai đoạn.
2. **SCCT tự hiệu năng:** đánh giá sự tự tin trong lựa chọn sự nghiệp (họ có đảm nhận những vai trò đòi hỏi cao không? chuyển hướng quyết đoán? tránh rủi ro?). Bằng chứng đến từ mô hình quyết định và kết quả.

**Kịch bản là xác định; LLM là heuristic.** Kịch bản tìm dữ liệu; LLM đánh giá mô hình (ví dụ, "người này đưa ra quyết định táo bạo với sự tự tin vừa phải" vs "mô hình bảo thủ, nghi ngờ cao").

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:career-path --character <name>` — xem dòng thời gian sự nghiệp và tóm tắt quyết định. Chú ý đánh giá giai đoạn sự nghiệp.

**Tiếp theo:** `gro:career-path --all` — so sánh giai đoạn của cả 3 nhân vật song song. Một nhân vật có thể ở Establishment, cái khác ở Exploration.

**Sâu hơn:** `gro:career-path --decisions-only` — tập trung vào các quyết định sự nghiệp chính (thay đổi vai trò, giáo dục, chuyển hướng). Xem lý do quyết định, kết quả, và nó tiết lộ điều gì về các mô hình ra quyết định.

**Khi phát triển:** `gro:career-path --json` cho các bộ lập trình vào các kỹ năng hạ lưu (competency-map, career-forecast).

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Hiểu giai đoạn sự nghiệp hiện tại của nhân vật

> **Bạn:** "gro:career-path --character hieu"
>
> **Kỹ năng:** Thu thập lịch sử vai trò của Nhân vật A (giáo dục → công việc đầu tiên → vai trò hiện tại), ngày, và bối cảnh. LLM đánh giá: tuổi 28, 5 năm ở vai trò, các chứng chỉ gần đây, không có những chuyển hướng lớn → Có khả năng ở giai đoạn **Establishment** (cam kết vai trò, xây dựng chuyên môn). Yếu tố rủi ro: phạm vi kỹ năng hẹp. Cơ hội phát triển: những bước ngoài lề trong các lĩnh vực liên quan.
>
> **Sử dụng:** Bây giờ bạn biết mức độ trưởng thành sự nghiệp của Nhân vật A. Hữu ích để hiểu nhu cầu cố vấn, các lỗ hổng năng lực, hoặc cung cấp câu chuyện (ổn định vs xáo trộn).

### Trường hợp sử dụng: Phân tích các mô hình ra quyết định

> **Bạn:** "gro:career-path --character chien --decisions-only"
>
> **Kỹ năng:** Chiết xuất 4–5 quyết định sự nghiệp lớn (ví dụ, "rời startup để gia nhập công ty", "theo đuổi chứng chỉ", "đàm phán thăng chức"). Với mỗi một, LLM chấm điểm chất lượng bằng chứng, kết quả (thành công/trung lập/setback), và nó tiết lộ điều gì về khả năng chịu rủi ro và sự tự tin.
>
> **Sử dụng:** Xem liệu nhân vật có tránh rủi ro, theo cơ hội, cân nhắc, hay phân tán. Hữu ích để dự đoán hành vi trong tương lai hoặc phát triển động lực nhân vật.

## 5. Những lưu ý quan trọng

- **Tự hiệu năng là heuristic.** LLM suy ra sự tự tin từ mô hình quyết định và kết quả; đây là suy đoán có giáo dục, không phải một bài kiểm tra tâm lý được xác thực.
- **Không phân tích lĩnh vực PSY.** Career-path phân tích quyết định sự nghiệp và giai đoạn, không những người lái tâm lý (gắn kết, phòng vệ, chấn thương, v.v.). Nếu bạn cần "tại sao họ đưa ra lựa chọn đó về mặt tâm lý?", dùng lĩnh vực PSY.
- **Biên giới (Rule 15):** Đọc từ PSY (ví dụ, growth-edges để có bối cảnh) nhưng không bao giờ đánh giá PSY hoặc ghi chéo vào các tệp PSY.
- **Chất lượng bằng chứng quan trọng.** Phân tích này tốt bằng dữ liệu trong growth/career-path.md. Ngày thiếu, quyết định mơ hồ, hoặc dữ liệu cũ làm suy yếu độ chính xác.
