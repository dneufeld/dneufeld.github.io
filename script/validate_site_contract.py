#!/usr/bin/env python3

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
SITE_ROOT = ROOT / "_site"
POSTS_ROOT = ROOT / "_posts"
CONFIG_PATH = ROOT / "_config.yml"

DESCRIPTION_BLOCKLIST = (
    re.compile(r"\bnot financial advice\b", re.IGNORECASE),
    re.compile(r"\bformer Shopify employee\b", re.IGNORECASE),
)


def normalize_text(value: str | None) -> str:
    if value is None:
        return ""

    translation = str.maketrans(
        {
            "\u2018": "'",
            "\u2019": "'",
            "\u201c": '"',
            "\u201d": '"',
            "\u2013": "-",
            "\u2014": "-",
            "\xa0": " ",
        }
    )
    return re.sub(r"\s+", " ", value.translate(translation)).strip()


def parse_scalar_yaml(path: Path) -> dict[str, str]:
    data: dict[str, str] = {}
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or line.startswith("- "):
            continue
        if raw_line.startswith("  "):
            continue
        if ":" not in raw_line:
            continue

        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(value[:1]):
            value = value[1:-1]
        data[key] = value
    return data


def parse_front_matter(path: Path) -> dict[str, str]:
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        raise ValueError(f"{path} is missing YAML front matter")

    _, front_matter, _ = content.split("---", 2)
    data: dict[str, str] = {}
    for raw_line in front_matter.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or ":" not in raw_line:
            continue

        key, value = raw_line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith(("'", '"')) and value.endswith(value[:1]):
            value = value[1:-1]
        data[key] = value
    return data


class HeadParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta_tags: list[dict[str, str]] = []
        self.link_tags: list[dict[str, str]] = []
        self.script_tags: list[dict[str, str]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._store_tag(tag, attrs)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self._store_tag(tag, attrs)

    def _store_tag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "meta":
            self.meta_tags.append(attributes)
        elif tag == "link":
            self.link_tags.append(attributes)
        elif tag == "script":
            self.script_tags.append(attributes)

    def meta_content(self, *, name: str | None = None, property_name: str | None = None) -> str | None:
        for attrs in self.meta_tags:
            if name and attrs.get("name") == name:
                return attrs.get("content")
            if property_name and attrs.get("property") == property_name:
                return attrs.get("content")
        return None

    def canonical_href(self) -> str | None:
        for attrs in self.link_tags:
            if attrs.get("rel") == "canonical":
                return attrs.get("href")
        return None

    def cloudflare_script(self) -> dict[str, str] | None:
        for attrs in self.script_tags:
            if attrs.get("src") == "https://static.cloudflareinsights.com/beacon.min.js":
                return attrs
        return None


@dataclass
class ValidationError:
    path: Path
    message: str


def post_output_path(permalink: str) -> Path:
    clean_permalink = permalink.strip("/")
    return SITE_ROOT / clean_permalink / "index.html"


def validate_front_matter(path: Path, front_matter: dict[str, str]) -> list[ValidationError]:
    errors: list[ValidationError] = []
    required = ("layout", "title", "permalink", "description")

    for field in required:
        value = front_matter.get(field, "").strip()
        if not value:
            errors.append(ValidationError(path, f"missing required front matter field: {field}"))

    if front_matter.get("layout") and front_matter["layout"] != "post":
        errors.append(ValidationError(path, "layout must be 'post'"))

    description = front_matter.get("description", "")
    for pattern in DESCRIPTION_BLOCKLIST:
        if pattern.search(description):
            errors.append(ValidationError(path, "description looks like disclaimer text"))

    return errors


def validate_built_output(
    path: Path,
    front_matter: dict[str, str],
    site_url: str,
    cloudflare_token: str,
) -> list[ValidationError]:
    errors: list[ValidationError] = []
    output_path = post_output_path(front_matter["permalink"])

    if not output_path.exists():
        return [ValidationError(path, f"missing built HTML at {output_path}")]

    parser = HeadParser()
    parser.feed(output_path.read_text(encoding="utf-8"))

    expected_description = normalize_text(front_matter["description"])
    expected_title = normalize_text(front_matter["title"])
    expected_canonical = f"{site_url.rstrip('/')}{front_matter['permalink']}"

    rendered_description = normalize_text(parser.meta_content(name="description"))
    rendered_og_description = normalize_text(parser.meta_content(property_name="og:description"))
    rendered_twitter_description = normalize_text(parser.meta_content(name="twitter:description"))
    rendered_og_title = normalize_text(parser.meta_content(property_name="og:title"))
    rendered_canonical = normalize_text(parser.canonical_href())
    rendered_og_url = normalize_text(parser.meta_content(property_name="og:url"))

    if rendered_description != expected_description:
        errors.append(ValidationError(path, "meta description does not match front matter"))

    if rendered_og_description != expected_description:
        errors.append(ValidationError(path, "og:description does not match front matter"))

    if rendered_twitter_description != expected_description:
        errors.append(ValidationError(path, "twitter:description does not match front matter"))

    if rendered_og_title != expected_title:
        errors.append(ValidationError(path, "og:title does not match front matter title"))

    if rendered_canonical != expected_canonical:
        errors.append(ValidationError(path, "canonical URL does not match site URL + permalink"))

    if rendered_og_url != expected_canonical:
        errors.append(ValidationError(path, "og:url does not match site URL + permalink"))

    cloudflare_script = parser.cloudflare_script()
    if cloudflare_token:
        if not cloudflare_script:
            errors.append(ValidationError(path, "missing Cloudflare Web Analytics script"))
        else:
            beacon_config = cloudflare_script.get("data-cf-beacon", "")
            if f'"token":"{cloudflare_token}"' not in beacon_config:
                errors.append(ValidationError(path, "Cloudflare token does not match _config.yml"))

    return errors


def main() -> int:
    if not SITE_ROOT.exists():
        print("missing _site/ directory, run `bundle exec jekyll build` first", file=sys.stderr)
        return 1

    config = parse_scalar_yaml(CONFIG_PATH)
    site_url = config.get("url", "").strip()
    cloudflare_token = config.get("cloudflare_web_analytics_token", "").strip()

    if not site_url:
        print("_config.yml is missing url", file=sys.stderr)
        return 1

    errors: list[ValidationError] = []
    for path in sorted(POSTS_ROOT.glob("*.md")):
        front_matter = parse_front_matter(path)
        errors.extend(validate_front_matter(path, front_matter))
        if all(field in front_matter for field in ("permalink", "description", "title")):
            errors.extend(validate_built_output(path, front_matter, site_url, cloudflare_token))

    if errors:
        for error in errors:
            print(f"{error.path}: {error.message}", file=sys.stderr)
        return 1

    print(f"validated {len(list(POSTS_ROOT.glob('*.md')))} posts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
