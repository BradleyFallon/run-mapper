#!/usr/bin/env python3
from __future__ import annotations

import argparse
import mimetypes
from collections import deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests


SEED_URLS = [
    "https://giscience.github.io/openrouteservice/api-reference/",
    "https://openrouteservice.org/dev/",
]

PAGE_PREFIXES = [
    "https://giscience.github.io/openrouteservice/api-reference/",
]

ASSET_PREFIXES = [
    "https://giscience.github.io/openrouteservice/",
    "https://openrouteservice.org/dev/",
]

ASSET_EXTENSIONS = {
    ".css",
    ".js",
    ".ico",
    ".png",
    ".jpg",
    ".jpeg",
    ".svg",
    ".webp",
    ".woff",
    ".woff2",
    ".ttf",
    ".eot",
    ".json",
}


class LinkExtractor(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: set[str] = set()

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        for attr_name in ("href", "src"):
            value = attrs_dict.get(attr_name)
            if value:
                self.links.add(value)


def normalize_url(url: str) -> str:
    parsed = urlparse(url)
    return parsed._replace(fragment="", query="").geturl()


def is_page_url(url: str) -> bool:
    return any(url.startswith(prefix) for prefix in PAGE_PREFIXES)


def is_asset_url(url: str) -> bool:
    if not any(url.startswith(prefix) for prefix in ASSET_PREFIXES):
        return False
    return Path(urlparse(url).path).suffix.lower() in ASSET_EXTENSIONS


def local_path_for(base_dir: Path, url: str, content_type: str | None) -> Path:
    parsed = urlparse(url)
    path = parsed.path
    if not path or path.endswith("/"):
        path = f"{path}index.html"

    suffix = Path(path).suffix
    if not suffix and content_type:
        extension = mimetypes.guess_extension(content_type.split(";", 1)[0].strip()) or ""
        if extension:
            path = f"{path}{extension}"

    return base_dir / parsed.netloc / path.lstrip("/")


def download_docs(output_dir: Path) -> tuple[int, int]:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": "run-mapper-docs-downloader/1.0",
        }
    )

    output_dir.mkdir(parents=True, exist_ok=True)

    queue = deque(normalize_url(url) for url in SEED_URLS)
    seen: set[str] = set()
    saved_pages = 0
    saved_assets = 0

    while queue:
        url = queue.popleft()
        if url in seen:
            continue
        seen.add(url)

        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
        except requests.RequestException:
            continue
        content_type = response.headers.get("content-type", "")
        target_path = local_path_for(output_dir, url, content_type)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        target_path.write_bytes(response.content)

        if content_type.startswith("text/html"):
            saved_pages += 1
            parser = LinkExtractor()
            parser.feed(response.text)
            for raw_link in parser.links:
                if raw_link.startswith(("mailto:", "javascript:", "#")):
                    continue
                linked_url = normalize_url(urljoin(url, raw_link))
                if linked_url in seen:
                    continue
                if is_page_url(linked_url) or is_asset_url(linked_url):
                    queue.append(linked_url)
        else:
            saved_assets += 1

    return saved_pages, saved_assets


def write_readme(output_dir: Path, saved_pages: int, saved_assets: int) -> None:
    readme_path = output_dir / "README.md"
    readme_path.write_text(
        "\n".join(
            [
                "# openrouteservice Docs Mirror",
                "",
                "Downloaded from the official sources:",
                "- https://openrouteservice.org/dev/#/api-docs",
                "- https://giscience.github.io/openrouteservice/api-reference/",
                "",
                f"Saved HTML pages: {saved_pages}",
                f"Saved assets/files: {saved_assets}",
                "",
                "Main local entry points:",
                "- `giscience.github.io/openrouteservice/api-reference/index.html`",
                "- `openrouteservice.org/dev/index.html`",
                "",
                "This is a raw mirror for local reference. Links were not rewritten for offline browsing.",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Download official openrouteservice API docs.")
    parser.add_argument(
        "--output",
        default="docs/openrouteservice",
        help="Directory to write the mirrored docs into.",
    )
    args = parser.parse_args()

    output_dir = Path(args.output)
    if output_dir.exists():
        # Clear old mirror files but keep the parent directory.
        for child in output_dir.iterdir():
            if child.is_dir():
                for nested in sorted(child.rglob("*"), reverse=True):
                    if nested.is_file() or nested.is_symlink():
                        nested.unlink()
                    elif nested.is_dir():
                        nested.rmdir()
                child.rmdir()
            else:
                child.unlink()

    saved_pages, saved_assets = download_docs(output_dir)
    write_readme(output_dir, saved_pages, saved_assets)
    print(f"Saved {saved_pages} HTML pages and {saved_assets} assets under {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
