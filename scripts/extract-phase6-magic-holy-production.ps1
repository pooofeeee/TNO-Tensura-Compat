param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('MAGIC_WEAPON', 'HOLY_WEAPON')]
    [string]$ExpectedFamily,

    [Parameter(Mandatory = $true)]
    [string]$ExpectedBoss
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_MAGIC_HOLY_PRODUCTION '
$session = [System.Collections.Generic.List[object]]::new()
$lines = @(Get-Content -LiteralPath $LogPath)

foreach ($line in $lines) {
    $index = $line.IndexOf($marker, [System.StringComparison]::Ordinal)
    if ($index -lt 0) { continue }
    $jsonText = $line.Substring($index + $marker.Length)
    if (-not $jsonText.TrimStart().StartsWith('{')) { continue }
    try { $record = $jsonText | ConvertFrom-Json -Depth 100 }
    catch { throw "Invalid production acceptance JSON: $jsonText" }
    if ($record.kind -eq 'catalog') { $session.Clear() }
    $session.Add($record)
}

if ($session.Count -eq 0) {
    foreach ($line in $lines) {
        $jsonText = $line.Trim()
        if (-not $jsonText.StartsWith('{')) { continue }
        try { $record = $jsonText | ConvertFrom-Json -Depth 100 }
        catch { throw "Invalid production acceptance JSONL: $jsonText" }
        if ($record.kind -eq 'catalog') { $session.Clear() }
        $session.Add($record)
    }
}

if ($session.Count -eq 0) { throw "No production acceptance records found in $LogPath" }
$errors = @($session | Where-Object kind -eq 'case_error')
if ($errors.Count -ne 0) { throw "Production session contains $($errors.Count) case_error record(s)" }
$suites = @($session | Where-Object kind -eq 'suite_result')
if ($suites.Count -ne 1 -or $suites[0].status -ne 'complete') {
    throw "Expected one complete suite_result, found $($suites.Count)"
}

$expectedCases = if ($ExpectedBoss -eq 'tensura:orc_disaster') { 39 } else { 4 }
$cases = @($session | Where-Object kind -eq 'case_result')
$rows = @($session | Where-Object kind -eq 'row')
if ($cases.Count -ne $expectedCases -or [int]$suites[0].case_count -ne $expectedCases -or
        [int]$suites[0].requested_case_count -ne $expectedCases) {
    throw "Case count mismatch: cases=$($cases.Count), suite=$($suites[0].case_count)/$($suites[0].requested_case_count), expected=$expectedCases"
}
if ($rows.Count -ne $expectedCases * 10) {
    throw "Row count mismatch: rows=$($rows.Count), expected=$($expectedCases * 10)"
}

$policy = @{
    S0 = @(0.00, 0.000, 0.000)
    S1 = @(0.00, 0.000, 0.000)
    S2 = @(0.00, 0.000, 0.000)
    S3 = @(0.00, 0.000, 0.000)
    S4 = @(0.00, 0.000, 0.000)
    S5 = @(0.50, 0.500, 0.500)
    S6 = @(0.75, 0.625, 0.625)
    S7 = @(1.00, 0.750, 0.750)
}
$penetration = @{
    S0 = 0.00
    S1 = 0.00
    S2 = 0.00
    S3 = 0.00
    S4 = 0.00
    S5 = 0.25
    S6 = 0.50
    S7 = 1.00
}
$expectedDamageType = if ($ExpectedFamily -eq 'MAGIC_WEAPON') { 'tensura:magic' } else { 'tensura:holy_damage' }
$coordinates = [System.Collections.Generic.HashSet[string]]::new()

