"""Scaffold N platform-NATIVE content variants from one source/angle (deterministic).

GOLDEN RULE #4 split:
  - SCRIPT (here): resolve target platforms, create each assets/{platform}/{slug}/
    package dir, and emit a per-platform `brief.json` carrying the native-structure
    constraints (length, hook model, hashtags, aspect ratio, privacy threshold) +
    the source reference. Pure dir scaffold + constraint lookup. Deterministic.
  - LLM (downstream): writes the NATIVE post.md per platform FROM the brief — not a
    reformat of one master post (research: native ≠ watermarked cross-post). Then runs
    cre:evidence-scanner + cre:voice-audit + cre:privacy-guard per variant; writes the
    publish-ready post only on all-pass, emits CRE.published per written variant.

The privacy_threshold per platform (from platform_constraints) drives how strict the
downstream privacy-guard runs: LinkedIn strict (employer/colleague names), blog permissive.

Usage:
  generate-native-variants-for-platforms.py --source <path|angle.json> \
      --slug <slug> [--platforms active|all|"linkedin,facebook"] [--character <c>] [--json]
Scaffolds dirs + briefs only — never writes final copy (LLM does), never runs gates here.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))

from platform_lib import paths
from platform_lib.platform_constraints import resolve_platforms, get_constraints


def _read_source(source: str) -> dict:
    """Source is either a path to an existing post / angle JSON, or a literal title."""
    p = Path(source)
    if p.exists():
        if p.suffix == ".json":
            data = json.loads(p.read_text(encoding="utf-8"))
            return data if isinstance(data, dict) else {"angles": data}
        return {"source_path": str(p), "source_text": p.read_text(encoding="utf-8")[:2000]}
    return {"source_text": source}


def build_brief(platform: str, slug: str, source: dict, character: str) -> dict:
    """Per-platform native brief the LLM writes copy from."""
    c = get_constraints(platform)
    return {
        "platform": platform,
        "slug": slug,
        "character": character or None,
        "native_structure": c["native_structure"],
        "max_length": c["max_length"],
        "hook_model": c["hook"],
        "hashtags": c["hashtags"],
        "aspect_ratio": c["aspect_ratio"],
        "privacy_threshold": c["privacy_threshold"],
        "source": source,
        "gates_required": ["cre:evidence-scanner", "cre:voice-audit", "cre:privacy-guard"],
        "note": "Write a NATIVE post for THIS platform from the source — do NOT reformat "
                "another platform's post. Run all gates_required; write post.txt only on all-pass.",
    }


def scaffold_variant(platform: str, slug: str, source: dict, character: str,
                     assets_root: Path | None = None, dry_run: bool = False) -> dict:
    root = assets_root or paths.ASSETS
    variant_dir = root / platform / slug
    brief = build_brief(platform, slug, source, character)
    if dry_run:
        return {"platform": platform, "dir": str(variant_dir), "scaffolded": False, "brief": brief}
    (variant_dir / "images").mkdir(parents=True, exist_ok=True)
    (variant_dir / "brief.json").write_text(
        json.dumps(brief, indent=2, ensure_ascii=False), encoding="utf-8")
    # placeholder the LLM fills; gate-passed copy replaces it
    pmd = variant_dir / "post.md"
    if not pmd.exists():
        pmd.write_text(f"<!-- {platform} native draft for '{slug}' — LLM writes from brief.json -->\n",
                       encoding="utf-8")
    return {"platform": platform, "dir": str(variant_dir), "scaffolded": True, "brief": brief}


def generate(source_spec: str, slug: str, platforms_spec: str | None, character: str,
             assets_root: Path | None = None, dry_run: bool = False) -> dict:
    platforms = resolve_platforms(platforms_spec, assets_root)
    source = _read_source(source_spec)
    variants = [scaffold_variant(p, slug, source, character, assets_root, dry_run)
                for p in platforms]
    return {"slug": slug, "character": character or None,
            "platforms": platforms, "variant_count": len(variants), "variants": variants}


def main():
    ap = argparse.ArgumentParser(description="Scaffold native content variants per platform.")
    ap.add_argument("--source", required=True, help="Source post path, angle.json, or literal title")
    ap.add_argument("--slug", help="Asset slug (default: YYMMDD-from-source)")
    ap.add_argument("--platforms", default="active", help="active | all | comma list")
    ap.add_argument("--character", default="")
    ap.add_argument("--dry-run", action="store_true", help="Preview dirs + briefs, write nothing")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    slug = args.slug or f"{datetime.now().strftime('%y%m%d')}-multiplatform"
    out = generate(args.source, slug, args.platforms, args.character, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        verb = "would scaffold" if args.dry_run else "scaffolded"
        print(f"{verb} {out['variant_count']} native variants (slug={slug}):")
        for v in out["variants"]:
            b = v["brief"]
            print(f"  {v['platform']:>10}  privacy={b['privacy_threshold']:<10} → {v['dir']}")


if __name__ == "__main__":
    main()
