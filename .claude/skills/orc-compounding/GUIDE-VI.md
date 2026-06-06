# orc:compounding — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Mỗi phiên dạy bạn điều gì đó. Những cơ chế phòng vệ nào kích hoạt dưới áp lực? Những móc viết nào hoạt động tốt nhất trên LinkedIn? Cách tiếp cận mentoring nào hoạt động cho nhân vật nào? Nếu không ghi lại những kiến thức đó, bạn lặp lại cùng một phương pháp thử-sai mỗi phiên. Compounding khóa những gì bạn đã học, vì vậy các phiên trong tương lai được thừa kế kiến thức đó.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Danh mục học tập:** Tâm lý (kiến thức nhân vật), Viết (những móc nào hoạt động), Khán giả (mẫu engagement), Lâm sàng (ứng dụng lý thuyết), Tăng trưởng (tiến hoá năng lực), Quy trình (hiệu quả quy trình).

**Từ ghi chú rải rác đến bộ nhớ bền vững:** Diffs git hiển thị những gì đã thay đổi. Trạng thái phiên hiển thị những gì được chạm tới. Compounding trích xuất kiến thức từ những tín hiệu đó và ghi nó vào bộ nhớ dự án và kho bản năng.

**Gia tăng theo thời gian:** Nếu bạn quan sát cùng một mẫu hai lần, compounding gia tăng nó, nâng cao độ tin cậy. Cuối cùng, các mẫu được thăng cấp lên bộ nhớ tác nhân (để các tác nhân miền sử dụng).

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:compounding --session` — sau hoàn thành công việc, trích xuất kiến thức một cách tương tác. Chọn cái nào để lưu.

**Chế độ tự động:** `orc:compounding --auto` — trích xuất tất cả ứng cử viên, ghi tự động. Sử dụng khi bạn tự tin vào quá trình trích xuất.

**Tiêu điểm nhân vật:** `orc:compounding --character character-a` — trích xuất kiến thức về một nhân vật chỉ.

**Các mẫu nội dung:** `orc:compounding --content` — tập trung vào các mẫu viết/engagement từ các bài đăng gần đây.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Trích xuất kiến thức tâm lý sau cập nhật hồ sơ

> Bạn: "I just updated Nhân vật B's formulation. Extract learnings about her."
>
> Kỹ năng: Đọc formulation.md, defense-mechanisms.md, relationships/family.md. Tìm thấy: "Nhân vật B's avoidance intensifies under academic pressure" (tâm lý). Đề xuất lưu vào bộ nhớ. Bạn xác nhận. Bộ nhớ được cập nhật cho phiên tiếp theo.

### Trường hợp sử dụng: Ghi lại các mẫu viết sau tạo nội dung

> Bạn: "I wrote three LinkedIn posts this session. What patterns worked?"
>
> Kỹ năng: Đọc bài đăng, so sánh với writing-voice.md. Trích xuất: "Vulnerability hook + resolution structure gets engagement" (mẫu viết). Cũng ghi chú: "Nhân vật A voice best when personal + actionable" (mẫu khán giả). Bạn xem xét và lưu.

### Trường hợp sử dụng: Tự động trích xuất khi kết thúc phiên

> Bạn: "Session wrap-up. Compound everything automatically."
>
> Kỹ năng: Chạy --auto, trích xuất tất cả learnings ứng cử viên từ diffs git + trạng thái phiên, ghi vào bộ nhớ mà không hỏi. Tóm tắt được in hiển thị những gì được ghi lại.

## 5. Những cảnh báo quan trọng

- **Trích xuất là heuristic.** Compounding gợi ý kiến thức dựa trên những gì đã thay đổi, nhưng nó không thể phán xét tầm quan trọng. Xem xét gợi ý trước khi lưu.
- **Bộ nhớ là tích cực.** Nếu bạn trích xuất cùng một mẫu hai lần, nó được gia tăng (độ tin cậy tăng). Nhưng mâu thuẫn không được tự động giải quyết; cần xem xét thủ công.
- **Bản năng phân rã theo thời gian.** Các bản năng độ tin cậy cao vẫn mạnh mẽ, các bản năng độ tin cậy thấp phân rã. `orc:dream` xử lý vòng đời.
- **Ngữ cảnh quan trọng.** Một mẫu hoạt động một lần có thể không hoạt động lại nếu ngữ cảnh thay đổi. Learnings là những quan sát, không phải luật.
