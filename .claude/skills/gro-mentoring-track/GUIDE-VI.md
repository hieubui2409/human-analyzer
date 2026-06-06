# gro:mentoring-track — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn muốn hiểu **nhân vật được hỗ trợ như thế nào trong sự phát triển của họ.** Cố vấn của họ là ai? Cố vấn cung cấp điều gì? Có những lỗ hổng (ví dụ, tài trợ sự nghiệp nhưng không có mô hình vai trò) không? Kỹ năng này phân tích các mối quan hệ cố vấn bằng cách sử dụng **khung Mạng lưới Phát triển của Kram**, phân biệt hai loại hỗ trợ: **Chức năng sự nghiệp** (tài trợ, huấn luyện, tiếp xúc) và **Chức năng tâm lý xã hội** (tình bạn, chấp nhận, mô hình vai trò). Hữu ích để hiểu khả năng phục hồi, hệ thống hỗ trợ, rủi ro cô lập, hoặc các góc độ nội dung cố vấn.

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thu thập dữ liệu, LLM đánh giá.** Tập lệnh Python chiết xuất dữ liệu cố vấn (tên cố vấn, mối quan hệ, tần suất, vai trò, chức năng được cung cấp). LLM sau đó đánh giá:

1. **Chức năng sự nghiệp:** Nhân vật này có một nhà tài trợ (người ủng hộ ở các vị trí cao cấp) không? Một huấn luyện viên (xây dựng kỹ năng)? Tiếp xúc (cơ hội)?
2. **Chức năng tâm lý xã hội:** Họ có sự chấp nhận (hỗ trợ vô điều kiện) không? Một mô hình vai trò (con số truyền cảm hứng)? Tình bạn (hỗ trợ ngang hàng)?
3. **Đa dạng mạng lưới:** Cố vấn có từ các nền tảng, ngành công nghiệp, nhân khẩu học khác nhau không? Hoặc tất cả đều tương tự?
4. **Rủi ro phụ thuộc:** Có phụ thuộc quá mức vào một cố vấn không? Cô lập nếu cố vấn đó rời đi?

**Hiểu biết của Kram:** Các chuyên gia phát triển tốt thường cần cố vấn từ các nguồn đa dạng, không phải một cố vấn hữu dụng cho tất cả.

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:mentoring-track --character <name>` — xem các mối quan hệ cố vấn và đánh giá chức năng Kram. Chú ý chức năng nào mạnh/yếu.

**Tiếp theo:** `gro:mentoring-track --all` — so sánh mạng lưới cố vấn trên cả 3 nhân vật. Ai có sự hỗ trợ mạnh nhất? Cô lập nhất?

**Sâu hơn:** Tham chiếu chéo với `gro:career-path` — lộ trình sự nghiệp có phù hợp với hỗ trợ cố vấn không? (ví dụ, ai đó ở giai đoạn Establishment nên có cố vấn đa dạng; ai đó ở Exploration có thể dựa vào một huấn luyện viên).

**Khi phát triển:** Kết hợp với `gro:compare --dimension mentoring` để thấy các kết nối cố vấn chéo (ví dụ, "Nhân vật A cố vấn Nhân vật B trong các kỹ năng kỹ thuật; Nhân vật B cố vấn Nhân vật A trong giao tiếp").

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Đánh giá hỗ trợ cố vấn để thăng chức sự nghiệp

> **Bạn:** "gro:mentoring-track --character character-a"
>
> **Kỹ năng:** Chiết xuất các mối quan hệ cố vấn của Nhân vật A. Tìm thấy: Cố vấn chính cung cấp huấn luyện (xây dựng kỹ năng) và tình bạn (hỗ trợ cảm xúc). Cố vấn thứ cấp ở vị trí cao cấp (tiềm năng tài trợ). Không có mô hình vai trò hoặc những người hỗ trợ ngang hàng (lỗ hổng).
>
> **Sử dụng:** Nhân vật A có huấn luyện tốt nhưng thiếu mô hình vai trò rõ ràng và mạng lưới ngang hàng. Tiến bộ sự nghiệp có thể dừng lại nếu không có tiếp xúc và ủng hộ. Hữu ích cho storytelling (lỗ hổng cố vấn như chướng ngại) hoặc góc độ tăng trưởng (xây dựng sự hỗ trợ ngang hàng).

### Trường hợp sử dụng: Phát hiện các kết nối cố vấn để nội dung dyad

> **Bạn:** "gro:mentoring-track --all"
>
> **Kỹ năng:** Tìm thấy Nhân vật A cố vấn Nhân vật B (huấn luyện), Nhân vật B cố vấn Nhân vật C (chấp nhận/tình bạn), Nhân vật C tư vấn Nhân vật A (tài trợ). Tạo thành một tam giác.
>
> **Sử dụng:** Họ tạo thành một hệ sinh thái cố vấn nơi mỗi người cung cấp các chức năng khác nhau cho những người khác. Hữu ích cho động lực nhóm, tường thuật hỗ trợ lẫn nhau, hoặc nội dung khả năng phục hồi hệ thống.

## 5. Những lưu ý quan trọng

- **Khung Kram là heuristic.** LLM suy ra các chức năng mà mỗi cố vấn cung cấp; đây là diễn giải có giáo dục, không phải dữ liệu được xác thực.
- **Đa dạng mạng lưới là tự báo cáo.** Đánh giá dựa vào dữ liệu mentoring-map; nếu dữ liệu thưa thớt hoặc mơ hồ, điểm đa dạng không đáng tin cậy.
- **Không độ sâu tâm lý xã hội.** Kỹ năng này đánh giá liệu hỗ trợ tâm lý xã hội có tồn tại (mô hình vai trò, tình bạn), không phải chất lượng hoặc tính xác thực. Để tâm lý mối quan hệ, dùng lĩnh vực PSY.
- **Cố vấn là động.** Đầu ra phản ánh mentoring-map hiện tại; các mối quan hệ cố vấn thực tế phát triển. Dữ liệu cũ = phân tích cũ.
- **Biên giới (Rule 15):** Kỹ năng này đọc bối cảnh gia đình từ identity/core.md nhưng không thực hiện đánh giá gắn kết hoặc chấn thương — những cái đó là lĩnh vực PSY.
