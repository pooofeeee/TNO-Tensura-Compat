param(
    [string] $EvidenceRoot = (Join-Path $PSScriptRoot '..\docs\benchmarks\phase5f-suite-c')
)

$ErrorActionPreference = 'Stop'
$expectedProfile = 'ANCIENT_SINGLE_PROSPEROUS_SPECTRAL'
$expectedStages = @('Native', 'S0', 'S1', 'S2', 'S3', 'S4', 'S5', 'S6', 'S7')
$stageConfiguration = @{
    Native = @(0.00, 1.00, 0.00)
    S0 = @(0.05, 1.10, 0.00)
    S1 = @(0.10, 1.20, 0.00)
    S2 = @(0.15, 1.30, 0.00)
    S3 = @(0.20, 1.40, 0.00)
    S4 = @(0.25, 1.50, 0.00)
    S5 = @(0.30, 1.60, 0.25)
    S6 = @(0.35, 1.70, 0.50)
    S7 = @(0.40, 1.80, 1.00)
}
$bossCases = [ordered]@{
    luminous_valentine = 45
    hinata_sakaguchi = 54
    gazel_dwargo = 54
    orc_disaster = 54
    elemental_colossus = 54
    carrion = 54
    rimuru_ogre_fight = 54
}
$bossIds = [ordered]@{
    luminous_valentine = 'tensura_neb:luminous_valentine'
    hinata_sakaguchi = 'tensura:hinata_sakaguchi'
    gazel_dwargo = 'tensura:gazel_dwargo'
    orc_disaster = 'tensura:orc_disaster'
    elemental_colossus = 'tensura:elemental_colossus'
    carrion = 'tensura_neb:carrion'
    rimuru_ogre_fight = 'tensura_neb:rimuru_ogre_fight'
}
$families = [ordered]@{
    MAGIC_WEAPON = @{ Folder = 'magic_weapon'; Engraving = 'tensura:magic_weapon'; Source = 'tensura:magic'; Rows = 3200 }
    HOLY_WEAPON = @{ Folder = 'holy_weapon'; Engraving = 'tensura:holy_weapon'; Source = 'tensura:holy_damage'; Rows = 3245 }
    SOUL_EATER = @{ Folder = 'soul_eater'; Engraving = 'tensura:soul_eater'; Source = 'tensura:soul_scatter'; Rows = 3690 }
    ELEMENTAL_SLOTTING = @{ Folder = 'elemental_slotting'; Engraving = 'tensura:slotting'; Source = 'tensura:earth'; Rows = 3690 }
    ENERGY_STEAL = @{ Folder = 'energy_steal'; Engraving = 'tensura:energy_steal'; Source = ''; Rows = 3690 }
    SEVERANCE = @{ Folder = 'severance'; Engraving = 'tensura:severance'; Source = 'minecraft:arrow'; Rows = 3689 }
}
$strongestProfiles = @{
    'tensura_neb:luminous_valentine' = @{ Traits = 'l2hostility:adaptive=5,l2hostility:dementor=1,l2hostility:dispell=3,l2hostility:killer_aura=1,l2hostility:reflect=2,l2hostility:regenerate=5,l2hostility:soul_burner=2,l2hostility:tank=5'; Spent = 1000; Remaining = 0 }
    'tensura:hinata_sakaguchi' = @{ Traits = 'l2hostility:adaptive=5,l2hostility:dementor=1,l2hostility:dispell=2,l2hostility:reflect=2,l2hostility:regenerate=5,l2hostility:tank=5'; Spent = 950; Remaining = 50 }
    'tensura:gazel_dwargo' = @{ Traits = 'l2hostility:adaptive=5,l2hostility:dementor=1,l2hostility:dispell=2,l2hostility:reflect=1,l2hostility:regenerate=5,l2hostility:tank=5'; Spent = 950; Remaining = 50 }
    'tensura:orc_disaster' = @{ Traits = 'l2hostility:adaptive=5,l2hostility:dementor=1,l2hostility:dispell=2,l2hostility:drain=2,l2hostility:regenerate=5,l2hostility:tank=5,l2hostility:wither=1'; Spent = 980; Remaining = 20 }
    'tensura:elemental_colossus' = @{ Traits = 'l2hostility:adaptive=5,l2hostility:dementor=1,l2hostility:dispell=2,l2hostility:regenerate=5,l2hostility:speedy=2,l2hostility:tank=5'; Spent = 950; Remaining = 50 }
    'tensura_neb:carrion' = @{ Traits = 'l2hostility:adaptive=5,l2hostility:dementor=1,l2hostility:dispell=2,l2hostility:reflect=1,l2hostility:regenerate=5,l2hostility:speedy=1,l2hostility:tank=5'; Spent = 1000; Remaining = 0 }
    'tensura_neb:rimuru_ogre_fight' = @{ Traits = 'l2hostility:adaptive=5,l2hostility:dementor=1,l2hostility:dispell=2,l2hostility:drain=2,l2hostility:regenerate=5,l2hostility:tank=5'; Spent = 940; Remaining = 60 }
}

