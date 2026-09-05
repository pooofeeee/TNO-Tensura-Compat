param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_SEVERANCE_PROTOTYPE '
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$content = [IO.File]::ReadAllText($resolvedLog)
$records = [Collections.Generic.List[object]]::new()

foreach ($line in ($content -split "`r?`n")) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -ge 0) { $json = $line.Substring($index + $marker.Length) }
    else { $json = $line.Trim() }
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json }
    catch { throw "Malformed R4 JSON in ${resolvedLog}: $json" }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$starts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$results = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -in @('case_error', 'suite_error') })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1 -or $starts.Count -ne 72 -or $rows.Count -ne 720 -or
    $results.Count -ne 72 -or $suites.Count -ne 1) {
    throw "Expected 1/72/720/72/1 catalog/start/row/result/suite records; found $($catalogs.Count)/$($starts.Count)/$($rows.Count)/$($results.Count)/$($suites.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) error record(s)." }

$catalog = $catalogs[0].Value
$suite = $suites[0].Value
if ($catalog.schema -ne 'tno.phase6.severance_prototype.r4.v1' -or
    $catalog.TNO_family -ne 'SEVERANCE' -or $catalog.calibration_mode -ne 'severance_prototype' -or
    -not $catalog.production_stage_observation -or -not $catalog.prototype_development_only -or
    $catalog.prototype_changes_Royal_Arrow_base -or $catalog.prototype_creates_second_source -or
    $catalog.prototype_writes_wound_directly -or $catalog.production_balance_mutated -or
    $catalog.production_combat_mutated -or -not $catalog.development_only_combat_fixture_active -or
    $suite.status -ne 'complete' -or $suite.case_count -ne 72 -or
    $suite.requested_case_count -ne 72) {
    throw 'Catalog or suite_result does not match the locked R4 protocol.'
}

$levels = @(600, 800, 1000)
$stages = @('S5', 'S6', 'S7')
$accepted = 'ACCEPTED_STRONGEST_LEGAL'
$controls = @(
    'WITHOUT_TANK_CONTROL',
    'WITHOUT_DEMENTOR_CONTROL',
    'WITHOUT_ADAPTIVE_CONTROL',
    'WITHOUT_TANK_DEMENTOR_ADAPTIVE_CONTROL'
)
$cases = @{
    SEVERANCE_PROTOTYPE_X1 = 1.0
    SEVERANCE_PROTOTYPE_X4 = 4.0
    SEVERANCE_PROTOTYPE_X16 = 16.0
    SEVERANCE_PROTOTYPE_X64_DIAGNOSTIC_CEILING = 64.0
}
$removed = @{
    ACCEPTED_STRONGEST_LEGAL = @()
    WITHOUT_TANK_CONTROL = @('l2hostility:tank')
    WITHOUT_DEMENTOR_CONTROL = @('l2hostility:dementor')
    WITHOUT_ADAPTIVE_CONTROL = @('l2hostility:adaptive')
    WITHOUT_TANK_DEMENTOR_ADAPTIVE_CONTROL = @('l2hostility:tank', 'l2hostility:dementor', 'l2hostility:adaptive')
}

foreach ($level in $levels) {
    foreach ($stage in $stages) {
        foreach ($case in $cases.Keys) {
            $matchingRows = @($rows | Where-Object {
                $_.Value.level -eq $level -and $_.Value.TNO_stage -eq $stage -and
                $_.Value.L2_profile_variant -eq $accepted -and $_.Value.calibration_case -eq $case
            })
            if ($matchingRows.Count -ne 10) {
                throw "Incomplete accepted matrix cell Lv${level}/${stage}/${case}."
            }
        }
        foreach ($profile in $controls) {
            $matchingRows = @($rows | Where-Object {
                $_.Value.level -eq $level -and $_.Value.TNO_stage -eq $stage -and
                $_.Value.L2_profile_variant -eq $profile -and
                $_.Value.calibration_case -eq 'SEVERANCE_PROTOTYPE_X16'
            })
            if ($matchingRows.Count -ne 10) {
                throw "Incomplete X16 control matrix cell Lv${level}/${stage}/${profile}."
            }
        }
    }
}

foreach ($record in $starts + $results) {
    $value = $record.Value
    if ($value.schema -ne 'tno.phase6.severance_prototype.r4.v1' -or
        $value.boss -ne 'tensura:orc_disaster' -or $value.TNO_family -ne 'SEVERANCE' -or
        $value.calibration_mode -ne 'severance_prototype' -or
        [double]$value.Q_generic_health -ne 0 -or [double]$value.RD_dementor -ne 0 -or
        [double]$value.RA_adaptive -ne 0 -or $value.APO_profile -ne 'NONE' -or
        $value.royal_arrow_mark_enabled -or -not $value.fresh_L2_attachment_per_case -or
        -not $value.prototype_development_only) {
        throw 'Case metadata violates the development-only R4 protocol.'
    }
    $expectedMultiplier = [double]$cases[$value.calibration_case]
    if ($expectedMultiplier -le 0 -or [double]$value.Severance_eligible_multiplier -ne $expectedMultiplier) {
        throw "Invalid candidate multiplier in $($value.calibration_case)."
    }
    if ($value.L2_profile_variant -ne $accepted -and $value.calibration_case -ne 'SEVERANCE_PROTOTYPE_X16') {
        throw 'Trait-removal controls must use only the X16 candidate.'
    }
    foreach ($trait in $removed[$value.L2_profile_variant]) {
        if ($null -ne $value.trait_ranks.$trait) {
            throw "Profile $($value.L2_profile_variant) retained removed trait $trait."
        }
    }
}

