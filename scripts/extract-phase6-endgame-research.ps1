param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('MAGIC_WEAPON', 'HOLY_WEAPON', 'SOUL_EATER', 'ELEMENTAL_SLOTTING', 'ENERGY_STEAL', 'SEVERANCE')]
    [string] $ExpectedFamily
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_ENDGAME_RESEARCH '
$content = [IO.File]::ReadAllText((Resolve-Path -LiteralPath $LogPath).Path)
$records = [Collections.Generic.List[object]]::new()

foreach ($line in ($content -split "`r?`n")) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -lt 0) { continue }
    $json = $line.Substring($index + $marker.Length)
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json -Depth 100 }
    catch { throw "Malformed Phase 6 endgame JSON: $json" }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$cases = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -eq 'case_error' })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1) { throw "Expected one catalog; found $($catalogs.Count)." }
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) case_error record(s)." }
if ($cases.Count -ne 32 -or $rows.Count -ne 320) {
    throw "Expected 32 cases and 320 rows; found $($cases.Count) and $($rows.Count)."
}
if ($suites.Count -ne 1 -or $suites[0].Value.status -ne 'complete' -or
    $suites[0].Value.case_count -ne 32 -or $suites[0].Value.requested_case_count -ne 32) {
    throw 'Capture lacks one complete 32-case suite_result.'
}

$catalog = $catalogs[0].Value
if ($catalog.suite -ne 'PHASE6_TNO_ENDGAME_RESEARCH' -or
    $catalog.TNO_family -ne $ExpectedFamily -or $catalog.APO_profile -ne 'NONE' -or
    $catalog.stage_fixture_only -or -not $catalog.production_stage_observation -or
    $catalog.production_balance_mutated -or $catalog.production_combat_mutated -or
    $catalog.shots_per_case -ne 10 -or $catalog.fixed_window_ticks -ne 200 -or
    $catalog.cases[0].boss -ne 'tensura:orc_disaster') {
    throw 'Catalog does not describe the locked TNO-only production observation protocol.'
}

$expectedStages = @('S0','S1','S2','S3','S4','S5','S6','S7')
$expectedLevels = @(300,600,800,1000)
$expectedEp = @{ S0=1000; S1=41500; S2=207500; S3=830000; S4=1245000; S5=1660000; S6=2075000; S7=2490000 }
$expectedTraits = @{
    300 = @('l2hostility:dementor=1','l2hostility:drain=2','l2hostility:regenerate=2','l2hostility:tank=5','l2hostility:wither=1')
    600 = @('l2hostility:adaptive=3','l2hostility:dementor=1','l2hostility:drain=2','l2hostility:regenerate=4','l2hostility:tank=5','l2hostility:wither=1')
    800 = @('l2hostility:adaptive=5','l2hostility:dementor=1','l2hostility:drain=2','l2hostility:regenerate=5','l2hostility:tank=5','l2hostility:wither=1')
    1000 = @('l2hostility:adaptive=5','l2hostility:dementor=1','l2hostility:dispell=2','l2hostility:drain=2','l2hostility:regenerate=5','l2hostility:tank=5','l2hostility:wither=1')
}

foreach ($level in $expectedLevels) {
    $levelCases = @($cases | Where-Object { $_.Value.level -eq $level })
    $actualStages = @($levelCases.Value.TNO_stage | Sort-Object -Unique)
    if ($levelCases.Count -ne 8 -or (Compare-Object $actualStages $expectedStages).Count -ne 0) {
        throw "Lv$level does not contain the exact S0-S7 matrix."
    }
    $traitPackages = @($levelCases | ForEach-Object {
        @($_.Value.traits | ForEach-Object { "$($_.id)=$($_.rank)" } | Sort-Object) -join ';'
    } | Sort-Object -Unique)
    $expectedPackage = @($expectedTraits[$level] | Sort-Object) -join ';'
    if ($traitPackages.Count -ne 1 -or $traitPackages[0] -ne $expectedPackage) {
        throw "Lv$level profile differs from the accepted strongest-legal artifact."
    }
}

foreach ($case in $cases) {
    $value = $case.Value
    if ($value.status -ne 'ok' -or $value.boss -ne 'tensura:orc_disaster' -or
        $value.level -notin $expectedLevels -or $value.TNO_stage -notin $expectedStages -or
        $value.native_gear_EP -ne $expectedEp[$value.TNO_stage] -or
        $value.resolved_production_stage -ne $value.TNO_stage -or
        -not $value.l2_initialized -or -not $value.legal_profile -or
        -not $value.strongest_legal_endgame_profile -or -not $value.profile_clone_verified -or
        $value.APO_profile -ne 'NONE' -or $value.TNO_family -ne $ExpectedFamily -or
        $value.shots_released -ne 10 -or $value.hits_recorded -ne 10) {
        throw "Invalid case invariant at Lv$($value.level) $($value.TNO_stage)."
    }
}

$allowedFailures = @(
    'NONE','TENSURA_RESISTANCE','TENSURA_NULLIFICATION','L2_MITIGATION',
    'L2_ADMISSION_VETO','L2_PROJECTILE_REJECTION','PREREQUISITE_HIT_FAILED',
    'NATIVE_EVENT_ABSENT','OTHER_VERIFIED_REASON'
)
foreach ($row in $rows) {
    $value = $row.Value
    if ($value.schema -ne 'tno.phase6.endgame_research.v1' -or
        $value.APO_profile -ne 'NONE' -or $value.TNO_family -ne $ExpectedFamily -or
        $value.native_gear_EP -ne $expectedEp[$value.TNO_stage] -or
        $value.resolved_production_stage -ne $value.TNO_stage -or
        $value.failure_reason -notin $allowedFailures -or
        $value.l2_layer_bypassed_unexpectedly -or $value.tensura_layer_bypassed_unexpectedly -or
        $value.unexpected_source_duplication -or $value.event_recursion_observed -or
        $value.royal_arrow_mark_observed -or $value.crit) {
        throw "Invalid row invariant at Lv$($value.level) $($value.TNO_stage) hit $($value.hit_index)."
    }
}

$preserved = @($catalogs + $rows + $cases + $suites)
$directory = Split-Path -Parent $OutputPath
if ($directory) { [IO.Directory]::CreateDirectory((Join-Path (Get-Location) $directory)) | Out-Null }
[IO.File]::WriteAllLines((Join-Path (Get-Location) $OutputPath), @($preserved.Json), [Text.UTF8Encoding]::new($false))

Write-Host "Validated ${ExpectedFamily}: 32 cases, 320 rows, zero errors."
Write-Host "Wrote $($preserved.Count) records to $OutputPath"
