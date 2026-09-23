# Fast brain, slow brain

## The problem with LLM-only agents

An AI agent is a loop. It asks the LLM what to do, runs the tool the LLM picked, feeds the result back, and
repeats until the LLM gives a final answer. (The prequel course,
[build-your-first-ai-agent](https://github.com/harshithsunku/build-your-first-ai-agent), builds that loop in
about 35 lines.)

Look closely and the loop is full of **small decisions**:

- Which model should answer this request?
- Is it safe to run this command?
- Is this web page trying to hijack the agent?
- Did the agent actually finish the task?
- Was the final answer any good?

In an LLM-only agent, the LLM makes all of them, slowly and expensively, and often **not at all**:
nobody checks whether the command is safe, because checking would double the cost.

## The fix: give the agent a fast brain

Jev takes over the small decisions. Each one costs ~0.4 seconds and a fraction of a cent, which is cheap
enough to make on **every** step. The LLM keeps doing what only it can do: reasoning, writing and calling
tools.

![The agent loop with five Jev decision points](../assets/fast-slow-loop.svg){ .diagram }

There are **five places** to plug Jev in. [Notebook 03](../course/03_agent_loop_with_jev.ipynb) adds all
five to the same loop.

### (A) Router: before the loop

A `Choice` picks the model tier (or the tools) for a request. If Jev isn't confident, play it safe and use
the stronger model.

```python
def route(query, min_confidence=0.7):
    r = ask_jev(query, {"tier": Choice(
        instructions="Which model tier should handle this request?",
        criteria={"fast": "lookups, arithmetic, single-step tasks",
                  "capable": "multi-step planning, design, root-cause analysis, anything high-stakes"})})
    a = r.choices["tier"]
    tier = a.choice if a.confidence >= min_confidence else "capable"   # unsure -> play safe
    return SMART_MODEL if tier == "capable" else MODEL
```

### (B) Jev as a tool: inside the capability table

Give the LLM a tool that calls Jev. The LLM decides *when* to classify, and Jev does the classifying.

```python
def classify_syslog(line):
    """Classify a syslog line: severity, subsystem, and whether a human must act now."""
    r = ask_jev(line, {"severity": Score(...), "subsystem": Choice(...), "page_now": Noul(...)})
    return {...}
```

### (C) Guard: before any tool runs

Before every tool call, check it. Read-only tools pass straight through. Risky calls get
`allow` / `ask` / `block`, and `ask` goes to a human.

```python
def jev_guard(name, args, user_request):
    r = ask_jev({"tool": name, "args": args, "user_request": user_request}, {
        "verdict": Choice(instructions="Should an agent run this without asking a human?",
                          criteria={"allow": "...", "ask": "...", "block": "..."}),
        "irreversible": Noul(instructions="Could this cause an outage or lose data?"),
    })
    ...
```

### (D) "Am I done?": when the LLM says it's finished

LLMs sometimes stop early. Before accepting the final answer, ask Jev whether every part of the task has
been answered. If not, send the model back to work.

### (E) Judge: after the answer

Score every final answer. It's cheap enough to run on all of them, as a quality monitor in production
or as an eval gate in CI ([notebook 11](../course/11_jev_as_judge_and_evals.ipynb)).

## The whole loop, with two hooks

The course uses one agent loop everywhere. It's the classic loop plus two optional hooks for the guard and
the done gate:

```python
def run_agent(user_query, tools, registry, system="...", model=None,
              before_tool=None, check_done=None, max_iterations=8, verbose=True):
    messages = [{"role": "system", "content": system}, {"role": "user", "content": user_query}]
    for step in range(1, max_iterations + 1):
        resp = client.chat.completions.create(model=model or MODEL, messages=messages, tools=tools)
        msg = resp.choices[0].message
        if not msg.tool_calls:                                   # the LLM thinks it's finished
            feedback = check_done(user_query, msg.content) if check_done else None   # (D)
            if not feedback:
                return msg.content
            messages += [{"role": "assistant", "content": msg.content or ""},
                         {"role": "user", "content": feedback}]
            continue
        messages.append(...)                                    # record the tool calls
        for tc in msg.tool_calls:
            name, args = tc.function.name, json.loads(tc.function.arguments or "{}")
            blocked = before_tool(name, args) if before_tool else None               # (C)
            result = {"blocked": blocked} if blocked else registry[name](**args)
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": json.dumps(result)})
    return "Stopped: hit max_iterations."
```

## Beyond the loop: three more patterns

The use cases combine the decision points with three patterns you'll see again and again:

| Pattern | How it works | Where you'll see it |
|---|---|---|
| **Classify, then act** | Jev decides every item; the LLM works only on the slice that needs language | email triage, scam detector |
| **Map-reduce** | Jev checks every chunk; the LLM reads only the flagged ones | vulnerability hunter, log triage |
| **Layered checks** | exact rules in code + Jev for intent + a human for grey areas | guardrails, scam detector |

**Next:** [When not to use Jev](when-not-to-use-jev.md).
