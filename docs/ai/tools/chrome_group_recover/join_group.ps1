# 把我窗口里没进组的标签（名字不含“属于”）拖进我的组（名字含“AI时代PR审查讨论视频”的标签）；矩形实时读，起点 / 终点最上面的窗口不是我的就不拖。
param([long]$Window = 50009034, [string]$NameLike = "哔哩哔哩")
. "$PSScriptRoot/mouse_util.ps1"
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$h = [IntPtr]$Window
[void][M]::ShowWindow($h, 9)
[M]::keybd_event(0x12, 0, 0, 0); [M]::keybd_event(0x12, 0, 2, 0); Start-Sleep -Milliseconds 150
[void][M]::SetForegroundWindow($h); Start-Sleep -Milliseconds 500
$root = [System.Windows.Automation.AutomationElement]::FromHandle($h)
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
$src = $null; $dst = $null
foreach ($e in $all) {
  try {
    if ($e.Current.ClassName -ne "Tab") { continue }
    $nm = $e.Current.Name
    if ($nm -like "*$NameLike*" -and $nm -notlike '*属于*') { $src = $e }
    if ($nm -like '*AI时代PR审查讨论视频*' -and $nm -like '*属于*' -and -not $dst) { $dst = $e }
  } catch {}
}
if (-not $src -or -not $dst) { Write-Output "没找到源标签或组内标签"; exit 1 }
$rs = $src.Current.BoundingRectangle; $rd = $dst.Current.BoundingRectangle
$x0 = [int]($rs.X + $rs.Width / 2); $y0 = [int]($rs.Y + $rs.Height / 2)
$x1 = [int]($rd.X + $rd.Width / 2); $y1 = [int]($rd.Y + $rd.Height / 2)
$t0 = [long](Top-WindowAt $x0 $y0); $t1 = [long](Top-WindowAt $x1 $y1)
Write-Output ("源 ({0},{1}) 最上面窗口 {2}；终点 ({3},{4}) 最上面窗口 {5}" -f $x0, $y0, $t0, $x1, $y1, $t1)
if ($t0 -ne $Window -or $t1 -ne $Window) { Write-Output "起点或终点最上面的窗口不是我的窗口，不拖"; exit 2 }
Drag $x0 $y0 $x1 $y1 30
Start-Sleep -Milliseconds 800
Write-Output "已拖"
