from patient_bot.scenarios import SCENARIOS, get_scenario


def test_suite_has_ten_scenarios() -> None:
    assert len(SCENARIOS) == 10


def test_scenario_can_be_selected_by_id_or_name() -> None:
    assert get_scenario("01") == get_scenario("new-appointment")
