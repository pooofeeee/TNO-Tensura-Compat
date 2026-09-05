param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_SEVERANCE_WALL '
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$content = [IO.File]::ReadAllText($resolvedLog)
$records = [Collections.Generic.List[object]]::new()

foreach ($line in ($content -split "`r?`n")) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -ge 0) {
        $json = $line.Substring($index + $marker.Length)
    }
    else {
        $json = $line.Trim()
    }
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json }
    catch { throw "Malformed R3 JSON in ${resolvedLog}: $json" }
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
if ($catalog.schema -ne 'tno.phase6.severance_wall.r3.v1' -or
    $catalog.TNO_family -ne 'SEVERANCE' -or $catalog.calibration_mode -ne 'severance_wall' -or
    -not $catalog.production_stage_observation -or
    $suite.status -ne 'complete' -or $suite.case_count -ne 72 -or
    $suite.requested_case_count -ne 72) {
    throw 'Catalog or suite_result does not match the locked R3 protocol.'
}

$levels = @(600, 800, 1000)
$stages = @('S5', 'S6', 'S7')
$profiles = @(
    'ACCEPTED_STRONGEST_LEGAL',
    'WITHOUT_TANK_CONTROL',
    'WITHOUT_DEMENTOR_CONTROL',
    'WITHOUT_ADAPTIVE_CONTROL',
    'WITHOUT_TANK_DEMENTOR_CONTROL',
    'WITHOUT_TANK_ADAPTIVE_CONTROL',
    'WITHOUT_DEMENTOR_ADAPTIVE_CONTROL',
    'WITHOUT_TANK_DEMENTOR_ADAPTIVE_CONTROL'
)
$removed = @{
    ACCEPTED_STRONGEST_LEGAL = @()
    WITHOUT_TANK_CONTROL = @('l2hostility:tank')
    WITHOUT_DEMENTOR_CONTROL = @('l2hostility:dementor')
    WITHOUT_ADAPTIVE_CONTROL = @('l2hostility:adaptive')
    WITHOUT_TANK_DEMENTOR_CONTROL = @('l2hostility:tank', 'l2hostility:dementor')
    WITHOUT_TANK_ADAPTIVE_CONTROL = @('l2hostility:tank', 'l2hostility:adaptive')
    WITHOUT_DEMENTOR_ADAPTIVE_CONTROL = @('l2hostility:dementor', 'l2hostility:adaptive')
    WITHOUT_TANK_DEMENTOR_ADAPTIVE_CONTROL = @('l2hostility:tank', 'l2hostility:dementor', 'l2hostility:adaptive')
}

foreach ($level in $levels) {
    foreach ($profile in $profiles) {
        foreach ($stage in $stages) {
            $matchingStarts = @($starts | Where-Object {
                $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile -and
                $_.Value.TNO_stage -eq $stage
            })
            $matchingResults = @($results | Where-Object {
                $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile -and
                $_.Value.TNO_stage -eq $stage
            })
            $matchingRows = @($rows | Where-Object {
                $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile -and
                $_.Value.TNO_stage -eq $stage
            })
            if ($matchingStarts.Count -ne 1 -or $matchingResults.Count -ne 1 -or $matchingRows.Count -ne 10) {
                throw "Incomplete matrix cell Lv${level}/${profile}/${stage}."
            }
            $indices = @($matchingRows.Value.hit_index | Sort-Object)
            if (($indices -join ',') -ne '1,2,3,4,5,6,7,8,9,10') {
                throw "Hit indices are incomplete for Lv${level}/${profile}/${stage}."
            }
        }
    }
}

foreach ($record in $starts + $results) {
    $value = $record.Value
    if ($value.schema -ne 'tno.phase6.severance_wall.r3.v1' -or
        $value.boss -ne 'tensura:orc_disaster' -or $value.TNO_family -ne 'SEVERANCE' -or
        $value.calibration_mode -ne 'severance_wall' -or
        $value.calibration_case -ne 'SEVERANCE_WALL_NATIVE_POLICY' -or
        [double]$value.Q_generic_health -ne 0 -or [double]$value.RD_dementor -ne 0 -or
        [double]$value.RA_adaptive -ne 0 -or $value.APO_profile -ne 'NONE' -or
        $value.royal_arrow_mark_enabled -or -not $value.fresh_L2_attachment_per_case) {
        throw 'Case metadata violates the observation-only R3 protocol.'
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
        throw "Case result failed count invariants: Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)."
    }
}

