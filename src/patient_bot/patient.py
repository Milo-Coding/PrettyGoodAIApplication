"""Conversation policy for the simulated patient."""

from .scenarios import Scenario


PATIENT_POLICY = """Act as a realistic patient. Stay consistent with the scenario facts, ask natural
follow-up questions, answer one question at a time, and politely end when the objective is complete.
Do not invent clinical facts or read a fixed script mechanically."""


def build_patient_instructions(scenario: Scenario) -> str:
    return f"{PATIENT_POLICY}\nScenario: {scenario.objective}"
