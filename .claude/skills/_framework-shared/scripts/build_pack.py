#!/usr/bin/env python3
"""build_pack — deterministic, reproducible tarball of the 7-framework toolkit.

Same source + manifest ⇒ byte-identical `.tar.gz` (PAX, sorted walk, mtime=0, uid/gid=0, uname/gname="",
gzip mtime=0). Ships the toolkit (skills + platform_lib + rules + schemas + shared refs + docs guides + the
synthetic e2e fixture), NEVER the live character corpus or secrets (enforced by safety_filter as a hard
backstop after the include globs). Emits a per-file SHA256 MANIFEST.json embedded in the archive.

Usage:
  build_pack.py                 build dist/<name>-v<version>.tar.gz, print its sha256
  build_pack.py --verify        build twice in memory, assert byte-identical (determinism gate)
  build_pack.py --source-date-epoch N   override mtime (release CI passes the tag date)
"""

import argparse
import gzip
import hashlib
import io
import json
import re
import sys
import tarfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import safety_filter  # noqa: E402

try:
    import yaml
except ImportError:  # keep the determinism path usable without pyyaml in odd envs
    yaml = None

REPO = Path(__file__).resolve().parents[4]  # scripts → _framework-shared → skills → .claude → repo
MANIFEST_YAML = REPO / ".claude" / "pack.manifest.yaml"

_DEFAULT_INCLUDE = [
    ".claude/skills/orc-*/**/*", ".claude/skills/psy-*/**/*", ".claude/skills/cre-*/**/*",
    ".claude/skills/gro-*/**/*", ".claude/skills/mat-*/**/*", ".claude/skills/com-*/**/*",
    ".claude/skills/evl-*/**/*",
    ".claude/skills/_framework-shared/**/*",
    ".claude/scripts/**/*", ".claude/schemas/**/*",
    "docs/rules/**/*", "docs/references/**/*",
    "tests/**/*", "e2e/**/*",
    "CLAUDE.md", "README.md", "STANDARDIZE.md", "pyproject.toml",
    ".github/workflows/frameworks-ci.yml", ".github/workflows/cross-framework-bug-class.yml",
]


def _load_manifest() -> dict:
    if MANIFEST_YAML.exists() and yaml is not None:
        data = yaml.safe_load(MANIFEST_YAML.read_text(encoding="utf-8")) or {}
    else:
        data = {}
    data.setdefault("version", "0.1.0")
    data.setdefault("name", "human-analyzer-frameworks")
    data.setdefault("include", _DEFAULT_INCLUDE)
    return data


def _selection(manifest: dict) -> list[tuple[Path, str]]:
    """[(src_path, arcname), ...] sorted by arcname — include globs minus the safety backstop, files only."""
    seen: dict[str, Path] = {}
    for pattern in manifest["include"]:
        for p in REPO.glob(pattern):
            if not p.is_file() or p.is_symlink():
                continue
            arc = p.relative_to(REPO).as_posix()
            dropped, _ = safety_filter.is_dropped(arc)
            if dropped:
                continue
            seen[arc] = p
    return [(seen[a], a) for a in sorted(seen)]


def _framework_hook_basenames(manifest: dict) -> set:
    """The explicit `.claude/hooks/*.cjs` entries in the manifest = the hooks the pack actually ships."""
    return {Path(p).name for p in manifest.get("include", [])
            if p.startswith(".claude/hooks/") and p.endswith(".cjs") and "*" not in p}


# A hook command invokes its script by path, e.g. `node "$CLAUDE_PROJECT_DIR"/.claude/hooks/foo.cjs`.
# Capture the actual hooks/<file>.cjs the command runs so retention is path-anchored.
_HOOK_PATH_RE = re.compile(r"\.claude/hooks/([^\s\"']+\.cjs)")


def _command_targets_shipped_hook(command: str, hook_basenames: set) -> bool:
    """True iff ``command`` runs a ``.claude/hooks/<file>.cjs`` whose basename is a shipped framework
    hook. Path-anchored, not a loose substring: a hook name that is merely a substring of another
    (``init.cjs`` inside ``session-init.cjs``) cannot falsely keep an entry, and a non-framework
    command that runs no shipped hook file (e.g. ``external-tool hook claude``) is correctly dropped."""
    return any(Path(ref).name in hook_basenames for ref in _HOOK_PATH_RE.findall(command))