foreach ($case in $cases) {
    $expected = $policy[$case.TNO_stage]
    $expectedPenetration = if ([bool]$case.matching_Tensura_resistance_present -and
            -not [bool]$case.matching_Tensura_nullification_present) {
        [double]$penetration[$case.TNO_stage]
    } else { 0.0 }
    if ($null -eq $expected -or $case.suite -ne 'PHASE6_MAGIC_HOLY_PRODUCTION' -or
            $case.schema -ne 'tno.phase6.magic_holy_production.v1' -or
            $case.status -ne 'ok' -or $case.TNO_family -ne $ExpectedFamily -or
            $case.boss -ne $ExpectedBoss -or $case.APO_profile -ne 'NONE' -or
            -not [bool]$case.l2_initialized -or -not [bool]$case.legal_trait_profile -or
            -not [bool]$case.fresh_L2_attachment_per_case -or
            -not [bool]$case.production_feature_active_without_calibration_property -or
            [double]$case.Q_generic_health -ne [double]$expected[0] -or
            [double]$case.RD_dementor -ne [double]$expected[1] -or
            [double]$case.RA_adaptive -ne [double]$expected[2] -or
            [double]$case.penetration_percentage_applied -ne $expectedPenetration -or
            $case.resolved_production_stage -ne $case.TNO_stage -or
            [int]$case.shots_released -ne 10 -or [int]$case.hits_recorded -ne 10 -or
            [int]$case.production_rows -ne 10 -or [int]$case.family_event_count -ne 10 -or
            [int]$case.duplicate_event_count -ne 0 -or [int]$case.recursion_count -ne 0 -or
            [int]$case.unexpected_Tensura_bypass_count -ne 0 -or
            [int]$case.unexpected_L2_bypass_count -ne 0) {
        throw "Invalid production case: $($case | ConvertTo-Json -Depth 10 -Compress)"
    }
    $key = "$($case.level)|$($case.TNO_stage)|$($case.L2_profile_variant)"
    if (-not $coordinates.Add($key)) { throw "Duplicate case coordinate: $key" }
}

foreach ($row in $rows) {
    $expected = $policy[$row.TNO_stage]
    $expectedPenetration = if ([bool]$row.matching_Tensura_resistance_present -and
            -not [bool]$row.matching_Tensura_nullification_present) {
        [double]$penetration[$row.TNO_stage]
    } else { 0.0 }
    if ($null -eq $expected -or $row.TNO_family -ne $ExpectedFamily -or $row.boss -ne $ExpectedBoss -or
            $row.APO_profile -ne 'NONE' -or -not [bool]$row.production_feature_active_without_calibration_property -or
            [double]$row.Q_generic_health -ne [double]$expected[0] -or
            [double]$row.RD_dementor -ne [double]$expected[1] -or
            [double]$row.RA_adaptive -ne [double]$expected[2] -or
            [double]$row.penetration_percentage_applied -ne $expectedPenetration -or
            [int]$row.released_projectile_count -ne 1 -or
            [int]$row.physical_damage_event_count -ne 1 -or
            [int]$row.engraving_damage_event_count -ne 1 -or
            $row.physical_damage_source_id -ne 'minecraft:arrow' -or
            $row.family_damage_source_id -ne $expectedDamageType -or
            [bool]$row.duplicate_event_from_same_projectile -or
            [bool]$row.unexpected_source_duplication -or [bool]$row.event_recursion_observed -or
            [bool]$row.l2_layer_bypassed_unexpectedly -or [bool]$row.tensura_layer_bypassed_unexpectedly -or
            [bool]$row.royal_arrow_mark_observed -or [bool]$row.spectral_affix_projectile_conversion -or
            -not [bool]$row.royal_arrow_created -or -not [bool]$row.royal_arrow_ammunition_used -or
            [bool]$row.family_source_is_l2_magic -or [bool]$row.dispell_transformed) {
        throw "Production row identity/invariant failed: $($row.level)/$($row.TNO_stage)/$($row.hit_index)"
    }

    $nativeHealthAmount = if ([bool]$row.L2_exponentialHealth) {
        [math]::Pow(1.0 + [double]$row.L2_healthFactor, [int]$row.L2_level) - 1.0
    } else {
        [int]$row.L2_level * [double]$row.L2_healthFactor
    }
    $h = 1.0 + $nativeHealthAmount * [double]$row.entity_healthScale
    $q = [double]$expected[0]
    $rd = [double]$expected[1]
    $ra = [double]$expected[2]
    $input = [double]$row.production_expectation.input_after_Tensura
    $normalization = 1.0 + $q * ($h - 1.0)
    $genericPost = $input * $normalization
    $hasDementor = [bool]$row.production_expectation.Dementor_present
    $nativeDementor = if ($hasDementor) {
        if ($genericPost -lt 2.0) { $genericPost / 2.0 }
        else { [math]::Log($genericPost, [double]$row.Dementor_reduction_base) }
    } else { $genericPost }
    $dementorPost = $nativeDementor + $rd * ($genericPost - $nativeDementor)
    $hasAdaptive = [bool]$row.production_expectation.Adaptive_present
    $nativeAdaptive = if ($hasAdaptive) {
        [math]::Pow([double]$row.Adaptive_configured_factor, [int]$row.hit_index - 1)
    } else { 1.0 }
    $adaptiveFactor = $nativeAdaptive + $ra * (1.0 - $nativeAdaptive)
    $expectedFinal = $dementorPost * $adaptiveFactor
    $actualFinal = [double]$row.family_effect_final_event_amount
    if ([math]::Abs([double]$row.generic_L2_health_multiplier - $h) -gt 0.000001 -or
            [math]::Abs([double]$row.production_expectation.generic_normalization - $normalization) -gt 0.000001 -or
            [math]::Abs([double]$row.production_expectation.Dementor_negotiated_post - $dementorPost) -gt 0.001 -or
            [math]::Abs([double]$row.production_expectation.Adaptive_negotiated_factor - $adaptiveFactor) -gt 0.000001 -or
            [math]::Abs($actualFinal - $expectedFinal) -gt 0.001 -or
            -not [bool]$row.production_expectation.formula_matches_observation) {
        throw "Production formula mismatch: $($row.level)/$($row.TNO_stage)/$($row.L2_profile_variant)/hit$($row.hit_index)"
    }
    if (@('S0','S1','S2','S3','S4') -contains $row.TNO_stage -and
            ([math]::Abs($normalization - 1.0) -gt 0.000001 -or
             [math]::Abs($dementorPost - $nativeDementor) -gt 0.000001 -or
             [math]::Abs($adaptiveFactor - $nativeAdaptive) -gt 0.000001)) {
        throw "S0-S4 production negotiation changed native behavior"
    }
    if ([bool]$row.matching_Tensura_nullification_present -and
            ([double]$row.family_effect_final_event_amount -ne 0.0 -or -not [bool]$row.nullification_authoritative)) {
        throw "Matching Nullification was not absolute"
    }
}

