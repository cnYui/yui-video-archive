# 我的新标签组在窗口 $Grp 里：把那个窗口挪到左下 / 右下不挡我主窗口标签栏的位置，把组 chip 拖进主窗口 $Mine 的标签栏（落在最后一个标签右半部分）。
param([long]$Grp = 21567626, [long]$Win = 37885880)
. "$PSScriptRoot/mouse_util.ps1"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class W6 { [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hgt, bool repaint); }
'@
function Raise($h) {
  [void][M]::ShowWindow([IntPtr]$h, 9)
  [M]::keybd_event(0x12, 0, 0, 0); [M]::keybd_event(0x12, 0, 2, 0); Start-Sleep -Milliseconds 150
  [void][M]::SetForegroundWindow([IntPtr]$h); Start-Sleep -Milliseconds 500
}
function Rects($w) {
  $root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$w)
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  $out = @()
  foreach ($e in $all) { try { $cn = $e.Current.ClassName; if ($cn -eq 'Tab' -or $cn -eq 'TabGroupHeader') { $out += [pscustomobject]@{Cls = $cn; R = $e.Current.BoundingRectangle; Name = $e.Current.Name} } } catch {} }
  return $out
}
[void][W6]::MoveWindow([IntPtr]$Win, 0, 0, 1113, 1032, $true)
[void][W6]::MoveWindow([IntPtr]$Grp, 1000, 600, 900, 400, $true)
Start-Sleep -Milliseconds 500
Raise $Win
Raise $Grp
$chip = Rects $Grp | Where-Object { $_.Cls -eq 'TabGroupHeader' -and $_.Name -like '*AI时代PR审查讨论视频*' } | Select-Object -First 1
if (-not $chip) { Write-Output '没找到组 chip'; exit 1 }
$tabsMain = Rects $Win | Where-Object { $_.Cls -eq 'Tab' }
$last = $tabsMain | Sort-Object { $_.R.X } | Select-Object -Last 1
if (-not $last) { Write-Output '主窗口没有标签'; exit 1 }
$x0 = [int]($chip.R.X + $chip.R.Width / 2); $y0 = [int]($chip.R.Y + $chip.R.Height / 2)
$x1 = [int]($last.R.X + $last.R.Width * 0.8); $y1 = [int]($last.R.Y + $last.R.Height / 2)
$t0 = [long](Top-WindowAt $x0 $y0); $t1 = [long](Top-WindowAt $x1 $y1)
Write-Output ('chip ({0},{1}) 最上面窗口 {2}（应为 {3}）；终点 ({4},{5}) 最上面窗口 {6}（应为 {7}）' -f $x0, $y0, $t0, $Grp, $x1, $y1, $t1, $Win)
if ($t0 -ne $Grp -or $t1 -ne $Win) { Write-Output '起点或终点最上面的窗口不对，不拖'; exit 2 }
Drag $x0 $y0 $x1 $y1 30
Start-Sleep -Milliseconds 1000
Write-Output '已拖'
