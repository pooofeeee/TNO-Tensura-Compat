param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_ADAPTIVE_WOUND '
$schema = 'tno.phase6.regenerate_severance_counter_protocol.p2.v1'
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$records = [Collections.Generic.List[object]]::new()

foreach ($line in [IO.File]::ReadAllLines($resolvedLog)) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -lt 0) { continue }
    $json = $line.Substring($index + $marker.Length)
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json -Depth 100 }
    catch { throw "Malformed P2 JSON in ${resolvedLog}: $json" }
    if ($value.schema -ne $schema) { continue }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$starts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$states = @($records | Where-Object { $_.Value.kind -eq 'counter_state_result' })
$results = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -in @('case_error', 'suite_error') })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1 -or $starts.Count -ne 10 -or $rows.Count -ne 8 -or
    $states.Count -ne 10 -or $results.Count -ne 10 -or $suites.Count -ne 1) {
    throw "Expected 1/10/8/10/10/1 catalog/start/row/state/result/suite records; found $($catalogs.Count)/$($starts.Count)/$($rows.Count)/$($states.Count)/$($results.Count)/$($suites.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) error record(s)." }

$catalog = $catalogs[0].Value
$suite = $suites[0].Value
if ($catalog.calibration_mode -ne 'adaptive_wound_counter_states' -or
    $catalog.checkpoint -ne 'P2_COUNTER_STATES' -or
    $catalog.P2_candidate -ne 'C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY' -or
    [double]$catalog.P2_diagnostic_RW -ne 0.5 -or
    -not $catalog.prototype_development_only -or
    $catalog.prototype_changes_physical_damage -or
    $catalog.prototype_changes_Royal_Arrow_base -or
    $catalog.prototype_creates_physical_source -or
    $catalog.prototype_writes_wound_directly -or
    $catalog.prototype_changes_Adaptive_state -or
    $catalog.prototype_changes_Regenerate -or
    $catalog.P2_setup_changes_wound_directly -or
    $catalog.P2_setup_counted_as_combat_output -or
    $catalog.production_balance_mutated -or $catalog.production_combat_mutated -or
    $catalog.APO_profile -ne 'NONE' -or
    $catalog.shots_per_case -ne 1 -or $catalog.fixed_window_ticks -ne 40 -or
    $suite.status -ne 'complete' -or $suite.case_count -ne 10 -or
    $suite.requested_case_count -ne 10) {
    throw 'Catalog or suite_result does not match the locked P2 protocol.'
}

$caseDefinitions = [ordered]@{
    COUNTER_STATE_A_BELOW_CEILING = 'A_BELOW_CEILING'
    COUNTER_STATE_B_CROSSING_CEILING = 'B_CROSSING_CEILING'
    COUNTER_STATE_C_AT_CEILING = 'C_AT_CEILING'
    COUNTER_NO_REGENERATE_CONTROL = 'NO_REGENERATE_CONTROL'
    COUNTER_NO_WOUND_CONTROL = 'NO_WOUND_CONTROL'
}
$tolerance = 0.01