foreach ($record in $results) {
    $value = $record.Value
    if ($value.status -ne 'ok' -or $value.shots_released -ne 10 -or $value.hits_recorded -ne 10 -or
        $value.severance_wall_trace_count -ne 10 -or $value.calibration_trace_count -ne 0) {
        throw "Case result failed count invariants: Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/$($value.calibration_case)."
    }
}

$processedCount = 0
$attemptCount = 0
$storeCount = 0
foreach ($record in $rows) {
    $value = $record.Value
    $trace = $value.severance_wall_trace
    $multiplier = [double]$cases[$value.calibration_case]
    if ($value.schema -ne 'tno.phase6.severance_prototype.r4.v1' -or
        $value.APO_profile -ne 'NONE' -or $value.royal_arrow_mark_enabled -or
        $value.released_projectile_count -ne 1 -or $value.physical_damage_event_count -ne 1 -or
        $value.physical_damage_source_id -ne 'minecraft:arrow' -or
        @($value.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
        @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic' -or
        $value.unexpected_source_duplication -or $value.event_recursion_observed -or
        $value.l2_layer_bypassed_unexpectedly -or $value.tensura_layer_bypassed_unexpectedly -or
        $value.severance_distinct_damage_source -or $value.severance_wall_trace_count -ne 1 -or
        $null -eq $trace -or $trace.observation_only -or $trace.modifier_values_changed -or
        -not $trace.eligible_pre_hurt_prototype_active -or $trace.Royal_Arrow_base_changed_by_prototype -or
        $value.severance_base_affected_by_prototype -or
        [Math]::Abs([double]$trace.context_combined_physical - [double]$value.physical_combined_original_before_L2) -gt 0.001 -or
        [Math]::Abs([double]$trace.pre_L2_combined_physical - [double]$value.physical_combined_original_before_L2) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_prototype_post_round - [double]$value.physical_combined_original_before_L2) -gt 0.001) {
        throw "Per-hit source/prototype invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/$($value.calibration_case)/hit$($value.hit_index)."
    }

    $productionEligible = 3.0 * [double]$value.stage_coefficient
    $prototypeEligible = $productionEligible * $multiplier
    $prototypePre = [double]$value.severance_projectile_speed *
        ([double]$value.severance_base_projectile_damage + $prototypeEligible)
    if ([double]$value.severance_native_attack_bonus -ne 3.0 -or
        [Math]::Abs([double]$value.severance_production_eligible_contribution - $productionEligible) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_prototype_eligible_contribution - $prototypeEligible) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_prototype_pre_round - $prototypePre) -gt 0.001 -or
        [Math]::Abs([double]$trace.prototype_eligible_pre_velocity - $prototypeEligible) -gt 0.001 -or
        [Math]::Abs([double]$trace.prototype_eligible_multiplier - $multiplier) -gt 0.000001 -or
        [Math]::Abs([double]$value.physical_original_before_stage - [double]$value.severance_base_only_post_round) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_after_stage_pre_round -
            [double]$value.severance_projectile_speed *
                ([double]$value.severance_base_projectile_damage + $productionEligible)) -gt 0.001) {
        throw "Eligible-only arithmetic failed at Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/$($value.calibration_case)/hit$($value.hit_index)."
    }

    $processed = [double]$trace.DamageData_original -gt 0.0001
    if ($processed) {
        $processedCount++
        if (-not $trace.final_hurt_returned_success -or $trace.Adaptive_source_msgId -ne 'arrow' -or
            [Math]::Abs([double]$trace.context_combined_physical - [double]$trace.DamageData_original) -gt 0.001 -or
            -not $trace.wound_attempted -or $trace.wound_attempt_count -ne 1 -or
            -not $trace.wound_stored -or [double]$trace.wound_delta -le 0.0001) {
            throw "Processed native pipeline trace failed at hit $($value.hit_index)."
        }
        $attemptCount++
        $storeCount++
    }
    elseif ($trace.final_hurt_returned_success -or $trace.Dementor_applied -or $trace.Adaptive_applied -or
        $trace.wound_attempted -or $trace.wound_attempt_count -ne 0 -or $trace.wound_stored -or
        [double]$trace.final_HP_delta -ne 0 -or [double]$trace.final_SHP_delta -ne 0) {
        throw "Early-rejected release incorrectly reports downstream execution at hit $($value.hit_index)."
    }
}

if ($processedCount -le 0 -or $attemptCount -ne $processedCount -or $storeCount -ne $processedCount) {
    throw "R4 callback/storage accounting failed: processed=$processedCount attempts=$attemptCount stores=$storeCount."
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
[IO.File]::WriteAllLines($OutputPath, @($records.Json), [Text.UTF8Encoding]::new($false))
Write-Output "Validated R4: 72 cases, 720 real Royal Arrow releases, ${processedCount} admitted callbacks/stores, zero errors, eligible-only single-source prototype intact."
