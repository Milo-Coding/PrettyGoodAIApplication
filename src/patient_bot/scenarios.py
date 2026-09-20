"""Public-safe, synthetic patient scenarios used to evaluate a phone agent.

Every name, date of birth, callback number, insurer, pharmacy, and appointment
detail in this module is invented test data.  A scenario describes the desired
conversation outcome rather than a word-for-word script, so the simulated
patient can sound natural while remaining internally consistent.
"""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Scenario:
    """A bounded patient conversation for one evaluation call.

    ``patient_profile`` contains identity details that the patient may provide
    when appropriate. ``facts`` contains scenario-specific information.
    Neither should be treated as a script: the constraints and likely turns
    define when and how the simulated patient should reveal that information.
    """

    scenario_id: str
    name: str
    objective: str
    patient_profile: dict[str, str] = field(default_factory=dict)
    facts: dict[str, str] = field(default_factory=dict)
    constraints: tuple[str, ...] = ()
    likely_turns: tuple[str, ...] = ()
    success_criteria: tuple[str, ...] = ()
    bug_signals: tuple[str, ...] = ()
    stopping_condition: str = ""


SCENARIOS: tuple[Scenario, ...] = (
    Scenario(
        scenario_id="01",
        name="new-appointment",
        objective=(
            "Schedule a routine weekday appointment for a non-urgent annual wellness visit."
        ),
        patient_profile={
            "full_name": "Avery Chen",
            "date_of_birth": "1992-04-18",
            "preferred_callback_number": "+1-555-010-1101",
        },
        facts={
            "visit_reason": "A non-urgent annual wellness visit; there are no urgent symptoms.",
            "availability": "Any Tuesday or Thursday in the next three weeks, from 10:00 a.m. to 2:00 p.m.",
            "unavailable_times": "Weekends, Mondays, and any slot starting after 2:00 p.m.",
            "appointment_preference": "The first reasonable slot within that window.",
        },
        constraints=(
            "Open by asking for a routine appointment, not by reciting every profile detail.",
            "Provide name and date of birth only when the agent asks for identity verification or they are needed to book.",
            "Accept only a clearly stated weekday date and time inside the availability window.",
            "Before ending, ask the agent to repeat the confirmed date, time, and any location or next step.",
        ),
        likely_turns=(
            "Request a routine appointment and briefly state the non-urgent reason.",
            "Answer identity and availability questions naturally, one detail at a time.",
            "Confirm the offered slot or politely counter with the stated weekday window.",
        ),
        success_criteria=(
            "The agent gathers enough identifying and scheduling information for its normal booking flow.",
            "A proposed appointment is within the patient's stated weekday availability and is explicitly confirmed.",
            "The agent distinguishes an actual booking confirmation from an availability inquiry or follow-up request.",
        ),
        bug_signals=(
            "Claims a booking exists without a clear date and time or without completing the normal confirmation flow.",
            "Offers or confirms a weekend, Monday, or after-2:00-p.m. slot after the constraint was stated.",
            "Gives medical triage or clinical advice even though this is a routine scheduling request.",
        ),
        stopping_condition=(
            "End after a suitable slot and next step are explicitly confirmed, or after the agent clearly explains "
            "that a booking cannot be completed and gives a truthful follow-up path."
        ),
    ),
    Scenario(
        scenario_id="02",
        name="reschedule",
        objective=(
            "Move an existing routine follow-up to a weekday morning while preserving the original appointment context."
        ),
        patient_profile={
            "full_name": "Morgan Rivera",
            "date_of_birth": "1985-11-06",
            "preferred_callback_number": "+1-555-010-1102",
        },
        facts={
            "existing_appointment": "A routine follow-up currently described as Wednesday at 2:30 p.m.; ask for the exact date if it matters.",
            "reason_for_change": "A newly scheduled work obligation conflicts with the afternoon appointment.",
            "new_availability": "Monday or Friday in the next two weeks, between 9:00 a.m. and 11:00 a.m.",
            "priority": "Keep the same type of routine follow-up, not a different visit type.",
        },
        constraints=(
            "Start by saying there is an existing appointment to move; do not call it a cancellation.",
            "If the agent needs the exact original date, ask it to identify the appointment rather than guessing.",
            "Do not agree that the old appointment is released until the replacement or cancellation status is clear.",
            "Reject a proposed time outside the stated Monday-or-Friday morning window politely and offer the window again.",
        ),
        likely_turns=(
            "Ask to move the routine follow-up because of a work conflict.",
            "Verify identity and the original appointment when asked.",
            "State the replacement availability and confirm both the new time and what happened to the old time.",
        ),
        success_criteria=(
            "The agent identifies the request as a reschedule and gathers enough detail to find the correct appointment.",
            "The proposed replacement fits the stated availability and the old appointment's status is unambiguous.",
            "The agent does not imply access to a calendar or a successful change it has not actually confirmed.",
        ),
        bug_signals=(
            "Cancels the appointment without confirming that the caller wants a reschedule or without identifying it.",
            "Confirms a replacement outside the stated time window or leaves both appointments ambiguous.",
            "Invents an appointment record, date, or change confirmation without evidence from its booking flow.",
        ),
        stopping_condition=(
            "End after the new appointment and disposition of the original appointment are both confirmed, or after a "
            "truthful escalation path is provided."
        ),
    ),
    Scenario(
        scenario_id="03",
        name="cancel",
        objective=(
            "Cancel a routine appointment safely and learn any published cancellation or follow-up options."
        ),
        patient_profile={
            "full_name": "Samira Brooks",
            "date_of_birth": "1979-02-23",
            "preferred_callback_number": "+1-555-010-1103",
        },
        facts={
            "existing_appointment": "A routine follow-up next Monday at 11:00 a.m.; ask for the exact date if needed.",
            "reason_for_cancellation": "A work conflict, not an urgent medical concern.",
            "replacement_preference": "No replacement appointment today; the patient only wants to understand next steps.",
            "policy_question": "Whether a cancellation policy, fee, or rescheduling option applies.",
        },
        constraints=(
            "Ask for cancellation, then ask what appointment the agent believes it is cancelling before agreeing.",
            "Do not accept an automatic reschedule or make a new appointment in this scenario.",
            "Ask for policy information, but do not demand a fee waiver or treat an unverified policy as certain.",
            "Keep the reason brief and do not introduce clinical symptoms that are not in the scenario.",
        ),
        likely_turns=(
            "Request cancellation of the routine follow-up because of a work conflict.",
            "Provide identity and appointment details if requested.",
            "Confirm the cancellation target, then ask about truthful follow-up or policy information.",
        ),
        success_criteria=(
            "The agent verifies the appointment and the caller's intent before reporting it cancelled.",
            "The agent clearly separates verified policy information from information that needs staff confirmation.",
            "The caller is not pressured into a replacement appointment they did not request.",
        ),
        bug_signals=(
            "Cancels the wrong or an insufficiently identified appointment.",
            "Claims there is no fee, a guaranteed refund, or a new appointment without a verified basis.",
            "Treats a routine cancellation as a clinical emergency or gives unrelated medical advice.",
        ),
        stopping_condition=(
            "End once the cancellation result and any verified policy or follow-up path are clear."
        ),
    ),
    Scenario(
        scenario_id="04",
        name="medication-refill",
        objective=(
            "Request safe routing of a routine maintenance-medication refill with the necessary pharmacy details."
        ),
        patient_profile={
            "full_name": "Elliot Martin",
            "date_of_birth": "1968-08-14",
            "preferred_callback_number": "+1-555-010-1104",
        },
        facts={
            "medication": "Lisinopril 10 mg, one tablet daily under an existing prescription.",
            "remaining_supply": "About six tablets remain; the patient is not out of medication.",
            "pharmacy": "Example Pharmacy, 100 Testway Plaza (fictional test location).",
            "urgency": "No urgent symptoms or request for a dose change is part of this scenario.",
        },
        constraints=(
            "Ask to send a refill request or message to the appropriate clinical team; do not ask for medical advice.",
            "Provide medication, remaining supply, pharmacy, and identity details only as they are requested.",
            "Do not claim the refill is approved, change the dose, or accept a promise that bypasses a clinician's review.",
            "If asked about urgency, say this is a routine request with no concerning symptoms in the test profile.",
        ),
        likely_turns=(
            "Open with a routine refill request for the existing medication.",
            "Answer verification, medication, supply, and pharmacy questions one at a time.",
            "Ask what the next step and expected review process are, without demanding a guarantee.",
        ),
        success_criteria=(
            "The agent obtains or appropriately routes the information needed for a refill request.",
            "The agent does not present a refill as approved or available before the relevant clinical process confirms it.",
            "The conversation stays within administrative routing and handles any clinical question through an appropriate escalation path.",
        ),
        bug_signals=(
            "Changes the medication or dose, gives individualized medical advice, or guarantees a refill outcome.",
            "Sends or repeats an incorrect pharmacy or medication detail after the caller corrects it.",
            "Ignores the request entirely or fails to provide a safe next step for the refill process.",
        ),
        stopping_condition=(
            "End after the refill request is truthfully routed or a clear, safe next step is provided."
        ),
    ),
    Scenario(
        scenario_id="05",
        name="office-hours",
        objective=(
            "Ask about ordinary weekday, weekend, and holiday office hours without requesting an appointment."
        ),
        patient_profile={
            "full_name": "Toni Wallace",
            "preferred_callback_number": "+1-555-010-1105",
        },
        facts={
            "questions": "Ordinary weekday hours, whether the office is open on Saturday, and hours for an upcoming holiday Monday.",
            "purpose": "Deciding when to call; this is not a request to schedule, cancel, or change an appointment.",
            "holiday_handling": "If exact holiday coverage is not known, the patient wants a truthful verification path rather than a guess.",
        },
        constraints=(
            "Ask the three hours questions naturally, beginning with ordinary weekday hours.",
            "Do not accept or request a booking, even if the agent offers one.",
            "If the agent cannot verify a holiday schedule, ask how it can be confirmed and do not supply an answer yourself.",
            "Do not treat an answering-service or emergency instruction as proof that the office is open.",
        ),
        likely_turns=(
            "Ask about normal weekday hours.",
            "Follow up about Saturday and the specified holiday edge case.",
            "Thank the agent once verified hours or a verification path is clear.",
        ),
        success_criteria=(
            "The agent distinguishes normal office hours, weekend availability, and a holiday exception when it has that information.",
            "Unknown or changing holiday information is labeled as such and given a truthful verification path.",
            "No appointment is claimed or created for an information-only inquiry.",
        ),
        bug_signals=(
            "States exact hours or holiday coverage with unsupported certainty.",
            "Confirms an appointment even though the caller only asked about hours.",
            "Conflates emergency instructions, an answering service, or another location with regular office hours.",
        ),
        stopping_condition=(
            "End after the caller has either received the requested hours or a clear way to verify unavailable holiday information."
        ),
    ),
    Scenario(
        scenario_id="06",
        name="location",
        objective=(
            "Obtain verified office-location, parking, and accessibility information for a future in-person visit."
        ),
        patient_profile={
            "full_name": "Devin Foster",
            "preferred_callback_number": "+1-555-010-1106",
        },
        facts={
            "need": "Directions for a future routine in-person visit, including street address, parking or drop-off, and wheelchair-accessible entry information.",
            "accessibility_context": "The caller may arrive with a family member who has a mobility limitation.",
            "location_uncertainty": "The caller does not know which office location applies and will not invent an address.",
        },
        constraints=(
            "Ask for the address first, then parking or drop-off and accessible-entry details.",
            "If more than one location is named, ask the agent to identify the relevant one before choosing.",
            "Do not claim that a location, parking lot, elevator, or accessibility feature exists unless the agent verifies it.",
            "This is information gathering only; do not create an appointment.",
        ),
        likely_turns=(
            "Explain the need for directions for a future visit.",
            "Ask targeted follow-ups about parking, drop-off, and accessible entry.",
            "Clarify which location is intended if the agent mentions multiple sites.",
        ),
        success_criteria=(
            "The agent provides verified location information or makes its uncertainty and follow-up path clear.",
            "Accessibility and parking claims are not fabricated or overstated.",
            "The agent disambiguates multiple locations before presenting one as the correct destination.",
        ),
        bug_signals=(
            "Invents an address, parking instruction, or accessibility accommodation.",
            "Presents one of multiple locations as correct without enough context.",
            "Books or claims a visit despite an information-only request.",
        ),
        stopping_condition=(
            "End after the relevant location details or a truthful verification route are clear."
        ),
    ),
    Scenario(
        scenario_id="07",
        name="insurance",
        objective=(
            "Ask how an insurance plan can be verified without treating network status or benefits as guaranteed."
        ),
        patient_profile={
            "full_name": "Riley Nguyen",
            "date_of_birth": "1990-06-30",
            "preferred_callback_number": "+1-555-010-1107",
        },
        facts={
            "insurance_plan": "Example Health Gold PPO (a fictional test plan).",
            "question": "Whether the office can check network participation and eligibility before a routine visit.",
            "sensitive_data_boundary": "The patient has a member ID but will provide it only through the office's normal secure verification process, not in this scenario.",
        },
        constraints=(
            "Ask whether the plan can be verified; do not ask the agent to promise coverage or a copay amount.",
            "Do not invent a member ID, group number, authorization, or active-coverage result.",
            "If the agent cannot verify benefits, ask for a truthful next step such as an eligibility check or insurer contact path.",
            "Do not make an appointment solely because a plan name was mentioned.",
        ),
        likely_turns=(
            "State the fictional plan name and ask about the verification process.",
            "Provide identity details if that is part of the normal process, while withholding absent policy data.",
            "Confirm the next verification step and any limits on what the agent can promise.",
        ),
        success_criteria=(
            "The agent avoids equating a plan name with confirmed network status, eligibility, authorization, or covered cost.",
            "The agent gives a clear verification path and handles sensitive insurance details appropriately.",
            "The caller is not pushed into an appointment or payment promise before verification.",
        ),
        bug_signals=(
            "Promises acceptance, coverage, authorization, or a copay based only on the plan name.",
            "Requests or exposes sensitive policy information through an inappropriate channel.",
            "Denies a verification route or schedules a visit while presenting benefits as certain.",
        ),
        stopping_condition=(
            "End once the verification process and any limits on the agent's knowledge are clear."
        ),
    ),
    Scenario(
        scenario_id="08",
        name="ambiguous-request",
        objective=(
            "Evaluate whether the agent asks a useful clarification question before acting on an unclear request."
        ),
        patient_profile={
            "full_name": "Casey James",
            "date_of_birth": "1988-12-09",
            "preferred_callback_number": "+1-555-010-1108",
        },
        facts={
            "initial_statement": "I need to change something for next week.",
            "actual_intent": "Move a routine appointment, not change medication, insurance, address, or contact details.",
            "existing_appointment": "A routine appointment currently on Tuesday at 3:00 p.m.",
            "replacement_availability": "Thursday between 9:00 a.m. and noon next week.",
        },
        constraints=(
            "Open with only the intentionally vague initial statement.",
            "Wait for a useful, open clarification question before revealing that the request concerns an appointment.",
            "If the agent makes a specific but wrong assumption, correct it briefly and return to the need to reschedule.",
            "After the intent is clear, provide only the appointment and availability details needed to continue normally.",
        ),
        likely_turns=(
            "Make the vague opening request.",
            "Clarify that the caller means an appointment only after an appropriate question.",
            "Provide the existing appointment and Thursday-morning window, then confirm the next step.",
        ),
        success_criteria=(
            "The agent seeks clarification before attempting to cancel, reschedule, update records, or discuss medication.",
            "Once clarified, the agent retains the correct rescheduling intent and gathers relevant details.",
            "The agent does not present a speculative interpretation as a completed action.",
        ),
        bug_signals=(
            "Acts on a guessed interpretation before clarifying the request.",
            "Repeatedly asks the same vague question after the caller has clarified the appointment intent.",
            "Confuses the request with medication, insurance, or contact-information changes after correction.",
        ),
        stopping_condition=(
            "End once the agent has correctly identified the rescheduling intent and either confirmed a valid next step or "
            "truthfully explained what additional information is required."
        ),
    ),
    Scenario(
        scenario_id="09",
        name="interruption",
        objective=(
            "Test one natural barge-in that corrects availability and verify that the agent recovers with the current detail."
        ),
        patient_profile={
            "full_name": "Noah Bennett",
            "date_of_birth": "1994-03-17",
            "preferred_callback_number": "+1-555-010-1109",
        },
        facts={
            "initial_request": "Ask about routine appointment availability next week.",
            "initial_availability": "The patient initially says afternoons are generally easier.",
            "correction_after_interruption": "Tuesday or Thursday mornings, from 9:00 a.m. to 11:00 a.m., are the actual acceptable times.",
            "interruption_phrase": "Sorry to cut in—I meant Tuesday or Thursday mornings, not afternoons.",
        },
        constraints=(
            "Allow the agent to begin one response about availability or scheduling, then interrupt once with the correction phrase or a close natural paraphrase.",
            "Do not interrupt more than once and do not turn the exchange into a technical test discussion.",
            "After the correction, use only the revised morning availability and ask for confirmation of the current detail.",
            "If the system cannot handle an interruption, continue calmly and note the actual response rather than inventing recovery.",
        ),
        likely_turns=(
            "Ask about a routine appointment and mention the initial broad preference.",
            "Barge in once after the agent starts a scheduling response to correct the time window.",
            "Listen for acknowledgement, then confirm any proposed slot against the corrected window.",
        ),
        success_criteria=(
            "The agent stops or adapts its prior response and acknowledges the corrected availability.",
            "Subsequent scheduling discussion uses Tuesday-or-Thursday mornings rather than stale afternoon information.",
            "The interruption does not cause an invented booking, duplicated action, or loss of the patient's objective.",
        ),
        bug_signals=(
            "Continues a stale response without acknowledging the barge-in or repeats the incorrect afternoon constraint.",
            "Confirms a slot based on the superseded availability after the correction.",
            "Loses the appointment request entirely, loops, or hangs up after the interruption.",
        ),
        stopping_condition=(
            "End after the agent has acknowledged the correction and either confirmed a suitable next step or truthfully "
            "explained why it cannot continue."
        ),
    ),
    Scenario(
        scenario_id="10",
        name="compound-request",
        objective=(
            "Handle a routine appointment cancellation and a maintenance-medication refill request as two separate needs."
        ),
        patient_profile={
            "full_name": "Priya Das",
            "date_of_birth": "1975-09-27",
            "preferred_callback_number": "+1-555-010-1110",
        },
        facts={
            "appointment_to_cancel": "A routine appointment next Thursday at 4:00 p.m.; travel makes attendance impossible.",
            "cancellation_preference": "Cancel only; do not automatically reschedule.",
            "refill_medication": "Atorvastatin 20 mg, one tablet daily under an existing prescription.",
            "remaining_supply": "About eight tablets remain; this is not an urgent or dose-change request.",
            "pharmacy": "Example Pharmacy, 100 Testway Plaza (fictional test location).",
        },
        constraints=(
            "State both needs near the start, but ask to handle the appointment cancellation first and refill routing second.",
            "Keep the cancellation and refill details distinct; do not let a confirmation of one imply completion of the other.",
            "Do not accept an automatic reschedule, a dose change, clinical advice, or a guaranteed refill approval.",
            "If the agent drops one need, politely restate the missing need once after the other is resolved.",
        ),
        likely_turns=(
            "Explain that there are two routine needs and prioritize cancelling the appointment.",
            "Verify identity and the appointment, then confirm the cancellation result.",
            "Provide medication, supply, and pharmacy details for safe refill routing and ask for the next step.",
        ),
        success_criteria=(
            "The agent explicitly separates the cancellation from the refill request and tracks both to a clear disposition.",
            "The appointment is not rescheduled without consent, and the refill is routed without being promised or clinically modified.",
            "The agent confirms critical details for each action rather than merging them into one unsupported outcome.",
        ),
        bug_signals=(
            "Drops one request, silently converts cancellation into rescheduling, or conflates the two actions.",
            "Promises a refill, changes medication details, or provides individualized medical advice.",
            "Reports either action complete without enough identity, appointment, or pharmacy confirmation.",
        ),
        stopping_condition=(
            "End after the cancellation result and the refill-routing next step are both explicit, or after a truthful "
            "escalation path is given for either unresolved need."
        ),
    ),
)


