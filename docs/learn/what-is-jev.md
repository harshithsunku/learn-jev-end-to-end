# Jev in 5 minutes

## What is Jev?

**Jev** is an AI model made by [TypeSafe AI](https://typesafe.ai/blog/introducing-system-one-models-and-jev).
TypeSafe calls it a **System One model**, after the "fast thinking" system in Daniel Kahneman's book
*Thinking, Fast and Slow*.

A normal LLM (like GPT or Claude) is a **writer**. It generates text one token at a time, and it can write
anything, including things that are wrong.

Jev is a **decider**. It doesn't write at all. You ask it questions whose possible answers you define in
advance, and it returns:

- the **answer**, which is always one of the options you allowed, and
- **how sure it is**, as a probability you can act on.

Because it only picks from your options, it can't hallucinate a new answer. Because it doesn't write, it's
fast (a few hundred milliseconds) and cheap (you pay only for input tokens; output is free).

!!! note "The name"
    Jev is named after William Stanley Jevons, the economist behind the *Jevons paradox*: when something
    becomes much cheaper, people use far more of it. TypeSafe's bet is that very cheap decisions will get
    used everywhere.

## The three kinds of question

Everything Jev does is built from three question types. Learn these and you know Jev.

=== "Noul: yes or no"

    Ask a yes/no question and get the **probability of yes**.

    ```python
    r = ask_jev(
        "The delivery arrived two weeks late and the box was crushed. Not ordering again.",
        {"complaint": Noul(instructions="Is the customer complaining?")},
    )
    r.nouls["complaint"].noul   # 0.99
    ```

    Use it for: *is this spam? is this safe? is the task complete? does this passage answer the question?*

=== "Choice: pick one"

    Give a list of named options (up to **255**) and get the winner plus a probability for **every** option.

    ```python
    r = ask_jev(
        "I was charged twice for my subscription this month.",
        {"team": Choice(
            instructions="Which team should handle this message?",
            criteria={"billing": "payments, invoices, refunds",
                      "technical": "bugs, outages, errors",
                      "sales": "pricing questions, upgrades"})},
    )
    r.choices["team"].choice         # 'billing'
    r.choices["team"].probabilities  # {'billing': 1.0, 'technical': 0.0, 'sales': 0.0}
    r.choices["team"].confidence     # 1.0
    ```

    Use it for: *routing, categories, picking a tool, picking a model, severity levels.*

=== "Score: a position on a scale"

    Give 2-10 **ordered** levels and get a score. It can fall **between** levels, which tells you more
    than a single label would.

    ```python
    r = ask_jev(
        "Production checkout has been down for 20 minutes and customers are tweeting about it.",
        {"urgency": Score(
            instructions="How urgent is this for the on-call engineer?",
            criteria=["next week", "today", "within the hour", "drop everything now"])},
    )
    r.scores["urgency"].score   # 2.93  -> almost "drop everything now"
    ```

    Use it for: *urgency, severity, quality ratings, rubric grading.*

## Five things to know

**1. The state is what's being judged.** It can be plain text or JSON (a ticket, a log line, a row from a
database). Keep it small and relevant; Jev is less accurate when you pad it with unrelated detail.

**2. You can ask many questions in one call.** Jev answers them all at once, in parallel, so four questions
cost about the same time as one.

```python
r = ask_jev(message, {
    "is_urgent":    Noul(instructions="Does the message convey urgency?"),
    "department":   Choice(instructions="Which team?", criteria={...}),
    "frustration":  Score(instructions="How frustrated?", criteria=[...]),
    "wants_refund": Noul(instructions="Is the customer asking for money back?"),
})
```

**3. Jev reads your question literally.** Asked "is this urgent?", a sale email that *says* URGENT gets a
fence-sitting answer. Say exactly what you mean, and use `criteria` to define the edges:

```python
Noul(
    instructions="Will the recipient suffer real harm if they don't act within the next hour?",
    criteria={"true": "a real deadline with real consequences",
              "false": "marketing pressure or no consequence"},
)
```

**4. The probability is the product.** Because answers come with calibrated probabilities, you can set
thresholds based on what a mistake costs you: *block above 0.7, warn above 0.4, ask a human when confidence
is below 0.6.* You'll use this pattern in almost every notebook.

**5. Jev is not a chat model.** It can't write an email, count items reliably, or do date math. Keep those
in code or give them to the LLM. [When not to use Jev](when-not-to-use-jev.md) covers this in detail.

## How you call it

Jev has its own endpoint, `/v1/systemone`. It's not a chat-completions API. The easiest way to call it is
through the official `typesafe-sdk` package, pointed at OpenRouter so the same key works for everything:

```python
from typesafe_sdk import TypeSafeClient

jev = TypeSafeClient(api_key=OPENROUTER_KEY,
                     base_url="https://openrouter.ai/api",
                     model="~typesafe/jev-latest")
```

Prefer raw HTTP? See the [cheat sheet](../reference/cheatsheet.md) for a `curl` example.

**Next:** [Fast brain, slow brain](fast-and-slow.md) shows where Jev fits inside an AI agent.
