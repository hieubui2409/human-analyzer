"""Canonical skill-id conversions shared across com:skill-analytics scripts.

A skill has two surface forms that the analytics scripts kept converting ad-hoc
(and in opposite directions): the directory-name form `framework-skill` (e.g.
`com-git`, used as the on-disk catalog key) and the invocation/reference form
`framework:skill` (e.g. `com:git`, how skills are called and logged). Only the
first hyphen/colon is the framework separator, so multi-word skill names
(`com-skill-analytics`) round-trip correctly.
"""


def framework_of(skill: str) -> str:
    """First segment before the framework separator: 'com-git' / 'com:git' → 'com'."""
    return (skill or "").split("-", 1)[0].split(":", 1)[0]


def to_dir_id(skill: str) -> str:
    """Directory-name / catalog-key form: 'com:git' → 'com-git'."""
    return (skill or "").replace(":", "-")


def to_skill_ref(skill: str) -> str:
    """Invocation / reference form: 'com-git' → 'com:git' (first hyphen only)."""
    return (skill or "").replace("-", ":", 1)
