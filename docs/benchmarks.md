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
| **Jev** | 98% | 0.029 | **92%** | **363 ms** | **486 ms** | **$0.019** |
| Small LLM | 100% | 0.001 | 88% | 2,455 ms | 5,610 ms | $0.080 |
| Frontier LLM | 100% | 0.000 | 92% | 2,943 ms | 4,159 ms | $1.645 |

**Jev vs the small LLM:** 6.8x faster, 4.3x cheaper. **Jev vs the frontier LLM:** 8.1x faster, 87x cheaper.

## How to read this honestly

- **The easy task saturates.** Every model gets about 100% on obvious scam texts, so task A mostly tells
  you about speed and cost.
- **The LLMs had better Brier scores on task A.** They were confident *and* right on an easy set. Jev put
  some legitimate-but-scammy-looking texts (a bill that's due, a sale ending tonight) in the 0.1-0.5 range.
  It didn't block them, but it was less certain.
- **On the harder task, Jev matched the frontier model** (92%) and beat the small one (88%).
- **Speed and cost are Jev's clearest advantage.** It was 7-8x faster at the median and 4-87x cheaper per
  decision, and its latency was more consistent (p95).
- **Structural advantages don't show up in a table:** Jev's answer is *always* one of your options (no
  parsing, no retries), and one call answers many questions at once.

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
