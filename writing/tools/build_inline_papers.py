#!/usr/bin/env python3
"""Build complete bilingual paper notes inside the homepage Writing section."""
import argparse
import html
import importlib.util
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
RENDERER = Path(__file__).with_name('render_paper.py')
START = '<!-- PAPER_NOTES_ENTRIES:START -->'
END = '<!-- PAPER_NOTES_ENTRIES:END -->'


def esc(value):
    return html.escape(str(value), quote=True)


def load_renderer():
    spec = importlib.util.spec_from_file_location('paper_renderer', RENDERER)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def validate_pair(zh, en):
    if len(zh['pages']) != len(en['pages']):
        raise ValueError('Both languages must cover the same pages')
    for zp, ep in zip(zh['pages'], en['pages']):
        if len(zp['columns']) != len(ep['columns']):
            raise ValueError('Bilingual column structure differs')
        for zc, ec in zip(zp['columns'], ep['columns']):
            if len(zc['blocks']) != len(ec['blocks']):
                raise ValueError('Bilingual block coverage differs')
            for zb, eb in zip(zc['blocks'], ec['blocks']):
                if zb['type'] != eb['type']:
                    raise ValueError('Bilingual block types differ')
                if zb['type'] == 'figure' and zb['src'] != eb['src']:
                    raise ValueError('Both languages must show the same actual figure')
                if zb['type'] == 'formula' and (zb.get('plain'), zb.get('latex')) != (eb.get('plain'), eb.get('latex')):
                    raise ValueError('The mathematical statement changed between languages')
                if zb['type'] == 'table':
                    if len(zb['headers']) != len(eb['headers']) or len(zb['rows']) != len(eb['rows']):
                        raise ValueError('A bilingual table lost rows or columns')
                    for zr, er in zip(zb['rows'], eb['rows']):
                        if len(zr) != len(er):
                            raise ValueError('A bilingual table row changed width')
                        for z, e in zip(zr, er):
                            if re.findall(r'\d+(?:\.\d+)?', str(z)) != re.findall(r'\d+(?:\.\d+)?', str(e)):
                                raise ValueError('A numeric table cell changed in translation')


def fragments(data, slug, language, renderer):
    target = ROOT / 'writing' / 'papers' / slug / 'index.html'
    document = renderer.render(data, target)
    articles = re.findall(r'<article class="sheet".*?</article>', document, re.S)
    if len(articles) != len(data['pages']):
        raise ValueError('Every semantic page must have a rendered article')
    rendered = '\n'.join(articles)
    rendered = re.sub(r'\bid="([^"]+)"', lambda m: 'id="' + slug + '-' + language + '-' + m.group(1) + '"', rendered)
    rendered = rendered.replace('src="assets/', 'src="writing/papers/' + slug + '/assets/')
    rendered = rendered.replace('<h2', '<h5').replace('</h2>', '</h5>').replace('<h3', '<h6').replace('</h3>', '</h6>')
    if language == 'en':
        rendered = rendered.replace('论文精读 · ', 'Paper note · ').replace('aria-label="第 ', 'aria-label="Page ').replace(' 页：', ': ')
        rendered = rendered.replace('aria-label="放大：', 'aria-label="Enlarge: ')
        rendered = rendered.replace('>作者代码<', '>Author code<')
    return '<h4 class="sr-only">' + esc(data['title']) + '</h4>\n' + rendered


def entry(paper, zh, en, renderer):
    slug = paper['slug']
    labels = {'zh': paper['summary_zh'], 'en': paper['summary']}
    parts = [f'<details id="paper-{slug}" class="paper-note" data-paper-note="{slug}"><summary><span class="paper-note-summary-main"><strong>{esc(paper["short_title"])}</strong>']
    for language in ('zh', 'en'):
        parts.append('<span class="paper-note-description" data-paper-summary-language="' + language + '" lang="' + ('zh-CN' if language == 'zh' else 'en') + '"' + (' hidden' if language == 'en' else '') + '>' + esc(labels[language]) + '</span>')
    parts.append('</span><span class="paper-note-expansion" aria-hidden="true"></span></summary><div class="paper-note-versions">')
    for language, data in (('zh', zh), ('en', en)):
        parts.append('<div class="paper-note-content" data-paper-language-content="' + language + '" lang="' + ('zh-CN' if language == 'zh' else 'en') + '"' + (' hidden' if language == 'en' else '') + '><p class="paper-language-label">' + ('中文' if language == 'zh' else 'English') + '</p>')
        parts.append(f'<!-- PAPER:{slug}:{language}:START -->')
        parts.append(fragments(data, slug, language, renderer))
        credit = '原图与数据来自原论文。解释与比较属于阅读笔记，版本及图表编号随正文标明。' if language == 'zh' else 'Original figures and data come from the cited paper. Explanations and comparisons are reading notes. The source version and figure labels appear beside the material.'
        parts.append('<p class="edition">' + credit + '</p>')
        parts.append(f'<!-- PAPER:{slug}:{language}:END -->')
        parts.append('</div>')
    parts.append('</div></details>')
    return '\n'.join(parts)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--content-dir', required=True)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    directory = Path(args.content_dir).expanduser().resolve(strict=True)
    if directory == ROOT or ROOT in directory.parents:
        raise ValueError('Private content sources must stay outside the public repository')
    manifest = json.loads((ROOT / 'writing' / 'papers.json').read_text())
    renderer = load_renderer()
    entries = []
    for paper in manifest['papers']:
        slug = paper['slug']
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
            raise ValueError('Invalid paper slug')
        zh = json.loads((directory / (slug + '-content.json')).read_text())
        en = json.loads((directory / (slug + '-content-en.json')).read_text())
        validate_pair(zh, en)
        entries.append(entry(paper, zh, en, renderer))
    index = ROOT / 'index.html'
    old = index.read_text()
    if old.count(START) != 1 or old.count(END) != 1:
        raise ValueError('The existing Writing insertion boundary is missing or ambiguous')
    prefix, remainder = old.split(START, 1)
    _, suffix = remainder.split(END, 1)
    new = prefix + START + '\n' + '\n'.join(entries) + '\n' + END + suffix
    new = re.sub(r'(<div class="paper-reader-toolbar">\s*<p>).*?(</p>)', lambda m: m.group(1) + str(len(entries)) + ' 篇精读 · Bilingual notes' + m.group(2), new, count=1, flags=re.S)
    if any(value in new for value in ('/Users/kaijing', '/scratch/11757', 'BEGIN OPENSSH PRIVATE KEY')):
        raise ValueError('Private content cannot appear in the public homepage')
    if args.check:
        if new != old:
            raise ValueError('The inline bilingual notes are out of date')
        print('Validated ' + str(len(entries)) + ' complete bilingual notes in the homepage Writing section.')
    else:
        index.write_text(new, encoding='utf-8')
        print('Built ' + str(len(entries)) + ' complete bilingual notes inside the existing homepage.')


if __name__ == '__main__':
    main()
