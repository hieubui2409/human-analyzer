# orc:graph

> Search the character-corpus knowledge graph for related files and relationships.

## What it does

Query the markdown-derived knowledge graph to find files related to a character or theory, inspect graph stats, validate integrity. Thin wrapper over `platform_lib.knowledge_graph`. No external dependencies (no networkx/numpy). Disposable graph—rebuilt lazily on first call.

## When to use

- **Exploration/navigation** — which files relate to this character or theory?
- **Relationship discovery** — cross-character links, theory citations, dyad members
- **Health snapshot** — node/edge counts, orphan detection
- Trigger phrases: "graph context", "related files", "knowledge graph", "find connections"

## Flags

| Flag | Effect |
|------|--------|
| `query <entity>` | Find files related to entity (character slug, theory, or file path) |
| `--hops <N>` | Hops distance (default: 2) |
| `--types <types>` | Filter node types: profile, material, reference, graph_dyad |
| `stats` | Show graph statistics (nodes, edges, by type) |
| `validate` | Check for missing refs, orphans, broken links |
| `rebuild` | Force rebuild cache |

## What it does NOT do

- Does NOT find exhaustive usage (text-scan scripts are authoritative for that).
- Does NOT validate schema—that's for single-file validators.
- Does NOT modify the knowledge graph—read-only exploration.

## See also

- Contract: [`SKILL.md`](./SKILL.md) · Guide: [`GUIDE-EN.md`](./GUIDE-EN.md) / [`GUIDE-VI.md`](./GUIDE-VI.md)

---

## Tiếng Việt

### Nó làm gì

Truy vấn biểu đồ kiến thức dẫn xuất markdown để tìm các tệp liên quan đến một nhân vật hoặc lý thuyết, kiểm tra thống kê biểu đồ, xác thực tính toàn vẹn. Ổn định mỏng trên `platform_lib.knowledge_graph`. Không phụ thuộc bên ngoài (không networkx/numpy). Biểu đồ có thể loại bỏ—được xây dựng lại một cách lười biếng khi gọi lần đầu.

### Khi nào dùng

- **Khám phá/điều hướng** — những tệp nào liên quan đến nhân vật hoặc lý thuyết này?
- **Phát hiện quan hệ** — liên kết đa nhân vật, trích dẫn lý thuyết, thành viên dyad
- **Ảnh chụp sức khỏe** — số nút/cạnh, phát hiện mồ côi
- Cụm từ kích hoạt: "graph context", "related files", "knowledge graph", "find connections"

### Không làm gì

- **Không tìm** sử dụng toàn diện (các kịch bản quét văn bản là có thẩm quyền).
- **Không xác thực** lược đồ—đó là cho các trình xác thực tệp đơn.
- **Không sửa đổi** biểu đồ kiến thức—khám phá chỉ đọc.
