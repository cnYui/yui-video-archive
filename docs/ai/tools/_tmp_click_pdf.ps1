[Console]::OutputEncoding = [Text.Encoding]::UTF8
Add-Type -AssemblyName UIAutomationClient, UIAutomationTypes
Add-Type @"
using System; using System.Runtime.InteropServices;
public class Mouse {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(uint f, int x, int y, uint d, UIntPtr i);
  public static void Click(int x, int y) {
    SetCursorPos(x, y);
    System.Threading.Thread.Sleep(100);
    mouse_event(0x0002, 0, 0, 0, UIntPtr.Zero); // left down
    System.Threading.Thread.Sleep(50);
    mouse_event(0x0004, 0, 0, 0, UIntPtr.Zero); // left up
  }
}
"@

$el = [Windows.Automation.AutomationElement]::FromHandle([IntPtr]107351746)
$all = $el.FindAll([Windows.Automation.TreeScope]::Descendants, [Windows.Automation.Condition]::TrueCondition)
$pdfs = @()
foreach ($e in $all) {
  try {
    $ct = $e.Current.ControlType
    $n = $e.Current.Name
    if ($ct -eq [Windows.Automation.ControlType]::Hyperlink -and $n -like "*PDF*") {
      $rect = $e.Current.BoundingRectangle
      $pdfs += @{name=$n; x=[int]($rect.X + $rect.Width/2); y=[int]($rect.Y + $rect.Height/2); el=$e}
    }
  } catch {}
}

Write-Host "Found $($pdfs.Count) PDF links"
foreach ($p in $pdfs) {
  Write-Host ("  " + $p.name + " at x=" + $p.x + " y=" + $p.y)
}

# click each PDF link with a delay between
foreach ($p in $pdfs) {
  Write-Host ("Clicking: " + $p.name)
  [Mouse]::Click($p.x, $p.y)
  Start-Sleep -Milliseconds 1500
}
Write-Host "Done"
