# psy:wave

> Orchestrate 3-wave profile generation pipeline (Foundation→Deep Dive→Validation). Use for new characters or major profile updates.

## What it does

Orchestrates the complete profile build: **Wave 1** (Foundation): extract identity, timeline, relationships from materials. **Wave 2** (Deep Dive): analyze psychology, wounds, coping, voice. **Wave 3** (Validation): cross-character consistency via psy:crossref + psy:ref-audit, apply fixes, cascade to connected characters via psy:propagate. Each wave has a gate; fails at gate → stop, report missing work before proceeding to next wave.

## When to use

- Creating new character profile from scratch
- Major profile updates (≥3 files affected)
- Integrating significant new source materials (crisis events, relationship reveals, transcripts)
- NOT for single-fact additions or minor corrections (edit directly)

## Flags

| Flag                 | Effect |
|----------------------|--------|
| `--wave <1\|2\|3>`   | Execute specific wave only |
| `--character <name>` | Target character (required) |
| `--all`              | Run all 3 waves sequentially with gates |
| `--status`           | Show current wave progress |
| `--plan <path>`      | Link to existing plan file for context |

## What it does NOT do

- Does NOT replace manual editing (toolkit, not replacement)
- Does NOT skip Wave 3 validation (mandatory)
- Does NOT modify cross-character files without user confirmation
- Does NOT force updates (recommends, user decides)

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)
- Rule 05: [`docs/rules/05-wave-pipeline.md`](../../rules/05-wave-pipeline.md)

---

## Tiếng Việt

**Điều phối đường ống tạo hồ sơ 3 sóng** (Foundation→Deep Dive→Validation). Sử dụng cho các nhân vật mới hoặc cập nhật hồ sơ lớn.

**Khi nào sử dụng:** Tạo hồ sơ nhân vật mới, cập nhật lớn, hoặc tích hợp các vật liệu nguồn quan trọng.
