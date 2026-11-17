[CmdletBinding()]
param(
    [ValidateRange(1, 2147483647)]
    [int]$Seed = 20261116,
    [switch]$KeepArtifacts
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Get-FileManifest {
    [OutputType([object[]])]
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Root)
    $rootPath = [System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar)
    $files = @(Get-ChildItem -LiteralPath $rootPath -File -Recurse | Sort-Object FullName)
    $entries = @(
        foreach ($file in $files) {
            $relativePath = $file.FullName.Substring($rootPath.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar)
            [pscustomobject][ordered]@{
                path = $relativePath.Replace('\', '/')
                size_bytes = [long]$file.Length
                sha256 = (Get-FileHash -LiteralPath $file.FullName -Algorithm SHA256).Hash.ToLowerInvariant()
            }
        }
    )
    return $entries
}

function Test-FileManifest {
    [OutputType([bool])]
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Root, [Parameter(Mandatory)][object[]]$Expected)
    if (-not (Test-Path -LiteralPath $Root -PathType Container)) { return $false }
    $actual = @(Get-FileManifest -Root $Root)
    if ($actual.Count -ne $Expected.Count) { return $false }
    for ($index = 0; $index -lt $Expected.Count; $index++) {
        if ($actual[$index].path -cne $Expected[$index].path) { return $false }
        if ([long]$actual[$index].size_bytes -ne [long]$Expected[$index].size_bytes) { return $false }
        if ($actual[$index].sha256 -cne $Expected[$index].sha256) { return $false }
    }
    return $true
}

