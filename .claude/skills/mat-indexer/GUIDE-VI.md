# mat:indexer — Hướng dẫn

> Cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn đã tải một chồng tài liệu — bản ghi lại, thư, quan sát. Trước khi chúng có thể định hình các hồ sơ nhân vật của bạn, bạn cần biết: Tài liệu này có mâu thuẫn với những gì đã có trong hồ sơ không? Nó có hỗ trợ các tuyên bố hiện có hay thêm chi tiết mới? Có những khoảng trống trong những gì hồ sơ nói mà tài liệu này có thể điền vào không? mat:indexer trả lời cả ba câu hỏi cùng một lúc: nó tìm thấy các mâu thuẫn (và chúng nghiêm trọng đến mức nào), ánh xạ phạm vi bằng chứng trên toàn bộ hồ sơ và đánh dấu các tài liệu đã nằm trong quy trình quá lâu.

## 2. Khái niệm cốt lõi (mô hình tinh thần)

**Cánh cổng tích hợp:** Tài liệu được tải không tự động cấp cho phân tích. Giai đoạn 3 (kịch bản mat:indexer) thu thập dữ liệu mâu thuẫn và phạm vi; giai đoạn 4 (phán xét LLM) quyết định xem liệu mỗi tài liệu có an toàn để tích hợp hay không. Nếu các mâu thuẫn nhỏ hoặc được giải quyết, tài liệu chuyển sang "integrated" và sự kiện `MAT.integrated` kích hoạt, kích hoạt phân tích PSY. Nếu các mâu thuẫn có mức độ nghiêm trọng cao, tài liệu sẽ được đánh dấu để xem xét thủ công thay thế.

**Mức độ nghiêm trọng của mâu thuẫn:** Không phải tất cả các xung đột đều bằng nhau. Ngày bị sai lệch vài ngày là THẤP. Mô tả một sự kiện không phù hợp với hồ sơ là TRUNG BÌNH. Một tuyên bố quan trọng về an toàn (ví dụ: mismatch cấp độ ý tưởng tự sát) là RẤT QUAN TRỌNG và dừng cánh cổng hoàn toàn.

**Phạm vi so với khoảng trống:** Hồ sơ có 21 phần tiêu chuẩn cho mỗi nhân vật. Một số phần (ví dụ: psychology/formulation) có thể có 10+ tài liệu hỗ trợ chúng; những người khác (ví dụ: light/strengths-hope) có thể có không. Các khoảng trống không có nghĩa là hồ sơ của bạn sai — chúng đánh dấu nơi bạn cần bằng chứng thêm nếu bạn muốn độ tin cậy cao hơn.

**Trạng thái xử lý chuyển tiếp:** Sau khi xác thực giai đoạn 3, LLM cập nhật `processing_status` từ "raw" hoặc "extracted" thành "validated" (pass gate) hoặc ở lại "analyzed" (cần xem xét thủ công). Chỉ có tài liệu "validated" mới có thể trở thành "integrated".

## 3. Đường dẫn học tập

1. **Lần chạy đầu tiên:** `mat:indexer --all` — thực hiện tham chiếu chéo đầy đủ. Nhìn vào bảng mâu thuẫn (được sắp xếp theo mức độ nghiêm trọng) và ma trận phạm vi.
2. **Hiểu những khoảng trống của bạn:** `mat:indexer --coverage` — xem những phần hồ sơ nào được hỗ trợ bằng bằng chứng dưới mức.
3. **Tìm điểm đau:** `mat:indexer --contradictions` — xem liệu có bất kỳ tài liệu nào mâu thuẫn với hồ sơ không.
4. **Kiểm tra tài liệu cũ:** `mat:indexer --stale` — tìm tài liệu bị mắc kẹt trong quy trình và quyết định xem có hoàn thành hay lưu trữ.
5. **Nhân vật duy nhất:** `mat:indexer --character <name>` — phóng to trên tài liệu và hồ sơ của một người.

## 4. Các trường hợp sử dụng

### Trường hợp sử dụng: Xác thực đầu tiên sau tải hàng loạt
> **Bạn:** "Tôi vừa tải 30 tài liệu cho cả ba nhân vật. Có bất kỳ mâu thuẫn nào không?"
> 
> **Kỹ năng:** Chạy `--all`:
> - Quét tất cả các tài liệu để tìm các tuyên bố thực tế (sự kiện, mối quan hệ, trạng thái cảm xúc)
> - So sánh từng tuyên bố với phần hồ sơ tương ứng
> - Bảng mâu thuẫn trả lại:
>   ```
>   # | Tài liệu | Tuyên bố | Hồ sơ nói | Mức độ | Tệp
>   1 | letter-01 | "Nhân vật A anxious Jan 2024" | "anxiety emerged Jun 2024" | MEDIUM | ...
>   2 | news-02 | "crisis hospitalization" | "no psychiatric admission" | CRITICAL | ...
>   ```
> - Bạn thấy: 1 RẤT QUAN TRỌNG (dừng — cần xem xét ngay lập tức), 2 TRUNG BÌNH (đánh dấu để phán xét thủ công)

