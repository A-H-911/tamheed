"""HTML renderer for the Tamheed user guide (docs/guide/build.py writes the result to index.html).

Structure comes from extract.facts(); prose comes from content.TEXT keyed by stable ids. Every id
the renderer asks for is recorded in USED_IDS so the coverage test can demand EN + AR for each.
"""
from __future__ import annotations

import re
from html import escape as esc

import diagrams

USED_IDS: list[str] = []
LANGS = ("en", "ar")
_ID_TOKEN = re.compile(r"(?<![\w`/-])((?:FR|NFR|CON|INV|ASM|DEP|OQ|DEC|ADR|RISK|HYP|EXP|POC|TEST|KPI|STK|PH|MS|SL|WBS|AC|AV|PE|DEF|DW|GATE|EP|CONV|SC|WVR|DOC|SEC|DIA|GT|LL|SKL|FB|PRT|G)-[\w.]+)(?![\w`-])")


class Text:
    def __init__(self, table: dict):
        self.table = table

    def get(self, cid: str, lang: str) -> str:
        if cid not in USED_IDS:
            USED_IDS.append(cid)
        entry = self.table.get(cid)
        if not entry or not entry.get(lang):
            return f"[[{cid}]]"
        return entry[lang]


def md(s: str) -> str:
    """The tiny markup subset content.py may use: `code`, **bold**, *italic*, [text](#anchor),
    id tokens. Code spans are lifted out first so their contents are never marked up, then
    bold and italic run over the prose (bold may wrap a code span), then the spans return."""
    spans: list[str] = []

    def lift(m):
        spans.append(f"<code>{esc(m.group(1))}</code>")
        return f"\x00{len(spans) - 1}\x00"

    s = re.sub(r"`([^`]+)`", lift, s)
    s = _inline(s)
    return re.sub(r"\x00(\d+)\x00", lambda m: spans[int(m.group(1))], s)


