"""B12 Monitoring Phase 2 — com:skill-analytics (S2 health, P3 deps, P4 cascade).

Isolated: each script module is loaded from its file and its module-level SKILLS_DIR /
PLATFORM_LIB globals are monkeypatched at a tmp fixture tree, so no real repo dependency.
"""
import importlib.util
from pathlib import Path

import pytest

SCRIPTS = Path(__file__).resolve().parents[1] / ".claude" / "skills" / "com-skill-analytics" / "scripts"


def _load(name: str):
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), SCRIPTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _make_skill(root: Path, name: str, *, scripts: dict | None = None, frontmatter=True,
                md_extra="", description="test skill desc"):
    d = root / name
    (d / "scripts").mkdir(parents=True, exist_ok=True)
    fm = ('---\nname: "%s"\ndescription: "%s"\n---\n'
          % (name.replace("-", ":", 1), description)) if frontmatter else ""
    (d / "SKILL.md").write_text(fm + "# " + name + "\n" + md_extra, encoding="utf-8")
    for fn, body in (scripts or {}).items():
        (d / "scripts" / fn).write_text(body, encoding="utf-8")
    return d


@pytest.fixture
def fake_tree(tmp_path):
    skills = tmp_path / "skills"
    lib = tmp_path / "platform_lib"
    lib.mkdir(parents=True)
    (lib / "paths.py").write_text("ROOT=1\n", encoding="utf-8")
    (lib / "lonely.py").write_text("x=1\n", encoding="utf-8")  # unused module
    _make_skill(skills, "psy-good", scripts={"ok.py": "from platform_lib.paths import ROOT\n"})
    _make_skill(skills, "cre-broken", scripts={"bad.py": "def (:\n"})  # syntax error
    _make_skill(skills, "orc-prompt")  # prompt-only, no scripts
    _make_skill(skills, "zztop-ignored", scripts={"x.py": "y=1\n"})  # non-framework prefix → ignored
    return skills, lib


def test_s2_detects_broken_and_classifies(fake_tree, tmp_path):
    skills, lib = fake_tree
    mod = _load("check-skill-and-lib-health")
    mod.SKILLS_DIR = skills
    mod.PLATFORM_LIB = lib
    data = mod.gather(None, perf=False)
    assert set(data["frameworks"]) == {"psy", "cre", "orc"}  # zztop ignored
    statuses = {s["skill"]: s["status"] for s in data["skills"]}
    assert statuses["cre-broken"] == "BROKEN"
    assert statuses["psy-good"] == "OK"
    types = {s["skill"]: s["type"] for s in data["skills"]}
    assert types["orc-prompt"] == "prompt-only"
    assert data["platform_lib"]["paths"] == 1   # imported by psy-good
    assert data["platform_lib"]["lonely"] == 0  # unused


def test_p3_fanin_and_unused(fake_tree):
    skills, lib = fake_tree
    mod = _load("build-dependency-graph")
    mod.SKILLS_DIR = skills
    mod.PLATFORM_LIB = lib
    data = mod.gather()
    assert data["fanin"].get("paths") == 1
    assert "lonely" in data["unused_modules"]
    assert data["cycles"] == []  # no platform_lib cycles in fixture


def test_p4_extracts_events_and_orphans(tmp_path):
    skills = tmp_path / "skills"
    _make_skill(skills, "mat-loader", md_extra="Pipeline: MAT.integrated → PSY.refresh\n")
    _make_skill(skills, "com-rules", md_extra="No events here.\n")
    mod = _load("build-cascade-graph")
    mod.SKILLS_DIR = skills
    data = mod.gather()
    assert ("MAT.integrated", "PSY.refresh") in [tuple(e) for e in data["chain_edges"]]
    assert "com:rules" in data["orphans"]
    assert "MAT.integrated" in data["skill_events"]["mat:loader"]


