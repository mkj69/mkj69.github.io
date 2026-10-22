#!/usr/bin/env python3
"""Render a detailed, source-backed reading sheet as semantic HTML."""
import argparse
import html
import json
from pathlib import Path
import re


def esc(value):
    return html.escape(str(value), quote=True)


def prose(value):
    value = str(value).replace('\u2014', '；').replace('\u2013', '至')
    return re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', esc(value))


def safe_url(value):
    return isinstance(value, str) and value.startswith('https://') and not any(c in value for c in '\r\n<>"')


def block_html(block, output):
    kind = block['type']
    color = block.get('color', 'blue')
    if color not in ('blue', 'pink', 'orange', 'green', 'gray'):
        color = 'blue'
    if kind == 'heading':
        return f'<h3 class="accent {color}">{prose(block["text"])}</h3>'
    if kind == 'paragraph':
        return '<p>' + prose(block['text']) + '</p>'
    if kind == 'list':
        return '<ul>' + ''.join('<li>' + prose(x) + '</li>' for x in block['items']) + '</ul>'
    if kind == 'formula':
        plain = block.get('plain')
        if not plain:
            raise ValueError('A readable formula representation is required')
        return '<div class="equation" role="math" aria-label="' + esc(plain) + '">' + esc(plain) + '</div>'
    if kind == 'code':
        return '<pre>' + esc(block['text']) + '</pre>'
    if kind == 'table':
        headers, rows = block['headers'], block['rows']
        if any(len(row) != len(headers) for row in rows):
            raise ValueError('Table rows must match the header width: ' + block.get('caption', ''))
        result = '<div class="table-wrap"><table><caption>' + prose(block.get('caption', '')) + '</caption><thead><tr>'
        result += ''.join('<th scope="col">' + prose(x) + '</th>' for x in headers)
        result += '</tr></thead><tbody>'
        result += ''.join('<tr>' + ''.join(('<th scope="row">' + prose(x) + '</th>') if i == 0 else ('<td>' + prose(x) + '</td>') for i,x in enumerate(row)) + '</tr>' for row in rows)
        result += '</tbody></table></div>'
        if block.get('note'):
            result += '<p class="table-note">' + prose(block['note']) + '</p>'
        return result
    if kind == 'figure':
        src = block['src']
        path = Path(src)
        if path.is_absolute() or '..' in path.parts or not (output.parent / path).is_file():
            raise ValueError('Figure asset must exist beside the article: ' + src)
        alt = block.get('alt') or block.get('label') or block.get('caption', '')
        return ('<figure><button class="figure-open" type="button" aria-label="放大：' + esc(alt) + '">'
                '<img src="' + esc(src) + '" alt="' + esc(alt) + '" loading="lazy"></button>'
                '<figcaption><strong>' + prose(block.get('label', '原论文图')) + '。</strong> '
                + prose(block.get('caption', '')) + '</figcaption></figure>')
    raise ValueError('Unsupported content block: ' + kind)


