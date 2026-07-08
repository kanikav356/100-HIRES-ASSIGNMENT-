"""Download YouTube transcripts via the Supadata API for experts tracked in RESEARCH/sources.md."""

import os
import re
from urllib.parse import urlparse, parse_qs

from supadata import Supadata, SupadataError

API_KEY = "YOUR_SUPADATA_API_KEY"

supadata = Supadata(api_key=API_KEY)

# Fill in each expert's name and the YouTube URL(s) to pull a transcript from.
VIDEOS = [
    {"expert": "Morgan J. Ingram", "url": "https://www.youtube.com/watch?v=NVMa1jRCu0U"},
    {"expert": "Morgan J. Ingram", "url": "https://www.youtube.com/watch?v=gY2RPCbEnvU"},
    {"expert": "Pierre Herubel", "url": "https://www.youtube.com/watch?v=mc7nK3PYgjw"},
    {"expert": "Pierre Herubel", "url": "https://www.youtube.com/watch?v=2HSavr17yq0"},
    {"expert": "Pierre Herubel", "url": "https://www.youtube.com/watch?v=2eovlLOHOU4"},
    {"expert": "Sherry Shinde", "url": ""},
    {"expert": "Sakshi Tyagi", "url": ""},
    {"expert": "Will McTighe", "url": "https://www.youtube.com/watch?v=5rLlzb6_vgA"},
    {"expert": "Will McTighe", "url": "https://www.youtube.com/watch?v=D_MY33bviuQ"},
    {"expert": "Will McTighe", "url": "https://www.youtube.com/watch?v=F8IGilhJItA"},
    {"expert": "Fatima Khan", "url": "https://www.youtube.com/watch?v=RXm2WK1rLGI"},
    {"expert": "Jesse Chan", "url": ""},
    {"expert": "Lara Acosta", "url": "https://www.youtube.com/watch?v=e3E83C-Xxn0"},
    {"expert": "Lara Acosta", "url": "https://www.youtube.com/watch?v=6d_oxo1R9gs"},
    {"expert": "Lara Acosta", "url": "https://www.youtube.com/watch?v=1ph8i-NDz4k"},
    {"expert": "Matt Barker", "url": ""},
    {"expert": "Amanda Natividad", "url": "https://www.youtube.com/watch?v=gsHFoqf-r10"},
    {"expert": "Amanda Natividad", "url": "https://www.youtube.com/watch?v=8-ZR3fdG7K8"},
    {"expert": "Amanda Natividad", "url": "https://www.youtube.com/watch?v=l7XHNwsJ3ug"},
]

OUTPUT_DIR = os.path.join(
    os.path.dirname(__file__), "..", "..", "youtube-transcripts"
)


def extract_video_id(url):
    """Pull the 11-character video ID out of common YouTube URL formats."""
    parsed = urlparse(url)

    if parsed.hostname in ("youtu.be",):
        return parsed.path.lstrip("/")

    if parsed.hostname and "youtube.com" in parsed.hostname:
        if parsed.path == "/watch":
            return parse_qs(parsed.query).get("v", [None])[0]
        if parsed.path.startswith(("/embed/", "/shorts/")):
            return parsed.path.split("/")[2]

    raise ValueError(f"Could not extract a video ID from URL: {url}")


def slugify(name):
    """Match the kebab-case filenames already used under RESEARCH/."""
    slug = name.strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def save_transcript(expert, url, video_id, text):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    file_path = os.path.join(OUTPUT_DIR, f"{slugify(expert)}-{video_id}.md")

    with open(file_path, "w", encoding="utf-8") as f:
        f.write(f"# {expert}\n\n")
        f.write(f"Source: {url}\n\n")
        f.write("## Transcript\n\n")
        f.write(text + "\n")

    return file_path


def main():
    for entry in VIDEOS:
        expert = entry["expert"]
        url = entry.get("url", "").strip()

        if not url:
            print(f"[SKIP] {expert}: no URL provided")
            continue

        try:
            video_id = extract_video_id(url)
        except ValueError as e:
            print(f"[ERROR] {expert}: {e}")
            continue

        try:
            transcript = supadata.transcript(url=url, text=True, mode="auto")
        except SupadataError as e:
            print(f"[SKIP] {expert}: no transcript available for {url} ({e.message})")
            continue
        except Exception as e:
            print(f"[ERROR] {expert}: unexpected error - {e}")
            continue

        text = transcript.content if isinstance(transcript.content, str) else None
        if not text:
            print(f"[SKIP] {expert}: empty transcript for {url}")
            continue

        file_path = save_transcript(expert, url, video_id, text)
        print(f"[OK] {expert}: saved to {file_path}")


if __name__ == "__main__":
    main()
