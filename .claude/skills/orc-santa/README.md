# orc:santa

> Dual-reviewer quality gate for high-risk changes with input-level isolation.

## What it does

Spawns 2 independent reviewers to examine high-risk changes (profile edits, content, growth files). Each reviewer receives only target files + pre-check report, never the other's output. Both must pass to ship. Any fail → fix → re-review with fresh agents (max 2 rounds). Read-only quality framework.

## When to use

- **After high_risk classification** — orc:classify suggests Santa
- **Major profile edits** — clinical accuracy + cross-character consistency review
- **High-risk content** — voice authenticity + profile alignment review
- **Growth file updates** — career data accuracy + timeline consistency review
- Trigger phrases: "santa review", "dual review", "quality gate", "santa method"

## Flags

| Flag | Effect |
|------|--------|
| `--review <target>` | Target file or directory |
| `--framework <psy\|cre\|gro\|mat>` | Domain framework |
| `--scope <full\|changes\|ref>` | Scope mode (default: ref) |
| `--auto` | Auto-triggered by orc:classify |

## What it does NOT do

- Does NOT modify files—only reviews.
- Does NOT enforce fixes—recommends; you fix and re-review.
- Does NOT go beyond 2 review rounds—escalates to user after round 2 if issues remain.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Sinh ra 2 nhà phê bình độc lập để kiểm tra các thay đổi rủi ro cao (chỉnh sửa hồ sơ, nội dung, tệp tăng trưởng). Mỗi nhà phê bình chỉ nhận được các tệp mục tiêu + báo cáo kiểm tra trước, không bao giờ đầu ra của người khác. Cả hai phải vượt qua để vận chuyển. Bất kỳ thất bại → sửa → xem xét lại với các tác nhân tươi (tối đa 2 vòng). Khung chất lượng chỉ đọc.

### Khi nào dùng

- **Sau phân loại high_risk** — orc:classify gợi ý Santa
- **Chỉnh sửa hồ sơ chính** — kiểm tra độ chính xác lâm sàng + sự nhất quán đa nhân vật
- **Nội dung rủi ro cao** — kiểm tra xác thực giọng + sự phù hợp hồ sơ
- **Cập nhật tệp tăng trưởng** — kiểm tra độ chính xác dữ liệu sự nghiệp + sự nhất quán dòng thời gian
- Cụm từ kích hoạt: "santa review", "dual review", "quality gate", "santa method"

### Không làm gì

- **Không sửa đổi** tệp—chỉ kiểm tra.
- **Không thực thi** sửa chữa—khuyến nghị; bạn sửa và kiểm tra lại.
- **Không vượt quá** 2 vòng kiểm tra—tăng cấp cho người dùng sau vòng 2 nếu vấn đề vẫn còn.
