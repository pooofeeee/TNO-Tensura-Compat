param(
    [string]$EvidencePath = 'docs/benchmarks/phase6-elemental-native-event-path/e2-runtime.jsonl',
    [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
$PSNativeCommandUseErrorActionPreference = $false
$extractor = Join-Path $PSScriptRoot 'extract-phase6-elemental-native-path.ps1'
$pwsh = Join-Path $PSHOME 'pwsh.exe'
$raw = [IO.File]::ReadAllLines((Resolve-Path -LiteralPath $EvidencePath))
$baseline = & $pwsh -NoProfile -File $extractor -LogPath $EvidencePath 2>&1
if ($LASTEXITCODE -ne 0) { throw "Baseline failed: $baseline" }
$temporary = Join-Path (Split-Path $PSScriptRoot) ('run/elemental-extractor-tests-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temporary | Out-Null
$results = [Collections.Generic.List[object]]::new()
function Reject([string]$Name, [scriptblock]$Mutation, [string]$Expected) {
    $records = @($raw | ConvertFrom-Json)
    $rows = @($records | Where-Object kind -eq row)
    & $Mutation $rows
    $path = Join-Path $temporary ($Name + '.jsonl')
    $records | ForEach-Object { $_ | ConvertTo-Json -Compress -Depth 30 } | Set-Content -LiteralPath $path
    $output = (& $pwsh -NoProfile -File $extractor -LogPath $path 2>&1) -join "`n"
    if ($LASTEXITCODE -eq 0 -or !$output.Contains($Expected)) {
        throw "Corruption $Name was not rejected for the expected reason ($Expected): $output"
    }
    $results.Add([ordered]@{test=$Name;status='PASS';expected_rejection=$Expected})
}
Reject 'missing_native_event' { param($rows)
    $rows[0].traces = @($rows[0].traces | Where-Object boundary -ne incoming_highest)
} 'missing/duplicated tensura:earth_elemental at incoming_highest'
Reject 'bypassed_projectile_gate' { param($rows)
    $rows[0].traces[0].detail = 'PASS/NONE'
} 'unexpected native gate/deflection'
Reject 'replaced_direct_projectile' { param($rows)
    ($rows[0].traces | Where-Object boundary -eq native_hurt_call).direct_uuid = [guid]::NewGuid().ToString()
} 'changed native source identity'
Reject 'double_scaling' { param($rows)
    ($rows[4].traces | Where-Object boundary -eq native_hurt_call).amount = 1.96
} 'wrong native hurt amount'
Reject 'uninitialized_l2' { param($rows)
    $rows[6].l2_initialized = $false
} 'invalid L2 initialization'
Reject 'fabricated_legacy_damage' { param($rows)
    $rows[1].traces += $rows[0].traces[4]
} 'trace projectile replaced'
Reject 'bypassed_nullification' { param($rows)
    ($rows[12].traces | Where-Object boundary -eq incoming_lowest).canceled = $false
} 'Nullification did not remain authoritative'
Reject 'unproven_fire_guard' { param($rows)
    $row = $rows | Where-Object { $_.traces | Where-Object { $_.boundary -eq 'native_hurt_call' -and $_.source_is_fire -and $_.target_fire_resistance } } | Select-Object -First 1
    if (!$row) { throw 'Evidence must include a real native Fire Resistance rejection' }
    ($row.traces | Where-Object boundary -eq native_hurt_call).target_fire_resistance = $false
} 'missing/duplicated tensura:fire_elemental at incoming_highest'
$report = [ordered]@{schema='tno.phase6.elemental_native_path.extractor_tests.v1';status='PASS';baseline='PASS';negative_tests=$results.Count;tests=@($results)}
$json = $report | ConvertTo-Json -Depth 8
if ($OutputPath) {
    if (Test-Path -LiteralPath $OutputPath) { throw 'Refusing to overwrite validation' }
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath), $json + "`n")
}
$json
