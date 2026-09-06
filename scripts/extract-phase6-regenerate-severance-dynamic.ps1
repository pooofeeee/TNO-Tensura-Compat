param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_ADAPTIVE_WOUND '
$schema = 'tno.phase6.regenerate_severance_counter_protocol.p3.v1'
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$records = [Collections.Generic.List[object]]::new()

foreach ($line in [IO.File]::ReadAllLines($resolvedLog)) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -ge 0) { $json = $line.Substring($index + $marker.Length) }
    else { $json = $line.Trim() }
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json -Depth 100 }
    catch { throw "Malformed P3 JSON in ${resolvedLog}: $json" }
    if ($value.schema -ne $schema) { continue }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$starts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$cycles = @($records | Where-Object { $_.Value.kind -eq 'regenerate_cycle' })
$results = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -in @('case_error', 'suite_error') })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1 -or $starts.Count -ne 9 -or $rows.Count -ne 540 -or
    $cycles.Count -ne 360 -or $results.Count -ne 9 -or $suites.Count -ne 1) {
    throw "Expected 1/9/540/360/9/1 catalog/start/row/cycle/result/suite records; found $($catalogs.Count)/$($starts.Count)/$($rows.Count)/$($cycles.Count)/$($results.Count)/$($suites.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) error record(s)." }

$catalog = $catalogs[0].Value
$suite = $suites[0].Value
if ($catalog.calibration_mode -ne 'adaptive_wound_dynamic' -or
    $catalog.checkpoint -ne 'P3_DYNAMIC_DEFENDER_ADVANTAGE' -or
    $catalog.P3_candidate -ne 'C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY' -or
    [double]$catalog.P3_diagnostic_RW -ne 0.5 -or
    [double]$catalog.P3_native_control_RW -ne 0.0 -or
    -not $catalog.P3_magic_holy_production_unchanged -or
    -not $catalog.prototype_development_only -or
    $catalog.prototype_changes_physical_damage -or
    $catalog.prototype_changes_Royal_Arrow_base -or
    $catalog.prototype_creates_physical_source -or
    $catalog.prototype_writes_wound_directly -or
    $catalog.prototype_changes_Adaptive_state -or
    $catalog.prototype_changes_Regenerate -or
    $catalog.production_balance_mutated -or $catalog.production_combat_mutated -or
    $catalog.APO_profile -ne 'NONE' -or
    $catalog.shots_per_case -ne 60 -or $catalog.fixed_window_ticks -ne 1200 -or
    $suite.status -ne 'complete' -or $suite.case_count -ne 9 -or
    $suite.requested_case_count -ne 9) {
    throw 'Catalog or suite_result does not match the locked P3 protocol.'
}

$accepted = 'ACCEPTED_STRONGEST_LEGAL'
$withoutRegenerate = 'WITHOUT_REGENERATE_CONTROL'
$candidate = 'DYNAMIC_CANDIDATE_C_RW_50'
$native = 'DYNAMIC_NATIVE_WOUND_RW_0_CONTROL'
$tolerance = 0.02