STYLE = '''
.sr-only{position:absolute;width:1px;height:1px;padding:0;margin:-1px;overflow:hidden;clip:rect(0,0,0,0);white-space:nowrap;border:0}tbody th[scope=row]{font-weight:400;border-top:0;border-bottom:1px solid #c8c9c8;text-align:left}
.callout{border:1px solid currentColor;border-radius:7px;padding:10px 12px;margin:12px 0}.callout>p,.callout>ul{color:var(--ink)}.callout.pink{background:#fbf1f4}.callout.blue{background:#f0f4fa}.callout.green{background:#eef6f0}.callout .accent{margin-top:0;border-left:0;padding-left:0}.overview .column+.column{border-left:0;padding-left:0}.overview figure{border:1px solid #aaa;border-radius:7px;padding:10px}
:root{color-scheme:light;--ink:#202124;--muted:#5d6062;--blue:#2f5f93;--pink:#c93664;--orange:#c9741c;--green:#2e7d4f}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;color:var(--ink);background:#e9ecea;font:15px/1.53 "Noto Serif CJK SC","Songti SC","STSong","Times New Roman",serif}a{color:var(--blue);text-underline-offset:3px}.reader-bar{position:sticky;top:0;z-index:5;display:flex;align-items:center;gap:20px;padding:12px 28px;background:#fffef9ed;border-bottom:1px solid #d0d4cf;backdrop-filter:blur(12px);font:13px/1.5 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}.reader-bar nav{display:flex;gap:16px;flex-wrap:wrap}.reader-bar button{margin-left:auto;font:inherit;background:white;border:1px solid #a7afa9;border-radius:5px;padding:5px 12px;cursor:pointer}.sheet{max-width:1480px;min-height:1046px;background:white;margin:26px auto;padding:26px 30px 14px;box-shadow:0 3px 18px #18302115;display:flex;flex-direction:column;scroll-margin-top:62px}.running{display:flex;justify-content:space-between;gap:20px;align-items:center;border-bottom:1px solid #242628;padding-bottom:10px;margin-bottom:15px;font-size:14px}.running .subject{font-weight:600}.page-columns{display:grid;grid-template-columns:repeat(var(--cols),minmax(0,1fr));gap:19px;flex:1}.page-columns.overview{grid-template-columns:1.42fr 1fr}.column{min-width:0}.column+.column{border-left:1px solid #d8dcda;padding-left:18px}.bibliography{border:1px solid #aaa;border-radius:8px;background:#f6f6f7;padding:14px 18px;margin-bottom:14px}.bibliography .bib-title{font:700 26px/1.3 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;margin:0 0 6px}.bibliography .subtitle{font-style:italic;font-size:16px;margin:0 0 6px}.bibliography p{margin:4px 0}.accent{font:700 17px/1.4 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;border-left:5px solid currentColor;padding-left:9px;margin:17px 0 8px}.accent:first-child{margin-top:0}.blue{color:var(--blue)}.pink{color:var(--pink)}.orange{color:var(--orange)}.green{color:var(--green)}.gray{color:#333}p{margin:7px 0;text-align:justify;overflow-wrap:anywhere}ul{padding-left:19px;margin:7px 0}li{margin:5px 0;overflow-wrap:anywhere}figure{margin:12px 0}.figure-open{display:block;width:100%;padding:0;border:0;background:white;cursor:zoom-in}.figure-open img{display:block;width:100%;height:auto;max-height:590px;object-fit:contain}.figure-open:focus-visible{outline:2px solid var(--blue);outline-offset:3px}figcaption,.table-note{font-size:12.5px;line-height:1.48;color:#484c4b;margin-top:6px}figcaption strong{color:#222}.equation{font-family:"STIX Two Math","Cambria Math","Times New Roman",serif;font-size:15px;line-height:1.65;white-space:pre-wrap;overflow-wrap:anywhere;background:#f3f5f8;border-left:2px solid #bbc9d5;padding:8px 10px;margin:10px 0}pre{font:11.5px/1.5 "SFMono-Regular",Consolas,monospace;white-space:pre-wrap;overflow-wrap:anywhere;background:#f6f7f5;padding:10px}.table-wrap{overflow-x:auto;margin:10px 0}table{width:100%;border-collapse:collapse;font-size:12px;line-height:1.4;font-variant-numeric:tabular-nums}caption{text-align:left;font-weight:bold;font-size:13px;line-height:1.5;padding-bottom:5px}th,td{padding:4px 5px;border-bottom:1px solid #c8c9c8;text-align:right;vertical-align:top}th:first-child,td:first-child{text-align:left}th{border-top:1px solid #222;border-bottom:1px solid #222;white-space:normal}td strong{background:#fbe3ea;padding:0 2px}tbody tr:last-child td{border-bottom:1px solid #222}.page-foot{display:flex;justify-content:space-between;border-top:1px solid #222;margin-top:15px;padding-top:7px;color:#555;font-size:12px}.page-foot span:nth-child(2){font-weight:bold}.edition{max-width:1480px;margin:16px auto;padding:0 20px 24px;color:#555;font:13px/1.7 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}dialog{max-width:95vw;max-height:95vh;border:0;padding:36px 12px 12px;border-radius:7px;background:white;box-shadow:0 15px 70px #0005}dialog::backdrop{background:#07120deb}dialog img{display:block;max-width:90vw;max-height:84vh;width:auto;height:auto}dialog button{position:absolute;right:10px;top:7px;border:1px solid #aaa;background:white;padding:4px 12px;cursor:pointer}@media(max-width:1540px){.sheet{margin:20px 18px}}@media(max-width:1250px){body{font-size:15px}.page-columns:not(.overview){grid-template-columns:repeat(2,minmax(0,1fr))}.column:nth-child(odd){border-left:0;padding-left:0}.running .subject{display:none}.sheet{min-height:0}.equation{font-size:15px}}@media(max-width:700px){body{background:white;font-size:16px}.reader-bar{position:static;padding:12px 15px;gap:12px;flex-wrap:wrap}.reader-bar nav{gap:12px}.reader-bar button{margin-left:0}.sheet{box-shadow:none;margin:0;padding:24px 17px 16px;border-bottom:8px solid #e8ece7}.page-columns,.page-columns.overview,.page-columns:not(.overview){display:block}.column+.column{border:0;padding:0;margin-top:22px}.bibliography .bib-title{font-size:24px}.running{font-size:12px}.running a{overflow-wrap:anywhere}.accent{font-size:19px}.figure-open img{max-height:none}table{font-size:13px}figcaption,.table-note{font-size:14px}.equation{font-size:17px}.page-foot{font-size:11px}.edition{padding:18px}}@media print{@page{size:A4 landscape;margin:8mm}body{background:white;font-size:7.8pt;line-height:1.35}.reader-bar,.edition,dialog{display:none}.sheet{width:auto;max-width:none;min-height:0;margin:0;padding:0;box-shadow:none;break-after:page;scroll-margin:0}.sheet:last-of-type{break-after:auto}.running{font-size:7.5pt;padding-bottom:4px;margin-bottom:7px}.page-columns{gap:9px}.column+.column{padding-left:8px}.bibliography{padding:6px 8px;margin-bottom:6px}.bibliography .bib-title{font-size:15pt}.bibliography .subtitle{font-size:8.5pt}.accent{font-size:9.7pt;margin:7px 0 4px;border-left-width:3px;padding-left:5px}p,li{margin:3px 0}.equation{font-size:8pt;line-height:1.3;padding:4px 6px;margin:4px 0}pre{font-size:6.5pt;padding:5px}figure{margin:5px 0}.figure-open img{max-height:92mm}figcaption,.table-note{font-size:6.6pt;line-height:1.35}table{font-size:6.5pt;line-height:1.25}caption{font-size:7pt}th,td{padding:2px 3px}.page-foot{font-size:6.5pt;margin-top:7px;padding-top:4px}.page-columns:not(.overview){grid-template-columns:repeat(var(--cols),minmax(0,1fr))}}
'''