function Assert-Phase5F([bool] $Condition, [string] $Message) {
    if (-not $Condition) { throw $Message }
}

function Has-Property($Object, [string] $Name) {
    return $null -ne $Object.PSObject.Properties[$Name]
}

function Read-JsonLines([string] $Path) {
    Assert-Phase5F (Test-Path -LiteralPath $Path -PathType Leaf) "Missing Suite C artifact: $Path"
    $lineNumber = 0
    return @(Get-Content -LiteralPath $Path | ForEach-Object {
        $lineNumber++
        try { $_ | ConvertFrom-Json }
        catch { throw "Malformed JSON in $Path at line ${lineNumber}: $($_.Exception.Message)" }
    })
}

function Assert-Close([double] $Actual, [double] $Expected, [string] $Message, [double] $Tolerance = 0.0001) {
    Assert-Phase5F ([Math]::Abs($Actual - $Expected) -le $Tolerance) "$Message (expected $Expected, found $Actual)"
}

function Assert-CommonRecord($Record, [string] $Family, [string] $Path) {
    Assert-Phase5F ($Record.suite -eq 'BOTH') "Non-BOTH record in $Path."
    Assert-Phase5F (-not [bool]$Record.diagnostic) "Diagnostic record leaked into $Path."
    Assert-Phase5F ($Record.TNO_family -eq $Family) "Wrong family in $Path."
    Assert-Phase5F ($Record.APO_profile -eq $expectedProfile) "Wrong APO profile in $Path."
    Assert-Phase5F (-not [bool]$Record.royal_arrow_mark_enabled) "Royal Arrow Mark was enabled in $Path."
    if (Has-Property $Record 'production_balance_mutated') {
        Assert-Phase5F (-not [bool]$Record.production_balance_mutated) "Production balance mutation reported in $Path."
    }
    if (Has-Property $Record 'production_combat_mutated') {
        Assert-Phase5F (-not [bool]$Record.production_combat_mutated) "Production combat mutation reported in $Path."
    }
}

function Assert-StageRecord($Record, [string] $Path) {
    $stage = [string]$Record.TNO_stage
    Assert-Phase5F $stageConfiguration.ContainsKey($stage) "Unknown Stage $stage in $Path."
    $configuration = $stageConfiguration[$stage]
    Assert-Close ([double]$Record.stage_bonus) ([double]$configuration[0]) "Wrong Stage bonus for $stage in $Path"
    $expectedCoefficient = switch ([string]$Record.TNO_family) {
        { $_ -in @('MAGIC_WEAPON', 'HOLY_WEAPON', 'ELEMENTAL_SLOTTING') } { [double]$configuration[1]; break }
        { $_ -in @('SOUL_EATER', 'ENERGY_STEAL') } { 1.0 + [double]$configuration[0]; break }
        'SEVERANCE' { 1.0 + (1.8 * [double]$configuration[0]); break }
        default { throw "Unknown family $($Record.TNO_family) in $Path." }
    }
    Assert-Close ([double]$Record.stage_coefficient) $expectedCoefficient "Wrong Stage coefficient for $stage in $Path"
    $expectedPenetration = 0.0
    if ([bool]$Record.matching_Tensura_resistance_present -and -not [bool]$Record.matching_Tensura_nullification_present) {
        $expectedPenetration = [double]$configuration[2]
    }
    Assert-Close ([double]$Record.penetration_percentage_applied) $expectedPenetration "Wrong matching-Resistance recovery for $stage in $Path"
}

