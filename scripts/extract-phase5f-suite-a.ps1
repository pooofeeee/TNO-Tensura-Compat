param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath,

    [Parameter(Mandatory = $true)]
    [string] $ExpectedBoss,

    [Parameter(Mandatory = $true)]
    [int] $ExpectedCases
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE5F_SUITE_A '
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path

if ($resolvedLog.EndsWith('.gz', [StringComparison]::OrdinalIgnoreCase)) {
    $stream = [IO.File]::OpenRead($resolvedLog)
    try {
        $gzip = [IO.Compression.GzipStream]::new(
            $stream,
            [IO.Compression.CompressionMode]::Decompress
        )
        try {
            $reader = [IO.StreamReader]::new($gzip)
            try {
                $content = $reader.ReadToEnd()
            }
            finally {
                $reader.Dispose()
            }
        }
        finally {
            $gzip.Dispose()
        }
    }
    finally {
        $stream.Dispose()
    }
}
else {
    $content = [IO.File]::ReadAllText($resolvedLog)
}

$records = [Collections.Generic.List[object]]::new()
foreach ($line in ($content -split "`r?`n")) {
    $markerIndex = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($markerIndex -lt 0) {
        continue
    }

    $json = $line.Substring($markerIndex + $marker.Length)
    if (-not $json.StartsWith('{')) {
        continue
    }

    try {
        $value = $json | ConvertFrom-Json
    }
    catch {
        throw "Malformed Suite A JSON in ${resolvedLog}: $json"
    }

    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$caseStarts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$caseResults = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$caseErrors = @($records | Where-Object { $_.Value.kind -eq 'case_error' })
$suiteResults = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1) {
    throw "Expected one catalog record; found $($catalogs.Count)"
}
if ($catalogs[0].Value.cases[0].boss -ne $ExpectedBoss) {
    throw "Expected boss $ExpectedBoss; found $($catalogs[0].Value.cases[0].boss)"
}
if ($catalogs[0].Value.APO_profile -ne 'ANCIENT_SINGLE_PROSPEROUS_SPECTRAL' -or
    $catalogs[0].Value.TNO_family -ne 'NONE' -or
    $catalogs[0].Value.TNO_stage -ne 'Native') {
    throw 'The capture does not use the locked APO-only profile.'
}
if ($catalogs[0].Value.shots_per_case -ne 10 -or
    $catalogs[0].Value.fixed_window_ticks -ne 200) {
    throw 'The capture does not use the locked 10-shot/200-tick protocol.'
}
if ($caseErrors.Count -ne 0) {
    throw "Capture contains $($caseErrors.Count) case_error record(s)."
}
if ($caseStarts.Count -ne $ExpectedCases -or $caseResults.Count -ne $ExpectedCases) {
    throw "Expected $ExpectedCases complete cases; found $($caseStarts.Count) starts and $($caseResults.Count) results."
}
if ($suiteResults.Count -ne 1 -or
    $suiteResults[0].Value.status -ne 'complete' -or
    $suiteResults[0].Value.case_count -ne $ExpectedCases -or
    $suiteResults[0].Value.requested_case_count -ne $ExpectedCases) {
    throw 'The capture does not contain one complete suite_result with the expected case count.'
}

foreach ($case in $caseResults) {
    if ($case.Value.status -ne 'ok' -or
        -not $case.Value.l2_initialized -or
        $case.Value.APO_profile -ne 'ANCIENT_SINGLE_PROSPEROUS_SPECTRAL' -or
        $case.Value.TNO_family -ne 'NONE' -or
        $case.Value.TNO_stage -ne 'Native') {
        throw "Invalid case result at level $($case.Value.level)."
    }
    if ($case.Value.shots_released -lt 1 -or $case.Value.shots_released -gt 10) {
        throw "Invalid released-shot count at level $($case.Value.level): $($case.Value.shots_released)"
    }
}

if ($rows.Count -lt ($caseResults | Measure-Object -Property hits_recorded -Sum).Sum) {
    throw 'Capture is missing machine-readable per-hit rows.'
}

$parent = Split-Path -Parent $OutputPath
if ($parent) {
    [IO.Directory]::CreateDirectory((Join-Path (Get-Location) $parent)) | Out-Null
}
$encoding = [Text.UTF8Encoding]::new($false)
[IO.File]::WriteAllLines(
    (Join-Path (Get-Location) $OutputPath),
    [string[]]($records | ForEach-Object { $_.Json }),
    $encoding
)

Write-Host "Preserved ${ExpectedBoss}: $($caseResults.Count) cases, $($rows.Count) per-hit rows, zero case errors -> $OutputPath"
