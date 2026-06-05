# orc:council

> 4-voice decision framework for ambiguous situations with anti-anchoring isolation.

## What it does

Spawns 4 independent subagents (Advocate, Skeptic, Pragmatist, Wildcard) to argue a decision question from different angles. Each receives only the question + their role, no context from others. Synthesizes verdicts and stores in decision records. Use for clinically ambiguous interpretations, content direction disputes, or cross-character framing conflicts.

## When to use

- **Clinical ambiguity** — conflicting valid interpretations of behavior (is this avoidance or anxious attachment?)
- **Content direction unclear** — multiple valid angles for a story
- **Career trajectory disputes** — plausible but different paths forward
- **Cross-character dynamics** — relationship framing disagreements
- Trigger phrases: "council", "council vote", "4 voices", "ambiguous decision"

## Flags

| Flag | Effect |
|------|--------|
| `--question "<text>"` | Decision question (max 500 chars) |
| `--category <psy\|cre\|gro\|cross>` | Domain category |
| `--character <name>` | Character name or "cross" (default) |

## What it does NOT do

- Does NOT execute the decision—only gathers perspectives and synthesizes.
- Does NOT modify files—council is decision-gathering, not implementation.
- Does NOT auto-trigger—always manual invocation; never auto-spawned during work.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Sinh ra 4 tác nhân con độc lập (Advocate, Skeptic, Pragmatist, Wildcard) để tranh luận một câu hỏi quyết định từ các góc độ khác nhau. Mỗi cái chỉ nhận được câu hỏi + vai trò của họ, không có ngữ cảnh từ những cái khác. Tổng hợp phán quyết và lưu trữ trong hồ sơ quyết định. Dùng cho các cách giải thích lâm sàng mơ hồ, tranh chấp hướng nội dung, hoặc xung đột khung động quan hệ đa nhân vật.

### Khi nào dùng

- **Tính mơ hồ lâm sàng** — các cách giải thích hợp lệ xung đột của hành vi
- **Hướng nội dung không rõ** — các góc độ hợp lệ cho một câu chuyện
- **Tranh chấp quỹ đạo sự nghiệp** — các con đường khả thi nhưng khác nhau phía trước
- **Động lực đa nhân vật** — bất đồng về khung động quan hệ
- Cụm từ kích hoạt: "council", "council vote", "4 voices", "ambiguous decision"

### Không làm gì

- **Không thực hiện** quyết định—chỉ thu thập các quan điểm và tổng hợp.
- **Không sửa đổi** tệp—hội đồng là thu thập quyết định, không phải triển khai.
- **Không tự động kích hoạt**—luôn gọi thủ công; không bao giờ tự động sinh ra trong công việc.