function Get-TraitSignature($Record) {
    return (@($Record.traits | ForEach-Object { "$($_.id)=$($_.rank)" }) | Sort-Object) -join ','
}

function Assert-Row($Row, [string] $Family, [string] $ExpectedSource, [string] $Path) {
    Assert-CommonRecord $Row $Family $Path
    Assert-StageRecord $Row $Path
    Assert-Phase5F (-not [bool]$Row.duplicate_event_from_same_projectile) "Same-projectile re-hit in $Path."
    Assert-Phase5F (-not [bool]$Row.unexpected_source_duplication) "Unexpected source duplication in $Path."
    Assert-Phase5F (-not [bool]$Row.event_recursion_observed) "Event recursion in $Path."
    Assert-Phase5F (-not [bool]$Row.l2_layer_bypassed_unexpectedly) "Unexpected L2 bypass in $Path."
    Assert-Phase5F (-not [bool]$Row.tensura_layer_bypassed_unexpectedly) "Unexpected Tensura bypass in $Path."
    Assert-Phase5F (-not [bool]$Row.royal_arrow_mark_observed) "Royal Arrow Mark event in $Path."
    Assert-Phase5F ([bool]$Row.suite_a_apotheosis_profile_preserved) "APO profile drift in $Path."
    Assert-Phase5F (-not [bool]$Row.suite_a_full_enchantment_package_preserved) "Illegal full Suite A enchantment package in $Path."
    Assert-Phase5F ($Row.suite_a_enchantment_removed -eq 'tensura:barrier_piercing') "Wrong Suite A substitution in $Path."
    $expectedAmmo = 'royalvariations:royal_arrow'
    if ($Family -eq 'ELEMENTAL_SLOTTING') {
        $expectedAmmo = 'royalvariations:royal_arrow consumed by native Slotting release'
    }
    Assert-Phase5F ($Row.requested_ammo_item -eq $expectedAmmo) "Wrong ammunition in $Path."

    $releasedIds = @($Row.released_projectile_entity_ids)
    $releasedUuids = @($Row.released_projectile_uuids)
    $hitUuids = @($Row.hit_projectile_uuids)
    Assert-Phase5F ($releasedIds.Count -eq [int]$Row.released_projectile_count) "Released projectile count mismatch in $Path."
    Assert-Phase5F (($releasedUuids | Sort-Object -Unique).Count -eq $releasedUuids.Count) "Duplicate released projectile UUID in one row of $Path."
    foreach ($projectileId in $releasedIds) {
        Assert-Phase5F ($projectileId -in @('royalvariations:royal_arrow', 'minecraft:spectral_arrow', 'tensura:stone_shot')) "Unknown projectile $projectileId in $Path."
    }
    foreach ($hitUuid in $hitUuids) {
        Assert-Phase5F ($hitUuid -in $releasedUuids) "Hit projectile was not released in $Path."
    }

    if ([int]$Row.physical_damage_event_count -gt 0) {
        Assert-Phase5F ($Row.physical_damage_source_id -eq 'minecraft:arrow') "Physical DamageSource changed in $Path."
    }
    if ([int]$Row.engraving_damage_event_count -gt 0 -and $ExpectedSource) {
        Assert-Phase5F ($Row.family_damage_source_id -eq $ExpectedSource) "Family DamageSource changed in $Path."
    }
    if ($Family -in @('MAGIC_WEAPON', 'HOLY_WEAPON')) {
        Assert-Phase5F (-not [bool]$Row.family_source_is_l2_magic) "Tensura family source was reclassified as neoforge:is_magic in $Path."
        Assert-Close ([double]$Row.engraving_after_stage_coefficient) `
            ([double]$Row.engraving_native_amount * [double]$Row.stage_coefficient) `
            "Family Stage formula mismatch in $Path"
    }
    if ($Family -ne 'SEVERANCE') {
        Assert-Close ([double]$Row.physical_combined_original_before_L2) `
            ([double]$Row.physical_original_before_stage) `
            "Base/raw physical damage entered Stage scaling in $Path"
    }
    if ($Family -eq 'ENERGY_STEAL') {
        Assert-Phase5F ([int]$Row.energy_drain_event_count -le 1) "Duplicated Energy Steal event in $Path."
        Assert-Phase5F ([int]$Row.energy_drain_event_count -le [int]$Row.physical_damage_event_count) "Energy Steal occurred without an admitted physical event in $Path."
        Assert-Phase5F (-not [bool]$Row.energy_operation_emitted_damage_source) "Energy Steal emitted a DamageSource in $Path."
        if ([int]$Row.energy_drain_event_count -gt 0) {
            Assert-Close ([double]$Row.energy_native_percentage) 0.01 "Wrong native Energy Steal percentage in $Path" 0.0000001
            Assert-Close ([double]$Row.energy_after_stage_percentage) `
                (0.01 * [double]$Row.stage_coefficient) `
                "Energy Steal Stage formula mismatch in $Path" 0.0000001
        }
    }
    elseif ([int]$Row.energy_drain_event_count -gt 0) {
        throw "Energy Steal event leaked into $Family in $Path."
    }
    if ($Family -eq 'SEVERANCE') {
        Assert-Phase5F (-not [bool]$Row.severance_distinct_damage_source) "Second Severance DamageSource in $Path."
        if ([double]$Row.combined_physical_post_damage -le 0.0001) {
            Assert-Close ([double]$Row.severance_amount_delta) 0.0 "Zero/cancelled physical damage stored Severance wound in $Path"
        }
    }
    if ([bool]$Row.nullification_authoritative) {
        Assert-Close ([double]$Row.damage_after_matching_resistance_recovery) 0.0 "Nullification was penetrated in $Path"
    }
}

