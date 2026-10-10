# 只读：列出窗口里每个标签 / 标签组标题的矩形，拖标签时按这个取坐标。
param([long]$Window)
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root = [System.Windows.Automation.AutomationElement]::FromHandle([IntPtr]$Window)
$all = $root.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition)
foreach ($e in $all) {
  try {
    $cn = $e.Current.ClassName
    if ($cn -eq "Tab" -or $cn -eq "TabGroupHeader") {
      $r = $e.Current.BoundingRectangle
      Write-Output ("{0} | x{1}-{2} y{3}-{4} | 选中={5} | {6}" -f $cn, [int]$r.X, [int]($r.X + $r.Width), [int]$r.Y, [int]($r.Y + $r.Height), $(try { $e.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Current.IsSelected } catch { "" }), $e.Current.Name)
    }
  } catch {}
}
