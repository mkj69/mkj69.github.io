# Incremental research notes

`build_research_batch.py` builds explicitly supplied final bilingual note sources.
It does not invoke the legacy all-article build and does not require its private
content library. Original source PDFs and working review records stay outside the
public repository.

Run with Python 3 (standard library only):

```
python3 writing/tools/build_research_batch.py --source-dir /absolute/source-package
python3 writing/tools/build_research_batch.py --source-dir /absolute/source-package --check
```

The source package contains `batch.json` and `notes/<slug>.txt`. Metadata records
contain `slug`, formal `title`, `authors`, pinned `version`, `url`, `license`,
`code_links`, and optionally a verified author repository `verified_code`.
Each prose line is `English sentence. | 中文句子。`; headings start with `# `;
shared formulas start with `! `. Source files are reviewed outside the repository.
The generated note itself is public. `aligned/` aligns the **original note**,
not the source paper. Full-paper reading editions are separate deliverables.

The builder updates only the supplied slugs, their aligned notes, the manifest,
the hub, and the homepage note count. Existing slugs must match their source URL.
It deliberately does not rebuild existing unrelated articles.

## Teaching components

`assets/method-demos.js` implements synthetic numerical examples. No model API,
tracking, or external numerical service is called. `method-demo-text.json` holds
the static bilingual steps, rendered into HTML so they remain readable without
JavaScript. Keep its steps synchronized with the JS configurations. The controls
start paused, use native buttons and range inputs, pause on hidden documents,
and disable playback for `prefers-reduced-motion: reduce`.

Demonstrations identify approximations and unresolved source details. APD's
bounded curve is illustrative, not its trained extrapolator. GGRO's printed
gradient sign and the dynamic negative-prompting coefficient discrepancy are not
silently resolved. Numeric examples are not paper benchmark results.

VFD's existing paper note receives only the new teaching section and asset
references. Its previously published full reader, aligned note, and figures
remain untouched.
