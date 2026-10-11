# 只选中含指定名字的标签（不前置窗口、不最小化）；-Window 可限定窗口句柄。用来把别的会话的标签选回去。
param([string]$Key, [long]$Window = 0)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::RootElement
$cond = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ClassNameProperty, "Chrome_WidgetWin_1")
$done = $false
foreach ($w in $root.FindAll([System.Windows.Automation.TreeScope]::Children, $cond)) {
  if ($Window -ne 0 -and $w.Current.NativeWindowHandle -ne $Window) { continue }
  $tc = New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, [System.Windows.Automation.ControlType]::TabItem)
  foreach ($t in $w.FindAll([System.Windows.Automation.TreeScope]::Descendants, $tc)) {
    if ($t.Current.Name -like "*$Key*") {
      try { $t.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select(); Write-Output ("已选中：" + $t.Current.Name); $done = $true } catch { Write-Output ("选中失败：" + $_.Exception.Message) }
      break
    }
  }
  if ($done) { break }
}
if (-not $done) { Write-Output "没找到含 '$Key' 的标签" }
