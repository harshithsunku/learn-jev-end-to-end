# Contributing

Thanks for helping people learn Jev. Contributions of every size are welcome: typo fixes, clearer
explanations, new use cases, better fixtures, translations.

## Ground rules

- **Pedagogy first.** Code is intentionally explicit. Don't replace the hand-rolled loop or helpers with a
  framework. The contrast is the lesson (framework versions belong in appendix cells).
- **Shared cells stay identical.** The provider config cell, the helpers cell and the `run_agent` loop are
  copied verbatim into every notebook. Change them everywhere at once; `scripts/check_notebooks.py` enforces it.
- **Keep tools safe.** Tools are read-only, sandboxed, or dry-run mocks. Anything that mutates state needs a
  guard *and* a human-approval path (see notebook 07). Never loosen a sandbox for convenience.
- **Measure.** A new use case ships with labeled fixture data in `data/` and an assertion on a *threshold*
  (never on an exact probability; Jev's outputs are probabilistic).
- **Math, counting and dates live in code**, not in Jev questions (see notebook 02, section 6).
- **No secrets, no real personal data.** Use `.example` / `.test` domains and documented fake credentials.

## Workflow

```bash
uv sync --extra ui
cp .env.example .env          # add your OpenRouter key
uv run python scripts/doctor.py
uv run jupyter lab            # edit
uv run python scripts/check_notebooks.py
uv run jupyter nbconvert --to notebook --execute --inplace NN_your_notebook.ipynb
```

Preview the docs site (it renders the notebooks too) with:

```bash
uv sync --extra docs
uv run mkdocs serve          # http://127.0.0.1:8000
uv run mkdocs build --strict # what CI runs; fails on broken links
```

Commit notebooks **with outputs**, so GitHub and the docs site show real results. Run `scripts/check_notebooks.py`
before committing; it fails if anything that looks like an API key appears in a notebook output.

## Adding a use case

1. Put labeled fixtures in `data/`.
2. Start from the closest notebook and paste the shared cells unchanged.
3. Show where Jev sits in the loop (router, guard, tool, gate or judge), not just a standalone call.
4. Measure it against the labels, route low-confidence cases somewhere safe, and print `SPEND` at the end.
5. Add a row to the use-case table in `README.md`.
