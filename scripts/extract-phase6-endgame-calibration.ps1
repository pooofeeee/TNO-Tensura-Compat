param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('durability')]
    [string]$Mode
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_CALIBRATION '
$session = [System.Collections.Generic.List[object]]::new()

foreach ($line in Get-Content -LiteralPath $LogPath) {
    $markerIndex = $line.IndexOf($marker, [System.StringComparison]::Ordinal)
    if ($markerIndex -lt 0) { continue }
    $jsonText = $line.Substring($markerIndex + $marker.Length)
    try { $record = $jsonText | ConvertFrom-Json -Depth 100 }
    catch { throw "Invalid calibration JSON in ${LogPath}: $jsonText" }
    if ($record.kind -eq 'suite_start') {
        $session.Clear()
    }
    $session.Add($record)
}

if ($session.Count -eq 0) { throw "No calibration records found in $LogPath" }
$errors = @($session | Where-Object kind -eq 'case_error')
if ($errors.Count -ne 0) { throw "Calibration session contains $($errors.Count) case_error record(s)" }
$suite = @($session | Where-Object kind -eq 'suite_result')
if ($suite.Count -ne 1) { throw "Expected one suite_result, found $($suite.Count)" }
if ($suite[0].status -ne 'complete') { throw 'suite_result is not complete' }

switch ($Mode) {
    'durability' {
        $rows = @($session | Where-Object kind -eq 'durability_result')
        if ($rows.Count -ne 16) { throw "Expected 16 durability_result records, found $($rows.Count)" }
        if ([int]$suite[0].case_count -ne 16 -or [int]$suite[0].requested_case_count -ne 16) {
            throw 'Durability suite count mismatch'
        }
        $expectedBosses = @(
            'tensura_neb:luminous_valentine', 'tensura:hinata_sakaguchi',
            'tensura:gazel_dwargo', 'tensura:orc_disaster')
        $expectedLevels = @(300, 600, 800, 1000)
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($row in $rows) {
            if ($row.status -ne 'complete' -or $row.APO_profile -ne 'NONE') { throw "Invalid row status/profile: $($row | ConvertTo-Json -Compress)" }
            if ($expectedBosses -notcontains $row.boss -or $expectedLevels -notcontains [int]$row.L2_level) { throw "Unexpected target/level: $($row.boss) Lv$($row.L2_level)" }
            if (-not $keys.Add("$($row.boss)|$($row.L2_level)")) { throw "Duplicate target/level: $($row.boss) Lv$($row.L2_level)" }
            if ([math]::Abs([double]$row.generic_L2_health_modifier_amount - [double]$row.generic_L2_health_modifier_expected_amount) -gt 0.000001) { throw 'Generic L2 health formula mismatch' }
            if ([bool]$row.generic_L2_health_modifier_present_on_SHP) { throw 'L2 hostility_health unexpectedly appeared on SHP' }
            if ([math]::Abs([double]$row.Tensura_L2H_datapack_SHP_modifier_amount - [double]$row.Tensura_L2H_datapack_SHP_expected_amount) -gt 0.000001) { throw 'Tensura:L2Hostility SHP formula mismatch' }
        }
    }
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
$session | ForEach-Object { $_ | ConvertTo-Json -Depth 100 -Compress } | Set-Content -LiteralPath $OutputPath -Encoding utf8
Write-Output "Validated $Mode calibration: $($suite[0].case_count)/$($suite[0].requested_case_count) cases, 0 case_error"
Write-Output "Wrote $OutputPath"