foreach ($record in $rows) {
    $value = $record.Value
    $trace = $value.severance_wall_trace
    if ($value.schema -ne 'tno.phase6.severance_wall.r3.v1' -or
        $value.boss -ne 'tensura:orc_disaster' -or $value.TNO_family -ne 'SEVERANCE' -or
        $value.APO_profile -ne 'NONE' -or $value.royal_arrow_mark_enabled -or
        $value.released_projectile_count -ne 1 -or $value.physical_damage_event_count -ne 1 -or
        $value.physical_damage_source_id -ne 'minecraft:arrow' -or
        @($value.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
        @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic' -or
        $value.unexpected_source_duplication -or $value.event_recursion_observed -or
        $value.l2_layer_bypassed_unexpectedly -or $value.tensura_layer_bypassed_unexpectedly -or
        $value.severance_distinct_damage_source -or $value.severance_wall_trace_count -ne 1 -or
        $null -eq $trace -or -not $trace.observation_only -or $trace.modifier_values_changed -or
        [Math]::Abs([double]$trace.pre_L2_combined_physical - [double]$value.physical_combined_original_before_L2) -gt 0.001 -or
        [Math]::Abs([double]$trace.final_physical_after_L2_pipeline - [double]$value.combined_physical_after_L2) -gt 0.001) {
        throw "Per-hit physical/source invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/hit$($value.hit_index)."
    }
    if ([double]$value.severance_native_attack_bonus -ne 3.0 -or
        [double]$value.severance_native_post_round -le [double]$value.severance_base_only_post_round -or
        [double]$value.severance_after_stage_post_round -lt [double]$value.severance_native_post_round -or
        [Math]::Abs([double]$value.severance_native_pre_round -
            ([double]$value.severance_projectile_speed *
                ([double]$value.severance_base_projectile_damage + 3.0))) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_after_stage_pre_round -
            ([double]$value.severance_projectile_speed *
                ([double]$value.severance_base_projectile_damage +
                    3.0 * [double]$value.stage_coefficient))) -gt 0.001 -or
        [Math]::Abs([double]$value.physical_original_before_stage -
            [double]$value.severance_base_only_post_round) -gt 0.001 -or
        [Math]::Abs([double]$value.physical_combined_original_before_L2 -
            [double]$value.severance_after_stage_post_round) -gt 0.001) {
        throw "Native +3/base/Stage decomposition failed at Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/hit$($value.hit_index)."
    }
    $hasTank = $null -ne $value.trait_ranks.'l2hostility:tank'
    $hasDementor = $null -ne $value.trait_ranks.'l2hostility:dementor'
    $hasAdaptive = $null -ne $value.trait_ranks.'l2hostility:adaptive'
    if ($trace.Tank_present -ne $hasTank) {
        throw "Trait trace mismatch at Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/hit$($value.hit_index)."
    }
    $processed = [double]$trace.DamageData_original -gt 0.0001
    if ($processed) {
        if (-not $trace.final_hurt_returned_success -or $trace.Adaptive_source_msgId -ne 'arrow' -or
            [Math]::Abs([double]$trace.context_combined_physical - [double]$trace.DamageData_original) -gt 0.001 -or
            $trace.Dementor_applied -ne $hasDementor -or $trace.Adaptive_applied -ne $hasAdaptive -or
            -not $trace.wound_attempted -or $trace.wound_attempt_count -ne 1) {
            throw "Processed native pipeline trace failed at Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/hit$($value.hit_index)."
        }
    }
    elseif ($trace.final_hurt_returned_success -or $trace.Dementor_applied -or $trace.Adaptive_applied -or
        $trace.wound_attempted -or $trace.wound_attempt_count -ne 0 -or
        [double]$trace.final_physical_after_L2_pipeline -ne 0) {
        throw "Early-rejected hit incorrectly reports downstream execution at Lv$($value.level)/$($value.L2_profile_variant)/$($value.TNO_stage)/hit$($value.hit_index)."
    }
    if ($processed -and -not $hasDementor -and
        [Math]::Abs([double]$trace.Dementor_input - [double]$trace.Dementor_native_output) -gt 0.001) {
        throw 'Dementor-free processed control changed across the Dementor boundary.'
    }
    if ($processed -and -not $hasAdaptive -and
        [Math]::Abs([double]$trace.Adaptive_native_factor - 1.0) -gt 0.000001) {
        throw 'Adaptive-free control did not retain factor 1.'
    }
    if ($trace.wound_attempt_count -gt 1 -or $trace.wound_attempted -ne ($trace.wound_attempt_count -eq 1) -or
        $trace.wound_stored -ne ([double]$trace.wound_delta -gt 0.0001)) {
        throw 'Native wound-attempt/storage accounting is inconsistent.'
    }
}

$processedRows = @($rows | Where-Object {
    [double]$_.Value.severance_wall_trace.DamageData_original -gt 0.0001
})
$earlyRejectedRows = @($rows | Where-Object {
    [double]$_.Value.severance_wall_trace.DamageData_original -le 0.0001
})
$processedAttempts = @($processedRows | Where-Object {
    $_.Value.severance_wall_trace.wound_attempted -and
    $_.Value.severance_wall_trace.wound_attempt_count -eq 1
})
$processedStores = @($processedRows | Where-Object {
    $_.Value.severance_wall_trace.wound_stored -and
    [double]$_.Value.severance_wall_trace.wound_delta -gt 0.0001
})
$earlyCallbacks = @($earlyRejectedRows | Where-Object {
    $_.Value.severance_wall_trace.wound_attempted -or
    $_.Value.severance_wall_trace.wound_attempt_count -ne 0 -or
    $_.Value.severance_wall_trace.wound_stored
})
if ($processedRows.Count -ne 140 -or $earlyRejectedRows.Count -ne 580 -or
    $processedAttempts.Count -ne 140 -or $processedStores.Count -ne 140 -or
    $earlyCallbacks.Count -ne 0) {
    throw "Observed R3 admission/callback split changed: processed=$($processedRows.Count), early_rejected=$($earlyRejectedRows.Count), attempts=$($processedAttempts.Count), stores=$($processedStores.Count), early_callbacks=$($earlyCallbacks.Count)."
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
[IO.File]::WriteAllLines($OutputPath, @($records.Json), [Text.UTF8Encoding]::new($false))
Write-Output "Validated R3: 72 cases, 720 real Royal Arrow releases, zero errors, complete 3-level x 8-profile x 3-stage matrix."
