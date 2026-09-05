param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_ADAPTIVE_WOUND '
$schema = 'tno.phase6.adaptive_wound.w4.v1'
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$records = [Collections.Generic.List[object]]::new()

foreach ($line in [IO.File]::ReadAllLines($resolvedLog)) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -lt 0) { continue }
    $json = $line.Substring($index + $marker.Length)
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json -Depth 100 }
    catch { throw "Malformed W4 JSON in ${resolvedLog}: $json" }
    if ($value.schema -ne $schema) { continue }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$starts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$results = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -in @('case_error', 'suite_error') })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1 -or $starts.Count -ne 15 -or $rows.Count -ne 150 -or
    $results.Count -ne 15 -or $suites.Count -ne 1) {
    throw "Expected 1/15/150/15/1 catalog/start/row/result/suite records; found $($catalogs.Count)/$($starts.Count)/$($rows.Count)/$($results.Count)/$($suites.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) error record(s)." }

$catalog = $catalogs[0].Value
$suite = $suites[0].Value
if ($catalog.calibration_mode -ne 'adaptive_wound_safety' -or
    $catalog.checkpoint -ne 'W4_TRAIT_IDENTITY' -or
    $catalog.W4_candidate -ne 'C_PARTIAL_ADAPTIVE_RECOVERY_WOUND_ONLY' -or
    [double]$catalog.W4_diagnostic_RW -ne 0.5 -or
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
    $catalog.production_balance_mutated -or
    $catalog.production_combat_mutated -or
    $catalog.APO_profile -ne 'NONE' -or
    $catalog.shots_per_case -ne 10 -or $catalog.fixed_window_ticks -ne 200 -or
    $suite.status -ne 'complete' -or $suite.case_count -ne 15 -or
    $suite.requested_case_count -ne 15) {
    throw 'Catalog or suite_result does not match the locked W4 protocol.'
}

$profiles = @{
    ACCEPTED_STRONGEST_LEGAL = $null
    WITHOUT_TANK_CONTROL = 'l2hostility:tank'
    WITHOUT_DEMENTOR_CONTROL = 'l2hostility:dementor'
    WITHOUT_ADAPTIVE_CONTROL = 'l2hostility:adaptive'
    WITHOUT_REGENERATE_CONTROL = 'l2hostility:regenerate'
}

foreach ($level in @(600, 800, 1000)) {
    foreach ($profile in $profiles.Keys) {
        $cellStarts = @($starts | Where-Object {
            $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile
        })
        $cellResults = @($results | Where-Object {
            $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile
        })
        $cellRows = @($rows | Where-Object {
            $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile
        })
        if ($cellStarts.Count -ne 1 -or $cellResults.Count -ne 1 -or $cellRows.Count -ne 10) {
            throw "Missing or duplicate W4 cell Lv${level}/$profile."
        }
        if ((@($cellRows.Value.hit_index | Sort-Object) -join ',') -ne '1,2,3,4,5,6,7,8,9,10') {
            throw "Lv${level}/$profile does not contain hit indices 1-10."
        }
    }

    $accepted = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq 'ACCEPTED_STRONGEST_LEGAL'
    })[0].Value
    $acceptedRanks = @{}
    $accepted.trait_ranks.PSObject.Properties | ForEach-Object { $acceptedRanks[$_.Name] = $_.Value }
    foreach ($profile in $profiles.Keys | Where-Object { $_ -ne 'ACCEPTED_STRONGEST_LEGAL' }) {
        $control = ($results | Where-Object {
            $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile
        })[0].Value
        $expected = $acceptedRanks.Clone()
        $expected.Remove($profiles[$profile])
        $actual = @{}
        $control.trait_ranks.PSObject.Properties | ForEach-Object { $actual[$_.Name] = $_.Value }
        $same = $expected.Count -eq $actual.Count
        foreach ($trait in $expected.Keys) {
            $same = $same -and $actual.ContainsKey($trait) -and
                [int]$actual[$trait] -eq [int]$expected[$trait]
        }
        if (-not $same) { throw "$profile at Lv${level} did not remove exactly one trait." }
    }
}

