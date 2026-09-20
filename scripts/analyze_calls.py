"""Triage completed transcript artifacts without claiming confirmed bugs."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

from patient_bot.analysis import analyze_transcript, parse_transcript, transcript_summary
from patient_bot.artifacts import read_metadata, write_artifact_index


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--artifact-dir",
        default="artifacts",
        help="Root containing transcripts/ and call-*.json (default: artifacts)",
    )
    parser.add_argument("--transcript", type=Path, help="Analyze one transcript instead of all metadata")
    parser.add_argument(
        "--write-index",
        action="store_true",
        help="Refresh artifacts/index.md before analysis",
    )
    args = parser.parse_args()

    root = Path(args.artifact_dir)
    if args.write_index:
        print(f"Wrote {write_artifact_index(root)}")

    transcript_paths = [args.transcript] if args.transcript else _transcripts_from_metadata(root)
    if not transcript_paths:
        print("No reviewed transcript artifacts found.")
        return 0

    for transcript_path in transcript_paths:
        print(f"\n## {transcript_path}")
        turns = parse_transcript(transcript_path)
        summary = transcript_summary(turns)
        print(
            "Turns: {turn_count}; patient: {patient_turn_count}; agent: {agent_turn_count}; "
            "timestamps: {has_timestamps}".format(**summary)
        )
        findings = analyze_transcript(transcript_path)
        if findings:
            print("Candidate findings — verify against the recording before reporting:")
            for finding in findings:
                print(f"- {finding}")
        else:
            print("No mechanical candidate findings. Manual audio/factual review is still required.")
    return 0


def _transcripts_from_metadata(root: Path) -> list[Path]:
    paths: list[Path] = []
    for metadata_path in sorted(root.glob("call-*.json")):
        metadata = read_metadata(metadata_path)
        transcript_path = root / metadata["transcript_path"]
        if transcript_path.exists():
            paths.append(transcript_path)
        else:
            print(f"Skipping missing transcript referenced by {metadata_path}: {transcript_path}", file=sys.stderr)
    return paths


if __name__ == "__main__":
    raise SystemExit(main())
