param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_SEVERANCE_SUSTAINED '
$schema = 'tno.phase6.severance_sustained.r5.v1'
$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$records = [Collections.Generic.List[object]]::new()

foreach ($line in ([IO.File]::ReadAllLines($resolvedLog))) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -ge 0) { $json = $line.Substring($index + $marker.Length) }
    else { $json = $line.Trim() }
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json -Depth 100 }
    catch { throw "Malformed R5 JSON in ${resolvedLog}: $json" }
    if ($value.schema -ne $schema) { continue }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$catalogs = @($records | Where-Object { $_.Value.kind -eq 'catalog' })
$starts = @($records | Where-Object { $_.Value.kind -eq 'case_start' })
$rows = @($records | Where-Object { $_.Value.kind -eq 'row' })
$results = @($records | Where-Object { $_.Value.kind -eq 'case_result' })
$errors = @($records | Where-Object { $_.Value.kind -in @('case_error', 'suite_error') })
$suites = @($records | Where-Object { $_.Value.kind -eq 'suite_result' })

if ($catalogs.Count -ne 1 -or $starts.Count -ne 18 -or $rows.Count -ne 1080 -or
    $results.Count -ne 18 -or $suites.Count -ne 1) {
    throw "Expected 1/18/1080/18/1 catalog/start/row/result/suite records; found $($catalogs.Count)/$($starts.Count)/$($rows.Count)/$($results.Count)/$($suites.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) error record(s)." }

$catalog = $catalogs[0].Value
$suite = $suites[0].Value
if ($catalog.TNO_family -ne 'SEVERANCE' -or $catalog.calibration_mode -ne 'severance_sustained' -or
    -not $catalog.R5_sustained_viability -or -not $catalog.R5_enchantment_exclusivity_preserved -or
    -not $catalog.R5_magic_holy_production_unchanged -or -not $catalog.prototype_development_only -or
    $catalog.prototype_changes_Royal_Arrow_base -or $catalog.prototype_creates_second_source -or
    $catalog.prototype_writes_wound_directly -or $catalog.production_balance_mutated -or
    $catalog.production_combat_mutated -or -not $catalog.development_only_combat_fixture_active -or
    $catalog.APO_profile -ne 'NONE' -or $catalog.shots_per_case -ne 60 -or
    $catalog.fixed_window_ticks -ne 1200 -or $suite.status -ne 'complete' -or
    $suite.case_count -ne 18 -or $suite.requested_case_count -ne 18) {
    throw 'Catalog or suite_result does not match the locked R5 protocol.'
}

$levels = @(600, 800, 1000)
$accepted = 'ACCEPTED_STRONGEST_LEGAL'
$profiles = @(
    $accepted,
    'WITHOUT_REGENERATE_CONTROL',
    'WITHOUT_TANK_CONTROL',
    'WITHOUT_DEMENTOR_CONTROL',
    'WITHOUT_ADAPTIVE_CONTROL'
)
$removed = @{
    ACCEPTED_STRONGEST_LEGAL = $null
    WITHOUT_REGENERATE_CONTROL = 'l2hostility:regenerate'
    WITHOUT_TANK_CONTROL = 'l2hostility:tank'
    WITHOUT_DEMENTOR_CONTROL = 'l2hostility:dementor'
    WITHOUT_ADAPTIVE_CONTROL = 'l2hostility:adaptive'
}

foreach ($level in $levels) {
    $x1 = @($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $accepted -and
        [double]$_.Value.Severance_eligible_multiplier -eq 1.0
    })
    if ($x1.Count -ne 1) { throw "Missing/duplicate accepted x1 case at Lv${level}." }
    foreach ($profile in $profiles) {
        $cell = @($results | Where-Object {
            $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile -and
            [double]$_.Value.Severance_eligible_multiplier -eq 64.0
        })
        if ($cell.Count -ne 1) { throw "Missing/duplicate x64 $profile case at Lv${level}." }
    }
}

