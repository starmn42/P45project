$ErrorActionPreference = 'Stop'

$taskName = 'P45 Weekly Draw Update'
$toolsRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $toolsRoot '..\..')).Path
$updateCmd = Join-Path $toolsRoot 'P45 회차 업데이트.cmd'

if (-not $updateCmd -or -not (Test-Path -LiteralPath $updateCmd -PathType Leaf)) {
    throw "P45 update command not found: $updateCmd"
}

$action = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\cmd.exe" `
    -Argument "/d /c call `"$updateCmd`" scheduled" `
    -WorkingDirectory $projectRoot

$primaryAt = [datetime]::Today.AddHours(22).AddMinutes(30)
$backupAt = [datetime]::Today.AddHours(9)
$primaryTrigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Saturday -At $primaryAt
$backupTrigger = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -DaysOfWeek Sunday -At $backupAt

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

$userId = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
$principal = New-ScheduledTaskPrincipal `
    -UserId $userId `
    -LogonType Interactive `
    -RunLevel Limited

$task = New-ScheduledTask `
    -Action $action `
    -Trigger @($primaryTrigger, $backupTrigger) `
    -Settings $settings `
    -Principal $principal `
    -Description 'P45 official draw check: Saturday primary and Sunday backup. No research rule changes.'

Register-ScheduledTask -TaskName $taskName -InputObject $task -Force | Out-Null

$registered = Get-ScheduledTask -TaskName $taskName
$info = Get-ScheduledTaskInfo -TaskName $taskName
Write-Host ''
Write-Host 'P45 automatic update schedule installed.' -ForegroundColor Green
Write-Host "Task: $taskName"
Write-Host 'Primary: Saturday 22:30'
Write-Host 'Backup: Sunday 09:00'
Write-Host "Command: $updateCmd"
Write-Host "Next run: $($info.NextRunTime)"
Write-Host "State: $($registered.State)"
