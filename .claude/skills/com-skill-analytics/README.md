# com:skill-analytics

> Observe and analyze framework skills + scripts across 11 lenses: health, dependencies, cascades, usage, coverage, content, dashboard, memory, reliability, forensics, workflows.

## What it does

Deterministic, read-only observability for all 58 framework skills and scripts. Scans skill syntax, dependency graphs, event topology, invocation metrics, token costs, SKILL.md budget, memory health, subagent reliability, session forensics, and workflow chains. No edits; pure analysis.

## When to use

- User says "skill health", "skill analytics", "dependency graph", "token usage", "content pipeline"
- Before releases or after adding/editing scripts
- Finding broken scripts, mapping dependencies, spotting unused skills, tracking subagent reliability

## Flags

| Flag          | Effect                                    |
| ------------- | ----------------------------------------- |
| `--health`    | Script syntax + SKILL.md parseable + fan-in |
| `--deps`      | Import dependency graph + critical modules |
| `--cascade`   | Skill interaction topology from events     |
| `--usage`     | Invocation counts + token attribution      |
| `--coverage`  | SKILL.md budget, trigger overlap, gaps     |
| `--content`   | Posts per platform, cadence, inactive      |
| `--dashboard` | All lenses + traffic-light snapshot       |
| `--memory`    | Memory dir health, orphans, dead links    |
| `--reliability` | Subagent success/failure rates + modes   |
| `--forensics` | Session reconstruction from transcripts   |
| `--workflow`  | Actual chains vs routing-doc declared    |
| `--all`       | Run all 11 lenses sequentially            |

## What it does NOT do

- **Does not edit skills** — gather-only; LLM judges refactor decisions
- **Does not audit event consistency** — that is `orc:audit`
- **Does not judge skill necessity** — that is `orc:skill-stocktake`
- **Does not scan ck skills** — scope is project frameworks (mat, psy, cre, gro, orc, com) only
- **Does not make behavioral inferences** — only invocation/perf metrics, not intent

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

Khả năng quan sát xác định, chỉ đọc cho tất cả 58 kỹ năng khung và script. Quét cú pháp kỹ năng, biểu đồ phụ thuộc, cấu trúc liên kết sự kiện, số liệu gọi, chi phí token, ngân sách SKILL.md, sức khỏe bộ nhớ, độ tin cậy tác nhân phụ, pháp y phiên, và chuỗi quy trình. Không chỉnh sửa; phân tích thuần túy.

**Khi sử dụng:** người dùng nói "skill health", "skill analytics", "dependency graph", "token usage", "content pipeline" — thường trước khi phát hành hoặc sau khi thêm/chỉnh sửa script.

**Không làm gì:**
- Không chỉnh sửa kỹ năng
- Không kiểm tra tính nhất quán của sự kiện
- Không đánh giá sự cần thiết của kỹ năng
- Không quét kỹ năng ck
- Không suy luận hành vi
