# evl:rubric-import

> Ingest an external evaluation framework and convert it into a canonical EVL rubric DRAFT.

## What it does

Parses an external framework (markdown, JSON, YAML, or freeform text — from a file, stdin, or
pre-fetched URL text), scaffolds a canonical rubric skeleton with TODO placeholders where weights
and anchors are unknown, then spawns the `evl-rubric-importer` sub-agent (input-isolated) to
propose a semantic mapping. The mapping is re-validated by the same gap-detection logic before
an optional write to `docs/rubrics/imported/<id>.yaml`. The draft is stamped `status: draft` and
blocked from scoring until a human fills any remaining gaps and `evl:validate` passes.

## When to use

- **Trigger phrases:** "evl rubric import", "import rubric", "convert framework to rubric", "ingest evaluation framework"
- **Workflow position:** before `evl:validate` and `evl:score`; first stop for any 3rd-party instrument
- **Output user:** anyone who has an external framework (psychometric battery, casting brief, competency model, clinical screen) and wants it scoreable

## Flags

| Flag | Effect |
|------|--------|
| `--input <path>` | Read framework from a file |
| `--stdin` | Read framework from standard input |
| `--fmt md\|json\|yaml\|freeform` | Input format (default `md`) |
| `--id <slug>` | Draft file slug (default: derived from title) |
| `--title <str>` | Override rubric title |
| `--kind decision\|psychometric\|clinical\|dyad` | Rubric kind (default `decision`) |
| `--source <str>` | Provenance string (URL, citation, author) |
| `--write` | Write draft YAML and print path |

## What it does NOT do

- **Not an inventor:** the script never proposes a weight or anchor — gaps are loud by design.
- **Not a network tool:** URL fetching happens via WebFetch in the skill, not in the script.
- **Not a scorer:** a gap-laden draft cannot pass `evl:validate` and therefore cannot be scored.
- **Not a silent filler:** every unclassified source line surfaces in `_import_gaps`, never dropped.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

**Mục đích:** Nhập một framework đánh giá bên ngoài (markdown, JSON, YAML, hoặc văn bản tự do — từ tệp, stdin, hoặc văn bản URL đã lấy trước) và chuyển đổi thành bản thảo rubric chuẩn hoá EVL dưới `docs/rubrics/imported/`. Script chỉ xử lý cấu trúc; ánh xạ ngữ nghĩa do sub-agent `evl-rubric-importer` đảm nhận. Bản thảo còn thiếu sót sẽ bị chặn ở `evl:validate` — không thể chấm điểm cho đến khi con người bổ sung đầy đủ.

**Khi nào dùng:** Trước `evl:validate` và `evl:score`; điểm đến đầu tiên cho bất kỳ công cụ đo lường bên thứ ba nào.

**Không làm được:** Không đề xuất trọng số hay mốc neo (thiếu sót được báo to). Không lấy URL (WebFetch chạy ở cấp skill). Không bỏ qua dòng nguồn chưa phân loại.
