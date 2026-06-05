# orc:observe — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Các kỹ năng khung nhận thấy những điều: "Nhân vật B uses intellectualization when conflicted," "LinkedIn posts with vulnerability hooks get 2x engagement," "Nhân vật A's competency gap in delegation." Những quan sát này đáng nhớ. Observe cho phép các kỹ năng phát hành tín hiệu được ghi lại trong một luồng quan sát. Sau đó, `orc:compounding` khai thác những tín hiệu đó thành learnings.

## 2. Khái niệm cơ bản (mô hình tinh thần)

**Hai nguồn quan sát:** Tự động (chỉnh sửa khung kích hoạt tín hiệu `*-touched`) và ngữ nghĩa (kỹ năng phán xét một cái gì đó đáng chú ý và phát hành tín hiệu). Cả hai đều cấp nguồn luồng quan sát.

**Từ vựng tín hiệu được giới hạn.** Defense-pattern, low-craap, voice-drift, competency-delta, v.v. Không tùy ý; tín hiệu phải nằm trong từ vựng được phép.

**Quan sát là thụ động.** Không giống như các sự kiện (kích hoạt tầng), quan sát tích lũy để khai thác sau. Tín hiệu không làm bất cứ điều gì chạy.

## 3. Đường dẫn học tập

**Tín hiệu tự động:** Các kỹ năng không gọi quan sát; móc khung tự động phát hành khi dữ liệu được chỉnh sửa.

**Tín hiệu ngữ nghĩa:** Ở cuối công việc kỹ năng, nếu có gì đó đáng chú ý, kỹ năng gọi quan sát để ghi lại nó.

**Tín hiệu khai thác:** `orc:compounding` đọc luồng quan sát và trích xuất learnings.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kỹ năng khung phát hành tín hiệu defense-pattern

> Kỹ năng (psy:crossref) kết thúc công việc và nhận thấy: "Nhân vật B intellectualizes under conflict." Gọi: `orc:observe --framework psy --signal defense-pattern --payload '{"character":"hoa","mechanism":"intellectualization","trigger":"conflict"}' --source psy:crossref`. Tín hiệu được ghi lại.

### Trường hợp sử dụng: Kỹ năng nội dung quan sát drift giọng

> Kỹ năng (cre:voice-audit) kết thúc và nhận thấy: "Recent posts diverge from writing-voice.md (too clinical, should be personal)." Gọi: `orc:observe --framework cre --signal voice-drift --payload '{"character":"hieu","issue":"too clinical","expected":"personal"}' --source cre:voice-audit`. Tín hiệu được ghi lại.

### Trường hợp sử dụng: Compounding khai thác quan sát thành learnings

> Sau đó, `orc:compounding --session` đọc luồng quan sát, tìm 5 tín hiệu defense-pattern, 2 tín hiệu voice-drift. Đề xuất trích xuất: "Nhân vật B intellectualizes under conflict (reinforced 5x)" như một learning đáng nhớ.

## 5. Những cảnh báo quan trọng

- **Quan sát là tùy chọn.** Các kỹ năng có thể hoạt động mà không phát hành tín hiệu; các móc tự động đảm bảo theo dõi cơ sở.
- **Tín hiệu là con trỏ, không phải bãi rác.** Giữ payload ≤2 KB; tín hiệu trỏ đến các mẫu, không phải dữ liệu toàn diện.
- **Tín hiệu ngữ nghĩa yêu cầu phán xét.** Chỉ phát hành khi genuinely đáng chú ý (không phải mọi quan sát).
- **Quan sát ≠ Hành động.** Ghi lại "Nhân vật B avoids conflict" không thay đổi hành vi; nó là một ghi chú để tham khảo trong tương lai.
