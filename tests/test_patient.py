from patient_bot.patient import build_patient_instructions
from patient_bot.scenarios import get_scenario


def test_patient_instructions_include_objective() -> None:
    instructions = build_patient_instructions(get_scenario("01"))
    assert "Schedule a routine weekday appointment" in instructions
