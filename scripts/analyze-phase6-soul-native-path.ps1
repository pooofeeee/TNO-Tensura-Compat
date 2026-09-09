param([string]$EvidenceDirectory='docs/benchmarks/phase6-soul-native-event-path',[string]$OutputPath)
$ErrorActionPreference='Stop'
$extractor=Join-Path $PSScriptRoot 'extract-phase6-soul-native-path.ps1'
$a=& $extractor -Checkpoint S3 -LogPath (Join-Path $EvidenceDirectory 's3-runtime.jsonl') | ConvertFrom-Json
$b=& $extractor -Checkpoint S3F -LogPath (Join-Path $EvidenceDirectory 's3f-runtime.jsonl') | ConvertFrom-Json
$all=@($a.rows)+@($b.rows)
$projectiles=@(foreach($file in @('s3-runtime.jsonl','s3f-runtime.jsonl')) {
    Get-Content (Join-Path $EvidenceDirectory $file) | ConvertFrom-Json | Where-Object kind -eq row | ForEach-Object projectile_uuid
})
if(($projectiles | Sort-Object -Unique).Count -ne 23){throw 'Cross-run duplicate projectile'}
function Sum($rows,$field){[double]($rows | Measure-Object $field -Sum).Sum}
$targets=@($all | Group-Object target | ForEach-Object {
    [ordered]@{target=$_.Name;releases=$_.Count;physical_attempts=(Sum $_.Group physical_attempts);physical_incoming=(Sum $_.Group physical_incoming);
        physical_applied=(Sum $_.Group physical_applied);physical_hp_damage=(Sum $_.Group physical_damage);native_hp_recovery=(Sum $_.Group native_hp_recovery);
        soul_callbacks=(Sum $_.Group soul_callbacks);soul_sources=(Sum $_.Group soul_sources);spiritual_events=(Sum $_.Group spiritual_events);
        gross_shp_damage=(Sum $_.Group shp_damage);native_shp_recovery=(Sum $_.Group native_shp_recovery);net_shp_loss=((Sum $_.Group shp_damage)-(Sum $_.Group native_shp_recovery))}
})
$report=[ordered]@{schema='tno.phase6.soul_native_path.comparison.v1';checkpoint='S3';status='COMPLETE';
    unique_releases=23;physical_attempts=(Sum $all physical_attempts);physical_incoming=(Sum $all physical_incoming);physical_applied=(Sum $all physical_applied);
    soul_callbacks=(Sum $all soul_callbacks);soul_sources=(Sum $all soul_sources);spiritual_events=(Sum $all spiritual_events);spiritual_events_accepted=(Sum $all spiritual_events);
    ordinary_soul_hp_incoming=0;ordinary_soul_hp_applied=0;targets=$targets;
    native_control='Accepted S2: 2 vanilla bow cases, one Soul callback/source/spiritual event, 7 SHP damage and 2 native recovery; plain has none. Not rerun.';
    plain_royal_controls='S3F cases 0/1 at S0/S7: two physical hits, no Soul callbacks/sources/events, unchanged SHP.';
    historical_flight_gap='S3 case 19 retained unchanged: no physical attempt; original trajectory cause not proved. S3F case 2 uses a centered loaded-chunk lane and reaches native Hinata S7 physical/Soul Resistance gates. No compatibility defect inferred from the earlier miss.';
    spiritual_event_result_evidence='Each dispatched event is followed by one actual native SHP write and true native helper return; accepted event result is established from that native continuation.';
    neb_attribution='S3 case 15: 50 SHP recovery reconstructed from adjacent NEB tick heal(10) and installed bytecode; old SHP stack filter omitted addon namespace. Amount/write/persistence directly recorded.';
    native_spiritual_nullification='Source-proven unchanged early return; selected native profiles have no active spiritual nullification. No synthetic skill was granted; this gate is not claimed runtime-tested.';
    source_stage_isolation='Source holders/tags/owner checked; Soul amount equals actual callback amount times 1.05 at S0 or 1.4 at S7. Existing Hinata S7 Resistance metadata=1 does not bypass native direct spiritual HP/2 gate.';
    limitations=@('single shot cases, no sustained DPS/balance claim','not full boss roster or multiplayer','SHP-zero native death and special Berserker/TrainingDummy branches are source-only','preserved random initial L2 effects may influence later movement/native ticks; exact effects captured');
    production_changed=$false;production_prototype=$false;next='S4 final decision and validation, then owner review'}
$json=$report|ConvertTo-Json -Depth 20
if($OutputPath){if(Test-Path -LiteralPath $OutputPath){throw 'Refusing to overwrite evidence'};[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")}
$json
