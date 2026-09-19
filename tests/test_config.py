from patient_bot.config import ASSESSMENT_NUMBER, load_settings


def valid_environment() -> dict[str, str]:
    return {
        "LIVEKIT_URL": "wss://example.livekit.cloud",
        "LIVEKIT_API_KEY": "key",
        "LIVEKIT_API_SECRET": "secret",
        "STT_API_KEY": "stt",
        "LLM_API_KEY": "llm",
        "TTS_API_KEY": "tts",
        "CALLER_NUMBER": "+15551234567",
        "ASSESSMENT_NUMBER": ASSESSMENT_NUMBER,
    }


def test_load_settings_accepts_valid_environment() -> None:
    settings = load_settings(valid_environment())
    assert settings.assessment_number == ASSESSMENT_NUMBER


def test_load_settings_rejects_wrong_destination() -> None:
    environment = valid_environment()
    environment["ASSESSMENT_NUMBER"] = "+15551234567"
    try:
        load_settings(environment)
    except ValueError as error:
        assert "fixed assessment number" in str(error)
    else:
        raise AssertionError("Expected destination validation to fail")
