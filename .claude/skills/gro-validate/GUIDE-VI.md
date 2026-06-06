# gro:validate — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này giúp bạn điều gì

Bạn đang xây dựng hoặc duy trì các tệp hồ sơ GRO và muốn **bắt các vấn đề về chất lượng dữ liệu trước khi các kỹ năng hạ lưu tiêu thụ chúng.** Tất cả 4 tệp bắt buộc có hiện diện không? Các tham chiếu chéo có kiểm tra không (ví dụ, các kỹ năng được đề cập trong career-path xuất hiện trong competencies)? Có những tệp cũ? Rò rỉ thuật ngữ PSY-domain? Kỹ năng này chạy các kiểm tra xác định và (tùy chọn) gợi ý các bản sửa chữa LLM-powered. Hữu ích để đảm bảo chất lượng trước khi xuất bản hồ sơ hoặc kích hoạt các sự kiện hạ lưu.

## 2. Các khái niệm cơ bản (mô hình tư duy)

**Kịch bản thực hiện các kiểm tra xác định; LLM phán xét heuristic.** Tập lệnh Python xác minh:

1. **Frontmatter schema:** Tất cả 4 tệp tồn tại, có các trường bắt buộc (`domain: growth`, `type: data`, `character:` slug, `last_updated`, `updated_by`), và dấu thời gian không cũ (mặc định: >90 ngày = cảnh báo).
2. **Tính nhất quán tệp chéo:** Sự hiện diện từ khóa (các kỹ năng có xuất hiện trong nhiều tệp không? các cố vấn có khớp với các tệp mối quan hệ không?).
3. **Biên giới GRO↔PSY:** Không có cơ chế phòng vệ, thuật ngữ gắn kết, ngôn ngữ chấn thương trong các tệp phát triển (chỉ PSY).
4. **Nền tảng bằng chứng:** Sự hiện diện của các nhãn trích dẫn ([Source:], [UNVERIFIED], [LIMITED DATA], [PRIVATE]).

**Các kiểm tra kỹ năng chi tiết là heuristic.** Kịch bản cờ "Python được đề cập trong career-path nhưng không ở competencies" là WARN; LLM phán xét nếu nó là một lỗ hổng thực tế hoặc có thể chấp nhận được (có thể Python là ngoại lệ).

## 3. Lộ trình học tập

**Chạy lần đầu:** `gro:validate --character <name>` — xem báo cáo xác thực. Quét các mục WARN/FAIL. Hầu hết xác thực là nhanh; các mục WARN xứng đáng xem xét.

**Tiếp theo:** `gro:validate --all --json` — đầu ra lập trình cho đường ống CI/CD hoặc xử lý hạ lưu.

**Sâu hơn:** `gro:validate --fix` — bao gồm các bản sửa chữa được gợi ý bởi LLM cho các lỗi. Xem xét các gợi ý trước khi áp dụng thủ công.

**Khi phát triển:** Chạy xác thực trước khi phát hành các sự kiện GRO.assessed (career-path) hoặc GRO.mentored (mentoring-track) — đảm bảo tiêu thụ PSY/CRE hạ lưu là đáng tin cậy.

## 4. Các trường hợp sử dụng (mỗi = một cuộc hội thoại mẫu)

### Trường hợp sử dụng: Kiểm tra chất lượng trước khi xuất bản một hồ sơ

> **Bạn:** "gro:validate --character character-a --fix"
>
> **Kỹ năng:** Chạy kiểm tra. Tìm thấy: Frontmatter OK. Tệp chéo: 2 kỹ năng trong career-path thiếu trong competencies. Bằng chứng: 3 mục nhập thiếu nhãn [Source:]. GRO↔PSY: Không có những vấn đề biên giới.
>
> **Kết quả:** WARN trên khoảng trống kỹ năng, WARN trên nền tảng bằng chứng. LLM gợi ý: (1) thêm kỹ năng thiếu vào competencies.md hoặc xóa khỏi career-path nếu ngoại lệ, (2) thêm [Source: materials/hieu/XXX.md] vào các mục nhập không có nguồn.
>
> **Sử dụng:** Bây giờ bạn biết những gì cần sửa trước khi hồ sơ được tiêu thụ bởi các kỹ năng hạ lưu.

### Trường hợp sử dụng: Xác thực hàng loạt trước khi phát hành sự kiện

> **Bạn:** "gro:validate --all --json | jq '.characters[] | select(.score < 80)'"
>
> **Kỹ năng:** Trả về các nhân vật có điểm xác thực dưới 80/100. Cờ những cái nào sẵn sàng vs cần xem xét.
>
> **Sử dụng:** Trước khi phát hành sự kiện GRO.assessed từ career-path, hãy kiểm tra rằng tất cả các nhân vật đều vượt qua xác thực. Ngăn chặn các lỗi xả xuôi hạ lưu.

## 5. Những lưu ý quan trọng

- **Các kiểm tra xác định là nghiêm ngặt; các kiểm tra heuristic là khoan dung.** Frontmatter schema phải khớp chính xác (FAIL nếu không khớp). Tham chiếu kỹ năng chéo sử dụng khớp từ khóa (WARN nếu không tìm thấy, nhưng có thể chấp nhận được).
- **Tính cũ có thể định cấu hình.** Mặc định là 90 ngày; bạn có thể đặt `--stale-days 180` để dung sai dài hơn (ví dụ, nếu hồ sơ được cập nhật hàng quý, không phải hàng tháng).
- **Các bản sửa chữa LLM chỉ là gợi ý.** Cờ `--fix` xuất các đề xuất; chúng phải được xem xét và áp dụng thủ công. Không bao giờ tự động áp dụng các bản sửa chữa trong sản xuất.
- **Các nhãn bằng chứng là thô.** Kịch bản kiểm tra sự hiện diện ([Source:] tồn tại); nó không xác thực tính chính xác hoặc chất lượng liên kết bằng chứng. Vẫn cần xem xét thủ công.
- **Biên giới (Rule 15):** Kỹ năng này thực thi biên giới GRO↔PSY bằng cách quét các thuật ngữ PSY-domain trong các tệp phát triển. Nếu bạn tìm thấy một vi phạm, hãy sửa nó ngay — nó báo hiệu một ghi chéo lĩnh vực.
