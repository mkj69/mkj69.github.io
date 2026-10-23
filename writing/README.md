# Paper Notes

The existing homepage Writing section links to the Paper Notes hub at `/writing/`. Each paper has a complete article at `/writing/papers/<slug>/`. The article has two language choices, 中文 and English. Every language version retains the full method, formulas, genuine figures, native tables and source attribution.

The formal full paper title appears once as the main article heading. There is no repeated title subtitle. Existing author-code links remain. The pages use the homepage palette, transparent content sections and responsive reading columns. Figures open at their original resolution.

## Build and check

The source JSON stays outside this public checkout. It contains metadata and ordered pages, columns and semantic blocks. Each paper needs matching `<slug>-content.json` and `<slug>-content-en.json` files. Their `title` fields match the formal `paper_title` in `writing/papers.json`; `subtitle` is empty. Metadata includes a verified `source_url`, source version, authors and an optional author-code URL.

```sh
python3 -B writing/tools/build_paper_notes.py --content-dir /path/to/private-content
python3 -B writing/tools/build_paper_notes.py --content-dir /path/to/private-content --check
```

The builder writes the hub, individual articles and the marked Paper Notes entry on the homepage. It preserves unrelated homepage content. Check mode only verifies that the generated files are current. A missing source figure, malformed table, missing readable `plain` formula, or incomplete translation stops the build. Language versions must preserve section and block coverage, figure files, mathematical statements and numeric table values.

`render_paper.py` is the internal semantic block renderer. Shared styling and language behavior live in `writing/assets/paper-notes.css` and `paper-notes.js`. The language preference is remembered. An unsupported saved preference returns to Chinese. Existing homepage bookmarks such as `#paper-sd3` redirect to the corresponding article.

## New papers

Add approved public bibliographic metadata and Chinese/English summaries to `writing/papers.json`. Set `url` to `https://mkj69.github.io/writing/papers/<slug>/` and place genuine figure assets in `writing/papers/<slug>/assets/`. Store the complete language source files in the private content directory, then build and check. The paper order follows the manifest.

The public manifest contains only approved paper identities and summaries. Reading queues, private annotations, source documents, credentials and drafts remain outside this repository. A generated note does not imply that the reader has completed the paper. Publication uses the user's authorized public research notes and required source assets. Source versions, figure labels and applicable attribution remain attached to the material.
