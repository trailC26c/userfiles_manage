#C:\Windows\System32\WindowsPowerShell\v1.0
#C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Users\janec\Python\backup_userfiles.ps1"
#Set-ExecutionPolicy RemoteSigned -Scope Process

# --- CONFIGURATION ---
$Source = "C:\Users\tcnet"
$Destination = "E:\hp_spectre backup 2026"
$MinDate = [datetime]"2026-01-01" # Target date filter

# SIMULATION MODE SWITCH
# 1 = Simulation Only (Preview mode, no files are written)
# 0 = Actual Backup (Files will be written/overwritten)
$SimulationMode = 0
# ---------------------

# Start precision timer
$Stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$StartTime = [datetime]::Now

# Generate dynamic log file name with datestamp
$DateStamp = Get-Date -Format "yyyyMMdd_HHmmss"
$LogFileName = "backup_summary_$DateStamp.txt"

$ScriptDir = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
if ([string]::IsNullOrEmpty($ScriptDir)) { $ScriptDir = $pwd.Path }
$LogFilePath = Join-Path -Path $ScriptDir -ChildPath $LogFileName

# 1. SCANNING TARGET ITEMS
if ($SimulationMode -eq 1) {
    Write-Host "[SIMULATION MODE ENABLED] Previewing backup process..." -ForegroundColor Yellow
}
Write-Host "Scanning your target items for matching files..." -ForegroundColor Cyan

# Full expanded target list with mixed relative and absolute paths
$UserTargets = @(
    '.thinkorswim',
    '.vscode',
    'Contacts',
    'Desktop',
    'Documents',
    'Downloads',
    'Music',
    'OneDrive',
    'Pictures',
    'Python',
    'temp',
    'Videos',
    'exiftool',
    '.python_history',
    'Notepad++',
    'vscode',
    'TOS_Data_Local',
    'QuantTerminal',
    'TOS',
    'Ableton',
    'Muse Hub',
    'HOC5',
    "C:\Jane's Document",
    "C:\China Assets",
    "C:\Lama"
)

$FilesToCopy = [System.Collections.Generic.List[PSCustomObject]]::new()
$FoundItems = [System.Collections.Generic.HashSet[string]]::new()

foreach ($Target in $UserTargets) {
    # SMART PATH LOGIC: Accommodate any drive letter or absolute paths safely
    if ([System.IO.Path]::IsPathRooted($Target)) {
        $TargetPath = $Target
        # Dynamically set base source to the item's immediate parent directory 
        # to accurately preserve its folder structure under the backup destination folder
        $BaseSource = Split-Path -Parent -Path $TargetPath
    } else {
        $TargetPath = Join-Path -Path $Source -ChildPath $Target
        $BaseSource = $Source
    }

    if (Test-Path -Path $TargetPath) {
        if ((Get-Item -Path $TargetPath) -is [System.IO.DirectoryInfo]) {
            # Target is a folder: scan recursively
            $FoundFiles = Get-ChildItem -Path $TargetPath -Recurse -File -ErrorAction SilentlyContinue | 
                           Where-Object { $_.LastWriteTime -ge $MinDate }
            
            foreach ($File in $FoundFiles) {
                # Store the file along with its specific root source directory boundary
                $FilesToCopy.Add([PSCustomObject]@{ File = $File; BaseSource = $BaseSource })
                [void]$FoundItems.Add($TargetPath)
            }
        } else {
            # Target is a single file: check date filter directly
            $File = Get-Item -Path $TargetPath
            if ($File.LastWriteTime -ge $MinDate) {
                $FilesToCopy.Add([PSCustomObject]@{ File = $File; BaseSource = $BaseSource })
                [void]$FoundItems.Add($TargetPath)
            }
        }
    }
}

# Print the list of items being processed
Write-Host "`nTarget Items to be Processed:" -ForegroundColor Cyan
foreach ($Item in $FoundItems) {
    Write-Host " -> $Item" -ForegroundColor Gray
}

# Calculate total size safely using direct property unrolling
$TotalBytes = ($FilesToCopy.File | Measure-Object -Property Length -Sum).Sum
if ($null -eq $TotalBytes) { $TotalBytes = 0 }
$TotalGB = [math]::Round($TotalBytes / 1GB, 2)

$ModeLabel = if ($SimulationMode -eq 1) { "to simulate" } else { "to copy" }
Write-Host "`nTotal user data ${ModeLabel}: $TotalGB GB ($($FilesToCopy.Count) files)`n" -ForegroundColor Green

# 2. PROCESSING FILES & TRACKING OVERWRITES
$CopiedBytes = 0
$Counter = 0
$ProcessedFilesList = [System.Collections.Generic.List[string]]::new()