foreach ($record in $starts + $results) {
    $value = $record.Value
    if ($value.boss -ne 'tensura:orc_disaster' -or $value.TNO_family -ne 'SEVERANCE' -or
        $value.TNO_stage -ne 'S7' -or $value.calibration_mode -ne 'severance_sustained' -or
        $value.APO_profile -ne 'NONE' -or $value.royal_arrow_mark_enabled -or
        -not $value.fresh_L2_attachment_per_case -or -not $value.prototype_development_only -or
        -not $value.R5_magic_holy_production_unchanged -or
        [double]$value.native_gear_EP -ne 2490000 -or $value.resolved_production_stage -ne 'S7' -or
        [double]$value.Q_generic_health -ne 1.0 -or [double]$value.RD_dementor -ne 0.75 -or
        [double]$value.RA_adaptive -ne 0.75 -or
        [double]$value.Magic_Holy_Q_generic_health -ne 1.0 -or
        [double]$value.Magic_Holy_RD_dementor -ne 0.75 -or
        [double]$value.Magic_Holy_RA_adaptive -ne 0.75 -or
        [double]$value.Severance_prototype_Q_generic_health -ne 0.0 -or
        [double]$value.Severance_prototype_RD_dementor -ne 0.0 -or
        [double]$value.Severance_prototype_RA_adaptive -ne 0.0) {
        throw "Case metadata violates the R5 production/prototype isolation at Lv$($value.level)/$($value.L2_profile_variant)/$($value.calibration_case)."
    }
    $factor = [double]$value.Severance_eligible_multiplier
    if ($factor -notin @(1.0, 64.0) -or $value.diagnostic_upper_bound_only -ne ($factor -eq 64.0)) {
        throw "Invalid diagnostic factor metadata at Lv$($value.level)/$($value.L2_profile_variant)."
    }
    if ($factor -eq 1.0 -and $value.L2_profile_variant -ne $accepted) {
        throw 'Ordinary Severance x1 is valid only for the accepted profile in R5.'
    }
    $removedTrait = $removed[$value.L2_profile_variant]
    if ($removedTrait -and $null -ne $value.trait_ranks.$removedTrait) {
        throw "Profile $($value.L2_profile_variant) retained $removedTrait."
    }
}

foreach ($level in $levels) {
    $acceptedResult = ($results | Where-Object {
        $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $accepted -and
        [double]$_.Value.Severance_eligible_multiplier -eq 64.0
    })[0].Value
    foreach ($profile in $profiles | Where-Object { $_ -ne $accepted }) {
        $control = ($results | Where-Object {
            $_.Value.level -eq $level -and $_.Value.L2_profile_variant -eq $profile
        })[0].Value
        $removedTrait = $removed[$profile]
        $acceptedRanks = @{}
        $acceptedResult.trait_ranks.PSObject.Properties | ForEach-Object { $acceptedRanks[$_.Name] = $_.Value }
        $controlRanks = @{}
        $control.trait_ranks.PSObject.Properties | ForEach-Object { $controlRanks[$_.Name] = $_.Value }
        $acceptedRanks.Remove($removedTrait)
        $sameRanks = $acceptedRanks.Count -eq $controlRanks.Count
        foreach ($trait in $acceptedRanks.Keys) {
            $sameRanks = $sameRanks -and $controlRanks.ContainsKey($trait) -and
                [int]$controlRanks[$trait] -eq [int]$acceptedRanks[$trait]
        }
        if (-not $sameRanks) {
            throw "Control $profile at Lv${level} is not the accepted profile with only $removedTrait removed."
        }
    }
}

$admitted = 0
$rejected = 0
$callbacks = 0
$woundStores = 0
foreach ($record in $rows) {
    $value = $record.Value
    $factor = [double]$value.Severance_eligible_multiplier
    $expectedFamily = switch (($value.hit_index - 1) % 3) {
        0 { 'MAGIC_WEAPON' }
        1 { 'HOLY_WEAPON' }
        2 { 'SEVERANCE' }
    }
    if ($value.rotation_family -ne $expectedFamily -or -not $value.legal_separate_bow_rotation -or
        $value.APO_profile -ne 'NONE' -or $value.royal_arrow_mark_enabled -or
        $value.released_projectile_count -ne 1 -or $value.projectile_entity_id -ne 'royalvariations:royal_arrow' -or
        $value.requested_ammo_item -ne 'royalvariations:royal_arrow' -or
        $value.unexpected_source_duplication -or $value.event_recursion_observed -or
        $value.l2_layer_bypassed_unexpectedly -or $value.tensura_layer_bypassed_unexpectedly) {
        throw "Shared per-hit invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/hit$($value.hit_index)."
    }

    if ($expectedFamily -in @('MAGIC_WEAPON', 'HOLY_WEAPON')) {
        $expectedEnchantment = if ($expectedFamily -eq 'MAGIC_WEAPON') { 'tensura:magic_weapon' } else { 'tensura:holy_weapon' }
        $expectedSource = if ($expectedFamily -eq 'MAGIC_WEAPON') { 'tensura:magic' } else { 'tensura:holy_damage' }
        if ($value.rotation_enchantment -ne $expectedEnchantment -or
            $value.physical_damage_event_count -ne 1 -or $value.engraving_damage_event_count -ne 1 -or
            $value.physical_damage_source_id -ne 'minecraft:arrow' -or
            $value.family_damage_source_id -ne $expectedSource -or
            [Math]::Abs([double]$value.engraving_native_amount - 8.0) -gt 0.001 -or
            [Math]::Abs([double]$value.engraving_after_stage_coefficient - 11.2) -gt 0.001 -or
            $value.severance_configured_projectile_count -ne 0 -or
            $value.severance_admitted_projectile_count -ne 0) {
            throw "Production Magic/Holy invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/hit$($value.hit_index)."
        }
        continue
    }

    $trace = $value.severance_wall_trace
    $productionEligible = 3.0 * 1.4
    $prototypeEligible = $productionEligible * $factor
    if ($value.rotation_enchantment -ne 'tensura:severance' -or
        $value.physical_damage_event_count -ne 1 -or $value.engraving_damage_event_count -ne 0 -or
        $value.physical_damage_source_id -ne 'minecraft:arrow' -or
        @($value.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
        @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic' -or
        $value.severance_distinct_damage_source -or $value.severance_wall_trace_count -ne 1 -or
        $null -eq $trace -or $trace.observation_only -or $trace.modifier_values_changed -or
        -not $trace.eligible_pre_hurt_prototype_active -or $trace.Royal_Arrow_base_changed_by_prototype -or
        $value.severance_base_affected_by_prototype -or
        [Math]::Abs([double]$value.physical_original_before_stage - 8.0) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_native_attack_bonus - 3.0) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_production_eligible_contribution - $productionEligible) -gt 0.001 -or
        [Math]::Abs([double]$value.severance_prototype_eligible_contribution - $prototypeEligible) -gt 0.001 -or
        [Math]::Abs([double]$trace.context_combined_physical - [double]$value.physical_combined_original_before_L2) -gt 0.001 -or
        [Math]::Abs([double]$trace.DamageData_original - [double]$value.physical_combined_original_before_L2) -gt 0.001) {
        throw "Eligible-only one-source Severance invariant failed at Lv$($value.level)/$($value.L2_profile_variant)/hit$($value.hit_index)."
    }
    if ($trace.final_hurt_returned_success) {
        $admitted++
        if (-not $trace.wound_attempted -or $trace.wound_attempt_count -ne 1 -or -not $trace.wound_stored) {
            throw "Admitted Severance hit lost its native callback/store at hit $($value.hit_index)."
        }
        $callbacks += [int]$trace.wound_attempt_count
        $woundStores++
    }
    else {
        $rejected++
        if ($trace.wound_attempted -or $trace.wound_attempt_count -ne 0 -or $trace.wound_stored) {
            throw "Rejected Severance hit reports a callback/store at hit $($value.hit_index)."
        }
    }
}

