param([long]$Window = 37885880)
. "$PSScriptRoot/mouse_util.ps1"
$h = [IntPtr]$Window
[void][M]::ShowWindow($h, 9)
[M]::keybd_event(0x12, 0, 0, 0); [M]::keybd_event(0x12, 0, 2, 0); Start-Sleep -Milliseconds 150
[void][M]::SetForegroundWindow($h); Start-Sleep -Milliseconds 500
Write-Output ("raised {0}; top at (300,25) = {1}" -f $Window, [long](Top-WindowAt 300 25))
