"""Call artifact paths and metadata helpers."""

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ArtifactPaths:
    recording: Path
    transcript: Path
    metadata: Path


def artifact_paths(root: str | Path, call_id: str) -> ArtifactPaths:
    root_path = Path(root)
    return ArtifactPaths(
        recording=root_path / "recordings" / f"{call_id}.mp3",
        transcript=root_path / "transcripts" / f"{call_id}.txt",
        metadata=root_path / f"{call_id}.json",
    )
