# Detailed paper notes

The complete Chinese and English notes live directly in the existing homepage Writing section. Each expandable note contains semantic HTML, readable equations, native data tables and local figure assets. Chinese, English and parallel views share the same article. Figures open at their original resolution.

The content source is a JSON reading sheet kept outside this public checkout. It contains paper metadata and ordered pages, columns and blocks. The renderer accepts headings, paragraphs, lists, formulas with a readable `plain` representation, code, tables and figures. Figure captions retain their original paper labels and source context. Missing figure files, malformed tables or missing readable equations stop generation.

```sh
python3 writing/tools/build_inline_papers.py --content-dir /path/to/private-content
python3 writing/tools/build_inline_papers.py --content-dir /path/to/private-content --check
```

The private content directory contains matching `paper-slug-content.json` and `paper-slug-content-en.json` files. Both languages must cover the same pages and blocks, with unchanged figures, equations and table numbers. The public manifest contains only approved paper identities and summaries. The build replaces only the marked paper entries inside the existing Writing section. Reading queues, personal annotations, source documents, credentials and drafts remain outside this repository. A completed reading note does not imply that the reader has finished reading the paper.

Publication uses checked public research material and the user's authorized paper notes. Paper authors retain ownership of original figures. Preserve source, version, figure labels and any applicable attribution. Do not infer paper-figure permissions from a code repository's software license. If a future source or figure cannot be checked, keep the affected article as a draft and record the gap.
