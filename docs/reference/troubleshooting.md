# Troubleshooting

Run `uv run python scripts/doctor.py` first. It tells you which part is failing.

| Symptom | Cause | Fix |
|---|---|---|
| `No key yet: paste your OpenRouter key...` | `.env` still has the placeholder | paste your real key into `OPENAI_API_KEY` |
| `401 User not found` on every check | the key is wrong or deleted | create a new key at [openrouter.ai/keys](https://openrouter.ai/keys) |
| only the **Jev** check fails with `401` / `403` (JSON body) | your key has no Jev access yet | set `JEV_BACKEND=adapter` ([details](../guides/no-jev-access.md)) |
| `403` with a **Cloudflare HTML page** | the gateway's firewall rejected a payload that looked like a live exploit (for example, a `curl ... \| sh` command plus a key-theft command) | rephrase the data; guards in this course fail closed on this error |
| `429` or `529` | rate limited or overloaded | the SDK retries with backoff; lower `workers` in `jev_map(...)` |
| the model answers without calling tools | `MODEL` doesn't support tool calling | pick a tool-capable model; the doctor checks this |
| an error mentioning `temperature` | some current models reject it | the course never sends `temperature`; remove it from your own code |
| SSL certificate errors | a corporate proxy intercepts HTTPS | `VERIFY_SSL=false` (trusted networks only) |
| a notebook's `assert` fails | accuracy dropped below the notebook's threshold | results vary a little between runs; re-run, and if it keeps failing, look at the misclassified rows it prints |
| `ModuleNotFoundError: gradio` | the UI extra isn't installed | `uv sync --extra ui` |
