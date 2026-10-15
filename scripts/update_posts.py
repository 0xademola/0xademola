#!/usr/bin/env python3
"""Rewrite the README blog list from the Frensense docs site manifest."""
import json
import re
import sys
import urllib.request
from pathlib import Path

FEED = "https://frensense.friehub.cloud/posts.json"
README = Path("README.md")
START, END = "<!-- BLOG-POST-LIST:START -->", "<!-- BLOG-POST-LIST:END -->"
LIMIT = 5

def md_escape(text: str) -> str:
    return re.sub(r"([\[\]\\])", r"\\\1", text)

def main() -> int:
    req = urllib.request.Request(FEED, headers={"User-Agent": "profile-readme-updater"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)

    posts = [
        p for p in data.get("posts", [])
        if p.get("title") and str(p.get("url", "")).startswith("https://frensense.friehub.cloud/")
    ][:LIMIT]
    if not posts:
        print("feed returned no usable posts; leaving README untouched", file=sys.stderr)
        return 1  # fail loudly instead of blanking the list

    lines = [f"- [{md_escape(p['title'])}]({p['url']}) · {p.get('date', '')}" for p in posts]
    block = f"{START}\n" + "\n".join(lines) + f"\n{END}"

    text = README.read_text(encoding="utf-8")
    pattern = re.compile(re.escape(START) + r".*?" + re.escape(END), re.DOTALL)
    if not pattern.search(text):
        print("markers not found in README.md", file=sys.stderr)
        return 1
    new = pattern.sub(lambda _m: block, text)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print(f"updated with {len(posts)} posts")
    else:
        print("no change")
    return 0

if __name__ == "__main__":
    sys.exit(main())
