# When not to use Jev

Jev is very good at one thing: **fast judgement calls with answers you define in advance**. Knowing its
limits is what separates a demo from a system you can trust. TypeSafe publishes these limits itself
([Jev 1.13 known limitations](https://docs.typesafe.ai/model-jaggedness/jev-1.13)), and the course
demonstrates several of them live in [notebook 02](../course/02_jev_vs_llm.ipynb).

## Don't ask Jev to...

| Don't ask Jev to... | Why | Do this instead |
|---|---|---|
| **write** anything (emails, summaries, fixes) | it doesn't generate text | use the LLM, *after* Jev decides it's needed |
| **count** or do **arithmetic** | not reliable, even when it gets it right | count in code: `items.count("optic") > 3` |
| **compare dates** | it treats dates as text | `date.fromisoformat(a) > date.fromisoformat(b)` |
| **be your only security check** | adversarial text can nudge any model | pair it with exact rules in code (regex, URL checks, allow-lists) |
| **read a huge document at once** | accuracy drops with irrelevant detail; state + question max 32k tokens | chunk it, filter first, or ask per passage |
| **keep two answers consistent** | separate questions have no guaranteed relationship | ask for the *fact*, derive the *action* in code |
| **work in other languages as well as English** | English is primary; others work with lower accuracy | test on your own data first |

## Seven design rules

These rules come from building the 13 use cases. Every notebook follows them.

1. **Math, counting, dates and policy consequences live in code.** Ask Jev for the *fact* ("which SEV
   level?"), then derive the *action* in code ("SEV1 or SEV2 means page someone now").
2. **Say exactly what you mean.** Jev reads literally. Describe every `Choice` option, and use `criteria` to
   define what *yes* and *no* mean for a `Noul`.
3. **Always include a "none" option** in a `Choice`, or Jev has to pick *something*. For precision, use two
   questions that must agree ("which vulnerability class?" **and** "is it really exploitable?").
4. **Keep the state small and relevant.** Judge *a question plus one passage*, not *a question plus ten
   passages*.
5. **Pair Jev with deterministic checks** for anything adversarial.
6. **Fail closed.** If a safety check can't run (timeout, rate limit, error), quarantine the content or ask
   a human. Never treat "couldn't check" as "safe".
7. **Measure against labeled data** and assert on thresholds ("accuracy >= 0.75"), never on exact
   probabilities. Probabilities vary slightly from run to run.

!!! example "A real example of rule 1"
    In [notebook 09](../course/09_oncall_log_triage.ipynb), Jev classifies an incident as **SEV2**. The runbook
    says SEV1 and SEV2 must page on-call immediately. We could ask Jev a second question ("should we
    page?"), but its answer isn't guaranteed to agree with the first. So the code does it:

    ```python
    sev = r.choices["sev"].choice
    page_now = sev in ("SEV1", "SEV2")   # the runbook rule, in code
    ```

## When an LLM is the better choice

- The answer space is **open-ended** (write, summarize, translate, explain).
- The task needs **multi-step reasoning** over the whole context.
- You make the decision **rarely**, so speed and cost don't matter much.

For everything else (anything you'd otherwise write as a quick `if` statement that needs judgement), Jev is
usually faster, cheaper and easier to trust.
