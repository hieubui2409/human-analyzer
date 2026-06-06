# com:release

> Cut a versioned release of the frameworks pack via the Keep a Changelog lifecycle. Interview-driven; the tag push is owner-owned.

## What it does

Manages the release lifecycle of the root `CHANGELOG.md`: locks the hand-curated `[Unreleased]` section
into a versioned `[X.Y.Z] — <date>` entry, opens a fresh `[Unreleased]`, bumps the pack manifest, and
regenerates the deterministic `RELEASE-NOTES` catalog. Pushing the resulting `frameworks-v<ver>` tag fires
the release CI, which publishes a GitHub Release whose body is the locked changelog section.

## When to use

- User says "cut a release", "release vX.Y.Z", "bump version", "ship the pack"
- Typical position: after a batch of changes is recorded under `[Unreleased]` and the pack is ready to ship

## Flags

| Flag | Effect |
| --- | --- |
| `--extract X.Y.Z` | Print a version's changelog section (read-only; what CI uses as the release body) |
| `--release X.Y.Z` | Cut a release at an explicit version |
| `--bump patch\|minor\|major` | Cut a release at the next version computed from the manifest |
| `--pre-release LABEL` | Append a pre-release label (e.g. `rc.1`); published as a GitHub prerelease |
| `--apply` | Write changes (default: dry-run preview) |
| `--push` | Owner opt-in: also tag + push (requires `--apply`) |

## What it does NOT do

- **Never auto-derives content from git** — `[Unreleased]` is hand/LLM-maintained; the committed file is reproducible
- **Never pushes a tag without explicit owner approval** — default dry-run; `--push` requires `--apply` + a go
- **Never edits a past version** or releases an empty `[Unreleased]`

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

Quản lý vòng đời release của `CHANGELOG.md` ở root: khoá mục `[Unreleased]` (viết tay/LLM) thành mục có
version `[X.Y.Z] — <ngày>`, mở `[Unreleased]` rỗng mới, bump version trong pack manifest, và sinh lại
catalog `RELEASE-NOTES` deterministic. Đẩy tag `frameworks-v<ver>` sẽ kích hoạt release CI, tạo GitHub
Release với body chính là mục changelog vừa khoá.

**Khi dùng:** người dùng nói "cut a release", "release vX.Y.Z", "bump version", "ship pack" — thường sau khi
gom đủ thay đổi dưới `[Unreleased]`.

**Không làm gì:**
- Không tự sinh nội dung từ git — `[Unreleased]` do người/LLM giữ; file committed tái lập được
- Không đẩy tag khi chưa có owner đồng ý rõ ràng — mặc định dry-run; `--push` cần `--apply` + lệnh go
- Không sửa version cũ, không release `[Unreleased]` rỗng
