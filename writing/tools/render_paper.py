#!/usr/bin/env python3
"""Internal semantic blocks for build_paper_notes.py."""
import html
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
        attribution = ''
        if block.get('attribution'):
            attribution += ' ' + prose(block['attribution'])
        for key, label in (('source_url', block.get('source_label', 'Source')),
                           ('license_url', block.get('license_label', 'License'))):
            if block.get(key):
                if not safe_url(block[key]):
                    raise ValueError('Figure attribution links must use public HTTPS: ' + key)
                attribution += ' <a href="' + esc(block[key]) + '">' + prose(label) + '</a>.'
        if block.get('changes'):
            attribution += ' ' + prose(block['changes'])
        return ('<figure><button class="figure-open" type="button" aria-label="放大：' + esc(alt) + '">'
                '<img src="' + esc(src) + '" alt="' + esc(alt) + '" loading="lazy"></button>'
                '<figcaption><strong>' + prose(block.get('label', '原论文图')) + '。</strong> '
                + prose(block.get('caption', '')) + attribution + '</figcaption></figure>')
    raise ValueError('Unsupported content block: ' + kind)
