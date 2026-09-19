# Test Scenarios

Scenario definitions will be implemented in `src/patient_bot/scenarios.py` and expanded with observed outcomes after smoke testing.

| ID  | Scenario          | Objective                                  | Status  |
| --- | ----------------- | ------------------------------------------ | ------- |
| 01  | New appointment   | Schedule a routine weekday appointment     | Planned |
| 02  | Reschedule        | Move an existing appointment               | Planned |
| 03  | Cancel            | Cancel an appointment safely               | Planned |
| 04  | Medication refill | Request a refill with pharmacy details     | Planned |
| 05  | Office hours      | Test weekend and holiday handling          | Planned |
| 06  | Location          | Ask for address and access information     | Planned |
| 07  | Insurance         | Test coverage uncertainty and verification | Planned |
| 08  | Ambiguous request | Evaluate clarification behavior            | Planned |
| 09  | Interruption      | Test barge-in and recovery                 | Planned |
| 10  | Compound request  | Test conflicting or multiple needs         | Planned |
