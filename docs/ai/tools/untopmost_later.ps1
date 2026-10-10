# 保险：N 秒后取消 Chrome 窗口的“总在最前”，不管我有没有收尾。
param([long]$Hwnd = 3082854, [int]$Seconds = 900)
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class UT { [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr h, IntPtr a, int x, int y, int cx, int cy, uint f); }
'@
Start-Sleep -Seconds $Seconds
[void][UT]::SetWindowPos([IntPtr]$Hwnd, [IntPtr](-2), 0, 0, 0, 0, 0x0003)
