# psy:wave — Hướng dẫn

> Cho nhà điều hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn vừa tích hợp 10 bản phỏng vấn cho một nhân vật mới. Hồ sơ trống. Thay vì thủ công chỉnh sửa 25 tệp trong sự cô lập, kỹ năng này điều phối quy trình 3 sóng có cấu trúc: (1) Sóng 1 trích xuất các sự kiện khách quan (danh tính, dòng thời gian, mối quan hệ) từ các vật liệu. (2) Sóng 2 phân tích tâm lý (vết mích, phòng thủ, ứng phó, giọng nói) với hỗ trợ lâm sàn. (3) Sóng 3 xác thực mọi thứ (tính nhất quán qua các nhân vật, độ chính xác tham chiếu, cập nhật xếp tầng). Bạn nhận được một hồ sơ hoàn chỉnh, được xác thực ở cuối — không phải một đống lộn xộn của các tệp một nửa điền đầy.

## 2. Khái niệm cốt lõi (mô hình tư duy)

- **Mô hình sóng đảm bảo tính hoàn chỉnh**: Mỗi sóng dựa trên sóng trước đó. Sóng 1 = dữ liệu; Sóng 2 = phân tích; Sóng 3 = tính nhất quán. Bỏ qua một, và hồ sơ yếu.
- **Cổng ngăn chặn rác vào**: Sau Sóng 1, kiểm tra: chúng ta có đủ sự kiện dòng thời gian không? Sau Sóng 2, kiểm tra: tất cả các thuật ngữ lâm sàn có được tham chiếu không? Cổng Sóng 3 = psy:crossref + psy:ref-audit thông qua.
- **Xếp tầng được tích hợp sẵn**: Sóng 3 tự động chạy psy:propagate, vì vậy các nhân vật liên quan được cập nhật đối xứng (không bị quên).

## 3. Đường dẫn học tập

**Đường ống đầy đủ:** `psy:wave --character chiến --all` — tạo hồ sơ hoàn chỉnh từ đầu.

**Sóng riêng lẻ:** `psy:wave --character hieu --wave 1` (trích xuất sự kiện), sau đó `--wave 2` (tâm lý), sau đó `--wave 3` (xác thực).

**Kiểm tra tiến trình:** `psy:wave --character hoa --status` — xem những sóng nào được thực hiện.

**Với bối cảnh kế hoạch:** `psy:wave --character chien --plan ./plans/260605-chiến-profile-build/plan.md` — theo dõi tiến trình trong tệp kế hoạch.

## 4. Trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Nhân vật mới từ đầu

> Bạn: "Tôi có vật liệu cho một nhân vật mới (30 trang phỏng vấn). Tạo hồ sơ đầy đủ."
> Kỹ năng: `psy:wave --character <name> --all`
> → Sóng 1: Trích xuất 45 sự kiện, 8 thành viên gia đình, 12 mối quan hệ. Kiểm tra cổng: ≥N sự kiện? ✓ Tiếp tục. → Sóng 2: Xác định nỗi sợ hãi cốt lõi, cơ chế phòng thủ, kích hoạt. Kiểm tra cổng: ≥5 kích hoạt? ✓ ≥3 cơ chế ứng phó? ✓ Tiếp tục. → Sóng 3: Chạy psy:crossref (không có nhân vật khác để so sánh yet, nhưng cấu trúc được xác thực). Chạy psy:ref-audit (tất cả các thuật ngữ lâm sàn được tham chiếu). Đầu ra: hồ sơ 25 tệp hoàn chỉnh + báo cáo xác thực.

### Trường hợp sử dụng: Cập nhật lớn cho nhân vật hiện có

> Bạn: "Câu chuyện của Nhân vật C phát triển đáng kể. Tôi có vật liệu mới (sự kiện khủng hoảng, tiết lộ). Làm sóng lại hồ sơ."
> Kỹ năng: `psy:wave --character chien --all`
> → Sóng 1: Cập nhật identity/core.md, timeline/overview.md, milestones.md với sự kiện mới. Cổng: tất cả sự kiện có ngày? ✓ → Sóng 2: Phân tích lại psychology/formulation.md dưới ánh sáng của khủng hoảng mới. Chạy psy:crisis-assess (phát hiện rủi ro CAO). Cổng: giao thức khủng hoảng áp dụng? ✓ → Sóng 3: psy:crossref kiểm tra xem tệp Nhân vật A/Nhân vật B cần cập nhật không (cung điểm Nhân vật C thay đổi). psy:propagate gợi ý cập nhật. Xác thực. Xong.

### Trường hợp sử dụng: Kiểm tra tiến trình sóng

> Bạn: "Tôi bắt đầu Sóng 1 hôm qua. Trạng thái là gì?"
> Kỹ năng: `psy:wave --character hieu --status`
> → Sóng 1: ✅ Hoàn thành (trích xuất 67 sự kiện, 15 mối quan hệ). Sóng 2: 🔄 Đang tiến hành (psychology/formulation.md: 40% xong). Sóng 3: ⬜ Chưa bắt đầu. Trở ngại: "Hoàn thành psychology/formulation.md để tiếp tục Sóng 3."

## 5. Cảnh báo quan trọng

- **Sóng là tuần tự, không song song**: Bạn không thể bỏ qua Sóng 1 và nhảy đến Sóng 2. Mỗi cái dựa trên cái trước.
- **Cổng là không thể thương lượng**: Nếu cổng Sóng 1 thất bại (quá ít sự kiện), sóng sẽ không tiếp tục đến Sóng 2. Sửa khoảng trống trước tiên.
- **Sóng 3 là bắt buộc**: Bạn không thể xuất bản hồ sơ mà không có psy:crossref + psy:ref-audit thông qua (ngầm hiểu bởi hoàn thành Sóng 3).
- **Cập nhật xếp tầng cần xác nhận**: Sóng 3 gợi ý cập nhật qua các nhân vật nhưng không tự động áp dụng. Bạn xác nhận, sau đó psy:propagate thực hiện.
- **Hành động sau sóng bắt buộc**: Sau khi Sóng 3 hoàn thành, chạy `orc:compounding` để trích xuất những hiểu biết để lưu vào bộ nhớ, và cập nhật `orc:session-state` để phục hồi.
