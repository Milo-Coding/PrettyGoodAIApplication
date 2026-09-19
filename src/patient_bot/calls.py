"""Outbound-call orchestration and destination guardrails."""

from .config import ASSESSMENT_NUMBER, Settings


def validate_destination(destination: str) -> None:
    if destination != ASSESSMENT_NUMBER:
        raise ValueError("Outbound calls are restricted to the assessment number")


def run_call(settings: Settings, scenario_name: str) -> None:
    """Placeholder for one guarded LiveKit/SIP call."""
    validate_destination(settings.assessment_number)
    raise NotImplementedError(f"Call runner is not configured for scenario {scenario_name!r}")
