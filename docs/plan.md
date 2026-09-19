# AI Engineering Challenge Implementation Plan

## 1. Goal and success criteria

Build a Python voice caller that uses LiveKit Agents in **pipeline mode** to call only the assessment number `+1-805-439-8008`, behave like a realistic patient, and produce evidence that can be submitted in a public GitHub repository.

The finished submission must demonstrate:

- Coherent, natural conversations with sensible turn-taking and low enough latency.
- At least 10 meaningful calls, generally 1–3 minutes each, covering varied patient scenarios.
- Audio recordings in OGG or MP3 containing both sides of every call.
- Transcripts for every call.
- A concrete bug and quality report tied to call evidence and timestamps.
- Readable Python code, setup documentation, architecture rationale, and a `.env.example` with no secrets.
- Two public Loom videos: a project walkthrough and an AI-assisted debugging session, both recorded with the submitter visible on webcam.

The bot must use separate speech-to-text, LLM, and text-to-speech components. Realtime or speech-to-speech models and hosted voice-agent platforms are out of scope and must not be introduced.

## 2. Repository structure to create

```text
.
├── .env.example
├── .gitignore
├── README.md
├── pyproject.toml                  # Dependencies and project metadata
├── docs/
|   ├── plan.md
│   ├── architecture.md             # 1–2 paragraph architecture explanation
│   ├── test-scenarios.md           # Scenario catalog and expected observations
│   ├── bug-report.md               # Findings with severity and evidence
│   └── loom-outline.md             # Recording checklist and talking points
├── src/
│   └── patient_bot/
│       ├── __init__.py
│       ├── agent.py                # LiveKit worker and pipeline entrypoint
│       ├── config.py               # Validated environment/config loading
│       ├── scenarios.py            # Scenario definitions and state
│       ├── patient.py              # Patient behavior and conversation policy
│       ├── calls.py                # Outbound call orchestration and guardrails
│       ├── artifacts.py            # Call IDs, metadata, audio/transcript paths
│       └── analysis.py             # Transcript quality/bug analysis
├── scripts/
│   ├── run_call.py                 # Run one selected scenario
│   ├── run_suite.py                # Run the 10-call suite with confirmation
│   └── analyze_calls.py            # Generate/update findings from artifacts
├── tests/
│   ├── test_config.py
│   ├── test_scenarios.py
│   ├── test_patient.py
│   ├── test_artifacts.py
│   └── fixtures/
└── artifacts/
    ├── README.md                   # Naming and redaction policy
    ├── recordings/.gitkeep
    └── transcripts/.gitkeep
```

Generated recordings and transcripts should be committed only after reviewing them for secrets or sensitive data. Keep credentials, local logs, and temporary files ignored.

## 3. Implementation phases

### Phase 0: Confirm constraints and accounts

1. Read the product context at `pgai.us/athena` and create a test account as requested by the challenge.
2. Do **not** call the phone number shown in the account confirmation screen.
3. Confirm that every outbound call target is exactly `+1-805-439-8008`.
4. Choose providers for each pipeline stage. A practical initial choice is:
   - Telephony: LiveKit SIP/outbound calling or the supported LiveKit telephony integration.
   - STT: a streaming provider supported by LiveKit Agents.
   - LLM: a low-latency text model supported by LiveKit Agents.
   - TTS: a streaming provider supported by LiveKit Agents.
5. Create the required provider accounts and obtain credentials. The user must perform account creation, billing/phone verification, and secret entry locally.
6. Choose one caller phone number in E.164 format and use that same number for all 10 calls. Record it in a local environment variable and later in the submission form.
7. Verify current LiveKit Agents Python APIs and provider plugin versions before implementation so the code matches installed packages.

**User intervention required:** account creation, billing/phone verification, API key entry, selection of caller number, and permission to make paid test calls.

### Phase 1: Project setup and configuration

1. Add `pyproject.toml` with Python version constraints, LiveKit Agents, selected STT/LLM/TTS plugins, dotenv support, audio/transcript utilities, and test dependencies.
2. Add `.env.example` documenting every required variable without real values, including:
   - LiveKit URL, API key, and API secret.
   - STT, LLM, and TTS provider keys.
   - Outbound caller number.
   - Fixed assessment destination number.
   - Optional artifact directory and model/voice settings.
3. Implement `config.py` to load and validate configuration at startup.
4. Hard-code or strongly validate the assessment destination so a typo cannot route calls elsewhere. Refuse to run if the destination differs from `+1-805-439-8008`.
5. Update `.gitignore` for `.env`, caches, virtual environments, logs, temporary audio, and local run metadata.
6. Add a minimal README setup section: Python environment, dependency installation, `.env` creation, provider setup, and one-call smoke-test command.

**Validation:** configuration tests must reject missing credentials, invalid E.164 numbers, and any non-assessment destination.

### Phase 2: Build the LiveKit pipeline voice agent

1. Implement the LiveKit worker in `agent.py` using pipeline mode only.
2. Configure separate streaming components in this order:
   - Incoming phone audio -> speech-to-text.
   - Transcript plus conversation state -> LLM.
   - LLM response text -> text-to-speech.
   - TTS audio -> phone call.
