"""Generate a reference file template with mandatory schema fields for psy:ref-create."""
import argparse
import sys
from datetime import date


VALID_DOMAINS = [
    "personality", "developmental", "attachment", "trauma", "defense-mechanisms",
    "cognitive", "behavioral", "psychodynamic", "neuropsychology", "social",
    "cultural", "clinical", "positive-psychology", "family-systems",
]


def generate_template(theory_name: str, domain: str = "clinical", author: str = "") -> str:
    """Generate reference markdown with mandatory schema fields."""
    slug = theory_name.lower().replace(" ", "-").replace("'", "").replace("(", "").replace(")", "")
    today = date.today().isoformat()

    return f"""---
reference_id: REF_{slug.upper().replace('-', '_')}
title: "{theory_name}"
domain: {domain}
authors: [{author or '"Author Name"'}]
year: null
type: theory
status: draft
confidence: unverified
tags: [{domain}]
last_updated: {today}
updated_by: psy:ref-create
---

# {theory_name}

## Overview

Brief description of the theory and its relevance to character profiling.

## Key Concepts

- **Concept 1**: Description
- **Concept 2**: Description
- **Concept 3**: Description

## Diagnostic Markers

Observable indicators that this theory applies to a character:

| Marker | Observable Behavior | Profile Section |
|--------|-------------------|-----------------|
| Marker 1 | Behavior description | psychology/formulation.md |
| Marker 2 | Behavior description | psychology/defense-mechanisms.md |

## Therapeutic Implications

How this theory informs understanding and intervention:

- Implication 1
- Implication 2

## Application to Characters

### Character-Specific Notes

- **Nhân vật A**: (applicability notes)
- **Nhân vật B**: (applicability notes)
- **Nhân vật C**: (applicability notes)

## Citations

- Author, A. (Year). *Title*. Publisher. DOI/URL
"""


def main():
    parser = argparse.ArgumentParser(description="Generate reference file template")
    parser.add_argument("theory", help="Theory name (e.g., 'Bowlby Attachment Theory')")
    parser.add_argument("--domain", "-d", default="clinical", choices=VALID_DOMAINS, help="Psychology domain")
    parser.add_argument("--author", "-a", default="", help="Primary author name")
    args = parser.parse_args()

    print(generate_template(args.theory, args.domain, args.author))


if __name__ == "__main__":
    main()
