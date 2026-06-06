# psy:crossref — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn cập nhật hồ sơ của Nhân vật A bằng một sự kiện mới, nhưng quên cập nhật câu chuyện của Nhân vật B — họ là những anh em kết nghĩa, vì vậy sự kiện ảnh hưởng đến cả hai. Hoặc bạn nhận thấy Nhân vật A nói anh gặp Nhân vật B vào tháng 7 năm 2025, nhưng dòng thời gian của Nhân vật B nói tháng 6. Kỹ năng này bắt những điểm gãy: nó đọc tất cả các hồ sơ, tìm mọi đề cập đến nhân vật khác, và kiểm tra xem ngày tháng có khớp, cảm xúc có tương thích, và chi tiết không có mâu thuẫn.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Xác định + LLM**: Các chiều 1–4 (ngày tháng, tham chiếu gia đình, liên kết tâm lý, dữ liệu cứng) chạy kiểm tra dựa trên kịch bản. Các chiều 5–10 (hỗ trợ bằng bằng chứng, sự liên kết của câu chuyện, sự nhất quán về giọng nói) cần sự phán xét của con người — LLM làm điều đó.
- **Bộ đệm phán quyết**: 6 chiều của LLM sử dụng lại các phán quyết được lưu trong bộ đệm nếu phần hồ sơ không thay đổi (xác minh bằng mã băm nội dung). Điều này tiết kiệm mã thông báo. Các phán quyết khủng hoảng không bao giờ được lưu trong bộ đệm (luôn chạy lại).
- **Mức độ nghiêm trọng quan trọng**: Sự không khớp ngày tháng là QUAN TRỌNG (một trong hai là sai). Một tông cảm xúc khác là NHỎ (cả hai cảm xúc hợp lệ, chỉ được khung khác nhau).

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `psy:crossref --pair hieu hoa` — kiểm tra chỉ anh em kết nghĩa, xem định dạng.

**Mở rộng:** `psy:crossref --all --extended` — chạy tất cả các cặp, tất cả 10 chiều. Mong đợi một báo cáo phong phú.

**Lặp lại:** Sửa các vấn đề trong hồ sơ, sau đó `psy:crossref --fresh` để xóa bộ đệm và kiểm tra lại.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra dòng thời gian nhanh chóng

> Bạn: "Tôi đã thêm Oct 2025 vào dòng thời gian của Nhân vật A cho cuộc khủng hoảng cờ bạc. Nhân vật B có đồng ý không?"
> Kỹ năng: `psy:crossref --timeline --pair hieu hoa`
> → Tìm thấy dòng thời gian của Nhân vật B nói Sep 2025. Sự không khớp QUAN TRỌNG. Bạn sửa một trong hai, chạy lại.

### Trường hợp sử dụng: Xác thực đầy đủ

> Bạn: "Tôi viết lại psychology/formulation.md của Nhân vật A và thêm các mối quan hệ mới. Có bất kỳ điểm gãy nào không?"
> Kỹ năng: `psy:crossref --all --extended --report`
> → Chạy tất cả các cặp, tất cả 10 chiều. Tìm: (1) Nhân vật A bây giờ tuyên bố phức tạp người cứu rỗi mạnh mẽ, nhưng hồ sơ của Nhân vật C nói Nhân vật A "là người hướng dẫn rút lui". Kiểm tra sự liên kết. (2) Dòng thời gian nhất quán. → Lưu báo cáo chi tiết.

### Trường hợp sử dụng: Bộ lưu trữ qua các nhân vật

> Bạn: "Tệp tâm lý học của Nhân vật B bây giờ đề cập đến 'sự gắn bó lo lắng'. Điều này ảnh hưởng đến các tệp quan hệ của Nhân vật A và Nhân vật C không?"
> Kỹ năng: `psy:crossref --pair hoa hieu --extended` + `psy:crossref --pair hoa chien --extended`
> → Kiểm tra xem Nhân vật A/Nhân vật C có mô tả hành vi của Nhân vật B theo cách phù hợp với sự gắn bó lo lắng không. Có thể cần cập nhật.

### Trường hợp sử dụng: Hỗ trợ bằng bằng chứng

> Bạn: "Tôi đã sử dụng thuật ngữ 'complex-PTSD' trong hồ sơ của Nhân vật C. Điều đó có được hỗ trợ bởi các vật liệu không?"
> Kỹ năng: `psy:crossref --dimension 5 --character character-c`
> → Chiều 5 (Hỗ trợ bằng bằng chứng) kiểm tra: hồ sơ của Nhân vật C có tuyên bố bằng chứng vật liệu ≥T3 không? Cờ nếu không.

## 5. Cảnh báo quan trọng

- **Không phải là người sửa chữa**: Kỹ năng này báo cáo các vấn đề; bạn quyết định những gì sẽ sửa. Các khung cảm xúc khác nhau của cùng một sự kiện (Nhân vật A: "dũng cảm," Nhân vật B: "liều lĩnh") là hợp lệ — không phải là lỗi.
- **Yêu cầu các hồ sơ đầy đủ**: Nếu tệp nhân vật trống hoặc rất mỏng, crossref không thể tìm thấy đủ chi tiết để xác thực. Chạy `psy:health-check` đầu tiên để điền khoảng trống.
- **Bộ đệm chỉ giúp nếu không thay đổi**: Nếu bạn sửa lại một phần hồ sơ, bộ đệm sẽ vô hiệu hóa. `--fresh` buộc phán xét lại nếu bạn muốn xác minh.
- **Khủng hoảng/xoay chiều câu chuyện không bao giờ được lưu trong bộ đệm**: Bằng thiết kế. Nếu hồ sơ gợi ý rủi ro tự sát hoặc một sự thật được tiết lộ, kỹ năng luôn chạy lại kiểm tra đó (không có đường tắt mã thông báo).
