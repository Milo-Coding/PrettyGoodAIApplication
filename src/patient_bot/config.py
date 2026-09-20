"""Runtime configuration and outbound-call guardrails.

The project deliberately keeps provider credentials out of source control.  This
module centralises the small amount of configuration that every runtime command
needs and rejects unsafe calling configuration before an agent is started.
"""

from dataclasses import asdict, dataclass
import os
import re
from urllib.parse import urlparse

ASSESSMENT_NUMBER = "+18054398008"
_E164_PATTERN = re.compile(r"^\+[1-9]\d{7,14}$")
_MIN_CALL_DURATION_SECONDS = 30
_MAX_CALL_DURATION_SECONDS = 600


class ConfigurationError(ValueError):
    """Raised when runtime configuration is missing, malformed, or unsafe."""


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

    def public_summary(self) -> dict[str, object]:
        """Return configuration suitable for structured logs.

        Secrets are intentionally absent.  Phone numbers are redacted because
        logs may later be committed with the rest of the call evidence.
        """
        values = asdict(self)
        for key in ("livekit_api_key", "livekit_api_secret", "stt_api_key", "llm_api_key", "tts_api_key"):
            values.pop(key)
        values["caller_number"] = redact_phone_number(self.caller_number)
        values["assessment_number"] = redact_phone_number(self.assessment_number)
        return values


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
        raise ConfigurationError(f"Missing required environment variables: {', '.join(missing)}")

    caller_number = values["CALLER_NUMBER"]
    assessment_number = values.get("ASSESSMENT_NUMBER", ASSESSMENT_NUMBER)
    if not _E164_PATTERN.fullmatch(caller_number):
        raise ConfigurationError("CALLER_NUMBER must be an E.164 phone number")
    if assessment_number != ASSESSMENT_NUMBER:
        raise ConfigurationError("ASSESSMENT_NUMBER must be the fixed assessment number")

    livekit_url = values["LIVEKIT_URL"]
    parsed_livekit_url = urlparse(livekit_url)
    if parsed_livekit_url.scheme not in {"ws", "wss"} or not parsed_livekit_url.hostname:
        raise ConfigurationError("LIVEKIT_URL must be an absolute ws:// or wss:// URL")

    artifact_dir = values.get("ARTIFACT_DIR", "artifacts").strip()
    if not artifact_dir:
        raise ConfigurationError("ARTIFACT_DIR cannot be empty")

    raw_max_duration = values.get("MAX_CALL_DURATION_SECONDS", "240")
    try:
        max_call_duration_seconds = int(raw_max_duration)
    except ValueError as error:
        raise ConfigurationError("MAX_CALL_DURATION_SECONDS must be an integer") from error
    if not _MIN_CALL_DURATION_SECONDS <= max_call_duration_seconds <= _MAX_CALL_DURATION_SECONDS:
        raise ConfigurationError(
            "MAX_CALL_DURATION_SECONDS must be between "
            f"{_MIN_CALL_DURATION_SECONDS} and {_MAX_CALL_DURATION_SECONDS}"
        )

    return Settings(
        livekit_url=livekit_url,
        livekit_api_key=values["LIVEKIT_API_KEY"],
        livekit_api_secret=values["LIVEKIT_API_SECRET"],
        stt_api_key=values["STT_API_KEY"],
        llm_api_key=values["LLM_API_KEY"],
        tts_api_key=values["TTS_API_KEY"],
        caller_number=caller_number,
        assessment_number=assessment_number,
        artifact_dir=artifact_dir,
        max_call_duration_seconds=max_call_duration_seconds,
    )


def redact_phone_number(number: str) -> str:
    """Keep enough digits to correlate a configured caller without publishing it."""
    if len(number) <= 4:
        return "***"
    return f"***{number[-4:]}"
