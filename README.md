# PrettyGoodAIApplication

My submission for the AI Engineering Challenge from Pretty Good AI.

## Current status

The repository scaffold is in place. Provider-specific LiveKit, STT, LLM, and TTS dependencies are intentionally pending account and provider selection. See [docs/plan.md](docs/plan.md) for the implementation sequence.

## Layout

- `src/patient_bot/`: application package and guarded call pipeline entrypoints
- `scripts/`: one-call, suite, and artifact-analysis commands
- `tests/`: configuration, scenario, patient-policy, and artifact-path tests
- `docs/`: architecture, scenarios, bug-report, Loom, and implementation plan
- `artifacts/`: reviewed recordings, transcripts, and metadata

## Local setup

1. Copy [.env.example](.env.example) to `.env` and fill in the LiveKit, provider, Twilio, and caller-number values for your local setup.
2. Install the project in a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .[dev]
```

3. Validate the environment and call guardrails without placing a paid call:

```powershell
python -m pytest
python scripts\run_call.py --list
python scripts\run_call.py 01 --validate-config
```

Do not run paid calls until provider accounts, credentials, caller number, and the fixed assessment destination have been verified. Never commit `.env` or provider secrets.