foreach ($record in $results) {
    $value = $record.Value
    if ($value.status -ne 'ok' -or $value.shots_released -ne 60 -or $value.hits_recorded -ne 60 -or
        $value.elapsed_ticks -ne 1200 -or $value.severance_release_count -ne 20 -or
        $value.source_event_integrity_failure_count -ne 0 -or $value.unexpected_L2_bypass_count -ne 0 -or
        $value.unexpected_Tensura_bypass_count -ne 0 -or $value.late_window_seconds -lt 29.9) {
        throw "Case result failed sustained/count invariants at Lv$($value.level)/$($value.L2_profile_variant)."
    }
    $hasRegenerate = $value.L2_profile_variant -ne 'WITHOUT_REGENERATE_CONTROL'
    if ($hasRegenerate) {
        if ($value.Regenerate_rank -le 0 -or $value.regenerate_native_tick_attempt_count -ne 60 -or
            $value.regenerate_callback_count -ne 60 -or -not $value.regenerate_trait_valid_at_start -or
            -not $value.regenerate_trait_valid_on_all_observed_attempts -or
            $value.regenerate_trait_rank_at_end -ne $value.Regenerate_rank -or
            $value.regenerate_trait_missing_tick_count -ne 0 -or
            [Math]::Abs([double]$value.regenerate_actual_healing_clock_vs_observer_delta) -gt 0.001 -or
            [Math]::Abs([double]$value.regenerate_unconstrained_healing_demand -
                ([double]$value.regenerate_actual_healing_at_native_ticks +
                 [double]$value.regenerate_healing_denied_by_wound_ceiling)) -gt 0.01) {
            throw "Native Regenerate invariant failed at Lv$($value.level)/$($value.L2_profile_variant)."
        }
    }
    elseif ($value.Regenerate_rank -ne 0 -or $value.regenerate_native_tick_attempt_count -ne 0 -or
        $value.regenerate_callback_count -ne 0 -or [double]$value.regenerate_actual_healing -ne 0) {
        throw "Regenerate-removed control retained Regenerate activity at Lv$($value.level)."
    }
}

if ($admitted -ne 360 -or $rejected -ne 0 -or $callbacks -ne 360 -or $woundStores -ne 360) {
    throw "R5 Severance accounting failed: admitted=$admitted rejected=$rejected callbacks=$callbacks stores=$woundStores."
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { [IO.Directory]::CreateDirectory($parent) | Out-Null }
[IO.File]::WriteAllLines($OutputPath, @($records.Json), [Text.UTF8Encoding]::new($false))
Write-Output "Validated R5: 18 cases, 1,080 Royal Arrow releases, 360/360 Severance admissions/callbacks/stores, 900 native Regenerate ticks, zero errors/source duplication/bypasses."