if ($ExpectedBoss -eq 'tensura_neb:luminous_valentine') {
    if (@($cases | Where-Object { -not [bool]$_.matching_Tensura_resistance_present }).Count -ne 0 -or
            @($rows | Where-Object { -not [bool]$_.matching_Tensura_resistance_present }).Count -ne 0) {
        throw "Luminous matching Resistance was not present throughout the smoke capture"
    }
}

foreach ($group in ($rows | Group-Object level, TNO_stage, L2_profile_variant)) {
    $ordered = @($group.Group | Sort-Object {[int]$_.hit_index})
    if ($ordered.Count -ne 10 -or (@($ordered.hit_index) -join ',') -ne '1,2,3,4,5,6,7,8,9,10') {
        throw "Repeated-hit sequence incomplete: $($group.Name)"
    }
    if ([bool]$ordered[0].production_expectation.Adaptive_present -and
            @('S5','S6','S7') -contains $ordered[0].TNO_stage -and
            [double]$ordered[-1].production_expectation.Adaptive_negotiated_factor -ge
            [double]$ordered[0].production_expectation.Adaptive_negotiated_factor) {
        throw "Adaptive repeated-source harm disappeared: $($group.Name)"
    }
}

if ($ExpectedBoss -eq 'tensura:orc_disaster') {
    foreach ($level in @(300,600,800,1000)) {
        $accepted = @($cases | Where-Object {
            [int]$_.level -eq $level -and $_.L2_profile_variant -eq 'ACCEPTED_STRONGEST_LEGAL'
        })
        $dps = @{}
        foreach ($stage in @('S5','S6','S7')) {
            $dps[$stage] = [double]($accepted | Where-Object TNO_stage -eq $stage).DPS
        }
        if (-not ($dps.S5 -lt $dps.S6 -and $dps.S6 -lt $dps.S7)) {
            throw "Production Stage progression is not strict at Lv$level"
        }
        $s7 = [double]($accepted | Where-Object TNO_stage -eq 'S7').DPS
        $withoutDementor = [double]($cases | Where-Object {
            [int]$_.level -eq $level -and $_.L2_profile_variant -eq 'WITHOUT_DEMENTOR_CONTROL'
        }).DPS
        if ($s7 -ge $withoutDementor) { throw "Dementor is not measurably harmful at Lv$level" }
        if ($level -ge 600) {
            $withoutAdaptive = [double]($cases | Where-Object {
                [int]$_.level -eq $level -and $_.L2_profile_variant -eq 'WITHOUT_ADAPTIVE_CONTROL'
            }).DPS
            if ($s7 -ge $withoutAdaptive) { throw "Adaptive is not measurably harmful at Lv$level" }
        }
    }
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
$session | ForEach-Object { $_ | ConvertTo-Json -Depth 100 -Compress } |
    Set-Content -LiteralPath $OutputPath -Encoding utf8
Write-Output "Validated production acceptance: $($cases.Count) cases, $($rows.Count) rows, 0 case_error"
Write-Output "Wrote $OutputPath"
