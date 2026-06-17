#!/usr/bin/env python3
"""Build the human-analyzer showcase site from a single source of truth.

Source of truth (hand-authored):
  partials/hub.html              — homepage (showcase / overview) content
  partials/guides-index.html     — the guides landing ("Welcome to the Guides")
  partials/<guide>.html          — one detailed guide per file
  partials/_footer.html          — shared footer ({ROOT} = repo-root prefix)
  assets/showcase.css, assets/showcase.js  — shared styles + behavior
  artifacts/*.txt                — REAL captured stdout (never pasted into partials)

Outputs (generated — DO NOT hand-edit):
  index.html                     — homepage (slim header, no sidebar)
  guides/index.html              — guides landing (slim header + left sidebar)
  guides/<guide>.html            — one page per guide (slim header + left sidebar)
  human-analyzer-showcase.html   — ONE portable file (CSS+JS inlined, hash-router)

The homepage uses a plain shell; every guide uses a docs shell with a left
sidebar nav tree grouped by track (see CATEGORIES). The portable file wraps
every page in a [data-route] panel and the router in showcase.js switches them
on hashchange, showing the sidebar only on guide routes. Stdlib only — run:
python3 build.py
"""
import html
import pathlib
import re
import shutil

HERE = pathlib.Path(__file__).resolve().parent
PARTIALS = HERE / "partials"
ASSETS = HERE / "assets"
ARTDIR = HERE / "artifacts"

# Homepage (the showcase / overview) — not a guide; lives at index.html.
#   key, label(en), label(vi), partial, <title>, accent css-var
HOME = ("hub", "Overview", "Tổng quan", "hub.html",
        "human-analyzer — Interactive Showcase", "var(--orc)")

# The guides landing — lives at guides/index.html.
GUIDES_INDEX = ("guides", "All guides", "Mục lục", "guides-index.html",
                "Guides — human-analyzer", "var(--orc)")

# Guides — each gets the docs sidebar. Same fields as HOME.
# Order follows the sidebar reading order (also drives prev/next via SEQ).
GUIDES = [
    ("quickstart",   "Quick start",    "Bắt đầu",        "quickstart.html",   "Quick start — human-analyzer",      "var(--ok)"),
    ("install",      "Install",        "Cài đặt",        "install.html",      "Install — human-analyzer",          "var(--ok)"),
    ("journey",      "Journey",        "Hành trình",     "journey.html",      "Journey — human-analyzer",          "var(--gold)"),
    ("mat",          "MAT",            "Tư liệu",        "mat.html",          "MAT — human-analyzer",              "var(--mat)"),
    ("psy",          "PSY",            "Tâm lý",         "psy.html",          "PSY — human-analyzer",              "var(--psy)"),
    ("evl",          "EVL",            "Đánh giá",       "evl.html",          "EVL — human-analyzer",              "var(--evl)"),
    ("cre",          "CRE",            "Nội dung",       "cre.html",          "CRE — human-analyzer",              "var(--cre)"),
    ("gro",          "GRO",            "Phát triển",     "gro.html",          "GRO — human-analyzer",              "var(--gro)"),
    ("orc",          "ORC",            "Điều phối",      "orc.html",          "ORC — human-analyzer",              "var(--orc)"),
    ("pipeline",     "Event bus",      "Event bus",      "pipeline.html",     "Event bus — human-analyzer",        "var(--orc)"),
    ("gates",        "Gates",          "Cổng",           "gates.html",        "Gates — human-analyzer",            "var(--crit)"),
    ("privacy",      "Privacy",        "Bảo mật",        "privacy.html",      "Privacy — human-analyzer",          "var(--crit)"),
    ("rubrics",      "Rubrics",        "Rubric",         "rubrics.html",      "Rubrics — human-analyzer",          "var(--evl)"),
    ("catalog",      "All skills",     "Toàn bộ skill",  "catalog.html",      "All skills — human-analyzer",       "var(--gold)"),
    ("finder",       "Skill finder",   "Chọn skill",     "finder.html",       "Skill finder — human-analyzer",     "var(--gold)"),
    ("glossary",     "Glossary",       "Thuật ngữ",      "glossary.html",     "Glossary — human-analyzer",         "var(--rel)"),
    ("cheatsheet",   "Cheatsheet",     "Tra cứu nhanh",  "cheatsheet.html",   "Cheatsheet — human-analyzer",       "var(--spec)"),
    ("subagents",    "Subagents",      "Subagent",       "subagents.html",    "Subagents — human-analyzer",        "var(--orc)"),
    ("architecture", "Architecture",   "Kiến trúc",      "architecture.html", "Architecture — human-analyzer",     "var(--tel)"),
    ("distribution", "Distribution",   "Phân phối",      "distribution.html", "Distribution — human-analyzer",     "var(--tel)"),
]