### Trường hợp sử dụng: Bản đồ phạm vi cho một nhân vật
> **Bạn:** "Chúng ta có bằng chứng gì cho hồ sơ của Nhân vật C? Những khoảng trống ở đâu?"
> 
> **Kỹ năng:** Chạy `--character chien --coverage`:
> - Liệt kê tất cả 21 phần hồ sơ
> - Đối với mỗi, đếm bao nhiêu tài liệu tham khảo nó + những gì tầng
>   ```
>   | Phần hồ sơ | Tài liệu hỗ trợ | Tầng | Khoảng trống? |
>   | psychology/formulation | 5 tệp (T1×2, T2×3) | Mạnh | Không |
>   | light/strengths-hope | 0 tệp | — | CÓ |
>   ```
> - Bạn thấy: phần sức mạnh/hy vọng không có bằng chứng. Bạn có thể muốn thêm các cuộc phỏng vấn hoặc cuộc trò chuyện cho thấy khả năng phục hồi.

### Trường hợp sử dụng: Dọn dẹp tài liệu cũ
> **Bạn:** "Tôi có một số tài liệu đã ở trong 'raw' trong nhiều tuần. Tôi phải làm gì?"
> 
> **Kỹ năng:** Chạy `--stale`:
> - Tìm tất cả các tài liệu có `processing_status: raw` hoặc `extracted` cũ hơn 7 ngày
> - Hiển thị tệp, trạng thái, bao lâu bị mắc kẹt
> - Gợi ý: chạy lại `mat:loader --ingest` để hoàn thành chúng, hoặc sử dụng `mat:archive` để loại bỏ chúng
> - Giúp bạn dọn sạch quy trình

### Trường hợp sử dụng: Mâu thuẫn sâu
> **Bạn:** "Chỉ các mâu thuẫn — không phân tích phạm vi, tôi đang vội."
> 
> **Kỹ năng:** Chạy `--contradictions` chỉ:
> - Đầu ra nhanh: chỉ bảng mâu thuẫn
> - Được sắp xếp theo mức độ nghiêm trọng (RẤT QUAN TRỌNG trước)
> - Tiết kiệm thời gian nếu bạn chỉ cần ưu tiên các xung đột

## 5. Những cảnh báo quan trọng

**Mâu thuẫn không có nghĩa là lỗi.** Nếu tài liệu nói "Nhân vật A lo âu vào tháng 1" và hồ sơ nói "lo âu xuất hiện vào tháng 6," đó là một mâu thuẫn thực sự. Nhưng có thể hồ sơ không đầy đủ (lo âu tiềm ẩn), hoặc tài liệu nhớ lầm, hoặc cả hai đều đúng (các loại lo âu khác nhau). Mâu thuẫn được đánh dấu; LLM quyết định nó có nghĩa là gì.

**Khoảng trống phạm vi là thông tin, không phải vấn đề.** Một số phần hồ sơ vốn khó chứng minh hơn. Sức mạnh (light/strengths-hope.md) có thể có ít tài liệu hơn các chấn thương. Đó là bình thường — nó không làm mất hiệu lực hồ sơ của bạn, chỉ báo hiệu nơi bạn có thể muốn thêm thông tin đầu vào.

**LLM phán xét tích hợp, không phải kịch bản.** Kịch bản mat:indexer thu thập các mâu thuẫn và phạm vi; chúng không phát hành các sự kiện. Chỉ LLM, sau khi xem xét đầu ra, quyết định xem liệu một tài liệu có "validated" (vượt qua giai đoạn 4) hay không và có phát hành `MAT.integrated` hay đánh dấu nó để xem xét thủ công.

**Cũ không có nghĩa là xấu.** Một tài liệu bị mắc kẹt ở "raw" trong 2 tháng có thể hoàn toàn tốt — bạn chỉ chưa hoàn thành việc nạp nó. Cờ `--stale` là một cú đẩy để hoàn thành hoặc lưu trữ nó, không phải một lời lên án.

**Không bao giờ sửa đổi hồ sơ từ mat:indexer.** Nếu mâu thuẫn là thực sự, hồ sơ có thể không đầy đủ hoặc sai. Nhưng mat:indexer không bao giờ ghi vào hồ sơ — bạn xem xét cờ, sau đó cập nhật hồ sơ riêng biệt thông qua kỹ năng miền PSY.
