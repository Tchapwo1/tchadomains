# TchaDomains Windows Scheduled Task Setup
# Automatically registers a daily silent task to run the Alpha Dispatcher at 18:00 local time.

$TaskName = "TchaDomainsDailyAlphaDispatch"
$PythonPath = (Get-Command python).Source
$ProjectDir = "D:\Downloads\tchadomains"
$ScriptArgs = "-m src.cli.radar_cli --dispatch both"

Write-Host "⚡ Registering Windows Scheduled Task: $TaskName..." -ForegroundColor Cyan

# Action: Run Python inside project directory
$Action = New-ScheduledTaskAction -Execute $PythonPath -Argument $ScriptArgs -WorkingDirectory $ProjectDir

# Trigger: Every day at 18:00
$Trigger = New-ScheduledTaskTrigger -Daily -At "18:00"

# Settings: Allow on battery, restart on failure
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

# Unregister old task if it exists
Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false -ErrorAction SilentlyContinue

# Register new scheduled task
Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Description "TchaDomains Automated Daily Top 10 Drops Dispatch to Telegram"

Write-Host "✅ Scheduled Task '$TaskName' registered successfully!" -ForegroundColor Green
Write-Host "It will trigger every day at 18:00 to send your Top 10 AI and Fintech drops." -ForegroundColor Green
