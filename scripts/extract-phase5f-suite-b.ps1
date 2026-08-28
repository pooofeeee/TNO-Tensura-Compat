param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('MAGIC_WEAPON', 'HOLY_WEAPON', 'SOUL_EATER', 'ELEMENTAL_SLOTTING', 'ENERGY_STEAL', 'SEVERANCE')]
    [string] $ExpectedFamily,

    [Parameter(Mandatory = $true)]
    [string] $ExpectedBoss,

    [Parameter(Mandatory = $true)]
    [int] $ExpectedCases,

    [ValidateSet('B', 'C')]
    [string] $Suite = 'B'
)

$ErrorActionPreference = 'Stop'
$marker = if ($Suite -eq 'C') { 'TNO_PHASE5F_SUITE_C ' } else { 'TNO_PHASE5F_SUITE_B ' }
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
    catch { throw "Malformed Suite $Suite JSON in ${resolvedLog}: $json" }
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
if ($catalog.diagnostic) { throw "Diagnostic output cannot be preserved as official Suite $Suite evidence." }
$expectedProfile = if ($Suite -eq 'C') { 'ANCIENT_SINGLE_PROSPEROUS_SPECTRAL' } else { 'NONE' }
$expectedSuiteLabel = if ($Suite -eq 'C') { 'BOTH' } else { 'B_TNO_ONLY' }
if ($catalog.suite -ne $expectedSuiteLabel -or $catalog.TNO_family -ne $ExpectedFamily -or
    $catalog.APO_profile -ne $expectedProfile) {
    throw "Capture does not use the requested Suite $Suite family/profile."
}
if ($catalog.cases[0].boss -ne $ExpectedBoss) {
    throw "Expected boss $ExpectedBoss; found $($catalog.cases[0].boss)"
}
if ($catalog.shots_per_case -ne 10 -or $catalog.fixed_window_ticks -ne 200) {
    throw 'Capture does not use the locked 10-shot/200-tick protocol.'
}
if ($catalog.royal_arrow_mark_enabled -or -not $catalog.stage_fixture_only -or
    $catalog.production_balance_mutated -or $catalog.production_combat_mutated) {
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
        $value.APO_profile -ne $expectedProfile -or $value.suite -ne $expectedSuiteLabel -or
        $value.TNO_family -ne $ExpectedFamily) {
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
    if ($Suite -eq 'B' -and $row.Value.crit) { throw 'TNO-only isolation unexpectedly recorded a critical hit.' }
}

