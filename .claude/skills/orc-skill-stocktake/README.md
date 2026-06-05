# orc:skill-stocktake

> Audit the project skill catalog for overlap, gaps, and conformance.

## What it does

Quick Scan counts skills per framework vs CLAUDE.md, detects metadata gaps, finds catalog drift. Full Stocktake analyzes pairwise overlap/gaps, assigns verdicts (KEEP/ENHANCE/CONSOLIDATE/RETIRE). Conformance audit checks code size, structure, reference quality. Read-only analysis—never modifies SKILL.md.

## When to use

- **After adding/renaming skills** — catch count drift early
- **Quarterly catalog review** — detect overlap/bloat
- **Before release** — ensure skill catalog is clean
- **Conformance checking** — verify skills follow structural rules
- Trigger phrases: "skill stocktake", "skill audit", "catalog audit", "skill overlap"

## Flags

| Flag | Effect |
|------|--------|
| `--quick` | Count + metadata + CLAUDE.md reconciliation |
| `--full` | Overlap + gap + usage analysis (LLM verdict) |
| `--conformance` | Check code size, structure, reference quality |
| `--ce02` | Conformance gate (strict) |
| `--framework <fw>` | Filter to one framework (orc, psy, cre, gro, mat, com) |
| `--report` | Save audit report to file |

## What it does NOT do

- Does NOT modify SKILL.md—only reports findings.
- Does NOT execute recommendations—suggests KEEP/CONSOLIDATE/RETIRE.
- Does NOT auto-prune—changes require manual review.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Quick Scan đếm các kỹ năng cho mỗi khung so với CLAUDE.md, phát hiện khoảng cách siêu dữ liệu, tìm drift danh mục. Full Stocktake phân tích sự chồng chéo/khoảng cách pairwise, gán các phán quyết (KEEP/ENHANCE/CONSOLIDATE/RETIRE). Kiểm tra phù hợp kiểm tra kích thước mã, cấu trúc, chất lượng tham chiếu. Phân tích chỉ đọc—không bao giờ sửa đổi SKILL.md.

### Khi nào dùng

- **Sau khi thêm/đổi tên kỹ năng** — bắt drift đếm sớm
- **Kiểm tra danh mục hàng quý** — phát hiện chồng chéo/bloat
- **Trước phát hành** — đảm bảo danh mục kỹ năng sạch
- **Kiểm tra phù hợp** — xác minh các kỹ năng tuân theo quy tắc cấu trúc
- Cụm từ kích hoạt: "skill stocktake", "skill audit", "catalog audit", "skill overlap"

### Không làm gì

- **Không sửa đổi** SKILL.md—chỉ báo cáo phát hiện.
- **Không thực hiện** khuyến nghị—gợi ý KEEP/CONSOLIDATE/RETIRE.
- **Không tự động cắt tỉa**—thay đổi yêu cầu xem xét thủ công.
