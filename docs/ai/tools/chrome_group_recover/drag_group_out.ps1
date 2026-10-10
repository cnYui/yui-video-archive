# 把我的标签组（组名含 ✅短视频制作、3 个标签）整组拖出共用窗口，成为一个独立窗口（组 chip 往窗口内容区拖 = 新窗口）。
param([long]$Win = 3082854, [string]$GroupKey = '✅短视频制作', [int]$DropX = 900, [int]$DropY = 650, [int]$NX = 560, [int]$NY = 30, [int]$NW = 1340, [int]$NH = 940)
. "D:\大疆\docs\ai\tools\chrome_group_recover\mouse_util.ps1"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;
public class W8 {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hgt, bool repaint);
  public static List<long> Chrome() {
    var l = new List<long>();
    EnumWindows((h, p) => { var cn = new StringBuilder(256); GetClassName(h, cn, 256); if (cn.ToString() == "Chrome_WidgetWin_1" && IsWindowVisible(h)) { var t = new StringBuilder(512); GetWindowText(h, t, 512); if (t.Length > 0) l.Add((long)h); } return true; }, IntPtr.Zero);
    return l;
  }
}
'@
function Raise($h) {
  [void][M]::ShowWindow([IntPtr]$h, 9)
  [M]::keybd_event(0x12, 0, 0, 0); [M]::keybd_event(0x12, 0, 2, 0); Start-Sleep -Milliseconds 150
  [void][M]::SetForegroundWindow([IntPtr]$h); Start-Sleep -Milliseconds 600
}
function Chip($w, $key) {
  $root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$w)
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  foreach ($e in $all) { try { if ($e.Current.ClassName -eq 'TabGroupHeader' -and $e.Current.Name -like "*$key*") { return $e } } catch {} }
  return $null
}
$before = [W8]::Chrome()
Raise $Win
$chip = Chip $Win $GroupKey
if (-not $chip) { Write-Output '没找到我的组 chip'; exit 1 }
$r = $chip.Current.BoundingRectangle
$x0 = [int]($r.X + $r.Width / 2); $y0 = [int]($r.Y + $r.Height / 2)
$t0 = [long](Top-WindowAt $x0 $y0)
Write-Output ('组 chip ({0},{1}) 最上面窗口 {2}（应为 {3}）；名字：{4}' -f $x0, $y0, $t0, $Win, $chip.Current.Name)
if ($t0 -ne $Win) { Write-Output '起点最上面的窗口不是共用窗口，不拖'; exit 2 }
Drag $x0 $y0 $DropX $DropY 30
Start-Sleep -Milliseconds 1800
$after = [W8]::Chrome()
$new = $after | Where-Object { $before -notcontains $_ }
Write-Output ('新窗口: ' + ($new -join ','))
if (-not $new) { Write-Output '没有出现新窗口'; exit 3 }
$nw = [long]($new | Select-Object -First 1)
[void][W8]::MoveWindow([IntPtr]$nw, $NX, $NY, $NW, $NH, $true)
Start-Sleep -Milliseconds 600
Write-Output ('新窗口 handle = {0}' -f $nw)