# ---------------------------------------------------------------------------
# Phase 3 — S1 usage/tokens, S4 coverage/budget, M5 content pipeline.
# All isolated: module path globals (SKILLS_DIR/INVOCATIONS/ASSETS_DIR/ROUTING_DOCS)
# repointed at tmp fixtures; token attribution uses CK_SESSIONS_DIR env.
# ---------------------------------------------------------------------------


def _write_jsonl(path: Path, records: list[dict]):
    import json
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(json.dumps(r) for r in records) + "\n", encoding="utf-8")


@pytest.fixture
def usage_tree(tmp_path):
    skills = tmp_path / "skills"
    _make_skill(skills, "com-git")
    _make_skill(skills, "psy-crossref")
    _make_skill(skills, "gro-validate")  # never invoked
    return skills


def test_s1_counts_and_never_used(usage_tree, tmp_path):
    mod = _load("scan-skill-usage-and-tokens")
    mod.SKILLS_DIR = usage_tree
    mod.INVOCATIONS = tmp_path / "invocations.jsonl"
    _write_jsonl(mod.INVOCATIONS, [
        {"ts": "2026-05-26T10:00:00Z", "skill": "com-git"},
        {"ts": "2026-05-26T11:00:00Z", "skill": "com-git"},
        {"ts": "2026-05-26T12:00:00Z", "skill": "psy:crossref"},  # colon form normalizes
    ])
    data = mod.gather(days=3650, framework=None, with_tokens=False)
    counts = {r["skill"]: r["count"] for r in data["rows"]}
    assert counts["com-git"] == 2
    assert counts["psy-crossref"] == 1
    assert data["total_invocations"] == 3
    assert "gro-validate" in data["never_used"]


def test_s1_empty_invocations_graceful(usage_tree, tmp_path):
    mod = _load("scan-skill-usage-and-tokens")
    mod.SKILLS_DIR = usage_tree
    mod.INVOCATIONS = tmp_path / "does-not-exist.jsonl"
    data = mod.gather(days=30, framework=None, with_tokens=False)
    assert data["total_invocations"] == 0
    assert "No invocation data" in mod.render_md(data, top=None)


def test_s1_days_filter_excludes_old(usage_tree, tmp_path):
    mod = _load("scan-skill-usage-and-tokens")
    mod.SKILLS_DIR = usage_tree
    mod.INVOCATIONS = tmp_path / "invocations.jsonl"
    _write_jsonl(mod.INVOCATIONS, [
        {"ts": "2020-01-01T10:00:00Z", "skill": "com-git"},  # outside 30d window
        {"ts": _now_iso(), "skill": "psy-crossref"},
    ])
    data = mod.gather(days=30, framework=None, with_tokens=False)
    counts = {r["skill"]: r["count"] for r in data["rows"]}
    assert counts["com-git"] == 0
    assert counts["psy-crossref"] == 1


def test_s1_token_attribution(usage_tree, tmp_path, monkeypatch):
    import json
    sdir = tmp_path / "sessions"
    sdir.mkdir()
    # One Skill tool_use opens a span for com-git; following assistant usage credited.
    lines = [
        {"message": {"content": [{"type": "tool_use", "name": "Skill",
                                  "input": {"skill": "com-git"}}]}},
        {"message": {"usage": {"input_tokens": 100, "output_tokens": 50}}},
        {"message": {"content": [{"type": "tool_use", "name": "Skill",
                                  "input": {"skill": "psy:crossref"}}]}},
        {"message": {"usage": {"input_tokens": 200, "output_tokens": 200}}},
    ]
    (sdir / "s1.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n", encoding="utf-8")
    monkeypatch.setenv("CK_SESSIONS_DIR", str(sdir))
    mod = _load("scan-skill-usage-and-tokens")
    tokens = mod.gather_tokens()
    assert tokens["com-git"] == 150
    assert tokens["psy-crossref"] == 400


