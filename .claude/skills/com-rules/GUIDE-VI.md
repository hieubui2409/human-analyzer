# com:rules — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã chỉnh sửa hồ sơ nhân vật, tạo nội dung hoặc sửa đổi tài liệu. Trước khi bạn commit, bạn muốn chắc chắn rằng tất cả đều tuân theo các quy tắc của dự án — trường frontmatter bị thiếu, liên kết bị hỏng, rò rỉ mức độ bằng chứng. com:rules chạy một kiểm tra, cho bạn biết những gì sai, và gợi ý sửa chữa. Không có bất ngờ khi xảy ra đánh giá mã.

## 2. Khái niệm cốt lõi (mô hình tư duy)

**16 quy tắc mô-đun:** Mỗi quy tắc sở hữu một mối quan tâm (cấu trúc hồ sơ, tài liệu tham khảo, tính bảo mật, mức độ bằng chứng, v.v.). Các quy tắc không trùng lặp — chúng phân vùng.

**Định tuyến thông minh:** Các quy tắc khác nhau cần các trình xác thực khác nhau. Một số được kiểm tra nội tuyến (sự hiện diện của frontmatter), những cái khác uỷ quyền cho các kỹ năng chuyên biệt (`psy:ref-audit`, `cre:privacy-guard`). com:rules điều phối.

**Phân loại tệp:** Kỹ năng xem xét đường dẫn tệp của bạn và quyết định áp dụng quy tắc nào. Chỉnh sửa `docs/profiles/*/psychology/`? Quy tắc 01, 02, 05, 08 áp dụng. Chỉnh sửa `assets/`? Quy tắc 03, 09, 14 áp dụng.

**Báo cáo, không sửa chữa:** Đây là kiểm tra chỉ đọc. Nó cờ các vấn đề và gợi ý phải làm gì; bạn thực hiện các thay đổi.

## 3. Lộ trình học tập

**Lần chạy đầu tiên:** Chỉnh sửa tệp hồ sơ, sau đó chạy `com:rules`. Xem những quy tắc nào áp dụng và những quy tắc nào báo cáo vi phạm.

**Tiếp theo:** Thử `com:rules --list` để xem tất cả 16 quy tắc và trạng thái của chúng. Cung cấp cho bạn một ảnh chụp sức khỏe của dự án.

**Khi bạn phát triển:** Sử dụng `--check 02` để xác thực tài liệu tham khảo trong cô lập; sử dụng `--scope all` để kiểm toán toàn bộ dự án; sử dụng `--scope docs/materials/` để xác thực một thư mục cụ thể.

## 4. Trường hợp sử dụng (mỗi = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Xác thực các thay đổi trước khi commit

> Bạn: "check rules"
> Kỹ năng: Quét git diff, tìm 2 tệp đã thay đổi. Chạy quy tắc 01, 02, 08 (quy tắc hồ sơ). Báo cáo: "Rule 01 ✅ | Rule 02 ⚠️ missing citation in line 45 | Rule 08 ✅". Bạn sửa dòng 45, sau đó commit.

### Trường hợp sử dụng: Liệt kê tất cả các quy tắc và trạng thái của chúng

> Bạn: "show me all the rules"
> Kỹ năng: `com:rules --list`. In tất cả 16 quy tắc với mô tả ngắn gọn và xem chúng đã vượt qua/không vượt qua trong dự án. Cung cấp cho bạn cảnh quan quy tắc.

### Trường hợp sử dụng: Kiểm tra sâu một quy tắc cụ thể

> Bạn: "validate rule 09 (confidentiality)"
> Kỹ năng: `com:rules --check 09`. Quét tất cả các tệp assets/ để tìm các vi phạm quyền riêng tư (tên thực, thông tin liên hệ, v.v.). Báo cáo từng trường hợp có số dòng.

### Trường hợp sử dụng: Kiểm toán mọi thứ (pre-release)

> Bạn: "full compliance audit"
> Kỹ năng: `com:rules --scope all`. Kiểm tra tất cả các tệp .md được theo dõi đối với tất cả các quy tắc áp dụng. Cung cấp cho bạn một báo cáo toàn dự án. Tốt trước khi phát hành.

### Trường hợp sử dụng: Xác thực một thư mục

> Bạn: "check rules in materials"
> Kỹ năng: `com:rules --scope docs/materials/`. Chạy quy tắc 04, 11 trên tất cả các tệp tài liệu. Kiểm tra mức độ bằng chứng và trạng thái xử lý.

## 5. Những cảnh báo quan trọng

**Các trình xác thực được ủy quyền cần bối cảnh.** Nếu quy tắc 02 (tài liệu tham khảo) cờ một vấn đề, com:rules gọi `psy:ref-audit` dưới nắp. Kỹ năng đó cần bối cảnh phù hợp để chạy. Nếu nó thất bại, bạn sẽ thấy lỗi và phải xử lý nó thủ công.

**Các quy tắc xử lý bị bỏ qua.** Quy tắc 06 (crisis-protocol) và 13 (workflow) là quy tắc xử lý, không phải quy tắc tệp. Chúng mô tả các bước/sự kiện, không phải frontmatter/schema. Không được xác thực ở đây.

**Schema != logic.** com:rules kiểm tra xem các trường frontmatter có tồn tại và được định dạng chính xác không. Nó KHÔNG kiểm tra xem nội dung có phải là đúng sự thật hoặc nhất quán không. Đó là công việc của các trình xác thực ngữ nghĩa như `psy:crossref`.

**Báo cáo chỉ đọc.** Bạn nhận được khuyến nghị; bạn áp dụng chúng. Kỹ năng không bao giờ sửa đổi các tệp của bạn.

**Phạm vi là quan trọng.** Cờ `--scope` xác định liệu bạn xác thực chỉ các thay đổi (uncommitted), tất cả các tệp (all), hoặc một đường dẫn cụ thể (path). Chọn phạm vi đúng hoặc lãng phí thời gian kiểm tra các tệp không liên quan.
