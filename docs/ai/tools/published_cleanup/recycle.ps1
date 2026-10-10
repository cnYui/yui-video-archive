param(
    [Parameter(Mandatory = $true)][string]$Manifest,   # build_manifest.py 出的 CSV
    [switch]$Execute,                                   # 不带 = 只校验不动手（dry-run）
    [string]$OnlyPathLike = '',                         # 试点：只处理路径里含这段字的行
    [string]$OnlyWork = '',
    [string]$BinRoot = 'D:\'                            # 文件在哪个盘，就数哪个盘的回收站
)
# 把清单里的文件逐个“移进回收站”（不是永久删除）。每个文件先核对字节数和修改时间（和清单不一致就跳过：说明
# 别的会话刚改过）；每处理完一个作品，数回收站文件夹里 $R* 实体文件增加的个数和字节数，对不上就停。
# 为什么不用 SHQueryRecycleBin：刚移完它的计数是滞后的（2026-10-05 试点时显示 +0 但文件其实在回收站里）。
# 回收站有容量上限（注册表 BitBucket\Volume\{卷 GUID}\MaxCapacity，MB）：装不下时 Windows 会静默永久清掉超出的部分，
# 动手前自己核对：清单总量 < 上限，且回收站里原来的东西 + 这次的 < 上限。
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName Microsoft.VisualBasic

function Get-Bin([string]$root) {
    $sid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
    $dir = Join-Path (Join-Path $root '$RECYCLE.BIN') $sid
    $n = 0; $b = 0L
    foreach ($f in [System.IO.Directory]::EnumerateFiles($dir)) {
        $name = [System.IO.Path]::GetFileName($f)
        if ($name.StartsWith('$R')) { $n++; $b += ([System.IO.FileInfo]::new($f)).Length }
    }
    [pscustomobject]@{ Items = $n; Bytes = $b }
}

$rows = Import-Csv -LiteralPath $Manifest -Encoding UTF8
if ($OnlyPathLike) { $rows = $rows | Where-Object { $_.path -like "*$OnlyPathLike*" } }
if ($OnlyWork)     { $rows = $rows | Where-Object { $_.work -eq $OnlyWork } }
$logPath = [System.IO.Path]::ChangeExtension($Manifest, $(if ($Execute) { 'recycle_log.tsv' } else { 'dryrun.tsv' }))
$log = [System.Collections.Generic.List[string]]::new()
$log.Add("work`tstatus`tbytes`tpath")

$binStart = Get-Bin $BinRoot
"mode: $(if ($Execute) {'EXECUTE (send to Recycle Bin)'} else {'DRY-RUN'})   rows: $($rows.Count)   bin before: items=$($binStart.Items) MB=$([math]::Round($binStart.Bytes/1MB,1))"

$okCount = 0; $okBytes = 0L; $skipCount = 0
foreach ($grp in ($rows | Group-Object work)) {
    $before = Get-Bin $BinRoot
    $movedHere = 0; $movedBytes = 0L
    foreach ($r in $grp.Group) {
        $p = $r.path
        if (-not (Test-Path -LiteralPath $p -PathType Leaf)) { $log.Add("$($r.work)`tMISSING`t0`t$p"); $skipCount++; continue }
        $fi = [System.IO.FileInfo]::new($p)
        $expSize = [int64]$r.size
        $expMtime = [int64][math]::Floor([double]$r.mtime)
        $curMtime = [DateTimeOffset]::new($fi.LastWriteTimeUtc).ToUnixTimeSeconds()
        if ($fi.Length -ne $expSize -or [math]::Abs($curMtime - $expMtime) -gt 2) {
            $log.Add("$($r.work)`tCHANGED-SKIP`t$($fi.Length)`t$p"); $skipCount++; continue
        }
        if ($Execute) {
            try {
                [Microsoft.VisualBasic.FileIO.FileSystem]::DeleteFile($p, 'OnlyErrorDialogs', 'SendToRecycleBin')
            } catch {
                $log.Add("$($r.work)`tERROR: $($_.Exception.Message)`t$expSize`t$p"); $skipCount++; continue
            }
            if (Test-Path -LiteralPath $p) { $log.Add("$($r.work)`tSTILL-EXISTS`t$expSize`t$p"); $skipCount++; continue }
        }
        $log.Add("$($r.work)`t$(if ($Execute) {'RECYCLED'} else {'WOULD-RECYCLE'})`t$expSize`t$p")
        $movedHere++; $movedBytes += $expSize
    }
    $okCount += $movedHere; $okBytes += $movedBytes
    if ($Execute) {
        $after = Get-Bin $BinRoot
        $dItems = $after.Items - $before.Items
        $dBytes = $after.Bytes - $before.Bytes
        $flag = if ($dItems -eq $movedHere -and $dBytes -eq $movedBytes) { 'ok' } else { 'MISMATCH' }
        "{0,-42} moved={1,4}  bin items +{2,4}  MB +{3,8:N1} (expected {4,8:N1}) [{5}]" -f $grp.Name, $movedHere, $dItems, ($dBytes/1MB), ($movedBytes/1MB), $flag
        if ($flag -ne 'ok') {
            [System.IO.File]::WriteAllLines($logPath, $log, [System.Text.UTF8Encoding]::new($false))
            throw "Recycle Bin accounting mismatch for '$($grp.Name)': moved $movedHere files but the bin grew by $dItems items. Stopping."
        }
    } else {
        "{0,-42} files={1,4}  MB={2,8:N1}" -f $grp.Name, $movedHere, ($movedBytes/1MB)
    }
}
[System.IO.File]::WriteAllLines($logPath, $log, [System.Text.UTF8Encoding]::new($false))
$binEnd = Get-Bin $BinRoot
"---- total files=$okCount  GiB=$([math]::Round($okBytes/1GB,2))  skipped=$skipCount  bin after: items=$($binEnd.Items) MB=$([math]::Round($binEnd.Bytes/1MB,1))"
"log: $logPath"
