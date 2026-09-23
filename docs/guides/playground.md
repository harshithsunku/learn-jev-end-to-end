# The Jev Playground app

`app.py` puts the use cases behind a click-through web UI built with [Gradio](https://gradio.app). It's one
self-contained file that you can read and copy.

```bash
uv sync --extra ui
uv run --extra ui python app.py
```

Then open <http://127.0.0.1:7860>.

| Tab | What you can do |
|---|---|
| **Playground** | Type any text, choose `Noul`, `Choice` or `Score`, write a question and see Jev's answer with probabilities |
| **Email triage** | Paste an email and get its category, whether it needs a reply, its urgency, and optionally an LLM draft |
| **SMS scam shield** | Paste a text message and get a risk score, a verdict and a plain-words explanation |
| **Code vuln hunter** | Paste Python code and see every function checked for vulnerabilities (parsed, never executed) |
| **Guarded agent** | Ask a shell agent to do something and watch the guard allow, ask or block each command (dry-run) |
| **Jev vs LLM race** | Ask the same yes/no question to both brains and compare the latency |

!!! note "Safe to play with"
    Every tool in the app is read-only or a dry-run. The guarded agent's shell never executes anything.