# Sidebar grouping (5 categories). Each: key, EN label, VI label, EN intro, VI
# intro (shown on the guides landing as a per-category overview), guide keys.
CATEGORIES = [
    ("start",      "Start here",            "Bắt đầu",
     "Install in one command, then watch one material flow to a gated, published asset.",
     "Cài trong một lệnh, rồi xem một tư liệu đi đến asset đã-gate, đã-đăng.",
     ["quickstart", "install", "journey"]),
    ("frameworks", "The seven frameworks",  "Bảy framework",
     "One guide per framework: ingest, analyze, evaluate, create, grow, orchestrate. (COM utilities live in Architecture.)",
     "Một guide cho mỗi framework: thu nhận, phân tích, đánh giá, sáng tạo, phát triển, điều phối. (Tiện ích COM nằm trong Kiến trúc.)",
     ["mat", "psy", "evl", "cre", "gro", "orc"]),
    ("pipeline",   "Pipeline & gates",      "Pipeline & cổng",
     "How events cascade across domains, and the gates that block unbacked or unsafe output.",
     "Cách sự kiện cascade qua các miền, và các cổng chặn output thiếu bằng chứng hoặc không an toàn.",
     ["pipeline", "gates", "privacy", "rubrics"]),
    ("catalog",    "Catalog & reference",   "Danh mục & tra cứu",
     "Browse all 68 skills, find the right one, and look terms up fast.",
     "Duyệt toàn bộ 68 skill, tìm đúng cái cần, và tra thuật ngữ nhanh.",
     ["catalog", "finder", "glossary", "cheatsheet"]),
    ("internals",  "Internals",             "Bên trong",
     "Inside the machinery: subagents, architecture (+ COM), and how the toolkit ships.",
     "Bên trong bộ máy: subagent, kiến trúc (+ COM), và cách toolkit được phân phối.",
     ["subagents", "architecture", "distribution"]),
]

# Linear order for prev/next footer nav: homepage → guides landing → guides.
SEQ = ["hub", "guides"] + [g[0] for g in GUIDES]

DESC = ("An interactive, standalone tour of human-analyzer: a clinical-grade character-profile "
        "intelligence system for Claude Code — 7 frameworks, 68 skills, an event-bus pipeline, "
        "and a two-stage publish gate that blocks any claim it can't cite.")
GEN_BANNER = "<!-- GENERATED by build.py — edit showcase/partials/ + assets/, never this file -->"
CHROME = ('<div class="glow g1"></div><div class="glow g2"></div><div class="glow g3"></div>\n'
          '<canvas id="net"></canvas>')


def read(p):
    fp = PARTIALS / p
    return fp.read_text(encoding="utf-8") if fp.exists() else f"<!-- missing partial: {p} -->"


def _art(name):
    return (ARTDIR / name).read_text(encoding="utf-8")


def _pre(name):
    """Real captured stdout, escaped, in a <pre> block."""
    return "<pre>" + html.escape(_art(name), quote=False) + "</pre>"


# placeholder token -> artifact file rendered as a <pre> terminal block.
# (Artifacts are captured in Phase 3; a partial only references a token once its
#  .txt exists in artifacts/ — otherwise the build raises on the missing file.)
_PRE_TOKENS = {
    "<!--PYTEST-->": "pytest-tail.txt",
    "<!--E2E-->": "e2e-run.txt",
    "<!--SCHEMA_VALIDATE-->": "schema-validate.txt",
    "<!--EVL_SCORECARD-->": "evl-scorecard.txt",
    "<!--ORC_AUDIT-->": "orc-audit.txt",
    "<!--SKILL_STOCKTAKE-->": "skill-stocktake.txt",
    "<!--PACK_BUILD-->": "pack-build.txt",
}


def inject(text):
    """Replace artifact placeholders in a partial with the real captured output.
    Artifacts are the single source of truth — never pasted into partials."""
    for tok, fn in _PRE_TOKENS.items():
        if tok in text:
            text = text.replace(tok, _pre(fn))
    return text


