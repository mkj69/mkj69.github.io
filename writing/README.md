# Detailed paper notes

Each article contains semantic HTML, readable equations, native data tables and local figure assets. The desktop layout follows a landscape reading sheet. Smaller screens reflow into readable columns. Figures open at their original resolution.

The content source is a JSON reading sheet kept outside this public checkout. It contains paper metadata and ordered pages, columns and blocks. The renderer accepts headings, paragraphs, lists, formulas with a readable `plain` representation, code, tables and figures. Figure captions retain their original paper labels and source context. Missing figure files, malformed tables or missing readable equations stop generation.

```sh
python3 writing/tools/render_paper.py /path/to/private-content.json writing/papers/paper-slug/index.html
python3 scripts/build_paper_index.py
python3 scripts/build_paper_index.py --check
```

The public manifest contains only approved paper identities and summaries. Reading queues, personal annotations, source documents, credentials and drafts remain outside this repository. A completed reading note does not imply that the reader has finished reading the paper.

Publication uses checked public research material and the user's authorized paper notes. Paper authors retain ownership of original figures. Preserve source, version, figure labels and any applicable attribution. Do not infer paper-figure permissions from a code repository's software license. If a future source or figure cannot be checked, keep the affected article as a draft and record the gap.
