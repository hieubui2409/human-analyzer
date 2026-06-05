# orc:cascade — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Khi bạn thay đổi hồ sơ hoặc nạp vào tài liệu mới, nhiều miền cần phản ứng. Tài liệu được tích hợp (MAT) → hồ sơ được làm mới (PSY) → nội dung được hiệu chỉnh (CRE) → giọng được kiểm toán. Đó là một chuỗi tầng. Nếu không có khả năng hiển thị, bạn không biết công việc tầng dưới nào đã được kích hoạt. Cascade lập bản đồ chuỗi đầy đủ cho bạn.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Các sự kiện kích hoạt các kỹ năng tầng dưới.** Mỗi miền (MAT, PSY, CRE, GRO) phát hành các sự kiện khi công việc hoàn thành. Các sự kiện đó kích hoạt các kỹ năng tầng dưới trong các miền khác. Cascade theo dõi chuỗi kích hoạt đó.

**Chuỗi có thể sâu.** Tài liệu được tích hợp → PSY.refresh → CRE.recalibrate → privacy-guard. Đó là 3 bước nhảy. Cascade hiển thị tất cả chúng.

**Tham chiếu vòng tròn là có thể.** Nếu PSY.refresh kích hoạt GRO.assessed, điều này kích hoạt PSY.refresh lại, bạn có một vòng lặp. Cascade phát hiện nó và dừng lại.

**Độ sâu tối đa ngăn chặn runaway.** Theo mặc định, cascade dừng ở độ sâu 5. Bạn có thể nâng nó lên, nhưng chuỗi sâu thường là dấu hiệu định tuyến sai cấu hình.

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:cascade --trigger MAT.integrated` — xem điều gì xảy ra sau khi nạp tài liệu.

**Khám phá các kích hoạt khác:** Hãy thử `PSY.refresh`, `CRE.recalibrate`, `GRO.assessed` để hiểu định tuyến.

**Kiểm tra vòng lặp:** `orc:cascade --trigger PSY.refresh --max-depth 10` — nếu nó dừng trước 10, không có vòng lặp.

**Chế độ JSON:** `orc:cascade --trigger MAT.integrated --json` — đầu ra có cấu trúc để phân tích.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Hiểu chuỗi tầng sau khi nạp tài liệu

> Bạn: "I just ingested a new transcript. What cascades from that?"
>
> Kỹ năng: Chạy `orc:cascade --trigger MAT.integrated`, xuất ra:
> - Độ sâu 0: MAT.integrated
> - Độ sâu 1: PSY.refresh (psy:crossref, psy:ref-audit)
> - Độ sâu 2: CRE.recalibrate (cre:voice-audit)
> - Độ sâu 3: (không)
>
> Bạn thấy: PSY phải làm mới, sau đó CRE phải kiểm toán giọng. Lập kế hoạch cho phù hợp.

### Trường hợp sử dụng: Kiểm tra các chuỗi tầng tròn

> Bạn: "Does changing PSY profiles cause infinite loops?"
>
> Kỹ năng: Chạy `orc:cascade --trigger PSY.refresh --max-depth 10`, xuất ra chuỗi mà không hit giới hạn. Bạn xác nhận: không vòng lặp, an toàn để thực hiện thay đổi.

### Trường hợp sử dụng: Lập kế hoạch tác động trước thay đổi rủi ro cao

> Bạn: "If I update the growth domain, what domains react?"
>
> Kỹ năng: Chạy `orc:cascade --trigger GRO.assessed`, hiển thị các kỹ năng PSY, CRE nào được kích hoạt tầng dưới. Bạn tính đến điều đó trong lập kế hoạch của bạn.

## 5. Những cảnh báo quan trọng

- **Cascade là lập kế hoạch, không phải thực hiện.** Nó lập bản đồ chuỗi nhưng không chạy bất cứ điều gì.
- **Định tuyến là xác định.** Chuỗi tầng được mã hóa cứng trong EVENT_ROUTING; nó không thay đổi dựa trên nội dung.
- **Độ sâu tối đa là van an toàn.** Nếu bạn hit độ sâu 5, có một vòng lặp hoặc chuỗi tầng sâu. Kiểm tra config định tuyến.
- **Tên sự kiện quan trọng.** `MAT.integrated` chuỗi tầng khác với `MAT.archived`. Sử dụng tên sự kiện chính xác.
