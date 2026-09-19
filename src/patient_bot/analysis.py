"""Transcript quality and bug-analysis entrypoints."""

from pathlib import Path


def analyze_transcript(transcript_path: str | Path) -> list[str]:
    """Return candidate findings for manual verification."""
    if not Path(transcript_path).exists():
        raise FileNotFoundError(transcript_path)
    return []
