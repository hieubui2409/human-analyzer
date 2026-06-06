# psy:ref-audit — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã viết: "Nhân vật A cho thấy các mẫu parentification" và "Nhân vật C thể hiện sự gắn bó lo lắng." Những thuật ngữ lâm sàn đó có được hỗ trợ đúng bởi các tệp tham khảo không? Có phải `docs/references/parentification.md` tồn tại không? Có `docs/references/anxious-attachment.md`? Kỹ năng này quét các hồ sơ để tìm các thuật ngữ lâm sàn (kịch bản tập hợp các ứng viên), sau đó phán xét xem từng thuật ngữ có chính xác, được tham chiếu, bị sử dụng sai hay ngầm hiểu. Nó cũng tìm ra điều ngược lại: các khái niệm tâm lý được đề cập trong mô tả hồ sơ mà không có tên chính thức — ví dụ: "Nhân vật A luôn cố gắng cứu mọi người" ngầm mô tả phức tạp người cứu rỗi. Và nó kiểm tra thư viện tài liệu tham khảo chính nó: tất cả các lý thuyết được đề cập có thực sự được ghi lại không?

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Kịch bản tập hợp, LLM phán xét**: Kịch bản tìm thấy các ứng viên thuật ngữ trong các hồ sơ (regex + tìm kiếm từ khóa). LLM đọc bối cảnh và quyết định: từ này có được sử dụng lâm sàn hay thường ngày không? Nó có chính xác không? Một tài liệu tham khảo hỗ trợ nó không?
- **Năm tầng phân loại**: CHÍNH XÁC (thuật ngữ đúng + tài liệu tham khảo tồn tại), KHÔNG ĐƯỢC THAM CHIẾU (thuật ngữ đúng, không có tài liệu tham khảo), BỊ ÁP DỤNG SAI (thuật ngữ bối cảnh sai), KHÔNG CHÍNH THỨC (thường ngày, OK), NGẦM (mô tả khái niệm mà không có tên chính thức).
- **Hai chiều**: Profile→ref (các khái niệm trong hồ sơ có hỗ trợ không?), Ref→profile (các lý thuyết trong thư viện tài liệu tham khảo áp dụng cho nhân vật nào?), Ref→ref (tất cả các lý thuyết được đề cập có được ghi lại không?).

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `psy:ref-audit --character character-a` — xem Nhân vật A hồ sơ sử dụng những thuật ngữ nào.

**Kiểm tra đầy đủ:** `psy:ref-audit --all` — tất cả các nhân vật, tất cả các hướng.

**Khám phá điểm mù:** `psy:ref-audit --discover` — tìm các lý thuyết bị mất ở mọi nơi.

**Liên kết ref chéo:** `psy:ref-audit --cross-ref` — chỉ kiểm tra các liên kết nội bộ thư viện tài liệu tham khảo.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra sau cập nhật hồ sơ

> Bạn: "Tôi vừa cập nhật psychology/formulation.md cho Nhân vật C. Các thuật ngữ lâm sàn có được hỗ trợ đúng không?"
> Kỹ năng: `psy:ref-audit --character character-c`
> → Tìm: "complex-PTSD" (CHÍNH XÁC, tài liệu tham khảo tồn tại), "repetition compulsion" (NGẦM — hồ sơ mô tả nó nhưng không đặt tên, tài liệu tham khảo tồn tại), "learned helplessness" (KHÔNG ĐƯỢC THAM CHIẾU — thuật ngữ sử dụng, không có tệp tài liệu tham khảo). Khuyến nghị: liên kết lặp lại-bức xúc một cách rõ ràng, tạo tài liệu tham khảo từ nhân văn học hay rephrase.

### Trường hợp sử dụng: Sức khỏe thư viện định kỳ

> Bạn: "Những khái niệm tâm lý nào đang nổi dậy trong các hồ sơ của chúng ta nhưng không nằm trong thư viện tài liệu tham khảo?"
> Kỹ năng: `psy:ref-audit --discover`
> → Tìm các khái niệm ngầm: "identity fusion" (mô tả trong hồ sơ của Nhân vật C, không có tài liệu tham khảo), "benevolence fatigue" (trong hồ sơ của Nhân vật A, không có tài liệu tham khảo). Khuyến nghị: tạo tài liệu tham khảo hoặc thêm vào các tệp lý thuyết hiện có.

### Trường hợp sử dụng: Kiểm tra thư viện tài liệu tham khảo

> Bạn: "Các tài liệu tham khảo của chúng ta đề cập đến 'co-dependency' rất nhiều. Có phải co-dependency.md tệp không?"
> Kỹ năng: `psy:ref-audit --cross-ref`
> → Ref→ref scan: "co-dependency" được đề cập trong savior-complex.md (3x), parentification.md (2x), nhưng không có tệp co-dependency.md. Khuyến nghị: tạo tài liệu tham khảo hoặc hợp nhất thành hiện có.

## 5. Cảnh báo quan trọng

- **Phát hiện ngầm là heuristic**: Kỹ năng có thể cờ "Nhân vật A luôn cứu mọi người" như ngầm mô tả phức tạp người cứu rỗi, nhưng dương tính giả xảy ra. LLM đọc bối cảnh; con người xác nhận.
- **Thông tục vs lâm sàn là một cuộc gọi phán xét**: "Gắn bó với thành phố quê hương" là bình thường; "mẫu gắn bó lo lắng" là lâm sàn. LLM thực hiện cuộc gọi, nhưng bạn có thể ghi đè.
- **Không phải là bộ kiểm tra tính chính xác lâm sàn**: Kỹ năng này kiểm tra sử dụng tài liệu tham khảo, không phải liệu chẩn đoán có đúng không. Nếu một hồ sơ tuyên bố ai đó có "ADHD" nhưng tài liệu tham khảo nói điều gì khác, psy:ref-audit cờ nó là BỊ ÁP DỤNG SAI, nhưng bản sửa yêu cầu sự phán xét của chuyên gia.
- **Chế độ sâu thêm quét hành vi**: `--deep` tìm các lý thuyết được mô tả như các mẫu hành vi (ví dụ: "luôn nhường nhịn cho người khác" → chỉ báo gắn bó lo lắng). Thêm độ phức tạp; sử dụng khi bạn nghi ngờ các khái niệm ngầm.
