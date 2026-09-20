"""Portable, public-safe call artifact helpers.

Only reviewed recordings and transcripts should be committed.  Runtime code can
use these helpers to keep the public evidence predictable without ever writing
provider credentials or full phone numbers into artifact metadata.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any, Mapping


_CALL_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9-]{0,79}$")
_SENSITIVE_KEY_PARTS = ("api_key", "apikey", "secret", "token", "password", "authorization")


@dataclass(frozen=True)
class ArtifactPaths:
    """Canonical locations for one completed call's public evidence."""

    recording: Path
    transcript: Path
    metadata: Path


@dataclass(frozen=True)
class CallMetadata:
    """Minimal public metadata that links a call to its evidence.

    Paths are repository-relative strings.  Provider versions are useful for
    reproduction, but must never contain provider credentials or request IDs
    that expose sensitive account data.
    """

    call_id: str
    scenario_id: str
    scenario_name: str
    started_at_utc: str
    outcome: str
    recording_path: str
    transcript_path: str
    ended_at_utc: str | None = None
    duration_seconds: float | None = None
    termination_reason: str | None = None
    provider_versions: dict[str, str] = field(default_factory=dict)
    notes: str | None = None

    def to_dict(self) -> dict[str, Any]:
        """Validate and return metadata ready for JSON serialization."""
        validate_call_id(self.call_id)
        values = asdict(self)
        assert_public_metadata(values)
        return values


def validate_call_id(call_id: str) -> None:
    """Reject path traversal and unstable artifact names."""
    if not _CALL_ID_PATTERN.fullmatch(call_id):
        raise ValueError(
            "call_id must use lowercase letters, digits, and single hyphens "
            "(for example, 'call-01-new-appointment')"
        )


def artifact_paths(root: str | Path, call_id: str) -> ArtifactPaths:
    """Return stable paths without creating files or directories."""
    validate_call_id(call_id)
    root_path = Path(root)
    return ArtifactPaths(
        recording=root_path / "recordings" / f"{call_id}.mp3",
        transcript=root_path / "transcripts" / f"{call_id}.txt",
        metadata=root_path / f"{call_id}.json",
    )


def ensure_artifact_directories(root: str | Path) -> Path:
    """Create the fixed artifact layout and return its root directory."""
    root_path = Path(root)
    (root_path / "recordings").mkdir(parents=True, exist_ok=True)
    (root_path / "transcripts").mkdir(parents=True, exist_ok=True)
    return root_path


def write_metadata(path: str | Path, metadata: CallMetadata | Mapping[str, Any]) -> Path:
    """Write validated, indented JSON metadata for a completed or partial call."""
    target = Path(path)
    values = metadata.to_dict() if isinstance(metadata, CallMetadata) else dict(metadata)
    _validate_metadata_shape(values)
    assert_public_metadata(values)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(values, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return target


def read_metadata(path: str | Path) -> dict[str, Any]:
    """Read and validate a call metadata JSON document."""
    source = Path(path)
    try:
        values = json.loads(source.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(f"Invalid call metadata JSON: {source}") from error
    if not isinstance(values, dict):
        raise ValueError(f"Call metadata must be a JSON object: {source}")
    _validate_metadata_shape(values)
    assert_public_metadata(values)
    return values


def build_artifact_index(root: str | Path) -> str:
    """Render a small Markdown index from available call metadata files."""
    root_path = Path(root)
    rows: list[dict[str, Any]] = []
    for metadata_path in sorted(root_path.glob("call-*.json")):
        rows.append(read_metadata(metadata_path))

    lines = [
        "# Call Artifact Index",
        "",
        "Only calls with reviewed two-sided audio and a readable transcript should be counted.",
        "",
        "| Call | Scenario | Outcome | Duration | Recording | Transcript |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in rows:
        duration = _format_duration(item.get("duration_seconds"))
        lines.append(
            "| {call_id} | {scenario_name} | {outcome} | {duration} | "
            "[{recording}](./{recording}) | [{transcript}](./{transcript}) |".format(
                call_id=item["call_id"],
                scenario_name=item["scenario_name"],
                outcome=item["outcome"],
                duration=duration,
                recording=item["recording_path"],
                transcript=item["transcript_path"],
            )
        )
    if not rows:
        lines.extend(["| _No reviewed calls yet_ | — | — | — | — | — |", ""])
    return "\n".join(lines) + "\n"


def write_artifact_index(root: str | Path) -> Path:
    """Create or refresh ``artifacts/index.md`` from call metadata."""
    root_path = ensure_artifact_directories(root)
    index_path = root_path / "index.md"
    index_path.write_text(build_artifact_index(root_path), encoding="utf-8")
    return index_path


def assert_public_metadata(values: Mapping[str, Any]) -> None:
    """Fail fast if metadata appears to contain a credential.

    This is a deliberately conservative guard, not a replacement for manual
    review before publishing recordings or transcripts.
    """
    for key, value in _walk_mapping(values):
        normalized = key.lower().replace("-", "_")
        if any(part in normalized for part in _SENSITIVE_KEY_PARTS):
            raise ValueError(f"Sensitive field is not allowed in public metadata: {key}")
        if isinstance(value, str) and _looks_like_phone_number(value):
            raise ValueError("Full phone numbers are not allowed in public metadata")


def utc_now() -> str:
    """Return a stable ISO-8601 UTC timestamp for metadata creation."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _validate_metadata_shape(values: Mapping[str, Any]) -> None:
    required = {
        "call_id",
        "scenario_id",
        "scenario_name",
        "started_at_utc",
        "outcome",
        "recording_path",
        "transcript_path",
    }
    missing = sorted(required.difference(values))
    if missing:
        raise ValueError(f"Call metadata is missing required fields: {', '.join(missing)}")
    if not isinstance(values["call_id"], str):
        raise ValueError("call_id must be a string")
    validate_call_id(values["call_id"])
    for field_name in ("scenario_id", "scenario_name", "started_at_utc", "outcome", "recording_path", "transcript_path"):
        if not isinstance(values[field_name], str) or not values[field_name].strip():
            raise ValueError(f"{field_name} must be a non-empty string")
    for path_field in ("recording_path", "transcript_path"):
        path = Path(values[path_field])
        if path.is_absolute() or ".." in path.parts:
            raise ValueError(f"{path_field} must be a safe repository-relative path")


def _walk_mapping(value: Any, prefix: str = "") -> list[tuple[str, Any]]:
    if isinstance(value, Mapping):
        pairs: list[tuple[str, Any]] = []
        for key, nested_value in value.items():
            key_name = f"{prefix}.{key}" if prefix else str(key)
            pairs.extend(_walk_mapping(nested_value, key_name))
        return pairs
    if isinstance(value, list):
        pairs = []
        for index, nested_value in enumerate(value):
            pairs.extend(_walk_mapping(nested_value, f"{prefix}[{index}]"))
        return pairs
    return [(prefix, value)]


def _looks_like_phone_number(value: str) -> bool:
    return bool(re.fullmatch(r"\+[1-9]\d{7,14}", value.strip()))


def _format_duration(value: Any) -> str:
    if not isinstance(value, (int, float)) or value < 0:
        return "—"
    minutes, seconds = divmod(round(value), 60)
    return f"{minutes}:{seconds:02d}"
