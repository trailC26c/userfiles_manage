$root = "C:\Users\tcnet"
$files = Get-ChildItem -Path $root -Recurse -File -ErrorAction SilentlyContinue |
    Sort-Object Length -Descending |
    Select-Object -First 50

$files | Select-Object `
    @{Name="SizeGB";Expression={"{0:N3}" -f ($_.Length / 1GB)}},
    @{Name="Created";Expression={$_.CreationTime}},
    @{Name="Modified";Expression={$_.LastWriteTime}},
    FullName

$TotalGB = ($files | Measure-Object -Property Length -Sum).Sum / 1GB
Write-Host ""
Write-Host "Total size of top 50 files: $([math]::Round($TotalGB,3)) GB"