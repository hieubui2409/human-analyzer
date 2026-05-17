#!/bin/bash
# Generate a new clinical reference file template with all mandatory sections.
# Usage: ./generate-reference-file-template.sh <theory-name-kebab-case>
# Output: template content to stdout (caller redirects to file)
# Example: ./generate-reference-file-template.sh attachment-theory

set -euo pipefail

THEORY_SLUG="${1:-}"

if [[ -z "$THEORY_SLUG" ]]; then
    echo "Usage: $0 <theory-name-kebab-case>" >&2
    echo "  Example: $0 attachment-theory" >&2
    echo "  Output is written to stdout — redirect to target file:" >&2
    echo "  $0 attachment-theory > docs/references/attachment-theory.md" >&2
    exit 1
fi

# Convert kebab-case to Title Case for display
THEORY_TITLE=$(echo "$THEORY_SLUG" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) substr($i,2); print}')
TODAY=$(date +%Y-%m-%d)

cat <<EOF
---
title: "${THEORY_TITLE}"
slug: "${THEORY_SLUG}"
category: "[Attachment | Defense Mechanisms | Clinical Intervention | Trauma | Personality | Other]"
created: "${TODAY}"
status: "DRAFT"
---

# ${THEORY_TITLE}

## Definition

> [1-2 sentence clinical definition. Be precise. Use DSM-5/ICD-11 language where applicable.]

**Core construct:** [The essential psychological mechanism this theory describes]

## Key Theorists

- **[Primary theorist name]** — [Brief contribution]
- **[Secondary theorist]** — [Brief contribution]

## Core Mechanisms

### [Mechanism 1 Name]
[Explanation of how this mechanism works]

### [Mechanism 2 Name]
[Explanation of how this mechanism works]

## Behavioral Indicators

Signs this pattern is present in a character:

- [ ] [Observable behavior 1]
- [ ] [Observable behavior 2]
- [ ] [Observable behavior 3]

## Character Application

### Show-Don't-Tell Translation

| Clinical Term | Narrative Expression |
|---------------|---------------------|
| [term] | [how it shows in behavior/dialogue] |
| [term] | [how it shows in behavior/dialogue] |

### Relevant Character Profiles

- **Nhân vật A (character-a):** [How this theory applies, or "N/A"]
- **Nhân vật B (character-b):** [How this theory applies, or "N/A"]
- **Nhân vật C (character-c):** [How this theory applies, or "N/A"]

## Interaction With Other Theories

- Links to: [theory-slug-1], [theory-slug-2]
- Contrasts with: [theory-slug]
- Often co-occurs with: [theory-slug]

## Clinical Citations

- [Author, Year. *Title*. Publisher.]
- [DSM-5 / ICD-11 reference if applicable]

## Content Creation Notes

> Guidelines for referencing this theory in social media content without exposing raw clinical terms.

- Safe framing: "[Example of how to write about this implicitly]"
- Avoid: "[Terms too clinical for public content]"
- Audience-appropriate language: "[Alternative phrasing]"

---

*Added: ${TODAY} | Status: DRAFT | Reviewer: [name]*
EOF
