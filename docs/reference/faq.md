# FAQ

??? question "What is Jev, in one sentence?"
    A model from TypeSafe AI that answers typed questions (yes/no, pick one, score) about some text,
    with a calibrated probability, in a few hundred milliseconds, without ever generating text.

??? question "Do I need a TypeSafe account?"
    No. One **OpenRouter** key works for both Jev and the LLM. If you have a direct TypeSafe key, set
    `TYPESAFE_API_KEY` and `TYPESAFE_BASE_URL=https://api.typesafe.ai`.

??? question "What if my key doesn't have Jev access?"
    Set `JEV_BACKEND=adapter`. Every notebook except the benchmark runs with your LLM answering the same
    questions. [Details](../guides/no-jev-access.md).

??? question "How much does it cost?"
    A full run of all 12 notebooks costs about **$0.17**; the frontier model in the benchmark is most of that.
    A single Jev decision costs about $0.00002.

??? question "Do I need to know machine learning?"
    No. If you can read Python and run a Jupyter notebook, you can take the course. There's no training
    and no GPUs.

??? question "Can I use a different LLM?"
    Yes. Set `MODEL` to any tool-capable model on OpenRouter, or point `OPENAI_BASE_URL` at any
    OpenAI-compatible server (for example, a local Ollama). Jev still runs through OpenRouter.

??? question "Is it safe to run?"
    Yes. Every tool is read-only, sandboxed or a dry-run mock. Nothing runs shell commands or sends email.
    The vulnerable app is parsed, never executed. The injection examples are data, used as test targets.

??? question "Why notebooks and not a library?"
    Because the goal is to *learn the pattern*. Every notebook is self-contained and copy-pasteable, and
    the same loop and helpers repeat so you can see what changes. When you're ready, `app.py` and
    `jobs/email_triage.py` show the same code as plain Python.

??? question "Can I use this with LangChain or Pydantic AI?"
    Yes. TypeSafe ships `langchain-typesafe` (with router and Auto Mode middleware) and a `typesafe:` model
    for Pydantic AI. Notebook 03's appendix shows both. The course hand-rolls the patterns first so you know
    what those one-liners do.

??? question "How is this different from the prequel?"
    [build-your-first-ai-agent](https://github.com/harshithsunku/build-your-first-ai-agent) teaches the
    agent loop itself. This course reuses that loop and adds a second kind of model to make the agent's
    decisions faster, cheaper and safer.
