"""jev-zero-to-agent setup doctor.

Checks, in order, that your one key can drive both brains:
  1. the slow brain (LLM) answers a chat completion,
  2. the slow brain can call a tool (needed by notebooks 03-12),
  3. the fast brain (Jev) answers Noul / Choice / Score questions.

    uv run python scripts/doctor.py
    JEV_BACKEND=adapter uv run python scripts/doctor.py   # no Jev access yet? test the fallback

Never prints your API key.
"""

import os
import sys
import time

try:
    from dotenv import find_dotenv, load_dotenv

    load_dotenv(find_dotenv(usecwd=True))
except Exception:
    pass

import httpx
import httpx2
from openai import OpenAI

BASE_URL = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
API_KEY = os.environ.get("OPENAI_API_KEY", "set-me")
MODEL = os.environ.get("MODEL", "openai/gpt-6-luna")
JEV_BACKEND = os.environ.get("JEV_BACKEND", "typesafe").strip().lower()
JEV_MODEL = os.environ.get("JEV_MODEL", "~typesafe/jev-latest")
JEV_BASE_URL = os.environ.get("TYPESAFE_BASE_URL", "https://openrouter.ai/api")
JEV_API_KEY = os.environ.get("TYPESAFE_API_KEY") or API_KEY
VERIFY_SSL = os.environ.get("VERIFY_SSL", "true").strip().lower() not in ("false", "0", "no")

OK, FAIL = "\033[32mOK  \033[0m", "\033[31mFAIL\033[0m"
failures = 0


def check(label, fn):
    global failures
    t0 = time.perf_counter()
    try:
        detail = fn()
        print(f"{OK} {label:<34} {1000 * (time.perf_counter() - t0):6.0f} ms  {detail}")
    except Exception as exc:  # noqa: BLE001 - a doctor reports everything
        failures += 1
        print(f"{FAIL} {label:<34} {type(exc).__name__}: {str(exc)[:160]}")


def masked(key):
    return "(missing)" if key in ("", "set-me") else f"{key[:8]}…{key[-4:]}"


print(f"LLM  endpoint {BASE_URL}  model {MODEL}")
print(f"Jev  backend  {JEV_BACKEND}  endpoint {JEV_BASE_URL}  model {JEV_MODEL}")
print(f"key  {masked(API_KEY)}   VERIFY_SSL={VERIFY_SSL}\n")

client = OpenAI(base_url=BASE_URL, api_key=API_KEY, http_client=httpx.Client(verify=VERIFY_SSL))


def llm_chat():
    r = client.chat.completions.create(
        model=MODEL, messages=[{"role": "user", "content": "Reply with the single word: pong"}]
    )
    return repr(r.choices[0].message.content.strip()[:40])


def llm_tools():
    tools = [{"type": "function", "function": {
        "name": "get_time", "description": "Current time in a city.",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]}}}]
    r = client.chat.completions.create(
        model=MODEL, tools=tools, messages=[{"role": "user", "content": "What time is it in Paris? Use the tool."}]
    )
    calls = r.choices[0].message.tool_calls or []
    if not calls:
        raise RuntimeError("model answered without calling the tool - pick a tool-capable MODEL")
    return f"{calls[0].function.name}({calls[0].function.arguments})"


def jev_call():
    if JEV_BACKEND == "adapter":
        from system_one_adapter import Choice, Noul, Score, SystemOneAdapterClient
        from system_one_adapter.providers.openai import OpenAIProvider

        jev = SystemOneAdapterClient(
            structured_outputs=True, llm_answer_mode="probabilities", normalize_probabilities=True,
            n_retry_malformed_structure=2,
            model=OpenAIProvider(MODEL, base_url=BASE_URL, api_key=API_KEY, api="chat_completions"),
        )
    else:
        from typesafe_sdk import Choice, Noul, Score, TypeSafeClient

        jev = TypeSafeClient(api_key=JEV_API_KEY, base_url=JEV_BASE_URL, model=JEV_MODEL,
                             http_client=httpx2.Client(verify=VERIFY_SSL))
    r = jev.system_one(
        "URGENT: your bank account is locked. Verify now at http://secure-bank-login.test/verify",
        {
            "is_scam": Noul(instructions="Is this SMS a phishing scam?"),
            "kind": Choice(instructions="What kind of message is this?",
                           criteria={"phishing": "credential theft", "marketing": "a promotion",
                                     "personal": "from a friend or family member"}),
            "pressure": Score(instructions="How much time pressure does it apply?",
                              criteria=["none", "some", "extreme"]),
        },
    )
    assert r.nouls["is_scam"].noul > 0.5, "expected is_scam > 0.5"
    assert r.choices["kind"].choice == "phishing", "expected kind == phishing"
    return (f"model={r.model}  is_scam={r.nouls['is_scam'].noul:.2f}  "
            f"kind={r.choices['kind'].choice}  pressure={r.scores['pressure'].score:.2f}")


check("LLM chat completion", llm_chat)
check("LLM tool calling", llm_tools)
check(f"Jev System One ({JEV_BACKEND})", jev_call)

if failures:
    print(f"\n{failures} check(s) failed. See README > Troubleshooting.")
    if JEV_BACKEND != "adapter":
        print("No Jev access yet? Set JEV_BACKEND=adapter in .env - same API, answered by your LLM.")
    sys.exit(1)
print("\nAll green. Next: uv run jupyter lab  ->  open 01_hello_jev.ipynb")
