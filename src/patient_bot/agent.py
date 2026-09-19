"""LiveKit Agents worker entrypoint.

Provider-specific LiveKit pipeline construction belongs here once providers are selected.
"""


def build_pipeline_agent():
    """Return the configured STT -> LLM -> TTS pipeline.

    Raises:
        NotImplementedError: until provider plugins and LiveKit configuration are selected.
    """
    raise NotImplementedError("Configure the LiveKit pipeline providers before running calls")


def main() -> None:
    raise NotImplementedError("LiveKit worker startup is not configured yet")


if __name__ == "__main__":
    main()
