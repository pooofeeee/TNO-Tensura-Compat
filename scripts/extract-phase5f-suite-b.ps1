param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('MAGIC_WEAPON', 'HOLY_WEAPON', 'SOUL_EATER', 'ELEMENTAL_SLOTTING')]
    [string] $ExpectedFamily,

    [Parameter(Mandatory = $true)]
    [string] $ExpectedBoss,

    [Parameter(Mandatory = $true)]
    [int] $ExpectedCases
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE5F_SUITE_B '
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
            try { $content = $reader.ReadToEnd() }
            finally { $reader.Dispose() }
        }
        finally { $gzip.Dispose() }
    }
    finally { $stream.Dispose() }
}
else {
    $content = [IO.File]::ReadAllText($resolvedLog)
}

$records = [Collections.Generic.List[object]]::new()
foreach ($line in ($content -split "`r?`n")) {
    $markerIndex = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($markerIndex -lt 0) { continue }
    $json = $line.Substring($markerIndex + $marker.Length)
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json }
    catch { throw "Malformed Suite B JSON in ${resolvedLog}: $json" }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$caseStarts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$caseResults = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$caseErrors = @($records | Where-Object { $_.Value.kind -eq 'case_error' })
$suiteResults = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1) { throw "Expected one catalog record; found $($catalogs.Count)" }
$catalog = $catalogs[0].Value
if ($catalog.diagnostic) { throw 'Diagnostic output cannot be preserved as official Suite B evidence.' }
if ($catalog.TNO_family -ne $ExpectedFamily -or $catalog.APO_profile -ne 'NONE') {
    throw 'Capture does not use the requested TNO-only family/profile.'
}
if ($catalog.cases[0].boss -ne $ExpectedBoss) {
    throw "Expected boss $ExpectedBoss; found $($catalog.cases[0].boss)"
}
if ($catalog.shots_per_case -ne 10 -or $catalog.fixed_window_ticks -ne 200) {
    throw 'Capture does not use the locked 10-shot/200-tick protocol.'
}
if ($catalog.royal_arrow_mark_enabled -or -not $catalog.stage_fixture_only -or $catalog.production_balance_mutated) {
    throw 'Capture is not the locked Mark-disabled, fixture-only benchmark setup.'
}
if ($caseErrors.Count -ne 0) { throw "Capture contains $($caseErrors.Count) case_error record(s)." }
if ($caseStarts.Count -ne $ExpectedCases -or $caseResults.Count -ne $ExpectedCases) {
    throw "Expected $ExpectedCases complete cases; found $($caseStarts.Count) starts and $($caseResults.Count) results."
}
if ($suiteResults.Count -ne 1 -or $suiteResults[0].Value.status -ne 'complete' -or
    $suiteResults[0].Value.case_count -ne $ExpectedCases -or
    $suiteResults[0].Value.requested_case_count -ne $ExpectedCases) {
    throw 'Capture lacks one complete suite_result with the expected case count.'
}

$grouped = @($caseResults | Group-Object { "$($_.Value.level)|$($_.Value.level_mode)" })
foreach ($group in $grouped) {
    $stages = @($group.Group.Value.TNO_stage | Sort-Object -Unique)
    $expectedStages = @('Native', 'S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7')
    if ((Compare-Object $stages $expectedStages).Count -ne 0) {
        throw "Level profile $($group.Name) is missing one or more locked stages."
    }
    $traitPackages = @($group.Group | ForEach-Object {
        ConvertTo-Json -InputObject @($_.Value.traits) -Compress
    } | Sort-Object -Unique)
    if ($traitPackages.Count -ne 1) {
        throw "Level profile $($group.Name) changed L2 traits across stages."
    }
}

