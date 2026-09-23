<div align="center">

# Jev: Zero to Agent

**Your agent has a slow brain. Give it a fast one.**

A hands-on course that takes you from your first call to **Jev** (TypeSafe AI's *System One* model) to
**13 production-style use cases** where Jev makes the decisions inside a real LLM agent loop.
It uses one OpenRouter key and 12 notebooks, and every result on this page comes from a real run.

[![CI](https://github.com/harshithsunku/jev-zero-to-agent/actions/workflows/ci.yml/badge.svg)](.github/workflows/ci.yml)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![notebooks](https://img.shields.io/badge/notebooks-12-orange)
![use cases](https://img.shields.io/badge/use%20cases-13-teal)
![one key](https://img.shields.io/badge/one%20key-OpenRouter-6f42c1)
![license](https://img.shields.io/badge/license-MIT-green)

<img src="docs/jev-vs-llm.png" alt="Jev vs a small and a frontier LLM on the same typed questions: accuracy, latency, cost" width="100%">

<sub>From notebook 02: the same typed questions on the same labeled data. On this run Jev matched the frontier model's accuracy on the 8-way task, and was <b>8x faster and 87x cheaper</b> than it (6.8x faster and 4.3x cheaper than the small model). Run it yourself; your numbers will vary.</sub>

</div>

---

## Why this repo exists

LLM agents spend most of their time on **small decisions**: *Which tool? Is this safe to run? Is this email
urgent? Is this passage relevant? Am I done?* Today we pay a text-generating model, token by token, to make
every one of them.

[**Jev**](https://typesafe.ai/blog/introducing-system-one-models-and-jev) is a new kind of model built for
exactly those decisions. You give it a **state** (text or JSON) and **typed questions**, and it returns
**typed, calibrated answers** in a few hundred milliseconds. It never generates text, so it can't
hallucinate an answer you didn't define.

| | **Fast brain: Jev (System 1)** | **Slow brain: LLM (System 2)** |
|---|---|---|
| Output | `Noul` P(yes) · `Choice` one of <=255 · `Score` 2-10 levels | free text + tool calls |
| Latency (our run) | **~360 ms p50** | 2.5-3 s p50 |
| Price | **$0.042 / M input tokens, output free** | $0.10-$10 / M input + output |
| Good at | classify, route, guard, score, verify, judge | write, explain, plan, call tools |
| Bad at | generating text, counting, date math | being cheap and fast at thousands of tiny decisions |

**This course teaches the pattern that combines them:** Jev makes the thousands of small decisions and the
LLM does the few things that need language. You learn it the way
[build-your-first-ai-agent](https://github.com/harshithsunku/build-your-first-ai-agent) taught agents: one
hand-rolled loop, reused in every notebook.

<p align="center"><img src="docs/fast-slow-loop.svg" alt="The agent loop with five Jev decision points: router, Jev as a tool, guard, done gate, judge" width="92%"></p>

## Quick start (about 60 seconds)

You need **one [OpenRouter key](https://openrouter.ai/keys)**. It drives the LLM *and* Jev.

```bash
git clone https://github.com/harshithsunku/jev-zero-to-agent.git
cd jev-zero-to-agent
./setup.sh                      # Windows: .\setup.ps1   (uses uv if present, else venv + pip)
# paste your key into .env  ->  OPENAI_API_KEY=sk-or-v1-...
uv run python scripts/doctor.py # checks: LLM chat, LLM tool calling, Jev
uv run jupyter lab              # open 01_hello_jev.ipynb
```

```text
OK   LLM chat completion                  1449 ms  'pong'
OK   LLM tool calling                      887 ms  get_time({"city":"Paris"})
OK   Jev System One (typesafe)             804 ms  model=typesafe/jev-1.13-20260917  is_scam=0.97  kind=phishing  pressure=1.98
```

Your first Jev call is this:

```python
from typesafe_sdk import TypeSafeClient, Noul, Choice, Score

jev = TypeSafeClient(api_key=OPENROUTER_KEY, base_url="https://openrouter.ai/api", model="~typesafe/jev-latest")
r = jev.system_one(
    "Help! Payouts have failed for 3 days and my team can't get paid.",
    {
        "urgent":     Noul(instructions="Does the message convey urgency?"),
        "team":       Choice(instructions="Which team handles this?",
                             criteria={"billing": "payments, payouts", "technical": "bugs, outages"}),
        "frustration": Score(instructions="How frustrated is the customer?",
                             criteria=["calm", "annoyed", "frustrated", "furious"]),
    },
)
r.nouls["urgent"].noul          # 0.98
r.choices["team"].choice        # 'billing'  (probabilities + confidence included)
r.scores["frustration"].score   # 2.83 -> between 'frustrated' and 'furious'
```

> **No Jev access yet?** Set `JEV_BACKEND=adapter` in `.env`. The notebooks then answer the same typed
> questions with your LLM through [`system-one-adapter`](https://github.com/typesafe-ai/system-one-adapter-python).
> It's slower and pricier, but notebooks 01 and 03-12, `app.py` and the email job all run, and their built-in
> accuracy checks pass (we tested this). Only notebook 02 needs real Jev, because it benchmarks Jev itself.

## The course

Every notebook runs top to bottom in under a minute (notebook 02 takes about 2), prints what it cost, and
is committed **with its outputs**, so you can read the results on GitHub before you run anything.

| # | Notebook | You learn | Headline result (our run) |
|---|---|---|---|
| 01 | [`hello_jev`](01_hello_jev.ipynb) | `Noul`, `Choice` and `Score`; fan-out; JSON state; `criteria`; Jev vs LLM head to head | 4 questions in 1 call, ~360 ms |
| 02 | [`jev_vs_llm`](02_jev_vs_llm.ipynb) | Benchmark vs a small and a frontier LLM; calibration; **known limits** | 8x faster, 87x cheaper than frontier |
| 03 | [`agent_loop_with_jev`](03_agent_loop_with_jev.ipynb) | The agent loop + **5 decision points**: router, Jev-as-tool, guard, done gate, judge | guard blocks shutting the only core uplink |
| 04 | [`email_triage_job`](04_email_triage_job.ipynb) | **UC1**: classify a whole inbox, LLM drafts only where needed, read-only IMAP | 40 emails in 2.4 s, 92% category accuracy |
| 05 | [`sms_scam_shield`](05_sms_scam_shield.ipynb) | **UC2**: code signals + Jev composite score, as an agent tool | 20/20 scams caught, 0 legit texts blocked |
| 06 | [`code_vuln_hunter`](06_code_vuln_hunter.ipynb) | **UC3**: `ast` chunking, Jev map, LLM reduce | 9/9 planted bugs, 0 false alarms, 1.3 s |
| 07 | [`auto_mode_guardrails`](07_auto_mode_guardrails.ipynb) | **UC4-5**: action guard with human approval; prompt-injection shield on inputs *and tool results* | 14/14 guard decisions; hidden injection quarantined |
| 08 | [`model_and_tool_router`](08_model_and_tool_router.ipynb) | **UC6-7**: route to the cheapest capable model; shortlist tools from a 48-tool catalog | 14/14 routes, 47% cheaper; 90% fewer tool tokens |
| 09 | [`oncall_log_triage`](09_oncall_log_triage.ipynb) | **UC8**: templating in code, Jev per template, LLM root cause, SEV from *your* runbook | 162 lines -> 14 templates -> root cause |
| 10 | [`rag_relevance_and_citations`](10_rag_relevance_and_citations.ipynb) | **UC9-10**: relevance filter before generation, citation check after | wrong citation caught (P=0.02); "I don't know" when nothing fits |
| 11 | [`jev_as_judge_and_evals`](11_jev_as_judge_and_evals.ipynb) | **UC11-12**: Jev judge vs LLM judges; CI eval gate; measure the done gate | 20/20 agreement; gate 8/8 |
| 12 | [`capstone_ops_copilot`](12_capstone_ops_copilot.ipynb) | **UC13**: shield -> dispatcher -> 5 desks + human queue | 25 mixed items in 8.6 s, 24/25 routed right |

**A full run of all 12 notebooks costs about $0.17.** Most of that is the frontier model in notebook 02's
benchmark; everything else together is under 3 cents.

## 13 use cases, and where Jev sits in each

| # | Use case | Jev primitives | Where Jev sits | What the LLM does |
|---|---|---|---|---|
| 1 | **Email triage job** | `Choice` category · `Noul` needs_reply · `Score` urgency | batch pre-filter over the whole inbox | drafts replies **only** for the "reply" bucket |
| 2 | **SMS scam (smishing) shield** | `Noul` is_scam · `Choice` scam type · `Score` pressure | composite score with deterministic URL checks | explains red flags in plain words |
| 3 | **Code vulnerability hunter** | `Choice` CWE class · `Noul` really exploitable? · `Score` severity | **map** over every function | **reduce**: exploit story + patch for the hits |
| 4 | **Auto Mode tool-call guard** | `Choice` allow/ask/block · `Noul` irreversible · `Noul` exfiltration | before every tool executes | normal agent work |
| 5 | **Prompt-injection shield** | `Noul` injection (+ regex) | on user input **and on tool results** | never sees quarantined content |
| 6 | **Model router** | `Choice` fast/capable + confidence fallback | before the loop | answers on the chosen tier |
| 7 | **Tool / skill picker** | `Choice` over up to 255 tools | before the loop | tool-calls from a 5-tool shortlist |
| 8 | **On-call log and alert triage** | `Score` severity · `Choice` area · `Noul` customer impact / security · `Choice` SEV | once per log template | root-causes the top clusters |
| 9 | **RAG relevance filter** | `Noul` relevant, per passage | between retrieve and generate | answers from kept passages only |
| 10 | **Citation / hallucination check** | `Noul` supported, per claim | after generation | rewrites if unsupported |
| 11 | **LLM-output judge and CI evals** | `Noul` correct · `Score` quality | offline, and on every PR | nothing (that's the point) |
| 12 | **"Am I done?" gate** | `Noul` complete | loop termination | keeps working until the gate passes |
| 13 | **Support / ops dispatcher** | `Choice` desk · `Score` urgency · `Noul` needs human | supervisor | the specialist desks do the work |

## Run the use cases outside the notebooks

**The email job (cron-able).** Jev decides every email and the LLM drafts only the replies that are needed.
It works on the sample inbox or your real mailbox over **read-only** IMAP, and it never sends mail.

```bash
uv run python jobs/email_triage.py --draft-replies                   # sample inbox
uv run python jobs/email_triage.py --source imap --limit 50          # set IMAP_* in .env (app password)
# cron: */30 8-18 * * 1-5  cd /path/to/jev-zero-to-agent && uv run python jobs/email_triage.py --source imap --draft-replies
```

**The Jev Playground (Gradio).** The Playground, Email triage, SMS shield, Code vuln hunter, Guarded agent
and "Jev vs LLM race" tabs are all in one file, [`app.py`](app.py).

```bash
uv run --extra ui python app.py      # http://127.0.0.1:7860
```

## Configure

Everything lives in `.env` (see [`.env.example`](.env.example)):

| Variable | Default | What |
|---|---|---|
| `OPENAI_API_KEY` | - | your OpenRouter key (used for both brains) |
| `OPENAI_BASE_URL` | `https://openrouter.ai/api/v1` | LLM endpoint (any OpenAI-compatible server works) |
| `MODEL` | `openai/gpt-6-luna` | slow brain: any **tool-capable** chat model |
| `SMART_MODEL` | `openai/gpt-6-sol` | the "capable" tier for routing and benchmarks |
| `JEV_MODEL` | `~typesafe/jev-latest` | fast brain (resolves to `typesafe/jev-1.13-20260917` at the time of writing) |
| `TYPESAFE_BASE_URL` | `https://openrouter.ai/api` | the SDK appends `/v1/systemone`; use `https://api.typesafe.ai` with a direct TypeSafe key |
| `TYPESAFE_API_KEY` | = `OPENAI_API_KEY` | set only if you use a separate key |
| `JEV_BACKEND` | `typesafe` | `adapter` answers Jev questions with `MODEL` (no Jev access needed) |
| `VERIFY_SSL` | `true` | `false` only behind a TLS-intercepting proxy |

## Design rules we learned the hard way

1. **Math, counting, dates and policy consequences live in code.** Ask Jev for the *fact* (for example, "which
   SEV level?") and derive the *action* in code ("SEV1 or SEV2 means page"). Separate Jev questions have no
   guaranteed consistency with each other.
2. **Say exactly what you mean.** Jev reads literally. Asked "is this urgent?", a sale email that *says* URGENT
   sits on the fence (P=0.44 in our run). Spell out the condition with `criteria` and you get a decisive 0.04
   (notebook 01, section 6). Describe every `Choice` option too.
3. **Always include a `none` option**, and use two questions that must agree (a class *and* "is it really
   exploitable?") to separate real bugs from safe look-alikes (notebook 06).
4. **Keep the state small and relevant.** Judge a *question + one passage*, not a question + ten passages.
5. **Pair Jev with deterministic checks** for anything adversarial: URL checks for scams, regex ACLs for shell
   commands.
6. **Guards fail closed.** If screening fails, quarantine the content or ask a human.
7. **Measure everything against labels** and assert on thresholds, never on exact probabilities.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `401` / `403 permission` from `/v1/systemone` with a JSON body | Your key has no Jev access. Set `JEV_BACKEND=adapter`. |
| `403` with a **Cloudflare HTML page** | The gateway's firewall rejected the payload because it looked like a live exploit chain (e.g. `curl ... \| sh` plus a key-theft command). This is why the guards fail closed. Rephrase fixtures; don't retry in a loop. |
| `429` / `529` | Rate limited or overloaded. The SDK retries with backoff. Lower `jev_map(workers=...)`. |
| The model answers without calling tools | Pick a tool-capable `MODEL`. `doctor.py` checks this. |
| `temperature` errors | Current OpenAI models on OpenRouter reject `temperature`, so the course never sends it. |
| SSL errors behind a corporate proxy | `VERIFY_SSL=false` (trusted networks only). |

## Project layout

```text
01_hello_jev.ipynb ... 12_capstone_ops_copilot.ipynb   the course (committed with outputs)
app.py                     Gradio playground (the only file that imports gradio)
jobs/email_triage.py       the email job, cron-able, read-only IMAP
scripts/doctor.py          "is my setup working?"
scripts/check_notebooks.py keyless CI: valid notebooks, identical shared cells, no secrets
data/                      labeled fixtures: inbox, SMS, tickets, KB, logs, a vulnerable toy app, evals
docs/                      the benchmark chart and the loop diagram
AGENTS.md                  conventions for AI coding agents working on this repo
```

## Safety

All agent tools are read-only, sandboxed, or **dry-run mocks**. `data/vulnerable_app/` is parsed with `ast`
and never executed, and its "secrets" are AWS's documented example values. `data/untrusted/` contains a
deliberate prompt injection used as a test target. IMAP access is read-only. Nothing in this repo sends
email or runs shell commands.

## Learn more

- [Introducing System One models and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev) (TypeSafe)
- [Building a harness with Jev](https://www.langchain.com/blog/building-a-harness-with-jev) (LangChain)
- [TypeSafe docs](https://docs.typesafe.ai/introduction/quickstart) · [Jev 1.13 known limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13) · [Jev on OpenRouter](https://openrouter.ai/docs/guides/community/typesafe-sdk)
- The prequel: [build-your-first-ai-agent](https://github.com/harshithsunku/build-your-first-ai-agent), 12 notebooks from a single chat completion to multi-agent systems

## Contributing

New use cases, fixes and translations are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md). If this helped
you, a ⭐ helps others find it.

## License

[MIT](LICENSE). Not affiliated with TypeSafe AI, OpenRouter or OpenAI.
