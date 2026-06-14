# orc:event-log — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Khi các miền kích hoạt các sự kiện (PSY.refresh, CRE.recalibrate), chúng được ghi lại. Event-log là dấu vết kiểm tra: "ai kích hoạt cái gì, khi nào?" Bạn có thể truy vấn: "tất cả các sự kiện PSY trong 3 ngày cuối cùng," "tất cả các sự kiện từ psy:crossref," "tất cả các sự kiện cho Nhân vật B." Đó là một lịch sử hoạt động miền có thể tìm kiếm được.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**7 luồng khung.** Mỗi miền (MAT, PSY, CRE, GRO, EVL, ORC, COM) có tệp JSONL riêng. Các sự kiện định tuyến theo tiền tố (PSY.* → character-events.jsonl, v.v.).

**Chỉ ghi thêm.** Một khi được ghi lại, các sự kiện không bao giờ thay đổi. Luôn có lịch sử có thể tìm kiếm.

**Truy vấn là bộ lọc.** Kết hợp loại sự kiện + nhân vật + ngày + kỹ năng để tìm hoạt động cụ thể.

## 3. Đường dẫn học tập

**Truy vấn đầu tiên:** `orc:event-log --query` — sự kiện gần đây (20 cuối cùng).

**Lọc theo sự kiện:** `orc:event-log --query --event-type PSY.refresh` — chỉ làm mới PSY.

**Lọc theo nhân vật:** `orc:event-log --query --character character-b` — tất cả sự kiện cho Nhân vật B.

**Lọc theo ngày:** `orc:event-log --query --since 2026-06-01` — sự kiện từ tháng 6 trở đi.

**Ghi thêm một sự kiện:** Các kỹ năng gọi `--append --event-type MAT.integrated --source mat:indexer --character character-a --reason "New material processed"`.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Truy vấn các sự kiện PSY gần đây

> Bạn: "What PSY work happened this week?"
>
> Kỹ năng: Truy vấn character-events.jsonl cho `event-type=PSY.refresh`, `--since=7 days ago`. Hiển thị: PSY.refresh on 2026-06-04 (psy:crossref, Nhân vật B), PSY.refresh on 2026-06-02 (psy:wave, Nhân vật A). Bạn thấy hoạt động PSY.

### Trường hợp sử dụng: Truy tìm tất cả các sự kiện cho một nhân vật

> Bạn: "Show all events for Nhân vật C."
>
> Kỹ năng: Truy vấn trên tất cả 7 luồng cho `character=character-c`. Trả lại: MAT.integrated, PSY.refresh, GRO.assessed events theo thứ tự. Bạn thấy chuỗi hoạt động đầy đủ cho nhân vật đó.

### Trường hợp sử dụng: Ghi lại một sự kiện miền

> Kỹ năng (mat:indexer) hoàn thành: `orc:event-log --append --event-type MAT.integrated --source mat:indexer --character character-a --reason "Transcript validated, integration gate passed"`. Sự kiện được ghi lại vào material-events.jsonl với dấu thời gian ISO.

## 5. Những cảnh báo quan trọng

- **Sự kiện là sự kiện, không phải cách giải thích.** Nhật ký nói "MAT.integrated," không phải "tài liệu tốt" hoặc "sẵn sàng sử dụng."
- **Nhật ký sự kiện phát triển vô hạn.** Không làm sạch tự động; lưu trữ nên định kỳ sao lưu nhật ký cũ.
- **Truy vấn phân biệt chữ hoa chữ thường.** `--event-type PSY.refresh` ≠ `PSY.REFRESH`.
- **Dấu thời gian là ISO 8601.** Sắp xếp và lọc giả định UTC.
