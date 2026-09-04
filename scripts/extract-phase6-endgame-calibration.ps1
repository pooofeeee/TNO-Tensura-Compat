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
    'dementor' {
        if (-not $ExpectedFamily) { throw 'dementor mode requires -ExpectedFamily' }
        $rows = @($session | Where-Object kind -eq 'row')
        $cases = @($session | Where-Object kind -eq 'case_result')
        if ($rows.Count -ne 1200 -or $cases.Count -ne 120 -or
                [int]$suite[0].case_count -ne 120 -or [int]$suite[0].requested_case_count -ne 120) {
            throw "Dementor suite count mismatch: cases=$($cases.Count), rows=$($rows.Count)"
        }
        $profiles = @('ACCEPTED_STRONGEST_LEGAL', 'WITHOUT_DEMENTOR_CONTROL')
        $expectedRD = @(0.0, 0.25, 0.5, 0.75, 1.0)
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($case in $cases) {
            if ($case.status -ne 'ok' -or $case.calibration_mode -ne 'dementor' -or
                    $case.TNO_family -ne $ExpectedFamily -or $case.APO_profile -ne 'NONE' -or
                    $profiles -notcontains $case.L2_profile_variant -or $expectedRD -notcontains [double]$case.RD_dementor -or
                    [double]$case.Q_generic_health -ne 0.0 -or [double]$case.RA_adaptive -ne 0.0 -or
                    [int]$case.shots_released -ne 10 -or [int]$case.hits_recorded -ne 10 -or
                    [int]$case.calibration_trace_count -ne 10) { throw 'Invalid Dementor case' }
            if (-not $keys.Add("$($case.level)|$($case.TNO_stage)|$($case.L2_profile_variant)|$($case.RD_dementor)")) {
                throw 'Duplicate Dementor case coordinate'
            }
        }
        foreach ($row in $rows) {
            $trace = $row.calibration_trace
            $expectedSource = if ($ExpectedFamily -eq 'MAGIC_WEAPON') { 'tensura.magic' } else { 'tensura.holy_damage' }
            $withDementor = $row.L2_profile_variant -eq 'ACCEPTED_STRONGEST_LEGAL'
            if ($row.TNO_family -ne $ExpectedFamily -or $row.APO_profile -ne 'NONE' -or
                    [int]$row.calibration_trace_count -ne 1 -or [int]$row.engraving_damage_event_count -ne 1 -or
                    $trace.Adaptive_source_msgId -ne $expectedSource -or
                    [bool]$trace.Dementor_applied -ne $withDementor -or
                    [bool]$row.l2_layer_bypassed_unexpectedly -or [bool]$row.tensura_layer_bypassed_unexpectedly -or
                    [bool]$row.unexpected_source_duplication -or [bool]$row.event_recursion_observed) {
                throw 'Invalid Dementor row identity/invariant'
            }
            $x = [double]$trace.Dementor_pre
            $native = if ($withDementor) {
                if ($x -lt 2.0) { $x / 2.0 } else { [math]::Log($x, 2.0) }
            }
            else { $x }
            $expected = $native + [double]$row.RD_dementor * ($x - $native)
            if ([math]::Abs([double]$trace.Dementor_native_post - $native) -gt 0.001 -or
                    [math]::Abs([double]$trace.Dementor_diagnostic_post - $expected) -gt 0.001 -or
                    [double]$trace.Dementor_diagnostic_post -gt $x + 0.001 -or
                    [math]::Abs([double]$trace.generic_diagnostic_output - [double]$trace.generic_input) -gt 0.001) {
                throw 'Dementor reducer formula/bound failed'
            }
            if ([bool]$trace.Adaptive_applied -and
                    [math]::Abs([double]$trace.Adaptive_negotiated_factor - [double]$trace.Adaptive_native_factor) -gt 0.000001) {
                throw 'Dementor sweep changed native Adaptive behavior'
            }
            if ([math]::Abs([double]$trace.final_family_event_amount - [double]$row.family_effect_final_event_amount) -gt 0.001) {
                throw 'Dementor final family event/trace mismatch'
            }
        }
        foreach ($group in ($rows | Group-Object level, TNO_stage, L2_profile_variant, calibration_case)) {
            $ordered = @($group.Group | Sort-Object {[int]$_.hit_index})
            if ($ordered.Count -ne 10) { throw 'Dementor repeated-hit sequence count mismatch' }
            if ([bool]$ordered[0].calibration_trace.Adaptive_applied -and
                    (@($ordered | ForEach-Object {[int]$_.calibration_trace.Adaptive_adaptation_count}) -join ',') -ne
                    '1,2,3,4,5,6,7,8,9,10') { throw 'Dementor sweep reset Adaptive state' }
        }
    }
    'adaptive' {
        if (-not $ExpectedFamily) { throw 'adaptive mode requires -ExpectedFamily' }
        $rows = @($session | Where-Object kind -eq 'row')
        $cases = @($session | Where-Object kind -eq 'case_result')
        if ($rows.Count -ne 1200 -or $cases.Count -ne 120 -or
                [int]$suite[0].case_count -ne 120 -or [int]$suite[0].requested_case_count -ne 120) {
            throw "Adaptive suite count mismatch: cases=$($cases.Count), rows=$($rows.Count)"
        }
        $profiles = @('ACCEPTED_STRONGEST_LEGAL', 'WITHOUT_ADAPTIVE_CONTROL')
        $expectedRA = @(0.0, 0.25, 0.5, 0.75, 1.0)
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($case in $cases) {
            if ($case.status -ne 'ok' -or $case.calibration_mode -ne 'adaptive' -or
                    $case.TNO_family -ne $ExpectedFamily -or $case.APO_profile -ne 'NONE' -or
                    $profiles -notcontains $case.L2_profile_variant -or $expectedRA -notcontains [double]$case.RA_adaptive -or
                    [double]$case.Q_generic_health -ne 0.0 -or [double]$case.RD_dementor -ne 0.0 -or
                    [int]$case.shots_released -ne 10 -or [int]$case.hits_recorded -ne 10 -or
                    [int]$case.calibration_trace_count -ne 10) { throw 'Invalid Adaptive case' }
            if (-not $keys.Add("$($case.level)|$($case.TNO_stage)|$($case.L2_profile_variant)|$($case.RA_adaptive)")) {
                throw 'Duplicate Adaptive case coordinate'
            }
        }
        foreach ($row in $rows) {
            $trace = $row.calibration_trace
            $expectedSource = if ($ExpectedFamily -eq 'MAGIC_WEAPON') { 'tensura.magic' } else { 'tensura.holy_damage' }
            $withAdaptive = $row.L2_profile_variant -eq 'ACCEPTED_STRONGEST_LEGAL' -and [int]$row.level -ge 600
            if ($row.TNO_family -ne $ExpectedFamily -or $row.APO_profile -ne 'NONE' -or
                    [int]$row.calibration_trace_count -ne 1 -or [int]$row.engraving_damage_event_count -ne 1 -or
                    $trace.Adaptive_source_msgId -ne $expectedSource -or
                    [bool]$trace.Adaptive_applied -ne $withAdaptive -or
                    [bool]$row.l2_layer_bypassed_unexpectedly -or [bool]$row.tensura_layer_bypassed_unexpectedly -or
                    [bool]$row.unexpected_source_duplication -or [bool]$row.event_recursion_observed) {
                throw 'Invalid Adaptive row identity/invariant'
            }
            if ([math]::Abs([double]$trace.generic_diagnostic_output - [double]$trace.generic_input) -gt 0.001 -or
                    [math]::Abs([double]$trace.Dementor_diagnostic_post - [double]$trace.Dementor_native_post) -gt 0.001) {
                throw 'Adaptive sweep changed generic or Dementor behavior'
            }
            $nativeFactor = if ($withAdaptive) {
                [math]::Pow([double]$trace.Adaptive_configured_factor,
                    [int]$trace.Adaptive_adaptation_count - 1)
            }
            else { 1.0 }
            $expectedFactor = $nativeFactor + [double]$row.RA_adaptive * (1.0 - $nativeFactor)
            if ([math]::Abs([double]$trace.Adaptive_native_factor - $nativeFactor) -gt 0.000001 -or
                    [math]::Abs([double]$trace.Adaptive_negotiated_factor - $expectedFactor) -gt 0.000001 -or
                    [math]::Abs([double]$trace.Adaptive_diagnostic_result -
                        ([double]$trace.Adaptive_pre * $expectedFactor)) -gt 0.001 -or
                    [double]$trace.Adaptive_diagnostic_result -gt [double]$trace.Adaptive_pre + 0.001) {
                throw 'Adaptive factor formula/bound failed'
            }
            if ([math]::Abs([double]$trace.final_family_event_amount - [double]$row.family_effect_final_event_amount) -gt 0.001) {
                throw 'Adaptive final family event/trace mismatch'
            }
        }
        foreach ($group in ($rows | Group-Object level, TNO_stage, L2_profile_variant, calibration_case)) {
            $ordered = @($group.Group | Sort-Object {[int]$_.hit_index})
            if ($ordered.Count -ne 10) { throw 'Adaptive repeated-hit sequence count mismatch' }
            if ([bool]$ordered[0].calibration_trace.Adaptive_applied) {
                $counts = @($ordered | ForEach-Object {[int]$_.calibration_trace.Adaptive_adaptation_count})
                if (($counts -join ',') -ne '1,2,3,4,5,6,7,8,9,10') { throw 'Adaptive state was reset' }
                if ([double]$ordered[-1].calibration_trace.Adaptive_negotiated_factor -ge
                        [double]$ordered[0].calibration_trace.Adaptive_negotiated_factor -and
                        [double]$ordered[0].RA_adaptive -lt 1.0) { throw 'Adaptive repeated-source penalty disappeared' }
            }
        }
    }
    'combined' {
        if (-not $ExpectedFamily) { throw 'combined mode requires -ExpectedFamily' }
        $rows = @($session | Where-Object kind -eq 'row')
        $cases = @($session | Where-Object kind -eq 'case_result')
        if ($rows.Count -ne 1350 -or $cases.Count -ne 135 -or
                [int]$suite[0].case_count -ne 135 -or [int]$suite[0].requested_case_count -ne 135) {
            throw "Combined suite count mismatch: cases=$($cases.Count), rows=$($rows.Count)"
        }
        $profiles = @(
            'ACCEPTED_STRONGEST_LEGAL', 'WITHOUT_DEMENTOR_CONTROL',
            'WITHOUT_ADAPTIVE_CONTROL', 'WITHOUT_DEMENTOR_ADAPTIVE_CONTROL',
            'WITHOUT_REGENERATE_CONTROL')
        $parameters = @{
            'COMBINED_LOW_S5'  = @(0.25,   0.50,  0.50)
            'COMBINED_LOW_S6'  = @(0.375,  0.625, 0.625)
            'COMBINED_LOW_S7'  = @(0.50,   0.75,  0.75)
            'COMBINED_MID_S5'  = @(0.375,  0.50,  0.50)
            'COMBINED_MID_S6'  = @(0.5625, 0.625, 0.625)
            'COMBINED_MID_S7'  = @(0.75,   0.75,  0.75)
            'COMBINED_HIGH_S5' = @(0.50,   0.50,  0.50)
            'COMBINED_HIGH_S6' = @(0.75,   0.625, 0.625)
            'COMBINED_HIGH_S7' = @(1.00,   0.75,  0.75)
        }
        $keys = [System.Collections.Generic.HashSet[string]]::new()
        foreach ($case in $cases) {
            $expected = $parameters[$case.calibration_case]
            if ($null -eq $expected -or $case.status -ne 'ok' -or $case.calibration_mode -ne 'combined' -or
                    $case.TNO_family -ne $ExpectedFamily -or $case.APO_profile -ne 'NONE' -or
                    @(600,800,1000) -notcontains [int]$case.level -or
                    @('S5','S6','S7') -notcontains $case.TNO_stage -or
                    $profiles -notcontains $case.L2_profile_variant -or
                    -not [bool]$case.fresh_L2_attachment_per_case -or [bool]$case.profile_clone_verified -or
                    [double]$case.Q_generic_health -ne [double]$expected[0] -or
                    [double]$case.RD_dementor -ne [double]$expected[1] -or
                    [double]$case.RA_adaptive -ne [double]$expected[2] -or
                    -not [bool]$case.legal_trait_profile -or
                    [int]$case.shots_released -ne 10 -or [int]$case.hits_recorded -ne 10 -or
                    [int]$case.calibration_trace_count -ne 10) { throw 'Invalid combined case' }
            if ($case.calibration_case -notmatch "_$($case.TNO_stage)$") {
                throw 'Combined candidate was paired with the wrong Stage'
            }
            if (-not $keys.Add("$($case.level)|$($case.TNO_stage)|$($case.L2_profile_variant)|$($case.calibration_case)")) {
                throw 'Duplicate combined case coordinate'
            }
            $hasRegenerate = $case.L2_profile_variant -ne 'WITHOUT_REGENERATE_CONTROL'
            $expectedRank = if ($hasRegenerate) { if ([int]$case.level -eq 600) { 4 } else { 5 } } else { 0 }
            if ([int]$case.Regenerate_rank -ne $expectedRank -or
                    [math]::Abs([double]$case.Regenerate_nominal_HP_per_second -
                        ([double]$case.HP * [double]$case.Regenerate_config_fraction_per_rank_per_second * $expectedRank)) -gt 0.001) {
                throw 'Combined Regenerate rank/rate mismatch'
            }
            if ($case.L2_profile_variant -eq 'ACCEPTED_STRONGEST_LEGAL') {
                if (-not [bool]$case.profile_is_accepted_strongest_legal -or [bool]$case.removed_trait_budget_not_reallocated) {
                    throw 'Accepted combined profile flags are invalid'
                }
            }
            elseif (-not [bool]$case.removed_trait_budget_not_reallocated) {
                throw 'Combined control reallocated removed trait budget'
            }
        }
        foreach ($row in $rows) {
            $trace = $row.calibration_trace
            $expectedSource = if ($ExpectedFamily -eq 'MAGIC_WEAPON') { 'tensura.magic' } else { 'tensura.holy_damage' }
            $withDementor = @('WITHOUT_DEMENTOR_CONTROL','WITHOUT_DEMENTOR_ADAPTIVE_CONTROL') -notcontains $row.L2_profile_variant
            $withAdaptive = @('WITHOUT_ADAPTIVE_CONTROL','WITHOUT_DEMENTOR_ADAPTIVE_CONTROL') -notcontains $row.L2_profile_variant
            if ($row.TNO_family -ne $ExpectedFamily -or $row.APO_profile -ne 'NONE' -or
                    [int]$row.calibration_trace_count -ne 1 -or [int]$row.engraving_damage_event_count -ne 1 -or
                    $trace.Adaptive_source_msgId -ne $expectedSource -or
                    [bool]$trace.Dementor_applied -ne $withDementor -or
                    [bool]$trace.Adaptive_applied -ne $withAdaptive -or
                    [bool]$row.l2_layer_bypassed_unexpectedly -or [bool]$row.tensura_layer_bypassed_unexpectedly -or
                    [bool]$row.unexpected_source_duplication -or [bool]$row.event_recursion_observed) {
                throw 'Invalid combined row identity/invariant'
            }
            $expectedH = 1.0 + [int]$row.level * 0.03 * 1.2
            $expectedGeneric = [double]$trace.generic_input *
                (1.0 + [double]$row.Q_generic_health * ($expectedH - 1.0))
            if ([math]::Abs([double]$trace.generic_L2_health_multiplier - $expectedH) -gt 0.00001 -or
                    [math]::Abs([double]$trace.generic_diagnostic_output - $expectedGeneric) -gt 0.001) {
                throw 'Combined generic normalization formula failed'
            }
            $x = [double]$trace.Dementor_pre
            $nativeDementor = if ($withDementor) {
                if ($x -lt 2.0) { $x / 2.0 } else { [math]::Log($x, 2.0) }
            }
            else { $x }
            $expectedDementor = $nativeDementor + [double]$row.RD_dementor * ($x - $nativeDementor)
            if ([math]::Abs([double]$trace.Dementor_native_post - $nativeDementor) -gt 0.001 -or
                    [math]::Abs([double]$trace.Dementor_diagnostic_post - $expectedDementor) -gt 0.001 -or
                    [double]$trace.Dementor_diagnostic_post -gt $x + 0.001) {
                throw 'Combined Dementor formula/bound failed'
            }
            $nativeAdaptiveFactor = if ($withAdaptive) {
                [math]::Pow([double]$trace.Adaptive_configured_factor,
                    [int]$trace.Adaptive_adaptation_count - 1)
            }
            else { 1.0 }
            $expectedAdaptiveFactor = $nativeAdaptiveFactor +
                [double]$row.RA_adaptive * (1.0 - $nativeAdaptiveFactor)
            if ([math]::Abs([double]$trace.Adaptive_native_factor - $nativeAdaptiveFactor) -gt 0.000001 -or
                    [math]::Abs([double]$trace.Adaptive_negotiated_factor - $expectedAdaptiveFactor) -gt 0.000001 -or
                    [math]::Abs([double]$trace.Adaptive_diagnostic_result -
                        ([double]$trace.Adaptive_pre * $expectedAdaptiveFactor)) -gt 0.001 -or
                    [double]$trace.Adaptive_diagnostic_result -gt [double]$trace.Adaptive_pre + 0.001 -or
                    [math]::Abs([double]$trace.final_family_event_amount - [double]$row.family_effect_final_event_amount) -gt 0.001) {
                throw 'Combined Adaptive/final-event formula failed'
            }
        }
        foreach ($group in ($rows | Group-Object level, TNO_stage, L2_profile_variant, calibration_case)) {
            $ordered = @($group.Group | Sort-Object {[int]$_.hit_index})
            if ($ordered.Count -ne 10 -or (@($ordered.hit_index) -join ',') -ne '1,2,3,4,5,6,7,8,9,10') {
                throw 'Combined repeated-hit sequence count/order mismatch'
            }
            if ([bool]$ordered[0].calibration_trace.Adaptive_applied) {
                $counts = @($ordered | ForEach-Object {[int]$_.calibration_trace.Adaptive_adaptation_count})
                if (($counts -join ',') -ne '1,2,3,4,5,6,7,8,9,10') { throw 'Combined candidate reset Adaptive state' }
                if ([double]$ordered[-1].calibration_trace.Adaptive_negotiated_factor -ge
                        [double]$ordered[0].calibration_trace.Adaptive_negotiated_factor) {
                    throw 'Combined candidate erased Adaptive repeated-source harm'
                }
            }
        }
    }
}

$parent = Split-Path -Parent $OutputPath
if ($parent) { New-Item -ItemType Directory -Path $parent -Force | Out-Null }
$session | ForEach-Object { $_ | ConvertTo-Json -Depth 100 -Compress } | Set-Content -LiteralPath $OutputPath -Encoding utf8
Write-Output "Validated $Mode calibration: $($suite[0].case_count)/$($suite[0].requested_case_count) cases, 0 case_error"
Write-Output "Wrote $OutputPath"
