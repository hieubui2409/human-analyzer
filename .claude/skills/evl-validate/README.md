# evl:validate

> Deterministic structural checker for EVL rubrics and scorecards — the honesty gate before scoring or consuming results.

## What it does

Two modes, zero heuristics:

**RUBRIC mode** (`--rubric <id|path>` or `--all`): validates a rubric's shape (JSON-Schema Draft-7) plus cross-field invariants — weight sums, high-stakes judge floor, clinical rails, threshold coverage, anchor endpoints. Prints each error with rubric id prefix; exits non-zero on any failure.

**SCORECARD mode** (`--scorecard <json> --rubric <id|path>`): runs the full checker registry (`rubric_schema_valid` · `criteria_mapped` · `every_criterion_cited` · `weight_sum_unity` · `aggregate_math_correct` · `score_in_bounds` · `verdict_thresholds_cover_range`) and prints a per-checker verdict table (PASS / FAIL / SKIP / UNMAPPED) with a final summary. Add `--strict` to treat UNMAPPED criteria as FAIL.

## When to use

- **Trigger phrases:** "evl validate", "validate rubric", "check scorecard", "evl check"
- **Workflow position:** (1) after authoring a rubric — before any character is scored; (2) before consuming a scorecard — before CRE or external output
- **Output user:** anyone who needs a rubric or scorecard to be trustworthy before acting on it

## Flags

| Flag | Effect |
|------|--------|
| `--rubric <id\|path>` | Rubric to validate |
| `--all` | Validate all `docs/rubrics/*.yaml` |
| `--scorecard <path>` | Scorecard JSON to validate (requires `--rubric`) |
| `--strict` | UNMAPPED → FAIL instead of loud-but-non-fatal |
| `--json` | Machine-readable output |

## What it does NOT do

- **Not a scoring tool:** no character, no evidence, no judgment — purely structural.
- **Not auto-fixing:** prints findings; all remediation is manual.
- **Not LLM-driven:** every check is algebraic; no Agent step, no network.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Hai chế độ, không heuristic. RUBRIC: xác thực hình dạng + bất biến chéo-trường của rubric (tổng trọng số, sàn giám khảo rủi ro cao, rail lâm sàng, phủ ngưỡng, điểm neo). SCORECARD: chạy toàn bộ registry kiểm tra và in bảng verdict (PASS / FAIL / SKIP / UNMAPPED) kèm tóm tắt cuối.

**Khi nào dùng:** Sau khi viết rubric (trước khi chấm bất kỳ nhân vật nào); trước khi tiêu thụ scorecard (trước CRE hoặc đầu ra ngoài).

**Không làm được:** Không chấm điểm. Không tự sửa. Không dùng LLM — mọi kiểm tra đều là đại số.
