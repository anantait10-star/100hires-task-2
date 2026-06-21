"""Format manually collected LinkedIn posts for outbound research.

Workflow:
1. Manually collect the original LinkedIn post text into a local text file.
2. Run this formatter with the expert name, post URL, and input file path.
3. Review the generated markdown under research/linkedin-posts/{expert-name}/.

Example:
   python scripts/linkedin_formatter.py \
       --expert "Josh Braun" \
       --post-url "https://www.linkedin.com/posts/..." \
       --input manual-post.txt

This script does not scrape LinkedIn and does not create placeholder posts.
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterable


REPO_ROOT = Path(__file__).resolve().parents[1]
LINKEDIN_ROOT = REPO_ROOT / "research" / "linkedin-posts"


def slugify(value: str, fallback: str = "untitled") -> str:
    """Convert names into clean filesystem-safe slugs."""
    cleaned = value.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    cleaned = cleaned.strip("-")
    return cleaned or fallback


def validate_post_url(post_url: str) -> None:
    """Require a LinkedIn URL so source attribution stays trustworthy."""
    if not re.match(r"^https://(www\.)?linkedin\.com/", post_url.strip()):
        raise ValueError("post_url must be a LinkedIn URL.")


def read_post_text(input_path: Path) -> str:
    """Read manually collected post text and reject empty content."""
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    post_text = input_path.read_text(encoding="utf-8").strip()
    if not post_text:
        raise ValueError("Input file is empty. No LinkedIn post was formatted.")

    return post_text


def next_output_path(expert_name: str, post_date: str | None = None) -> Path:
    """Build the output path using post date when supplied, otherwise a number."""
    expert_slug = slugify(expert_name, fallback="unknown-expert")
    output_dir = LINKEDIN_ROOT / expert_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    if post_date:
        base_name = f"post-{slugify(post_date, fallback='date')}"
        output_path = output_dir / f"{base_name}.md"
        counter = 2
        while output_path.exists():
            output_path = output_dir / f"{base_name}-{counter}.md"
            counter += 1
        return output_path

    existing = list(output_dir.glob("post-*.md"))
    return output_dir / f"post-{len(existing) + 1:03d}.md"


def build_markdown(expert_name: str, post_url: str, post_text: str) -> str:
    """Build markdown with required metadata and original post wording."""
    return "\n".join(
        [
            "---",
            f"expert: {expert_name}",
            "source: linkedin",
            f"post_url: {post_url}",
            f"date_collected: {date.today().isoformat()}",
            "---",
            "",
            post_text,
            "",
        ]
    )


def format_post(
    expert_name: str,
    post_url: str,
    input_path: Path,
    post_date: str | None = None,
) -> Path:
    """Convert one manually collected LinkedIn post into a markdown file."""
    validate_post_url(post_url)
    post_text = read_post_text(input_path)
    output_path = next_output_path(expert_name, post_date)
    output_path.write_text(build_markdown(expert_name, post_url, post_text), encoding="utf-8")
    return output_path


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Format manually collected LinkedIn posts into markdown."
    )
    parser.add_argument(
        "--expert",
        required=True,
        help='Expert name used for metadata and folder name, e.g. "Josh Braun".',
    )
    parser.add_argument(
        "--post-url",
        required=True,
        help="Canonical LinkedIn post URL.",
    )
    parser.add_argument(
        "--input",
        required=True,
        type=Path,
        help="Path to a text file containing the original manually collected post.",
    )
    parser.add_argument(
        "--post-date",
        help="Optional post date for the output filename, e.g. 2026-06-21.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    try:
        output_path = format_post(
            expert_name=args.expert,
            post_url=args.post_url,
            input_path=args.input,
            post_date=args.post_date,
        )
    except (FileNotFoundError, OSError, ValueError) as error:
        print(f"[linkedin-format-error] {error}", file=sys.stderr)
        return 1

    print(f"Saved LinkedIn post: {output_path.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
