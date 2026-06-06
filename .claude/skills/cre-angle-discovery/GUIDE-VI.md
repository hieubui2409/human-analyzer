# cre:angle-discovery — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Hãy tưởng tượng bạn thức dậy và hỏi: "Điều gì thú vị về Nhân vật A mà chúng ta nên chia sẻ tuần này?" Kỹ năng này thức dậy tự động (hoặc theo yêu cầu), đọc mọi khuôn khổ — những tín hiệu tăng trưởng gần đây của anh ấy, tài liệu mới, mốc quan trọng sự nghiệp, những gì đã được chia sẻ trước đó, mọi người phản ứng như thế nào, những thay đổi trong mối quan hệ của anh ấy — và đưa ra 5 góc nhìn hàng đầu có bằng chứng xếp hạng **mà bạn không cần phải gõ một chữ nào**. Bạn chỉ cần chọn một cái mà bạn thích và viết.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Quy trình ba lớp:**

1. **Thu thập (xác định):** Các kịch bản trích xuất các tín hiệu thô từ mỗi khuôn khổ — các thay đổi Big Five, cạnh tăng trưởng PSY, mốc quan trọng GRO, tài liệu MAT gần đây, tương tác CRE, các sự kiện ORC. Các kịch bản thu thập quá rộng; dự kiến có những dương tính giả.
2. **Tổng hợp (kinh nghiệm):** LLM đọc các tín hiệu thô và viết các góc nhìn ứng viên — tiêu đề, móc, cấp độ bằng chứng, điểm phù hợp nền tảng. Loại bỏ nhiễu, giữ lại các tín hiệu thực.
3. **Xếp hạng (xác định):** Kịch bản tính điểm từng góc nhìn theo `độ tươi × độ mạnh của bằng chứng × phù hợp với nền tảng × hệ số đồng ý` và sắp xếp. Các góc nhìn BỊ CHẶN (đồng ý = từ chối) chìm xuống đáy nhưng không bao giờ biến mất (minh bạch).

**Tỷ lệ độ mạnh của bằng chứng:** T1 (chính) = 1,0, T2 (phụ) = 0,85, T3 (ba) = 0,55, T4/T5 (yếu) = 0,25/0,15. Các góc nhìn T4-T5 được gắn cờ `suy đoán` — có thể công bố nhưng bằng chứng yếu.

**Cửa sổ độ tươi mới:** Các tín hiệu cũ hơn `--since-days` (mặc định 30) thoái lui thành không và bị loại bỏ. Giữ các góc nhìn cập nhật.

## 3. Đường học tập

**Lần chạy đầu tiên:**
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-angle-discovery/scripts/aggregate-angle-signals-across-frameworks.py \
  --character character-a --framework all --since-days 30 --json
```
Đọc kết quả — bạn sẽ thấy các tín hiệu thô như "B5 tính cẩn trọng +8% kể từ tháng Giêng", "cạnh tăng trưởng: mở khóa khẳng định", "tài liệu mới: phản hồi của người hướng dẫn". Những cái này trở thành hạt giống góc nhìn.

**Khi bạn phát triển:** Hãy thử `--graph-signal` để bao gồm các ứng viên quan hệ ngữ nghĩa từ đồ thị kiến thức (chậm hơn, chỉ mang tính chất cố vấn — đừng quá phụ thuộc vào nó). Hãy thử `--top 3` để lựa chọn hàng ngày thay vì 5 hàng đầu.

**Luồng tiêu chuẩn:** Chạy khám phá → chọn một góc nhìn → cung cấp cho `cre:exploring --resume` để tinh chỉnh → `cre:post-writer --from-context` để viết.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Ý tưởng định kỳ (hàng ngày/hàng tuần)

> **Bạn:** "Chúng ta nên đăng bài gì về Nhân vật A tuần này?"
>
> **Kỹ năng:** Chạy tự động qua đêm; trả lại 5 góc nhìn hàng đầu được xếp hạng theo độ tươi mới. Phát hiện "tính nhất quán trong hướng dẫn của Nhân vật A (mốc GRO)" ghi được 0,82, cao hơn "tái phát lo âu (cạnh tăng trưởng PSY)" ở 0,61.
>
> **Bạn:** Chọn góc nhìn hướng dẫn, chạy `cre:post-writer --from-context`.

### Trường hợp sử dụng: Hạt giống khám phá

> **Bạn:** "Tôi muốn tinh chỉnh một góc nhìn trước khi viết."
>
> **Kỹ năng:** `--to-context` viết góc nhìn hàng đầu dưới dạng khối CONTEXT.md (định dạng `cre:exploring`).
>
> **Bạn:** Chạy `cre:exploring --resume`, tinh chỉnh qua Q2-Q7, sau đó `cre:post-writer --from-context`.

### Trường hợp sử dụng: Tạo nhiều nền tảng hàng loạt

> **Bạn:** "Tạo 5 góc nhìn, viết các bài đăng TikTok/LinkedIn/Facebook bản địa cho mỗi bài."
>
> **Kỹ năng:** `--top 5 --json` trả lại JSON góc nhìn.
>
> **Bạn:** Vòng lặp: mỗi góc nhìn, chạy `cre:multiplatform --source <angle> --platforms tiktok,linkedin,facebook`.

### Trường hợp sử dụng: Khai thác cụ thể khuôn khổ

> **Bạn:** "Điều gì tươi mới trong tài liệu tuần này?"
>
> **Kỹ năng:** `--framework mat --since-days 7 --top 3` trả lại các góc nhìn chỉ có nguồn từ vật liệu từ tuần trước.

## 5. Những cảnh báo quan trọng

- **Thu thập quá rộng theo thiết kế:** Các kịch bản gắn cờ nhiều tín hiệu yếu; LLM loại bỏ nhiễu. Dương tính giả dự kiến — đó là OK.
- **Không rò rỉ sự kiện:** Văn bản góc nhìn paraphrase thời gian sự kiện ("mùa mốc quan trọng", "kỷ niệm của X") — không bao giờ trích dẫn các tải trọng ORC nội bộ hoặc chi tiết lâm sàng thô. Các cổng hạ lưu (`cre:evidence-scanner`, `cre:privacy-guard`) thực thi Quy tắc 09.
- **Đồng ý quan trọng:** Các góc nhìn được gắn cờ `BỊ CHẶN` (quan hệ/chủ đề từ chối sự đồng ý theo Quy tắc 09) chìm xuống đáy nhưng được gửi trong kết quả — minh bạch. Đừng công bố chúng.
- **T4/T5 suy đoán:** Các góc nhìn được hỗ trợ chỉ bằng bằng chứng yếu được gắn cờ `suy đoán` — hợp lệ để công bố (chúng được xếp hạng thấp hơn), nhưng hãy tiết lộ cấp độ bằng chứng.
- **Đồ thị ngữ nghĩa tùy chọn:** `--graph-signal` thêm các ứng viên KG nhưng CHẬM và chỉ mang tính chất cố vấn; đừng dựa vào nó cho các quyết định quan trọng.

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:exploring` — tinh chỉnh tương tác
- `cre:post-writer --from-context` — viết ngay lập tức
- `psy:relation-intelligence` — nguồn góc nhìn chuyên biệt về mối quan hệ
- Quy tắc 03 (quy trình nội dung), Quy tắc 14 (sự kiện CRE + bằng chứng)