foreach ($level in @(600, 1000)) {
    $expectedRank = if ($level -eq 600) { 4 } else { 5 }
    $expectedRequest = if ($level -eq 600) { 400.0 } else { 500.0 }
    foreach ($calibration in $caseDefinitions.Keys) {
        $stateId = $caseDefinitions[$calibration]
        $cellStarts = @($starts | Where-Object {
            $_.Value.level -eq $level -and $_.Value.calibration_case -eq $calibration
        })
        $cellStates = @($states | Where-Object {
            $_.Value.level -eq $level -and $_.Value.calibration_case -eq $calibration
        })
        $cellResults = @($results | Where-Object {
            $_.Value.level -eq $level -and $_.Value.calibration_case -eq $calibration
        })
        if ($cellStarts.Count -ne 1 -or $cellStates.Count -ne 1 -or $cellResults.Count -ne 1) {
            throw "Missing or duplicate P2 cell Lv${level}/$calibration."
        }
        $value = $cellStates[0].Value
        $summary = $cellResults[0].Value
        if ($value.P2_counter_state -ne $stateId -or
            $value.boss -ne 'tensura:orc_disaster' -or
            $value.TNO_family -ne 'SEVERANCE' -or $value.TNO_stage -ne 'S7' -or
            [double]$value.P2_diagnostic_RW -ne 0.5 -or
            $value.APO_profile -ne 'NONE' -or -not $value.diagnostic_setup_only -or
            $value.setup_health_placement_counted_as_combat_output -or
            $value.wound_written_directly_by_TNO -or
            $value.native_tick_boundary_count -ne 1 -or
            -not $value.state_condition_verified -or
            -not $value.native_counter_contract_matched -or
            $value.source_event_integrity_failure_count -ne 0 -or
            $value.duplicate_physical_event_count -ne 0 -or
            $value.recursion_count -ne 0 -or
            $value.unexpected_L2_bypass_count -ne 0 -or
            $value.unexpected_Tensura_bypass_count -ne 0 -or
            [Math]::Abs([double]$value.SHP_after_Regenerate -
                [double]$value.SHP_before_Regenerate) -gt $tolerance) {
            throw "P2 common invariant failed at Lv${level}/$stateId."
        }
        if ([Math]::Abs([double]$value.reference_native_Regenerate_request -
                $expectedRequest) -gt $tolerance) {
            throw "P2 native request reference mismatch at Lv${level}/$stateId."
        }

        $requiresWound = $stateId -ne 'NO_WOUND_CONTROL'
        $expectedArrows = if ($requiresWound) { 1 } else { 0 }
        if ([bool]$value.wound_required -ne $requiresWound -or
            [bool]$value.wound_created_by_native_Royal_Arrow -ne $requiresWound -or
            $value.setup_arrow_count -ne $expectedArrows -or
            $summary.shots_released -ne $expectedArrows -or
            $summary.hits_recorded -ne $expectedArrows) {
            throw "P2 wound/setup provenance failed at Lv${level}/$stateId."
        }
        if ($requiresWound) {
            if ([double]$value.setup_wound_amount -le 0 -or
                $value.setup_physical_source_count -ne 1 -or
                $value.setup_native_wound_callback_count -ne 1) {
                throw "P2 native wound was not created by exactly one arrow at Lv${level}/$stateId."
            }
        }
        elseif ([Math]::Abs([double]$value.setup_wound_amount) -gt $tolerance -or
            $value.setup_physical_source_count -ne 0 -or
            $value.setup_native_wound_callback_count -ne 0) {
            throw "P2 no-wound control contains wound/arrow output at Lv${level}."
        }

        $actual = [double]$value.actual_healing
        $requested = [double]$value.requested_healing
        $legal = [double]$value.legal_healing_space
        $allowed = [double]$value.event_allowed_healing
        $denied = [double]$value.denied_healing
        $expectedActual = [Math]::Min($requested, $legal)
        if ([Math]::Abs($actual - $expectedActual) -gt $tolerance -or
            [Math]::Abs($allowed - $expectedActual) -gt $tolerance -or
            [Math]::Abs($denied - ($requested - $actual)) -gt $tolerance -or
            [Math]::Abs([double]$value.HP_after_Regenerate -
                ([double]$value.HP_before_Regenerate + $actual)) -gt $tolerance -or
            [Math]::Abs([double]$summary.final_HP - [double]$value.HP_after_Regenerate) -gt $tolerance) {
            throw "P2 healing arithmetic failed at Lv${level}/$stateId."
        }

        if ($stateId -eq 'NO_REGENERATE_CONTROL') {
            if ($value.Regenerate_rank -ne 0 -or $value.Regenerate_trait_rank_at_end -ne 0 -or
                $value.heal_event_observed -or $value.regenerate_callback_count -ne 0 -or
                $value.regenerate_native_tick_attempt_count -ne 0 -or
                $requested -ne 0 -or $actual -ne 0) {
                throw "P2 no-Regenerate control failed at Lv${level}."
            }
        }
        else {
            if ($value.Regenerate_rank -ne $expectedRank -or
                $value.Regenerate_trait_rank_at_end -ne $expectedRank -or
                -not $value.Regenerate_trait_valid_on_all_observed_attempts -or
                -not $value.heal_event_observed -or
                -not $value.native_Regenerate_stack_verified -or
                $value.regenerate_callback_count -ne 1 -or
                $value.regenerate_native_tick_attempt_count -ne 1 -or
                [Math]::Abs($requested - $expectedRequest) -gt $tolerance) {
                throw "P2 native Regenerate identity failed at Lv${level}/$stateId."
            }
        }

        switch ($stateId) {
            'A_BELOW_CEILING' {
                if ($value.heal_event_cancelled -or $legal + $tolerance -lt $requested -or
                    [Math]::Abs($actual - $requested) -gt $tolerance -or $denied -gt $tolerance) {
                    throw "P2 State A failed at Lv${level}."
                }
            }
            'B_CROSSING_CEILING' {
                if ($value.heal_event_cancelled -or $legal -le $tolerance -or
                    $legal -ge $requested - $tolerance -or
                    [Math]::Abs($actual - $legal) -gt $tolerance) {
                    throw "P2 State B failed at Lv${level}."
                }
            }
            'C_AT_CEILING' {
                if (-not $value.heal_event_cancelled -or $legal -gt $tolerance -or
                    $actual -gt $tolerance -or
                    [Math]::Abs($denied - $requested) -gt $tolerance) {
                    throw "P2 State C failed at Lv${level}."
                }
            }
            'NO_WOUND_CONTROL' {
                if ($value.heal_event_cancelled -or $actual -le 0 -or
                    [Math]::Abs($actual - $requested) -gt $tolerance) {
                    throw "P2 no-wound Regenerate control failed at Lv${level}."
                }
            }
        }
    }
}

