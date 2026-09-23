# Use your own data

Every use case is built from two things you can swap: **the data** and **the questions**. The loop, the
helpers and the patterns stay the same.

## Swap the data

| Use case | Point it at | Where |
|---|---|---|
| Email triage | your mailbox (read-only IMAP) | `.env` → `IMAP_*`, or `load_imap()` in notebook 04 |
| Scam shield | your helpdesk's "is this real?" reports | `SMS` list in notebook 05 |
| Vulnerability hunter | any Python repo | `ROOT` in notebook 06 (the sandbox root) |
| Log triage | your service logs | `LOG_DIR` and `LINE_RE` in notebook 09 |
| RAG filter | your docs, as Markdown with `## ` sections | `load_passages("your/docs")` in notebook 10 |
| Judge / evals | your Q&A pairs with reference answers | `data/eval_set.jsonl` format |

## Rewrite the questions

This is where the real work is, and it's worth doing carefully:

1. **Start from the decision you'd make by hand.** "Would I reply to this?" is a better question than "Is
   this important?".
2. **Describe every option.** `"billing": "payments, invoices, refunds, charges"` is better than
   `"billing": None`.
3. **Add a `none` or `other` option** so Jev isn't forced to pick something that doesn't fit.
4. **Use `criteria` on `Noul` questions** to say exactly what counts as *yes*.
5. **Label 30-50 examples** of your own data and measure accuracy before you trust it. Every notebook
   shows how.
6. **Route low confidence to a human.** It's the cheapest way to make a classifier safe.

## Keep it safe

- Keep tools **read-only** until you've added a guard and a human-approval step ([notebook 07](../course/07_auto_mode_guardrails.ipynb)).
- Keep **hard rules in code** (phishing is never answered; SEV1 always pages).
- **Fail closed** when a check can't run.
