param(
    [Parameter(Mandatory = $true)]
    [string]$LogPath,

    [Parameter(Mandatory = $true)]
    [string]$OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('durability', 'classification', 'ceiling', 'health', 'dementor', 'adaptive', 'combined', 'safety')]
    [string]$Mode,

    [ValidateSet('MAGIC_WEAPON', 'HOLY_WEAPON')]
    [string]$ExpectedFamily
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE6_CALIBRATION '
$session = [System.Collections.Generic.List[object]]::new()

foreach ($line in Get-Content -LiteralPath $LogPath) {
    $markerIndex = $line.IndexOf($marker, [System.StringComparison]::Ordinal)
    $jsonText = if ($markerIndex -ge 0) {
        $line.Substring($markerIndex + $marker.Length)
    }
    elseif ($line.TrimStart().StartsWith('{')) {
        $line.Trim()
    }
    else { continue }
    if (-not $jsonText.TrimStart().StartsWith('{')) { continue }
    try { $record = $jsonText | ConvertFrom-Json -Depth 100 }
    catch { throw "Invalid calibration JSON in ${LogPath}: $jsonText" }
    if ($record.kind -eq 'suite_start' -or $record.kind -eq 'catalog') {
        $session.Clear()
    }
    $session.Add($record)
}

if ($session.Count -eq 0) { throw "No calibration records found in $LogPath" }
$errors = @($session | Where-Object kind -eq 'case_error')
if ($errors.Count -ne 0) { throw "Calibration session contains $($errors.Count) case_error record(s)" }
$suite = @($session | Where-Object kind -eq 'suite_result')
if ($suite.Count -ne 1) { throw "Expected one suite_result, found $($suite.Count)" }
if ($suite[0].status -ne 'complete') { throw 'suite_result is not complete' }

