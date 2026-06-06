# cre:exploring — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn có một ý tưởng mơ hồ: "Tôi muốn viết điều gì đó về sự hướng dẫn của Nhân vật A." Kỹ năng này hỏi bạn 7 câu hỏi tập trung — mỗi lượt một — khóa mỗi quyết định bạn cần *trước khi* bắt đầu viết. Ở cuối cùng, bạn có CONTEXT.md cho `cre:post-writer` biết chính xác ai, cái gì, ở đâu, như thế nào, và tại sao. Không có bất ngờ nào giữa bản nháp.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Khóa quyết định tuần tự:**

Mỗi câu hỏi xây dựng trên câu hỏi trước đó. Bạn không thể chọn "giọng điệu" trước khi chọn "nền tảng" (giọng TikTok ≠ giọng LinkedIn). Kỹ năng hướng dẫn bạn thông qua chuỗi phụ thuộc:

1. **Nhân vật** (ai?)
2. **Loại nội dung** (bài đăng / bài viết / cập nhật hồ sơ / cung cấp?)
3. **Góc nhìn** (gợi ý từ dữ liệu hồ sơ phù hợp với lựa chọn nhân vật của bạn)
4. **Nền tảng** (LinkedIn / TikTok / Blog vv — thông báo cho lựa chọn giọng điệu)
5. **Giọng điệu** (thô / suy ngẫm / phân tích / truyền cảm hứng — nhận thức về nền tảng)
6. **Khung lâm sàn** (nếu nội dung tâm lý, nền tảng trong lý thuyết?)
7. **Ràng buộc** (tên thật để tránh, chủ đề nhạy cảm, nhu cầu độ chính xác dòng thời gian)

**Đầu ra:** CONTEXT.md với tất cả các quyết định bị khóa. Cung cấp `cre:post-writer --from-context` (bỏ qua tương tác, đi thẳng tới viết).

## 3. Đường học tập

**Lần chạy đầu tiên:**
```bash
/cre:exploring Hành trình hướng dẫn của tôi với Nhân vật C
```
Bắt đầu với một chủ đề. Kỹ năng hỏi Q1 (nhân vật) — trả lời Nhân vật A. Q2 (loại) — trả lời "bài đăng LinkedIn". Q3 (góc nhìn) — chọn từ gợi ý dẫn xuất hồ sơ. Và cứ thế tiếp tục. Ở cuối cùng, bạn có CONTEXT.md.

**Khi bạn phát triển:** Hãy thử `--resume` để chọn từ khám phá cuối cùng của bạn (cùng một tệp). Nếu bạn muốn trả lời lại Q3 nhưng giữ Q1-Q2, kỹ năng giữ lại các câu trả lời trước đó của bạn và hỏi "Q3 lại?"

**Luồng tiêu chuẩn:** Khám phá → khóa quyết định → `cre:post-writer --from-context` → viết ngay lập tức.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Nội dung từ đầu

> **Bạn:** `/cre:exploring`
>
> **Kỹ năng:** Q1: Nhân vật nào? → Bạn: Nhân vật B. Q2: Loại nội dung? → Bạn: Bài đăng Facebook. Q3: Góc nhìn? (gợi ý 3 từ hồ sơ). → Bạn: "Sức chịu đựng của Nhân vật B trong khó khăn". Q4-Q7: nền tảng → giọng điệu → lâm sàn → ràng buộc.
>
> **Kỹ năng:** Viết CONTEXT.md, xác nhận quyết định, sẵn sàng cho `cre:post-writer --from-context`.

### Trường hợp sử dụng: Tinh chỉnh một góc nhìn được phát hiện

> **Bạn:** `cre:angle-discovery --character character-a --top 1` trả lại một góc nhìn.
>
> **Kỹ năng:** `cre:exploring --from-context` (giả thuyết nếu góc nhìn được xuất ra dưới dạng CONTEXT). Hoặc sao chép tiêu đề góc nhìn → `/cre:exploring {tiêu đề góc nhìn}`.
>
> **Kỹ năng:** Hỏi Q2+ (Q1 suy luận). Bạn tinh chỉnh nền tảng, giọng điệu, khung lâm sàn. CONTEXT.md được cập nhật.

### Trường hợp sử dụng: Khôi phục khám phá bị gián đoạn

> **Bạn:** Đã bắt đầu khám phá, trả lời Q1-Q3, chưa hoàn thành.
>
> **Kỹ năng:** `/cre:exploring --resume` → đọc CONTEXT.md cuối cùng → "Bạn đã trả lời Q1-Q3. Q4?" (tiếp tục từ nơi bạn dừng lại).

## 5. Những cảnh báo quan trọng

- **Một câu hỏi mỗi lượt:** Đừng trả lời cùng một lúc. Kỹ năng chờ câu trả lời của bạn trước khi tiếp tục.
- **Quyết định bị khóa:** Khi bạn trả lời Q5 (giọng điệu), bạn không thể quay lại Q2 mà không `--reset`. `--resume` tiếp tục từ nơi bạn dừng lại.
- **Góc nhìn dẫn xuất hồ sơ:** Các gợi ý Q3 đến từ dữ liệu hồ sơ thực tế (các sự kiện dòng thời gian, cạnh tăng trưởng, mối quan hệ). Không ngẫu nhiên.
- **Không viết nội dung:** Kỹ năng này xuất ra CONTEXT.md. Nội dung thực tế được viết bởi `cre:post-writer`.
- **Ràng buộc là tùy chọn:** Nếu Q7 (ràng buộc) bạn trả lời "không", điều đó OK. Nhưng hãy suy nghĩ về tên thật, chủ đề nhạy cảm.

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:post-writer --from-context` — tiêu thụ CONTEXT.md
- `cre:prompt-leverage` — tăng cường bối cảnh trước khi viết
- `cre:angle-discovery` — khai thác góc nhìn tự động (cung cấp khám phá)
- Quy tắc 03 (quy trình nội dung), Quy tắc 09 (bảo mật)
