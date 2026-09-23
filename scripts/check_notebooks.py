"""Keyless repo checks, run in CI and before every commit.

    uv run python scripts/check_notebooks.py

1. Every notebook is valid nbformat.
2. The shared cells (provider config, helpers, agent loop) are byte-identical in every notebook that has them,
   so a fix to one is a fix to all. The loop is the teaching device: it must not drift.
3. Nothing that looks like an API key is committed anywhere (notebook outputs included).
4. Notebook code cells compile.
"""

import re
import sys
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted(ROOT.glob("[0-9][0-9]_*.ipynb"))
SHARED = {
    "config": "# --- Provider config: ONE OpenRouter key drives both brains",
    "helpers": "# --- Helpers used in every notebook",
    "loop": "def run_agent(user_query, tools, registry,",
}
SECRET = re.compile(r"(sk-or-v1-[0-9a-f]{20,}|sk-[A-Za-z0-9]{32,}|ghp_[A-Za-z0-9]{30,}|xox[bp]-[A-Za-z0-9-]{20,})")
problems = []

seen = {k: {} for k in SHARED}
for nb_path in NOTEBOOKS:
    nb = nbformat.read(nb_path, as_version=4)
    try:
        nbformat.validate(nb)
    except Exception as exc:  # noqa: BLE001
        problems.append(f"{nb_path.name}: invalid notebook ({exc})")
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        for key, marker in SHARED.items():
            if cell.source.startswith(marker):
                seen[key][nb_path.name] = cell.source
        src = "\n".join(line for line in cell.source.splitlines() if not line.lstrip().startswith(("%", "!")))
        try:
            compile(src, f"{nb_path.name}[{i}]", "exec")
        except SyntaxError as exc:
            problems.append(f"{nb_path.name} cell {i}: {exc}")

for key, by_nb in seen.items():
    variants = {}
    for name, src in by_nb.items():
        variants.setdefault(src, []).append(name)
    if len(variants) > 1:
        groups = sorted(variants.values(), key=len)
        problems.append(f"shared '{key}' cell differs: {groups[0]} vs the other {sum(map(len, groups[1:]))} notebooks")

for path in ROOT.rglob("*"):
    if path.is_dir() or ".venv" in path.parts or ".git" in path.parts or path.name == ".env":
        continue
    if path.suffix.lower() in {".png", ".jpg", ".lock"}:
        continue
    try:
        text = path.read_text(errors="ignore")
    except OSError:
        continue
    if SECRET.search(text):
        problems.append(f"{path.relative_to(ROOT)}: looks like it contains an API key")

print(f"checked {len(NOTEBOOKS)} notebooks; shared cells: " +
      ", ".join(f"{k} in {len(v)}" for k, v in seen.items()))
if problems:
    print("\n".join("FAIL " + p for p in problems))
    sys.exit(1)
print("OK")
