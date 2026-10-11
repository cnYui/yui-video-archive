param([string]$Needle = "开源信息")
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
$root = [Windows.Automation.AutomationElement]::RootElement
# 顶层窗口：Chrome_WidgetWin_1
$cond = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ClassNameProperty, "Chrome_WidgetWin_1")
$wins = $root.FindAll([Windows.Automation.TreeScope]::Children, $cond)
foreach ($w in $wins) {
  $h = $w.Current.NativeWindowHandle
  $all = $w.FindAll([Windows.Automation.TreeScope]::Descendants, [Windows.Automation.Condition]::TrueCondition)
  $hits = @()
  foreach ($e in $all) {
    try {
      $n = $e.Current.Name
      if ($n -and $n -like "*$Needle*") { $hits += ($e.Current.ControlType.ProgrammaticName + " | " + $n + " | offscreen=" + $e.Current.IsOffscreen) }
    } catch {}
  }
  "== window hwnd=$h name=" + $w.Current.Name + " elements=" + $all.Count + " hits=" + $hits.Count
  $hits | Select-Object -First 12
}
