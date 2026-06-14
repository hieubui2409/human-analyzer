# evl:compatibility

> Score a pair of characters against a versioned, evidence-cited dyad rubric — the EVL dyad engine.

## What it does

Validates a dyad rubric, gathers per-criterion candidate evidence pooled from BOTH characters'
profile files, has the LLM judge each criterion (with a mandatory MAT evidence-tier citation),
aggregates the verified scores into a weighted overall score with a verdict, and writes a
standardized dyad scorecard (markdown + JSON) under `docs/profiles/{char-a}/eval/` with the
partner slug in the filename. The default rubric (`relationship-compatibility`) implements Gottman's
Four Horsemen + repair + 5:1 ratio + ECR-R attachment pairing + similarity/complementarity.

## When to use

- **Trigger phrases:** "evl compatibility", "score compatibility", "rate compatibility between", "how compatible are", "compatibility between characters"
- **Workflow position:** after MAT/PSY have populated both profiles (especially `relationships/*.md` and `psychology/attachment-style.md`); feeds `EVL.scored` → CRE
- **Output user:** anyone needing a defensible, evidence-cited compatibility assessment of a pair

## Flags

| Flag | Effect |
|------|--------|
| `--character-a <name>` | First character in the pair (dynamic resolution) |
| `--character-b <name>` | Second character in the pair (dynamic resolution) |
| `--rubric <id>` | Dyad rubric id or path (default: `relationship-compatibility`) |
| `--scores <json>` | Path to judge scores JSON (finalize only) |
| `--asof <YYYY-MM-DD>` | ISO date for the scorecard (finalize only) |

## Verdict Bands

| Band | Score |
|------|-------|
| Incompatible | < 2.0 |
| At-Risk | 2.0 – 3.0 |
| Compatible | 3.0 – 4.0 |
| Highly-Compatible | ≥ 4.0 |

## What it does NOT do

- **Not a judgment-in-script tool:** the script gathers + aggregates; the LLM judges each criterion. No scoring heuristic lives in the script.
- **Not a silent pass:** an uncited criterion is `[UNVERIFIED]` (excluded + counted), not a guessed score.
- **Not for single-subject rubrics:** rubric must carry `subject: dyad` — any other kind raises immediately.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Chấm điểm một cặp nhân vật theo một rubric dyad có phiên bản, trích dẫn bằng chứng. Script gộp bằng chứng từ CẢ HAI nhân vật và tổng hợp trọng số; LLM chấm từng tiêu chí và bắt buộc trích dẫn tầng bằng chứng MAT (T1–T5). Xuất scorecard chuẩn (markdown + JSON) dưới `docs/profiles/{char-a}/eval/` với slug của đối tác trong tên tệp.

**Khi nào dùng:** Sau khi MAT/PSY đã dựng hồ sơ cả hai nhân vật (đặc biệt `relationships/*.md` và `psychology/attachment-style.md`); kết quả phát `EVL.scored` → CRE.

**Không làm được:** Không chấm điểm trong script (LLM chấm). Tiêu chí không trích dẫn → `[UNVERIFIED]`, không bao giờ pass ngầm. Chỉ dùng rubric có `subject: dyad` — loại khác báo lỗi ngay.
