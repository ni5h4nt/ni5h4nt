"""Sync the README blog list with the cybertect.ai sitemap.

Existing entries keep their (possibly hand-edited) titles; only new URLs
get a slug-derived title.
"""

import re
import sys
import urllib.request
from pathlib import Path

SITEMAP = "https://cybertect.ai/sitemap.xml"
README = Path(__file__).resolve().parents[2] / "README.md"
START = "<!-- BLOG-POST-LIST:START -->"
END = "<!-- BLOG-POST-LIST:END -->"
MAX_POSTS = 5

ACRONYMS = {"ai": "AI", "llm": "LLM", "llms": "LLMs", "pcas": "PCAS", "sok": "SoK"}
SMALL = {"a", "an", "and", "as", "at", "but", "by", "for", "in", "is", "it",
         "its", "of", "on", "or", "the", "to", "with"}


def title_from_slug(url: str) -> str:
    words = url.rstrip("/").rsplit("/", 1)[-1].split("-")
    out = []
    for i, w in enumerate(words):
        if w in ACRONYMS:
            out.append(ACRONYMS[w])
        elif i > 0 and w in SMALL:
            out.append(w)
        else:
            out.append(w.capitalize())
    return " ".join(out)


def main() -> int:
    req = urllib.request.Request(SITEMAP, headers={"User-Agent": "Mozilla/5.0"})
    body = urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")
    posts = [u for u in re.findall(r"<loc>(.*?)</loc>", body) if "/insights/" in u]
    if not posts:
        print("No posts found in sitemap; leaving README unchanged.")
        return 0

    readme = README.read_text(encoding="utf-8")
    block = readme.split(START)[1].split(END)[0]
    existing = dict(re.findall(r"- \[(.*?)\]\((\S+?)\)", block))
    titles_by_url = {url: title for title, url in existing.items()}

    lines = [
        f"- [{titles_by_url.get(url, title_from_slug(url))}]({url})"
        for url in posts[:MAX_POSTS]
    ]
    updated = (
        readme.split(START)[0] + START + "\n" + "\n".join(lines) + "\n" + END
        + readme.split(END)[1]
    )
    if updated != readme:
        README.write_text(updated, encoding="utf-8")
        print("README updated.")
    else:
        print("No changes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
