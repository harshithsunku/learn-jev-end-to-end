# Start in 3 steps

You need about **5 minutes**, **Python 3.10 or newer**, and **one OpenRouter API key**. That single key
works for both Jev and the LLM.

## 1. Get an OpenRouter key

Sign in at [openrouter.ai/keys](https://openrouter.ai/keys) and create a key. It starts with `sk-or-v1-`.
Add a few dollars of credit. The whole course costs **less than $0.20** to run.

## 2. Clone and set up

=== "Linux / macOS"

    ```bash
    git clone https://github.com/harshithsunku/learn-jev-end-to-end.git
    cd learn-jev-end-to-end
    ./setup.sh
    ```

=== "Windows (PowerShell)"

    ```powershell
    git clone https://github.com/harshithsunku/learn-jev-end-to-end.git
    cd learn-jev-end-to-end
    .\setup.ps1
    ```

=== "Manual (uv)"

    ```bash
    git clone https://github.com/harshithsunku/learn-jev-end-to-end.git
    cd learn-jev-end-to-end
    uv sync --extra ui
    cp .env.example .env
    ```

The setup script installs everything (with [uv](https://docs.astral.sh/uv/) if you have it, otherwise with
`pip`) and creates a `.env` file for your settings.

Open `.env` and paste your key:

```bash title=".env"
OPENAI_API_KEY=sk-or-v1-your-key-here
```

Then check that everything works:

```bash
uv run python scripts/doctor.py
```

```text
OK   LLM chat completion                  1169 ms  'pong'
OK   LLM tool calling                      842 ms  get_time({"city":"Paris"})
OK   Jev System One (typesafe)             447 ms  model=typesafe/jev-1.13-20260917  is_scam=0.97  kind=phishing

All green. Next: uv run jupyter lab  ->  open 01_hello_jev.ipynb
```

!!! tip "Only the Jev check failed?"
    Your key may not have Jev access yet. Set `JEV_BACKEND=adapter` in `.env` and the notebooks will answer
    the same questions with your LLM instead. Everything except the benchmark notebook runs.
    [More about the fallback](../guides/no-jev-access.md).

## 3. Open the first notebook

```bash
uv run jupyter lab
```

Open **`01_hello_jev.ipynb`** and run the cells from top to bottom (++shift+enter++).
Every notebook is also [readable on this site](../course/index.md), with real outputs, if you just want to read first.

## Your first Jev call, explained

This is the whole idea. Everything else in the course builds on it.

```python
from typesafe_sdk import TypeSafeClient, Noul, Choice, Score

jev = TypeSafeClient(
    api_key="sk-or-v1-...",                  # your OpenRouter key
    base_url="https://openrouter.ai/api",    # Jev through OpenRouter
    model="~typesafe/jev-latest",
)

r = jev.system_one(
    "Help! Payouts have failed for 3 days and my team can't get paid.",     # the state
    {
        "urgent": Noul(instructions="Does the message convey urgency?"),
        "team":   Choice(instructions="Which team handles this?",
                         criteria={"billing": "payments, payouts", "technical": "bugs, outages"}),
        "mood":   Score(instructions="How frustrated is the customer?",
                        criteria=["calm", "annoyed", "frustrated", "furious"]),
    },
)

r.nouls["urgent"].noul      # 0.98       -> probability of "yes"
r.choices["team"].choice    # 'billing'  -> plus .probabilities and .confidence
r.scores["mood"].score      # 2.83       -> between "frustrated" (2) and "furious" (3)
```

| Part | What it is |
|---|---|
| **state** | the thing being judged: text or JSON |
| **`Noul`** | a yes/no question; you get the probability of *yes* |
| **`Choice`** | pick one option from a list you define (up to 255); you get a probability for each |
| **`Score`** | a position on an ordered scale (2-10 levels); the score can fall between levels |

All three questions are answered in **one call**, in parallel.

## Where to next?

<div class="grid cards" markdown>

-   :material-lightbulb-on: **Understand Jev**

    ---

    [Jev in 5 minutes](../learn/what-is-jev.md): the three question types, probabilities and when to trust them.

-   :material-school: **Take the course**

    ---

    [Pick a learning path](../course/index.md): 15 minutes, 1 hour, or all 12 notebooks.

-   :material-hammer-wrench: **Jump to a use case**

    ---

    [13 things you can build](../use-cases/index.md), each with a runnable notebook.

</div>
