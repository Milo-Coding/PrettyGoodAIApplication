"""Preview the approved 10-call suite without placing any calls."""

from __future__ import annotations

import argparse

from patient_bot.scenarios import SCENARIOS


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plan-only",
        action="store_true",
        help="Explicitly acknowledge that this command currently only previews the suite",
    )
    args = parser.parse_args()

    if not args.plan_only:
        parser.error(
            "Paid suite execution is not configured. Use --plan-only to preview the scenarios; "
            "a LiveKit/SIP runner and explicit approval are required before real calls."
        )
    for scenario in SCENARIOS:
        print(f"{scenario.scenario_id}. {scenario.name}: {scenario.objective}")
    return 0


if __name__ == "__main__":
    main()
