# orc:domain-router — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Khi bạn thay đổi hồ sơ hoặc nạp vào tài liệu, bạn không chỉ chỉnh sửa một tệp—bạn đang kích hoạt công việc tầng dưới trong các miền khác. Domain-router cho bạn thấy chuỗi hoàn chỉnh của những gì nên thực hiện tiếp theo, vì vậy bạn có thể lập kế hoạch tác động đầy đủ trước khi bắt đầu.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Các sự kiện định tuyến đến các kỹ năng.** Mỗi thay đổi miền (MAT, PSY, CRE, GRO) phát hành một sự kiện. Sự kiện đó kích hoạt các kỹ năng tầng dưới. Router lập bản đồ chuỗi.

**Định tuyến là xác định.** Quy tắc được mã hóa cứng: nếu MAT.integrated, thì psy:crossref chạy. Nếu PSY.refresh, thì cre:voice-audit chạy. Không ngẫu nhiên, không đoán.

**Phát hiện từ-diff.** Router có thể suy luận những miền nào đã thay đổi bằng cách xem diffs git (profile/ = PSY, assets/ = CRE, docs/growth/ = GRO, v.v.).

## 3. Đường dẫn học tập

**Lần chạy đầu tiên:** `orc:domain-router --from-diff` — xem những gì đã thay đổi và những gì nên chạy.

**Sự kiện rõ ràng:** `orc:domain-router --event MAT.integrated` — truy tìm định tuyến từ một sự kiện.

**Chế độ JSON:** `orc:domain-router --from-diff --json` — đầu ra có cấu trúc để phân tích.

**Dry-run:** `orc:domain-router --from-diff --dry-run` — lập kế hoạch mà không thực hiện.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Xem định tuyến sau các thay đổi hồ sơ

> Bạn: "I edited Nhân vật B's psychology files. What cascades from that?"
>
> Kỹ năng: Phát hiện psychology/ change → PSY.refresh event → psy:crossref, psy:ref-audit run. Sau đó chúng phát hành PSY.refresh downstream → CRE.recalibrate → cre:voice-audit runs. Bạn thấy chuỗi đầy đủ.

### Trường hợp sử dụng: Truy tìm định tuyến cho sự kiện rõ ràng

> Bạn: "If MAT.integrated fires, what should run?"
>
> Kỹ năng: Lập bản đồ EVENT_ROUTING: MAT.integrated → psy:ref-audit, psy:crossref. Bạn thấy: tích hợp tài liệu yêu cầu các kỹ năng PSY để xác thực so với hồ sơ.

## 5. Những cảnh báo quan trọng

- **Định tuyến hiển thị khuyến nghị, không phải đảm bảo.** Bạn vẫn cần thực sự chạy các kỹ năng.
- **Quy tắc được mã hóa cứng có nghĩa là không linh hoạt.** Nếu định tuyến không khớp với quy trình công việc của bạn, đó là vấn đề thiết kế hệ thống, không phải vấn đề kỹ năng.
- **From-diff là heuristic.** Nó suy luận từ đường dẫn tệp; các thay đổi mơ hồ có thể định tuyến đến miền sai.
