param([string]$Action = "front", [Int64]$Hwnd = 272565968, [Int64]$Back = 6035236)
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class W2 {
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int c);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern bool IsIconic(IntPtr h);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, uint flags, UIntPtr extra);
  [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
}
"@
$h = [IntPtr]$Hwnd
if ($Action -eq "front") {
  [W2]::ShowWindow($h, 9) | Out-Null          # SW_RESTORE
  [W2]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)   # Alt down（解除前置限制）
  [W2]::SetForegroundWindow($h) | Out-Null
  [W2]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)   # Alt up
  Start-Sleep -Milliseconds 600
  "front: iconic=" + [W2]::IsIconic($h) + " fg=" + ([W2]::GetForegroundWindow() -eq $h)
} else {
  [W2]::ShowWindow($h, 6) | Out-Null          # SW_MINIMIZE
  Start-Sleep -Milliseconds 300
  [W2]::keybd_event(0x12, 0, 0, [UIntPtr]::Zero)
  [W2]::SetForegroundWindow([IntPtr]$Back) | Out-Null
  [W2]::keybd_event(0x12, 0, 2, [UIntPtr]::Zero)
  "back: iconic=" + [W2]::IsIconic($h)
}
