#!/usr/bin/env python3
"""release_notes — deterministic, PII-clean RELEASE-NOTES generator.

Walks the LIVE toolkit tree (skills, framework agents/hooks, platform_lib, rules, schemas) and emits the
exhaustive release-notes catalog whose contents are generated, not hand-typed, so it stays correct as the
toolkit grows:
  * docs/RELEASE-NOTES-v<ver>.md — exhaustive enumeration (every skill/agent/hook/lib/rule)

The human-facing "what changed" narrative lives in the hand/LLM-maintained root ``CHANGELOG.md``
(Keep a Changelog + an [Unreleased] section), managed by ``release.py`` — NOT regenerated here,
so nothing reads git-at-build-time and the committed file is never clobbered by a later run.

DETERMINISM: no wall-clock — the release date is an explicit argument; every list is sorted. Same tree
+ same (version, date) ⇒ byte-identical output.

PRIVACY: the rendered notes are scanned with the same collision-free token set as scan_pack_pii and
asserted PII-clean before returning (a leak raises, failing the release).
"""
import argparse
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]  # scripts → _framework-shared → skills → .claude → repo
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pii_tokens  # noqa: E402  (sibling in _framework-shared/scripts)
import scan_pack_pii  # noqa: E402  (sibling in _framework-shared/scripts)

try:
    import yaml
except ImportError:
    yaml = None

FRAMEWORKS = [
    ("orc", "ORC — Orchestration"),
    ("psy", "PSY — Psychology"),
    ("cre", "CRE — Content Creation"),
    ("gro", "GRO — Growth"),
    ("mat", "MAT — Materials"),
    ("com", "COM — Common"),
]
FRONTMATTER = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


def _frontmatter(md_path: Path) -> dict:
    m = FRONTMATTER.search(md_path.read_text(encoding="utf-8"))
    if not m or yaml is None:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _first_sentence(text: str, limit: int = 160) -> str:
    text = " ".join((text or "").split())
    text = re.split(r"(?<=[.!?])\s", text)[0] if text else ""
    return (text[:limit] + "…") if len(text) > limit else text


def _humanize(stem: str) -> str:
    return stem.replace("-", " ").replace("_", " ").strip().capitalize()


def collect() -> dict:
    """Gather the full catalog from the live tree (sorted, deterministic)."""
    data = {"frameworks": []}
    for fw, title in FRAMEWORKS:
        skills = []
        for skill_dir in sorted((REPO / ".claude" / "skills").glob(f"{fw}-*")):
            sk = skill_dir / "SKILL.md"
            if not sk.exists():
                continue
            fm = _frontmatter(sk)
            skills.append({
                "name": fm.get("name", skill_dir.name),
                "purpose": _first_sentence(fm.get("description", "")),
            })
        data["frameworks"].append({"key": fw, "title": title, "skills": skills})

    data["agents"] = []
    for name in sorted(scan_pack_pii._FRAMEWORK_AGENTS):
        ap = REPO / ".claude" / "agents" / name
        if ap.exists():
            fm = _frontmatter(ap)
            data["agents"].append({"name": name[:-3], "purpose": _first_sentence(fm.get("description", ""))})

    data["hooks"] = []
    for rel in sorted(f for f in scan_pack_pii._FRAMEWORK_HOOK_FILES if not f.startswith("lib/")):
        hp = REPO / ".claude" / "hooks" / rel
        purpose = ""
        if hp.exists():
            for line in hp.read_text(encoding="utf-8").splitlines()[:6]:
                s = line.strip().lstrip("/*").strip()
                if s and not s.startswith("#!") and "require(" not in s and "function" not in s:
                    purpose = _first_sentence(s)
                    break
        data["hooks"].append({"name": rel[:-4], "purpose": purpose or _humanize(rel[:-4])})

    data["lib"] = []
    for py in sorted((REPO / ".claude" / "scripts" / "platform_lib").glob("*.py")):
        if py.name == "__init__.py":
            continue
        doc = ""
        m = re.search(r'"""(.*?)"""', py.read_text(encoding="utf-8"), re.DOTALL)
        if m:
            doc = _first_sentence(m.group(1))
        data["lib"].append({"name": py.name, "purpose": doc or _humanize(py.stem)})

    data["rules"] = []
    for rule in sorted((REPO / "docs" / "rules").glob("*.md")):
        head = ""
        for line in rule.read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                head = line.lstrip("#").strip()
                break
        data["rules"].append({"file": rule.name, "title": head or _humanize(rule.stem)})

    data["schemas"] = sorted(p.name for p in (REPO / ".claude" / "schemas").glob("*"))
    return data