3. Configure turn detection, interruption/barge-in behavior, endpointing, and silence limits appropriate for phone audio.
4. Add a concise system policy for the simulated patient:
   - Stay in character as the selected patient.
   - Use the scenario objective without reading a script mechanically.
   - Answer the agent's questions consistently from scenario state.
   - Ask natural follow-up questions and request clarification when needed.
   - Do not invent clinical facts beyond the scenario.
   - Do not disclose that the caller is an automated evaluator unless the test scenario requires it.
   - End politely after the objective is achieved or the conversation is clearly complete.
5. Keep responses short enough for a phone conversation and avoid multi-question monologues.
6. Add graceful handling for recognition failures, model/API errors, silence, hang-up, and transfer requests.
7. Add structured logging for call ID, scenario ID, turn timestamps, provider latency, termination reason, and artifact paths. Never log API keys.
8. Add an explicit maximum call duration and a clean hang-up path to prevent accidental runaway cost.

**Validation:** run a local agent startup/import check, then one paid smoke call only after the user confirms the destination, caller number, and budget.

### Phase 3: Scenario engine and realistic patient behavior

Create scenario objects with an ID, objective, patient profile, facts, constraints, likely turns, success criteria, and bug signals. Start with at least these 10 calls:

1. **New appointment:** request a routine appointment, provide name/date of birth when asked, and accept a reasonable weekday slot.
2. **Reschedule:** move an existing appointment, introduce a realistic availability constraint, and confirm the new time.
3. **Cancel:** cancel an appointment and check whether the agent explains consequences or follow-up options.
4. **Medication refill:** request a refill, provide medication and pharmacy details, and test whether the agent handles refill policy safely.
5. **Office hours:** ask about hours, including a weekend or holiday edge case, and check for unsupported appointment confirmation.
6. **Location:** ask for the office address, parking/accessibility information, and clarification if multiple locations are mentioned.
7. **Insurance:** ask whether a plan is accepted and observe whether the agent avoids unsupported certainty or offers verification.
8. **Ambiguous request:** begin with an unclear statement, then clarify after the agent asks a useful follow-up question.
9. **Interruption/barge-in:** interrupt a long response once, correct a detail, and verify that the agent recovers without repeating stale information.
10. **Unusual/compound request:** combine two needs or provide conflicting availability to test prioritization, confirmation, and graceful escalation.

For each scenario:

1. Define realistic patient identity and facts that remain internally consistent.
2. Define an objective and a stopping condition rather than a fixed word-for-word script.
3. Define expected safe behavior and potential bug signals.
4. Allow controlled variation in wording, pauses, confirmations, and follow-up questions.
5. Track whether the objective was achieved, partially achieved, or failed.
6. Ensure the patient actively steers back toward the scenario objective without sounding like a benchmark runner.

**User intervention required:** review the scenario facts and approve any patient details before paid calls, especially medication and insurance details.

### Phase 4: Recording, transcription, and artifact management

1. Record both directions of every call using the LiveKit/telephony recording mechanism supported by the selected integration.
2. Store recordings as OGG or MP3 with stable names such as `call-01-office-hours.mp3`.
3. Preserve a call metadata JSON file containing scenario ID, UTC start/end times, caller/destination numbers with appropriate privacy handling, provider/model versions, outcome, and recording/transcript paths.
4. Capture the conversation transcript with speaker labels, timestamps, and turn boundaries. Include both patient and agent sides.
5. If the telephony recording does not provide a usable transcript, transcribe the final mixed recording with a separate batch STT step and clearly document that choice.
6. Review each recording manually for intelligibility, missing sides, clipping, long dead air, accidental hangs-up, and whether it lasts long enough to be meaningful.
7. Keep the artifacts directory reproducible and easy for reviewers to browse. Add an index mapping call number to scenario, recording, transcript, and outcome.
8. Redact any unnecessary personal data before committing artifacts. Do not commit provider credentials or unrelated patient data.

**Acceptance gate:** do not count a call toward the required 10 until it has both sides of the audio and a readable transcript.

### Phase 5: Bug and quality analysis

1. Implement `analysis.py` and `scripts/analyze_calls.py` to help compare each transcript against scenario expectations.
2. Evaluate each call for:
   - Factual or scheduling errors.
   - Unsafe medication/refill handling.
   - Unsupported claims about insurance, office hours, location, or availability.
   - Failure to confirm identity or critical details when appropriate.
   - Failure to clarify ambiguity.
   - Poor interruption recovery or stale-state responses.
   - Repeated questions, hallucinated appointments, unexplained refusals, or premature hang-up.
   - Latency, awkward pauses, audio glitches, and turn-taking problems.
3. Treat automated analysis as triage only. Manually listen to the relevant audio and verify every reported issue against the transcript and timestamp.
4. Write `docs/bug-report.md` with one entry per confirmed issue using:
   - Title.
   - Severity: Critical/High/Medium/Low.
   - Scenario and call ID.
   - Recording and transcript links.
   - Timestamp and exact evidence.
   - Why the behavior is harmful or lowers quality.
   - Expected behavior and a suggested fix.
   - Confidence and whether the issue reproduced.
