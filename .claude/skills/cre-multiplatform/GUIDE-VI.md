# cre:multiplatform — Hướng dẫn

> Dành cho người vận hành. Tiếng Anh: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Kỹ năng này làm gì cho bạn

Bạn khám phá ra một góc nhìn: "Bước ngoặt tính nhất quán trong hướng dẫn của Nhân vật A." Bạn muốn cái đó trên LinkedIn (chuyên nghiệp), TikTok (hướng móc), và Facebook (cảm xúc). Nhưng không phải "cùng một văn bản, định dạng khác nhau." LinkedIn nên là văn bản-đầu tiên với một câu đóng câu hỏi. TikTok nên là kịch bản 9:16 với móc <1 giây. Facebook nên là kể chuyện nặng. Kỹ năng này viết 3 bản gốc hoàn toàn khác nhau từ một khái niệm, xác nhận từng bản trên nền tảng (cấp độ bằng chứng, giọng điệu, ngưỡng quyền riêng tư), và chỉ công bố những bản đó vượt qua.

## 2. Các khái niệm cốt lõi (mô hình tư duy)

**Tạo gốc 1→N (không định dạng lại):**

Các kịch bản lập kế hoạch cho các bài viết gốc trên mỗi nền tảng (cấu trúc gốc + ràng buộc + góc nhìn nguồn). LLM đọc bản tóm tắt + hồ sơ giọng điệu → viết bài gốc (không phải reformat chính). Mỗi nền tảng nhận được artifact riêng, giọng điệu, móc mô hình, độ dài của nó.

**Các cổng cách ly cạnh tranh:**

Sau khi tạo, từng biến thể chạy qua 3 cổng:
1. `cre:evidence-scanner` — yêu cầu được hỗ trợ bởi T1-T2? (THẤT BẠI nếu T4-T5 hoặc rò rỉ)
2. `cre:voice-audit` — giọng điệu trùng khớp với giọng của nhân vật? (THẤT BẠI nếu DRIFT cao)
3. `cre:privacy-guard` — PII/rò rỉ lâm sàn, theo ngưỡng quyền riêng tư của nền tảng? (THẤT BẠI nếu có)

Bất kỳ biến thể nào không vượt qua bất kỳ cổng nào được GIỮ LẠI (không viết). Những cái khác vẫn được gửi đi. Ngưỡng cách ly cạnh tranh dành riêng cho nền tảng có nghĩa là LinkedIn (nghiêm ngặt: không có tên đồng nghiệp) nghiêm ngặt hơn blog (cho phép).

**Nguồn ràng buộc DRY:** Quy tắc nền tảng (độ dài, móc, hashtag, tỷ lệ khía cạnh, ngưỡng quyền riêng tư) sống một lần trong `.claude/scripts/platform_lib/platform_constraints.py`, được nhập bởi kỹ năng này và `cre:repurpose`.

## 3. Đường học tập

**Lần chạy đầu tiên:** Cung cấp một góc nhìn từ `cre:angle-discovery`:
```bash
.claude/skills/.venv/bin/python3 .claude/skills/cre-multiplatform/scripts/generate-native-variants-for-platforms.py \
  --source "Tính nhất quán hướng dẫn của Nhân vật A" --slug 260526-mentorship --platforms linkedin,tiktok,facebook --dry-run
```
Xem các bài tóm tắt được lập kế hoạch: LinkedIn brief (văn bản-đầu tiên, 3000 ký tự, giọng điệu chuyên nghiệp). TikTok brief (kịch bản, 9:16, hội thoại). Facebook brief (tường thuật, 6000 ký tự, cảm xúc).

**Khi bạn phát triển:** Hãy thử `--platforms all` (7 nền tảng) khi bạn muốn đạt được mức tối đa. Sử dụng `--character hieu` để khóa hồ sơ giọng điệu, cải thiện độ chính xác kiểm toán giọng điệu.

**Luồng tiêu chuẩn:** Khám phá góc nhìn → `cre:multiplatform --source <angle> --platforms active` → LLM viết → cổng chạy → biến thể công bố.

## 4. Các trường hợp sử dụng (mỗi cái = một cuộc trò chuyện mẫu)

### Trường hợp sử dụng: Batch multiplatform từ khám phá

> **Bạn:** `cre:angle-discovery --character hieu --top 3 --json` trả lại 3 góc nhìn.
>
> **Bạn:** Vòng lặp: mỗi góc nhìn, `cre:multiplatform --source <angle> --platforms linkedin,tiktok,facebook --slug {dated-slug}`.
>
> **Kỹ năng:** Viết 3 bản gốc trên mỗi góc nhìn (9 bài đăng tổng cộng), cổng mỗi cái. 7 đạt, 2 giữ lại (bằng chứng THẤT BẠI trên một nền tảng, drift giọng điệu trên nền tảng khác).
>
> **Bạn:** Công bố 7 đạt; điều tra 2 giữ lại.

### Trường hợp sử dụng: Các nền tảng hoạt động duy nhất

> **Bạn:** `cre:multiplatform --source context.md --slug 260526-pivot --platforms active --character hieu`
>
> **Kỹ năng:** Mặc định `active` = các nền tảng có thư mục tài sản hiện tại (blog, facebook, linkedin). Chỉ viết cho những cái đó.
>
> **Bạn:** Công bố cho các nền tảng bạn thực sự sử dụng.

## 5. Những cảnh báo quan trọng

- **Gốc ≠ định dạng lại:** Mỗi nền tảng nhận được một lần viết mới, không phải một bản sao được định dạng lại. Điều này chậm hơn nhưng kiếm 2-3× tương tác nhiều hơn.
- **Các cổng có thể chặn:** Một biến thể không vượt qua bất kỳ cổng nào được GIỮ LẠI. Bạn không ghi đè nó hoặc buộc công bố. Điều tra tại sao nó thất bại.
- **Ngưỡng quyền riêng tư khác nhau:** LinkedIn nghiêm ngặt (không có tên đồng nghiệp ngay cả khi được đề cập tích cực). Blog cho phép (có thể thảo luận các câu chuyện gia đình). Cùng một yêu cầu có thể PASS trên blog, THẤT BẠI trên LinkedIn.
- **Ràng buộc nền tảng sống một lần:** Đừng mã hóa cứng quy tắc nền tảng trong nhắc lệnh. Sử dụng `platform_constraints.py` (chia sẻ với `cre:repurpose`).

## Xem thêm

- [`SKILL.md`](./SKILL.md) để biết hợp đồng kỹ thuật
- `cre:angle-discovery` — cung cấp các góc nhìn cho kỹ năng này
- `cre:post-writer` — quy trình đầy đủ nền tảng duy nhất (điều này quạt ra N)
- `cre:repurpose` — 1→1 sau khi công bố (chia sẻ platform_constraints.py)
- `cre:evidence-scanner`, `cre:voice-audit`, `cre:privacy-guard` — cổng cách ly cạnh tranh
- Quy tắc 03 (quy trình nội dung), Quy tắc 14 (sự kiện CRE)
