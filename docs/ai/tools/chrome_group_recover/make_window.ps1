# 把我的 4 个散标签（名字不含“属于”，含 抖音 / 视频号 / 小红书 / 哔哩哔哩）搬进一个新的独立窗口：先把抖音拖出去成新窗口，再把另外三个拖进去。
param([long]$Win = 37885880, [int]$NX = 1114, [int]$NY = 0, [int]$NW = 806, [int]$NH = 1032)
. "$PSScriptRoot/mouse_util.ps1"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type @'
using System;
using System.Runtime.InteropServices;
using System.Text;
using System.Collections.Generic;
public class W7 {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool MoveWindow(IntPtr h, int x, int y, int w, int hgt, bool repaint);
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r);
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
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
  [void][M]::SetForegroundWindow([IntPtr]$h); Start-Sleep -Milliseconds 500
}
function MyTab($w, $key) {
  $root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$w)
  $all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
  $hit = $null
  foreach ($e in $all) { try { if ($e.Current.ClassName -eq 'Tab') { $n = $e.Current.Name; if ($n -like "*$key*" -and $n -notlike '*属于*') { $hit = $e } } } catch {} }
  return $hit
}
$before = [W7]::Chrome()
[void][W7]::MoveWindow([IntPtr]$Win, 0, 0, 1113, 1032, $true)
Raise $Win
$src = MyTab $Win '抖音创作者中心'
if (-not $src) { Write-Output '没找到我的抖音散标签'; exit 1 }
$r = $src.Current.BoundingRectangle
$x0 = [int]($r.X + $r.Width / 2); $y0 = [int]($r.Y + $r.Height / 2)
$t0 = [long](Top-WindowAt $x0 $y0)
Write-Output ('抖音标签 ({0},{1}) 最上面窗口 {2}（应为 {3}）' -f $x0, $y0, $t0, $Win)
if ($t0 -ne $Win) { Write-Output '起点最上面窗口不是我的，不拖'; exit 2 }
Drag $x0 $y0 1500 700 30
Start-Sleep -Milliseconds 1500
$after = [W7]::Chrome()
$new = $after | Where-Object { $before -notcontains $_ }
Write-Output ('新窗口: ' + ($new -join ','))
if (-not $new) { Write-Output '没有出现新窗口'; exit 3 }
$nw = [long]($new | Select-Object -First 1)
[void][W7]::MoveWindow([IntPtr]$nw, $NX, $NY, $NW, $NH, $true)
Start-Sleep -Milliseconds 600
Write-Output ('新窗口 handle = {0}' -f $nw)
