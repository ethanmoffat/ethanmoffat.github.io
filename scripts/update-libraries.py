#!/usr/bin/env python3
"""Updates the third-party libraries section of site/index.html from the eo-protocol README.

The libraries listed in the "Libraries" section of the README are added to the landing page, except the ones owned by
this site's owner (listed separately). Each library links to its docs: the URL in libraries.json if there is one, else
the homepage of its GitHub repository. Set GITHUB_TOKEN to avoid the GitHub API's rate limit for anonymous requests.
"""

import html
import json
import os
import re
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG = ROOT / "libraries.json"
PAGE = ROOT / "site" / "index.html"
START = "<!-- third-party-libraries:start -->"
END = "<!-- third-party-libraries:end -->"

# e.g. 1. **[eolib-c](https://github.com/sorokya/eolib-c)** ([@sorokya](https://github.com/sorokya))
ENTRY = re.compile(r"^\d+\.\s+\*\*\[(?P<name>[^\]]+)\]\((?P<url>https://github\.com/(?P<repo>[^/)]+/[^/)]+))\)\*\*")
DESCRIPTION = re.compile(r"^\s+[*-]\s+(?P<text>.+)$")


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": "ethanmoffat.github.io"})
    token = os.environ.get("GITHUB_TOKEN")
    if token and url.startswith("https://api.github.com/"):
        request.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def parse_libraries(readme):
    """Returns the entries of the README's "### Libraries" section, in order."""
    section = re.search(r"^### Libraries\s*$(?P<body>.*?)^#", readme, re.MULTILINE | re.DOTALL)
    if not section:
        raise ValueError('the README has no "### Libraries" section')

    libraries = []
    for line in section.group("body").splitlines():
        entry = ENTRY.match(line)
        if entry:
            libraries.append({**entry.groupdict(), "description": ""})
            continue
        description = DESCRIPTION.match(line)
        if description and libraries and not libraries[-1]["description"]:
            libraries[-1]["description"] = description.group("text").strip()
    return libraries


def docs_url(library, overrides):
    if library["repo"] in overrides:
        return overrides[library["repo"]]
    repo = json.loads(fetch(f"https://api.github.com/repos/{library['repo']}"))
    return repo.get("homepage") or None


def render(libraries):
    lines = []
    for library in libraries:
        owner = library["repo"].split("/")[0]
        name = html.escape(library["name"])
        repo_url = html.escape(library["url"])
        docs = html.escape(library["docs"]) if library["docs"] else None
        links = [f'<a href="{docs}">Documentation</a>'] if docs else []
        links.append(f'<a href="{repo_url}">GitHub</a>')
        lines += [
            "            <li>",
            f'                <h2><a href="{docs or repo_url}">{name}</a></h2>',
            f"                <p>{html.escape(library['description'])}</p>",
            '                <p class="links">',
            *[f"                    {link}" for link in links],
            f'                    <span class="author">by <a href="https://github.com/{html.escape(owner)}">'
            f"@{html.escape(owner)}</a></span>",
            "                </p>",
            "            </li>",
        ]
    return "\n".join(lines)


def main():
    config = json.loads(CONFIG.read_text())
    excluded = {owner.lower() for owner in config["exclude_owners"]}
    libraries = [
        library
        for library in parse_libraries(fetch(config["source"]))
        if library["repo"].split("/")[0].lower() not in excluded
    ]
    if not libraries:
        raise ValueError("no third-party libraries were found in the README")
    for library in libraries:
        library["docs"] = docs_url(library, config["docs"])

    page = PAGE.read_text()
    start, end = page.index(START) + len(START), page.index(END)
    indent = page[page.rindex("\n", 0, page.index(END)) + 1 : page.index(END)]
    PAGE.write_text(page[:start] + "\n" + render(libraries) + "\n" + indent + page[end:])
    for library in libraries:
        print(f"{library['name']}: {library['docs'] or library['url']}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # noqa: BLE001 - report any failure as a short message
        sys.exit(f"error: {error}")
