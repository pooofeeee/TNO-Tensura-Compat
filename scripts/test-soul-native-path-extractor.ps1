param([string]$EvidencePath='docs/benchmarks/phase6-soul-native-event-path/s2-runtime.jsonl',[ValidateSet('S2','S3','S3F')][string]$Checkpoint='S2',[string]$OutputPath)
$ErrorActionPreference='Stop'
$extractor=Join-Path $PSScriptRoot 'extract-phase6-soul-native-path.ps1'
$baseline=Get-Content -LiteralPath $EvidencePath
& $extractor -LogPath $EvidencePath -Checkpoint $Checkpoint | Out-Null
$mutations=[ordered]@{
    missing_spiritual_event={param($r) $r[2].traces=@($r[2].traces | Where-Object boundary -ne spiritual_event)}
    missing_physical_event={param($r) $r[2].traces=@($r[2].traces | Where-Object boundary -ne incoming_highest)}
    source_substitution={param($r) ($r[2].traces | Where-Object boundary -eq soul_source).source='tensura:magic'}
    duplicate_delivery={param($r) $r[2].projectile_uuid=$r[1].projectile_uuid}
    invalid_prerequisite={param($r) $r[2].can_hit=$false}
    non_ticking_target={param($r) $r[2].target_tick_at_release=0}
    incorrect_resource_accounting={param($r) $r[2].post.shp+=1}
    duplicate_soul_write={param($r) $r[2].traces+=@($r[2].traces | Where-Object boundary -eq shp_write_after)}
    callback_order={param($r) $callback=@($r[2].traces | Where-Object boundary -eq soul_callback);$r[2].traces=@($callback)+@($r[2].traces | Where-Object boundary -ne soul_callback)}
    changed_source_tags={param($r) ($r[2].traces | Where-Object boundary -eq soul_source).tags+=@('tno:synthetic')}
}
if($Checkpoint -eq 'S3') {
    $mutations['resistance_bypassed']={param($r) ($r[18].traces | Where-Object boundary -eq soul_return).result=$true}
    $mutations['l2_profile_changed']={param($r) $r[5].traits.'l2hostility:tank'=0}
    $mutations['native_cost_missing']={param($r) $r[13].traces=@($r[13].traces | Where-Object { !($_.boundary -eq 'resource_after' -and $_.resource -eq 'target_magicule') })}
}
if($Checkpoint -eq 'S3F') {
    $mutations=[ordered]@{
        soul_added_to_plain_control={param($r) $r[1].traces+=@($r[3].traces | Where-Object boundary -eq soul_callback)}
        missing_physical_attempt={param($r) $r[3].traces=@($r[3].traces | Where-Object boundary -ne physical_attempt)}
        substituted_soul_source={param($r) ($r[3].traces | Where-Object boundary -eq soul_source).source='tensura:magic'}
        repeated_projectile={param($r) $r[3].projectile_uuid=$r[1].projectile_uuid}
        resistance_bypassed={param($r) ($r[3].traces | Where-Object boundary -eq soul_return).result=$true}
        invented_shp_loss={param($r) $r[3].post.shp-=1}
        incorrect_stage={param($r) $r[2].stage='S0'}
        non_ticking_target={param($r) $r[3].target_tick_at_release=0}
    }
}
$results=@()
foreach($name in $mutations.Keys) {
    $records=@($baseline | ConvertFrom-Json); & $mutations[$name] $records
    $temp=Join-Path ([IO.Path]::GetTempPath()) ('soul-extractor-'+[guid]::NewGuid()+'.jsonl')
    try {
        [IO.File]::WriteAllLines($temp,@($records | ForEach-Object { $_ | ConvertTo-Json -Depth 60 -Compress }))
        $rejected=$false;$reason=''
        try { & $extractor -LogPath $temp -Checkpoint $Checkpoint | Out-Null } catch { $rejected=$true;$reason=$_.Exception.Message }
        if(!$rejected) { throw "Accepted corruption: $name" }
        $results += [ordered]@{mutation=$name;rejected=$true;reason=$reason}
    } finally { Remove-Item -LiteralPath $temp }
}
$report=[ordered]@{schema='tno.phase6.soul_native_path.extractor_tests.v1';status='PASS';negative_tests=$results.Count;results=$results}
$json=$report|ConvertTo-Json -Depth 20
if($OutputPath) { if(Test-Path -LiteralPath $OutputPath) { throw 'Refusing to overwrite evidence' };[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n") }
$json
