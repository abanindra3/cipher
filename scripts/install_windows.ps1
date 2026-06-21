$ErrorActionPreference = "Stop"

Write-Host "Creating virtual environment..."
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\pip.exe install -e .

if (!(Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Created .env. Add GEMINI_API_KEY before full AI use."
}

Write-Host "Install complete. Run: .\.venv\Scripts\jarvis.exe"