foreach ($case in $caseResults) {
    $value = $case.Value
    if ($value.status -ne 'ok' -or -not $value.l2_initialized -or
        -not $value.profile_clone_verified -or -not $value.tensura_l2h_scaling_marker -or
        $value.APO_profile -ne 'NONE' -or $value.TNO_family -ne $ExpectedFamily) {
        throw "Invalid case result at level $($value.level), stage $($value.TNO_stage)."
    }
    if ($value.shots_released -lt 1 -or $value.shots_released -gt 10) {
        throw "Invalid shot count at level $($value.level), stage $($value.TNO_stage): $($value.shots_released)"
    }
    if ($value.matching_Tensura_nullification_present -and $value.penetration_percentage_applied -ne 0) {
        throw "Nullification was not authoritative at level $($value.level), stage $($value.TNO_stage)."
    }
}

if ($rows.Count -lt ($caseResults | Measure-Object -Property hits_recorded -Sum).Sum) {
    throw 'Capture is missing machine-readable per-hit rows.'
}
foreach ($row in $rows) {
    if ($row.Value.l2_layer_bypassed_unexpectedly) {
        throw "Unexpected L2 bypass at level $($row.Value.level), stage $($row.Value.TNO_stage), hit $($row.Value.hit_index)."
    }
    if ($row.Value.crit) { throw 'TNO-only isolation unexpectedly recorded a critical hit.' }
}

if ($ExpectedFamily -eq 'ELEMENTAL_SLOTTING') {
    if ($catalog.engraving -ne 'tensura:slotting' -or
        $catalog.damage_source_id -ne 'tensura:earth_elemental' -or
        $catalog.slotting_element -ne 'EARTH' -or
        $catalog.slotting_core -ne 'tensura:element_core_earth' -or
        $catalog.slotting_capacity -ne 1 -or
        $catalog.arrow -ne 'not created by native Slotting release') {
        throw 'Elemental capture does not describe the locked one-Earth-core native Slotting path.'
    }
    $eventRows = 0
    foreach ($row in $rows) {
        $value = $row.Value
        if ($value.slotting_projectile_id -ne 'tensura:stone_shot' -or
            -not $value.slotting_owner_retained -or $value.royal_arrow_created -or
            [Math]::Abs([double]$value.physical_original_before_stage) -gt 0.0001 -or
            [Math]::Abs([double]$value.slotting_native_projectile_damage - 1.0) -gt 0.0001 -or
            -not $value.slotting_stage_scoped_to_native_projectile_damage) {
            throw "Invalid native Slotting projectile row at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }
        $expectedProjectileDamage = [double]$value.slotting_native_projectile_damage * [double]$value.stage_coefficient
        if ([Math]::Abs([double]$value.slotting_after_stage_projectile_damage - $expectedProjectileDamage) -gt 0.0001) {
            throw "Slotting Stage coefficient escaped its locked damage scope at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }
        if ($value.family_source_is_l2_magic) {
            throw "Installed Earth Elemental source unexpectedly carries the L2 magic tag at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }
        if ([double]$value.engraving_native_amount -gt 0.0001) {
            $eventRows++
            if (@($value.damage_source_ids) -notcontains 'tensura:earth_elemental' -or
                @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic') {
                throw "Elemental event row did not retain the installed Earth source/tags at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
            }
        }
        if ($value.matching_Tensura_nullification_present -and
            ([double]$value.damage_after_L2_processing -gt 0.0001 -or
             ([double]$value.engraving_native_amount -gt 0.0001 -and -not $value.nullification_authoritative))) {
            throw "Elemental nullification was not absolute at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }
    }
    if ($eventRows -eq 0) {
        Write-Warning 'This boss emitted no Earth Elemental event; retain family-level positive-control evidence before interpreting the capture.'
    }
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { [IO.Directory]::CreateDirectory((Join-Path (Get-Location) $parent)) | Out-Null }
$encoding = [Text.UTF8Encoding]::new($false)
[IO.File]::WriteAllLines(
    (Join-Path (Get-Location) $OutputPath),
    [string[]]($records | ForEach-Object { $_.Json }),
    $encoding
)

Write-Host "Preserved $ExpectedFamily / ${ExpectedBoss}: $($caseResults.Count) cases, $($rows.Count) per-hit rows, zero case errors -> $OutputPath"
