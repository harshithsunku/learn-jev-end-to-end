# Configuration

All settings live in a `.env` file at the repository root. The notebooks, `app.py`, `jobs/` and
`scripts/` load it automatically. Start from the template:

```bash
cp .env.example .env
```

| Variable | Default | What it's for |
|---|---|---|
| `OPENAI_API_KEY` | (required) | your **OpenRouter key**; used for both the LLM and Jev |
| `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` | the LLM endpoint (any OpenAI-compatible server works) |
| `MODEL` | `openai/gpt-6-luna` | the slow brain; must support **tool calling** |
| `SMART_MODEL` | `openai/gpt-6-sol` | the "capable" tier for routing and benchmarks |
| `JEV_BACKEND` | `typesafe` | `adapter` answers Jev questions with `MODEL` ([details](../guides/no-jev-access.md)) |
| `JEV_MODEL` | `~typesafe/jev-latest` | the Jev model; the `~` alias always points to the latest release |
| `TYPESAFE_BASE_URL` | `https://openrouter.ai/api` | the Jev endpoint; use `https://api.typesafe.ai` with a direct TypeSafe key |
| `TYPESAFE_API_KEY` | = `OPENAI_API_KEY` | set only if Jev uses a different key |
| `IMAP_HOST`, `IMAP_USER`, `IMAP_PASSWORD` | unset | optional: triage your real mailbox (read-only; use an app password) |
| `VERIFY_SSL` | `true` | set `false` **only** behind a TLS-intercepting corporate proxy |

!!! warning "Keep your key secret"
    `.env` is git-ignored. Never paste your key into a notebook, an issue or a chat. If it leaks, delete it
    at [openrouter.ai/keys](https://openrouter.ai/keys) and create a new one.

## Check your settings

```bash
uv run python scripts/doctor.py                        # checks the LLM, tool calling and Jev
JEV_BACKEND=adapter uv run python scripts/doctor.py    # checks the no-Jev fallback
```