def test_s4_budget_overlap_and_decommission(tmp_path):
    skills = tmp_path / "skills"
    _make_skill(skills, "psy-alpha", description="Handles mentoring relationship dynamics.")
    _make_skill(skills, "gro-beta", description="Handles mentoring competency growth.")
    mod = _load("analyze-skill-coverage-and-budget")
    mod.SKILLS_DIR = skills
    mod.ROUTING_DOCS = [tmp_path / "no-routing.md"]  # nothing documented
    mod.INVOCATIONS = tmp_path / "invocations.jsonl"
    _write_jsonl(mod.INVOCATIONS, [{"ts": "2026-05-26T10:00:00Z", "skill": "psy-alpha"}])
    data = mod.gather()
    assert data["skill_count"] == 2
    assert all(s["tokens"] > 0 for s in data["skills"])
    overlap_kw = {o["keyword"] for o in data["trigger_overlaps"]}
    assert "mentoring" in overlap_kw  # shared, non-stopword
    assert set(data["routing_gaps"]) == {"psy-alpha", "gro-beta"}
    assert data["never_used"] == ["gro-beta"]  # psy-alpha was invoked


@pytest.fixture
def content_tree(tmp_path):
    assets = tmp_path / "assets"
    for plat, dirs in {
        "facebook": ["260101-new-year", "260215-mid-feb", "260301-march"],
        "linkedin": ["260220-single"],
    }.items():
        for d in dirs:
            (assets / plat / d).mkdir(parents=True)
    return assets


def test_m5_counts_cadence_and_inactive(content_tree):
    mod = _load("scan-content-pipeline-health")
    mod.ASSETS_DIR = content_tree
    data = mod.gather(platform_filter=None, since=None)
    rows = {r["platform"]: r for r in data["rows"]}
    assert rows["facebook"]["posts"] == 3
    assert rows["facebook"]["last_post"] == "2026-03-01"
    assert rows["linkedin"]["frequency"] == "<1/month"
    assert data["total_posts"] == 4
    # Expected-but-empty platforms still surface as INACTIVE.
    assert "instagram" in data["inactive"] and "tiktok" in data["inactive"]


def test_m5_since_filter(content_tree):
    mod = _load("scan-content-pipeline-health")
    mod.ASSETS_DIR = content_tree
    from datetime import date
    data = mod.gather(platform_filter="facebook", since=date(2026, 2, 1))
    fb = next(r for r in data["rows"] if r["platform"] == "facebook")
    assert fb["posts"] == 2  # 260101 excluded


def test_m5_empty_assets_no_crash(tmp_path):
    mod = _load("scan-content-pipeline-health")
    mod.ASSETS_DIR = tmp_path / "no-assets"
    data = mod.gather(platform_filter=None, since=None)
    assert data["total_posts"] == 0
    assert data["active_platforms"] == 0


def _now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


# ---------------------------------------------------------------------------
# Phase 4 — M1 unified dashboard, M6 memory health.
# M1 isolated by monkeypatching the single subprocess boundary `_run_json` with
# fixture JSON (no processes spawned). M6 isolated via MEMORY_DIR repoint.
# ---------------------------------------------------------------------------


