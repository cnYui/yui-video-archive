# 临时把 Chrome 窗口设为“总在最前”（Claude 桌面端在工具调用之间抢前台，会把 Chrome 完全盖住 → 页面 hidden、渲染冻结）。
# -Mode on：置顶并摆到屏幕内；-Mode off：取消置顶。on 时同时起一个 15 分钟后自动取消置顶的保险（untopmost_later.ps1）。
param([long]$Hwnd = 3082854, [string]$Mode = "on", [int]$X = 300, [int]$Y = 20, [int]$Wd = 1500, [int]$Ht = 1010)
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class TM {
  [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr after, int x, int y, int cx, int cy, uint flags);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr h, int cmd);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr h);
  [DllImport("user32.dll")] public static extern void keybd_event(byte vk, byte scan, int flags, int extra);
}
'@
$h = [IntPtr]$Hwnd
$HWND_TOPMOST = [IntPtr](-1); $HWND_NOTOPMOST = [IntPtr](-2)
if ($Mode -eq "on") {
  [void][TM]::ShowWindow($h, 9)
  [void][TM]::SetWindowPos($h, $HWND_TOPMOST, $X, $Y, $Wd, $Ht, 0x0040)
  [TM]::keybd_event(0x12, 0, 0, 0); [TM]::keybd_event(0x12, 0, 2, 0); Start-Sleep -Milliseconds 150
  [void][TM]::SetForegroundWindow($h)
  Start-Process powershell.exe -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-File", (Join-Path $PSScriptRoot "untopmost_later.ps1"), "-Hwnd", $Hwnd, "-Seconds", 900 -WindowStyle Hidden
  "topmost on, hwnd=$Hwnd at ($X,$Y) $Wd x $Ht（15 分钟后自动取消）"
} else {
  [void][TM]::SetWindowPos($h, $HWND_NOTOPMOST, 0, 0, 0, 0, 0x0003)
  "topmost off, hwnd=$Hwnd"
}
