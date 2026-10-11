Add-Type @"
using System;
using System.Runtime.InteropServices;
public class M {
  [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
  [DllImport("user32.dll")] public static extern void mouse_event(int flags, int dx, int dy, int data, int extra);
  [DllImport("user32.dll")] public static extern IntPtr WindowFromPoint(POINT p);
  [DllImport("user32.dll")] public static extern IntPtr GetAncestor(IntPtr h, int flags);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, int flags, int extra);
  [StructLayout(LayoutKind.Sequential)] public struct POINT { public int X; public int Y; }
}
"@
function Top-WindowAt($x, $y) { $p = New-Object M+POINT; $p.X = $x; $p.Y = $y; $h = [M]::WindowFromPoint($p); return [M]::GetAncestor($h, 2) }
function Drag($x0, $y0, $x1, $y1, $steps = 25) {
  [void][M]::SetCursorPos($x0, $y0); Start-Sleep -Milliseconds 150
  [M]::mouse_event(0x0002, 0, 0, 0, 0); Start-Sleep -Milliseconds 150          # left down
  for ($i = 1; $i -le $steps; $i++) {
    $x = [int]($x0 + ($x1 - $x0) * $i / $steps); $y = [int]($y0 + ($y1 - $y0) * $i / $steps)
    [void][M]::SetCursorPos($x, $y); Start-Sleep -Milliseconds 30
  }
  Start-Sleep -Milliseconds 250
  [M]::mouse_event(0x0004, 0, 0, 0, 0); Start-Sleep -Milliseconds 300         # left up
}
