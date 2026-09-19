from patient_bot.artifacts import artifact_paths


def test_artifact_paths_are_stable() -> None:
    paths = artifact_paths("artifacts", "call-01-new-appointment")
    assert paths.recording.name.endswith(".mp3")
    assert paths.transcript.name.endswith(".txt")
    assert paths.metadata.name.endswith(".json")