foreach ($record in $rows) {
    $value = $record.Value
    $wall = $value.severance_wall_trace
    if ($value.calibration_case -eq 'COUNTER_NO_WOUND_CONTROL' -or
        $value.boss -ne 'tensura:orc_disaster' -or
        $value.projectile_entity_id -ne 'royalvariations:royal_arrow' -or
        $value.released_projectile_count -ne 1 -or
        $value.physical_damage_event_count -ne 1 -or
        $value.physical_damage_source_id -ne 'minecraft:arrow' -or
        @($value.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
        @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic' -or
        $value.severance_wall_trace_count -ne 1 -or
        $wall.adaptive_wound_trace_count -ne 1 -or
        $wall.adaptive_wound_architecture.physical_damage_changed_by_prototype -or
        $wall.adaptive_wound_architecture.Adaptive_state_changed_by_prototype -or
        $wall.adaptive_wound_architecture.direct_TNO_wound_write -or
        $value.unexpected_source_duplication -or $value.event_recursion_observed -or
        $value.l2_layer_bypassed_unexpectedly -or
        $value.tensura_layer_bypassed_unexpectedly) {
        throw "P2 setup-arrow source invariant failed at Lv$($value.level)/$($value.P2_counter_state)."
    }
}

$resolvedOutput = [IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
[IO.Directory]::CreateDirectory((Split-Path -Parent $resolvedOutput)) | Out-Null
[IO.File]::WriteAllLines($resolvedOutput,
    [string[]]($records | ForEach-Object { $_.Json }), [Text.UTF8Encoding]::new($false))

$requestedTotal = ($states.Value | Measure-Object requested_healing -Sum).Sum
$actualTotal = ($states.Value | Measure-Object actual_healing -Sum).Sum
$deniedTotal = ($states.Value | Measure-Object denied_healing -Sum).Sum
Write-Host 'Validated P2 counter-state capture: 10 cases, 8 setup-arrow rows, 10 counter-state results, zero errors.'
Write-Host "Requested/actual/denied healing: $requestedTotal / $actualTotal / $deniedTotal"
Write-Host "Wrote $($records.Count) records to $resolvedOutput"
