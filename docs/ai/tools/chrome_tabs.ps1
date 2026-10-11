param([string]$Select = "", [string]$Also = "", [string]$Front = "")
# 列出 Chrome 窗口和各窗口里的标签（UIA）；-Select <名字里的关键词> 选中那个标签；-Front <hwnd> 把窗口放前台
[Console]::OutputEncoding = [Text.Encoding]::UTF8
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
Add-Type @"
using System; using System.Runtime.InteropServices; using System.Text; using System.Collections.Generic;
public class WinEnum {
  public delegate bool EnumProc(IntPtr h, IntPtr l);
  [DllImport("user32.dll")] public static extern bool EnumWindows(EnumProc p, IntPtr l);
  [DllImport("user32.dll")] public static extern int GetClassName(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr h, StringBuilder s, int n);
  [DllImport("user32.dll")] public static extern bool IsWindowVisible(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  public static List<IntPtr> List() { var r = new List<IntPtr>(); EnumWindows((h,l)=>{ var sb=new StringBuilder(256); GetClassName(h,sb,256); if (sb.ToString()=="Chrome_WidgetWin_1" && IsWindowVisible(h)) r.Add(h); return true;}, IntPtr.Zero); return r; }
  public static string Title(IntPtr h) { var sb=new StringBuilder(512); GetWindowText(h,sb,512); return sb.ToString(); }
}
"@
if ($Front) {
  $h = [IntPtr][Int64]$Front
  [WinEnum]::ShowWindow($h, 9) | Out-Null
  [WinEnum]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
  [WinEnum]::SetForegroundWindow($h) | Out-Null
  [WinEnum]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
  Start-Sleep -Milliseconds 500
  "front: iconic=" + [WinEnum]::IsIconic($h) + " fg=" + ([WinEnum]::GetForegroundWindow() -eq $h)
  return
}
foreach ($h in [WinEnum]::List()) {
  $t = [WinEnum]::Title($h)
  "== hwnd " + [Int64]$h + " iconic=" + [WinEnum]::IsIconic($h) + " title=" + $t
  try {
    $el = [Windows.Automation.AutomationElement]::FromHandle($h)
    $cond = New-Object Windows.Automation.PropertyCondition([Windows.Automation.AutomationElement]::ControlTypeProperty, [Windows.Automation.ControlType]::TabItem)
    $tabs = $el.FindAll([Windows.Automation.TreeScope]::Descendants, $cond)
    foreach ($tab in $tabs) {
      $sel = ""
      try { $p = $tab.GetCurrentPattern([Windows.Automation.SelectionItemPattern]::Pattern); if ($p.Current.IsSelected) { $sel = "*" } } catch {}
      $name = $tab.Current.Name
      "   [" + $sel + "] " + $name
      if ($Select -and $name -like "*$Select*" -and (-not $Also -or $name -like "*$Also*")) {
        try { $tab.GetCurrentPattern([Windows.Automation.SelectionItemPattern]::Pattern).Select(); "      -> selected" } catch { "      -> select failed: " + $_.Exception.Message }
      }
    }
  } catch { "   UIA error: " + $_.Exception.Message }
}