foreach ($level in @(600, 800, 1000)) {
    $expectedRank = if ($level -eq 600) { 4 } else { 5 }
    $expectedRequest = if ($level -eq 600) { 400.0 } else { 500.0 }
    $definitions = @(
        @{ Calibration = $candidate; Profile = $accepted; Role = 'CANDIDATE_C_RW_50_REGENERATE_ON'; RW = 0.5; Rank = $expectedRank; Cycles = 60 },
        @{ Calibration = $candidate; Profile = $withoutRegenerate; Role = 'CANDIDATE_C_RW_50_WITHOUT_REGENERATE'; RW = 0.5; Rank = 0; Cycles = 0 },
        @{ Calibration = $native; Profile = $accepted; Role = 'NATIVE_RW_0_REGENERATE_ON_CONTROL'; RW = 0.0; Rank = $expectedRank; Cycles = 60 }
    )

    foreach ($definition in $definitions) {
        $cellStarts = @($starts | Where-Object {
            $_.Value.level -eq $level -and
            $_.Value.calibration_case -eq $definition.Calibration -and
            $_.Value.L2_profile_variant -eq $definition.Profile
        })
        $cellRows = @($rows | Where-Object {
            $_.Value.level -eq $level -and
            $_.Value.calibration_case -eq $definition.Calibration -and
            $_.Value.L2_profile_variant -eq $definition.Profile
        })
        $cellCycles = @($cycles | Where-Object {
            $_.Value.level -eq $level -and
            $_.Value.calibration_case -eq $definition.Calibration -and
            $_.Value.L2_profile_variant -eq $definition.Profile
        })
        $cellResults = @($results | Where-Object {
            $_.Value.level -eq $level -and
            $_.Value.calibration_case -eq $definition.Calibration -and
            $_.Value.L2_profile_variant -eq $definition.Profile
        })
        if ($cellStarts.Count -ne 1 -or $cellRows.Count -ne 60 -or
            $cellCycles.Count -ne $definition.Cycles -or $cellResults.Count -ne 1) {
            throw "Missing or duplicate P3 cell Lv${level}/$($definition.Role)."
        }
        $summary = $cellResults[0].Value
        if ($summary.status -ne 'ok' -or $summary.boss -ne 'tensura:orc_disaster' -or
            $summary.TNO_family -ne 'SEVERANCE' -or $summary.TNO_stage -ne 'S7' -or
            $summary.APO_profile -ne 'NONE' -or
            $summary.P3_profile_role -ne $definition.Role -or
            [double]$summary.P3_diagnostic_RW -ne [double]$definition.RW -or
            $summary.shots_released -ne 60 -or $summary.hits_recorded -ne 60 -or
            $summary.elapsed_ticks -ne 1200 -or
            $summary.magic_release_count -ne 20 -or $summary.holy_release_count -ne 20 -or
            $summary.severance_release_count -ne 20 -or
            $summary.native_tick_boundary_count -ne 60 -or
            $summary.regenerate_cycle_count -ne $definition.Cycles -or
            $summary.regenerate_incomplete_cycle_count -ne 0 -or
            $summary.regenerate_ceiling_violation_count -ne 0 -or
            $summary.regenerate_SHP_movement_cycle_count -ne 0 -or
            $summary.counter_position_observation_ticks -lt 1190 -or
            $summary.production_Magic_Holy_behavior_changed -or
            [double]$summary.production_Magic_Holy_Q -ne 1.0 -or
            [double]$summary.production_Magic_Holy_RD -ne 0.75 -or
            [double]$summary.production_Magic_Holy_RA -ne 0.75 -or
            $summary.direct_TNO_wound_write -or
            $summary.source_event_integrity_failure_count -ne 0 -or
            $summary.duplicate_physical_event_count -ne 0 -or
            $summary.recursion_count -ne 0 -or
            $summary.unexpected_L2_bypass_count -ne 0 -or
            $summary.unexpected_Tensura_bypass_count -ne 0) {
            throw "P3 summary invariant failed at Lv${level}/$($definition.Role)."
        }

        if ($definition.Rank -eq 0) {
            if ($summary.Regenerate_rank -ne 0 -or
                $summary.regenerate_callback_count -ne 0 -or
                $summary.regenerate_native_tick_attempt_count -ne 0 -or
                [double]$summary.regenerate_actual_healing -ne 0 -or
                [double]$summary.regenerate_denied_healing -ne 0 -or
                $summary.defender_recovered_positive_HP) {
                throw "P3 no-Regenerate control retained Regenerate activity at Lv${level}."
            }
        }
        else {
            if ($summary.Regenerate_rank -ne $expectedRank -or
                $summary.regenerate_trait_rank_at_end -ne $expectedRank -or
                $summary.regenerate_callback_count -ne 60 -or
                $summary.regenerate_native_tick_attempt_count -ne 60 -or
                -not $summary.regenerate_trait_valid_at_start -or
                -not $summary.regenerate_trait_valid_on_all_observed_attempts -or
                $summary.regenerate_trait_missing_tick_count -ne 0 -or
                -not $summary.defender_recovered_positive_HP -or
                [double]$summary.regenerate_actual_healing -le 0) {
                throw "P3 native Regenerate identity/activity failed at Lv${level}/$($definition.Role)."
            }
        }

        $expectedIndices = 1..60
        if ((@($cellRows.Value.hit_index) -join ',') -ne ($expectedIndices -join ',')) {
            throw "P3 hit indices are incomplete/out of order at Lv${level}/$($definition.Role)."
        }
        foreach ($rowRecord in $cellRows) {
            $row = $rowRecord.Value
            $expectedFamily = switch (($row.hit_index - 1) % 3) {
                0 { 'MAGIC_WEAPON' }
                1 { 'HOLY_WEAPON' }
                2 { 'SEVERANCE' }
            }
            if ($row.rotation_family -ne $expectedFamily -or
                -not $row.legal_separate_bow_rotation -or
                $row.released_projectile_count -ne 1 -or
                $row.projectile_entity_id -ne 'royalvariations:royal_arrow' -or
                $row.requested_ammo_item -ne 'royalvariations:royal_arrow' -or
                $row.physical_damage_event_count -ne 1 -or
                $row.physical_damage_source_id -ne 'minecraft:arrow' -or
                @($row.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
                @($row.damage_source_tags_if_observable) -contains 'neoforge:is_magic' -or
                $row.unexpected_source_duplication -or $row.event_recursion_observed -or
                $row.l2_layer_bypassed_unexpectedly -or
                $row.tensura_layer_bypassed_unexpectedly -or
                $row.severance_wall_trace_count -ne 1) {
                throw "P3 source/rotation invariant failed at Lv${level}/$($definition.Role)/hit$($row.hit_index)."
            }
            if ($expectedFamily -in @('MAGIC_WEAPON', 'HOLY_WEAPON')) {
                $expectedEnchantment = if ($expectedFamily -eq 'MAGIC_WEAPON') { 'tensura:magic_weapon' } else { 'tensura:holy_weapon' }
                $expectedSource = if ($expectedFamily -eq 'MAGIC_WEAPON') { 'tensura:magic' } else { 'tensura:holy_damage' }
                if ($row.rotation_enchantment -ne $expectedEnchantment -or
                    $row.engraving_damage_event_count -ne 1 -or
                    $row.family_damage_source_id -ne $expectedSource -or
                    [Math]::Abs([double]$row.engraving_native_amount - 8.0) -gt 0.001 -or
                    [Math]::Abs([double]$row.engraving_after_stage_coefficient - 11.2) -gt 0.001 -or
                    $row.severance_configured_projectile_count -ne 0 -or
                    $row.severance_wall_trace.adaptive_wound_trace_count -ne 0) {
                    throw "P3 production Magic/Holy invariant failed at Lv${level}/hit$($row.hit_index)."
                }
            }
            else {
                $wall = $row.severance_wall_trace
                $adaptive = $wall.adaptive_wound_architecture
                if ($row.rotation_enchantment -ne 'tensura:severance' -or
                    $row.engraving_damage_event_count -ne 0 -or
                    $row.severance_configured_projectile_count -ne 1 -or
                    $wall.adaptive_wound_trace_count -ne 1 -or
                    $null -eq $adaptive -or
                    [Math]::Abs([double]$adaptive.diagnostic_RW - [double]$definition.RW) -gt 0.001 -or
                    $adaptive.physical_damage_changed_by_prototype -or
                    $adaptive.Adaptive_state_changed_by_prototype -or
                    $adaptive.direct_TNO_wound_write) {
                    throw "P3 Adaptive-wound/Severance invariant failed at Lv${level}/$($definition.Role)/hit$($row.hit_index)."
                }
            }
        }

        foreach ($cycleRecord in $cellCycles) {
            $cycle = $cycleRecord.Value
            $expectedActual = [Math]::Min([double]$cycle.requested_healing,
                [double]$cycle.legal_healing_space)
            if ($cycle.P3_profile_role -ne $definition.Role -or
                $cycle.Regenerate_rank -ne $expectedRank -or
                [Math]::Abs([double]$cycle.requested_healing - $expectedRequest) -gt $tolerance -or
                $cycle.target_tick_count -lt 20 -or
                -not $cycle.native_Regenerate_stack_verified -or
                -not $cycle.cycle_complete -or
                -not $cycle.SHP_unchanged_by_Regenerate -or
                -not $cycle.no_heal_above_wound_ceiling -or
                [Math]::Abs([double]$cycle.expected_actual_healing - $expectedActual) -gt $tolerance -or
                [Math]::Abs([double]$cycle.actual_healing - $expectedActual) -gt $tolerance -or
                [double]$cycle.event_allowed_healing + $tolerance -lt $expectedActual -or
                [double]$cycle.event_allowed_healing -gt [double]$cycle.requested_healing + $tolerance -or
                [Math]::Abs([double]$cycle.denied_healing -
                    ([double]$cycle.requested_healing - [double]$cycle.actual_healing)) -gt $tolerance -or
                [Math]::Abs([double]$cycle.HP_after_Regenerate -
                    ([double]$cycle.HP_before_Regenerate + [double]$cycle.actual_healing)) -gt $tolerance -or
                $cycle.production_Magic_Holy_behavior_changed -or
                $cycle.direct_TNO_wound_write -or
                $cycle.source_event_integrity_failure_count -ne 0 -or
                $cycle.unexpected_L2_bypass_count -ne 0 -or
                $cycle.unexpected_Tensura_bypass_count -ne 0) {
                throw "P3 Regenerate cycle invariant failed at Lv${level}/$($definition.Role)/cycle$($cycle.cycle_index)."
            }
        }
    }

    $on = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.P3_profile_role -eq 'CANDIDATE_C_RW_50_REGENERATE_ON'
    })[0].Value
    $off = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.P3_profile_role -eq 'CANDIDATE_C_RW_50_WITHOUT_REGENERATE'
    })[0].Value
    $nativeControl = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.P3_profile_role -eq 'NATIVE_RW_0_REGENERATE_ON_CONTROL'
    })[0].Value
    if ([double]$on.regenerate_actual_healing -le 0 -or
        [double]$nativeControl.regenerate_actual_healing -le 0 -or
        [double]$on.final_HP -le [double]$off.final_HP + $tolerance -or
        [double]$on.net_combined_resource_movement -ge
            [double]$off.net_combined_resource_movement - $tolerance) {
        throw "P3 dynamic defender advantage was not demonstrated at Lv${level}."
    }
}

$resolvedOutput = [IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
[IO.Directory]::CreateDirectory((Split-Path -Parent $resolvedOutput)) | Out-Null
[IO.File]::WriteAllLines($resolvedOutput,
    [string[]]($records | ForEach-Object { $_.Json }), [Text.UTF8Encoding]::new($false))

$actualTotal = ($cycles.Value | Measure-Object actual_healing -Sum).Sum
$deniedTotal = ($cycles.Value | Measure-Object denied_healing -Sum).Sum
Write-Host 'Validated P3 dynamic capture: 9 cases, 540 Royal Arrow rows, 360 native Regenerate cycles, zero errors.'
Write-Host "Actual/denied native healing: $actualTotal / $deniedTotal"
Write-Host "Wrote $($records.Count) records to $resolvedOutput"