# In-content page links are written mode-agnostically as href="@<key>" and
# rewritten here per target — relative paths for the multipage build, #hash
# routes for the portable build — so the same partial works in both.
_LINK_RE = re.compile(r'href="@([a-z]+)(#[a-z0-9-]+)?"')


def resolve_links(text, mode, here):
    def _sub(m):
        target, anchor = m.group(1), m.group(2) or ""
        if anchor and mode == "single":
            # one-file build: the section id lives in the same document
            return 'href="%s"' % anchor
        return 'href="%s%s"' % (_href(target, mode, here), anchor)
    return _LINK_RE.sub(_sub, text)


def page_body(partial, mode, here):
    """Read a partial, inject real artifacts, and resolve @<key> page links."""
    return resolve_links(inject(read(partial)), mode, here)


def _guide_meta(k):
    return next(g for g in GUIDES if g[0] == k)


def _nav_label(k):
    """(en, vi) label for any nav target key."""
    if k == "hub":
        return (HOME[1], HOME[2])
    if k == "guides":
        return (GUIDES_INDEX[1], GUIDES_INDEX[2])
    g = _guide_meta(k)
    return (g[1], g[2])


def _href(target, mode, here):
    """Resolve a link to a target page key.

    target: 'home'/'hub' | 'guides' | <guide-key>
    mode:   'multi' (real page links) | 'single' (#hash route)
    here:   'home' (page at showcase root) | anything else (page inside guides/)
    """
    if mode == "single":
        if target in ("home", "hub"):
            return "#hub"
        if target == "guides":
            return "#guides"
        return "#" + target
    if here == "home":                       # linking out from index.html
        if target in ("home", "hub"):
            return "index.html"
        if target == "guides":
            return "guides/index.html"
        return "guides/" + target + ".html"
    # linking out from a page inside guides/
    if target in ("home", "hub"):
        return "../index.html"
    if target == "guides":
        return "index.html"
    return target + ".html"


def header_slim(mode, here):
    """Slim top bar: hamburger (mobile, docs only) · brand · Guides · EN/VI."""
    home = _href("home", mode, here)
    guides = _href("guides", mode, here)
    return (
        '<header class="app-header">\n  <div class="app-header-in">\n'
        '    <button class="side-toggle" data-side-toggle aria-label="Toggle guides menu" aria-expanded="false">'
        '<svg viewBox="0 0 24 24" fill="none"><path d="M4 7h16M4 12h16M4 17h16" stroke="currentColor" '
        'stroke-width="2" stroke-linecap="round"/></svg></button>\n'
        f'    <a href="{home}" class="brand"><span class="dot"></span><span>human-analyzer</span></a>\n'
        '    <div class="app-header-right">\n'
        f'      <a href="{guides}" class="btn-guides" data-nav="guides">'
        '<svg viewBox="0 0 24 24" fill="none"><path d="M5 4h9a3 3 0 0 1 3 3v14H7a2 2 0 0 1-2-2V4Z" '
        'stroke="currentColor" stroke-width="1.8" stroke-linejoin="round"/>'
        '<path d="M9 9h5M9 13h4" stroke="currentColor" stroke-width="1.8" stroke-linecap="round"/></svg>'
        '<span class="en">Guides</span><span class="vi">Hướng dẫn</span></a>\n'
        '      <div class="langtoggle" role="group" aria-label="language">\n'
        '        <button id="btn-en" class="active" onclick="setLang(\'en\')">EN</button>\n'
        '        <button id="btn-vi" onclick="setLang(\'vi\')">VI</button>\n'
        '      </div>\n    </div>\n  </div>\n</header>'
    )


def sidebar(active, mode, here):
    """Left docs nav tree grouped by track (CATEGORIES)."""
    out = ['<aside class="docs-side" aria-label="Guides navigation">']
    gi = _href("guides", mode, here)
    gcls = " active" if active == "guides" else ""
    out.append(f'  <a href="{gi}" class="side-link side-top{gcls}" data-nav="guides">'
               '<span class="en">All guides</span><span class="vi">Mục lục</span></a>')
    for _ck, cen, cvi, _ien, _ivi, keys in CATEGORIES:
        out.append(f'  <div class="side-cat"><span class="en">{cen}</span><span class="vi">{cvi}</span></div>')
        for k in keys:
            g = _guide_meta(k)
            href = _href(k, mode, here)
            cls = " active" if active == k else ""
            out.append(f'  <a href="{href}" class="side-link{cls}" data-nav="{k}">'
                       f'<span class="en">{g[1]}</span><span class="vi">{g[2]}</span></a>')
    out.append("</aside>")
    return "\n".join(out)


