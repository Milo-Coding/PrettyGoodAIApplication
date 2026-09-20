"""Inspect or validate one patient scenario before a paid test call."""

from __future__ import annotations

import argparse
import os

from patient_bot.calls import build_call_plan, run_call
from patient_bot.config import ConfigurationError, load_settings
from patient_bot.patient import build_patient_instructions
from patient_bot.scenarios import SCENARIOS, get_scenario


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", nargs="?", help="Scenario ID or name")
    parser.add_argument("--list", action="store_true", help="List available scenarios and exit")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the scenario policy only; does not read credentials or place a call",
    )
    parser.add_argument(
        "--validate-config",
        action="store_true",
        help="Validate local environment configuration without placing a call",
    )
    args = parser.parse_args()

    if args.list:
        for scenario in SCENARIOS:
            print(f"{scenario.scenario_id}: {scenario.name} — {scenario.objective}")
        return 0
    if not args.scenario:
        parser.error("scenario is required unless --list is used")

    scenario = get_scenario(args.scenario)
    if args.dry_run:
        print(f"Scenario: {scenario.scenario_id} / {scenario.name}")
        print(build_patient_instructions(scenario))
        return 0

    try:
        settings = load_settings(dict(os.environ))
    except ConfigurationError as error:
        parser.error(str(error))
    plan = build_call_plan(settings, scenario.name)
    if args.validate_config:
        print("Configuration is valid. Destination guard is active.")
        print(f"Scenario: {plan.scenario.name}; max duration: {plan.max_duration_seconds}s")
        return 0

    run_call(settings, scenario.name)
    return 0


if __name__ == "__main__":
    main()
