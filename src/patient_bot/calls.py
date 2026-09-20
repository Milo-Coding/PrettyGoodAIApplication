"""Outbound-call planning and destination guardrails.

The actual SIP dispatch is intentionally kept behind this module.  That gives
the project one place to enforce the challenge's single permitted destination
before a provider-specific implementation can spend money or place a call.
"""

from __future__ import annotations

from dataclasses import dataclass

from .config import ASSESSMENT_NUMBER, Settings
from .scenarios import Scenario, get_scenario


@dataclass(frozen=True)
class CallPlan:
    """A validated, provider-neutral description of one outbound test call."""

    scenario: Scenario
    caller_number: str
    destination: str
    max_duration_seconds: int


def validate_destination(destination: str) -> None:
    """Ensure a caller cannot be repurposed to reach another phone number."""
    if destination != ASSESSMENT_NUMBER:
        raise ValueError("Outbound calls are restricted to the assessment number")


def build_call_plan(settings: Settings, scenario_name: str) -> CallPlan:
    """Select a known scenario and validate all call-critical settings."""
    validate_destination(settings.assessment_number)
    return CallPlan(
        scenario=get_scenario(scenario_name),
        caller_number=settings.caller_number,
        destination=settings.assessment_number,
        max_duration_seconds=settings.max_call_duration_seconds,
    )


def run_call(settings: Settings, scenario_name: str) -> None:
    """Run one guarded LiveKit/SIP call after a provider runner is configured."""
    build_call_plan(settings, scenario_name)
    raise RuntimeError(
        "No LiveKit/SIP call runner is configured yet. "
        "Provider selection, credentials, and explicit approval are required before a paid call."
    )