def crumb(key, mode, here):
    """Breadcrumb: Home › Guides › <current> (Guides hop omitted on the landing)."""
    home = _href("home", mode, here)
    gi = _href("guides", mode, here)
    en, vi = _nav_label(key)
    cur = f'<span class="cur"><span class="en">{en}</span><span class="vi">{vi}</span></span>'
    mid = ""
    if key != "guides":
        mid = (f'<a href="{gi}"><span class="en">Guides</span><span class="vi">Hướng dẫn</span></a> '
               '<span class="sep">›</span> ')
    return (f'<div class="crumb"><a href="{home}"><span class="en">Home</span>'
            f'<span class="vi">Trang chủ</span></a> <span class="sep">›</span> {mid}{cur}</div>')


def skill_nav(key, mode, here):
    """Generated prev · next footer nav. Order lives in SEQ (DRY)."""
    idx = SEQ.index(key)
    ac = "var(--orc)" if key in ("hub", "guides") else _guide_meta(key)[5]
    parts = [f'<div class="skill-nav" style="--ac:{ac}">']
    if idx > 0:
        pk = SEQ[idx - 1]
        pen, pvi = _nav_label(pk)
        parts.append(f'<a class="pv" href="{_href(pk, mode, here)}"><span class="k">← '
                     '<span class="en">Prev</span><span class="vi">Trước</span></span>'
                     f'<span class="v"><span class="en">{pen}</span><span class="vi">{pvi}</span></span></a>')
    else:
        parts.append('<span class="pv" style="flex:1"></span>')
    if idx + 1 < len(SEQ):
        nk = SEQ[idx + 1]
        nen, nvi = _nav_label(nk)
        parts.append(f'<a class="nx" href="{_href(nk, mode, here)}"><span class="k">'
                     '<span class="en">Next</span><span class="vi">Sau</span> →</span>'
                     f'<span class="v"><span class="en">{nen}</span><span class="vi">{nvi}</span></span></a>')
    else:
        parts.append('<span class="nx" style="flex:1"></span>')
    parts.append("</div>")
    return "".join(parts)


# One-line description per guide, shown on the landing-page overview cards.
GUIDE_DESC = {
    "quickstart":   ("Clone, install the venv, run the deterministic pipeline, invoke your first skill.",
                     "Clone, dựng venv, chạy pipeline tất định, gọi skill đầu tiên."),
    "install":      ("Provision the project-local interpreter and verify the toolkit imports cleanly.",
                     "Dựng trình thông dịch nội bộ và xác minh toolkit import sạch."),
    "journey":      ("Follow one synthetic material from ingest to a gated, published asset.",
                     "Theo một tư liệu giả lập từ thu nhận đến asset đã-gate, đã-đăng."),
    "mat":          ("Evidence ingestion — classify, CRAAP-score, tier T1–T5, gate before analysis.",
                     "Thu nhận bằng chứng — phân loại, chấm CRAAP, bậc T1–T5, gate trước phân tích."),
    "psy":          ("Clinical 5P formulation — defenses, attachment, trauma, diagnostics, consistency.",
                     "Formulation 5P lâm sàng — phòng vệ, gắn bó, sang chấn, chẩn đoán, nhất quán."),
    "evl":          ("Score a character against versioned rubrics → an evidence-cited scorecard + verdict.",
                     "Chấm điểm nhân vật theo rubric có phiên bản → scorecard có trích dẫn + phán quyết."),
    "cre":          ("Profile → platform-native content, double-gated by evidence and confidentiality.",
                     "Hồ sơ → nội dung gốc nền tảng, gate kép bởi bằng chứng và bảo mật."),
    "gro":          ("Career, competency, learning, and mentoring intelligence feeding PSY + CRE.",
                     "Tình báo sự nghiệp, năng lực, học tập, cố vấn — nuôi PSY + CRE."),
    "orc":          ("The event bus — routes, cascades, audits, and owns memory, decisions, the graph.",
                     "Event bus — định tuyến, cascade, kiểm toán, sở hữu bộ nhớ, quyết định, đồ thị."),
    "pipeline":     ("How MAT.integrated → PSY.refresh → CRE.recalibrate flows, gated and audited.",
                     "Cách MAT.integrated → PSY.refresh → CRE.recalibrate chảy, có gate và kiểm toán."),
    "gates":        ("The MAT integration gate, the per-claim evidence gate, and the privacy gate.",
                     "Cổng tích hợp MAT, cổng bằng chứng từng claim, và cổng bảo mật."),
    "privacy":      ("Clinical-grade confidentiality — privacy tags, caches, and the safe distribution pack.",
                     "Bảo mật cấp lâm sàng — privacy tag, cache, và gói phân phối an toàn."),
    "rubrics":      ("The 4 versioned rubrics, the JSON-schema, and how a scorecard is built.",
                     "4 rubric có phiên bản, JSON-schema, và cách dựng scorecard."),
    "catalog":      ("Browse the entire framework catalog, grouped by framework with deps.",
                     "Duyệt toàn bộ catalog framework, nhóm theo framework kèm phụ thuộc."),
    "finder":       ("Answer “I want to…” and get the exact skill or chain to run.",
                     "Trả lời “Tôi muốn…” và nhận đúng skill hoặc chuỗi cần chạy."),
    "glossary":     ("The canonical terms — evidence tier, CRAAP, 5P, cascade, scorecard, verdict.",
                     "Thuật ngữ chuẩn — bậc bằng chứng, CRAAP, 5P, cascade, scorecard, phán quyết."),
    "cheatsheet":   ("Every skill, event, rule, rubric, and venv command in scannable tables.",
                     "Mọi skill, sự kiện, quy tắc, rubric, lệnh venv trong bảng tra nhanh."),
    "subagents":    ("The 20 specialized subagents and the skills that deploy them, with input isolation.",
                     "20 subagent chuyên biệt và các skill triển khai chúng, có cô lập đầu vào."),
    "architecture": ("Inside the machinery — data locations, platform_lib, the knowledge graph, schemas + COM.",
                     "Bên trong bộ máy — vị trí dữ liệu, platform_lib, đồ thị tri thức, schema + COM."),
    "distribution": ("Deterministic toolkit packaging that ships no corpus, verified by SHA.",
                     "Đóng gói toolkit tất định không ship corpus, xác minh bằng SHA."),
}


