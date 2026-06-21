$ErrorActionPreference = "Stop"

$project = Resolve-Path "."
$shortcutPath = Join-Path $env:APPDATA "Microsoft\Windows\Start Menu\Programs\Startup\JARVIS.lnk"
$target = Join-Path $project ".venv\Scripts\jarvis.exe"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = $target
$shortcut.WorkingDirectory = $project
$shortcut.WindowStyle = 7
$shortcut.Description = "Start JARVIS assistant on login"
$shortcut.Save()

Write-Host "Startup shortcut created at $shortcutPath"