$tolerance = 0.001
foreach ($record in $rows) {
    $value = $record.Value
    $wall = $value.severance_wall_trace
    $trace = $wall.adaptive_wound_architecture
    $adaptive = $value.L2_profile_variant -ne 'WITHOUT_ADAPTIVE_CONTROL'
    $expectedFactor = if ($adaptive) { [Math]::Pow(0.5, [int]$trace.Adaptive_count - 1) } else { 1.0 }
    $woundFactor = $expectedFactor + 0.5 * (1.0 - $expectedFactor)
    $ratio = [Math]::Max(0.0, [Math]::Min(1.0,
        [double]$trace.post_Dementor_physical / [double]$trace.combined_physical_pre_L2))
    $eligiblePreAdaptive = [double]$trace.eligible_physical_post_round * $ratio
    $nativeEligible = 0.5 * $eligiblePreAdaptive * $expectedFactor
    $diagnosticEligible = 0.5 * $eligiblePreAdaptive * $woundFactor
    $extra = [Math]::Max(0.0, $diagnosticEligible - $nativeEligible)
    $offer = [Math]::Min([double]$trace.native_Severance_candidate,
        [double]$trace.native_post_clamp_offer + $extra)

    if ($value.boss -ne 'tensura:orc_disaster' -or
        $value.level -notin @(600, 800, 1000) -or
        $value.TNO_family -ne 'SEVERANCE' -or $value.TNO_stage -ne 'S7' -or
        $value.calibration_case -ne 'WOUND_RW_50_TRAIT_IDENTITY_DIAGNOSTIC' -or
        [double]$value.wound_Adaptive_recovery_RW -ne 0.5 -or
        $value.APO_profile -ne 'NONE' -or $value.royal_arrow_mark_enabled -or
        $value.released_projectile_count -ne 1 -or
        $value.projectile_entity_id -ne 'royalvariations:royal_arrow' -or
        $value.physical_damage_event_count -ne 1 -or
        $value.physical_damage_source_id -ne 'minecraft:arrow' -or
        @($value.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
        @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic' -or
        $value.severance_distinct_damage_source -or
        $value.severance_wall_trace_count -ne 1 -or $wall.adaptive_wound_trace_count -ne 1 -or
        $trace.physical_damage_changed_by_prototype -or
        $trace.Adaptive_state_changed_by_prototype -or $trace.direct_TNO_wound_write -or
        $value.unexpected_source_duplication -or $value.event_recursion_observed -or
        $value.l2_layer_bypassed_unexpectedly -or $value.tensura_layer_bypassed_unexpectedly) {
        throw "W4 source/scope invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/hit$($value.hit_index)."
    }

    if ([Math]::Abs([double]$trace.native_callback_damage - [double]$trace.combined_physical_pre_L2) -gt $tolerance -or
        [Math]::Abs([double]$trace.Adaptive_native_factor - $expectedFactor) -gt $tolerance -or
        [Math]::Abs([double]$trace.diagnostic_wound_Adaptive_factor - $woundFactor) -gt $tolerance -or
        [Math]::Abs([double]$trace.eligible_pre_Adaptive - $eligiblePreAdaptive) -gt $tolerance -or
        [Math]::Abs([double]$trace.native_eligible_wound_potential - $nativeEligible) -gt $tolerance -or
        [Math]::Abs([double]$trace.diagnostic_eligible_wound_potential - $diagnosticEligible) -gt $tolerance -or
        [Math]::Abs([double]$trace.diagnostic_eligible_extra - $extra) -gt $tolerance -or
        [Math]::Abs([double]$trace.negotiated_native_storage_offer - $offer) -gt $tolerance -or
        [Math]::Abs([double]$trace.post_Adaptive_physical - [double]$value.combined_physical_post_damage) -gt $tolerance -or
        [Math]::Abs([double]$trace.native_Severance_Protection_multiplier - 1.0) -gt $tolerance -or
        [Math]::Abs([double]$value.severance_base_projectile_damage - 2.4) -gt $tolerance -or
        [Math]::Abs([double]$value.severance_base_only_post_round - 8.0) -gt $tolerance) {
        throw "W4 arithmetic/native-wall invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/hit$($value.hit_index)."
    }
    if (-not $adaptive -and ([int]$trace.Adaptive_rank -ne 0 -or
        [int]$trace.Adaptive_count -ne 0 -or [Math]::Abs($extra) -gt $tolerance)) {
        throw "RW changed wound credit without Adaptive at Lv$($value.level)/hit$($value.hit_index)."
    }

    if ($value.native_severance_incoming_event_count -ne $value.native_severance_after_L2_event_count -or
        [Math]::Abs([double]$value.native_severance_incoming_amount -
            [double]$value.native_severance_after_L2_amount) -gt $tolerance -or
        $value.native_severance_incoming_cancelled -or
        $value.native_severance_damage_pre_event_count -ne $value.native_severance_damage_post_event_count -or
        [Math]::Abs([double]$value.native_severance_damage_pre_amount -
            [double]$value.native_severance_damage_post_amount) -gt $tolerance -or
        $value.native_severance_damage_post_event_count -gt 1 -or
        [Math]::Abs([double]$value.native_severance_damage_post_amount - [double]$value.DoT_damage) -gt $tolerance) {
        throw "W4 ceiling-source invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/hit$($value.hit_index)."
    }
}

foreach ($record in $results) {
    $value = $record.Value
    if ($value.status -ne 'ok' -or $value.shots_released -ne 10 -or
        $value.hits_recorded -ne 10 -or $value.elapsed_ticks -ne 200 -or
        $value.severance_wall_trace_count -ne 10 -or $value.hurt_success_count -ne 10 -or
        $value.wound_attempt_count -ne 10 -or $value.wound_success_count -ne 10 -or
        $value.source_event_integrity_failure_count -ne 0 -or
        $value.unexpected_L2_bypass_count -ne 0 -or $value.unexpected_Tensura_bypass_count -ne 0) {
        throw "W4 case-result invariant failed at Lv$($value.level)/$($value.L2_profile_variant)."
    }
    $hasRegenerate = $value.L2_profile_variant -ne 'WITHOUT_REGENERATE_CONTROL'
    if ($hasRegenerate) {
        if ($value.Regenerate_rank -le 0 -or $value.regenerate_native_tick_attempt_count -ne 10 -or
            $value.regenerate_callback_count -ne 10 -or -not $value.regenerate_trait_valid_at_start -or
            -not $value.regenerate_trait_valid_on_all_observed_attempts -or
            $value.regenerate_trait_rank_at_end -ne $value.Regenerate_rank -or
            $value.regenerate_trait_missing_tick_count -ne 0 -or
            [Math]::Abs([double]$value.regenerate_actual_healing_clock_vs_observer_delta) -gt $tolerance) {
            throw "Native Regenerate invariant failed at Lv$($value.level)/$($value.L2_profile_variant)."
        }
    }
    elseif ($value.Regenerate_rank -ne 0 -or $value.regenerate_native_tick_attempt_count -ne 0 -or
        $value.regenerate_callback_count -ne 0 -or [double]$value.regenerate_actual_healing -ne 0) {
        throw "No-Regenerate control retained Regenerate at Lv$($value.level)."
    }
}

$traitGateFailures = [Collections.Generic.List[string]]::new()
foreach ($level in @(600, 800, 1000)) {
    $accepted = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq 'ACCEPTED_STRONGEST_LEGAL'
    })[0].Value
    $noTank = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq 'WITHOUT_TANK_CONTROL'
    })[0].Value
    $noDementor = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq 'WITHOUT_DEMENTOR_CONTROL'
    })[0].Value
    $noAdaptive = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq 'WITHOUT_ADAPTIVE_CONTROL'
    })[0].Value
    $noRegenerate = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq 'WITHOUT_REGENERATE_CONTROL'
    })[0].Value
    if ([double]$accepted.severance_physical_damage -ge [double]$noTank.severance_physical_damage) {
        $traitGateFailures.Add("Tank@Lv${level}")
    }
    if ([double]$accepted.final_wound -ge [double]$noDementor.final_wound) {
        $traitGateFailures.Add("Dementor@Lv${level}")
    }
    if ([double]$accepted.final_wound -ge [double]$noAdaptive.final_wound) {
        $traitGateFailures.Add("Adaptive@Lv${level}")
    }
    if ([double]$accepted.net_vanilla_HP_movement -ge
        [double]$noRegenerate.net_vanilla_HP_movement) {
        $traitGateFailures.Add("Regenerate@Lv${level}")
    }
}

$resolvedOutput = [IO.Path]::GetFullPath((Join-Path (Get-Location) $OutputPath))
[IO.Directory]::CreateDirectory((Split-Path -Parent $resolvedOutput)) | Out-Null
[IO.File]::WriteAllLines($resolvedOutput,
    [string[]]($records | ForEach-Object { $_.Json }), [Text.UTF8Encoding]::new($false))

Write-Host 'Validated W4 Adaptive-wound safety capture: 15 cases, 150 rows, zero errors.'
Write-Host "Wrote $($records.Count) records to $resolvedOutput"
if ($traitGateFailures.Count -eq 0) {
    Write-Host 'W4 trait-identity decision gate: PASS'
}
else {
    Write-Warning "W4 trait-identity decision gate: FAIL ($($traitGateFailures -join ', '))"
}
