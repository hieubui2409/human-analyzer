---
name: psy:propagate
description: "Cross-character cascade analysis — when a profile section changes, detect which connected characters and profile files need review. Uses graph/relational-dynamics.md to trace dependencies. Triggers: 'propagate changes', 'cascade update', 'cross-character sync', 'propagate profile update'."
argument-hint: "[--character <name>] [--section <section>] [--json]"
metadata:
  author: hieubt
  version: "1.0.0"
  category: "psy-framework"
  position: "post-update"
  dependencies: []
---

# psy:propagate — Cross-Character Change Cascade

After updating one character's profile, detect which connected characters and profile sections may need corresponding updates.

## Default (No Arguments)

Prompt for character selection, then scan all connections.

## Flags

| Flag                  | Purpose                                          |
| --------------------- | ------------------------------------------------ |
| `--character <name>`  | Source character whose profile changed           |
| `--section <section>` | Specific profile section that changed (optional) |
| `--json`              | Output as JSON                                   |

## Relationship Graph

The propagation map is derived from `docs/graph/relational-dynamics.md`:

| Pair         | Connection Type            | Propagation Risk  |
| ------------ | -------------------------- | ----------------- |
| Nhân vật A ↔ Nhân vật B   | Sworn brothers (kết nghĩa) | HIGH — tight bond |
| Nhân vật A ↔ Nhân vật C | Mentor-mentee (Scholarship X)  | MEDIUM            |
| Nhân vật B ↔ Nhân vật C  | Indirect via Nhân vật A          | LOW               |

## Section Propagation Map

When a section changes in the source character, these sections in connected characters may need review:

| Source Section Changed         | Connected Character — Section to Review |
| ------------------------------ | --------------------------------------- |
| relationships/family.md        | All → relationships/family.md           |
| timeline/overview.md           | All → timeline/overview.md              |
| psychology/attachment-style.md | Connected → relationships/family.md     |
| psychology/core-wounds.md      | Connected → relationships/family.md     |
| CURRENT-STATE.md               | Connected → relationships/family.md     |
| identity/core.md               | All → INDEX.md, identity/core.md        |

> Cross-character relationship files (e.g. `relationships/character-b.md`) also carry mirror propagation — discovered dynamically via `list_relationship_files()`.

## Workflow

### Step 1: Load Graph

1. Read `docs/graph/relational-dynamics.md`
2. Identify which characters are connected to the source character
3. Determine connection strength (high/medium/low)

### Step 2: Detect Targets

1. Run `scripts/detect-propagation-targets-from-profile-diff.py --character <slug>`
2. For each connected character: map source section → affected sections in target
3. Output {character, file, reason, priority} tuples

### Step 3: Output

```
## Propagation Analysis: {Character}

**Source:** {character}
**Changed section:** {section or "unspecified — all sections"}

### Propagation Targets

| Priority | Target Character | File                       | Reason                                  |
|----------|-----------------|----------------------------|-----------------------------------------|
| HIGH     | Nhân vật B              | relationships/family.md    | Sworn brother — direct relationship ref |
| MEDIUM   | Nhân vật C            | timeline/overview.md       | Shared event timeline                   |
...

### Recommended Actions

1. Update {file} in {character}: {specific reason}
...

### Next Step
→ Run `psy:crossref --pair {source} {target}` to validate after updates
```

## Scripts

| Script                                                    | Purpose                                  |
| --------------------------------------------------------- | ---------------------------------------- |
| `scripts/detect-propagation-targets-from-profile-diff.py` | Map changed character → affected targets |

## Safety

- READ-ONLY — never modifies profile files
- Domain boundary: `docs/profiles/` + `docs/graph/` (read only)

## Examples

```bash
/psy:propagate --character hieu                          # what needs updating after Nhân vật A change
/psy:propagate --character hoa --section relationships   # Nhân vật B relationship changes
/psy:propagate --character chien --json                  # machine-readable output
```

## See Also

- `psy:crossref` — validate consistency after propagation
- `psy:timeline-sync` — sync timeline dates across characters
- `docs/graph/relational-dynamics.md` — relationship graph source
