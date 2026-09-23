# No Jev access yet?

Jev is new, and some keys may not have access yet. You can still take the whole course.

## Use the adapter backend

Add one line to `.env`:

```bash title=".env"
JEV_BACKEND=adapter
```

Now every `ask_jev(...)` call is answered by **your LLM** (`MODEL`) through TypeSafe's open-source
[`system-one-adapter`](https://github.com/typesafe-ai/system-one-adapter-python). It exposes the same
`system_one()` API and returns the same response types, so **no notebook code changes**.

## What works

We ran every notebook with `JEV_BACKEND=adapter`:

| | With the adapter |
|---|---|
| Notebooks 01 and 03-12 | :material-check: run, and their built-in accuracy checks pass |
| `app.py` and `jobs/email_triage.py` | :material-check: run |
| Notebook 02 (the benchmark) | :material-close: needs real Jev, because it benchmarks Jev itself; it stops with a clear message |

## What's different

- **Slower.** Each decision takes an LLM round-trip (~2-3 s instead of ~0.4 s).
- **More expensive.** You pay LLM prices, including output tokens.
- **The race tab says so.** In `app.py`, the "Jev vs LLM race" tells you the "Jev" side is really your LLM.

When you get Jev access, switch back with `JEV_BACKEND=typesafe` (or delete the line). Nothing else changes.
