param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('R4_CONTROL_NO_WOUND', 'R4_NATIVE_WOUND', 'R5_CONTROL_NO_WOUND', 'R5_NATIVE_WOUND')]
    [string] $ExpectedCase
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_SEVERANCE_REGENERATE '
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$content = [IO.File]::ReadAllText($resolvedLog)
$records = [Collections.Generic.List[object]]::new()

foreach ($line in ($content -split "`r?`n")) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -ge 0) { $json = $line.Substring($index + $marker.Length) }
    elseif ($line.TrimStart().StartsWith('{')) { $json = $line.Trim() }
    else { continue }
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json }
    catch { throw "Malformed R2 JSON in ${resolvedLog}: $json" }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$starts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$heals = @($records | Where-Object { $_.Value.kind -eq 'heal_event' })
$results = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -in @('case_error', 'suite_error') })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1 -or $starts.Count -ne 1 -or $results.Count -ne 1 -or
    $suites.Count -ne 1 -or $heals.Count -ne 6) {
    throw "Expected 1 catalog/start/result/suite and 6 heals; found $($catalogs.Count)/$($starts.Count)/$($results.Count)/$($suites.Count)/$($heals.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) error record(s)." }

$expected = @{
    R4_CONTROL_NO_WOUND = @{ Level = 600; Rank = 4; Wound = $false }
    R4_NATIVE_WOUND = @{ Level = 600; Rank = 4; Wound = $true }
    R5_CONTROL_NO_WOUND = @{ Level = 800; Rank = 5; Wound = $false }
    R5_NATIVE_WOUND = @{ Level = 800; Rank = 5; Wound = $true }
}[$ExpectedCase]
$catalog = $catalogs[0].Value
$start = $starts[0].Value
$result = $results[0].Value
$suite = $suites[0].Value

if ($catalog.schema -ne 'tno.phase6.severance_regenerate.r2.v1' -or
    $catalog.status -ne 'ready' -or $catalog.target -ne 'tensura:orc_disaster' -or
    $catalog.case_count -ne 1 -or $catalog.case_filter -ne $ExpectedCase -or
    $catalog.wound_release_count_per_case -ne 10 -or $catalog.heal_cycles_per_case -ne 6 -or
    [Math]::Abs([double]$catalog.regenerate_config_fraction_per_rank_per_second - 0.01) -gt 0.000001 -or
    $catalog.TNO_stage -ne 'S0' -or $catalog.APO_profile -ne 'NONE' -or
    $catalog.Magic_Holy_production_modified) {
    throw 'Catalog does not match the locked R2 protocol.'
}
if ($suite.status -ne 'complete' -or $suite.case_count -ne 1 -or
    $suite.requested_case_count -ne 1 -or $suite.heal_event_count -ne 6 -or
    $suite.case_error_count -ne 0) {
    throw 'Capture lacks one complete one-case suite_result.'
}

foreach ($value in @($start, $result) + @($heals.Value)) {
    if ($value.case_id -ne $ExpectedCase -or $value.target -ne 'tensura:orc_disaster' -or
        $value.L2_level -ne $expected.Level -or $value.Regenerate_rank -ne $expected.Rank -or
        $value.retain_native_wound -ne $expected.Wound -or
        $value.L2_profile -ne 'CONTROLLED_REGENERATE_ONLY' -or
        $value.TNO_stage -ne 'S0' -or $value.APO_profile -ne 'NONE') {
        throw 'Case metadata does not match the requested R2 case.'
    }
}
if ($start.status -ne 'running' -or $start.arrow_event_count -ne 10 -or
    $start.accepted_arrow_event_count -ne 10 -or -not $start.l2_trait_ticking_preserved -or
    @($start.arrow_damage_sources).Count -ne 1 -or $start.arrow_damage_sources[0] -ne 'minecraft:arrow' -or
    @($start.arrow_damage_tags) -notcontains 'minecraft:is_projectile' -or
    @($start.arrow_damage_tags) -contains 'neoforge:is_magic' -or
    [double]$start.wound_created_natively_before_control -le 0) {
    throw 'Native Royal Arrow wound setup invariants failed.'
}
if ($expected.Wound) {
    if ([double]$start.wound_at_heal_start -le 0 -or $start.wound_remaining_seconds_at_start -le 0) {
        throw 'Wounded case did not retain the legitimate native wound.'
    }
}
elseif ([double]$start.wound_at_heal_start -ne 0 -or $start.wound_remaining_seconds_at_start -ne 0) {
    throw 'Control case retained wound state after native clearSeverance.'
}

$nominal = [double]$start.max_hp * 0.01 * $expected.Rank
$previousServerTick = $null
for ($i = 0; $i -lt $heals.Count; $i++) {
    $heal = $heals[$i].Value
    if ($heal.cycle_index -ne ($i + 1) -or $heal.target_tick -ne 20 -or
        -not $heal.native_source_stack_verified -or -not $heal.healing_callback_executed -or
        $heal.native_source_cause -ne 'l2hostility:regenerate RegenTrait.tick -> LivingEntity.heal' -or
        [Math]::Abs([double]$heal.nominal_regenerate_amount - $nominal) -gt 0.01 -or
        [Math]::Abs([double]$heal.shp_after - [double]$heal.shp_before) -gt 0.01 -or
        $heal.error -ne '') {
        throw "Heal-cycle invariant failed at cycle $($i + 1)."
    }
    if ($null -ne $previousServerTick -and ([long]$heal.server_tick - $previousServerTick) -ne 20) {
        throw "Native Regenerate cadence changed at cycle $($i + 1)."
    }
    $previousServerTick = [long]$heal.server_tick
}

$ceiling = [double]$result.max_hp - [double]$result.wound_at_heal_start
$expectedActual = [Math]::Max(0.0, [Math]::Min(6.0 * $nominal, $ceiling - [double]$result.initial_hp))
if ($result.status -ne 'complete' -or $result.heal_event_count -ne 6 -or
    [Math]::Abs([double]$result.nominal_regenerate_amount_per_cycle - $nominal) -gt 0.01 -or
    [Math]::Abs([double]$result.actual_healing_total - $expectedActual) -gt 0.01 -or
    [Math]::Abs([double]$result.expected_ceiling_limited_healing_total - $expectedActual) -gt 0.01 -or
    [Math]::Abs([double]$result.final_hp - $ceiling) -gt 0.01 -or
    [Math]::Abs([double]$result.final_shp - [double]$result.initial_shp) -gt 0.01 -or
    $result.unexpected_l2_bypass_count -ne 0 -or $result.duplicate_damage_source_count -ne 0 -or
    $result.error_count -ne 0) {
    throw 'Completed case failed aggregate healing invariants.'
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
[IO.File]::WriteAllLines($OutputPath, @($records.Json), [Text.UTF8Encoding]::new($false))
Write-Output "Validated ${ExpectedCase}: 1 case, 10 accepted arrows, 6 native Regenerate events, actual healing $($result.actual_healing_total), wound $($result.wound_at_heal_start)."