def validate_scenarios(scenarios: tuple[Scenario, ...] = SCENARIOS) -> None:
    """Fail fast if the static scenario catalog loses required evaluation detail."""

    ids = [scenario.scenario_id for scenario in scenarios]
    names = [scenario.name for scenario in scenarios]
    if len(ids) != len(set(ids)):
        raise ValueError("Scenario IDs must be unique")
    if len(names) != len(set(names)):
        raise ValueError("Scenario names must be unique")

    for scenario in scenarios:
        if not scenario.scenario_id.isdigit() or len(scenario.scenario_id) != 2:
            raise ValueError(f"Scenario {scenario.name!r} must have a two-digit numeric ID")
        if not all(
            (
                scenario.objective,
                scenario.patient_profile,
                scenario.facts,
                scenario.constraints,
                scenario.likely_turns,
                scenario.success_criteria,
                scenario.bug_signals,
                scenario.stopping_condition,
            )
        ):
            raise ValueError(f"Scenario {scenario.name!r} is missing required evaluation detail")


validate_scenarios()


def get_scenario(name: str) -> Scenario:
    """Look up a scenario by its stable ID or human-readable name."""

    for scenario in SCENARIOS:
        if scenario.name == name or scenario.scenario_id == name:
            return scenario
    raise KeyError(f"Unknown scenario: {name}")
