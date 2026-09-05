param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_ADAPTIVE_WOUND '
$schema = 'tno.phase6.adaptive_wound.w3.v1'
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$records = [Collections.Generic.List[object]]::new()

foreach ($line in ([IO.File]::ReadAllLines($resolvedLog))) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -lt 0) { continue }
    $json = $line.Substring($index + $marker.Length)
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json -Depth 100 }
    catch { throw "Malformed adaptive-wound JSON in ${resolvedLog}: $json" }
    if ($value.schema -ne $schema) { continue }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$starts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$results = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -in @('case_error', 'suite_error') })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1 -or $starts.Count -ne 6 -or $rows.Count -ne 60 -or
    $results.Count -ne 6 -or $suites.Count -ne 1) {
    throw "Expected 1/6/60/6/1 catalog/start/row/result/suite records; found $($catalogs.Count)/$($starts.Count)/$($rows.Count)/$($results.Count)/$($suites.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) error record(s)." }

$catalog = $catalogs[0].Value
$suite = $suites[0].Value
if ($catalog.TNO_family -ne 'SEVERANCE' -or
    $catalog.calibration_mode -ne 'adaptive_wound_capability' -or
    $catalog.W3_candidate -ne 'C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY' -or
    -not $catalog.prototype_development_only -or
    $catalog.prototype_changes_physical_damage -or
    $catalog.prototype_changes_Royal_Arrow_base -or
    $catalog.prototype_creates_physical_source -or
    $catalog.prototype_writes_wound_directly -or
    $catalog.prototype_changes_Adaptive_state -or
    $catalog.prototype_changes_Tank -or
    $catalog.prototype_changes_Dementor -or
    $catalog.prototype_changes_Regenerate -or
    $catalog.prototype_has_persistent_combat_state -or
    -not $catalog.prototype_native_callback_storage -or
    $catalog.production_balance_mutated -or
    $catalog.production_combat_mutated -or
    $catalog.APO_profile -ne 'NONE' -or
    $catalog.shots_per_case -ne 10 -or
    $catalog.fixed_window_ticks -ne 200 -or
    $suite.status -ne 'complete' -or
    $suite.case_count -ne 6 -or
    $suite.requested_case_count -ne 6) {
    throw 'Catalog or suite_result does not match the locked W3 protocol.'
}

$caseRws = @{
    WOUND_RW_0_NATIVE_CONTROL = 0.0
    WOUND_RW_100_CAPABILITY_EXTREME = 1.0
}

foreach ($level in @(600, 800, 1000)) {
    foreach ($caseName in $caseRws.Keys) {
        $expectedRw = [double]$caseRws[$caseName]
        $caseStarts = @($starts | Where-Object {
            $_.Value.level -eq $level -and $_.Value.calibration_case -eq $caseName -and
            [double]$_.Value.wound_Adaptive_recovery_RW -eq $expectedRw
        })
        $caseResults = @($results | Where-Object {
            $_.Value.level -eq $level -and $_.Value.calibration_case -eq $caseName -and
            [double]$_.Value.wound_Adaptive_recovery_RW -eq $expectedRw
        })
        $caseRows = @($rows | Where-Object {
            $_.Value.level -eq $level -and $_.Value.calibration_case -eq $caseName -and
            [double]$_.Value.wound_Adaptive_recovery_RW -eq $expectedRw
        })
        if ($caseStarts.Count -ne 1 -or $caseResults.Count -ne 1 -or $caseRows.Count -ne 10) {
            throw "Missing or duplicate records for Lv${level}/$caseName."
        }
        $indices = @($caseRows.Value.hit_index | Sort-Object)
        if (($indices -join ',') -ne '1,2,3,4,5,6,7,8,9,10') {
            throw "Lv${level}/$caseName does not contain exactly hit indices 1-10."
        }
    }
}

foreach ($record in $starts + $results) {
    $value = $record.Value
    if ($value.boss -ne 'tensura:orc_disaster' -or
        $value.level -notin @(600, 800, 1000) -or
        $value.TNO_family -ne 'SEVERANCE' -or
        $value.TNO_stage -ne 'S7' -or
        $value.calibration_mode -ne 'adaptive_wound_capability' -or
        $value.L2_profile_variant -ne 'ACCEPTED_STRONGEST_LEGAL' -or
        -not $value.profile_is_accepted_strongest_legal -or
        $value.APO_profile -ne 'NONE' -or
        $value.royal_arrow_mark_enabled -or
        -not $value.prototype_development_only -or
        $value.physical_damage_negotiated -or
        $value.native_Adaptive_state_mutated -or
        [double]$value.native_gear_EP -ne 2490000 -or
        $value.resolved_production_stage -ne 'S7') {
        throw "Case metadata violates W3 isolation for $($value.calibration_case)."
    }
}

