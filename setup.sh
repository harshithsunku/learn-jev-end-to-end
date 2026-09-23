#!/usr/bin/env bash
# One-shot setup for Linux/macOS. Prefers uv; falls back to venv + pip.
set -euo pipefail
cd "$(dirname "$0")"

if command -v uv >/dev/null 2>&1; then
  echo "==> uv found: syncing (with the UI extra)"
  uv sync --extra ui
  RUN="uv run"
else
  echo "==> uv not found: using python -m venv + pip (install uv for faster setup: https://docs.astral.sh/uv/)"
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  pip install --upgrade pip >/dev/null
  pip install -r requirements.txt
  RUN=""
fi

if [ ! -f .env ]; then
  cp .env.example .env
  echo "==> created .env - paste your OpenRouter key into OPENAI_API_KEY, then re-run the doctor below"
fi

echo "==> checking your setup"
$RUN python scripts/doctor.py || true
echo
echo "Next:  ${RUN:+$RUN }jupyter lab     (open 01_hello_jev.ipynb)"
