"""Patient test scenario definitions."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Scenario:
    scenario_id: str
    name: str
    objective: str
    facts: dict[str, str] = field(default_factory=dict)
    success_criteria: tuple[str, ...] = ()
    bug_signals: tuple[str, ...] = ()


SCENARIOS: tuple[Scenario, ...] = (
    Scenario("01", "new-appointment", "Schedule a routine weekday appointment"),
    Scenario("02", "reschedule", "Move an existing appointment"),
    Scenario("03", "cancel", "Cancel an appointment safely"),
    Scenario("04", "medication-refill", "Request a medication refill"),
    Scenario("05", "office-hours", "Test office hours and weekend handling"),
    Scenario("06", "location", "Ask for location and access information"),
    Scenario("07", "insurance", "Test insurance coverage handling"),
    Scenario("08", "ambiguous-request", "Evaluate clarification behavior"),
    Scenario("09", "interruption", "Test barge-in and recovery"),
    Scenario("10", "compound-request", "Test conflicting or multiple needs"),
)


def get_scenario(name: str) -> Scenario:
    for scenario in SCENARIOS:
        if scenario.name == name or scenario.scenario_id == name:
            return scenario
    raise KeyError(f"Unknown scenario: {name}")
