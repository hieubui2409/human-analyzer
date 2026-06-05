"""scan-content-for-ai-tells — deterministic AI-tell scanner CLI (thin wrapper over the lib).

GOLDEN RULE #4 split:
  - SCRIPT (here, deterministic): run platform_lib.humanizer_patterns.scan over the target
    files and report findings. May OVER-FLAG. No LLM. No text mutation.
  - LLM (downstream, see SKILL.md): judge which findings to act on and perform any --rewrite,
    then re-chain cre:evidence-scanner + cre:privacy-guard + cre:voice-audit.

Corpus guard (Rule 09): --rewrite is permitted ONLY for paths that resolve under assets/
(the CRE write-jail in fs_guard — allowlist, stronger than a corpus denylist). The top --path
AND every file in the rewrite worklist are checked, so a symlink under assets/ pointing into
docs/profiles|materials cannot smuggle a corpus file into the rewrite set. Scanning is always
allowed (flag-only is safe on any path).

Usage:
  scan-content-for-ai-tells.py [--path P] [--character C] [--json] [--strictness S] [--rewrite]
Default --path = assets/. Strictness defaults to the `humanize_strictness` preference.
Exit 0 = clean · 1 = findings (advisory) · 2 = --rewrite refused on a corpus path.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import humanizer_patterns as hp
from platform_lib import preferences
from platform_lib import fs_guard
from platform_lib.paths import ASSETS, PROFILES, MATERIALS

_TEXT_SUFFIXES = {".md", ".txt"}


def resolve_strictness(explicit: str | None) -> str:
    """Explicit flag wins; else read the humanize_strictness preference (default balanced)."""
    if explicit:
        return explicit
    return preferences.load().get("humanize_strictness", hp.DEFAULT_STRICTNESS)


def rewrite_allowed(path: Path) -> bool:
    """Rewrite-eligible iff the path resolves under the CRE write-jail (assets/). Allowlist via
    fs_guard, so `..`/symlink/prefix-lookalike escapes are all rejected (resolve-then-contain)."""
    try:
        fs_guard.assert_under(path, "CRE")
        return True
    except fs_guard.FenceError:
        return False


def is_corpus_path(path: Path) -> bool:
    """True if the path resolves under the PSY/MAT corpus (profiles/materials) — used only to give
    a precise Rule-09 refusal reason; the actual gate is the assets/ allowlist (rewrite_allowed)."""
    resolved = path.resolve()
    for root in (PROFILES, MATERIALS):
        r = root.resolve()
        if resolved == r or resolved.is_relative_to(r):
            return True
    return False


def gather_files(path: Path) -> list[Path]:
    """Text files under `path` (recursive), or the single file if `path` is a file."""
    if path.is_file():
        return [path] if path.suffix.lower() in _TEXT_SUFFIXES else []
    if not path.exists():
        return []
    return sorted(p for p in path.rglob("*") if p.is_file() and p.suffix.lower() in _TEXT_SUFFIXES)


def scan_path(path: Path, strictness: str, rewrite: bool = False) -> dict:
    files = gather_files(path)
    file_reports = []
    total = 0
    for f in files:
        try:
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        findings = hp.scan(text, lang="auto", strictness=strictness)
        total += len(findings)
        if findings:
            report = {"file": str(f), "finding_count": len(findings), "findings": findings}
            if rewrite:
                # Per-file allowlist: a symlink under assets/ resolving into the corpus is NOT
                # rewrite-eligible even though the top path passed (closes the worklist hole).
                report["rewrite_eligible"] = rewrite_allowed(f)
            file_reports.append(report)
    return {
        "path": str(path), "strictness": strictness,
        "file_count": len(files), "finding_count": total,
        "files": file_reports,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Deterministic AI-tell scanner over content files.")
    ap.add_argument("--path", default=str(ASSETS), help="File or dir to scan (default: assets/)")
    ap.add_argument("--character", help="Advisory label only (scanner is character-agnostic)")
    ap.add_argument("--strictness", choices=["high", "balanced", "conservative"],
                    help="Override the humanize_strictness preference")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--rewrite", action="store_true",
                    help="Mark findings as an LLM rewrite worklist (assets/ only; refused on corpus)")
    args = ap.parse_args()

    path = Path(args.path)
    strictness = resolve_strictness(args.strictness)

    # Rule-09 allowlist guard: rewrite permitted ONLY under assets/ (the CRE write-jail).
    if args.rewrite and not rewrite_allowed(path):
        reason = "rule09_corpus_no_rewrite" if is_corpus_path(path) else "rewrite_assets_only"
        msg = {"path": str(path), "rewrite": False, "refused": True, "reason": reason,
               "note": "rewrite is permitted only under assets/ (Rule 09); scan is flag-only anywhere"}
        if args.json:
            print(json.dumps(msg, ensure_ascii=False, indent=2))
        else:
            print(f"REFUSED: --rewrite on {path} — only assets/ is rewritable (Rule 09). Scan instead.",
                  file=sys.stderr)
        return 2

    result = scan_path(path, strictness, rewrite=bool(args.rewrite))
    result["rewrite"] = bool(args.rewrite)
    result["character"] = args.character

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"\n  Scan: {result['path']}  (strictness={strictness}, files={result['file_count']})")
        print(f"  Findings: {result['finding_count']}\n")
        for fr in result["files"]:
            held = "" if fr.get("rewrite_eligible", True) else "  [HELD: resolves into corpus, not rewritable]"
            print(f"  • {fr['file']}  ({fr['finding_count']}){held}")
            for fnd in fr["findings"]:
                s, e = fnd["span"]
                snippet = (fnd["match"][:48] or fnd["category"]).replace("\n", " ")
                print(f"      [{fnd['severity']:<6}] {fnd['category']:<18} @{s:<5} {snippet}")
        if args.rewrite and result["finding_count"]:
            print("\n  --rewrite: findings in rewrite-eligible files are the LLM rewrite worklist "
                  "(corpus-resolving files are HELD, flag-only).")

    return 1 if result["finding_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
