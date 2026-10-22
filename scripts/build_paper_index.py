#!/usr/bin/env python3
"""Build the public paper-note index with the Python standard library."""
import argparse
from datetime import date
from html import escape
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "writing" / "papers.json"
INDEX = ROOT / "writing" / "index.html"


def text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be nonempty text")
    if any(character in value for character in ("\u2013", "\u2014")):
        raise ValueError(f"{field} contains a dash that is outside the writing style")
    return escape(value)


def load_manifest():
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("papers"), list):
        raise ValueError("Unsupported paper manifest")
    text(data.get("title"), "title")
    text(data.get("description"), "description")
    seen = set()
    for paper in data["papers"]:
        slug = paper.get("slug", "")
        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", slug) or slug in seen:
            raise ValueError("Paper slugs must be unique, lowercase path components")
        seen.add(slug)
        date.fromisoformat(paper["published"])
        for key in ["short_title", "paper_title", "authors", "summary", "source_label"]:
            text(paper.get(key), key)
        source = urlsplit(paper.get("source_url", ""))
        if source.scheme != "https" or not source.hostname or source.username or source.password:
            raise ValueError("Paper source must be a public HTTPS URL without credentials")
        if not isinstance(paper.get("topics"), list) or not paper["topics"]:
            raise ValueError("Each paper needs at least one topic")
        for topic in paper["topics"]:
            text(topic, "topic")
    return data


def render(data):
    entries = []
    papers = sorted(data["papers"], key=lambda paper: paper["published"], reverse=True)
    for number, paper in enumerate(papers, 1):
        published = date.fromisoformat(paper["published"])
        topics = "".join(f"<li>{text(topic, 'topic')}</li>" for topic in paper["topics"])
        entries.append(f'''      <article class="paper-entry" aria-labelledby="{paper['slug']}-title">
        <div class="paper-number" aria-hidden="true">{number:02d}</div>
        <div class="paper-main">
          <p class="paper-meta"><time datetime="{published.isoformat()}">{published.day} {published.strftime('%B %Y')}</time><span aria-hidden="true"> · </span>Reading note</p>
          <h2 id="{paper['slug']}-title"><a href="papers/{paper['slug']}/">{text(paper['short_title'], 'short_title')}</a></h2>
          <p class="paper-title">{text(paper['paper_title'], 'paper_title')}</p>
          <p class="paper-summary">{text(paper['summary'], 'summary')}</p>
          <ul class="paper-topics" aria-label="Topics">{topics}</ul>
          <p class="paper-source">{text(paper['authors'], 'authors')}<span aria-hidden="true"> · </span><a href="{escape(paper['source_url'], quote=True)}">{text(paper['source_label'], 'source_label')}</a></p>
        </div>
        <a class="note-link" href="papers/{paper['slug']}/" aria-label="Full reading note: {text(paper['short_title'], 'short_title')}">Full note <span aria-hidden="true">↗</span></a>
      </article>''')
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{text(data['title'], 'title')} | Kaijing Ma</title>
  <meta name="description" content="{text(data['description'], 'description')}">
  <link rel="canonical" href="https://mkj69.github.io/writing/">
  <link rel="icon" href="../assets/favicon.svg" type="image/svg+xml">
  <link rel="stylesheet" href="assets/notes.css">
</head>
<body class="paper-notes">
  <a class="skip-link" href="#notes">Paper notes</a>
  <div class="notes-page">
    <header class="notes-header">
      <a class="author-link" href="../">Kaijing Ma</a>
      <nav aria-label="Site navigation"><a href="../#writing">Writing</a><a href="../">Home</a></nav>
    </header>
    <main id="notes">
      <div class="notes-intro">
        <p class="eyebrow">Writing / Research</p>
        <h1>{text(data['title'], 'title')}</h1>
        <p class="notes-description">{text(data['description'], 'description')}</p>
      </div>
      <div class="list-heading"><span>Reading notes</span><span>{len(papers)} notes</span></div>
{chr(10).join(entries)}
    </main>
    <footer class="notes-footer"><span>Kaijing Ma</span><a href="../#writing">Writing &amp; Projects</a></footer>
  </div>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate note routes and confirm the index is current")
    options = parser.parse_args()
    try:
        data = load_manifest()
        rendered = render(data)
        if options.check:
            missing = [paper["slug"] for paper in data["papers"] if not (ROOT / "writing" / "papers" / paper["slug"] / "index.html").is_file()]
            if missing:
                raise ValueError("Missing paper pages: " + ", ".join(missing))
            if not INDEX.is_file() or INDEX.read_text(encoding="utf-8") != rendered:
                raise ValueError("The paper index is out of date; run scripts/build_paper_index.py")
            print(f"Paper index and {len(data['papers'])} public note routes are valid.")
        else:
            INDEX.write_text(rendered, encoding="utf-8")
            print(f"Built paper index with {len(data['papers'])} notes.")
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
