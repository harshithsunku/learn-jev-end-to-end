# The course

Twelve notebooks. Each one runs from top to bottom in about a minute (notebook 02 takes about two), measures
itself against labeled data, and prints what it cost. Every page here shows a **real run with real
outputs**, so you can read before you run.

## Pick your path

<div class="grid cards" markdown>

-   :material-timer-sand: **15 minutes: "What is this?"**

    ---

    [01 · Hello, Jev](01_hello_jev.ipynb) → [02 · Jev vs LLMs](02_jev_vs_llm.ipynb)

    You'll know what Jev does, how fast and cheap it is, and where it breaks.

-   :material-clock-outline: **1 hour: "Put it in an agent"**

    ---

    01 → [03 · The agent loop](03_agent_loop_with_jev.ipynb) → [04 · Email triage](04_email_triage_job.ipynb) → [07 · Guardrails](07_auto_mode_guardrails.ipynb)

    You'll plug Jev into a real agent and build two tools you can use today.

-   :material-trophy-outline: **A weekend: "End to end"**

    ---

    All 12, in order, finishing with the [capstone](12_capstone_ops_copilot.ipynb).

    You'll have built all 13 use cases and a complete ops copilot.

</div>

## All lessons

| # | Lesson | What you learn | What you build |
|---|---|---|---|
| 01 | [Hello, Jev](01_hello_jev.ipynb) | the three question types, many questions in one call, JSON state, `criteria` | your first calls, Jev vs an LLM head to head |
| 02 | [Jev vs LLMs](02_jev_vs_llm.ipynb) | accuracy, latency, cost, calibration; Jev's known limits | a fair benchmark and a chart |
| 03 | [The agent loop + Jev](03_agent_loop_with_jev.ipynb) | the five decision points: router, Jev as a tool, guard, done gate, judge | an agent that refuses to shut down a core network link |
| 04 | [Email triage job](04_email_triage_job.ipynb) | batch classification, confidence routing, LLM only where needed | a scheduled inbox-triage job (works with real IMAP) |
| 05 | [SMS scam shield](05_sms_scam_shield.ipynb) | combining code signals with Jev; three-way verdicts | a scam-text checker for your family |
| 06 | [Code vulnerability hunter](06_code_vuln_hunter.ipynb) | chunk with `ast`, map with Jev, reduce with the LLM | a security scanner that found 9/9 planted bugs |
| 07 | [Guardrails](07_auto_mode_guardrails.ipynb) | action guards, human approval, prompt-injection shields, failing closed | a shell agent that can't be tricked into leaking data |
| 08 | [Model and tool router](08_model_and_tool_router.ipynb) | tier routing with live prices, tool shortlists | a router that cuts cost by about half |
| 09 | [On-call log triage](09_oncall_log_triage.ipynb) | templating in code, Jev per template, SEV from your runbook | an incident summary from raw logs |
| 10 | [RAG relevance and citations](10_rag_relevance_and_citations.ipynb) | relevance filtering, citation checking | a docs Q&A bot that says "I don't know" |
| 11 | [Jev as judge](11_jev_as_judge_and_evals.ipynb) | Jev vs LLM judges, CI eval gates, measuring gates | an eval suite that runs on every PR |
| 12 | [Capstone: ops copilot](12_capstone_ops_copilot.ipynb) | everything together | a copilot that routes 25 mixed items in ~9 s |

## How every notebook is built

The same structure repeats on purpose, so each new notebook only teaches what's new:

1. **Config cell**: one OpenRouter key for both brains. It's identical in every notebook.
2. **Helpers cell**: `ask_jev()` for the fast brain, `chat()` for the slow brain, and `SPEND`, which tracks
   the exact cost of every call.
3. **The agent loop** (where one is needed), identical everywhere, from
   [build-your-first-ai-agent](https://github.com/harshithsunku/build-your-first-ai-agent), plus two hooks.
4. **The lesson**: data, questions, measurement against labels, and the recap.

!!! tip "Download and run"
    Each notebook page has a download button at the top. To run notebooks locally, follow
    [Start in 3 steps](../start/index.md).
