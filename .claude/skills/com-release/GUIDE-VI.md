# com:release — Hướng dẫn

> Dành cho người vận hành. English: [`GUIDE-EN.md`](./GUIDE-EN.md).

## 1. Skill này làm gì cho bạn

Bạn đã ghi một loạt thay đổi dưới `## [Unreleased]` trong `CHANGELOG.md` và pack sẵn sàng phát hành.
com:release biến nó thành một release có version: khoá `[Unreleased]` thành `[X.Y.Z] — <ngày>`, mở
`[Unreleased]` rỗng mới, bump manifest, sinh lại catalog RELEASE-NOTES deterministic, và đưa cho bạn
đúng các lệnh push tag để kích hoạt release CI.

## 2. Khái niệm cốt lõi (mô hình tư duy)

**Changelog viết tay, không sinh từ git.** Trong quá trình dev, bạn (hoặc LLM) viết mục dưới
`[Unreleased]`. Không có gì đọc `git log` lúc build, nên `CHANGELOG.md` đã commit là tái lập được —
chạy lại tooling về sau không bao giờ làm thay đổi nó.

**Khoá = dời, không phải sinh.** Một release-cut đổi tiêu đề `[Unreleased]` thành `[X.Y.Z] — <ngày>` và
chèn `[Unreleased]` rỗng mới lên trên. Nội dung bạn đã viết trở thành body của version đó.

**Hai artifact, hai vai.** `CHANGELOG.md` = "có gì đổi" cho người (curate). `RELEASE-NOTES-v<ver>.md` =
catalog "ship cái gì" deterministic (mọi skill/agent/hook, tự liệt kê). Mục changelog vừa khoá cũng trở
thành body của GitHub Release.

**Tag là trigger.** Đẩy `frameworks-v<ver>` kích hoạt `frameworks-pack-release.yml` (kiểm tag↔manifest →
determinism gate → PII gate → build → SHA256 → GitHub Release). Việc push là **của owner**.

## 3. Lộ trình học

**Xem trước:** `release_changelog.py --bump minor` (dry-run) — thấy version, phép khoá, và các lệnh git,
không ghi gì.

**Áp dụng local:** thêm `--apply` — ghi CHANGELOG/manifest/notes và in các lệnh tag cho bạn chạy.

**Owner go:** thêm `--push` (kèm `--apply`) chỉ khi owner đồng ý rõ ràng — tự tag + push, kích hoạt CI.

**Soi body release:** `--extract X.Y.Z` in đúng thứ CI sẽ đăng làm body của GitHub Release.

## 4. Tình huống dùng (mỗi cái = một hội thoại mẫu)

### Tình huống: Xem trước bản minor kế

> Bạn: "bản minor tiếp theo trông thế nào?"
> Skill: Phỏng vấn xác nhận minor (vd 1.0.0 → 1.1.0), đọc lại nội dung `[Unreleased]`, chạy
> `release_changelog.py --bump minor` (dry-run), hiện phép khoá + các lệnh git. Không ghi gì.

### Tình huống: Cut một release version cụ thể (local)

> Bạn: "cut release 1.1.0"
> Skill: Xác nhận version + soi `[Unreleased]`, rồi `--release 1.1.0 --apply`. Khoá changelog, bump
> manifest, sinh lại notes, và in `git tag frameworks-v1.1.0 && git push …` cho owner.

### Tình huống: Bản release candidate

> Bạn: "tạo rc cho 1.2.0"
> Skill: `--release 1.2.0 --pre-release rc.1` → version `1.2.0-rc.1`, đăng dưới dạng GitHub prerelease.

### Tình huống: Xem body release CI sẽ đăng

> Bạn: "cho xem release notes của 1.1.0"
> Skill: `--extract 1.1.0` — in body của mục đó, đã quét PII.

## 5. Lưu ý quan trọng

**Push là của owner.** Mặc định dry-run. `--push` cần `--apply` VÀ owner đồng ý rõ ràng. Release lên
master và re-tag một version đã có thì không bao giờ làm tự động.

**`[Unreleased]` rỗng bị từ chối.** Nếu chưa ghi gì, cut sẽ dừng — điền changelog trước đã.

**Một version chỉ cut một lần.** Cut lại `[X.Y.Z]` đã tồn tại bị từ chối; công cụ không sửa mục cũ.

**PII gate.** Mục vừa khoá và notes sinh lại đều bị quét token tên thật; rò rỉ thì cut dừng. `CHANGELOG.md`
đã commit cũng được test gate PII-clean.

**Determinism.** RELEASE-NOTES nhận ngày tường minh và sort mọi danh sách — cùng cây + version + ngày ⇒
output byte-identical, nên determinism gate của CI luôn xanh.
