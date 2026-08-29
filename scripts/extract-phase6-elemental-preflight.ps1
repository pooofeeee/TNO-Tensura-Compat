param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_ELEMENTAL_PREFLIGHT '
$schema = 'tno.phase6.elemental_preflight.v1'
$stages = [ordered]@{
    Native = 0.00
    S0 = 0.05
    S1 = 0.10
    S2 = 0.15
    S3 = 0.20
    S4 = 0.25
    S5 = 0.30
    S6 = 0.35
    S7 = 0.40
}

function Assert-Close([double] $Actual, [double] $Expected, [string] $Label) {
    if ([Math]::Abs($Actual - $Expected) -gt 0.0001) {
        throw "$Label mismatch: expected $Expected, found $Actual"
    }
}

$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$records = [Collections.Generic.List[object]]::new()
foreach ($line in [IO.File]::ReadLines($resolvedLog)) {
    $markerIndex = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($markerIndex -lt 0) { continue }
    $json = $line.Substring($markerIndex + $marker.Length)
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json }
    catch { throw "Malformed elemental preflight JSON in ${resolvedLog}: $json" }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

if ($records.Count -ne 101 -or @($records.Value.schema | Sort-Object -Unique) -ne $schema) {
    throw "Expected 101 records using schema $schema; found $($records.Count)."
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$stageResults = @($records | Where-Object { $_.Value.kind -eq 'stage_result' })
$suiteResults = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })
if ($catalogs.Count -ne 1 -or $rows.Count -ne 90 -or
    $stageResults.Count -ne 9 -or $suiteResults.Count -ne 1) {
    throw "Expected 1 catalog, 90 rows, 9 stage results, and 1 suite result."
}

$catalog = $catalogs[0].Value
if ($catalog.bow -ne 'royalvariations:royal_bow' -or
    $catalog.engraving -ne 'tensura:slotting' -or
    $catalog.slotting_level -ne 1 -or $catalog.slotting_capacity -ne 1 -or
    $catalog.inserted_core_count -ne 1 -or
    $catalog.inserted_core_id -ne 'tensura:element_core_earth' -or
    $catalog.shots_per_stage -ne 10 -or $catalog.apotheosis_loaded -or
    $catalog.l2hostility_loaded -or $catalog.royal_arrow_mark_enabled) {
    throw 'Catalog is not the locked Royal Bow / Slotting I / one-Earth-core positive control.'
}

foreach ($entry in $stages.GetEnumerator()) {
    $stageRows = @($rows | Where-Object { $_.Value.stage -eq $entry.Key })
    $stageSummary = @($stageResults | Where-Object { $_.Value.stage -eq $entry.Key })
    if ($stageRows.Count -ne 10 -or $stageSummary.Count -ne 1 -or
        (Compare-Object @($stageRows.Value.shot | Sort-Object) @(1..10)).Count -ne 0) {
        throw "Stage $($entry.Key) does not contain one summary and shots 1-10."
    }
    $multiplier = 1.0 + [double]$entry.Value
    Assert-Close $stageSummary[0].Value.stage_bonus $entry.Value "$($entry.Key) summary bonus"
    Assert-Close $stageSummary[0].Value.stage_multiplier $multiplier "$($entry.Key) summary multiplier"
    if ($stageSummary[0].Value.shots -ne 10 -or -not $stageSummary[0].Value.all_rows_validated) {
        throw "Stage $($entry.Key) summary is not complete."
    }

    foreach ($record in $stageRows) {
        $row = $record.Value
        if ($row.slotting_level -ne 1 -or $row.slotting_capacity -ne 1 -or
            $row.inserted_core_count -ne 1 -or
            $row.inserted_core_id -ne 'tensura:element_core_earth' -or
            $row.projectile_id -ne 'tensura:stone_shot' -or $row.projectile_count -ne 1 -or
            -not $row.projectile_owner_retained -or
            $row.damage_source_id -ne 'tensura:earth_elemental' -or
            $row.direct_entity_id -ne 'tensura:stone_shot' -or
            $row.elemental_event_count -ne 1 -or $row.base_physical_damage_event_count -ne 0 -or
            $row.cancelled -or $row.earth_resistance_present -or
            $row.spiritual_resistance_present -or $row.earth_nullification_present -or
            $row.spiritual_nullification_present -or $row.l2_loaded -or $row.l2_attached -or
            $row.royal_arrow_created -or $row.royal_arrow_mark_observed -or
            $row.slotting_capacity_changed -or $row.core_count_changed -or
            $row.base_physical_damage_stage_scaled) {
            throw "Invariant failure at $($entry.Key) shot $($row.shot)."
        }
        Assert-Close $row.native_elemental_coefficient 1.0 "$($entry.Key) native coefficient"
        Assert-Close $row.stage_coefficient $entry.Value "$($entry.Key) row coefficient"
        Assert-Close $row.stage_multiplier $multiplier "$($entry.Key) row multiplier"
        Assert-Close $row.expected_staged_elemental_amount $multiplier "$($entry.Key) expected amount"
        Assert-Close $row.applied_projectile_damage $multiplier "$($entry.Key) projectile amount"
        Assert-Close $row.actual_pre_defense_elemental_amount $multiplier "$($entry.Key) pre-defense amount"
        Assert-Close $row.incoming_highest_amount $multiplier "$($entry.Key) highest amount"
        Assert-Close $row.incoming_lowest_amount $multiplier "$($entry.Key) lowest amount"
        Assert-Close $row.damage_pre_amount $multiplier "$($entry.Key) pre amount"
        Assert-Close $row.actual_final_damage $multiplier "$($entry.Key) final damage"
    }
}

$suite = $suiteResults[0].Value
if ($suite.status -ne 'complete' -or $suite.classification -ne 'POSITIVE_CONTROL_PASS' -or
    $suite.case_count -ne 9 -or $suite.row_count -ne 90 -or $suite.shots_per_stage -ne 10 -or
    $suite.native_projectile -ne 'tensura:stone_shot' -or
    $suite.native_damage_source -ne 'tensura:earth_elemental' -or
    -not $suite.native_damage_observed -or -not $suite.all_curve_c_coefficients_matched -or
    $suite.slotting_capacity_changed -or $suite.core_count_changed -or
    $suite.base_physical_damage_stage_scaled -or $suite.resistance_nullification_or_l2_bypass) {
    throw 'Suite result is not a complete POSITIVE_CONTROL_PASS.'
}

$outputDirectory = Split-Path -Parent $OutputPath
if ($outputDirectory) { [IO.Directory]::CreateDirectory($outputDirectory) | Out-Null }
[IO.File]::WriteAllLines($OutputPath, @($records.Json), [Text.UTF8Encoding]::new($false))
Write-Output "Validated and wrote $($records.Count) records ($($rows.Count) rows) to $OutputPath"