def _filter_settings(raw: bytes, hook_basenames: set) -> bytes:
    """Rewrite settings.json so the shipped harness config has no dangling references: drop statusLine
    (points at statusline-* lib modules excluded from the framework pack) and keep only hook entries
    whose command targets one of the shipped framework hooks. Deterministic (sorted keys)."""
    data = json.loads(raw)
    data.pop("statusLine", None)
    hooks = data.get("hooks")
    if isinstance(hooks, dict):
        filtered = {}
        for event, groups in hooks.items():
            kept_groups = []
            for g in groups:
                kept = [hk for hk in g.get("hooks", [])
                        if _command_targets_shipped_hook(hk.get("command", ""), hook_basenames)]
                if kept:
                    ng = dict(g)
                    ng["hooks"] = kept
                    kept_groups.append(ng)
            if kept_groups:
                filtered[event] = kept_groups
        data["hooks"] = filtered
    return (json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n").encode("utf-8")


def _content_for(arc: str, src: Path, hook_basenames: set) -> bytes:
    """Bytes to ship for `arc` — transformed for settings.json, raw bytes otherwise. Used for BOTH the
    embedded MANIFEST.json hash and the archived payload so they always agree."""
    if arc == ".claude/settings.json":
        return _filter_settings(src.read_bytes(), hook_basenames)
    return src.read_bytes()


def _manifest_json(selection, version, name, hook_basenames) -> bytes:
    entries = {arc: hashlib.sha256(_content_for(arc, src, hook_basenames)).hexdigest()
               for src, arc in selection}
    payload = {"name": name, "version": version, "file_count": len(entries), "files": entries}
    return json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")


def build(out_stream, *, source_date_epoch: int = 0) -> str:
    """Write the deterministic tar.gz to out_stream; return its sha256 hex."""
    manifest = _load_manifest()
    selection = _selection(manifest)
    hook_basenames = _framework_hook_basenames(manifest)
    embedded = _manifest_json(selection, manifest["version"], manifest["name"], hook_basenames)

    sha = hashlib.sha256()

    class _Sink:
        def write(self, data):
            sha.update(data)
            return out_stream.write(data)
        def flush(self):
            out_stream.flush()

    gz = gzip.GzipFile(fileobj=_Sink(), mode="wb", mtime=0, compresslevel=9)
    try:
        tar = tarfile.open(fileobj=gz, mode="w", format=tarfile.PAX_FORMAT)
        try:
            _add_bytes(tar, "MANIFEST.json", embedded, source_date_epoch)
            for src, arc in selection:  # already sorted by arcname
                content = _content_for(arc, src, hook_basenames)
                _add_bytes(tar, arc, content, source_date_epoch)
        finally:
            tar.close()
    finally:
        gz.close()
    return sha.hexdigest()


def _normalize(info: tarfile.TarInfo, epoch: int) -> tarfile.TarInfo:
    info.mtime = epoch
    info.uid = info.gid = 0
    info.uname = info.gname = ""
    info.mode = 0o644 if info.isfile() else 0o755
    return info


def _add_bytes(tar, arcname, payload, epoch):
    info = tarfile.TarInfo(name=arcname)
    info.size = len(payload)
    info.type = tarfile.REGTYPE
    info = _normalize(info, epoch)
    tar.addfile(info, io.BytesIO(payload))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--verify", action="store_true", help="build twice, assert byte-identical")
    ap.add_argument("--source-date-epoch", type=int, default=0)
    args = ap.parse_args()

    if args.verify:
        a, b = io.BytesIO(), io.BytesIO()
        sha_a = build(a, source_date_epoch=args.source_date_epoch)
        sha_b = build(b, source_date_epoch=args.source_date_epoch)
        identical = a.getvalue() == b.getvalue() and sha_a == sha_b
        print(f"determinism: {'OK byte-identical' if identical else 'FAIL'} sha256={sha_a}")
        return 0 if identical else 1

    manifest = _load_manifest()
    out_dir = REPO / "dist"
    out_dir.mkdir(exist_ok=True)
    out = out_dir / f"{manifest['name']}-v{manifest['version']}.tar.gz"
    with out.open("wb") as f:
        sha = build(f, source_date_epoch=args.source_date_epoch)
    print(f"built {out.relative_to(REPO)}  sha256={sha}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
