"""Runtime configuration and outbound-call guardrails."""

from dataclasses import dataclass
import os
import re

ASSESSMENT_NUMBER = "+18054398008"
_E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")


@dataclass(frozen=True)
class Settings:
    livekit_url: str
    livekit_api_key: str
    livekit_api_secret: str
    stt_api_key: str
    llm_api_key: str
    tts_api_key: str
    caller_number: str
    assessment_number: str = ASSESSMENT_NUMBER
    artifact_dir: str = "artifacts"
    max_call_duration_seconds: int = 240


def load_settings(environ: dict[str, str] | None = None) -> Settings:
    values = os.environ if environ is None else environ
    required = (
        "LIVEKIT_URL",
        "LIVEKIT_API_KEY",
        "LIVEKIT_API_SECRET",
        "STT_API_KEY",
        "LLM_API_KEY",
        "TTS_API_KEY",
        "CALLER_NUMBER",
    )
    missing = [name for name in required if not values.get(name)]
    if missing:
        raise ValueError(f"Missing required environment variables: {', '.join(missing)}")

    caller_number = values["CALLER_NUMBER"]
    assessment_number = values.get("ASSESSMENT_NUMBER", ASSESSMENT_NUMBER)
    if not _E164_PATTERN.fullmatch(caller_number):
        raise ValueError("CALLER_NUMBER must be an E.164 phone number")
    if assessment_number != ASSESSMENT_NUMBER:
        raise ValueError("ASSESSMENT_NUMBER must be the fixed assessment number")

    return Settings(
        livekit_url=values["LIVEKIT_URL"],
        livekit_api_key=values["LIVEKIT_API_KEY"],
        livekit_api_secret=values["LIVEKIT_API_SECRET"],
        stt_api_key=values["STT_API_KEY"],
        llm_api_key=values["LLM_API_KEY"],
        tts_api_key=values["TTS_API_KEY"],
        caller_number=caller_number,
        assessment_number=assessment_number,
        artifact_dir=values.get("ARTIFACT_DIR", "artifacts"),
        max_call_duration_seconds=int(values.get("MAX_CALL_DURATION_SECONDS", "240")),
    )
