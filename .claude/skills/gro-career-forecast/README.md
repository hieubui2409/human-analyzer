# gro:career-forecast

> Generate LLM-powered career trajectory projections for any character. All output marked [FORECAST — NOT FACTUAL].

## What it does

Gathers current career data (stage, skills, learning patterns, education) and projects 3–5 year trajectories using Super's Life-Career Rainbow model, Dreyfus skill progression, and demographic context. Speculative analysis only — all projections explicitly marked non-factual.

## When to use

- **Trigger phrases:** "forecast career", "career projection", "predict career", "future career trajectory"
- **Workflow position:** After `gro:career-path` and `gro:competency-map` have established baseline data
- **Output user:** character profile curators exploring "what-if" scenarios

## Flags

| Flag | Effect |
|------|--------|
| `--character <name>` | Forecast one character only |
| `--all` | Forecast all 3 characters (default) |
| `--horizon <years>` | Projection window; default 3 |
| `--json` | Machine-readable output |

## What it does NOT do

- **Not factual:** [FORECAST — NOT FACTUAL] marker on all output; projections are speculative, not verified
- **Not prescriptive:** does not recommend actions, only speculates on trajectories
- **Boundary (Rule 15):** read-only GRO skill; never crosses into PSY domains (no psychological prediction, defense mechanism forecasting, or psychological change projection)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Dự báo lộ trình sự nghiệp 3–5 năm tới dựa trên dữ liệu hiện tại (giai đoạn, kỹ năng, mô hình học tập, học vấn). Tất cả đầu ra đều được đánh dấu [FORECAST — NOT FACTUAL].

**Khi nào dùng:** Sau khi `gro:career-path` và `gro:competency-map` đã cung cấp dữ liệu cơ sở. Dùng để khám phá các kịch bản "nếu như".

**Không làm được:** Không phải sự thật; chỉ là phỏng đoán. Không gợi ý hành động. Không vượt biên giới PSY.