# Per-source fixture JSON keyed by script filename (what gather() dispatches on).
def _dash_fixtures(*, broken=False, inactive=False):
    return {
        "check-skill-and-lib-health.py": {
            "frameworks": {"psy": {"skills": 2, "OK": 2 - int(broken), "WARN": 0,
                                   "BROKEN": int(broken)},
                           "com": {"skills": 1, "OK": 1, "WARN": 0, "BROKEN": 0}},
            "skills": [{"skill": "psy-x", "framework": "psy",
                        "status": "BROKEN" if broken else "OK"},
                       {"skill": "psy-y", "framework": "psy", "status": "OK"},
                       {"skill": "com-z", "framework": "com", "status": "OK"}],
            "platform_lib": {"paths": 5, "lonely": 0},
        },
        "scan-skill-usage-and-tokens.py": {
            "skills_used": 2, "total_invocations": 7,
            "rows": [{"skill": "psy-x", "framework": "PSY", "count": 5, "tokens": 1000},
                     {"skill": "com-z", "framework": "COM", "count": 2, "tokens": 50}],
        },
        "analyze-skill-coverage-and-budget.py": {
            "routing_gaps": [], "over_budget": [],
            "skills": [{"skill": "psy-x", "framework": "PSY", "tokens": 1200},
                       {"skill": "com-z", "framework": "COM", "tokens": 800}],
        },
        "scan-content-pipeline-health.py": {
            "active_platforms": 1 if inactive else 3,
            "inactive": ["tiktok", "youtube"] if inactive else [],
            "total_posts": 12,
        },
        "check-memory-system-health.py": {"status": "GREEN", "count": 4, "issue_count": 0},
        "score-profile-completeness.py": {
            "file_count_assertion": {"pass": True},
            "assessments": [{"overall": 90}, {"overall": 85}],
        },
        "identify-materials-needing-rescore.py": {"alpha": [], "beta": []},
    }


def _patch_dashboard(mod, fixtures, *, timeouts=None):
    timeouts = timeouts or set()

    def fake(script, args):
        if script.name in timeouts:
            return None, "timeout"
        return fixtures.get(script.name), None

    mod._run_json = fake


def test_m1_all_green(tmp_path):
    mod = _load("build-unified-dashboard")
    _patch_dashboard(mod, _dash_fixtures())
    data = mod.gather()
    status = {r["key"]: r["status"] for r in data["rows"]}
    assert status["skills"] == "GREEN"
    assert status["platform_lib"] == "YELLOW"  # 'lonely' unused module
    assert status["profiles"] == "GREEN"
    assert status["materials"] == "GREEN"
    assert status["content"] == "GREEN"
    assert data["overall"] == "YELLOW"  # platform_lib unused → degraded


def test_m1_red_on_broken_skill():
    mod = _load("build-unified-dashboard")
    _patch_dashboard(mod, _dash_fixtures(broken=True))
    data = mod.gather()
    status = {r["key"]: r["status"] for r in data["rows"]}
    assert status["skills"] == "RED"
    assert data["overall"] == "RED"


def test_m1_timeout_degrades_not_crash():
    mod = _load("build-unified-dashboard")
    _patch_dashboard(mod, _dash_fixtures(), timeouts={"score-profile-completeness.py"})
    data = mod.gather()
    prof = next(r for r in data["rows"] if r["key"] == "profiles")
    assert prof["status"] == "TIMEOUT"
    assert data["overall"] in ("YELLOW", "RED")  # never crashes


def test_m1_skip_excludes_rows_and_sources():
    mod = _load("build-unified-dashboard")
    called = []
    fixtures = _dash_fixtures()

    def fake(script, args):
        called.append(script.name)
        return fixtures.get(script.name), None

    mod._run_json = fake
    data = mod.gather(skip={"profiles", "memory"})
    keys = {r["key"] for r in data["rows"]}
    assert "profiles" not in keys and "memory" not in keys
    # psy/m6 sources must not run when their only rows are skipped.
    assert "score-profile-completeness.py" not in called
    assert "check-memory-system-health.py" not in called


def test_m1_framework_view():
    mod = _load("build-unified-dashboard")
    _patch_dashboard(mod, _dash_fixtures())
    data = mod.gather()
    fv = {f["framework"]: f for f in mod.framework_view(data["raw"])}
    assert fv["PSY"]["skills"] == 2
    assert fv["PSY"]["invocations"] == 5
    assert fv["COM"]["invocations"] == 2
    assert fv["PSY"]["skill_md_tokens"] == 1200


def test_m1_content_red_when_zero_active():
    mod = _load("build-unified-dashboard")
    fx = _dash_fixtures()
    fx["scan-content-pipeline-health.py"] = {"active_platforms": 0, "inactive": ["a", "b"],
                                             "total_posts": 0}
    _patch_dashboard(mod, fx)
    data = mod.gather()
    content = next(r for r in data["rows"] if r["key"] == "content")
    assert content["status"] == "RED"


