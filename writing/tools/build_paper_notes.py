#!/usr/bin/env python3
"""Build the Paper Notes hub and complete Chinese and English article pages."""
import argparse
from datetime import date
import html
import hashlib
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
BASE_URL = "https://mkj69.github.io/"
LAYOUT_QUERY = "?layout=single-column-en"
HOME_START = "<!-- PAPER_NOTES_LINK:START -->"
HOME_END = "<!-- PAPER_NOTES_LINK:END -->"


def esc(value):
    return html.escape(str(value), quote=True)


def public_url(value):
    if not isinstance(value, str):
        return False
    try:
        url = urlsplit(value)
        return url.scheme == "https" and bool(url.hostname) and not url.username and not url.password
    except ValueError:
        return False


def load_renderer():
    path = Path(__file__).with_name("render_paper.py")
    spec = importlib.util.spec_from_file_location("paper_blocks", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def number_tokens(value):
    return re.findall(r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", str(value).replace("−", "-"))


def validate_pair(zh, en, paper):
    if not zh.get("pages") or len(zh["pages"]) != len(en.get("pages", [])):
        raise ValueError("Both languages must cover the same substantive sections")
    for data in (zh, en):
        if data.get("title") != paper["paper_title"]:
            raise ValueError("The displayed title must be the formal paper title: " + paper["slug"])
        if data.get("subtitle"):
            raise ValueError("A second title or subtitle is not part of this reading layout")
        if not public_url(data["metadata"].get("source_url")):
            raise ValueError("A verified public source URL is required")
    for zp, ep in zip(zh["pages"], en["pages"]):
        if len(zp["columns"]) != len(ep["columns"]):
            raise ValueError("Bilingual column coverage differs")
        for zc, ec in zip(zp["columns"], ep["columns"]):
            if len(zc["blocks"]) != len(ec["blocks"]):
                raise ValueError("Bilingual block coverage differs")
            for zb, eb in zip(zc["blocks"], ec["blocks"]):
                if zb["type"] != eb["type"]:
                    raise ValueError("Bilingual block types differ")
                if zb["type"] == "figure" and zb["src"] != eb["src"]:
                    raise ValueError("Both languages must retain the same actual figure")
                if zb["type"] == "formula" and (zb.get("plain"), zb.get("latex")) != (eb.get("plain"), eb.get("latex")):
                    raise ValueError("The mathematical statement differs between languages")
                if zb["type"] == "table":
                    if len(zb["headers"]) != len(eb["headers"]) or len(zb["rows"]) != len(eb["rows"]):
                        raise ValueError("A bilingual table lost rows or columns")
                    for zr, er in zip(zb["rows"], eb["rows"]):
                        if len(zr) != len(er):
                            raise ValueError("A bilingual table row changed width")
                        for z, e in zip(zr, er):
                            if number_tokens(z) != number_tokens(e):
                                raise ValueError("A numeric table cell changed in translation")


def languages():
    return ('<div class="paper-language-controls" role="group" aria-label="语言 / Language">'
            '<button type="button" data-paper-language="zh" lang="zh-CN" aria-pressed="false">中文</button>'
            '<button type="button" data-paper-language="en" lang="en" aria-pressed="true">English</button></div>')


def language_text(zh, en, tag="span", class_name=""):
    style = ' class="' + esc(class_name) + '"' if class_name else ""
    return (f'<{tag}{style} data-paper-language-content="zh" lang="zh-CN" hidden>{esc(zh)}</{tag}>'
            f'<{tag}{style} data-paper-language-content="en" lang="en">{esc(en)}</{tag}>')


def document(title, body, depth, canonical):
    prefix = "../" * depth
    assets = "assets/" if depth == 1 else "../../assets/"
    revisions = {ext: hashlib.sha256((ROOT / 'writing' / 'assets' / ('paper-notes.' + ext)).read_bytes()).hexdigest()[:12] for ext in ('css', 'js')}
    font_links = "\n".join(re.findall(r'<link\b[^>]*href="https://fonts\.(?:googleapis|gstatic)\.com[^\"]*"[^>]*>', (ROOT / "index.html").read_text()))
    return ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>' + esc(title) + ' | Kaijing Ma</title>'
            '<link rel="canonical" href="' + esc(canonical) + '">'
            + font_links +
            '<link rel="icon" href="' + prefix + 'assets/favicon.svg" type="image/svg+xml">'
            '<link rel="stylesheet" href="' + assets + 'paper-notes.css?v=' + revisions['css'] + '">'
            '<script src="' + assets + 'paper-notes.js?v=' + revisions['js'] + '" defer></script>\n</head>\n'
            '<body class="paper-notes-site"><div class="notes-site-shell">'
            '<header class="notes-site-header"><a class="site-brand" href="' + prefix + '">Kaijing Ma</a>'
            '<nav aria-label="Site navigation"><a href="' + ("./" if depth == 1 else "../../") + LAYOUT_QUERY + '">Paper Notes</a>'
            '<a href="' + prefix + '#writing">Writing</a><a href="' + prefix + '">Home</a></nav></header>'
            + body + '<footer class="notes-site-footer"><span>Kaijing Ma</span><a href="' + prefix + '#writing">Writing &amp; Projects</a></footer>'
            '</div></body>\n</html>\n')


def render_hub(papers):
    entries = []
    for number, paper in enumerate(papers, 1):
        source = paper.get("source_label", "Source paper")
        topics = "".join("<li>" + esc(topic) + "</li>" for topic in paper.get("topics", []))
        entries.append('<article class="paper-entry"><span class="paper-number" aria-hidden="true">'
                       + str(number).zfill(2) + '</span><div class="paper-entry-main"><h2><a href="papers/'
                       + paper["slug"] + '/' + LAYOUT_QUERY + '" lang="en">' + esc(paper["paper_title"]) + '</a></h2>'
                       + language_text(paper["summary_zh"], paper["summary"], "p", "paper-summary")
                       + '<p class="paper-meta">' + esc(paper["authors"]) + ' · <a href="' + esc(paper["source_url"])
                       + '">' + esc(source) + '</a></p><ul class="paper-topics" aria-label="Topics">' + topics
                       + '</ul></div><a class="paper-entry-link" href="papers/' + paper["slug"] + '/' + LAYOUT_QUERY + '">'
                       + language_text("论文精读", "Reading note") + ' <span aria-hidden="true">↗</span></a></article>')
    body = ('<main class="paper-hub" data-paper-reader data-language="en"><header class="notes-hero">'
            '<p class="eyebrow">Writing / Research</p><h1 lang="en">Paper Notes</h1>'
            + language_text("每篇精读将问题、方法、公式与证据连起来。原图、数据表和局限保留在相应论证旁边。",
                            "Each note connects the question, method, and evidence. Figures, equations, and tables stay with the relevant argument.",
                            "p", "notes-intro")
            + '</header><div class="reader-toolbar">' + language_text(str(len(papers)) + " 篇精读", str(len(papers)) + " reading notes")
            + languages() + '</div><div class="paper-list">' + "\n".join(entries)
            + '</div><p class="reader-status sr-only" role="status" aria-live="polite"></p></main>')
    return document("Paper Notes", body, 1, BASE_URL + "writing/")


def render_language(data, paper, language, renderer, output):
    meta = data["metadata"]
    source_url = meta["source_url"]
    source_label = meta.get("source_label", "Source paper")
    panel_id = paper["slug"] + "-" + language
    nav = "".join('<li><a href="#' + panel_id + '-page-' + str(i + 1) + '">' + str(i + 1) + ' · ' + esc(page["title"]) + '</a></li>'
                  for i, page in enumerate(data["pages"]))
    result = ['<section class="paper-language-panel" data-paper-language-content="' + language + '" lang="'
              + ("zh-CN" if language == "zh" else "en") + '"' + (" hidden" if language == "zh" else "") + '>',
              '<nav class="paper-contents" aria-label="' + ("本文目录" if language == "zh" else "On this page") + '"><ol>' + nav + '</ol></nav>',
              '<div class="bibliography"><p>' + esc(meta.get("authors", "")) + '</p><p>'
              + esc(meta.get("venue", "")) + ' · ' + esc(meta.get("version", "")) + '</p><p><a href="'
              + esc(source_url) + '">' + esc(source_label) + '</a>']
    if public_url(meta.get("code")):
        result.append(' · <a href="' + esc(meta["code"]) + '">' + ("作者代码" if language == "zh" else "Author code") + '</a>')
    result.append('</p></div>')
    for index, page in enumerate(data["pages"], 1):
        heading_id = panel_id + "-page-" + str(index)
        result.append('<article class="sheet" id="' + heading_id + '" aria-labelledby="' + heading_id + '-heading">'
                      '<header class="running"><h2 id="' + heading_id + '-heading">' + esc(page["title"]) + '</h2></header>'
                      '<div class="page-columns' + (' overview' if page.get("layout") == "overview" else '') + '">')
        for column in page["columns"]:
            result.append('<section class="column">')
            opened = False
            last_heading = page["title"]
            for block in column["blocks"]:
                if block["type"] == "heading":
                    last_heading = block["text"]
                    if opened:
                        result.append('</section>')
                        opened = False
                    if page.get("layout") == "overview":
                        color = block.get("color", "blue")
                        if color not in ("blue", "pink", "orange", "green", "gray"):
                            color = "blue"
                        result.append('<section class="callout ' + color + '">')
                        opened = True
                if block["type"] == "table" and not block.get("caption"):
                    block = {**block, "caption": last_heading}
                rendered = renderer.block_html(block, output)
                if language == "en":
                    rendered = rendered.replace('aria-label="放大：', 'aria-label="Enlarge: ')
                result.append(rendered)
            if opened:
                result.append('</section>')
            result.append('</section>')
        result.append('</div><footer class="page-foot"><span>' + str(index) + ' / ' + str(len(data["pages"]))
                      + '</span><span>' + esc(meta.get("version", "")) + '</span></footer></article>')
    credit = ("原图与数据来自原论文。解释与比较属于阅读笔记。版本和图表编号随正文标明。" if language == "zh" else
              "Original figures and data come from the cited paper. Explanations and comparisons are reading notes. Source versions and figure labels appear beside the material.")
    result.append('<p class="edition">' + credit + '</p></section>')
    return "\n".join(result)


def render_paper(paper, zh, en, renderer, output):
    body = ('<main class="paper-note-reader" data-paper-reader data-language="en"><header class="notes-hero">'
            '<p class="eyebrow">Paper Notes</p><h1 lang="en">' + esc(paper["paper_title"]) + '</h1></header>'
            '<div class="reader-toolbar"><a href="../../' + LAYOUT_QUERY + '">Paper Notes</a>' + languages() + '</div>'
            + render_language(zh, paper, "zh", renderer, output)
            + render_language(en, paper, "en", renderer, output)
            + '<dialog id="paper-image-dialog" class="paper-image-dialog" aria-label="论文图片 / Paper figure">'
              '<button type="button" class="paper-dialog-close" aria-label="关闭图片 / Close figure">关闭 / Close</button><img alt=""></dialog>'
              '<p class="reader-status sr-only" role="status" aria-live="polite"></p></main>')
    return document(paper["paper_title"], body, 3, paper["url"])


def home_link(count):
    return '''<section class="writing-group writing-group-papers" aria-labelledby="paper-notes-heading">
                            <div class="writing-group-head">
                                <div><span class="writing-group-number">04</span><h3 id="paper-notes-heading">Paper Notes</h3></div>
                                <p>完整论文精读与中英文版本。方法、公式、原图和实验数据保留在同一条论证中。</p>
                            </div>
                            <div class="writing-grid">
                                <article class="writing-card">
                                    <div class="writing-card-lead">
                                        <div class="writing-card-meta"><span class="writing-card-index">08</span><span>Research reading notes</span></div>
                                        <h3><a href="writing/?layout=single-column-en">Paper Notes</a></h3>
                                    </div>
                                    <div class="writing-card-body">
                                        <p>Detailed readings of research papers. Each note connects methods, equations, figures, and evidence. Full Chinese and English versions are available.</p>
                                        <div class="writing-card-footer">
                                            <ul class="writing-tags" aria-label="Topics"><li>Paper reviews</li><li>Methods</li><li>Evidence</li></ul>
                                            <div class="writing-links"><a href="writing/?layout=single-column-en">''' + str(count) + ''' reading notes <span aria-hidden="true">↗</span></a></div>
                                        </div>
                                    </div>
                                </article>
                            </div>
                        </section>'''


class ExistingGroup(HTMLParser):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.offsets = [0]
        for match in re.finditer("\n", text):
            self.offsets.append(match.end())
        self.start = self.end = None
        self.depth = 0

    def position(self):
        row, col = self.getpos()
        return self.offsets[row - 1] + col

    def handle_starttag(self, tag, attrs):
        if tag != "section":
            return
        if self.start is None and "writing-group-papers" in dict(attrs).get("class", "").split():
            self.start = self.position()
            self.depth = 1
        elif self.start is not None and self.end is None:
            self.depth += 1

    def handle_endtag(self, tag):
        if tag == "section" and self.start is not None and self.end is None:
            self.depth -= 1
            if self.depth == 0:
                self.end = self.position() + len("</section>")


def render_home(old, count):
    insertion = HOME_START + "\n" + home_link(count) + "\n" + HOME_END
    if HOME_START in old or HOME_END in old:
        if old.count(HOME_START) != 1 or old.count(HOME_END) != 1:
            raise ValueError("The homepage Paper Notes boundary is ambiguous")
        prefix, rest = old.split(HOME_START, 1)
        _, suffix = rest.split(HOME_END, 1)
        return prefix + insertion + suffix
    group = ExistingGroup(old)
    group.feed(old)
    if group.start is None or group.end is None:
        raise ValueError("The existing homepage Paper Notes entry was not found")
    return old[:group.start] + insertion + old[group.end:]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content-dir", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    directory = Path(args.content_dir).expanduser().resolve(strict=True)
    if directory == ROOT or ROOT in directory.parents:
        raise ValueError("Private source JSON must stay outside the public website checkout")
    manifest = json.loads((ROOT / "writing" / "papers.json").read_text())
    papers = manifest.get("papers", [])
    if manifest.get("schema_version") != 1 or not papers:
        raise ValueError("A public paper manifest is required")
    seen = set()
    renderer = load_renderer()
    outputs = {}
    for paper in papers:
        slug = paper["slug"]
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError("Paper slugs must be unique lowercase path components")
        seen.add(slug)
        if paper.get("url") != BASE_URL + "writing/papers/" + slug + "/":
            raise ValueError("The canonical paper URL must point to its dedicated article page")
        if not public_url(paper.get("source_url")):
            raise ValueError("The paper source URL must be public HTTPS")
        date.fromisoformat(paper["published"])
        zh = json.loads((directory / (slug + "-content.json")).read_text())
        en = json.loads((directory / (slug + "-content-en.json")).read_text())
        validate_pair(zh, en, paper)
        output = ROOT / "writing" / "papers" / slug / "index.html"
        outputs[output] = render_paper(paper, zh, en, renderer, output)
    outputs[ROOT / "writing" / "index.html"] = render_hub(papers)
    home = ROOT / "index.html"
    outputs[home] = render_home(home.read_text(), len(papers))
    for path, value in outputs.items():
        if any(marker in value for marker in ("/Users/", "/scratch/", "BEGIN OPENSSH PRIVATE KEY", "github_pat_")):
            raise ValueError("Private operational data cannot appear in public pages")
        if args.check:
            if not path.is_file() or path.read_text() != value:
                raise ValueError("Generated page is out of date: " + str(path.relative_to(ROOT)))
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(value, encoding="utf-8")
    print(("Validated" if args.check else "Built") + " Paper Notes hub, " + str(len(papers))
          + " complete Chinese/English articles, and the homepage entry.")


if __name__ == "__main__":
    main()