def category_overview(mode, here):
    """Per-category overview for the guides landing: intro + cards, from CATEGORIES."""
    out = []
    for _ck, cen, cvi, ien, ivi, keys in CATEGORIES:
        out.append('<section class="cat-ov reveal">')
        out.append(f'  <h2 class="sectitle"><span class="en">{cen}</span><span class="vi">{cvi}</span></h2>')
        out.append(f'  <p class="lead cat-intro"><span class="en">{ien}</span><span class="vi">{ivi}</span></p>')
        out.append('  <div class="cards grid-2">')
        for k in keys:
            g = _guide_meta(k)
            href = _href(k, mode, here)
            den, dvi = GUIDE_DESC.get(k, ("", ""))
            out.append(f'    <a class="card" href="{href}" style="--ac:{g[5]}"><h3><span class="pin"></span>'
                       f'<span class="en">{g[1]}</span><span class="vi">{g[2]}</span></h3>'
                       f'<p><span class="en">{den}</span><span class="vi">{dvi}</span></p></a>')
        out.append('  </div>')
        out.append('</section>')
    return "\n".join(out)


def gi_page_body(mode, here):
    """Guides landing body: hand-authored welcome + generated category overview."""
    body = page_body(GUIDES_INDEX[3], mode, here)
    return body.replace("<!--CATEGORY_OVERVIEW-->", category_overview(mode, here))


def head(title, head_inject):
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        '<meta charset="UTF-8" />\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1.0" />\n'
        # Declared before the stylesheet loads so the browser paints a dark canvas during
        # navigation — no white flash between pages.
        '<meta name="color-scheme" content="dark" />\n'
        '<meta name="theme-color" content="#070b16" />\n'
        f"<title>{title}</title>\n"
        f'<meta name="description" content="{DESC}" />\n'
        f"{head_inject}\n</head>\n"
    )