def render(data, output):
    title = data['title']
    meta = data['metadata']
    arxiv = str(meta.get('arxiv') or '')
    arxiv_url = meta.get('source_url') or meta.get('arxiv_url') or (arxiv if arxiv.startswith('https://') else 'https://arxiv.org/abs/' + arxiv if arxiv else '')
    if not safe_url(arxiv_url):
        raise ValueError('A source URL is required')
    source_label = meta.get('source_label') or ('arXiv ' + arxiv.removeprefix('https://arxiv.org/abs/') if arxiv else '原论文')
    pages = data['pages']
    if len(pages) < 4:
        raise ValueError('A detailed reading sheet needs at least four substantive page sections')
    nav = ''.join(f'<a href="#page-{i+1}">{i+1} · {esc(p["title"])}</a>' for i,p in enumerate(pages))
    result = '<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>' + esc(title) + ' | Paper Notes</title><meta name="description" content="' + esc(data.get('subtitle', title)) + '"><style>' + STYLE + '</style></head><body>'
    result += '<header class="reader-bar"><a href="../../">Paper Notes</a><nav aria-label="页目录">' + nav + '</nav><button type="button" id="print">打印</button></header><main><h1 class="sr-only">' + esc(title) + '</h1>'
    for i,page in enumerate(pages):
        cols = page['columns']
        result += f'<article class="sheet" id="page-{i+1}" aria-label="第 {i+1} 页：{esc(page["title"])}"><h2 class="sr-only">{esc(page["title"])}</h2><header class="running"><span>论文精读 · {esc(page["title"])}</span><span class="subject">{esc(title)}</span><a href="{esc(arxiv_url)}">{esc(source_label)}</a></header>'
        result += '<div class="page-columns ' + ('overview' if page.get('layout') == 'overview' else '') + '" style="--cols:' + str(len(cols)) + '">'
        for j,column in enumerate(cols):
            result += '<section class="column">'
            if i == 0 and j == 0:
                result += '<div class="bibliography"><p class="bib-title">' + esc(title) + '</p><p class="subtitle">' + esc(data.get('subtitle', '')) + '</p><p>' + esc(meta.get('authors', '')) + '</p><p>' + esc(meta.get('venue', '')) + ' · ' + esc(meta.get('version', '')) + '</p>'
                if safe_url(meta.get('code')):
                    result += '<p><a href="' + esc(meta['code']) + '">作者代码</a></p>'
                result += '</div>'
            opened = False
            last_heading = '实验与方法对照'
            for block in column['blocks']:
                if block['type'] == 'heading':
                    last_heading = block['text']
                    if opened:
                        result += '</section>'
                        opened = False
                    if i == 0 and block['text'].startswith(('问题', '方案', '三个主要结论')):
                        color = block.get('color', 'blue')
                        if color not in ('blue', 'pink', 'orange', 'green', 'gray'):
                            color = 'blue'
                        result += '<section class="callout ' + color + '">'
                        opened = True
                if block['type'] == 'table' and not block.get('caption'):
                    block = {**block, 'caption': last_heading}
                result += block_html(block, output)
            if opened:
                result += '</section>'
            result += '</section>'
        result += '</div><footer class="page-foot"><span>Kaijing Ma · Paper Notes</span><span>' + str(i+1) + ' / ' + str(len(pages)) + '</span><span>' + esc(meta.get('version', '')) + '</span></footer></article>'
    origin = '本篇由用户提供的精读表转换为可搜索、可复制的 HTML。' if data.get('source_pdf') else '本篇依据原论文与明确标注的资料整理为结构化精读。'
    result += '</main><footer class="edition"><p>' + origin + '原图与实验数据归原论文作者；图号、表号和版本随正文标注。解释、对比与局限是阅读笔记，不代表作者额外作出的结论。<a href="' + esc(arxiv_url) + '">原论文</a></p></footer><dialog id="image-dialog" aria-label="论文原图预览"><button type="button" aria-label="关闭原图">关闭</button><img alt="放大的论文原图"></dialog><script>const d=document.getElementById("image-dialog");document.querySelectorAll(".figure-open").forEach(b=>b.addEventListener("click",()=>{const i=b.querySelector("img");d.querySelector("img").src=i.src;d.querySelector("img").alt=i.alt;d.showModal()}));d.querySelector("button").addEventListener("click",()=>d.close());d.addEventListener("click",e=>{if(e.target===d)d.close()});document.getElementById("print").addEventListener("click",()=>window.print());</script></body></html>'
    if any(s in result for s in ('/Users/', '/scratch/', 'github_pat_')):
        raise ValueError('Private operational details cannot appear in a public article')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('content')
    parser.add_argument('output')
    args = parser.parse_args()
    output = Path(args.output)
    data = json.loads(Path(args.content).read_text())
    result = render(data, output)
    output.write_text(result, encoding='utf-8')
    print(json.dumps({'pages':len(data['pages']), 'figures':sum(b['type']=='figure' for p in data['pages'] for c in p['columns'] for b in c['blocks']), 'output':str(output)}))


if __name__ == '__main__':
    main()
