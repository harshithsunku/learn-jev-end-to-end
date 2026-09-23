# Cheat sheet

## Set up a client

=== "Through OpenRouter (one key)"

    ```python
    from typesafe_sdk import TypeSafeClient, Noul, Choice, Score

    jev = TypeSafeClient(api_key="sk-or-v1-...",
                         base_url="https://openrouter.ai/api",   # SDK appends /v1/systemone
                         model="~typesafe/jev-latest")
    ```

=== "Direct TypeSafe key"

    ```python
    from typesafe_sdk import TypeSafeClient

    jev = TypeSafeClient()   # reads TYPESAFE_API_KEY; defaults to https://api.typesafe.ai and jev-latest
    ```

=== "No Jev access (adapter)"

    ```python
    from system_one_adapter import SystemOneAdapterClient, Noul, Choice, Score
    from system_one_adapter.providers.openai import OpenAIProvider

    jev = SystemOneAdapterClient(
        structured_outputs=True, llm_answer_mode="probabilities", normalize_probabilities=True,
        model=OpenAIProvider("openai/gpt-6-luna", base_url="https://openrouter.ai/api/v1",
                             api_key="sk-or-v1-...", api="chat_completions"))
    ```

## Ask questions

```python
r = jev.system_one(
    state,                                   # str, dict or list: the thing being judged
    {
        "q1": Noul(instructions="...",
                   criteria={"true": "what counts as yes", "false": "what counts as no"}),   # criteria optional
        "q2": Choice(instructions="...",
                     criteria={"option_a": "description", "option_b": "description"}),     # 2-255 options
        "q3": Score(instructions="...",
                    criteria=["lowest level", "...", "highest level"]),                     # 2-10 levels
    },
)
```

## Read answers

| Question | Read | Type |
|---|---|---|
| `Noul` | `r.nouls["q1"].noul` | float 0-1, the probability of *yes* |
| `Choice` | `r.choices["q2"].choice` | the winning option name |
| | `r.choices["q2"].probabilities` | `{option: probability}` for every option |
| | `r.choices["q2"].confidence` | float 0-1 |
| `Score` | `r.scores["q3"].score` | float; `1.6` sits between level 1 and level 2 |
| | `r.scores["q3"].legend` | `{0: "lowest level", ...}` |
| | `r.scores["q3"].probabilities`, `.confidence` | per-level probabilities, confidence |
| any | `r.model` | the exact model version that answered |
| any | `r.raw_http_response.json()["usage"]["cost"]` | exact USD cost (OpenRouter) |

## Raw HTTP

```bash
curl https://openrouter.ai/api/v1/systemone \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "~typesafe/jev-latest",
    "state": "Help! My payouts have been failing for 3 days.",
    "questions": {
      "urgent": {"type": "noul", "instructions": "Does this convey urgency?"},
      "team": {"type": "choice", "instructions": "Which team handles this?",
               "criteria": {"billing": "payments, payouts", "technical": "bugs, outages"}},
      "mood": {"type": "score", "instructions": "How frustrated is the customer?",
               "criteria": ["calm", "annoyed", "furious"]}
    }
  }'
```

## Many items in parallel

Jev allows **1,200 requests per minute**. Threads are the simplest way to use that:

```python
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=8) as pool:
    results = list(pool.map(lambda item: jev.system_one(item["text"], QUESTIONS), items))
```

## Handle errors (and fail closed)

```python
from typesafe_sdk import TypeSafeAPIError

try:
    r = jev.system_one(text, {"injection": Noul(instructions="...")})
    flagged = r.nouls["injection"].noul >= 0.5
except TypeSafeAPIError as err:        # 401 no access, 403 gateway, 429 rate limit, 529 overloaded
    flagged = True                     # a safety check that can't run must not say "safe"
```

## Limits

| | |
|---|---|
| Question types | `Noul`, `Choice` (<= 255 options), `Score` (2-10 levels) |
| Context | 64k tokens per request; state + longest question <= 32k |
| Rate | 1,200 requests / minute |
| Price | $0.042 per million input tokens; output tokens free |
| Input | text only (strings, JSON objects, lists) |
| Language | English is primary; other languages work with lower accuracy |