def shell(title, head_inject, view, header_html, sidebar_html, body_html,
          footer, script_inject, portable=False):
    """Assemble a page. view='home' → plain; view='guide' or portable → docs layout."""
    if portable or view == "guide":
        side = sidebar_html or ""
        # Right "On this page" TOC is built client-side (showcase.js) from the
        # active content's <h2 id> headings, so it works for both the multipage
        # guides and the portable router's active route.
        toc = '<nav class="toc" data-toc aria-label="On this page"></nav>'
        layout = ('<div class="scrim" data-scrim></div>\n'
                  '<div class="docs-layout">\n' + side + '\n'
                  '<main class="docs-main">\n' + body_html + '\n</main>\n'
                  + toc + '\n</div>')
    else:
        layout = body_html
    return (
        head(title, head_inject)
        + f'<body class="lang-en view-{view}">\n'
        # Restore the saved language before the content below paints — otherwise every
        # navigation flashes English first, then swaps to the stored Vietnamese.
        + '<script>try{if(localStorage.getItem(\'ha-lang\')===\'vi\')'
          'document.body.classList.replace(\'lang-en\',\'lang-vi\');}catch(e){}</script>\n'
        + GEN_BANNER + "\n"
        + CHROME + "\n"
        + header_html + "\n"
        + layout + "\n"
        + footer + "\n"
        + script_inject + "\n"
        + "</body>\n</html>\n"
    )


def build():
    css = (ASSETS / "showcase.css").read_text(encoding="utf-8")
    js = (ASSETS / "showcase.js").read_text(encoding="utf-8")
    # Vendored Three.js (r128, MIT) — drives the 3D hero background. Multipage links
    # the local copy; the portable file inlines it so it stays self-contained + offline.
    lib = (ASSETS / "lib" / "three.min.js").read_text(encoding="utf-8")
    footer_tpl = read("_footer.html")
    written = []

    guides_dir = HERE / "guides"
    guides_dir.mkdir(exist_ok=True)

    # ---------- multipage homepage (index.html) ----------
    link = '<link rel="stylesheet" href="assets/showcase.css" />'
    script = '<script src="assets/lib/three.min.js"></script>\n<script src="assets/showcase.js"></script>'
    home_body = (page_body("hub.html", "multi", "home")
                 + '\n<div class="wrap">' + skill_nav("hub", "multi", "home") + "</div>")
    out = shell(HOME[4], link, "home", header_slim("multi", "home"), None,
                home_body, footer_tpl.replace("{ROOT}", "../"), script)
    (HERE / "index.html").write_text(out, encoding="utf-8")
    written.append("index.html")

    # ---------- multipage guides (guides/*.html) ----------
    link_g = '<link rel="stylesheet" href="../assets/showcase.css" />'
    script_g = '<script src="../assets/lib/three.min.js"></script>\n<script src="../assets/showcase.js"></script>'
    footer_g = footer_tpl.replace("{ROOT}", "../../")

    gi_body = (crumb("guides", "multi", "guides") + "\n" + gi_page_body("multi", "guides")
               + '\n<div class="wrap">' + skill_nav("guides", "multi", "guides") + "</div>")
    out = shell(GUIDES_INDEX[4], link_g, "guide", header_slim("multi", "guides"),
                sidebar("guides", "multi", "guides"), gi_body, footer_g, script_g)
    (guides_dir / "index.html").write_text(out, encoding="utf-8")
    written.append("guides/index.html")

    for key, _en, _vi, pf, title, _ac in GUIDES:
        body = (crumb(key, "multi", key) + "\n" + page_body(pf, "multi", key)
                + '\n<div class="wrap">' + skill_nav(key, "multi", key) + "</div>")
        out = shell(title, link_g, "guide", header_slim("multi", key),
                    sidebar(key, "multi", key), body, footer_g, script_g)
        (guides_dir / (key + ".html")).write_text(out, encoding="utf-8")
        written.append(f"guides/{key}.html")

    # ---------- portable single file ----------
    style_inline = "<style>\n" + css + "\n</style>"
    script_inline = "<script>\n" + lib + "\n</script>\n<script>\n" + js + "\n</script>"
    footer_single = footer_tpl.replace("{ROOT}", "../")
    panels = []
    for key in SEQ:
        if key == "hub":
            inner = page_body(HOME[3], "single", "")
        elif key == "guides":
            inner = gi_page_body("single", "")
        else:
            inner = page_body(_guide_meta(key)[3], "single", "")
        body = inner + '\n<div class="wrap">' + skill_nav(key, "single", "") + "</div>"
        panels.append(f'<div class="route" data-route="{key}">\n{body}\n</div>')
    main_single = "\n".join(panels)
    out = shell(HOME[4], style_inline, "home", header_slim("single", ""),
                sidebar("hub", "single", ""), main_single, footer_single,
                script_inline, portable=True)
    (HERE / "human-analyzer-showcase.html").write_text(out, encoding="utf-8")
    written.append("human-analyzer-showcase.html")

    return written


if __name__ == "__main__":
    for w in build():
        print("wrote", w)
