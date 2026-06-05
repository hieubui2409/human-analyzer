# orc:intake — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn nhận được một nhiệm vụ mới: "Write a post about Nhân vật A's mentoring journey." Nhưng những kỹ năng nào nên chạy? Theo thứ tự nào? Intake phân tích nhiệm vụ, xác định nó là "content creation", và xuất ra chuỗi kỹ năng tối ưu: bootstrap → cre:exploring → orc:classify → cre:prompt-leverage → cre:post-writer → cre:privacy-guard → cre:voice-audit → orc:compounding. Bạn không phải nhớ chuỗi.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**10 loại công việc, mỗi cái với một chuỗi kỹ năng.** Content Creation, Profile Update, Arc Development, Research, Material Ingestion, Consistency Audit, Reference Management, Maintenance, Multi-Platform, Growth Analysis. Mỗi cái có điều kiện tiên quyết, kỹ năng chính, và bước sau công việc.

**Intake phát hiện và định tuyến.** Phân tích mô tả nhiệm vụ → khớp với loại công việc → xuất ra chuỗi.

**Chế độ tự động suy luận từ git.** Nếu bạn chạy `--auto`, nó nhìn vào diffs git và tên nhánh để đoán những gì bạn đang làm.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:intake "write a LinkedIn post about Nhân vật A's mentoring"` → thấy "viết bài" → Tạo Nội dung → xuất ra chuỗi.

**Tự động phát hiện:** `orc:intake --auto` → nhìn vào các thay đổi git, suy luận loại công việc.

**Kiểm tra hiện tại:** Sau intake, bạn thấy chuỗi và quyết định những bước nào thực sự chạy.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Phân loại nhiệm vụ tạo nội dung

> Bạn: "I'm writing a LinkedIn post about Nhân vật A. What's my workflow?"
>
> Kỹ năng: Phát hiện "viết bài" + "LinkedIn" → Tạo Nội dung. Xuất ra: bootstrap → cre:exploring → orc:classify → ... → orc:compounding. Bạn bây giờ biết chuỗi.

### Trường hợp sử dụng: Tự động phân loại từ các thay đổi git

> Bạn: "What should I work on? Auto-detect from recent changes."
>
> Kỹ năng: Thấy diffs trong docs/profiles/character-b/psychology/ → Cập nhật Hồ sơ loại công việc. Xuất ra: bootstrap → orc:classify → chỉnh sửa hồ sơ → psy:ref-audit → psy:crossref → orc:compounding.

## 5. Những cảnh báo quan trọng

- **Intake gợi ý; bạn quyết định.** Chuỗi được khuyến nghị, không bắt buộc. Bỏ qua các bước nếu chúng không phù hợp với quy trình công việc của bạn.
- **Loại công việc là rời rạc.** Nếu nhiệm vụ của bạn kéo dài nhiều loại (ví dụ, "cập nhật hồ sơ VÀ viết nội dung"), intake có thể gợi ý một chuỗi. Bạn có thể cần chạy cả hai chuỗi thủ công.
- **Chế độ tự động là heuristic.** Nếu git diffs mơ hồ (thay đổi trong nhiều miền), chế độ tự động đoán. Hãy rõ ràng nếu không chắc chắn.