$directCases = 0
$directRows = 0
$endgameCases = 0
$endgameRows = 0
$caseErrors = 0
$releasedUuidOwners = @{}
$directFamilySummary = [ordered]@{}

foreach ($familyName in $families.Keys) {
    $family = $families[$familyName]
    $familyPath = Join-Path $EvidenceRoot $family.Folder
    $files = @(Get-ChildItem -LiteralPath $familyPath -Filter '*.jsonl' -File)
    Assert-Phase5F ($files.Count -eq 7) "Expected seven direct artifacts for $familyName, found $($files.Count)."
    $familyCases = 0
    $familyRows = 0

    foreach ($file in $files) {
        Assert-Phase5F $bossCases.Contains($file.BaseName) "Unexpected direct artifact $($file.FullName)."
        $records = Read-JsonLines $file.FullName
        $catalogs = @($records | Where-Object kind -eq 'catalog')
        $starts = @($records | Where-Object kind -eq 'case_start')
        $rows = @($records | Where-Object kind -eq 'row')
        $results = @($records | Where-Object kind -eq 'case_result')
        $suiteResults = @($records | Where-Object kind -eq 'suite_result')
        $errors = @($records | Where-Object kind -eq 'case_error')
        $expectedCases = [int]$bossCases[$file.BaseName]
        $expectedBoss = $bossIds[$file.BaseName]

        Assert-Phase5F ($catalogs.Count -eq 1) "Expected one catalog in $($file.FullName)."
        Assert-Phase5F ($starts.Count -eq $expectedCases -and $results.Count -eq $expectedCases) "Case count mismatch in $($file.FullName)."
        Assert-Phase5F ($suiteResults.Count -eq 1) "Expected one suite_result in $($file.FullName)."
        Assert-Phase5F ($errors.Count -eq 0) "case_error present in $($file.FullName)."
        Assert-Phase5F ($suiteResults[0].status -eq 'complete') "Incomplete suite_result in $($file.FullName)."
        Assert-Phase5F ([int]$suiteResults[0].case_count -eq $expectedCases -and [int]$suiteResults[0].requested_case_count -eq $expectedCases) "suite_result count mismatch in $($file.FullName)."
        Assert-CommonRecord $catalogs[0] $familyName $file.FullName
        Assert-Phase5F ($catalogs[0].engraving -eq $family.Engraving) "Wrong Engraving in $($file.FullName)."
        Assert-Phase5F ([int]$catalogs[0].shots_per_case -eq 10 -and [int]$catalogs[0].fixed_window_ticks -eq 200) "Protocol drift in $($file.FullName)."

        $stageGroups = @($starts | Group-Object boss, level)
        Assert-Phase5F ($stageGroups.Count * 9 -eq $expectedCases) "Wrong boss/level profile count in $($file.FullName)."
        foreach ($group in $stageGroups) {
            $actualStages = @($group.Group.TNO_stage | Sort-Object)
            Assert-Phase5F (($actualStages -join ',') -eq (($expectedStages | Sort-Object) -join ',')) "Incomplete Native/S0-S7 coverage in $($file.FullName)."
        }
        foreach ($start in $starts) {
            Assert-CommonRecord $start $familyName $file.FullName
            Assert-StageRecord $start $file.FullName
            Assert-Phase5F ($start.boss -eq $expectedBoss) "Wrong boss in $($file.FullName)."
            Assert-Phase5F ([bool]$start.legal_trait_profile -and [bool]$start.profile_clone_verified) "Illegal or uncloned L2 profile in $($file.FullName)."
            Assert-Phase5F ([bool]$start.suite_a_apotheosis_profile_preserved) "APO profile drift in $($file.FullName)."
            Assert-Phase5F ([int]$start.APO_sockets -eq 5 -and @($start.APO_affixes).Count -eq 10 -and @($start.APO_gems).Count -eq 5) "Illegal APO layout in $($file.FullName)."
            Assert-Phase5F ($start.suite_c_enchantment_added -eq $family.Engraving) "Wrong family enchantment substitution in $($file.FullName)."
        }
        foreach ($row in $rows) {
            Assert-Row $row $familyName $family.Source $file.FullName
            foreach ($uuid in @($row.released_projectile_uuids)) {
                Assert-Phase5F (-not $releasedUuidOwners.ContainsKey($uuid)) "Projectile UUID $uuid was reused across Suite C rows."
                $releasedUuidOwners[$uuid] = $file.FullName
            }
        }
        foreach ($result in $results) {
            Assert-CommonRecord $result $familyName $file.FullName
            Assert-StageRecord $result $file.FullName
            Assert-Phase5F ($result.status -eq 'ok') "Incomplete case_result in $($file.FullName)."
        }

        $familyCases += $results.Count
        $familyRows += $rows.Count
        $caseErrors += $errors.Count
    }
    Assert-Phase5F ($familyCases -eq 369) "Expected 369 direct cases for $familyName, found $familyCases."
    Assert-Phase5F ($familyRows -eq [int]$family.Rows) "Unexpected direct row total for ${familyName}: $familyRows."
    $directFamilySummary[$familyName] = [ordered]@{ cases = $familyCases; rows = $familyRows }
    $directCases += $familyCases
    $directRows += $familyRows
}

