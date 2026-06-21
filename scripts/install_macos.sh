#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
./.venv/bin/python -m pip install --upgrade pip
./.venv/bin/pip install -e .

if [ ! -f .env ]; then
  cp .env.example .env
  echo "Created .env. Add GEMINI_API_KEY before full AI use."
fi

echo "Install complete. Run: ./scripts/run_macos.sh"