if ($Suite -eq 'C') {
    $expectedAffixes = @(
        'ancientreforging:melee/attribute/intricate',
        'ancientreforging:melee/attribute/lacerating',
        'ancientreforging:melee/attribute/piercing',
        'ancientreforging:ranged/attribute/elven',
        'ancientreforging:ranged/attribute/streamlined',
        'ancientreforging:ranged/enchantment/prosperous',
        'ancientreforging:ranged/mob_effect/acidic',
        'ancientreforging:ranged/mob_effect/deathbound',
        'ancientreforging:ranged/mob_effect/ivy_laced',
        'ancientreforging:ranged/spectral'
    )
    $expectedGems = @(
        'apotheosis:core/breach', 'apotheosis:core/combatant',
        'apotheosis:core/lightning', 'apotheosis:core/warlord', 'apotheosis:core/warlord'
    )
    $inspection = $catalog.APO_runtime_inspection
    $affixes = @($inspection.apotheosis.affixes.entries)
    $gems = @($inspection.apotheosis.sockets.gems)
    if ($inspection.item_id -ne 'royalvariations:royal_bow' -or
        $inspection.apotheosis.status -ne 'ok' -or
        $inspection.apotheosis.rarity -ne 'ancientreforging:ancient' -or
        $affixes.Count -ne 10 -or
        (Compare-Object @($affixes.id | Sort-Object) $expectedAffixes).Count -ne 0 -or
        @($affixes | Where-Object { -not $_.valid -or [Math]::Abs([double]$_.effective_level - 1.5) -gt 0.0001 }).Count -ne 0 -or
        $inspection.apotheosis.sockets.effective_socket_count -ne 5 -or
        -not $inspection.apotheosis.sockets.all_unique_constraints_satisfied -or
        $gems.Count -ne 5 -or
        (Compare-Object @($gems.id | Sort-Object) $expectedGems).Count -ne 0 -or
        @($gems | Where-Object { -not $_.valid -or $_.purity -ne 'perfect' }).Count -ne 0) {
        throw 'Suite C catalog does not contain the exact accepted Ancient rarity/affix/gem profile.'
    }

    $appliedEnchantments = @($inspection.enchantments.applied)
    $appliedIds = @($appliedEnchantments.id)
    if (-not $inspection.enchantments.applied_pairwise_compatible -or
        $appliedIds -contains 'tensura:barrier_piercing' -or
        $appliedIds -notcontains $catalog.engraving -or
        -not $catalog.suite_a_apotheosis_profile_preserved -or
        $catalog.suite_a_full_enchantment_package_preserved -or
        $catalog.suite_a_enchantment_removed -ne 'tensura:barrier_piercing' -or
        $catalog.suite_c_enchantment_added -ne $catalog.engraving) {
        throw 'Suite C did not preserve the legal barrier_piercing-to-family-Engraving substitution.'
    }

    foreach ($row in $rows) {
        $value = $row.Value
        $spawnedIds = @($value.released_projectile_entity_ids)
        $spawnedUuids = @($value.released_projectile_uuids)
        $hitIds = @($value.hit_projectile_entity_ids)
        $hitUuids = @($value.hit_projectile_uuids)
        $allowed = if ($ExpectedFamily -eq 'ELEMENTAL_SLOTTING') {
            @('tensura:stone_shot')
        }
        else { @('royalvariations:royal_arrow', 'minecraft:spectral_arrow') }
        if ($value.requested_ammo_item -notlike 'royalvariations:royal_arrow*' -or
            [int]$value.released_projectile_count -lt 1 -or
            $spawnedUuids.Count -ne [int]$value.released_projectile_count -or
            @($spawnedUuids | Sort-Object -Unique).Count -ne $spawnedUuids.Count -or
            @($spawnedIds | Where-Object { $_ -notin $allowed }).Count -ne 0 -or
            @($hitIds | Where-Object { $_ -notin $allowed }).Count -ne 0 -or
            @($hitUuids | Where-Object { $_ -notin $spawnedUuids }).Count -ne 0 -or
            [int]$value.projectiles_discarded_after_target_defeat -lt 0 -or
            [int]$value.projectiles_discarded_after_target_defeat -gt [int]$value.released_projectile_count -or
            ([int]$value.projectiles_discarded_after_target_defeat -gt 0 -and [double]$value.post_HP -gt 0.0001) -or
            $value.royal_arrow_mark_observed -or
            $value.duplicate_event_from_same_projectile -or
            $value.unexpected_source_duplication -or
            $value.event_recursion_observed -or
            $value.l2_layer_bypassed_unexpectedly -or
            $value.tensura_layer_bypassed_unexpectedly -or
            -not $value.suite_a_apotheosis_profile_preserved -or
            $value.suite_a_full_enchantment_package_preserved -or
            $value.suite_a_enchantment_removed -ne 'tensura:barrier_piercing' -or
            $value.suite_c_enchantment_added -ne $catalog.engraving) {
            throw "Invalid Suite C projectile/profile invariant at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }
        if ($ExpectedFamily -ne 'ELEMENTAL_SLOTTING' -and
            [int]$value.physical_damage_event_count -gt [int]$value.released_projectile_count) {
            throw "A Suite C release emitted more physical events than unique projectiles."
        }
        if ($ExpectedFamily -in @('MAGIC_WEAPON', 'HOLY_WEAPON', 'SOUL_EATER', 'ELEMENTAL_SLOTTING') -and
            [int]$value.engraving_damage_event_count -gt [int]$value.released_projectile_count) {
            throw "A Suite C release emitted more family events than unique projectiles."
        }
        if ($ExpectedFamily -ne 'ELEMENTAL_SLOTTING' -and [int]$value.physical_damage_event_count -gt 0 -and
            $value.physical_damage_source_id -ne 'minecraft:arrow') {
            throw "Suite C physical DamageSource changed from minecraft:arrow."
        }
    }
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

if ($ExpectedFamily -eq 'ENERGY_STEAL') {
    if ($catalog.engraving -ne 'tensura:energy_steal' -or
        $null -ne $catalog.damage_source_id -or
        $catalog.energy_operation_emits_damage_source -or
        $catalog.arrow -ne 'royalvariations:royal_arrow') {
        throw 'Energy capture does not describe the locked native Energy Steal I Royal Arrow path.'
    }

    $eventRows = 0
    foreach ($row in $rows) {
        $value = $row.Value
        $eventCount = [int]$value.energy_drain_event_count
        if ($eventCount -lt 0 -or $eventCount -gt 1 -or
            $value.energy_operation_emitted_damage_source -or
            $value.matching_Tensura_resistance_present -or
            $value.matching_Tensura_nullification_present -or
            [Math]::Abs([double]$value.penetration_percentage_applied) -gt 0.0001 -or
            [Math]::Abs([double]$value.engraving_native_amount) -gt 0.0001 -or
            [Math]::Abs([double]$value.engraving_after_stage_coefficient) -gt 0.0001 -or
            [Math]::Abs([double]$value.damage_before_matching_resistance_recovery) -gt 0.0001 -or
            [Math]::Abs([double]$value.damage_after_matching_resistance_recovery) -gt 0.0001 -or
            [Math]::Abs([double]$value.damage_after_L2_processing) -gt 0.0001) {
            throw "Energy row escaped the non-DamageSource/current-pool scope at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }

        $nativePercentage = [double]$value.energy_native_percentage
        $stagedPercentage = [double]$value.energy_after_stage_percentage
        $magiculeDrain = [double]$value.magicule_current_pool_drain
        $auraDrain = [double]$value.aura_current_pool_drain
        $totalDrain = [double]$value.energy_current_pool_drain
        $magiculeGain = [double]$value.attacker_magicule_gain
        $auraGain = [double]$value.attacker_aura_gain
        if ($eventCount -eq 0) {
            if ([Math]::Abs($nativePercentage) -gt 0.0001 -or
                [Math]::Abs($stagedPercentage) -gt 0.0001 -or
                [Math]::Abs($totalDrain) -gt 0.0001 -or
                [Math]::Abs($magiculeGain + $auraGain) -gt 0.0001) {
                throw "Energy values were recorded without a native event at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
            }
            continue
        }

        $eventRows++
        $expectedPercentage = 0.01 * [double]$value.stage_coefficient
        $expectedMagiculeDrain = [double]$value.pre_Magicules * $expectedPercentage
        $expectedAuraDrain = [double]$value.pre_Aura * $expectedPercentage
        $magiculeTolerance = [Math]::Max(0.001, [Math]::Abs($expectedMagiculeDrain) * 0.0000001)
        $auraTolerance = [Math]::Max(0.001, [Math]::Abs($expectedAuraDrain) * 0.0000001)
        if ([Math]::Abs($nativePercentage - 0.01) -gt 0.000001 -or
            [Math]::Abs($stagedPercentage - $expectedPercentage) -gt 0.000001 -or
            [Math]::Abs($magiculeDrain - $expectedMagiculeDrain) -gt $magiculeTolerance -or
            [Math]::Abs($auraDrain - $expectedAuraDrain) -gt $auraTolerance -or
            [Math]::Abs($totalDrain - ($magiculeDrain + $auraDrain)) -gt 0.001 -or
            [Math]::Abs($magiculeGain - $magiculeDrain) -gt $magiculeTolerance -or
            [Math]::Abs($auraGain - $auraDrain) -gt $auraTolerance) {
            throw "Invalid Energy Steal current-pool accounting at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }
    }

    foreach ($case in $caseResults) {
        $value = $case.Value
        $caseRows = @($rows | Where-Object {
            $_.Value.level -eq $value.level -and $_.Value.TNO_stage -eq $value.TNO_stage
        })
        if ($caseRows.Count -ne [int]$value.hits_recorded) {
            throw "Energy case row count mismatch at level $($value.level), stage $($value.TNO_stage)."
        }
        $totalDrain = ($caseRows.Value | Measure-Object -Property energy_current_pool_drain -Sum).Sum
        $expectedRate = if ([int]$value.elapsed_ticks -gt 0) {
            [double]$totalDrain / ([double]$value.elapsed_ticks / 20.0)
        }
        else { 0.0 }
        if ([Math]::Abs([double]$value.energy_current_pool_drain - [double]$totalDrain) -gt 0.001 -or
            [Math]::Abs([double]$value.resource_impact_per_second - $expectedRate) -gt 0.001) {
            throw "Energy case aggregate mismatch at level $($value.level), stage $($value.TNO_stage)."
        }
    }

    if ($eventRows -eq 0) {
        Write-Warning 'This boss emitted no Energy Drain event; retain family-level positive-control evidence before interpreting the capture.'
    }
}

if ($ExpectedFamily -eq 'SEVERANCE') {
    if ($catalog.engraving -ne 'tensura:severance' -or
        $null -ne $catalog.damage_source_id -or
        $catalog.severance_distinct_damage_source -or
        [Math]::Abs([double]$catalog.severance_native_attack_bonus - 3.0) -gt 0.0001 -or
        $catalog.arrow -ne 'royalvariations:royal_arrow') {
        throw 'Severance capture does not describe the locked native Severance I Royal Arrow path.'
    }

    $physicalEventRows = 0
    $woundRows = 0
    foreach ($row in $rows) {
        $value = $row.Value
        $speed = [double]$value.severance_projectile_speed
        $baseDamage = [double]$value.severance_base_projectile_damage
        $nativeBonus = [double]$value.severance_native_attack_bonus
        $stagedBonus = [double]$value.severance_after_stage_attack_bonus
        $configuredProjectiles = if ($Suite -eq 'C') {
            [int]$value.severance_configured_projectile_count
        }
        else { 1 }
        $admittedProjectiles = if ($Suite -eq 'C') {
            [int]$value.severance_admitted_projectile_count
        }
        else { 1 }
        $expectedNativePrePerProjectile = $speed * ($baseDamage + $nativeBonus)
        $expectedStagedPrePerProjectile = $speed * ($baseDamage + $stagedBonus)
        $expectedBasePostPerProjectile = [Math]::Ceiling($speed * $baseDamage)
        $expectedNativePostPerProjectile = [Math]::Ceiling($expectedNativePrePerProjectile)
        $expectedStagedPostPerProjectile = [Math]::Ceiling($expectedStagedPrePerProjectile)
        $expectedNativePre = $admittedProjectiles * $expectedNativePrePerProjectile
        $expectedStagedPre = $admittedProjectiles * $expectedStagedPrePerProjectile
        $expectedBasePost = $admittedProjectiles * $expectedBasePostPerProjectile
        $expectedNativePost = $admittedProjectiles * $expectedNativePostPerProjectile
        $expectedStagedPost = $admittedProjectiles * $expectedStagedPostPerProjectile
        $wound = [double]$value.severance_amount_delta
        $postPhysical = [double]$value.combined_physical_post_damage
        $combinedOriginal = [double]$value.physical_combined_original_before_L2
        $maximumExpectedWound = [Math]::Max(0.5, $combinedOriginal * 0.5)

        if (-not $value.royal_arrow_created -or $value.severance_distinct_damage_source -or
            $value.family_source_is_l2_magic -or
            $value.matching_Tensura_resistance_present -or
            $value.matching_Tensura_nullification_present -or
            [Math]::Abs([double]$value.penetration_percentage_applied) -gt 0.0001 -or
            $configuredProjectiles -lt 1 -or
            ($Suite -eq 'C' -and
                ($configuredProjectiles + [int]$value.projectiles_discarded_after_target_defeat) -ne
                    [int]$value.released_projectile_count) -or
            $admittedProjectiles -lt 0 -or $admittedProjectiles -gt $configuredProjectiles -or
            ($Suite -eq 'C' -and $admittedProjectiles -ne [int]$value.physical_damage_event_count) -or
            $speed -le 0.0 -or ($Suite -eq 'B' -and [Math]::Abs($baseDamage - 2.4) -gt 0.0001) -or
            [Math]::Abs($nativeBonus - 3.0) -gt 0.0001 -or
            [Math]::Abs($stagedBonus - (3.0 * [double]$value.stage_coefficient)) -gt 0.0001 -or
            [Math]::Abs([double]$value.severance_native_pre_round - $expectedNativePre) -gt 0.0001 -or
            [Math]::Abs([double]$value.severance_after_stage_pre_round - $expectedStagedPre) -gt 0.0001 -or
            [Math]::Abs([double]$value.severance_base_only_post_round - $expectedBasePost) -gt 0.0001 -or
            [Math]::Abs([double]$value.severance_native_post_round - $expectedNativePost) -gt 0.0001 -or
            [Math]::Abs([double]$value.severance_after_stage_post_round - $expectedStagedPost) -gt 0.0001 -or
            [Math]::Abs([double]$value.engraving_native_amount - ($expectedNativePost - $expectedBasePost)) -gt 0.0001 -or
            [Math]::Abs([double]$value.engraving_after_stage_coefficient - ($expectedStagedPost - $expectedBasePost)) -gt 0.0001 -or
            $wound -lt -0.0001 -or $postPhysical -lt -0.0001 -or
            ($postPhysical -le 0.0001 -and $wound -gt 0.0001) -or
            $wound -gt ($maximumExpectedWound + 0.001)) {
            throw "Invalid Severance velocity/rounding/wound scope at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }

        if (@($value.damage_source_ids) -contains 'minecraft:arrow') {
            $physicalEventRows++
            if ([Math]::Abs([double]$value.physical_original_before_stage - $expectedBasePost) -gt 0.0001 -or
                ($Suite -eq 'B' -and [Math]::Abs($combinedOriginal - $expectedStagedPost) -gt 0.0001) -or
                ($Suite -eq 'C' -and $combinedOriginal + 0.0001 -lt $expectedBasePost) -or
                @($value.damage_source_tags_if_observable) -notcontains 'minecraft:is_projectile' -or
                @($value.damage_source_tags_if_observable) -contains 'neoforge:is_magic') {
                throw "Severance combined source did not retain physical projectile tags at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
            }
        }
        elseif ([Math]::Abs([double]$value.physical_original_before_stage) -gt 0.0001 -or
            [Math]::Abs([double]$value.physical_combined_original_before_L2) -gt 0.0001 -or
            $postPhysical -gt 0.0001 -or $wound -gt 0.0001) {
            throw "Severance amounts were observed without an admitted arrow event at level $($value.level), stage $($value.TNO_stage), hit $($value.hit_index)."
        }
        if ($wound -gt 0.0001) { $woundRows++ }
    }

    if ($physicalEventRows -eq 0) {
        Write-Warning 'This boss admitted no combined physical Severance arrow event; retain family-level positive-control evidence before interpreting the capture.'
    }
    elseif ($woundRows -eq 0) {
        Write-Warning 'This boss admitted physical arrows but stored no Severance wound; preserve the native cancellation finding.'
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