# --- M6 memory health ---------------------------------------------------------

def _mem(root: Path, fname: str, *, name=None, desc="d", mtype="reference",
         body="", age_days=0):
    import os
    import time
    name = name if name is not None else fname.replace(".md", "")
    fm = "---\nname: %s\n" % name
    if desc is not None:
        fm += "description: %s\n" % desc
    fm += "metadata:\n  type: %s\n---\n" % mtype
    p = root / fname
    p.write_text(fm + body, encoding="utf-8")
    if age_days:
        old = time.time() - age_days * 86400
        os.utime(p, (old, old))
    return p


def test_m6_detects_all_issue_classes(tmp_path):
    mod = _load("check-memory-system-health")
    mod.MEMORY_DIR = tmp_path
    _mem(tmp_path, "good.md", name="good", body="links to [[other]]")
    _mem(tmp_path, "other.md", name="other")
    _mem(tmp_path, "orphan.md", name="orphan")  # not in index
    _mem(tmp_path, "nofield.md", name="nofield", desc=None)  # missing description
    _mem(tmp_path, "stale.md", name="stale", mtype="project", age_days=40)
    _mem(tmp_path, "dup-a.md", name="dupe")
    _mem(tmp_path, "dup-b.md", name="dupe")  # duplicate name
    _mem(tmp_path, "broken.md", name="broken", body="see [[ghost]]")  # broken link
    (tmp_path / "MEMORY.md").write_text(
        "- [Good](good.md) — hook\n- [Other](other.md) — h\n"
        "- [NoField](nofield.md) — h\n- [Stale](stale.md) — h\n"
        "- [DupA](dup-a.md) — h\n- [DupB](dup-b.md) — h\n- [Broken](broken.md) — h\n"
        "- [Dead](deleted.md) — h\n", encoding="utf-8")  # deleted.md missing → dead
    data = mod.gather()
    assert "orphan.md" in data["orphans"]
    assert "deleted.md" in data["dead_entries"]
    assert {"from": "broken.md", "to": "ghost"} in data["broken_links"]
    assert "dupe" in data["duplicates"]
    assert any(m["file"] == "nofield.md" for m in data["invalid_frontmatter"])
    assert any(s["file"] == "stale.md" for s in data["stale"])
    assert data["type_distribution"].get("project") == 1
    assert data["status"] == "RED"  # >3 issues


def test_m6_clean_is_green(tmp_path):
    mod = _load("check-memory-system-health")
    mod.MEMORY_DIR = tmp_path
    _mem(tmp_path, "a.md", name="a")
    (tmp_path / "MEMORY.md").write_text("- [A](a.md) — hook\n", encoding="utf-8")
    data = mod.gather()
    assert data["issue_count"] == 0
    assert data["status"] == "GREEN"


def test_m6_fix_dryrun_vs_apply(tmp_path):
    mod = _load("check-memory-system-health")
    mod.MEMORY_DIR = tmp_path
    _mem(tmp_path, "a.md", name="a")
    (tmp_path / "MEMORY.md").write_text(
        "- [A](a.md) — hook\n- [Gone](gone.md) — h\n", encoding="utf-8")
    data = mod.gather()
    removed = mod.fix_diff(data)
    assert any("gone.md" in ln for ln in removed)
    # dry-run did not mutate the file
    assert "gone.md" in (tmp_path / "MEMORY.md").read_text(encoding="utf-8")
    n = mod.apply_fix(data)
    assert n == 1
    after = (tmp_path / "MEMORY.md").read_text(encoding="utf-8")
    assert "gone.md" not in after and "a.md" in after


def test_m6_missing_dir_graceful(tmp_path):
    mod = _load("check-memory-system-health")
    mod.MEMORY_DIR = tmp_path / "nonexistent"
    data = mod.gather()
    assert data["count"] == 0
    assert data["status"] == "GREEN"