$endgamePath = Join-Path $EvidenceRoot 'endgame'
$endgameFiles = @(Get-ChildItem -LiteralPath $endgamePath -Filter '*.jsonl' -File)
Assert-Phase5F ($endgameFiles.Count -eq 6) "Expected six endgame artifacts, found $($endgameFiles.Count)."
foreach ($familyName in $families.Keys) {
    $family = $families[$familyName]
    $path = Join-Path $endgamePath "$($family.Folder).jsonl"
    $records = Read-JsonLines $path
    $catalogs = @($records | Where-Object kind -eq 'catalog')
    $starts = @($records | Where-Object kind -eq 'case_start')
    $rows = @($records | Where-Object kind -eq 'row')
    $results = @($records | Where-Object kind -eq 'case_result')
    $suiteResults = @($records | Where-Object kind -eq 'suite_result')
    $errors = @($records | Where-Object kind -eq 'case_error')

    Assert-Phase5F ($catalogs.Count -eq 1 -and [bool]$catalogs[0].strongest_legal_endgame_matrix) "Wrong endgame catalog in $path."
    Assert-Phase5F ($starts.Count -eq 14 -and $results.Count -eq 14 -and $rows.Count -eq 140) "Wrong endgame counts in $path."
    Assert-Phase5F ($suiteResults.Count -eq 1 -and $suiteResults[0].status -eq 'complete') "Incomplete endgame suite in $path."
    Assert-Phase5F ([int]$suiteResults[0].case_count -eq 14 -and [int]$suiteResults[0].requested_case_count -eq 14) "Wrong endgame suite_result count in $path."
    Assert-Phase5F ($errors.Count -eq 0) "case_error present in $path."
    Assert-CommonRecord $catalogs[0] $familyName $path

    foreach ($bossId in $strongestProfiles.Keys) {
        $bossStarts = @($starts | Where-Object boss -eq $bossId)
        Assert-Phase5F ($bossStarts.Count -eq 2) "Expected Native/S7 endgame cases for $bossId in $path."
        Assert-Phase5F ((@($bossStarts.TNO_stage | Sort-Object) -join ',') -eq 'Native,S7') "Wrong endgame stages for $bossId in $path."
        foreach ($start in $bossStarts) {
            $expected = $strongestProfiles[$bossId]
            Assert-CommonRecord $start $familyName $path
            Assert-StageRecord $start $path
            Assert-Phase5F ([int]$start.level -eq 1000 -and [bool]$start.strongest_legal_endgame_profile) "Wrong endgame level/profile for $bossId in $path."
            Assert-Phase5F ([bool]$start.legal_trait_profile -and [bool]$start.profile_clone_verified) "Illegal endgame profile for $bossId in $path."
            Assert-Phase5F ((Get-TraitSignature $start) -eq $expected.Traits) "Strongest profile trait drift for $bossId in $path."
            Assert-Phase5F ([int]$start.endgame_profile_budget_spent -eq $expected.Spent -and [int]$start.endgame_profile_budget_remaining -eq $expected.Remaining) "Strongest profile budget drift for $bossId in $path."
        }
    }
    foreach ($row in $rows) {
        Assert-Row $row $familyName $family.Source $path
        foreach ($uuid in @($row.released_projectile_uuids)) {
            Assert-Phase5F (-not $releasedUuidOwners.ContainsKey($uuid)) "Projectile UUID $uuid was reused across Suite C rows."
            $releasedUuidOwners[$uuid] = $path
        }
    }
    foreach ($result in $results) {
        Assert-CommonRecord $result $familyName $path
        Assert-StageRecord $result $path
        Assert-Phase5F ($result.status -eq 'ok') "Incomplete endgame case_result in $path."
    }
    $endgameCases += $results.Count
    $endgameRows += $rows.Count
    $caseErrors += $errors.Count
}

Assert-Phase5F ($directCases -eq 2214) "Expected 2,214 direct cases, found $directCases."
Assert-Phase5F ($directRows -eq 21204) "Expected 21,204 direct rows, found $directRows."
Assert-Phase5F ($endgameCases -eq 84) "Expected 84 endgame cases, found $endgameCases."
Assert-Phase5F ($endgameRows -eq 840) "Expected 840 endgame rows, found $endgameRows."
Assert-Phase5F ($caseErrors -eq 0) "Expected zero case errors, found $caseErrors."

$summary = [ordered]@{
    status = 'PASS'
    direct_artifacts = 42
    endgame_artifacts = 6
    direct_cases = $directCases
    direct_rows = $directRows
    endgame_cases = $endgameCases
    endgame_rows = $endgameRows
    total_cases = $directCases + $endgameCases
    total_rows = $directRows + $endgameRows
    case_errors = $caseErrors
    reused_projectile_uuids = 0
    unexpected_source_duplication = 0
    same_projectile_rehits = 0
    event_recursion = 0
    unexpected_l2_bypasses = 0
    unexpected_tensura_bypasses = 0
    production_mutations = 0
    families = $directFamilySummary
}
$summary | ConvertTo-Json -Depth 5