switch ($Mode) {
    'durability' {
        $rows = @($session | Where-Object kind -eq 'durability_result')
        if ($rows.Count -ne 16) { throw "Expected 16 durability_result records, found $($rows.Count)" }
        if ([int]$suite[0].case_count -ne 16 -or [int]$suite[0].requested_case_count -ne 16) {
            throw 'Durability suite count mismatch'
        }
        $expectedBosses = @(
            'tensura_neb:luminous_valentine', 'tensura:hinata_sakaguchi',
            'tensura:gazel_dwargo', 'tensura:orc_disaster')
        $expectedLevels = @(300, 600, 800, 1000)
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($row in $rows) {
            if ($row.status -ne 'complete' -or $row.APO_profile -ne 'NONE') { throw "Invalid row status/profile: $($row | ConvertTo-Json -Compress)" }
            if ($expectedBosses -notcontains $row.boss -or $expectedLevels -notcontains [int]$row.L2_level) { throw "Unexpected target/level: $($row.boss) Lv$($row.L2_level)" }
            if (-not $keys.Add("$($row.boss)|$($row.L2_level)")) { throw "Duplicate target/level: $($row.boss) Lv$($row.L2_level)" }
            if ([math]::Abs([double]$row.generic_L2_health_modifier_amount - [double]$row.generic_L2_health_modifier_expected_amount) -gt 0.000001) { throw 'Generic L2 health formula mismatch' }
            if ([bool]$row.generic_L2_health_modifier_present_on_SHP) { throw 'L2 hostility_health unexpectedly appeared on SHP' }
            if ([math]::Abs([double]$row.Tensura_L2H_datapack_SHP_modifier_amount - [double]$row.Tensura_L2H_datapack_SHP_expected_amount) -gt 0.000001) { throw 'Tensura:L2Hostility SHP formula mismatch' }
        }
    }
    'classification' {
        $rows = @($session | Where-Object kind -eq 'classification_result')
        if ($rows.Count -ne 2) { throw "Expected 2 classification_result records, found $($rows.Count)" }
        if ([int]$suite[0].case_count -ne 2 -or [int]$suite[0].requested_case_count -ne 2) { throw 'Classification suite count mismatch' }
        $expected = @('tensura:magic', 'tensura:holy_damage')
        foreach ($row in $rows) {
            if ($row.status -ne 'complete' -or $expected -notcontains $row.damage_type) { throw 'Invalid classification row' }
            if (-not [bool]$row.minecraft_bypasses_armor) { throw "$($row.damage_type) lost bypasses_armor" }
            if ([bool]$row.neoforge_is_magic -or [bool]$row.minecraft_bypasses_effects -or [bool]$row.minecraft_bypasses_invulnerability) { throw "$($row.damage_type) classification changed" }
            if (-not [bool]$row.L2_Dementor_eligible -or [bool]$row.L2_Dispell_eligible) { throw "$($row.damage_type) L2 routing changed" }
        }
    }
    'ceiling' {
        if (-not $ExpectedFamily) { throw 'ceiling mode requires -ExpectedFamily' }
        $rows = @($session | Where-Object kind -eq 'row')
        $cases = @($session | Where-Object kind -eq 'case_result')
        if ($rows.Count -ne 720) { throw "Expected 720 rows, found $($rows.Count)" }
        if ($cases.Count -ne 72) { throw "Expected 72 case_result records, found $($cases.Count)" }
        if ([int]$suite[0].case_count -ne 72 -or [int]$suite[0].requested_case_count -ne 72) {
            throw 'Ceiling suite count mismatch'
        }
        $expectedLevels = @(300, 600, 800, 1000)
        $expectedStages = @('S5', 'S6', 'S7')
        $expectedCases = @(
            'CASE_0_BASELINE', 'CASE_1_DEMENTOR_100', 'CASE_2_ADAPTIVE_100',
            'CASE_3_DEMENTOR_ADAPTIVE_100', 'CASE_4_GENERIC_HEALTH_100', 'CASE_5_ALL_100')
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($case in $cases) {
            if ($case.status -ne 'ok' -or $case.TNO_family -ne $ExpectedFamily -or $case.APO_profile -ne 'NONE') {
                throw 'Invalid ceiling case status/family/profile'
            }
            if ($expectedLevels -notcontains [int]$case.level -or $expectedStages -notcontains $case.TNO_stage -or
                    $expectedCases -notcontains $case.calibration_case) { throw 'Unexpected ceiling case coordinate' }
            if (-not $keys.Add("$($case.level)|$($case.TNO_stage)|$($case.calibration_case)")) {
                throw 'Duplicate ceiling case coordinate'
            }
            if ([int]$case.shots_released -ne 10 -or [int]$case.hits_recorded -ne 10 -or
                    [int]$case.calibration_trace_count -ne 10) { throw 'Ceiling case release/hit/trace mismatch' }
        }
        foreach ($row in $rows) {
            if ($row.TNO_family -ne $ExpectedFamily -or $row.APO_profile -ne 'NONE' -or
                    [int]$row.calibration_trace_count -ne 1) { throw 'Invalid ceiling row family/profile/trace count' }
            if ([int]$row.engraving_damage_event_count -ne 1 -or
                    [double]$row.calibration_trace.eligible_amount_before_Tensura_defense -lt 0.0) {
                throw 'Ceiling row lost or duplicated its one eligible native event'
            }
            if ([bool]$row.l2_layer_bypassed_unexpectedly -or [bool]$row.tensura_layer_bypassed_unexpectedly -or
                    [bool]$row.unexpected_source_duplication -or [bool]$row.event_recursion_observed) {
                throw 'Ceiling row contains a bypass, duplicate, or recursion failure'
            }
            $trace = $row.calibration_trace
            $expectedSource = if ($ExpectedFamily -eq 'MAGIC_WEAPON') { 'tensura.magic' } else { 'tensura.holy_damage' }
            if ($trace.Adaptive_source_msgId -ne $expectedSource) { throw 'Calibration source identity changed' }
            $expectedH = 1.0 + [int]$row.level * 0.03 * 1.2
            if ([math]::Abs([double]$trace.generic_L2_health_multiplier - $expectedH) -gt 0.00001) {
                throw 'Generic L2 health multiplier mismatch'
            }
            $expectedGeneric = [double]$trace.generic_input *
                (1.0 + [double]$row.Q_generic_health * ($expectedH - 1.0))
            if ([math]::Abs([double]$trace.generic_diagnostic_output - $expectedGeneric) -gt 0.001) {
                throw 'Generic normalization formula mismatch'
            }
            if ([double]$row.Q_generic_health -eq 0.0 -and
                    [math]::Abs([double]$trace.generic_diagnostic_output - [double]$trace.generic_input) -gt 0.001) {
                throw 'Q=0 changed native behavior'
            }
            if ([bool]$trace.Dementor_applied) {
                $x = [double]$trace.Dementor_pre
                $nativeDementor = if ($x -lt 2.0) { $x / 2.0 } else { [math]::Log($x, 2.0) }
                if ([math]::Abs([double]$trace.Dementor_native_post - $nativeDementor) -gt 0.001) {
                    throw 'Native Dementor formula mismatch'
                }
                $expectedDementor = $nativeDementor + [double]$row.RD_dementor * ($x - $nativeDementor)
                if ([math]::Abs([double]$trace.Dementor_diagnostic_post - $expectedDementor) -gt 0.001) {
                    throw 'Dementor diagnostic formula mismatch'
                }
                if ([double]$row.RD_dementor -eq 0.0 -and
                        [math]::Abs([double]$trace.Dementor_diagnostic_post - [double]$trace.Dementor_native_post) -gt 0.001) {
                    throw 'RD=0 changed native Dementor behavior'
                }
                if ([double]$trace.Dementor_diagnostic_post -gt [double]$trace.Dementor_pre + 0.001) {
                    throw 'Dementor diagnostic recovery exceeded its reducer input'
                }
            }
            if ([bool]$trace.Adaptive_applied) {
                $expectedFactor = [math]::Pow([double]$trace.Adaptive_configured_factor,
                    [int]$trace.Adaptive_adaptation_count - 1)
                if ([math]::Abs([double]$trace.Adaptive_native_factor - $expectedFactor) -gt 0.000001) {
                    throw 'Native Adaptive factor mismatch'
                }
                $negotiated = $expectedFactor + [double]$row.RA_adaptive * (1.0 - $expectedFactor)
                if ([math]::Abs([double]$trace.Adaptive_negotiated_factor - $negotiated) -gt 0.000001) {
                    throw 'Adaptive diagnostic formula mismatch'
                }
                if ([double]$row.RA_adaptive -eq 0.0 -and
                        [math]::Abs([double]$trace.Adaptive_negotiated_factor - [double]$trace.Adaptive_native_factor) -gt 0.000001) {
                    throw 'RA=0 changed native Adaptive behavior'
                }
                if ([double]$trace.Adaptive_diagnostic_result -gt [double]$trace.Adaptive_pre + 0.001) {
                    throw 'Adaptive diagnostic recovery exceeded its reducer input'
                }
            }
            if ([math]::Abs([double]$trace.final_family_event_amount - [double]$row.family_effect_final_event_amount) -gt 0.001) {
                throw 'Final family event/trace mismatch'
            }
        }
        foreach ($group in ($rows | Group-Object level, TNO_stage, calibration_case)) {
            $ordered = @($group.Group | Sort-Object {[int]$_.hit_index})
            if ($ordered.Count -ne 10 -or (@($ordered.hit_index) -join ',') -ne '1,2,3,4,5,6,7,8,9,10') {
                throw 'Repeated-hit sequence is incomplete or out of order'
            }
            if ([bool]$ordered[0].calibration_trace.Adaptive_applied) {
                $counts = @($ordered | ForEach-Object {[int]$_.calibration_trace.Adaptive_adaptation_count})
                if (($counts -join ',') -ne '1,2,3,4,5,6,7,8,9,10') {
                    throw 'Adaptive state was reset or did not advance naturally'
                }
            }
        }
    }
    'health' {
        if (-not $ExpectedFamily) { throw 'health mode requires -ExpectedFamily' }
        $rows = @($session | Where-Object kind -eq 'row')
        $cases = @($session | Where-Object kind -eq 'case_result')
        if ($rows.Count -ne 600 -or $cases.Count -ne 60 -or
                [int]$suite[0].case_count -ne 60 -or [int]$suite[0].requested_case_count -ne 60) {
            throw "Health suite count mismatch: cases=$($cases.Count), rows=$($rows.Count)"
        }
        $expectedQ = @(0.0, 0.25, 0.5, 0.75, 1.0)
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($case in $cases) {
            if ($case.status -ne 'ok' -or $case.calibration_mode -ne 'health' -or
                    $case.TNO_family -ne $ExpectedFamily -or $case.APO_profile -ne 'NONE' -or
                    @(300,600,800,1000) -notcontains [int]$case.level -or
                    @('S5','S6','S7') -notcontains $case.TNO_stage -or
                    $expectedQ -notcontains [double]$case.Q_generic_health -or
                    [double]$case.RD_dementor -ne 0.0 -or [double]$case.RA_adaptive -ne 0.0 -or
                    [int]$case.shots_released -ne 10 -or [int]$case.hits_recorded -ne 10 -or
                    [int]$case.calibration_trace_count -ne 10) { throw 'Invalid health case' }
            if (-not $keys.Add("$($case.level)|$($case.TNO_stage)|$($case.Q_generic_health)")) {
                throw 'Duplicate health case coordinate'
            }
        }
        foreach ($row in $rows) {
            $trace = $row.calibration_trace
            $expectedSource = if ($ExpectedFamily -eq 'MAGIC_WEAPON') { 'tensura.magic' } else { 'tensura.holy_damage' }
            if ($row.TNO_family -ne $ExpectedFamily -or $row.APO_profile -ne 'NONE' -or
                    [int]$row.calibration_trace_count -ne 1 -or [int]$row.engraving_damage_event_count -ne 1 -or
                    $trace.Adaptive_source_msgId -ne $expectedSource -or
                    [bool]$row.l2_layer_bypassed_unexpectedly -or [bool]$row.tensura_layer_bypassed_unexpectedly -or
                    [bool]$row.unexpected_source_duplication -or [bool]$row.event_recursion_observed) {
                throw 'Invalid health row identity/invariant'
            }
            $expectedH = 1.0 + [int]$row.level * 0.03 * 1.2
            $expectedOutput = [double]$trace.generic_input *
                (1.0 + [double]$row.Q_generic_health * ($expectedH - 1.0))
            if ([math]::Abs([double]$trace.generic_L2_health_multiplier - $expectedH) -gt 0.00001 -or
                    [math]::Abs([double]$trace.generic_diagnostic_output - $expectedOutput) -gt 0.001 -or
                    [math]::Abs([double]$trace.Dementor_diagnostic_post - [double]$trace.Dementor_native_post) -gt 0.001) {
                throw 'Health row formula or RD=0 invariant failed'
            }
            if ([bool]$trace.Adaptive_applied -and
                    [math]::Abs([double]$trace.Adaptive_negotiated_factor - [double]$trace.Adaptive_native_factor) -gt 0.000001) {
                throw 'Health row RA=0 changed Adaptive'
            }
            if ([math]::Abs([double]$trace.final_family_event_amount - [double]$row.family_effect_final_event_amount) -gt 0.001) {
                throw 'Health final family event/trace mismatch'
            }
        }
        foreach ($group in ($rows | Group-Object level, TNO_stage, calibration_case)) {
            $ordered = @($group.Group | Sort-Object {[int]$_.hit_index})
            if ($ordered.Count -ne 10) { throw 'Health repeated-hit sequence count mismatch' }
            if ([bool]$ordered[0].calibration_trace.Adaptive_applied -and
                    (@($ordered | ForEach-Object {[int]$_.calibration_trace.Adaptive_adaptation_count}) -join ',') -ne
                    '1,2,3,4,5,6,7,8,9,10') { throw 'Health sweep reset Adaptive state' }
        }
    }
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
$session | ForEach-Object { $_ | ConvertTo-Json -Depth 100 -Compress } | Set-Content -LiteralPath $OutputPath -Encoding utf8
Write-Output "Validated $Mode calibration: $($suite[0].case_count)/$($suite[0].requested_case_count) cases, 0 case_error"
Write-Output "Wrote $OutputPath"