$tolerance = 0.001
foreach ($record in $rows) {
    $value = $record.Value
    $wall = $value.severance_wall_trace
    $trace = $wall.adaptive_wound_architecture
    $rw = [double]$value.wound_Adaptive_recovery_RW
    $count = [int]$trace.Adaptive_count
    $nativeFactor = [Math]::Pow(0.5, $count - 1)
    $woundFactor = $nativeFactor + $rw * (1.0 - $nativeFactor)
    $ratio = if ([double]$trace.combined_physical_pre_L2 -gt 0) {
        [Math]::Max(0.0, [Math]::Min(1.0,
            [double]$trace.post_Dementor_physical / [double]$trace.combined_physical_pre_L2))
    } else { 0.0 }
    $eligiblePreAdaptive = [double]$trace.eligible_physical_post_round * $ratio
    $nativeEligible = 0.5 * $eligiblePreAdaptive * $nativeFactor
    $diagnosticEligible = 0.5 * $eligiblePreAdaptive * $woundFactor
    $extra = [Math]::Max(0.0, $diagnosticEligible - $nativeEligible)
    $offer = [Math]::Min([double]$trace.native_Severance_candidate,
        [double]$trace.native_post_clamp_offer + $extra)

    if ($value.boss -ne 'tensura:orc_disaster' -or
        $value.level -notin @(600, 800, 1000) -or
        $value.TNO_family -ne 'SEVERANCE' -or
        $value.TNO_stage -ne 'S7' -or
        $value.APO_profile -ne 'NONE' -or
        $value.projectile_entity_id -ne 'royalvariations:royal_arrow' -or
        $value.requested_ammo_item -ne 'royalvariations:royal_arrow' -or
        $value.released_projectile_count -ne 1 -or
        $value.physical_damage_event_count -ne 1 -or
        $value.physical_damage_source_id -ne 'minecraft:arrow' -or
        @($value.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
        @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic' -or
        $value.severance_distinct_damage_source -or
        $value.severance_wall_trace_count -ne 1 -or
        $wall.adaptive_wound_trace_count -ne 1 -or
        $null -eq $trace -or
        $trace.physical_source_id -ne 'minecraft:arrow' -or
        $trace.physical_source_msgId -ne 'arrow' -or
        $trace.wound_state_identity -ne 'tensura:effect_storage' -or
        $trace.native_ceiling_source_id -ne 'tensura:severance' -or
        $trace.physical_damage_changed_by_prototype -or
        $trace.Adaptive_state_changed_by_prototype -or
        $trace.direct_TNO_wound_write -or
        $value.unexpected_source_duplication -or
        $value.event_recursion_observed -or
        $value.l2_layer_bypassed_unexpectedly -or
        $value.tensura_layer_bypassed_unexpectedly) {
        throw "W3 source/state invariant failed for $($value.calibration_case)/hit$($value.hit_index)."
    }

    if ([Math]::Abs([double]$trace.native_callback_damage - [double]$trace.combined_physical_pre_L2) -gt $tolerance -or
        [Math]::Abs([double]$trace.native_Severance_candidate - (0.5 * [double]$trace.native_callback_damage)) -gt $tolerance -or
        [Math]::Abs([double]$trace.Tank_Dementor_survival_ratio - $ratio) -gt $tolerance -or
        [Math]::Abs([double]$trace.eligible_pre_Adaptive - $eligiblePreAdaptive) -gt $tolerance -or
        [Math]::Abs([double]$trace.Adaptive_native_factor - $nativeFactor) -gt $tolerance -or
        [Math]::Abs([double]$trace.diagnostic_wound_Adaptive_factor - $woundFactor) -gt $tolerance -or
        [Math]::Abs([double]$trace.native_eligible_wound_potential - $nativeEligible) -gt $tolerance -or
        [Math]::Abs([double]$trace.diagnostic_eligible_wound_potential - $diagnosticEligible) -gt $tolerance -or
        [Math]::Abs([double]$trace.diagnostic_eligible_extra - $extra) -gt $tolerance -or
        [Math]::Abs([double]$trace.negotiated_native_storage_offer - $offer) -gt $tolerance -or
        [Math]::Abs([double]$trace.post_Adaptive_physical - [double]$value.combined_physical_post_damage) -gt $tolerance -or
        [Math]::Abs([double]$trace.native_Severance_Protection_adjusted_increment -
            ([double]$trace.wound_after_native_storage - [double]$trace.wound_before_native_storage)) -gt $tolerance -or
        [Math]::Abs([double]$trace.native_Severance_Protection_multiplier - 1.0) -gt $tolerance -or
        [Math]::Abs([double]$value.severance_base_projectile_damage - 2.4) -gt $tolerance -or
        [Math]::Abs([double]$value.severance_base_only_post_round - 8.0) -gt $tolerance -or
        [Math]::Abs([double]$value.severance_native_attack_bonus - 3.0) -gt $tolerance -or
        [Math]::Abs([double]$value.severance_production_eligible_contribution - 4.2) -gt $tolerance -or
        [double]$trace.wound_after_native_storage + $tolerance -lt [double]$trace.wound_before_native_storage) {
        throw "W3 arithmetic/storage invariant failed for $($value.calibration_case)/hit$($value.hit_index)."
    }

    if ($value.native_severance_incoming_event_count -ne $value.native_severance_after_L2_event_count -or
        [Math]::Abs([double]$value.native_severance_incoming_amount -
            [double]$value.native_severance_after_L2_amount) -gt $tolerance -or
        $value.native_severance_incoming_cancelled -or
        $value.native_severance_damage_pre_event_count -ne
            $value.native_severance_damage_post_event_count -or
        [Math]::Abs([double]$value.native_severance_damage_pre_amount -
            [double]$value.native_severance_damage_post_amount) -gt $tolerance -or
        $value.native_severance_damage_post_event_count -gt 1 -or
        $value.native_severance_damage_post_event_count -gt
            $value.native_severance_incoming_event_count -or
        [Math]::Abs([double]$value.native_severance_damage_post_amount -
            [double]$value.DoT_damage) -gt $tolerance) {
        throw "Native ceiling-source invariant failed for $($value.calibration_case)/hit$($value.hit_index)."
    }
    if ($value.native_severance_incoming_event_count -gt 0 -and
        ((@($value.native_severance_source_entity_ids) -join ',') -ne 'NONE' -or
         (@($value.native_severance_direct_entity_ids) -join ',') -ne 'NONE')) {
        throw "Native ceiling source unexpectedly gained an entity for $($value.calibration_case)/hit$($value.hit_index)."
    }

    if ($rw -eq 0.0 -and
        ([Math]::Abs([double]$trace.diagnostic_eligible_extra) -gt $tolerance -or
         [Math]::Abs([double]$trace.negotiated_native_storage_offer - [double]$trace.native_post_clamp_offer) -gt $tolerance)) {
        throw "RW=0 was not an exact native storage-offer control at hit $($value.hit_index)."
    }
}

foreach ($level in @(600, 800, 1000)) {
    $control = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.calibration_case -eq 'WOUND_RW_0_NATIVE_CONTROL'
    })[0].Value
    $extreme = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.calibration_case -eq 'WOUND_RW_100_CAPABILITY_EXTREME'
    })[0].Value
    if (($control.trait_ranks | ConvertTo-Json -Compress) -ne
        ($extreme.trait_ranks | ConvertTo-Json -Compress)) {
        throw "RW cases do not use the same exact L2 traits at Lv${level}."
    }
    if ([double]$extreme.final_SHP -ne [double]$control.final_SHP) {
        throw "RW changed SHP outcome at Lv${level}."
    }
    $controlWound = (($rows | Where-Object {
        $_.Value.level -eq $level -and $_.Value.calibration_case -eq 'WOUND_RW_0_NATIVE_CONTROL'
    }).Value | Measure-Object severance_amount_delta -Sum).Sum
    $extremeWound = (($rows | Where-Object {
        $_.Value.level -eq $level -and $_.Value.calibration_case -eq 'WOUND_RW_100_CAPABILITY_EXTREME'
    }).Value | Measure-Object severance_amount_delta -Sum).Sum
    if ([double]$extremeWound -le [double]$controlWound + $tolerance) {
        throw "RW=1 did not increase eligible wound storage at Lv${level}."
    }
}

