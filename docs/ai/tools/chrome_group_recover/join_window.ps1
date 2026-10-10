# 把窗口 $From 里我的散标签（名字含 $Key、不含“属于”）拖进窗口 $To 的标签栏（落在 $To 里第一个标签的位置上）。
param([long]$From = 37885880, [long]$To = 990050, [string]$Key = '视频号助手')
. "$PSScriptRoot/mouse_util.ps1"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
function Raise($h) {
  [void][M]::ShowWindow([IntPtr]$h, 9)
  [M]::keybd_event(0x12, 0, 0, 0); [M]::keybd_event(0x12, 0, 2, 0); Start-Sleep -Milliseconds 150
  [void][M]::SetForegroundWindow([IntPtr]$h); Start-Sleep -Milliseconds 450
}
function Tabs($w) {
  $root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$w)
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  $o = @()
  foreach ($e in $all) { try { if ($e.Current.ClassName -eq 'Tab') { $o += [pscustomobject]@{N = $e.Current.Name; R = $e.Current.BoundingRectangle} } } catch {} }
  return $o
}
Raise $To
Raise $From
$s = Tabs $From | Where-Object { $_.N -like "*$Key*" -and $_.N -notlike '*属于*' } | Select-Object -Last 1
$d = Tabs $To | Sort-Object { $_.R.X } | Select-Object -First 1
if (-not $s -or -not $d) { Write-Output '没找到源标签或终点标签'; exit 1 }
$x0 = [int]($s.R.X + $s.R.Width / 2); $y0 = [int]($s.R.Y + $s.R.Height / 2)
$x1 = [int]($d.R.X + $d.R.Width * 0.7); $y1 = [int]($d.R.Y + $d.R.Height / 2)
$t0 = [long](Top-WindowAt $x0 $y0); $t1 = [long](Top-WindowAt $x1 $y1)
Write-Output ('{0}: 源 ({1},{2}) 最上面窗口 {3}（应为 {4}）；终点 ({5},{6}) 最上面窗口 {7}（应为 {8}）' -f $Key, $x0, $y0, $t0, $From, $x1, $y1, $t1, $To)
if ($t0 -ne $From -or $t1 -ne $To) { Write-Output '起点或终点最上面的窗口不对，不拖'; exit 2 }
Drag $x0 $y0 $x1 $y1 30
Start-Sleep -Milliseconds 1000
Write-Output '已拖'
