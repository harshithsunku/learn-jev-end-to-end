# One-shot setup for Windows PowerShell. Prefers uv; falls back to venv + pip.
$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "==> uv found: syncing (with the UI extra)"
    uv sync --extra ui
    $run = "uv run"
} else {
    Write-Host "==> uv not found: using venv + pip (install uv for faster setup: https://docs.astral.sh/uv/)"
    python -m venv .venv
    . .\.venv\Scripts\Activate.ps1
    python -m pip install --upgrade pip | Out-Null
    pip install -r requirements.txt
    $run = ""
}

if (-not (Test-Path .env)) {
    Copy-Item .env.example .env
    Write-Host "==> created .env - paste your OpenRouter key into OPENAI_API_KEY, then re-run the doctor below"
}

Write-Host "==> checking your setup"
if ($run) { uv run python scripts/doctor.py } else { python scripts/doctor.py }
Write-Host ""
Write-Host "Next:  $run jupyter lab     (open 01_hello_jev.ipynb)"