5. Also report important quality observations even when no definite product bug is proven, keeping them separate from confirmed bugs.

### Phase 6: Iteration and quality tuning

1. Run one or two smoke calls before the full suite.
2. Listen for latency, unnatural voice, overlong responses, missed interruptions, incorrect scenario facts, and premature endings.
3. Adjust endpointing, system instructions, model/voice settings, or scenario policy based on observed evidence.
4. Re-run the affected scenario after each meaningful change and document what changed and why.
5. Keep a short iteration log in `docs/architecture.md` or `docs/test-scenarios.md` showing evidence of improvement.
6. Avoid tuning the bot to hide product bugs; the patient should become more natural and reliable while preserving the test objective.

**User intervention required:** listen to smoke recordings and approve further paid calls before running the full 10-call suite.

### Phase 7: Full test suite and submission evidence

1. Run all 10 scenarios, using the same caller number and fixed assessment destination.
2. Prefer sequential calls so artifacts, provider usage, and failures are easy to attribute.
3. After every call, verify completion, recording, transcript, and metadata before starting the next one.
4. Re-run only failed or technically invalid calls; do not silently replace a valid negative test result.
5. Build an artifact index and final call summary with scenario, duration, outcome, and bug references.
6. Confirm the repository contains at least 10 qualifying recordings in OGG/MP3 and 10 matching transcripts with both speakers.
7. Run tests, formatting, linting/type checks if configured, and a clean setup/import check from a fresh environment.
8. Search the repository for secrets and confirm `.env` and provider credentials are ignored.

**User intervention required:** approve and monitor the 10 paid calls, retain receipts for reimbursement, and manually confirm that recordings/transcripts are suitable for public submission.

### Phase 8: Documentation and Loom videos

1. Complete `docs/architecture.md` in 1–2 focused paragraphs covering:
   - Why pipeline mode satisfies the requirement.
   - STT, LLM, and TTS provider choices and tradeoffs.
   - Phone network/LiveKit connection.
   - Turn detection, interruptions, and latency decisions.
   - Recording/transcription and analysis flow.
   - What was changed after hearing early calls.
2. Complete README instructions so setup is clear and the normal run is one command after setup.
3. Add `docs/loom-outline.md` with two recording scripts:
   - Project walkthrough, maximum 3 minutes: show structure, configuration without exposing secrets, pipeline, scenario design, artifacts, and one or two findings.
   - AI debugging video: show a real failing behavior, the prompt used to investigate, the iterative code change, the focused validation, and the resulting improvement.
4. Record both videos in the submitter's own voice with webcam visible, then make both Loom links public.
5. Add the final public Loom links to README or a submission section without embedding private credentials.

**User intervention required:** record and publish both Loom videos; the assistant can prepare scripts, demo order, and code changes but cannot supply the user's webcam/voice or create the final public submission on the user's behalf.

### Phase 9: Final submission checklist

Before submitting, verify every item below:

- [X] Public GitHub repository created.
- [ ] Python implementation uses LiveKit Agents pipeline mode.
- [ ] Separate STT, LLM, and TTS components are visible in code and documentation.
- [ ] No realtime/speech-to-speech model or hosted voice-agent platform is used.
- [ ] Destination is only `+1-805-439-8008`.
- [ ] Exactly one caller number was used for all test calls and is recorded in E.164 format.
- [ ] At least 10 calls completed, with varied scenarios and meaningful conversations.
- [ ] Every counted call has both-sided OGG/MP3 audio and a matching transcript.
- [ ] Bug report points to exact calls, files, and timestamps.
- [ ] README has setup, environment, run, artifact, and troubleshooting instructions.
- [ ] Architecture document is complete and explains decisions and tradeoffs.
- [ ] `.env.example` is present and `.env`/secrets are absent from Git.
- [ ] Tests and project checks pass from a clean environment.
- [ ] Recordings and transcripts have been manually reviewed and are appropriate to publish.
- [ ] Two public Loom videos exist, with webcam and voice as required.
- [ ] Receipts are retained for reimbursement up to the stated limit.
- [ ] Submission form includes the public repository, both Loom links, and the correct single caller number.

## 4. Recommended execution order

1. Confirm providers, accounts, caller number, and budget.
2. Create project metadata, configuration, and dependency files.
3. Implement and validate the pipeline agent with a strict destination guard.
4. Implement scenarios and one-call artifact capture.
5. Make one short smoke call and inspect the complete audio/transcript path.
6. Tune conversation quality and interruption handling.
7. Run and review all 10 scenarios.
8. Analyze findings and write the bug report.
9. Finish documentation, tests, README, and artifact index.
10. Record Loom videos, perform the final checklist, and submit.

## 5. Definition of done

The project is done when a reviewer can clone the public repository, follow the README, understand the architecture without reading every file, inspect 10 complete call artifacts, trace each bug report to evidence, and see proof that the caller was iterated based on real audio results. The only steps intentionally left to the user are provider/account actions, secret entry, approval and monitoring of paid calls, webcam/voice recording, and the final public submission form.
