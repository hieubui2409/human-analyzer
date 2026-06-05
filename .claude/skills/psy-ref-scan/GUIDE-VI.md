# psy:ref-scan — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn tạo một tệp tài liệu tham khảo mới về "lặp lại bức xúc" (lặp lại các mẫu chấn thương vô thức). Bây giờ bạn muốn biết: Các hồ sơ nhân vật của chúng tôi có đã mô tả mẫu này chưa? Nếu vậy, cái nào sẽ trích dẫn lý thuyết này? Kỹ năng này đọc tệp repetition-compulsion.md, trích xuất các khái niệm ("lặp lại chấn thương trong quá khứ," "tái diễn xuất vô thức"), sau đó quét tất cả các hồ sơ để tìm các mẫu đó. Đầu ra: "Nhân vật A ★★★ (được đề cập trực tiếp), Nhân vật C ★★ (khớp hành vi), Nhân vật B ★ (khớp tiềm năng)." Bạn có thể quyết định nơi thêm trích dẫn rõ ràng.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Ngược của psy:ref-audit**: Kiểm tra audit profile→ref ("Thuật ngữ này có được tham chiếu không?"). Quét ref→profile ("Lý thuyết này áp dụng ở đâu?").
- **Xếp hạng ba sao**: ★★★ = lý thuyết được đề cập rõ ràng trong hồ sơ. ★★ = mẫu hành vi phù hợp với các chỉ báo lý thuyết. ★ = khớp tiềm năng, cần phán xét.
- **Cơ hội làm giàu**: Nếu Nhân vật C cho thấy ★★ khớp để lặp lại-bức xúc nhưng hồ sơ không trích dẫn nó, đó là cơ hội làm giàu: thêm trích dẫn + giải thích mẫu.

## 3. Đường dẫn học tập

**Bản đồ đầy đủ:** `psy:ref-scan --map` — xem tất cả 60+ lý thuyết ánh xạ tới tất cả 3 nhân vật.

**Một lý thuyết:** `psy:ref-scan --theory "attachment theory"` — quét sâu cho một lý thuyết.

**Lý thuyết mới:** `psy:ref-scan --new` — lý thuyết quét được thêm trong commit cuối cùng.

**Lý thuyết không được sử dụng:** `psy:ref-scan --gaps` — những lý thuyết nào có kết nối hồ sơ bằng không?

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Ứng dụng tài liệu tham khảo mới

> Bạn: "Vừa tạo parentification.md ref. Nó áp dụng ở đâu?"
> Kỹ năng: `psy:ref-scan --theory parentification`
> → Nhân vật A ★★★ (trực tiếp: "đảm nhận vai trò của cha mẹ"), Nhân vật C ★★ (hành vi: chăm sóc các em trai, gánh nặng cảm xúc), Nhân vật B ★ (tiềm năng: trách nhiệm gia đình được đề cập). Đề xuất làm giàu: thêm trích dẫn parentification vào psychology/formulation.md của Nhân vật C.

### Trường hợp sử dụng: Ánh xạ đầy đủ

> Bạn: "Tôi cần hiểu những lý thuyết nào hỗ trợ những nhân vật nào."
> Kỹ năng: `psy:ref-scan --map`
> → Bảng: 60+ lý thuyết × 3 nhân vật. Hiển thị phạm vi bao phủ. Ví dụ phát hiện: "Lý thuyết gắn bó: Nhân vật A ★★★, Nhân vật B ★★★, Nhân vật C ★★" (cả 3 được bao phủ), so với "Tồn tại-Void: Nhân vật C ★★★ chỉ" (ngách).

### Trường hợp sử dụng: Lý thuyết được thêm gần đây

> Bạn: "Tuần trước chúng tôi thêm 3 tài liệu tham khảo mới. Chúng nên được áp dụng ở đâu?"
> Kỹ năng: `psy:ref-scan --new`
> → Quét tài liệu tham khảo được commit trong 7 ngày qua. Cho mỗi cái: hiển thị trận đấu nhân vật. Đề xuất cập nhật hồ sơ.

### Trường hợp sử dụng: Lý thuyết không được sử dụng

> Bạn: "Có lý thuyết nào trong thư viện của chúng tôi không áp dụng cho bất kỳ nhân vật nào không?"
> Kỹ năng: `psy:ref-scan --gaps`
> → Lý thuyết không có kết nối: cognitive-dissonance.md, existential-void.md (chỉ Nhân vật C ở ★ cấp). Đánh giá: lưu trữ hoặc giữ để sử dụng trong tương lai?

## 5. Cảnh báo quan trọng

- **Xếp hạng sao là heuristic**: ★★★ (đề cập trực tiếp) là khách quan. ★★ và ★ liên quan đến kết hợp mẫu, có thể có dương tính giả/âm tính giả. Luôn xem xét.
- **Khớp hành vi là bối cảnh**: Một lý thuyết có thể mô tả hành vi xuất hiện trong hồ sơ nhưng trong bối cảnh khác nhất kỳ vọng. Xem xét thủ công là cần thiết.
- **Quét tài liệu tham khảo gần đây phụ thuộc vào git**: `--new` xem xét các commit gần đây. Các tệp mới chưa theo dõi có thể không được quét. Commit đầu tiên, sau đó quét.
- **Làm giàu là tùy chọn**: Chỉ vì một lý thuyết phù hợp với một nhân vật không có nghĩa là hồ sơ PHẢI trích dẫn nó. Kỹ năng cờ cơ hội; bạn quyết định.
- **Ngược của psy:ref-audit**: Nếu psy:ref-audit nói "Thuật ngữ lâm sàn không được tham chiếu," psy:ref-scan nói "Tài liệu tham khảo này áp dụng ở đây." Chúng bổ sung nhau — sử dụng cả hai.
