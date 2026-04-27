$taskName = "BedtimeStoryGenerator"
$batFile  = Join-Path $PSScriptRoot "run_story.bat"

$action   = New-ScheduledTaskAction -Execute $batFile
$trigger  = New-ScheduledTaskTrigger -Daily -At "20:38"
$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1) `
    -MultipleInstances IgnoreNew

Register-ScheduledTask `
    -TaskName $taskName `
    -Action   $action `
    -Trigger  $trigger `
    -Settings $settings `
    -Force

Write-Host "Task '$taskName' scheduled to run daily at 8:00 PM."
Write-Host "Stories will be saved to: $(Join-Path (Split-Path $PSScriptRoot) 'stories')"
