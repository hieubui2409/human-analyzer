# psy:profile-lite

> Compress full character profiles into token-efficient summaries (~100-150 lines per character). Cached with git-aware invalidation.

## What it does

Reduces ~700–1000-line profiles to ~120–150 lines each. Preserves factual accuracy, clinical anchors, and actionable voice cues. Caches to `.claude/profile-cache/`, auto-invalidates when source profiles change (via git hash comparison). Enables loading all 3 characters in 1–2% of context budget vs 25%.

## When to use

- Context budget tight: "Load all 3 characters efficiently"
- Lite profile valid: check cache status with `--stats`
- Force refresh: `--refresh` to regenerate
- Trigger phrases: lite profile, compress profile, compact profile, profile summary, light load

## Flags

| Flag                 | Effect |
|----------------------|--------|
| `--all`              | Load all 3 lite profiles (default) |
| `--character <name>` | One character only |
| `--refresh`          | Force regeneration (ignore cache) |
| `--stats`            | Show cache status + size comparison |

## What it does NOT do

- Does NOT modify source profiles (derived artifact only)
- Does NOT replace full profiles (use for context loading, not detailed validation)
- Does NOT auto-fix stale cache (user must run --refresh or source files change)
- Does NOT validate consistency (that's psy:crossref)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Nén các hồ sơ nhân vật đầy đủ thành các bản tóm tắt hiệu quả mã thông báo.** Được lưu trong bộ đệm với vô hiệu hóa nhận thức git.

**Khi nào sử dụng:** Ngân sách ngữ cảnh chặt chẽ, tải tất cả các nhân vật một cách hiệu quả, kiểm tra trạng thái bộ đệm.
