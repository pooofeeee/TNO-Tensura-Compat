param([string]$EvidencePath='docs/benchmarks/phase6-energy-steal-physical-prerequisite/es3a-runtime.jsonl',[string]$OutputPath)
$ErrorActionPreference='Stop';$extractor=Join-Path $PSScriptRoot 'extract-phase6-energy-comparison.ps1'
$baseline=Get-Content -LiteralPath $EvidencePath
& $extractor -LogPath $EvidencePath | Out-Null
$mutations=[ordered]@{
    missing_physical_attempt={param($r) $r[2].traces=@($r[2].traces|Where-Object boundary -ne physical_attempt)}
    forged_energy_callback_on_plain={param($r) $r[1].traces+=@($r[2].traces|Where-Object boundary -eq energy_callback)}
    duplicate_drain={param($r) $r[2].traces+=@($r[2].traces|Where-Object boundary -eq drain_enter)}
    wrong_projectile={param($r) ($r[2].traces|Where-Object boundary -eq physical_attempt).direct_uuid=$r[1].projectile_uuid}
    wrong_source={param($r) ($r[2].traces|Where-Object boundary -eq physical_attempt).source='tensura:energy_drain'}
    wrong_percentage={param($r) foreach($t in $r[2].traces){if($t.boundary -in @('drain_enter','energy_event','drain_return')){$t.amount*=1.4}}}
    coherent_wrong_target_loss={param($r)
        $write=($r[2].traces|Where-Object {$_.boundary -eq 'resource_after' -and $_.resource -eq 'target_magicule'})[0].sequence
        foreach($t in $r[2].traces){if($t.sequence -ge $write){$t.target_magicule-=1};if($t.sequence -ge $write-1 -and $t.resource -eq 'target_magicule'){$t.requested-=1}}
        $r[2].post.target_magicule-=1
    }
    coherent_wrong_capped_gain={param($r)
        $write=($r[2].traces|Where-Object {$_.boundary -eq 'resource_after' -and $_.resource -eq 'owner_magicule'}).sequence
        foreach($t in $r[2].traces){if($t.sequence -ge $write){$t.owner_magicule+=1};if($t.sequence -ge $write-1 -and $t.resource -eq 'owner_magicule'){$t.requested+=1}}
        $r[2].post.owner_magicule+=1
    }
    invalid_operation_order={param($r)
        $a=($r[2].traces|Where-Object boundary -eq energy_callback).sequence;$b=($r[2].traces|Where-Object boundary -eq energy_apply).sequence
        $temp=$r[2].traces[$a];$r[2].traces[$a]=$r[2].traces[$b];$r[2].traces[$b]=$temp
    }
    incorrect_cooldown_attribution={param($r) ($r[2].traces|Where-Object boundary -eq cooldown_add_before).requested_ticks=19}
    unaccounted_resource_mutation={param($r) $r[2].post.owner_aura-=1}
    false_hurt_with_callback={param($r) ($r[2].traces|Where-Object boundary -eq physical_return).result=$false}
    fake_capacity={param($r) $r[2].post.owner_max_magicule=1000000;($r[2].traces|Where-Object boundary -eq drain_enter).owner_max_magicule=1000000}
    missing_resource_write={param($r) $r[2].traces=@($r[2].traces|Where-Object {!($_.boundary -eq 'resource_after' -and $_.resource -eq 'target_aura')})}
    false_drain_result={param($r) ($r[2].traces|Where-Object boundary -eq drain_return).result=$false}
}
$mutations['trait_mutation']={param($r) $r[4].traits.'l2hostility:tank'=0}
$mutations['actor_reset_between_releases']={param($r) $r[5].pre.target_magicule+=1}
$mutations['Gazel_phase_misattribution']={param($r) $r[34].pre.native_phase=1}
$mutations['Nullification_bypassed']={param($r) ($r[35].traces|Where-Object boundary -eq physical_return).result=$true}
$results=@()
foreach($name in $mutations.Keys){
    $records=@($baseline|ConvertFrom-Json);& $mutations[$name] $records
    # Renumber after edits so rejection tests the causal invariant, not stale sequence labels.
    foreach($row in @($records|Where-Object kind -eq row)){for($i=0;$i -lt $row.traces.Count;$i++){$row.traces[$i].sequence=$i}}
    $temp=Join-Path ([IO.Path]::GetTempPath()) ('energy-extractor-'+[guid]::NewGuid()+'.jsonl')
    try {
        [IO.File]::WriteAllLines($temp,@($records|ForEach-Object {$_|ConvertTo-Json -Depth 60 -Compress}))
        $rejected=$false;$reason='';try{& $extractor -LogPath $temp|Out-Null}catch{$rejected=$true;$reason=$_.Exception.Message}
        if(!$rejected){throw "Accepted corruption: $name"};$results+=@{mutation=$name;rejected=$true;reason=$reason}
    }finally{Remove-Item -LiteralPath $temp}
}
$report=[ordered]@{schema='tno.phase6.energy_native_path.extractor_tests.v1';checkpoint='ES3A';status='PASS';negative_tests=$results.Count;results=$results}
$json=$report|ConvertTo-Json -Depth 20
if($OutputPath){if(Test-Path -LiteralPath $OutputPath){throw 'Refusing evidence overwrite'};[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")};$json
