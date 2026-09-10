param([string]$OutputPath)
$ErrorActionPreference='Stop'
$folder='docs/benchmarks/phase6-energy-steal-physical-prerequisite'
$oldPath='docs/benchmarks/phase6-endgame-viability/energy_steal.jsonl'
$rows=@([IO.File]::ReadLines([IO.Path]::GetFullPath($oldPath))|ConvertFrom-Json|Where-Object kind -eq row)
$baseline=(& "$PSScriptRoot/extract-phase6-energy-historical.ps1" -LogPath "$folder/es3b-runtime.jsonl")|ConvertFrom-Json
$ticket=(& "$PSScriptRoot/extract-phase6-energy-historical.ps1" -LogPath "$folder/es3b-ticket-runtime.jsonl")|ConvertFrom-Json
$failure=@($rows|Where-Object energy_drain_event_count -eq 0)
if($rows.Count -ne 320 -or $failure.Count -ne 269 -or @($failure|Where-Object { $_.physical_damage_event_count -ne 1 -or $_.physical_damage -ne 0 -or $_.magicule_recovery_observed -ne 0 }).Count){throw 'Historical signatures changed'}
$firstNoRegen=-1;for($i=0;$i -lt $rows.Count;$i++){if($rows[$i].magicule_recovery_observed -eq 0){$firstNoRegen=$i;break}}
if($firstNoRegen -ne 14 -or @($rows|Select-Object -Skip 14|Where-Object magicule_recovery_observed -ne 0).Count){throw 'Historical freeze signature changed'}
$cases=@($rows|Group-Object level,TNO_stage|ForEach-Object {@{case=$_.Name;rows=$_.Count;successful_hit_indices=@($_.Group|Where-Object energy_drain_event_count -eq 1|ForEach-Object hit_index);absent=@($_.Group|Where-Object energy_drain_event_count -eq 0).Count;zero_regeneration_rows=@($_.Group|Where-Object magicule_recovery_observed -eq 0).Count}})
$report=[ordered]@{
 schema='tno.phase6.energy_native_path.historical_reassessment.v1';checkpoint='ES3';status='CAUSAL_MECHANISM_PROVEN_PER_OLD_ROW_ATTRIBUTION_UNAVAILABLE';
 historical_raw_sha256=(Get-FileHash $oldPath).Hash.ToLowerInvariant();historical_rows=320;historical_operations=51;historical_absent=269;historical_incoming=320;
 historical_absent_with_zero_physical_applied_amount=269;historical_absent_with_no_observed_MP_regeneration=269;
 historical_direct_causal_attribution_count=0;historical_individually_unresolved_absences=269;
 first_no_regeneration=@{zero_based_row=14;level=300;stage='S1';hit=5};all_later_rows_without_observed_MP_regeneration=306;cases=$cases;
 new_runtime=@{baseline=$baseline;ticket_control=$ticket;directly_proven_failed_releases=5;failed_category='HISTORICAL_PHYSICAL_HURT_FALSE_INVULNERABILITY';
  earliest_fixture_divergence='World emptyTime reaches 300; subsequent world ticks skip entityTickList, while benchmark ServerTick.Post and FakePlayer cooldown tracker continue';
  exact_combat_boundary='incoming accepted; invulnerableTime 20 > 10; incoming amount 8 <= lastHurt 8; native LivingEntity.hurt returns false before actuallyHurt and arrow after_damage';
  failed_target_age=86;failed_hurt_time=10;failed_hurt_duration=10;failed_item_cooldown=0;failed_adaptive_count=5;
  actor_tick_restoration='Ticket-only counterpart has age 106 at server tick 320 and advances normally; invulnerability 0 at all releases, 20/20 success';
  other_failure_categories_observed=0;l2_trait_removal_experiments=0;production_fix_proven=$false};
 inference=@{
  established='The historical fixture has a native empty-world suspension defect. It can continue manual collisions against a non-ticking target and produce incoming observations without hurt admission or Energy operations. The installed code and one-property runtime differential establish this mechanism';
  old_269='All 269 share zero physical applied amount and no observed MP regeneration; this is consistent with the reproduced gate and explains the fixture structurally. The old log has no direct hurt return/lastHurt/target timer/callback/drain gates, so no invented per-row causal allocation is made';
  first_shots='Every old case succeeds on its first shot, consistent with the original per-case invulnerability reset even after native target ticking has stopped';
  six_late_successes='Six later-than-first successes outside the first two cases remain. Native hurt permits amount > lastHurt during invulnerability and applies only the difference. These old partial damage records are consistent with that exception; their old incoming/crit data cannot prove the exact event that raised the amount';
  cooldown='Native FakePlayer clock advances once per server tick in both old source and new runtime; all five reproduced failures have expired item cooldown and never reach Energy apply. Cooldown is not their cause';
  l2='All accepted traits stay present. Rejected shots stop before onDamaged; Adaptive arrow count stays 5. Same profile with native ticks allows 10/10 each Stage. No evidence justifies Tank/Dementor/Adaptive removal or bypass';
  production='Accepted ES3a already proves genuine Royal gameplay delivery succeeds when native prerequisites allow it. The ticket control repairs only a development fixture world-loop prerequisite. No permanent production change is justified by this discrepancy'
 };
 limitations=@('No replay of all 320 cases: two original cases cross the relevant native boundary and isolate the cause','Random native initial MP and physical critical rolls differ across runs; compare admission and independently validated native resource formulas, not balance deltas','The original fixture explicitly grants initial capacities/pools and empties attacker pools; the new observer introduces no grants and those artificial setup values are not gameplay requirements','Startup-only S7 control is preserved separately, 10/10; it ended before emptyTime 300 and cannot diagnose sustained fixture viability')
}
$json=$report|ConvertTo-Json -Depth 45
if($OutputPath){if(Test-Path $OutputPath){throw 'Refusing evidence overwrite'};[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")};$json