$rwOneRows = @($rows | Where-Object { [double]$_.Value.wound_Adaptive_recovery_RW -eq 1.0 })
if (@($rwOneRows | Where-Object {
    [double]$_.Value.severance_wall_trace.adaptive_wound_architecture.diagnostic_eligible_extra -gt $tolerance
}).Count -lt 1) {
    throw 'RW=1 never demonstrated additional eligible wound capability.'
}

foreach ($record in $results) {
    $value = $record.Value
    if ($value.status -ne 'ok' -or
        $value.shots_released -ne 10 -or
        $value.hits_recorded -ne 10 -or
        $value.elapsed_ticks -ne 200 -or
        $value.severance_wall_trace_count -ne 10 -or
        $value.hurt_success_count -ne 10 -or
        $value.wound_attempt_count -ne 10 -or
        $value.wound_success_count -ne 10) {
        throw "Case result failed W3 count invariants for $($value.calibration_case)."
    }
}

$resolvedOutput = [IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
$outputDirectory = Split-Path -Parent $resolvedOutput
[IO.Directory]::CreateDirectory($outputDirectory) | Out-Null
[IO.File]::WriteAllLines($resolvedOutput, [string[]]($records | ForEach-Object { $_.Json }), [Text.UTF8Encoding]::new($false))

Write-Host "Validated W3 adaptive-wound capture: 6 cases, 60 per-hit rows, zero errors."
Write-Host "Wrote $($records.Count) records to $resolvedOutput"