foreach ($Item in $FilesToCopy) {
    $Counter++
    $File = $Item.File
    $BaseSource = $Item.BaseSource
    
    # Construct dynamic target paths cleanly based on the base file layout structure
    # FIXED: Trim leading slashes from relative path to avoid double-slashes during Join-Path
    $RelativePath = $File.FullName.Substring($BaseSource.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar)
    $TargetFilePath = Join-Path -Path $Destination -ChildPath $RelativePath
    $TargetFolder = Split-Path -Path $TargetFilePath

    # Determine actions based on existence and timestamp differences
    $DoCopy = $true
    $FileStatus = "New File"

    if (Test-Path -Path $TargetFilePath) {
        $TargetFile = Get-Item -Path $TargetFilePath
        if ($File.LastWriteTime -le $TargetFile.LastWriteTime) {
            $DoCopy = $false 
        } else {
            $FileStatus = "Updated/Newer (Overwrite)"
        }
    }

    if ($DoCopy) {
        $ProcessedFilesList.Add("[$FileStatus] $($File.FullName)")

        # Execute file copy only if Simulation Mode is OFF
        if ($SimulationMode -eq 0) {
            try {
                if (!(Test-Path -Path $TargetFolder)) {
                    New-Item -ItemType Directory -Path $TargetFolder -Force | Out-Null
                }
                Copy-Item -Path $File.FullName -Destination $TargetFilePath -Force -Container -ErrorAction SilentlyContinue
                Get-Acl -Path $File.FullName | Set-Acl -Path $TargetFilePath -ErrorAction SilentlyContinue
                (Get-Item $TargetFilePath).LastWriteTime = $File.LastWriteTime
            } catch {
                continue 
            }
        }
    }

    # Update progress metrics
    $CopiedBytes += $File.Length
    
    # FIXED: Added logic validation guard against 0 total bytes to prevent crashing divide-by-zero math errors
    if ($TotalBytes -gt 0) {
        $Percent = [math]::Round(($CopiedBytes / $TotalBytes) * 100, 1)
    } else {
        $Percent = 100.0
    }
    $CurrentGB = [math]::Round($CopiedBytes / 1GB, 2)

    # Calculate Time Remaining with safe fallback boundaries
    $ElapsedTime = [datetime]::Now - $StartTime
    $SafeSecondsRemaining = 0
    $SecondsRemainingString = "Calculating..."

    if ($CopiedBytes -gt 0) {
        # FIXED: Ensure $TotalBytes comparison logic handles empty states properly
        if ($TotalBytes -le $CopiedBytes) {
            $SecondsRemainingString = "00:00:00"
        } else {
            $CalculatedSeconds = ($ElapsedTime.TotalSeconds / $CopiedBytes) * ($TotalBytes - $CopiedBytes)
            if ($CalculatedSeconds -gt 0) {
                $SafeSecondsRemaining = [int]$CalculatedSeconds
                $TimeRemaining = [Timespan]::FromSeconds($SafeSecondsRemaining)
                $SecondsRemainingString = "{0:hh\:mm\:ss}" -f $TimeRemaining
            } else {
                $SafeSecondsRemaining = 0
                $SecondsRemainingString = "00:00:00"
            }
        }
    } else {
        # If no bytes have been copied yet and there's nothing to copy, immediately clear timer string
        if ($TotalBytes -eq 0) { $SecondsRemainingString = "00:00:00" }
    }

    # FIXED: Ensure $Percent never exceeds 100 or drops below 0 to prevent Write-Progress UI rendering errors
    $SafePercent = [math]::Max(0, [math]::Min(100, $Percent))

    # Display dynamic PowerShell progress bar
    $ActivityText = if ($SimulationMode -eq 1) { "SIMULATING backup to $Destination" } else { "Backing up files to $Destination" }
    Write-Progress -Activity $ActivityText `
                   -Status "Progress: $SafePercent% ($CurrentGB GB of $TotalGB GB)" `
                   -PercentComplete $SafePercent `
                   -SecondsRemaining $SafeSecondsRemaining `
                   -CurrentOperation "Time Left: $SecondsRemainingString | Processing: $($File.Name)"
}

# Clear progress bar
Write-Progress -Activity "Completing" -Completed

# Stop the timer
$Stopwatch.Stop()
$ExecutionTime = $Stopwatch.Elapsed.ToString('hh\:mm\:ss\.ff')

# 3. GENERATING LOG SUMMARY FILE
$LogContent = [System.Collections.Generic.List[string]]::new()
$LogContent.Add("==================================================")
$LogContent.Add("BACKUP RUN SUMMARY")
$LogContent.Add("Date: $([datetime]::Now.ToString('yyyy-MM-dd HH:mm:ss'))")
$LogContent.Add("Mode: $(if ($SimulationMode -eq 1) { 'SIMULATION (No changes made)' } else { 'LIVE BACKUP' })")
$LogContent.Add("Execution Time: $ExecutionTime")
$LogContent.Add("Total Data Found: $TotalGB GB ($($FilesToCopy.Count) files)")
$LogContent.Add("==================================================`n")

$LogContent.Add("Processed Items:")
foreach ($Item in $FoundItems) { $LogContent.Add(" -> $Item") }
$LogContent.Add("`nProcessed Files (New or Overwritten):")

if ($ProcessedFilesList.Count -gt 0) {
    foreach ($LoggedFile in $ProcessedFilesList) { $LogContent.Add(" -> $LoggedFile") }
} else {
    $LogContent.Add(" -> None (All destination files are up to date)")
}

# Write summary to file silently
$LogContent | Out-File -FilePath $LogFilePath -Encoding utf8

# 4. FINAL STATUS & AUDIO ALERT
if ($SimulationMode -eq 1) {
    Write-Host "`nSimulation completed! No data was written." -ForegroundColor Yellow
} else {
    Write-Host "`nBackup completed successfully!" -ForegroundColor Green
}

Write-Host "Total Execution Time: $ExecutionTime" -ForegroundColor Cyan
Write-Host "Summary log saved to: $LogFilePath" -ForegroundColor Cyan

# Audio alert chimes
# FIXED: Wrapped in try/catch because [console]::Beep fails on certain headless servers or SSH environments
try {
    [console]::Beep(440, 150)
    [console]::Beep(554, 150)
    [console]::Beep(659, 150)
    [console]::Beep(880, 300)
} catch {}

Read-Host "`nPress Enter to exit"
