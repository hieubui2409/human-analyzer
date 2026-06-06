# gro:career-forecast — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn muốn khám phá **các kịch bản nếu như** cho tương lai của nhân vật. Kỹ năng này lấy giai đoạn sự nghiệp hiện tại (theo mô hình Super's Life-Career Rainbow), mức kỹ năng hiện tại (Dreyfus), mô hình học tập (Kolb), và bối cảnh tuổi/giáo dục, sau đó dự báo 3–5 năm tới. Hãy coi đây là dự báo "nếu xu hướng tiếp tục" chứ không phải dự đoán bạn sẽ đặt cược vào — vì thế nên có nhãn [FORECAST — NOT FACTUAL] trên mọi thứ.

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thu thập dữ liệu, LLM đánh giá.** Tập lệnh Python kéo dữ liệu sự nghiệp (giai đoạn, kỹ năng, mô hình học tập) từ các tệp hồ sơ. LLM sau đó áp dụng ba lĩnh vực heuristic:

1. **Giai đoạn sự nghiệp của Super** (Growth → Exploration → Establishment → Maintenance → Disengagement): tập lệnh xác định giai đoạn hiện tại, LLM dự báo tương lai dựa trên tuổi và hướng lộ trình.
2. **Tốc độ tiến triển kỹ năng Dreyfus:** kỹ năng không nâng cấp đều; sự phát triển thành thạo chậm lại khi chuyên môn sâu hơn (Novice → Advanced Beginner nhanh; Proficient → Expert mất nhiều năm).
3. **Độ tin cậy có ý là THẤP.** Kỹ năng xuất ra cờ độ tin cậy vì sự nghiệp thực tế có những sự kiện bất ngờ, quyết định kinh doanh, may mắn. Tất cả đầu ra đều là phỏng đoán.

**Không phải sự thật bởi thiết kế.** Nhãn [FORECAST — NOT FACTUAL] xuất hiện trong mỗi phần đầu ra. Dùng cái này khi brainstorm các góc độ nội dung hoặc khám phá các cung cấp nhân vật trong viễn tưởng — không phải cho các tuyên bố sự thật.

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:career-forecast --character <name>` — xem định dạng dự báo. Chú ý các nhãn [FORECAST].

**Tiếp theo:** `gro:career-forecast --all --horizon 5` — so sánh dự báo 5 năm trên cả 3 nhân vật. Phát hiện các lộ trình phân kỳ (ví dụ, một ổn định, cái khác tăng tốc).

**Khi phát triển:** `gro:career-forecast --json` để xuất dạng máy-có-thể-đọc; đưa vào các phân tích so sánh hoặc tạo nội dung hạ lưu.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Khám phá cung cấp sự nghiệp 3 năm của nhân vật để lập kế hoạch nội dung

> **Bạn:** "gro:career-forecast --character character-a --horizon 3"
> 
> **Kỹ năng:** Thu thập giai đoạn sự nghiệp hiện tại của Nhân vật A (ví dụ, Exploration), mức Dreyfus (ví dụ, Competent trong lĩnh vực X, Advanced Beginner trong Y), phong cách học tập Kolb. LLM dự báo: nếu lộ trình hiện tại giữ nguyên, Nhân vật A có khả năng sẽ vào giai đoạn Establishment năm 2–3, với chuyên môn sâu hơn trong lĩnh vực cốt lõi nhưng tăng trưởng chậm hơn trong các lĩnh vực mới. Độ tin cậy: thấp (phụ thuộc vào thị trường việc làm, lựa chọn cá nhân, v.v.). Đánh dấu tất cả dự báo [FORECAST — NOT FACTUAL].
>
> **Sử dụng:** Bây giờ bạn thấy một cung cấp 3 năm có thể xảy ra (Exploration → Establishment chuyển tiếp). Hữu ích cho phát triển nhân vật, khai thác góc độ nội dung, hoặc xác thực một dòng thời gian tường thuật.

### Trường hợp sử dụng: So sánh dự báo sự nghiệp trên các nhân vật

> **Bạn:** "gro:career-forecast --all --json | jq '.characters | map(.stage_projection)'"
>
> **Kỹ năng:** Trả về các giai đoạn được dự báo của cả 3 nhân vật trong 3 năm. Một nhân vật có thể ổn định trong Establishment, cái khác có thể vẫn ở Exploration, cái thứ ba có thể đạt Maintenance.
>
> **Sử dụng:** Tiết lộ sự trưởng thành sự nghiệp khác nhau. Hữu ích cho nội dung dyad/triad (động lực cố vấn, so sánh ngang hàng).

## 5. Những lưu ý quan trọng

- **[FORECAST — NOT FACTUAL]:** Tất cả dự báo đều là phỏng đoán. Không bao giờ trình bày một dự báo như sự thật.
- **Độ tin cậy có ý là THẤP.** Dự báo sự nghiệp không đáng tin cậy vì cuộc sống xảy ra (sa thải, chuyển hướng, sự kiện sức khỏe, may mắn). Dùng cái này để khám phá, không phải dự đoán.
- **Tốc độ tiến triển Dreyfus là heuristic.** LLM ước tính nhanh kỹ năng sẽ phát triển bao nhiêu; đây là suy đoán có giáo dục, không phải được hiệu chỉnh khoa học.
- **Không dự báo lĩnh vực PSY.** Kỹ năng này dự báo giai đoạn sự nghiệp và mức kỹ năng chỉ. Nó KHÔNG dự báo thay đổi tâm lý, tiến hóa cơ chế phòng vệ, phục hồi chấn thương, hoặc sự thay đổi gắn kết — những cái đó thuộc lĩnh vực PSY (ví dụ, `psy:hypothesis` nếu bạn muốn dự đoán hành vi).
- **Biên giới (Rule 15):** GRO→PSY là một chiều. Dự báo có thể tham chiếu những hiểu biết PSY (ví dụ, "dựa trên hồ sơ khả năng phục hồi từ PSY") nhưng không bao giờ tạo dự báo PSY chính nó.
