"""Transcript triage helpers for the manual bug-review workflow.

Automated findings are deliberately labelled as candidates.  A transcript cannot
prove audio quality, factual correctness, or a product bug; reviewers must
listen to the linked recording before putting a finding in ``docs/bug-report.md``.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Iterable


_TIMESTAMPED_TURN = re.compile(
    r"^\[(?P<timestamp>(?:(?P<hours>\d{1,2}):)?(?P<minutes>\d{1,2}):(?P<seconds>\d{2}))\]\s*"
    r"(?P<speaker>[A-Za-z][A-Za-z _-]{0,31})\s*:\s*(?P<text>.+?)\s*$"
)
_UNTIMESTAMPED_TURN = re.compile(
    r"^(?P<speaker>[A-Za-z][A-Za-z _-]{0,31})\s*:\s*(?P<text>.+?)\s*$"
)
_SPEAKER_ALIASES = {
    "patient": "patient",
    "caller": "patient",
    "user": "patient",
    "agent": "agent",
    "assistant": "agent",
    "office": "agent",
    "staff": "agent",
}


@dataclass(frozen=True)
class TranscriptTurn:
    """One human-readable call turn parsed from a plain-text transcript."""

    speaker: str
    text: str
    line_number: int
    timestamp_seconds: int | None = None

    @property
    def timestamp_label(self) -> str:
        if self.timestamp_seconds is None:
            return "line " + str(self.line_number)
        minutes, seconds = divmod(self.timestamp_seconds, 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


@dataclass(frozen=True)
class CandidateFinding:
    """A lead for manual inspection, never a confirmed defect."""

    category: str
    evidence: str
    timestamp: str

    def render(self) -> str:
        return f"{self.category} at {self.timestamp}: {self.evidence}"


def parse_transcript(transcript_path: str | Path) -> list[TranscriptTurn]:
    """Parse the documented transcript format into speaker-labelled turns.

    Preferred format: ``[00:01:07] PATIENT: I need to reschedule.``  Untimed
    ``SPEAKER: text`` rows are accepted so a provider export can be reviewed,
    but they are surfaced as a candidate quality issue.
    """
    source = Path(transcript_path)
    if not source.exists():
        raise FileNotFoundError(source)
    return parse_transcript_text(source.read_text(encoding="utf-8"))


def parse_transcript_text(text: str) -> list[TranscriptTurn]:
    """Parse transcript text; ignore blank and comment lines."""
    turns: list[TranscriptTurn] = []
    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        timestamped = _TIMESTAMPED_TURN.fullmatch(line)
        if timestamped:
            turns.append(
                TranscriptTurn(
                    speaker=_normalise_speaker(timestamped.group("speaker")),
                    text=timestamped.group("text"),
                    line_number=line_number,
                    timestamp_seconds=_to_seconds(timestamped),
                )
            )
            continue
        untimed = _UNTIMESTAMPED_TURN.fullmatch(line)
        if untimed:
            turns.append(
                TranscriptTurn(
                    speaker=_normalise_speaker(untimed.group("speaker")),
                    text=untimed.group("text"),
                    line_number=line_number,
                )
            )
    return turns


def analyze_transcript(transcript_path: str | Path) -> list[str]:
    """Return candidate findings suitable for manual verification.

    This intentionally retains the original public API of a list of strings so
    existing scripts can use it without depending on provider-specific formats.
    """
    return [finding.render() for finding in find_candidates(parse_transcript(transcript_path))]


def find_candidates(turns: Iterable[TranscriptTurn]) -> list[CandidateFinding]:
    """Flag mechanical transcript-quality signals for a human to inspect."""
    parsed_turns = list(turns)
    if not parsed_turns:
        return [
            CandidateFinding(
                category="Unreadable transcript",
                timestamp="start",
                evidence="No speaker-labelled conversation turns were parsed.",
            )
        ]

    candidates: list[CandidateFinding] = []
    speakers = {turn.speaker for turn in parsed_turns}
    if "patient" not in speakers or "agent" not in speakers:
        missing = "patient" if "patient" not in speakers else "agent"
        candidates.append(
            CandidateFinding(
                category="Missing call side",
                timestamp="start",
                evidence=f"No recognised {missing} turns were found; verify the recording and labels.",
            )
        )

    untimed = [turn for turn in parsed_turns if turn.timestamp_seconds is None]
    if untimed:
        candidates.append(
            CandidateFinding(
                category="Missing timestamp",
                timestamp=f"line {untimed[0].line_number}",
                evidence="One or more turns have no timestamp, limiting evidence review.",
            )
        )

    for previous, current in zip(parsed_turns, parsed_turns[1:]):
        if previous.timestamp_seconds is not None and current.timestamp_seconds is not None:
            gap = current.timestamp_seconds - previous.timestamp_seconds
            if gap >= 20:
                candidates.append(
                    CandidateFinding(
                        category="Long turn gap",
                        timestamp=current.timestamp_label,
                        evidence=f"{gap} seconds since the prior labelled turn; listen for dead air or latency.",
                    )
                )
        if previous.speaker == current.speaker == "agent":
            candidates.append(
                CandidateFinding(
                    category="Consecutive agent turns",
                    timestamp=current.timestamp_label,
                    evidence="Verify whether interruption recovery or a duplicate response occurred.",
                )
            )

    for turn in parsed_turns:
        if len(turn.text) > 420:
            candidates.append(
                CandidateFinding(
                    category="Overlong turn",
                    timestamp=turn.timestamp_label,
                    evidence=f"{turn.speaker.title()} turn contains {len(turn.text)} characters; review phone pacing.",
                )
            )
    return candidates


def transcript_summary(turns: Iterable[TranscriptTurn]) -> dict[str, int | bool]:
    """Return simple counts for an artifact index or CI check."""
    parsed_turns = list(turns)
    return {
        "turn_count": len(parsed_turns),
        "patient_turn_count": sum(turn.speaker == "patient" for turn in parsed_turns),
        "agent_turn_count": sum(turn.speaker == "agent" for turn in parsed_turns),
        "has_timestamps": bool(parsed_turns) and all(turn.timestamp_seconds is not None for turn in parsed_turns),
    }


def _normalise_speaker(speaker: str) -> str:
    normalized = " ".join(speaker.lower().split())
    return _SPEAKER_ALIASES.get(normalized, normalized)


def _to_seconds(match: re.Match[str]) -> int:
    hours = int(match.group("hours") or 0)
    minutes = int(match.group("minutes"))
    seconds = int(match.group("seconds"))
    if minutes >= 60 or seconds >= 60:
        raise ValueError(f"Invalid transcript timestamp: {match.group('timestamp')}")
    return hours * 3600 + minutes * 60 + seconds
