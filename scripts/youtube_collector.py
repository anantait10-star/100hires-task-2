"""Collect YouTube transcripts for outbound research.

How to run:
1. Install dependencies:
   python -m pip install -r requirements.txt

2. Collect one or more transcripts:
   python scripts/youtube_collector.py --expert "Armand Farrokh" "https://www.youtube.com/watch?v=VIDEO_ID"

Output files are saved to:
   research/youtube-transcripts/{expert-name}/{clean-video-title}.md
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.error import URLError
from urllib.parse import parse_qs, quote, urlparse
from urllib.request import urlopen

from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    NoTranscriptFound,
    TranscriptsDisabled,
    VideoUnavailable,
)


REPO_ROOT = Path(__file__).resolve().parents[1]
TRANSCRIPT_ROOT = REPO_ROOT / "research" / "youtube-transcripts"


class InvalidYouTubeUrl(ValueError):
    """Raised when a URL does not contain a recognizable YouTube video id."""


def slugify(value: str, fallback: str = "untitled") -> str:
    """Convert names and titles into clean filesystem-safe slugs."""
    cleaned = value.lower().strip()
    cleaned = re.sub(r"[^a-z0-9]+", "-", cleaned)
    cleaned = cleaned.strip("-")
    return cleaned or fallback


def extract_video_id(video_url: str) -> str:
    """Extract a YouTube video id from common watch, short, embed, and shorts URLs."""
    parsed = urlparse(video_url)
    host = parsed.netloc.lower().replace("www.", "")

    if host == "youtu.be":
        video_id = parsed.path.strip("/").split("/")[0]
    elif host in {"youtube.com", "m.youtube.com", "music.youtube.com"}:
        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [""])[0]
        elif parsed.path.startswith(("/embed/", "/shorts/")):
            video_id = parsed.path.strip("/").split("/")[1]
        else:
            video_id = ""
    else:
        video_id = ""

    if not re.fullmatch(r"[A-Za-z0-9_-]{11}", video_id or ""):
        raise InvalidYouTubeUrl(f"Invalid YouTube URL: {video_url}")

    return video_id


def fetch_video_title(video_url: str, video_id: str) -> str:
    """Fetch a video title when YouTube oEmbed is available; otherwise use the id."""
    oembed_url = (
        "https://www.youtube.com/oembed?format=json&url="
        + quote(video_url, safe="")
    )

    try:
        with urlopen(oembed_url, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (URLError, TimeoutError, OSError, json.JSONDecodeError):
        return video_id

    title = str(payload.get("title", "")).strip()
    return title or video_id


def fetch_transcript_text(video_id: str) -> str:
    """Fetch transcript text using youtube-transcript-api."""
    try:
        try:
            transcript_items = YouTubeTranscriptApi.get_transcript(video_id)
        except AttributeError:
            transcript_items = YouTubeTranscriptApi().fetch(video_id).to_raw_data()
    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable) as error:
        raise RuntimeError(f"Transcript unavailable for {video_id}: {error}") from error

    lines = []
    for item in transcript_items:
        text = str(item.get("text", "")).replace("\n", " ").strip()
        if text:
            lines.append(text)

    if not lines:
        raise RuntimeError(f"Transcript was empty for {video_id}.")

    return "\n".join(lines)


def build_markdown(
    expert_name: str,
    video_url: str,
    video_title: str,
    transcript_text: str,
) -> str:
    """Build the markdown file with front matter metadata and transcript body."""
    return "\n".join(
        [
            "---",
            f"expert: {expert_name}",
            "source: youtube",
            f"video_url: {video_url}",
            f"date_collected: {date.today().isoformat()}",
            "---",
            "",
            f"# {video_title}",
            "",
            transcript_text,
            "",
        ]
    )


def save_transcript(expert_name: str, video_title: str, markdown: str) -> Path:
    """Create the expert folder if needed and save the transcript markdown."""
    expert_slug = slugify(expert_name, fallback="unknown-expert")
    title_slug = slugify(video_title, fallback="untitled-video")
    output_dir = TRANSCRIPT_ROOT / expert_slug
    output_dir.mkdir(parents=True, exist_ok=True)

    output_path = output_dir / f"{title_slug}.md"
    counter = 2
    while output_path.exists():
        output_path = output_dir / f"{title_slug}-{counter}.md"
        counter += 1

    output_path.write_text(markdown, encoding="utf-8")
    return output_path


def collect_video(expert_name: str, video_url: str) -> Path:
    """Collect one video transcript and return the saved file path."""
    video_id = extract_video_id(video_url)
    video_title = fetch_video_title(video_url, video_id)
    transcript_text = fetch_transcript_text(video_id)
    markdown = build_markdown(expert_name, video_url, video_title, transcript_text)
    return save_transcript(expert_name, video_title, markdown)


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Collect YouTube transcripts into the research folder."
    )
    parser.add_argument(
        "--expert",
        required=True,
        help='Expert name used for metadata and folder name, e.g. "Armand Farrokh".',
    )
    parser.add_argument(
        "video_urls",
        nargs="+",
        help="One or more YouTube video URLs.",
    )
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])

    if not TRANSCRIPT_ROOT.exists():
        print(f"Creating missing transcript folder: {TRANSCRIPT_ROOT}")
        TRANSCRIPT_ROOT.mkdir(parents=True, exist_ok=True)

    failures = 0
    for video_url in args.video_urls:
        try:
            output_path = collect_video(args.expert, video_url)
        except InvalidYouTubeUrl as error:
            failures += 1
            print(f"[invalid-url] {error}", file=sys.stderr)
        except RuntimeError as error:
            failures += 1
            print(f"[transcript-error] {error}", file=sys.stderr)
        except OSError as error:
            failures += 1
            print(f"[file-error] Could not save transcript: {error}", file=sys.stderr)
        else:
            print(f"Saved transcript: {output_path.relative_to(REPO_ROOT)}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