def _inline(s: str) -> str:
    s = esc(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*([^*\n]+?)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+)\]\((#[\w.-]+)\)", r'<a href="\2">\1</a>', s)
    s = _ID_TOKEN.sub(r'<bdi class="id">\1</bdi>', s)
    return s


class R:
    """Render context: facts + text + the output buffer."""

    def __init__(self, f: dict, text: Text):
        self.f = f
        self.t = text
        self.out: list[str] = []
        self.subs: dict[str, list[tuple[str, str]]] = {}   # plan 202: each section's H3 anchors
        self.figures: list[tuple[str, dict, str]] = []   # plan 203: (fid, model, caption id) of the file figures

    # ---- bilingual helpers -------------------------------------------------------
    def T(self, cid: str, tag: str = "span", cls: str = "") -> str:
        c = f' class="{cls}"' if cls else ""
        return "".join(f'<{tag} lang="{lg}"{c}>{md(self.t.get(cid, lg))}</{tag}>' for lg in LANGS)

    def P(self, cid: str, cls: str = "") -> str:
        return self.T(cid, "p", cls)

    def PS(self, prefix: str, n: int, cls: str = "") -> str:
        """n paragraphs prefix.1 .. prefix.n"""
        return "".join(self.P(f"{prefix}.{i}", cls) for i in range(1, n + 1))

    def H(self, level: int, cid: str, anchor: str = "") -> str:
        a = f' id="{anchor}"' if anchor else ""
        return f"<h{level}{a}>{self.T(cid)}</h{level}>"

    def UI(self, key: str) -> str:
        return self.T(f"ui.{key}")

    def code(self, s: str) -> str:
        return f"<code>{esc(s)}</code>"

    def pre(self, s: str, copy: bool = True) -> str:
        c = " data-copy" if copy else ""
        return f"<pre{c}><code>{esc(s)}</code></pre>"

    def table(self, head: list[str], rows: list[list[str]], cls: str = "") -> str:
        th = "".join(f"<th>{h}</th>" for h in head)
        body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
        return f'<div class="tbl {cls}"><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>'

    def badge(self, text: str, cls: str) -> str:
        return f'<span class="badge {cls}">{esc(text)}</span>'

    def tier(self, which: str) -> str:
        return self.T(f"ui.tier.{which}", "span", f"tier {which}")

    def section(self, sid: str, body: str, kicker: str | None = None) -> None:
        """Plan 202 (G10): the chapter as the kicker, the section number in the H2, and every H3
        gets a deterministic id ({sid}-h{n}) the two-level TOC links to."""
        subs: list[tuple[str, str]] = []

        def _anchor(m: re.Match) -> str:
            aid = m.group(1) or f"{sid}-h{len(subs) + 1}"   # an H3 that carries its own id keeps it
            subs.append((aid, m.group(2)))
            return f'<h3 id="{aid}">{m.group(2)}</h3>'

        body = re.sub(r'<h3(?: id="([^"]+)")?>(.*?)</h3>', _anchor, body, flags=re.S)
        self.subs[sid] = subs
        k = f'<p class="sec-kicker">{self.UI(f"toc.{SECTION_GROUP[sid]}")}</p>'
        if kicker:
            k += f'<p class="sec-kicker">{self.T(kicker)}</p>'
        h2 = (f'<h2><span class="sec-num">{SECTION_NUMBERS[sid]}</span>'
              f'{self.T(f"section.{sid}.title")}</h2>')
        self.out.append(f'<section class="sec" id="{sid}">{k}{h2}{body}</section>')

    def figure(self, did: str, caption_cid: str, isolate: bool = False, steps: int = 0,
               keys: bool = False, extra_html: str = "") -> str:
        model = diagrams.MODELS[did](self.f)
        parts = []
        for lg in LANGS:
            title = self.t.get(caption_cid, lg)
            parts.append(diagrams.svg(model, rtl=(lg == "ar"), lang=lg,
                                      resolve=lambda cid, lg=lg: self.t.get(cid, lg), title=title))
        iso = ' data-isolate=""' if isolate else ""
        step_bar = ""
        if steps:
            btns = "".join(f'<button type="button" data-step="{i}" aria-pressed="false">{i}</button>'
                           for i in range(1, steps + 1))
            step_bar = f'<div class="steps" data-keys="">{self.UI("steps")} {btns}</div>'
        return (f'<figure{iso}><div class="dia-wrap">{"".join(parts)}</div>{step_bar}{extra_html}'
                f'<figcaption>{self.T(caption_cid)}</figcaption></figure>')

    def figure_file(self, fid: str, caption_cid: str, title_cid: str = "", alt_prefix: str = "") -> str:
        """Plan 203 (G13): a per-item figure as sibling files, one per language and theme, embedded
        through <picture> (the dark source by media query; the script swaps on the explicit toggle)."""
        model = diagrams.file_models(self.f)[fid](self.f)
        W, H = model["w"], model["h"]
        if all(x[0] != fid for x in self.figures):     # one file per fid, however many folds embed it
            self.figures.append((fid, model, caption_cid))
        pics = []
        for lg in LANGS:
            # the labels are rendered into the files by build.py; resolve them here once so the
            # ids count as used (the missing-strings and orphan checks)
            diagrams.svg(model, rtl=(lg == "ar"), lang=lg, resolve=lambda cid, lg=lg: self.t.get(cid, lg), title="")
            head = self.t.get(title_cid, lg) if title_cid else alt_prefix
            alt = f"{head} — {self.t.get(caption_cid, lg)}"
            light, dark = f"docs/guide/figures/{fid}-{lg}.svg", f"docs/guide/figures/{fid}-{lg}-dark.svg"
            pics.append(f'<picture lang="{lg}" data-fig=""><source media="(prefers-color-scheme: dark)" srcset="{dark}">'
                        f'<img class="fig" src="{light}" data-light="{light}" data-dark="{dark}" alt="{esc(alt)}"'
                        f' width="{W}" height="{H}" loading="lazy"></picture>')
        return (f'<figure class="file"><div class="dia-wrap">{"".join(pics)}</div>'
                f'<figcaption>{self.T(caption_cid)}</figcaption></figure>')


# ------------------------------------------------------------------------------ page

FIGURES: list[tuple[str, dict, str]] = []   # plan 203: filled by render_page for build.py


def render_page(f: dict, text_table: dict, css: str, js: str) -> str:
    USED_IDS.clear()
    FIGURES.clear()
    diagrams.DIAGRAM_LABELS.clear()
    r = R(f, Text(text_table))
    v = f["version"]
    _hero(r)
    _what(r)
    _install(r)
    _actors(r)
    _modes(r)
    _stages(r)
    _workflows(r)
    _package(r)
    _families(r)
    _relations(r)
    _statuses(r)
    _tools(r)
    _gates(r)
    _readiness(r)
    _transitions(r)
    _skills(r)
    _session(r)
    _practices(r)
    _writing(r)
    _faq(r)
    _maintainer(r)
    _glossary(r)
    _about(r)
    toc = _toc(r)
    FIGURES.extend(r.figures)
    title_en, title_ar = r.t.get("ui.title", "en"), r.t.get("ui.title", "ar")
    logo_light = (diagrams_logo("logo-light.svg"))
    logo_dark = (diagrams_logo("logo-dark.svg"))
    boot = (
        "(function(){try{var s=JSON.parse(localStorage.getItem('tamheed-guide')||'{}')||{};"
        "var l=s.lang||((navigator.language||'').toLowerCase().indexOf('ar')===0?'ar':'en');"
        "var h=document.documentElement;h.lang=l;h.dir=l==='ar'?'rtl':'ltr';"
        "if(s.theme&&s.theme!=='system')h.setAttribute('data-theme',s.theme);}catch(e){}"
        "var k=document.createElement('link');k.rel='stylesheet';"
        "k.href='https://fonts.googleapis.com/css2?family=Markazi+Text:wght@400..700&family=Source+Serif+4:ital,opsz,wght@0,8..60,400..700;1,8..60,400..700&display=swap';"
        "document.head.appendChild(k);})();"
    )
    head = (
        '<!doctype html>\n<html lang="en" dir="ltr">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f'<title data-en="{esc(title_en)}" data-ar="{esc(title_ar)}">{esc(title_en)}</title>\n'
        f'<meta name="description" content="{esc(r.t.get("ui.description", "en"))}">\n'
        f'<meta name="generator" content="tamheed-guide {esc(v)}">\n'
        '<link rel="icon" href="data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2032%2032%22%3E%3Crect%20width%3D%2232%22%20height%3D%2232%22%20rx%3D%226%22%20fill%3D%22%235b3fd6%22%2F%3E%3Crect%20x%3D%222.5%22%20y%3D%2222.9%22%20width%3D%226.7%22%20height%3D%223.8%22%20rx%3D%220.9%22%20fill%3D%22%23e0e7ff%22%2F%3E%3Crect%20x%3D%228.8%22%20y%3D%2217.5%22%20width%3D%226.7%22%20height%3D%223.8%22%20rx%3D%220.9%22%20fill%3D%22%23c4b5fd%22%2F%3E%3Crect%20x%3D%2215.1%22%20y%3D%2212.0%22%20width%3D%226.7%22%20height%3D%223.8%22%20rx%3D%220.9%22%20fill%3D%22%23a78bfa%22%2F%3E%3Crect%20x%3D%2223.1%22%20y%3D%2212.6%22%20width%3D%228.4%22%20height%3D%222.5%22%20rx%3D%220.9%22%20fill%3D%22%23ede9fe%22%2F%3E%3Cpath%20d%3D%22M27.7%2010.9%20A13.9%2013.9%200%200%200%205.9%2020.0%22%20fill%3D%22none%22%20stroke%3D%22%23ffffff%22%20stroke-width%3D%221.18%22%20stroke-linecap%3D%22round%22%2F%3E%3Cpath%20d%3D%22M4.0%2019.4%20L7.8%2019.4%20L5.9%2022.3%20Z%22%20fill%3D%22%23ffffff%22%2F%3E%3C%2Fsvg%3E">\n'
        '<link rel="preconnect" href="https://fonts.googleapis.com">\n'
        '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n'
        f"<script>{boot}</script>\n<style>\n{css}</style>\n</head>\n<body>\n"
    )
    top = (
        '<header class="top">'
        f'<a class="brand" href="#top"><span class="logo-light">{logo_light}</span><span class="logo-dark">{logo_dark}</span></a>'
        f'<span class="ver">v{esc(v)}</span><span class="spacer"></span>'
        f'<div class="toggle" role="group" aria-label="Language">'
        '<button type="button" data-lang-btn="en" aria-pressed="true">English</button>'
        '<button type="button" data-lang-btn="ar" aria-pressed="false" class="ar-face">العربية</button></div>'
        f'<div class="toggle" role="group" aria-label="Theme">'
        f'<button type="button" data-theme-btn="light" aria-pressed="false">{r.UI("theme.light")}</button>'
        f'<button type="button" data-theme-btn="system" aria-pressed="true">{r.UI("theme.system")}</button>'
        f'<button type="button" data-theme-btn="dark" aria-pressed="false">{r.UI("theme.dark")}</button></div>'
        "</header>"
    )
    page = f'<div class="page" id="top">{toc}<main>{"".join(r.out)}</main></div>'
    foot = f'<footer class="footer">{r.T("ui.footer")}</footer>'
    return head + top + page + foot + f"\n<script>\n{js}</script>\n</body>\n</html>\n"


def diagrams_logo(name: str) -> str:
    from extract import BUNDLE
    svg = (BUNDLE / "assets" / name).read_text(encoding="utf-8")
    svg = re.sub(r"<\?xml[^>]*>", "", svg)
    svg = re.sub(r"<title>.*?</title>|<desc>.*?</desc>", "", svg, flags=re.S)
    svg = re.sub(r'\s(width|height)="[^"]*"', "", svg, count=2)
    return svg.strip()


SECTIONS = [
    ("what", "intro"), ("install", "intro"), ("actors", "intro"), ("modes", "use"), ("stages", "use"),
    ("workflows", "use"), ("package", "data"), ("families", "data"), ("relations", "data"),
    ("statuses", "data"), ("tools", "engine"), ("gates", "engine"), ("readiness", "engine"),
    ("transitions", "engine"), ("skills", "agents"), ("session", "agents"), ("practices", "agents"),
    ("writing", "agents"), ("faq", "agents"), ("maintainer", "appendix"), ("glossary", "appendix"),
    ("about", "appendix"),
]
SECTION_NUMBERS = {sid: i + 1 for i, (sid, _g) in enumerate(SECTIONS)}
SECTION_GROUP = dict(SECTIONS)


def _toc(r: R) -> str:
    """Plan 202 (G10): chapters as groups, numbered section links, and a closed <details> per
    section holding its H3 anchors. The script opens the active section's; with no script the
    section links alone read."""
    items, last = [], None
    for sid, group in SECTIONS:
        if group != last:
            items.append(f'<li class="toc-group">{r.UI(f"toc.{group}")}</li>')
            last = group
        link = (f'<a href="#{sid}"><span class="sec-num">{SECTION_NUMBERS[sid]}</span>'
                f'{r.T(f"section.{sid}.title")}</a>')
        subs = r.subs.get(sid, [])
        if subs:
            inner = "".join(f'<li><a href="#{aid}">{text}</a></li>' for aid, text in subs)
            items.append(f'<li data-sid="{sid}">{link}<details class="sub"><summary>{len(subs)}</summary>'
                         f'<ol>{inner}</ol></details></li>')
        else:
            items.append(f'<li data-sid="{sid}">{link}</li>')
    return (f'<nav class="toc" aria-label="Sections"><details open><summary>{r.UI("toc.contents")}</summary>'
            f'<ol>{"".join(items)}</ol></details></nav>')


# ------------------------------------------------------------------------- sections

def _hero(r: R) -> None:
    f = r.f
    stats = [
        (len(f["tools"]), "stat.tools"), (len(f["families"]), "stat.families"),
        (len(f["stages"]["stages"]), "stat.stages"), (len(f["skills"]), "stat.skills"),
    ]
    tiles = "".join(f'<div class="stat"><b>{n}</b><span>{r.UI(k)}</span></div>' for n, k in stats)
    r.out.append(
        '<section class="sec hero" id="hero">'
        f'<h1><span lang="en">Tamheed</span><span lang="ar" class="ar-name">تمهيد</span> <span class="muted">·</span> {r.T("ui.title")}</h1>'
        f'{r.P("section.hero.tagline", "tag")}{r.P("section.hero.lead", "lead")}'
        f'<div class="stats">{tiles}</div>'
        f'{r.P("section.hero.how")}</section>')


def _what(r: R) -> None:
    body = r.PS("section.what", 3)
    body += r.figure("d1", "dia.overview.caption")
    body += f'<div class="two-col"><div>{r.H(3, "section.what.is")}{r.PS("section.what.is", 3)}</div>' \
            f'<div>{r.H(3, "section.what.isnot")}{r.PS("section.what.isnot", 3)}</div></div>'
    body += f'<div class="callout">{r.P("section.what.principle")}</div>'
    r.section("what", body)


def _install(r: R) -> None:
    f = r.f
    body = r.P("section.install.1")
    body += r.H(3, "section.install.prereq") + r.P("section.install.prereq.1")
    body += r.H(3, "section.install.plugin") + r.P("section.install.plugin.1")
    body += r.pre("claude plugin marketplace add A-H-911/tamheed --scope project\n"
                  "claude plugin install tamheed@tamheed --scope project")
    body += r.P("section.install.plugin.2")
    body += r.pre("claude --plugin-dir ./plugins/tamheed")
    body += r.H(3, "section.install.scope") + r.P("section.install.scope.1")
    body += r.pre("claude plugin update tamheed@tamheed --scope project\n"
                  "# a user-scope record wins the load over the repository's own: remove it\n"
                  "claude plugin uninstall tamheed@tamheed --scope user")
    body += r.P("section.install.scope.2")
    body += r.H(3, "section.install.server") + r.P("section.install.server.1")
    body += r.pre(f["mcp"]["command"], copy=False)
    body += r.P("section.install.server.2")
    body += r.H(3, "section.install.upgrade") + r.P("section.install.upgrade.1")
    body += r.pre("claude plugin marketplace update tamheed\nclaude plugin update tamheed@tamheed --scope project")
    body += r.P("section.install.upgrade.2")
    body += r.H(3, "section.install.verify") + r.P("section.install.verify.1")
    body += r.pre("python check.py\nuv run plugins/tamheed/server/tamheed_server.py --selftest")
    r.section("install", body)


def _actors(r: R) -> None:
    body = r.PS("section.actors", 2)
    body += r.figure("d2", "dia.actors.caption", isolate=True)
    rows = [[r.T("dia.actors.operator"), r.T("section.actors.operator.may"), r.T("section.actors.operator.never")],
            [r.T("dia.actors.planner"), r.T("section.actors.planner.may"), r.T("section.actors.planner.never")],
            [r.T("dia.actors.executor"), r.T("section.actors.executor.may"), r.T("section.actors.executor.never")]]
    body += r.table([r.UI("col.actor"), r.UI("col.may"), r.UI("col.never")], rows)
    body += f'<div class="callout warn">{r.P("section.actors.word")}</div>'
    r.section("actors", body)


def _modes(r: R) -> None:
    f = r.f
    body = r.PS("section.modes", 2)
    body += r.pre("/tamheed:tamheed <project description | path/to/brief> [--mode <m>] [--profile <p>] [--package-dir <dir>]", copy=False)
    rows = []
    for m in f["modes"]["modes"]:
        rows.append([r.code(m), r.T(f"mode.{m}")])
    rows.append([r.code("stage:<id>"), r.T("mode.stage")])
    body += r.H(3, "section.modes.table") + r.table([r.UI("col.mode"), r.UI("col.what")], rows)
    body += r.H(3, "section.modes.update") + r.P("section.modes.update.1")
    body += "<ul>" + "".join(f"<li>{r.T(f'section.modes.update.{k}')}</li>"
                             for k in ("rederive", "progress", "defer", "reschedule", "reclassify", "cancel", "expand")) + "</ul>"
    rows = [[r.code(p), r.T(f"profile.{p}")] for p in f["modes"]["profiles"]]
    body += r.H(3, "section.modes.profiles") + r.P("section.modes.profiles.1") + r.table([r.UI("col.profile"), r.UI("col.what")], rows)
    body += r.P("section.modes.pkgdir")
    r.section("modes", body)


def _stages(r: R) -> None:
    f = r.f
    st = f["stages"]
    body = r.PS("section.stages", 2)
    def detail(s: dict) -> str:
        num = f"{s['n']:02d}"
        ar_title = esc(r.t.get("stagetitle." + num, "ar"))
        return (f'<div hidden data-detail="s{s["n"]}"><b class="id">{s["n"]}</b> · <b>{esc(s["title"])}</b>'
                f'<span lang="ar"> · {ar_title}</span> — {r.T("stage." + num)}</div>')
    details = "".join(detail(s) for s in st["stages"])
    body += r.figure("d3", "dia.stages.caption", isolate=True,
                     extra_html=f'<div class="stage-detail"></div>{details}')
    for p in st["phases"]:
        rows = []
        for n in p["stages"]:
            s = st["stages"][n - 1]
            mark = r.badge("human", "pk") if s["human"] else ""
            loop = r.badge("loop", "cond") if n in st["loops"] else ""
            title = f'<span lang="en">{esc(s["title"])}</span><span lang="ar">{esc(r.t.get(f"stagetitle.{n:02d}", "ar"))}</span>'
            rows.append([f'<b class="id">{n}</b>', f"{title} {mark}{loop}", r.T(f"stage.{n:02d}")])
        body += f'<h3>{r.T("phase." + p["letter"])} <span class="muted">({p["stages"][0]}–{p["stages"][-1]})</span></h3>'
        body += r.P(f"section.stages.phase.{p['letter']}")
        body += r.table([r.UI("col.n"), r.UI("col.stage"), r.UI("col.produces")], rows, "compact")
    body += f'<div class="callout">{r.P("section.stages.loops")}</div>'
    r.section("stages", body)


RECIPES = diagrams.RECIPES   # plan 203: the recipes live beside their swimlanes


def _workflows(r: R) -> None:
    f = r.f
    tools = {t['name'] for t in f['tools']}
    body = r.PS("section.workflows", 2)
    for i, (slug, names, steps) in enumerate(RECIPES, 1):
        chips = []
        for n in names:
            if n in tools:
                chips.append(f'<code>{n}</code>')
            else:
                chips.append(f'<code>/tamheed:{n}</code>')
        lis = "".join(f"<li>{r.T(f'workflow.{slug}.s{k}')}</li>" for k in range(1, steps + 1))
        fig = r.figure_file(f"wf-{slug}", "dia.wf.caption", f"workflow.{slug}.title") if slug in diagrams.SWIMLANES else ""
        body += (f'<div class="recipe" id="wf-{slug}"><h3>{i}. {r.T(f"workflow.{slug}.title")}</h3>'
                 f'<p class="who">{r.UI("recipe.when")} {r.T(f"workflow.{slug}.when")}</p>'
                 f'<p class="who">{r.UI("recipe.uses")} {" ".join(chips)}</p>{fig}<ol>{lis}</ol></div>')
    r.section("workflows", body)


def _package(r: R) -> None:
    f = r.f
    body = r.PS("section.package", 2)
    body += r.figure("d4", "dia.package.caption", isolate=True)
    body += r.pre(
        "<package>/\n"
        "├── data/              # the package: one <table>.jsonl per non-empty table; .lock while open\n"
        "├── README.md          # the stock operator guide (project prompts are rows: data/prompts.jsonl)\n"
        "├── review.html        # the human review page, exported by export_html\n"
        "├── csv/               # one CSV per table, written beside review.html\n"
        "├── exports/           # entity_export files: whole tool results, digest-stamped\n"
        "└── data-v3-backup/    # only after a v3 -> v4 package_migrate\n"
        "<target project>/\n"
        "├── .mcp.json          # target-side server config (handoff_emit)\n"
        "└── CLAUDE.md          # the tool-owned note span <!-- tamheed:note v7 --> ... <!-- /tamheed:note -->",
        copy=False)
    body += r.H(3, "section.package.canonical") + r.PS("section.package.canonical", 2)
    body += "<ul>" + "".join(f"<li>{r.T(f'section.package.rule.{k}')}</li>" for k in range(1, 8)) + "</ul>"
    body += r.H(3, "section.package.lock") + r.PS("section.package.lock", 2)
    body += r.H(3, "section.package.review") + r.P("section.package.review.1")
    rows = [[r.code(f"#{sid}"), esc(title), r.T(f"review.{sid}")] for sid, title in f["review_sections"]]
    body += r.table([r.UI("col.anchor"), r.UI("col.section"), r.UI("col.what")], rows, "compact")
    body += r.H(3, "section.package.target") + r.PS("section.package.target", 2)
    r.section("package", body)


def _col_rows(r: R, t: dict) -> list[list[str]]:
    rows = []
    for c in t["columns"]:
        flags = []
        if c["pk"]:
            flags.append(r.badge("PK", "pk"))     # a key the caller mints: neither optional nor a NOT NULL badge
        if c["server"]:
            flags.append(r.badge("server", "srv"))
        elif c["required"]:
            flags.append(r.badge("required", "req"))
        elif not c["pk"]:
            flags.append(r.badge("optional", "opt"))
        facts = []
        if c["fk"]:
            facts.append(f'→ <code>{esc(c["fk"][0])}.{esc(c["fk"][1])}</code>')
        if c["check_in"]:
            pills = " ".join(f'<span class="status-pill">{esc(v)}</span>' for v in c["check_in"])
            if c.get("check_glob"):
                pills += " " + " ".join(f'{r.UI("or")} <span class="status-pill">{esc(g)}</span>' for g in c["check_glob"])
            facts.append(pills)
        if c["nonempty"]:
            facts.append(r.badge("non-empty", "req"))
        if c["default"] is not None:
            facts.append(f'{r.UI("default")} <code>{esc(str(c["default"]))}</code>')
        if c["block"]:
            facts.append(f'<span class="badge block"><a href="#block-{c["block"]}">{c["block"]}</a></span>')
        if c["block"]:
            cid = f"col.{t['table']}.{c['name']}"
            desc = r.T(cid) if cid in r.t.table else r.T(f"block.{c['block']}.{c['name']}")
        else:
            desc = r.T(f"col.{t['table']}.{c['name']}")
        rows.append([f'<code>{esc(c["name"])}</code>', f'<span class="mono muted">{esc(c["type"])}</span> {" ".join(flags)}',
                     " ".join(facts), desc])
    return rows


def _families(r: R) -> None:
    f = r.f
    body = r.PS("section.families", 3)
    classes = ["Always", "Conditional", "Continuous", "On-request"]
    counts = {c: sum(1 for x in f['families'] if x['cls'] == c) for c in classes}
    chips = f'<button type="button" class="chip" data-class="all" aria-pressed="true">{r.UI("all")} ({len(f["families"])})</button>'
    for c in classes:
        chips += f'<button type="button" class="chip" data-class="{c}" aria-pressed="false">{r.T(f"ui.class.{c}")} ({counts[c]})</button>'
    body += r.H(3, "section.families.classes") + "<ul>" + "".join(
        f'<li><b>{esc(c)}</b> — {r.T(f"ui.classdef.{c}")}</li>' for c in classes + ["Derived"]) + "</ul>"
    body += r.H(3, "section.families.legend") + r.P("section.families.legend.1")
    body += ("<ul>"
             f'<li>{r.badge("required", "req")} — {r.T("ui.legend.required")}</li>'
             f'<li>{r.badge("server", "srv")} — {r.T("ui.legend.server")}</li>'
             f'<li>{r.badge("optional", "opt")} — {r.T("ui.legend.optional")}</li>'
             f'<li>{r.badge("PK", "pk")} — {r.T("ui.legend.pk")}</li>'
             f'<li><span class="status-pill">Value</span> — {r.T("ui.legend.check")}</li>'
             f'<li>→ <code>table.column</code> — {r.T("ui.legend.fk")}</li></ul>')
    # shared blocks
    body += r.H(3, "section.families.blocks") + r.P("section.families.blocks.1")
    block_cols = {b: [] for b in ("LIFE", "DISP", "SRC", "TAIL")}
    for t in f["schema"]["tables"]:
        for c in t["columns"]:
            if c["block"]:
                block_cols[c["block"]].append((t["table"], c))
    for b, items in block_cols.items():
        tables = sorted({tbl for tbl, _ in items})
        cols = {}
        for tbl, c in items:
            cols.setdefault(c["name"], c)
        rows = [[f'<code>{esc(n)}</code>', f'<span class="mono muted">{esc(c["type"])}</span>',
                 " ".join(f'<span class="status-pill">{esc(v)}</span>' for v in (c["check_in"] or [])) if b != "LIFE" else r.T("ui.block.life.values"),
                 r.T(f"block.{b}.{n}")] for n, c in cols.items()]
        body += (f'<details class="blk" id="block-{b}"><summary>{b} — {r.T(f"section.families.block.{b}")} '
                 f'<span class="muted">({len(tables)} {r.UI("tables")})</span></summary><div class="body">'
                 f'{r.P(f"section.families.block.{b}.1")}'
                 f'{r.table([r.UI("col.column"), r.UI("col.type"), r.UI("col.values"), r.UI("col.meaning")], rows, "compact")}'
                 f'<p class="muted">{r.UI("block.on")} {", ".join(f"<code>{esc(x)}</code>" for x in tables)}</p></div></details>')
    # explorer
    body += r.H(3, "section.families.explorer") + r.P("section.families.explorer.1")
    body += (f'<div class="fam-tools"><div class="chips" id="fam-filter">{chips}</div>'
             f'<input id="fam-search" type="search" placeholder="FR-, requirements, waiver…" aria-label="Search families"></div>')
    by_table = {x['table']: x for x in f['families']}
    file_models = diagrams.file_models(f)
    for t in f["schema"]["tables"]:
        fam = by_table.get(t["table"])
        cls = fam["cls"] if fam else "Store"
        hue = f"var(--a{t['hue']})" if t["hue"] else "var(--ink-2)"
        prefix = fam["prefix"] if fam else ""
        if t["table"] == "requirements":
            prefix = "FR- / NFR-"
        search = " ".join(filter(None, [t["table"], fam["type"] if fam else "", prefix, fam["label"] if fam else "", cls]))
        glob = " ".join(f"<code>{esc(g)}</code>" for g in t["id_globs"])
        head = (f'<span class="prefix">{esc(prefix) or esc(t["table"])}</span>'
                f'<span class="lbl">{esc(fam["label"]) if fam else r.T("ui.storetable")}</span>'
                f'<span class="tbl-name">{esc(t["table"])}</span>'
                f'<span class="chip"><span class="dot"></span>{r.T(f"ui.class.{cls}") if fam else r.UI("kind.store")}</span>')
        inner = r.P(f"type.{fam['type']}") if fam else ""
        inner += r.P(f"table.{t['table']}")
        meta = []
        if glob:
            meta.append(f'{r.UI("idformat")}: {glob}')
        if fam:
            meta.append(f'{r.UI("typeid")}: <code>{esc(fam["type"])}</code>')
        meta.append(f'{r.UI("primarykey")}: {", ".join(f"<code>{esc(p)}</code>" for p in t["pk"])}')
        if t["table_checks"]:
            meta.append(f'{r.UI("tablechecks")}: ' + " ".join(f"<code>{esc(x)}</code>" for x in t["table_checks"]))
        inner += '<p class="muted">' + " · ".join(meta) + "</p>"
        inner += r.table([r.UI("col.column"), r.UI("col.type"), r.UI("col.constraints"), r.UI("col.meaning")],
                         _col_rows(r, t), "compact")
        if fam:   # plan 204 (G4): the family's typed relations, or the sentence that there are none
            ftype = fam["type"]
            if f"rel-{ftype}" in file_models:
                inner += r.figure_file(f"rel-{ftype}", "dia.rel.caption", alt_prefix=fam["label"])
            else:
                inner += r.P("ui.rel.none", "muted")
            inner += r.H(4, "ui.data.heading") + r.figure_file(f"data-{ftype}", "dia.data.caption", alt_prefix=fam["label"])
            inner += r.H(4, "ui.trace.heading")
            if f"trace-{ftype}" in file_models:
                inner += r.figure_file(f"trace-{ftype}", "dia.trace.caption", alt_prefix=fam["label"])
            else:
                inner += r.P("ui.trace.none", "muted")
            life = diagrams.lifecycle_of(f, ftype)
            if life in ("STD8", "STD9"):
                inner += f'<p class="muted">{r.T("ui.life.link")}: <a href="#statuses"><code>{life}</code></a></p>'
            elif life:
                pills = " ".join(f'<span class="status-pill">{esc(v)}</span>' for v in f["lifecycles"]["domain"][life])
                inner += f'<p class="muted">{r.T("ui.life.link")}: {pills}</p>'
            else:
                inner += r.P("ui.life.none", "muted")
        body += (f'<details class="fam" id="fam-{t["table"]}" data-class="{esc(cls)}" data-search="{esc(search)}" '
                 f'style="--hue:{hue}"><summary>{head}</summary><div class="body">{inner}</div></details>')
    # triggers and views
    body += r.H(3, "section.families.triggers") + r.P("section.families.triggers.1")
    rows = [[r.code(tr), r.T(f"trigger.{tr}")] for tr in f["schema"]["named_triggers"]]
    body += r.table([r.UI("col.trigger"), r.UI("col.what")], rows, "compact")
    body += r.H(3, "section.families.views") + r.P("section.families.views.1")
    rows = [[r.code(vw), r.T(f"view.{vw}")] for vw in f["schema"]["views"]]
    body += r.table([r.UI("col.view"), r.UI("col.what")], rows, "compact")
    r.section("families", body)


def _relations(r: R) -> None:
    f = r.f
    body = r.PS("section.relations", 3)
    chips = "".join(f'<button type="button" class="chip" data-key="{esc(x["relation"])}">{esc(x["relation"])}</button>'
                    for x in f["relations"] if not x.get("fallback") and not x["same_type"])
    legend = "".join(f'<li><b>{r.T(f"dia.relations.h.{b}")}</b>: ' + ", ".join(f"<code>{esc(t)}</code>" for t in types) + "</li>"
                     for b, types in diagrams.BUCKETS)
    body += r.figure("d5", "dia.relations.caption", isolate=True, extra_html=f'<div class="chips">{chips}</div>')
    body += f'<ul class="buckets">{legend}</ul>' + r.P("section.relations.buckets.1")
    rows = []
    for x in f["relations"]:
        if x.get("fallback"):
            frm, to = r.UI("any"), r.UI("any")
        elif x["same_type"]:
            frm = to = r.UI("sametype")
        else:
            frm = ", ".join(f"<code>{esc(a)}</code>" for a in x["from"])
            to = ", ".join(f"<code>{esc(a)}</code>" for a in x["to"])
        rows.append([r.code(x["relation"]), frm, to, r.T(f"rel.{x['relation']}")])
    body += r.table([r.UI("col.relation"), r.UI("col.from"), r.UI("col.to"), r.UI("col.meaning")], rows, "compact")
    body += f'<div class="callout">{r.P("section.relations.retire")}</div>'
    r.section("relations", body)


def _statuses(r: R) -> None:
    f = r.f
    lc = f["lifecycles"]
    body = r.PS("section.statuses", 2)
    body += r.figure("d6", "dia.status.caption")
    body += r.H(3, "section.statuses.standard") + r.P("lifecycle.STD8")
    body += r.figure_file("life-STD8", "dia.life.caption")
    rows = [[f'<span class="status-pill">{esc(s)}</span>', r.T(f"status.{s}")] for s in lc["STD9"]["values"]]
    body += r.table([r.UI("col.status"), r.UI("col.meaning_only")], rows, "compact")
    body += (f'<p>{r.UI("std8.on")} {", ".join(f"<code>{esc(x)}</code>" for x in lc["STD8"]["tables"])}.</p>'
             f'<p>{r.T("lifecycle.STD9")} {", ".join(f"<code>{esc(x)}</code>" for x in lc["STD9"]["tables"])}.</p>')
    body += r.H(3, "section.statuses.domain") + r.P("section.statuses.domain.1")
    rows = [[r.code(tbl), " ".join(f'<span class="status-pill">{esc(v)}</span>' for v in vals),
             r.T(f"col.{tbl}.lifecycle_status") if f"col.{tbl}.lifecycle_status" in r.t.table else r.T(f"table.{tbl}")]
            for tbl, vals in lc["domain"].items()]
    body += r.table([r.UI("col.table"), r.UI("col.values"), r.UI("col.meaning")], rows, "compact")
    body += r.H(3, "section.statuses.axes") + r.PS("section.statuses.axes", 2)
    vs = f["verdicts"]
    rows = [[f'<span class="status-pill">{esc(v)}</span>', r.T(f"verdict.{v}")] for v in vs["audit_verdicts"]]
    body += r.H(4, "section.statuses.verdicts") + r.table([r.UI("col.verdict"), r.UI("col.meaning_only")], rows, "compact")
    r.section("statuses", body)


def _tools(r: R) -> None:
    f = r.f
    file_models = diagrams.file_models(f)
    body = r.PS("section.tools", 3)
    for g in ("read", "mutate", "staged", "export"):
        body += r.H(3, f"toolgroup.{g}", f"tools-{g}")
        for t in [x for x in f["tools"] if x["group"] == g]:
            rows = []
            for p in t["params"]:
                req = r.badge("required", "req") if p["required"] else f'{r.UI("default")} <code>{esc(p["default"])}</code>'
                rows.append([r.code(p["name"]), f'<span class="mono muted">{esc(p["annotation"])}</span>', req,
                             r.T(f"param.{t['name']}.{p['name']}")])
            params = r.table([r.UI("col.param"), r.UI("col.type"), r.UI("col.required"), r.UI("col.meaning_only")], rows, "compact") if rows else f'<p class="muted">{r.UI("noparams")}</p>'
            body += (f'<div class="card" id="tool-{t["name"]}"><h4><code>{esc(t["name"])}</code></h4>'
                     f'<p class="muted" lang="en" dir="ltr">“{esc(t["desc"])}”</p>'
                     f'<p class="muted" lang="ar"><span dir="ltr" style="unicode-bidi:isolate">“{esc(t["desc"])}”</span></p>'
                     f'{r.P("tool." + t["name"])}{params}'
                     f'{r.figure_file("fx-" + t["name"], "dia.fx.caption", alt_prefix=t["name"])}'
                     + (r.figure_file("seq-" + t["name"], "dia.seq.caption", alt_prefix=t["name"])
                        if "seq-" + t["name"] in file_models else r.P("ui.seq.none", "muted"))
                     + '</div>')
    body += r.H(3, "section.tools.upsert") + r.PS("section.tools.upsert", 2)
    rows = [[r.code(k), r.T(f"meta.{k}")] for k in f["header"]["meta_keys"]]
    body += r.table([r.UI("col.key"), r.UI("col.meaning_only")], rows, "compact")
    body += r.H(3, "section.tools.header") + r.P("section.tools.header.1")
    body += (f'<p>{r.UI("header.writable")} {", ".join(f"<code>{esc(x)}</code>" for x in f["header"]["writable"])}. '
             f'{r.UI("header.frozen")} {", ".join(f"<code>{esc(x)}</code>" for x in f["header"]["frozen"])}.</p>')
    body += r.P("section.tools.header.2")
    r.section("tools", body)


def _gates(r: R) -> None:
    f = r.f
    body = r.PS("section.gates", 2)
    body += r.figure_file("gates-pipeline", "dia.pipe.caption")
    for tier in ("mechanical", "judgment", "warn"):
        rows = [[f'<b class="id">{esc(g)}</b>', r.T(f"gate.{g}")] for g in f["gates"][tier]]
        body += r.H(3, f"gatetier.{tier}") + r.table([r.UI("col.gate"), r.UI("col.what")], rows, "compact")
        for g in f["gates"][tier]:        # plan 207: one fold per gate holding its figure
            body += (f'<details class="fold" id="gatefig-{esc(g)}"><summary><span class="prefix">{esc(g)}</span>'
                     f'<span class="lbl">{r.UI("gate.fold")}</span></summary><div class="body">'
                     f'{r.figure_file("gate-" + g, "dia.gate.caption", alt_prefix=g)}</div></details>')
    body += f'<div class="callout">{r.P("section.gates.ready")}</div>'
    r.section("gates", body)


def _readiness(r: R) -> None:
    f = r.f
    body = r.PS("section.readiness", 3)
    body += r.pre('readiness_check(scope="package")\nreadiness_check(scope="phase", id="PH-1")\nreadiness_check(scope="slice", id="SL-001")', copy=False)
    for scope in ("package", "phase", "slice"):
        rows = []
        for x in f["rules"][scope]:
            b = r.badge(x["severity"], x["severity"])
            if x["conditional"]:
                b += " " + r.badge("conditional", "cond")
            rows.append([f'<b class="id">{esc(x["rule"])}</b>', b, r.T("rule." + x["rule"])])
        body += r.H(3, f"section.readiness.scope.{scope}")
        body += r.P(f"section.readiness.scope.{scope}.1")
        body += r.table([r.UI("col.rule"), r.UI("col.severity"), r.UI("col.what")], rows, "compact")
    body += r.H(3, "section.readiness.statuses") + r.P("section.readiness.statuses.1")
    rows = [[f'<span class="status-pill">{esc(s)}</span>', r.T(f"rstatus.{s}")] for s in f["verdicts"]["readiness_statuses"]]
    body += r.table([r.UI("col.status"), r.UI("col.meaning_only")], rows, "compact")
    body += r.pre("ready = not indeterminate and not any(rule.severity == 'blocking' and rule.status == 'fail')", copy=False)
    body += r.H(3, "section.readiness.waivers") + r.PS("section.readiness.waivers", 2)
    body += r.H(3, "section.readiness.human") + r.PS("section.readiness.human", 2)
    body += r.H(3, "section.readiness.gonogo") + r.PS("section.readiness.gonogo", 2)
    r.section("readiness", body)


def _transitions(r: R) -> None:
    f = r.f
    body = r.PS("section.transitions", 2)
    body += f'<p>{r.tier("engine")} {r.T("ui.tier.engine.def")}</p><p>{r.tier("agent")} {r.T("ui.tier.agent.def")}</p>'
    body += r.figure("d7", "dia.guard.caption", steps=diagrams.STEPS["d7"])
    body += r.H(3, "section.transitions.engine")
    items = ["guard", "force", "create", "lessons", "feedback", "skills", "header", "journal", "edges", "expect", "substitute", "lock", "stale", "inject", "open"]
    body += "<ul>" + "".join(f'<li>{r.tier("engine")} {r.T(f"section.transitions.engine.{k}")}</li>' for k in items) + "</ul>"
    body += r.H(4, "section.transitions.triggers")
    body += "<ul>" + "".join(f'<li>{r.tier("engine")} <code>{esc(t)}</code> — {r.T(f"trigger.{t}")}</li>' for t in f["schema"]["named_triggers"]) + "</ul>"
    body += r.H(3, "section.transitions.events") + r.P("section.transitions.events.1")
    rows = []
    for e in f["events"]["all"]:
        who = r.badge("server only", "srv") if e in f["events"]["server_only"] else r.badge("caller", "opt")
        rows.append([f'<span class="status-pill">{esc(e)}</span>', who, r.T(f"event.{e}")])
    body += r.table([r.UI("col.event"), r.UI("col.who"), r.UI("col.meaning")], rows, "compact")
    body += r.H(3, "section.transitions.agent")
    items = ["force", "waivers", "evidence", "stop", "obligations", "tools", "shas", "scope"]
    body += "<ul>" + "".join(f'<li>{r.tier("agent")} {r.T(f"section.transitions.agent.{k}")}</li>' for k in items) + "</ul>"
    r.section("transitions", body)


def _skills(r: R) -> None:
    f = r.f
    body = r.PS("section.skills", 2)
    for g in ("front", "scenario", "discipline"):
        body += r.H(3, f"skillgroup.{g}", f"skills-{g}") + r.P(f"skillgroup.{g}.1")
        rows = []
        for s in [x for x in f["skills"] if x["group"] == g]:
            how = []
            if s["slash"]:
                how.append(r.code(f"/tamheed:{s['name']}" + (f" {s['arg_hint']}" if s["arg_hint"] else "")))
            if s["model"]:
                how.append(r.badge("model-invoked", "srv"))
            if not s["model"]:
                how.append(r.badge("operator only", "req"))
            rows.append([f'<b>{esc(s["name"])}</b><br><span class="muted" lang="en" dir="ltr">{esc(s["description"])}</span>'
                         f'<span class="muted" lang="ar"><span dir="ltr" style="unicode-bidi:isolate;display:inline-block;text-align:left">{esc(s["description"])}</span></span>',
                         " ".join(how), r.T(f"skill.{s['name']}")])
        body += r.table([r.UI("col.skill"), r.UI("col.invoke"), r.UI("col.when")], rows, "compact")
        for s in [x for x in f["skills"] if x["group"] == g]:   # plan 208: one fold per skill holding its strip
            body += (f'<details class="fold" id="skillfig-{esc(s["name"])}"><summary><span class="prefix">{esc(s["name"])}</span>'
                     f'<span class="lbl">{r.UI("skill.fold")}</span></summary><div class="body">'
                     f'{r.figure_file("skill-" + s["name"], "dia.skills.strip.caption", alt_prefix=s["name"])}</div></details>')
    body += r.H(3, "section.skills.matrix") + r.P("section.skills.matrix.1")
    body += r.figure_file("skills-matrix", "dia.skills.matrix.caption")
    body += r.H(3, "section.skills.lifecycle") + r.P("section.skills.lifecycle.1")
    body += r.figure_file("skills-lifecycle", "dia.skills.life.caption")
    body += r.H(3, "section.skills.styles") + r.PS("section.skills.styles", 2)
    body += r.pre("ITERATION: wbs=<id> slice=<id> acs_moved=<n> gate=<pass|fail> ready=<true|false> stop=<reason|none> lessons_pending=<n>", copy=False)
    body += r.P("section.skills.styles.3")
    r.section("skills", body)


def _session(r: R) -> None:
    f = r.f
    h = f["hook"]
    body = r.PS("section.session", 2)
    body += r.figure("d8", "dia.session.caption", steps=diagrams.STEPS["d8"])
    body += r.H(3, "section.session.hook") + r.P("section.session.hook.1")
    body += r.table([r.UI("col.field"), r.UI("col.value")], [
        [r.code("event"), r.code(h["event"])], [r.code("matcher"), r.code(h["matcher"])],
        [r.code("command"), r.code(h["command"])], [r.code("commandWindows"), r.code(h["commandWindows"])],
        [r.code("timeout"), r.code(str(h["timeout"]))]], "compact")
    body += r.P("section.session.hook.2")
    body += r.H(3, "section.session.handoff") + r.PS("section.session.handoff", 2)
    body += r.H(3, "section.session.resume") + r.PS("section.session.resume", 2)
    r.section("session", body)


PRACTICES = ["read-first", "full-rows", "expect-unchanged", "substitute", "paste", "evidence", "review",
             "register-first", "scope-first", "edges", "lessons", "feedback", "exports", "git", "close",
             "operator", "markers", "one-session"]


def _practices(r: R) -> None:
    body = r.P("section.practices.1")
    body += "<ol>" + "".join(f'<li>{r.T(f"practice.{k}")}</li>' for k in PRACTICES) + "</ol>"
    r.section("practices", body)


def _writing(r: R) -> None:
    """Plan 188 (R22): the writing discipline, with the vocabulary tables rendered FROM
    references/vocabulary.md (extract.vocabulary); build.py asserts the EN cells equal the file."""
    v = r.f["vocabulary"]
    body = r.PS("section.writing", 3)
    body += r.H(3, "section.writing.actions")
    rows = [[r.T(f"vocab.action.{a['slug']}"), r.code(a["verb"]), md(a["rejected"])] for a in v["actions"]]
    body += r.table([r.UI("col.action"), r.UI("col.verb"), r.UI("col.rejected")], rows, "compact")
    body += r.H(3, "section.writing.terms")
    rows = [[r.code(t["term"]), r.T(f"vocab.term.{t['slug']}"), r.T(f"vocab.never.{t['slug']}")] for t in v["terms"]]
    body += r.table([r.UI("col.term"), r.UI("col.means"), r.UI("col.nevermeans")], rows, "compact")
    body += r.H(3, "section.writing.names") + r.P("section.writing.names.1")
    rows = [[r.code(n["name"]), r.T(f"vocab.name.{n['slug']}")] for n in v["names"]]
    body += r.table([r.UI("col.name"), r.UI("col.where")], rows, "compact")
    r.section("writing", body)


FAQ = ["locked", "stale", "pre-v4", "uv", "silent-hook", "old-descriptions", "indeterminate", "not-null",
       "unknown-key", "g-complete", "g-rel", "forced", "review-not-done", "waiver", "github-page"]


def _faq(r: R) -> None:
    body = r.P("section.faq.1")
    for k in FAQ:
        body += f'<details class="blk"><summary>{r.T(f"faq.{k}.q")}</summary><div class="body">{r.P(f"faq.{k}.a")}</div></details>'
    r.section("faq", body)


def _maintainer(r: R) -> None:
    f = r.f
    m = f["maintainer"]
    body = r.PS("section.maintainer", 2)
    body += r.pre("python check.py            # everything CI runs\npython check.py lint       # one gate")
    body += r.H(3, "section.maintainer.gates")
    rows = [[r.code(g), r.T(f"checkgate.{g}")] for g in m["gates"]]
    body += r.table([r.UI("col.gate"), r.UI("col.what")], rows, "compact")
    body += r.H(3, "section.maintainer.lints") + r.P("section.maintainer.lints.1")
    rows = [[f'<b class="id">{n}</b>', f'<span class="muted" lang="en" dir="ltr">{esc(txt)}</span><span class="muted" lang="ar"><span dir="ltr" style="unicode-bidi:isolate;display:inline-block;text-align:left">{esc(txt)}</span></span>', r.T(f"lint.{n:02d}")] for n, txt in m["lints"]]
    body += r.table([r.UI("col.n"), r.UI("col.source"), r.UI("col.what")], rows, "compact")
    body += r.H(3, "section.maintainer.suites") + r.P("section.maintainer.suites.1")
    rows = [[r.code(s), r.T(f"suite.{s}")] for s in m["suites"]]
    body += r.table([r.UI("col.suite"), r.UI("col.what")], rows, "compact")
    body += r.H(3, "section.maintainer.evals") + r.PS("section.maintainer.evals", 2)
    body += r.H(3, "section.maintainer.lab") + r.PS("section.maintainer.lab", 2)
    body += r.H(3, "section.maintainer.release") + r.P("section.maintainer.release.1")
    body += "<ol>" + "".join(f'<li>{r.T(f"section.maintainer.release.s{k}")}</li>' for k in range(1, 10)) + "</ol>"
    body += r.H(3, "section.maintainer.guide") + r.PS("section.maintainer.guide", 3)
    body += r.pre("python docs/guide/build.py            # rebuild index.html\npython docs/guide/build.py --missing  # ids still lacking EN or AR prose\npython tests/test_user_guide.py       # byte-twin + coverage + runtime witness")
    r.section("maintainer", body)


GLOSSARY = ["package", "operator", "operator-word", "binding", "canonical", "register", "family", "always",
            "omission", "provenance", "marker", "trace-edge", "slice", "wbs", "ac", "verdict", "latest-met",
            "review-status", "implemented", "readiness", "indeterminate", "waiver", "human-required",
            "go-no-go", "handoff", "resume-block", "lesson", "feedback", "stock", "note-span", "lock",
            "digest", "drift"]


def _glossary(r: R) -> None:
    body = r.P("section.glossary.1")
    body += '<dl class="defs">' + "".join(
        f'<dt>{r.T(f"glossary.{k}.term")}</dt><dd>{r.T(f"glossary.{k}.def")}</dd>' for k in GLOSSARY) + "</dl>"
    r.section("glossary", body)


def _about(r: R) -> None:
    f = r.f
    body = r.P("section.about.1")
    body += (f'<p>{r.UI("about.version")} <b class="id">{esc(f["version"])}</b> · {r.UI("about.schema")} '
             f'<b class="id">{f["schema"]["schema_version"]}</b> · {r.UI("about.license")} MIT · '
             f'<a href="https://github.com/A-H-911/tamheed">github.com/A-H-911/tamheed</a></p>')
    body += r.P("section.about.2") + r.P("section.about.3")
    r.section("about", body)
