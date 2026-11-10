#!/usr/bin/env python3
"""Build explicitly supplied new notes without requiring or rebuilding old private sources.
Input directory remains private. Each line is English | Chinese; # marks paired
headings, ! marks a shared readable formula. Only explicitly supplied slugs change.
"""
import argparse, importlib.util, json, html, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('builder',Path(__file__).with_name('build_paper_notes.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
def demo_block(slug, en, zh):
    config=json.loads((ROOT/'writing/assets/method-demo-text.json').read_text())[slug]
    static='<ol class="demo-static">'+''.join('<li>'+b.language_text(x['zh'],x['en'])+'</li>' for x in config['steps'])+'</ol>'
    return '<section class="method-demo" data-demo="'+slug+'"><h2>'+b.language_text('逐步理解方法','Explore the method')+'</h2><p>'+b.language_text('合成教学数值，不是论文实验结果。默认静止；所有步骤均可在下方静态说明中阅读。','Synthetic teaching values, not paper results. Nothing plays automatically; all steps remain available in the static explanation.')+'</p><div class="demo-controls"></div><div class="demo-stage"></div><details open><summary>'+b.language_text('静态解释与适用限制','Static explanation and limits')+'</summary><p>'+b.language_text(zh,en)+'</p>'+static+'</details></section>'
def attach(page,slug,en,zh):
    anchor='<nav class="paper-contents"'
    # One interactive unit belongs outside language panels.
    marker='<section class="paper-language-panel"'
    at=page.index(marker)
    page=page[:at]+demo_block(slug,en,zh)+page[at:]
    return page.replace('</head>','<link rel="stylesheet" href="/writing/assets/method-demos.css"><script src="/writing/assets/method-demos.js" defer></script></head>')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',required=True);ap.add_argument('--check',action='store_true');args=ap.parse_args();d=Path(args.source_dir).resolve()
    if d==ROOT or ROOT in d.parents:raise ValueError('Source drafts must remain outside public checkout')
    entries=json.loads((d/'batch.json').read_text());manifest=json.loads((ROOT/'writing/papers.json').read_text());existing={p['slug']:p for p in manifest['papers']};outputs={}
    for m in entries:
        slug=m['slug'];assert re.fullmatch('[a-z0-9-]+',slug)
        lines=(d/'notes'/f'{slug}.txt').read_text().splitlines();pages={'en':[],'zh':[]};pairs=[]
        for line in lines:
            if not line.strip():continue
            if line.startswith('! '):
                block={'type':'formula','plain':line[2:]}
                for lang in pages:pages[lang][-1]['columns'][0]['blocks'].append(dict(block))
                pairs.append(('formula',line[2:],line[2:]));continue
            if ' | ' not in line:raise ValueError('Missing translation: '+line)
            en,zh=line.split(' | ',1)
            if en.startswith('# '):
                en=en[2:];kind='heading'
                for lang,text in [('en',en),('zh',zh)]:pages[lang].append({'title':text,'columns':[{'blocks':[]}]})
            else:
                kind='paragraph'
                for lang,text in [('en',en),('zh',zh)]:pages[lang][-1]['columns'][0]['blocks'].append({'type':'paragraph','text':text})
            pairs.append((kind,en,zh))
        first=next(x for x in pairs if x[0]=='paragraph');url=b.BASE_URL+'writing/papers/'+slug+'/'
        if slug in existing and existing[slug].get('source_url')!=m['url']:raise ValueError('Existing slug belongs to another source')
        p={**existing.get(slug,{}),'slug':slug,'paper_title':m['title'],'short_title':m['title'],'authors':m['authors'],'published':'2026-11-10','source_url':m['url'],'source_label':m['version'],'summary':first[1],'summary_zh':first[2],'url':url,'topics':['Inference-time methods'],'languages':['en','zh-CN'],'study_guides':[{'url':url+'aligned/','title_en':'Sentence-aligned original note','title_zh':'原创笔记逐句中英对照'}]}
        meta={'source_url':m['url'],'source_label':m['version'],'authors':m['authors'],'version':m['version'],'venue':'Original reading note; cited methods and evidence, not an experimental reproduction.'}
        if m.get('verified_code'):meta['code']=m['verified_code']
        docs={lang:{'title':m['title'],'subtitle':'','metadata':meta,'pages':pg} for lang,pg in pages.items()}
        for lang in docs:
            docs[lang]['pages'].append({'title':'Sources and reading scope' if lang=='en' else '来源与阅读范围','columns':[{'blocks':[{'type':'paragraph','text':('This original note covers the method and selected experimental evidence discussed above. It is not a full-paper translation. No model experiments were run for this note. Source license: ' if lang=='en' else '本原创笔记覆盖上文讨论的方法和选定实验证据，不是论文全文翻译；本次未运行模型复现实验。来源许可：')+m['license']},{'type':'paragraph','text':('Author-code links in the source: ' if lang=='en' else '原文所列作者或相关代码链接：')+('; '.join(m['code_links']) if m['code_links'] else ('No author-code link verified in the inspected source.' if lang=='en' else '检查的来源中尚未核实作者代码链接。'))}]}]})
        b.validate_pair(docs['zh'],docs['en'],p);out=ROOT/'writing/papers'/slug/'index.html';page=b.render_paper(p,docs['zh'],docs['en'],b.load_renderer(),out)
        outputs[out]=attach(page,slug,first[1],first[2])
        body='<main class="paper-note-reader"><h1>'+html.escape(m['title'])+'</h1><p>Original note, sentence-aligned / 原创笔记逐句对照。Not a full-paper translation / 不是论文全文翻译。</p><p><a href="../">English / 中文</a> · <a href="'+m['url']+'">Source / 原文</a></p>'
        for kind,en,zh in pairs:
            if kind=='formula':body+='<div class="equation">'+html.escape(en)+'</div>'
            else:
                tag='h2' if kind=='heading' else 'p';body+='<section class="aligned-pair"><'+tag+' lang="en">'+html.escape(en)+'</'+tag+'><'+tag+' lang="zh-CN">'+html.escape(zh)+'</'+tag+'></section>'
        body+='</main>';aligned=b.document(m['title'],body,4,url+'aligned/').replace('../../assets/paper-notes','../../../assets/paper-notes');outputs[out.parent/'aligned/index.html']=aligned
        existing[slug]=p
    # New batch first, keep all pre-existing entries and old article bytes intact.
    order=[m['slug'] for m in entries]+[p['slug'] for p in manifest['papers'] if p['slug'] not in {m['slug'] for m in entries}]
    manifest['papers']=[existing[s] for s in order]
    outputs[ROOT/'writing/papers.json']=json.dumps(manifest,ensure_ascii=False,indent=2)+'\n';outputs[ROOT/'writing/index.html']=b.render_hub(manifest['papers']);outputs[ROOT/'index.html']=b.render_home((ROOT/'index.html').read_text(),len(manifest['papers']))
    for path,data in outputs.items():
        if any(s in data for s in ['/Users/','/workspace/','github_pat_']):raise ValueError('Private path or credential')
        if args.check:
            if not path.exists() or path.read_text()!=data:raise ValueError('Stale output '+str(path))
        else:path.parent.mkdir(parents=True,exist_ok=True);path.write_text(data)
    print(('Checked' if args.check else 'Built'),len(entries),'new notes and aligned notes; old articles untouched')
if __name__=='__main__':main()