def _counts(data: dict) -> dict:
    return {
        "skills": sum(len(f["skills"]) for f in data["frameworks"]),
        "frameworks": len(data["frameworks"]),
        "agents": len(data["agents"]),
        "hooks": len(data["hooks"]),
        "lib": len(data["lib"]),
        "rules": len(data["rules"]),
        "schemas": len(data["schemas"]),
    }


def render_release_notes(data: dict, version: str, date: str) -> str:
    c = _counts(data)
    L = [
        f"# Release Notes — frameworks v{version}",
        "",
        f"_Released {date}. Clinical-grade character-profile intelligence toolkit — "
        f"{c['frameworks']} frameworks · {c['skills']} skills · {c['agents']} domain agents · "
        f"{c['hooks']} framework hooks · {c['lib']} platform-lib modules · {c['rules']} rules._",
        "",
        "> Privacy: this toolkit ships ZERO character profiles, materials, graph, or references — "
        "the entire real-character corpus is pack-excluded. The released tarball is byte-reproducible "
        "and passes a fail-closed whole-pack PII/secret scan with no carve-out.",
        "",
        "## Highlights",
        "- **Character roster externalised (code → data):** the roster moved out of `paths.py` into a "
        "pack-excluded `docs/profiles/characters.yaml`; the public `paths.py` API is unchanged.",
        "- **New-character registration + drift invariant:** scaffolding auto-registers a character; an "
        "invariant fails on any roster↔profile mismatch.",
        "- **PII-safe pack:** real names (display, full, romanised slug) + org/location extras live only in "
        "the excluded corpus; docs/tests/tools are name-free; a deterministic build + whole-pack scan gate it.",
        "- **Framework-owned pack:** manifest ships only the 6 domain agents + 6 framework hooks (settings.json "
        "is filtered to wire exactly those); an independent scanner ratchet rejects any non-framework agent/hook.",
        "",
        "## Framework & Skill Catalog",
    ]
    for f in data["frameworks"]:
        L.append(f"\n### {f['title']} ({len(f['skills'])} skills)\n")
        for s in f["skills"]:
            L.append(f"- **`{s['name']}`** — {s['purpose']}")
    L.append("\n## Domain Agents\n")
    for a in data["agents"]:
        L.append(f"- **{a['name']}** — {a['purpose']}")
    L.append("\n## Framework Hooks\n")
    for h in data["hooks"]:
        L.append(f"- **{h['name']}** — {h['purpose']}")
    L.append("\n## Platform Library (`platform_lib`)\n")
    for m in data["lib"]:
        L.append(f"- **{m['name']}** — {m['purpose']}")
    L.append("\n## Rules\n")
    for r in data["rules"]:
        L.append(f"- **{r['file']}** — {r['title']}")
    L.append("\n## Schemas\n")
    for s in data["schemas"]:
        L.append(f"- `{s}`")
    L.append("\n_See the root `CHANGELOG.md` for the human-curated list of changes in this release._")
    L.append("")
    return "\n".join(L)


def _assert_pii_clean(*texts: str) -> None:
    tokens = pii_tokens.scan_tokens()
    for text in texts:
        hits = scan_pack_pii.scan_text("changelog", text, tokens)
        if hits:
            raise SystemExit(f"❌ changelog would leak PII: {hits[:5]}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate the deterministic, PII-clean RELEASE-NOTES catalog.")
    ap.add_argument("--version", required=True)
    ap.add_argument("--date", required=True, help="release date YYYY-MM-DD (explicit for determinism)")
    ap.add_argument("--check", action="store_true", help="validate + assert PII-clean, do not write files")
    args = ap.parse_args()

    data = collect()
    notes = render_release_notes(data, args.version, args.date)
    _assert_pii_clean(notes)

    if args.check:
        c = _counts(data)
        print(f"✅ release-notes validate — {c['skills']} skills / {c['frameworks']} fw / {c['agents']} agents "
              f"/ {c['hooks']} hooks / {c['rules']} rules; PII-clean.")
        return 0

    (REPO / "docs" / f"RELEASE-NOTES-v{args.version}.md").write_text(notes, encoding="utf-8")
    print(f"wrote docs/RELEASE-NOTES-v{args.version}.md (PII-clean).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
