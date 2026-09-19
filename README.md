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

## Local checks

Create a virtual environment, install the development dependencies, and run:

```powershell
python -m pytest
```

Do not run paid calls until provider accounts, credentials, caller number, and the fixed assessment destination have been verified. Never commit `.env` or provider secrets.
