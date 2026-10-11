param([Int64]$Hwnd, [string]$Out, [int]$TopOnly = 0)
# 截某个窗口所在屏幕区域（CopyFromScreen；窗口要在前台才不会截到别的东西）。TopOnly > 0 时只截窗口顶部这么多像素（标签条）
Add-Type -AssemblyName System.Drawing
Add-Type @"
using System; using System.Runtime.InteropServices;
public class WS { [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r); }
"@
$r = New-Object WS+RECT
[WS]::GetWindowRect([IntPtr]$Hwnd, [ref]$r) | Out-Null
$w = $r.R - $r.L; $h = $r.B - $r.T
if ($TopOnly -gt 0) { $h = [Math]::Min($h, $TopOnly) }
$bmp = New-Object System.Drawing.Bitmap $w, $h
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($r.L, $r.T, 0, 0, $bmp.Size)
$bmp.Save($Out, [System.Drawing.Imaging.ImageFormat]::Png)
"rect: $($r.L),$($r.T) - $($r.R),$($r.B)  saved $w x $h"
