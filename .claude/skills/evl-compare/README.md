# evl:compare

> Rank characters against each other on the same rubric — deterministic, no LLM judging.

## What it does

Loads each character's existing scorecard for a given rubric, ranks them by raw overall score,
and attaches peer-relative z-score + percentile (suppressed with a note when the cohort is < 3).
Characters with no scorecard are listed as `missing` — loudly, never dropped, never treated as
zero. Outputs a ranked markdown table or JSON.

## When to use

- **Trigger phrases:** "evl compare", "rank characters on rubric", "compare characters", "cross-character ranking"
- **Workflow position:** after `evl:score` has produced scorecards for each character you want to compare
- **Output user:** anyone needing a peer-relative view across the character roster on one rubric

## Flags

| Flag | Effect |
|------|--------|
| `--rubric-id <id>` | Rubric id matching scorecard filenames under `docs/profiles/{char}/eval/` |
| `--characters a,b,c` | Comma-separated subset (dynamic resolution); default = all characters |
| `--json` | Machine-readable comparison result |

## What it does NOT do

- **No LLM judgment:** scores must already exist — run `evl:score` first.
- **No score imputation:** missing scorecard = loud gap, not a zero.
- **No z-score for tiny cohorts:** suppressed (with a note) when cohort < 3.
- **No writes:** comparison is ephemeral; it does not persist a scorecard.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Xếp hạng các nhân vật với nhau trên cùng một rubric, sử dụng các scorecard đã có sẵn.
Hoàn toàn xác định — không có bước LLM chấm điểm. Điểm phải tồn tại trước (do `evl:score` tạo ra).
Nhân vật thiếu scorecard được liệt kê nổi bật trong `missing` — không bao giờ bị bỏ qua ngầm.

**Khi nào dùng:** Sau khi `evl:score` đã tạo scorecard cho từng nhân vật cần so sánh.

**Không làm được:** Không chấm điểm (LLM không tham gia). Thiếu scorecard → hiển thị rõ ràng,
không điền số 0. z-score bị nén khi nhóm < 3 nhân vật. Không ghi file nào.
