# Windows 自带 OCR（Windows.Media.Ocr，WinRT）：逐行读一个列表文件里的图片路径，每张图输出识别到的行和位置（JSON Lines）。
# 用 Windows PowerShell 5.1 跑（PowerShell 7 调不了 WinRT 的这些类型）：
#   powershell.exe -NoProfile -ExecutionPolicy Bypass -File winocr.ps1 <列表.txt> <输出.jsonl> [语言 en-US]
param([string]$List, [string]$Out, [string]$Lang = "en-US", [double]$Scale = 2.0)
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$null = [Windows.Media.Ocr.OcrEngine, Windows.Foundation, ContentType = WindowsRuntime]
$null = [Windows.Graphics.Imaging.BitmapDecoder, Windows.Graphics.Imaging, ContentType = WindowsRuntime]
$null = [Windows.Storage.StorageFile, Windows.Storage, ContentType = WindowsRuntime]
$null = [Windows.Globalization.Language, Windows.Globalization, ContentType = WindowsRuntime]
$asTask = ([System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object { $_.Name -eq 'AsTask' -and $_.GetParameters().Count -eq 1 -and $_.GetParameters()[0].ParameterType.Name -eq 'IAsyncOperation`1' })[0]
function Await($op, [Type]$t) { $task = $asTask.MakeGenericMethod($t).Invoke($null, @($op)); $task.Wait(-1) | Out-Null; $task.Result }
$lg = New-Object Windows.Globalization.Language $Lang
$engine = [Windows.Media.Ocr.OcrEngine]::TryCreateFromLanguage($lg)
if ($null -eq $engine) { Write-Error "no OCR engine for $Lang"; exit 2 }
$sw = New-Object System.IO.StreamWriter($Out, $false, (New-Object System.Text.UTF8Encoding($false)))
foreach ($path in [System.IO.File]::ReadAllLines($List)) {
  if (-not $path) { continue }
  $file = Await ([Windows.Storage.StorageFile]::GetFileFromPathAsync($path)) ([Windows.Storage.StorageFile])
  $stream = Await ($file.OpenAsync([Windows.Storage.FileAccessMode]::Read)) ([Windows.Storage.Streams.IRandomAccessStream])
  $dec = Await ([Windows.Graphics.Imaging.BitmapDecoder]::CreateAsync($stream)) ([Windows.Graphics.Imaging.BitmapDecoder])
  # 先放大再识别：小字（画面缩小时 9–10 px 的邮箱）放大两倍才认得出
  $tf = New-Object Windows.Graphics.Imaging.BitmapTransform
  $tf.ScaledWidth = [uint32]($dec.PixelWidth * $Scale); $tf.ScaledHeight = [uint32]($dec.PixelHeight * $Scale)
  $tf.InterpolationMode = [Windows.Graphics.Imaging.BitmapInterpolationMode]::Cubic
  $bmp = Await ($dec.GetSoftwareBitmapAsync([Windows.Graphics.Imaging.BitmapPixelFormat]::Bgra8, [Windows.Graphics.Imaging.BitmapAlphaMode]::Premultiplied, $tf, [Windows.Graphics.Imaging.ExifOrientationMode]::IgnoreExifOrientation, [Windows.Graphics.Imaging.ColorManagementMode]::DoNotColorManage)) ([Windows.Graphics.Imaging.SoftwareBitmap])
  $res = Await ($engine.RecognizeAsync($bmp)) ([Windows.Media.Ocr.OcrResult])
  $lines = @()
  foreach ($ln in $res.Lines) {
    $xs = @(); $ys = @(); $x2 = @(); $y2 = @()
    foreach ($w in $ln.Words) { $r = $w.BoundingRect; $xs += $r.X; $ys += $r.Y; $x2 += ($r.X + $r.Width); $y2 += ($r.Y + $r.Height) }
    $lines += [pscustomobject]@{ t = $ln.Text; b = @([int](($xs | Measure-Object -Minimum).Minimum / $Scale), [int](($ys | Measure-Object -Minimum).Minimum / $Scale), [int](($x2 | Measure-Object -Maximum).Maximum / $Scale), [int](($y2 | Measure-Object -Maximum).Maximum / $Scale)) }
  }
  $sw.WriteLine((@{ p = $path; lines = $lines } | ConvertTo-Json -Compress -Depth 5))
  $stream.Dispose()
}
$sw.Close()
