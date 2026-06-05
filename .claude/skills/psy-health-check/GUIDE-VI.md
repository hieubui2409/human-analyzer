# psy:health-check — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn có ba hồ sơ nhân vật spanning 25 tệp mỗi cái. Một số tệp dày đặc và phong phú; những tệp khác là các sơ thảo hoặc bị mất. Trước khi bạn chạy psy:crossref hoặc bắt đầu tạo nội dung, bạn muốn biết: Nhân vật nào có các hồ sơ vững chắc, hoàn chỉnh? Cái nào mỏng và cần công việc trước tiên?

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **25 tệp phổ quát**: Mỗi nhân vật có cùng một cấu trúc hồ sơ (INDEX.md, CURRENT-STATE.md, identity/, psychology/, relationships/, timeline/, darkness/, light/, evidence/, growth/). Thiếu thậm chí một cái là một khoảng trống.
- **Chấm điểm từng tệp**: Điểm không phải là chủ quan (viết tốt vs xấu). Chúng là cơ học: Tệp có ở đó không? Bao nhiêu dòng? Các phần H2 dự kiến có mặt không?
- **Trung bình danh mục**: Tâm lý, nhận dạng, mối quan hệ, dòng thời gian, v.v. — bạn thấy cả sức khỏe từng tệp và từng danh mục, vì vậy bạn biết những lĩnh vực nào yếu.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `psy:health-check --character hieu` — xem hồ sơ của một nhân vật trông như thế nào.

**Quét đầy đủ:** `psy:health-check --all` — xem tất cả ba. Phát hiện các khoảng trống trên toàn bộ kho.

**Ưu tiên hóa:** `psy:health-check --all --gaps-only` — chỉ hiển thị các tệp <80, để bạn biết nơi cần tập trung vào psy:wave.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Kiểm tra trước crossref

> Bạn: "Hồ sơ Nhân vật A và Nhân vật B trông xong. Sẵn sàng cho xác thực chéo chưa?"
> Kỹ năng: `psy:health-check --character hieu --character hoa`
> → Nhân vật A: 87/100, Nhân vật B: 72/100. psychology/formulation.md mỏng (35 dòng). Đề xuất: mở rộng trước khi chạy psy:crossref.

### Trường hợp sử dụng: Xác định các tệp bị mất

> Bạn: "Tôi sắp bắt đầu Wave 2 trên Nhân vật C. Tôi cần điền gì trước tiên?"
> Kỹ năng: `psy:health-check --character chien --gaps-only`
> → psychology/archetype.md bị mất (0/100). identity/media-coverage.md: 10 dòng (10/100). Bắt đầu ở đây.

### Trường hợp sử dụng: Kiểm tra cấp danh mục

> Bạn: "Nhân vật nào cần công việc nhiều nhất về mối quan hệ?"
> Kỹ năng: `psy:health-check --json | jq '.categories.relationships'`
> → Danh mục mối quan hệ của Nhân vật B: 65/100 (relationships/family.md = 80, relationships/hieu.md = 50). Tệp quan hệ Nhân vật B-Nhân vật C bị mất.

## 5. Cảnh báo quan trọng

- **Tính hoàn chỉnh ≠ chất lượng**: Một tệp có 100 dòng ghi cao hơn một tệp 40 dòng, ngay cả khi tệp ngắn được viết chặt chẽ và tốt. Sử dụng phán xét của bạn.
- **Các tệp qua các nhân vật quan trọng**: psy:health-check đếm `relationships/{other-character}.md` tệp động. Nếu tệp Nhân vật B-Nhân vật A tồn tại, nó tính vào điểm của Nhân vật B.
- **Mỏng là một cờ, không phải là một thất bại**: Một tệp 50 dòng ghi ~50/100. Điều đó không tệ; nó là "xem xét và mở rộng nếu cần". Không phải mọi tệp đều cần 200 dòng.
- **Chạy trước xác thực lớn**: Luôn chạy psy:health-check trước psy:crossref. Các hồ sơ mỏng làm cho crossref ít hữu ích hơn (ít dữ liệu để so sánh).
