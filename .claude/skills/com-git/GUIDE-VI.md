# com:git — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã chỉnh sửa tài liệu, tạo tính năng hoặc sửa lỗi. Bây giờ bạn muốn lưu những thay đổi đó vào git mà không cần suy nghĩ về tệp nào quan trọng. com:git đọc các chỉnh sửa của bạn, chọn những tệp liên quan, hiển thị xem trước, commit với thông điệp chuyên nghiệp, và đẩy — tất cả trong một lệnh.

## 2. Khái niệm cốt lõi (mô hình tư duy)

**Chọn tệp thông minh:** Commit nhóm các tệp theo phạm vi (profile, assets, refs, materials). Không phải tất cả những gì bạn đã chạm vào đều được đưa vào — chỉ những tệp liên quan đến công việc hiện tại của bạn. Bí mật luôn bị loại trừ.

**Xem trước trước khi hành động:** Chế độ mặc định dừng lại và hỏi "điều này có đúng không?" trước khi commit. Bạn có thể chỉnh sửa, xác nhận hoặc thêm tệp khác.

**Rebase tự động:** Nếu ai đó đẩy trong khi bạn đang làm việc, `--push` tự động rebase và thử lại. Nếu xung đột rebase, nó sẽ dừng lại và yêu cầu sự giúp đỡ của bạn.

**Các commit thông thường:** Thông điệp tuân theo mẫu `type(scope): description` — lịch sử git sạch sẽ, dễ phân tích.

## 3. Lộ trình học tập

**Lần chạy đầu tiên:** `com:git` (mặc định) — xem xét trước, nói "có" để commit, xem nó đẩy.

**Tiếp theo:** Thử `com:git --auto` khi bạn tin tưởng vào lựa chọn tệp; bỏ qua xác nhận, đi thẳng đến commit + push.

**Khi bạn phát triển:** Sử dụng `--dry-run` để xem trước mà không thực thi; `--commit --all` để ghi sơ đồ mọi thứ; `--sync` để kéo trước khi đẩy (quy trình an toàn trước tiên).

## 4. Trường hợp sử dụng (mỗi = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Commit các thay đổi từ phiên này

> Bạn: "commit công việc của tôi"
> Kỹ năng: Đọc git status, phát hiện 3 tệp .md đã thay đổi trong docs/profiles/. Tạo thông điệp `docs(profile): update character psychology notes`. Hiển thị xem trước, chờ xác nhận, commit + push.

### Trường hợp sử dụng: Auto-commit và push (không gián đoạn)

> Bạn: "auto commit"
> Kỹ năng: `com:git --auto`. Các bước tương tự nhưng BỎ QUA câu hỏi xem trước. Commit các tệp liên quan + push. Hữu ích khi bạn tự tin.

### Trường hợp sử dụng: Dry-run để xem những gì sẽ xảy ra

> Bạn: "bạn sẽ commit cái gì?"
> Kỹ năng: `com:git --dry-run`. Hiển thị thông điệp và danh sách tệp, nhưng KHÔNG ghi sơ đồ hoặc commit. Cho phép bạn xác minh trước khi chạy thứ thực.

### Trường hợp sử dụng: Thông điệp commit tùy chỉnh

> Bạn: "commit với thông điệp 'thêm bản phác thảo nhân vật mới'"
> Kỹ năng: `com:git -m "add new character sketch"`. Sử dụng thông điệp của bạn thay vì tự động tạo. Vẫn xem trước, vẫn hỏi xác nhận.

### Trường hợp sử dụng: Commit tất cả mọi thứ

> Bạn: "commit tất cả các thay đổi của tôi"
> Kỹ năng: `com:git --commit --all`. Ghi sơ đồ tất cả các tệp đã thay đổi (ngoài bí mật), tạo thông điệp, hiển thị xem trước, xác nhận, commit.

## 5. Những cảnh báo quan trọng

**Bí mật bị loại trừ tự động.** Bạn không thể commit `.env`, `credentials.json` hoặc các tệp khóa — kỹ năng từ chối chúng. Đây là một tính năng bảo mật.

**Xem trước là mặc định.** Nếu bạn nói `--commit` (không có `--auto`), bạn SẼ được yêu cầu xác nhận. Kỹ năng không bao giờ commit mà không hiển thị cho bạn trước tiên.

**Xung đột rebase cần bạn.** Nếu pull --rebase gặp xung đột, kỹ năng sẽ hủy bỏ rebase và báo cáo. Bạn phải giải quyết thủ công và thử lại lần đẩy.

**Nhánh được bảo vệ.** Nếu remote của bạn có quy tắc bảo vệ nhánh (ví dụ: main), kỹ năng sẽ không force-push. Nó tôn trọng các quy tắc.

**Làm sạch khoảng trắng.** Kỹ năng chạy prettier trên các tệp được ghi sơ đồ trước khi commit (không xảy ra lỗi gì — nếu prettier bị thiếu, nó sẽ bỏ qua). Điều này giữ định dạng nhất quán.
