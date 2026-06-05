# cre:angle-discovery

> Autonomously discover publishable content angles by mining all 6 frameworks — emotional growth signals, recent materials, professional milestones, engagement history, relationship dynamics — ranked by evidence + freshness.

## What it does

Scans PSY, MAT, GRO, CRE, ORC, and relationship data for raw content signals, synthesizes them into ranked angle candidates (title, hook, evidence tier, platform fit), and outputs a CONTEXT.md block ready for `cre:post-writer` or `cre:multiplatform`. No questions asked — autonomous, cron-runnable.

## When to use

- Running periodically to discover "what should we post next?"
- Seeding `cre:exploring` (interactive refinement of discovered angles)
- Feeding `cre:post-writer --from-context` (write immediately)
- Generating N native variants via `cre:multiplatform --source <angle>`
- Dashboard-style ideation — "top 5 angles this week"

## Flags

| Flag | Effect |
|------|--------|
| `--character <slug>` | Character to mine (required) |
| `--framework <fw>` | Limit to psy\|mat\|gro\|cre\|orc\|all (default: all) |
| `--since-days N` | Freshness window — drop signals older than N days (default: 30) |
| `--top N` | Return top N ranked angles (default: 5) |
| `--graph-signal` | Include KG semantic candidates (slower; advisory only) |
| `--to-context` | Write top angle as CONTEXT.md block (cre:exploring format) |
| `--json` | Output angles JSON (for downstream processing) |

## What it does NOT do

- **Not interactive** — no user questions (use `cre:exploring` for that; Rule 03)
- **Not real-time** — signals older than `--since-days` are dropped, no historical deep dives
- **Not guaranteed unique** — may surface overlapping angles; LLM synthesis in Phase 2 deduplicates
- **Not a filter** — script gathers over-broadly; LLM prunes noise (Rule 04)
- **No event leakage** — angles are paraphrased; raw ORC payloads stay internal (Rule 14)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Related: `cre:exploring`, `cre:post-writer`, `cre:multiplatform`, `psy:relation-intelligence`
- Rules: Rule 03 (content pipeline), Rule 04 (materials ingestion), Rule 14 (CRE evidence + events)

---

## Tiếng Việt

**Công dụng:** Phát hiện tự động các góc nhìn nội dung có thể công bố bằng cách khai thác sáu khuôn khổ — tín hiệu tăng trưởng cảm xúc, tài liệu mới, mốc quan trọng về chuyên môn, lịch sử tương tác, động lực quan hệ — được xếp hạng theo bằng chứng và độ tươi mới.

**Khi nào sử dụng:**
- Chạy định kỳ để khám phá "chúng ta nên đăng bài gì tiếp theo?"
- Cung cấp dữ liệu cho `cre:exploring` (tinh chỉnh tương tác các góc nhìn được khám phá)
- Cung cấp cho `cre:post-writer --from-context` (viết ngay lập tức)
- Tạo N biến thể ngôn ngữ bản địa thông qua `cre:multiplatform --source <angle>`

**Điều nó KHÔNG làm:**
- Không tương tác — không hỏi người dùng (dùng `cre:exploring` cho việc đó)
- Không phải thời gian thực — tín hiệu cũ hơn `--since-days` bị loại bỏ
- Không đảm bảo độc nhất — có thể xuất hiện các góc nhìn trùng lặp
- Không phải bộ lọc — script thu thập quá rộng; tổng hợp LLM loại bỏ nhiễu
