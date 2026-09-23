# Benchmarks

[Notebook 02](course/02_jev_vs_llm.ipynb) asks the **same typed questions** about the **same labeled data**
to three contestants, and reports everything, including where Jev lost.

![Jev vs a small and a frontier LLM](assets/jev-vs-llm.png)

## Setup

| Contestant | How it answers |
|---|---|
| **Jev** (`typesafe/jev-1.13-20260917`) | the System One API, through OpenRouter |
| **Small LLM** (`openai/gpt-6-luna`) | the *same* typed question, through [`system-one-adapter`](https://github.com/typesafe-ai/system-one-adapter-python) |
| **Frontier LLM** (`openai/gpt-6-sol`) | the same, with a big model |

The adapter makes the LLMs answer the exact same `Noul` / `Choice` questions and return probabilities, so
this is a like-for-like comparison, not a prompt-writing contest. Every contestant ran with 4 parallel
workers.

| Task | Data | Question |
|---|---|---|
| **A: SMS scam** (easy) | 40 texts, 20 scams | `Noul`: is this a scam? |
| **B: email category** (harder) | 40 emails, 8 categories | `Choice`: which of 8 categories? |

## Results (run of 2026-09-23)

| Contestant | A: accuracy | A: Brier ↓ | B: accuracy | p50 latency | p95 latency | $ per 1,000 decisions |
|---|---|---|---|---|---|---|
| **Jev** | 98% | 0.029 | **92%** | **409 ms** | **686 ms** | **$0.019** |
| Small LLM | 98% | 0.008 | 90% | 2,427 ms | 3,848 ms | $0.082 |
| Frontier LLM | 100% | 0.000 | 92% | 2,901 ms | 4,271 ms | $1.667 |

**Jev vs the small LLM:** 5.9x faster, 4.3x cheaper. **Jev vs the frontier LLM:** 7.1x faster, 88x cheaper.

Numbers move a little between runs: an earlier run the same day gave 6.8x / 8.1x faster and 87x cheaper. The ratios, not the exact milliseconds, are the stable result.

## How to read this honestly

- **The easy task saturates.** Every model gets about 100% on obvious scam texts, so task A mostly tells
  you about speed and cost.
- **The LLMs had better Brier scores on task A.** They were confident *and* right on an easy set. Jev put
  some legitimate-but-scammy-looking texts (a bill that's due, a sale ending tonight) in the 0.1-0.5 range.
  It didn't block them, but it was less certain.
- **On the harder task, Jev matched the frontier model** (92%) and beat the small one (90%).
- **Speed and cost are Jev's clearest advantage.** It was 6-7x faster at the median and 4-88x cheaper per
  decision, and its latency was more consistent (p95).
- **Structural advantages don't show up in a table:** Jev's answer is *always* one of your options (no
  parsing, no retries), and one call answers many questions at once.

## Per-class results (task B)

Precision, recall and F1 for each email category. There are **only 5 emails per class**, so one mistake
moves a class's recall by 0.2: read this as a map of *where* errors happen, not as a per-class benchmark.

| Class | Jev P / R / F1 | Small LLM P / R / F1 | Frontier LLM P / R / F1 |
|---|---|---|---|
| action_request | 0.83 / 1.00 / 0.91 | 0.83 / 1.00 / 0.91 | 0.83 / 1.00 / 0.91 |
| meeting | 1.00 / 0.80 / 0.89 | 1.00 / 0.60 / 0.75 | 1.00 / 0.80 / 0.89 |
| billing | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| newsletter | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| security_alert | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| phishing | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 |
| personal | 1.00 / 0.60 / 0.75 | 1.00 / 0.60 / 0.75 | 1.00 / 0.60 / 0.75 |
| notification | 0.71 / 1.00 / 0.83 | 0.62 / 1.00 / 0.77 | 0.71 / 1.00 / 0.83 |
| **macro F1** | **0.92** | **0.90** | **0.92** |

All three models struggled with the same boundary: **personal vs action_request / notification**. Jev's three
misses were "Can you drive on Saturday?" (a friend's request, labeled personal, read as an action request),
"Water shut-off tomorrow 9-12" (labeled personal, read as a notification) and "Meeting recording available"
(labeled meeting, read as a notification). These are arguably labeling ambiguities as much as model errors.
Tightening the category descriptions is the fix.

## Known limits, tested live

Notebook 02 also tries three of Jev's documented weak spots: counting, date comparison and adversarial text.
Jev got these particular examples right, but TypeSafe's own docs say not to rely on it for them, so the
course does them in code. See [When not to use Jev](learn/when-not-to-use-jev.md).

## Run it yourself

```bash
uv run jupyter nbconvert --to notebook --execute --inplace 02_jev_vs_llm.ipynb
```

It takes about 2 minutes and costs about $0.14, mostly the frontier model. Change `MODEL` and
`SMART_MODEL` in `.env` to benchmark other LLMs. Your numbers will differ from ours: that's the point of
running it.
