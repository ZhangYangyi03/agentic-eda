
$ErrorActionPreference="Continue"
$u="https://github.com/YosysHQ/oss-cad-suite-build/releases/download/2026-09-20/oss-cad-suite-windows-x64-20260920.tgz"; $d="D:\eda\oss-cad-suite.tgz"
$sw=[System.Diagnostics.Stopwatch]::StartNew()
try {
  $c=(New-Object System.Net.WebClient)
  $c.Headers.Add("User-Agent","probe")
  $c.DownloadFile($u,$d)
  "OK $((Get-Item $d).Length) bytes in $([int]$sw.Elapsed.TotalSeconds)s" | Out-File -Encoding utf8 D:\eda\download.status
} catch { "FAIL $($_.Exception.Message)" | Out-File -Encoding utf8 D:\eda\download.status }