function Assert-PathWithinRoot {
    [CmdletBinding()]
    param([Parameter(Mandatory)][string]$Path, [Parameter(Mandatory)][string]$Root)
    $fullPath = [System.IO.Path]::GetFullPath($Path)
    $fullRoot = [System.IO.Path]::GetFullPath($Root).TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
    if (-not $fullPath.StartsWith($fullRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw 'Safety boundary violation: path is outside the isolated lab root.'
    }
}

$tempRoot = [System.IO.Path]::GetFullPath([System.IO.Path]::GetTempPath())
$labRoot = Join-Path $tempRoot ('sinayxa-issue-93-' + [guid]::NewGuid().ToString('N'))
$report = [ordered]@{
    schema_version = '1.0.0'
    issue = 93
    seed = $Seed
    status = 'FAIL'
    generated_at_utc = [DateTime]::UtcNow.ToString('o')
    isolation = [ordered]@{ temp_root = $tempRoot; lab_root = $labRoot; network_used = $false; external_services_used = $false; real_data_used = $false }
    checks = [ordered]@{}
    limits = @(
        'Filesystem-only simulation; no PostgreSQL export or restore was performed.',
        'No physical WORM/Object Lock guarantee was tested.',
        'Deletion reconciliation covers only the three directories managed by this run.',
        'No secure media erasure, external snapshots, provider backups, or production data were tested.'
    )
    artifacts_retained = [bool]$KeepArtifacts
}
try {
    New-Item -ItemType Directory -Path $labRoot -ErrorAction Stop | Out-Null
    $datasetRoot = Join-Path $labRoot 'dataset'
    $exportRoot = Join-Path $labRoot 'export'
    $exportPayloadRoot = Join-Path $exportRoot 'payload'
    $restoreRoot = Join-Path $labRoot 'restore'
    $restorePayloadRoot = Join-Path $restoreRoot 'payload'
    $tamperRoot = Join-Path $labRoot 'tamper'
    foreach ($directory in @($datasetRoot, $exportRoot, $restoreRoot, $tamperRoot)) {
        New-Item -ItemType Directory -Path $directory -ErrorAction Stop | Out-Null
    }
    $utf8 = [System.Text.UTF8Encoding]::new($false)
    foreach ($directory in @($datasetRoot, $exportRoot, $restoreRoot, $tamperRoot)) {
        Assert-PathWithinRoot -Path $directory -Root $labRoot
    }
    for ($index = 1; $index -le 3; $index++) {
        $fileName = 'synthetic-record-{0:D2}.json' -f $index
        $record = [ordered]@{
            record_id = 'SYN-{0:D4}' -f $index
            seed = $Seed
            sequence = $index
            synthetic = $true
            content = 'Deterministic synthetic evidence {0} / {1}' -f $Seed, $index
        }
        $filePath = Join-Path $datasetRoot $fileName
        Assert-PathWithinRoot -Path $filePath -Root $labRoot
        [System.IO.File]::WriteAllText($filePath, ($record | ConvertTo-Json -Depth 4), $utf8)
    }
    $manifest = @(Get-FileManifest -Root $datasetRoot)
    if ($manifest.Count -ne 3) { throw 'Expected exactly three synthetic records.' }
    $manifestDocument = [ordered]@{ manifest_version = '1.0.0'; seed = $Seed; hash_algorithm = 'SHA-256'; entries = $manifest }
    [System.IO.File]::WriteAllText((Join-Path $exportRoot 'manifest.json'), ($manifestDocument | ConvertTo-Json -Depth 8), $utf8)
    $report.checks.dataset_generation = 'PASS'
    $report.checks.manifest_sha256 = 'PASS'

    Copy-Item -LiteralPath $datasetRoot -Destination $exportPayloadRoot -Recurse -ErrorAction Stop
    $exportValid = Test-FileManifest -Root $exportPayloadRoot -Expected $manifest
    $report.checks.export_integrity = if ($exportValid) { 'PASS' } else { 'FAIL' }
    if (-not $exportValid) { throw 'Exported payload does not match the source manifest.' }

    Copy-Item -LiteralPath $exportPayloadRoot -Destination $restorePayloadRoot -Recurse -ErrorAction Stop
    $restoreValid = Test-FileManifest -Root $restorePayloadRoot -Expected $manifest
    $report.checks.restore_integrity = if ($restoreValid) { 'PASS' } else { 'FAIL' }
    if (-not $restoreValid) { throw 'Restored payload does not match the source manifest.' }

    Copy-Item -LiteralPath $restorePayloadRoot -Destination $tamperRoot -Recurse -ErrorAction Stop
    $tamperFile = Join-Path $tamperRoot 'synthetic-record-01.json'
    [System.IO.File]::AppendAllText($tamperFile, [Environment]::NewLine + 'TAMPERED', $utf8)
    $tamperDetected = -not (Test-FileManifest -Root $tamperRoot -Expected $manifest)
    $report.checks.tamper_detection = if ($tamperDetected) { 'PASS' } else { 'FAIL' }
    if (-not $tamperDetected) { throw 'Integrity validation failed to detect the intentional mutation.' }
    Remove-Item -LiteralPath $tamperRoot -Recurse -Force -ErrorAction Stop

    $managedCopies = @($datasetRoot, $exportPayloadRoot, $restorePayloadRoot)
    $deletionRequest = [ordered]@{
        request_id = 'SYNTHETIC-DELETE-001'
        object_paths = @($manifest | ForEach-Object { $_.path })
        managed_locations = @('dataset', 'export/payload', 'restore/payload')
        synthetic = $true
    }
    foreach ($managedRoot in $managedCopies) {
        foreach ($entry in $manifest) {
            $target = Join-Path $managedRoot ($entry.path.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
            Assert-PathWithinRoot -Path $target -Root $labRoot
            if (Test-Path -LiteralPath $target -PathType Leaf) { Remove-Item -LiteralPath $target -Force -ErrorAction Stop }
        }
    }
    $remaining = @(
        foreach ($managedRoot in $managedCopies) {
            foreach ($entry in $manifest) {
                $target = Join-Path $managedRoot ($entry.path.Replace('/', [System.IO.Path]::DirectorySeparatorChar))
                if (Test-Path -LiteralPath $target) {
                    [pscustomobject]@{
                        location = $managedRoot.Substring($labRoot.Length).TrimStart([System.IO.Path]::DirectorySeparatorChar)
                        path = $entry.path
                    }
                }
            }
        }
    )
    $report.checks.deletion_reconciliation = if ($remaining.Count -eq 0) { 'PASS' } else { 'FAIL' }
    $report.deletion_request = $deletionRequest
    $report.remaining_managed_copies = $remaining
    if ($remaining.Count -gt 0) { throw 'Deletion reconciliation found managed copies that remain.' }
    $report.status = 'PASS'
}
catch {
    $report.status = 'FAIL'
    $report.error = $_.Exception.Message
}
finally {
    if ($KeepArtifacts) {
        $report.checks.cleanup = 'NOT_RUN'
    }
    else {
        try {
            $fullLabRoot = [System.IO.Path]::GetFullPath($labRoot)
            $fullTempRoot = [System.IO.Path]::GetFullPath($tempRoot).TrimEnd([System.IO.Path]::DirectorySeparatorChar) + [System.IO.Path]::DirectorySeparatorChar
            if (-not $fullLabRoot.StartsWith($fullTempRoot, [System.StringComparison]::OrdinalIgnoreCase)) {
                throw 'Safety boundary violation: cleanup target is outside the system temporary directory.'
            }
            if (Test-Path -LiteralPath $fullLabRoot -PathType Container) {
                Remove-Item -LiteralPath $fullLabRoot -Recurse -Force -ErrorAction Stop
            }
            if (Test-Path -LiteralPath $fullLabRoot) {
                throw 'Temporary laboratory directory still exists after cleanup.'
            }
            $report.checks.cleanup = 'PASS'
        }
        catch {
            $report.checks.cleanup = 'FAIL'
            $report.status = 'FAIL'
            $report.cleanup_error = $_.Exception.Message
        }
    }
    $report.artifacts_retained = [bool](Test-Path -LiteralPath $labRoot -PathType Container)
}
$report | ConvertTo-Json -Depth 10 -Compress | Write-Output
if ($report.status -ne 'PASS') { exit 1 }
