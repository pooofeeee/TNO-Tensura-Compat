param([Parameter(Mandatory=$true)][string]$LogPath,[string]$OutputPath)
$ErrorActionPreference='Stop'
function Require($condition,$message){if(!$condition){throw $message}}
function Near($a,$b,$message,$tolerance=0.00001){Require ($null -ne $a -and $null -ne $b -and [double]::IsFinite([double]$a) -and [double]::IsFinite([double]$b) -and [math]::Abs([double]$a-[double]$b) -le $tolerance) "$message ($a != $b)"}
$records=@([IO.File]::ReadLines([IO.Path]::GetFullPath($LogPath))|ForEach-Object {if($_.StartsWith('{')){$_|ConvertFrom-Json}elseif($_.Contains('TNO_ENERGY_NATIVE_PATH ')){$_.Substring($_.IndexOf('{'))|ConvertFrom-Json}})
$catalog=@($records|Where-Object kind -eq catalog);$suite=@($records|Where-Object kind -eq suite_result);$rows=@($records|Where-Object kind -eq row)
Require ($catalog.Count -eq 1 -and $suite.Count -eq 1 -and $rows.Count -eq 20 -and $records.Count -eq 22) 'Incomplete or extra records'
$mode=$catalog[0].mode;$ticket=$mode -ceq 'historical_with_native_ticket'
Require ($mode -in @('historical_original','historical_with_native_ticket') -and $catalog[0].checkpoint -ceq 'ES3B' -and $catalog[0].requested_rows -eq 20) 'Wrong catalog'
Require ($suite[0].status -ceq 'complete' -and $suite[0].completed_rows -eq 20 -and $suite[0].observer_did_not_schedule_actors) 'Incomplete checkpoint'
if($ticket){Require ($suite[0].target_chunk_force_restored -and !$catalog[0].target_chunk_previously_forced) 'Ticket restoration'}
foreach($mod in @('tensura','l2hostility','apotheosis','royalvariations')){Require ($null -ne $catalog[0].mods.$mod) "Missing $mod"}
$ids=[Collections.Generic.HashSet[string]]::new();$results=@()
$resources=@('hp','shp','target_magicule','target_aura','owner_hp','owner_shp','owner_magicule','owner_aura')
$sourceBoundaries=@('physical_attempt','incoming_highest','incoming_lowest','damage_post','physical_return','after_damage_dispatch')
$effectBoundaries=@('energy_callback','energy_apply','energy_apply_return');$drainBoundaries=@('drain_enter','energy_event','drain_return')
$allowed=$sourceBoundaries+$effectBoundaries+$drainBoundaries+@('resource_before','resource_after','cooldown_add_before','cooldown_add_after','cooldown_tick_before','cooldown_tick_after','server_tick')
for($i=0;$i -lt $rows.Count;$i++){
 $r=$rows[$i];$label="ES3B $mode row $i";$traces=@($r.traces);$case=[int][math]::Floor($i/10);$shot=$i%10;$window=if($shot -eq 9){19}else{20};$target='orc_disaster'
 foreach($snap in @($r.pre,$r.post)+$traces){foreach($f in @('hp','owner_hp','target_max_hp')){$snap.$f=[double][float]$snap.$f}}
 $stage=if($case -eq 0){'S0'}else{'S7'};$coefficient=if($case -eq 0){1.05}else{1.4};$expectedPercentage=([double][float]0.01)*$coefficient
 $expectedEnergy=[int]($ticket -or $i -lt 15);$applied=$expectedEnergy;$incoming=1
 Require ($r.case -eq $case -and $r.shot -eq $shot -and $r.stage -ceq $stage -and $r.mode -ceq $mode) "$label matrix"
 Require ($r.target_id -ceq 'tensura:orc_disaster' -and $r.weapon_item -ceq 'royalvariations:royal_bow' -and $r.projectile -ceq 'royalvariations:royal_arrow') "$label identity"
 $r|Add-Member NoteProperty bow $r.weapon_item
 Require ($ids.Add($r.projectile_uuid) -and $r.delivery -ceq 'original_direct_collision_then_discard' -and $r.projectile_age_end -eq 0 -and $r.projectile_removed) "$label delivery"
 Require ($r.owner_retained -and $r.weapon_retained -and $r.can_hit -and $r.owner_creative -and !$r.target_no_ai -and !$r.native_immune -and @($r.owner_skills).Count -eq 0) "$label historical eligibility"
 Require ($r.l2_level -eq 1000 -and $r.l2_initialized) "$label native L2"
 foreach($key in @('traits','traits_after')){Require ((($r.$key.PSObject.Properties|Sort-Object Name|ForEach-Object {$_.Name.Replace('l2hostility:','')+'='+$_.Value}) -join ';') -ceq 'adaptive=5;dementor=1;dispell=2;drain=2;regenerate=5;tank=5;wither=1') "$label profile"}
 Require ($r.observation_ticks -eq $window -and $r.pre.server_tick -eq $(if($case -eq 0){13+20*$shot}else{220+20*$shot})) "$label original cadence"
 if($shot -eq 0){Require ($r.pre.cooldown -eq 0 -and $r.pre.hurt_time -eq 0 -and $r.pre.last_hurt -eq 0 -and $r.pre.target_tick -eq $(if($case -eq 0){12}else{6})) "$label original case setup"}
 if($shot -gt 0){$prior=$rows[$i-1];Require ($r.target_uuid -ceq $prior.target_uuid -and $r.owner_uuid -ceq $prior.owner_uuid) "$label actor reuse";foreach($res in $resources){Near $r.pre.$res $prior.post.$res "$label resource reset $res"};foreach($f in @('target_tick','server_tick','cooldown','hurt_time','last_hurt','item_clock','item_cooldown')){Near $r.pre.$f $prior.post.$f "$label timer reset $f"}}
 # Native world empty-time gate is independent of a chunk's entity-ticking status.
 foreach($t in @($r.pre)+$traces+@($r.post)){
  $dt=$t.server_tick-$r.pre.server_tick;$ageDelta=if($ticket){$dt}else{[math]::Min($dt,[math]::Max(0,300-$r.pre.server_tick))}
  Require ($dt -ge 0 -and $dt -le $window -and $t.target_tick -eq $r.pre.target_tick+$ageDelta -and $t.entity_ticking_chunk -and $t.world_player_count -eq 0) "$label native entity clock"
  Require ($t.world_forced_chunks -eq [int]$ticket -and $t.world_empty_time -eq $(if($ticket){0}else{$t.server_tick})) "$label native world empty gate"
 }
 $preCount=if($r.pre.adaptive.counts){[int]$r.pre.adaptive.counts.arrow}else{0};$postCount=[int]$r.post.adaptive.counts.arrow
 Require ($preCount -eq $(if(!$ticket -and $case -eq 1){[math]::Min($shot,5)}else{$shot}) -and $postCount -eq $preCount+$applied) "$label Adaptive admission count"
 Require (($r.post.adaptive.memory -join ';') -ceq 'arrow') "$label Adaptive source memory"
 $by=@{};foreach($b in $allowed){$by[$b]=@($traces|Where-Object boundary -eq $b)}
 foreach($b in @('physical_attempt','physical_return')){Require ($by[$b].Count -eq 1) "$label physical count $b"}
 foreach($b in @('incoming_highest','incoming_lowest')){Require ($by[$b].Count -eq $incoming) "$label incoming count"}
 foreach($b in @('damage_post','after_damage_dispatch')){Require ($by[$b].Count -eq $applied) "$label post count"}
 foreach($b in ($effectBoundaries+$drainBoundaries+@('cooldown_add_before','cooldown_add_after'))){Require ($by[$b].Count -eq $expectedEnergy) "$label native count $b"}
 Require ($by.physical_return[0].result -eq [bool]$applied -and $by.physical_attempt[0].projectile_age -eq 0) "$label hurt admission"
 if($incoming){Require ($by.incoming_lowest[0].result) "$label incoming admission"}
 Require ($by.incoming_lowest[0].result) "$label incoming cancellation"
 $gateAllows=$r.pre.cooldown -le 10 -or $by.incoming_lowest[0].amount -gt $r.pre.last_hurt
 Require ($gateAllows -eq [bool]$applied) "$label actual invulnerability admission rule"
 Require ($r.pre.item_cooldown -eq 0) "$label item cooldown cannot explain absence"
 foreach($t in $traces){
  $ageDelta=$t.target_tick-$r.pre.target_tick
  $entered=$applied -and $t.sequence -gt $by.incoming_lowest[0].sequence
  $returned=$applied -and $t.sequence -ge $by.physical_return[0].sequence
  $timer=if($entered){[math]::Max(0,20-$ageDelta)}else{[math]::Max(0,$r.pre.cooldown-$ageDelta)}
  $hurtTime=if($returned){[math]::Max(0,10-$ageDelta)}else{[math]::Max(0,$r.pre.hurt_time-$ageDelta)}
  Require ($t.cooldown -eq $timer -and $t.hurt_time -eq $hurtTime -and $t.hurt_duration -eq $(if($returned){10}else{$r.pre.hurt_duration})) "$label native hurt timer lifecycle at $($t.sequence)"
  Near $t.last_hurt $(if($entered){$by.incoming_lowest[0].amount}else{$r.pre.last_hurt}) "$label native lastHurt"
  Require ($t.server_tick -eq $r.pre.server_tick+$t.relative_tick) "$label absolute/relative clock"
 }
 foreach($f in @('cooldown','hurt_time','hurt_duration','last_hurt','world_empty_time','target_tick')){Near $r.post.$f $traces[-1].$f "$label final timer $f"}
 Require ($by.server_tick.Count -eq $window -and (($by.server_tick.relative_tick -join ',') -ceq ((1..$window) -join ','))) "$label missing server cadence"
 $ordered=@($sourceBoundaries|Where-Object {$by[$_].Count})+$(if($expectedEnergy){@('energy_callback','energy_apply','cooldown_add_before','cooldown_add_after','drain_enter','energy_event','drain_return','energy_apply_return')}else{@()})
 $prev=-1;foreach($b in $ordered){Require ($by[$b][0].sequence -gt $prev) "$label invalid operation order $b";$prev=$by[$b][0].sequence}
 foreach($b in $sourceBoundaries){foreach($t in $by[$b]){Require ($t.source -ceq 'minecraft:arrow' -and $t.message -ceq 'arrow' -and $t.direct_uuid -ceq $r.projectile_uuid -and $t.direct -ceq $r.projectile -and $t.owner_retained -and $t.source_object -eq $by.physical_attempt[0].source_object -and $t.resistance_bypass -eq 0) "$label source $b";Require (($t.tags -join ';') -ceq 'minecraft:always_kills_armor_stands;minecraft:is_projectile;minecraft:panic_causes;neoforge:is_physical;tensura:is_physical') "$label source tags"}}
 foreach($b in $effectBoundaries){foreach($t in $by[$b]){Near $t.native_percentage ([double][float]0.01) "$label native percentage" 0.000000000001;Require ($t.enchantment_level -eq 1 -and $t.configured_cooldown -eq 20 -and $t.effect_owner_retained -and $t.effect_item -ceq $r.bow -and $t.effect_weapon_same_components -and $t.effect_stage -ceq $stage) "$label effect identity"}}
 foreach($b in $drainBoundaries){foreach($t in $by[$b]){Near $t.amount $expectedPercentage "$label Stage once percentage" 0.000000000001;Require ($t.percentage -and $t.drain_type -ceq 'EP' -and $t.gain_type -ceq 'NORMAL' -and $t.item_cooldown -eq 20) "$label native arguments"}}
    $state=@{};foreach($res in $resources){$state[$res]=[double]$r.pre.$res}
    $clock=$r.pre.item_clock;$cooldown=$r.pre.item_cooldown;$pending=$null;$clockPending=$null;$addPending=$null
    $drainOpen=$false;$drainWrites=@();$hpLoss=0.0;$healHP=0.0;$nativeMPcost=0.0;$regenMP=0.0;$regenAP=0.0
    for($j=0;$j -lt $traces.Count;$j++) {
        $t=$traces[$j];Require ($t.sequence -eq $j -and $t.boundary -in $allowed) "$label sequence/unknown boundary"
        Require ($t.projectile_uuid -ceq $r.projectile_uuid -and $t.target_uuid -ceq $r.target_uuid -and $t.owner_uuid -ceq $r.owner_uuid) "$label trace identity"
        Require ($t.relative_tick -ge 0 -and $t.relative_tick -le $window) "$label trace timing"
        foreach($cap in @('owner_max_magicule','owner_max_aura','target_max_magicule','target_max_aura','owner_magicule_attribute','owner_aura_attribute','owner_magicule_limit','owner_aura_limit')){Near $t.$cap $r.pre.$cap "$label capacity mutation $cap"}
        if($t.boundary -eq 'resource_after') {
            Require ($null -ne $pending -and $pending.sequence -eq $j-1 -and $pending.resource -ceq $t.resource -and $pending.requested -eq $t.requested) "$label unpaired resource write"
            $res=$t.resource;Require ($res -in $resources) "$label unknown resource"
            $value=[double]$t.requested
            if($res -in @('target_magicule','target_aura','owner_magicule','owner_aura')){$value=[math]::Min([double]2147483647,$value)}
            elseif($res -eq 'hp'){$value=[math]::Clamp($value,[double]0,[double]$t.target_max_hp)}
            $delta=$value-$state[$res]; Near $t.$res $value "$label setter result $res"
            if($drainOpen){Require ($t.native_callers -contains 'io.github.manasmods.tensura.util.EnergyHelper.drainEnergy') "$label non-native transfer";$drainWrites+=@{resource=$res;delta=$delta}}
            elseif([math]::Abs($delta) -gt 0.000001){
                if($res -eq 'hp' -and $delta -lt 0){Require ($t.native_callers -contains 'net.minecraft.world.entity.LivingEntity.actuallyHurt') "$label unknown HP loss";$hpLoss-=$delta}
                elseif($res -eq 'target_magicule' -and $delta -gt 0){Require ($t.native_callers -contains 'io.github.manasmods.tensura.storage.ep.ExistenceStorage.handleMagiculeRegen') "$label unknown MP gain";$regenMP+=$delta}
                elseif($res -eq 'target_aura' -and $delta -gt 0){Require ($t.native_callers -contains 'io.github.manasmods.tensura.storage.ep.ExistenceStorage.handleAuraRegen') "$label unknown AP gain";$regenAP+=$delta}
                elseif($res -eq 'hp' -and $delta -gt 0 -and ($t.native_callers -contains 'dev.xkmc.l2hostility.content.traits.common.RegenTrait.tick' -or $t.native_callers -contains 'io.github.manasmods.tensura.effect.ability.SelfRegenerationEffect.applyEffectTick' -or ($case -in @(0,1) -and $t.native_callers -contains 'io.github.manasmods.tensura.entity.monster.OrcDisasterEntity.healAndEat'))){$healHP+=$delta}
                else {throw "$label unexpected resource mutation $res delta $delta"}
            }
            $state[$res]=$value;$pending=$null
        } elseif($t.boundary -eq 'resource_before') {Require ($null -eq $pending) "$label nested unexplained resource write";$pending=$t}
        foreach($res in $resources){Near $t.$res $state[$res] "$label unaccounted resource mutation $res at $j"}
        switch($t.boundary){
            'cooldown_tick_before' {Require ($null -eq $clockPending) "$label duplicate clock";$clockPending=$t}
            'cooldown_tick_after' {Require ($null -ne $clockPending -and $clockPending.sequence -eq $j-1) "$label clock pair";$clock++;$cooldown=[math]::Max(0,$cooldown-1);$clockPending=$null}
            'cooldown_add_before' {Require ($cooldown -eq 0 -and $t.requested_ticks -eq 20 -and $t.item -ceq $r.bow) "$label cooldown admission";$addPending=$t}
            'cooldown_add_after' {Require ($null -ne $addPending -and $addPending.sequence -eq $j-1 -and $t.requested_ticks -eq 20 -and $t.item -ceq $r.bow) "$label cooldown pair";$cooldown=20;$addPending=$null}
            'drain_enter' {Require (!$drainOpen) "$label recursion";$drainOpen=$true}
            'drain_return' {Require ($drainOpen -and $t.result) "$label unsuccessful positive control";$drainOpen=$false}
        }
        Require ($t.item_clock -eq $clock -and $t.item_cooldown -eq $cooldown) "$label incorrect cooldown attribution at $j"
    }
    Require ($null -eq $pending -and $null -eq $clockPending -and $null -eq $addPending -and !$drainOpen) "$label unfinished operation"
    Require ($by.cooldown_tick_before.Count -eq $window -and $by.cooldown_tick_after.Count -eq $window -and $r.post.item_clock -eq $clock -and $r.post.item_cooldown -eq $cooldown) "$label final cooldown"
    foreach($res in $resources){Near $r.post.$res $state[$res] "$label final unaccounted $res"}
    foreach($cap in @('owner_max_magicule','owner_max_aura','target_max_magicule','target_max_aura','owner_magicule_attribute','owner_aura_attribute','owner_magicule_limit','owner_aura_limit')){Near $r.post.$cap $r.pre.$cap "$label final capacity mutation $cap"}
    if($applied){Near $hpLoss $by.damage_post[0].amount "$label HP float damage ledger" 0.001}
    $lossMP=0.0;$lossAP=0.0;$gainMP=0.0;$gainAP=0.0
    if($expectedEnergy){
        Require (($drainWrites.resource -join ';') -ceq 'owner_aura;target_aura;owner_magicule;target_magicule') "$label native transfer order/count"
        $before=$by.drain_enter[0];$after=$by.drain_return[0];$p=$expectedPercentage
        $lossMP=[math]::Min($before.target_magicule,$before.target_magicule*$p);$lossAP=[math]::Min($before.target_aura,$before.target_aura*$p)
        foreach($pool in @('magicule','aura')){
            $targetPool='target_'+$pool;$owner='owner_'+$pool;$cap='owner_max_'+$pool;$loss=if($pool -eq 'magicule'){$lossMP}else{$lossAP}
            $newOwner=if($before.$owner -gt $before.$cap){$before.$owner+$loss}else{[math]::Min($before.$cap,$before.$owner+$loss)};$newOwner=[math]::Min([double]2147483647,$newOwner)
            Near ($before.$targetPool-$after.$targetPool) $loss "$label wrong target resource loss $pool"
            Near $after.$owner $newOwner "$label wrong attacker resource gain $pool"
        }
        $gainMP=$after.owner_magicule-$before.owner_magicule;$gainAP=$after.owner_aura-$before.owner_aura
        Near $r.post.target_magicule ($r.pre.target_magicule-$lossMP+$regenMP) "$label MP reconciliation"
        Near $r.post.target_aura ($r.pre.target_aura-$lossAP+$regenAP) "$label AP reconciliation"
    }
    $results+=@{case=$case;shot=$shot;mode=$r.mode;target=$target;physical_attempts=1;physical_incoming=$incoming;physical_applied=$applied;hurt_true=$applied;callbacks=$expectedEnergy;apply_calls=$expectedEnergy;drains=$expectedEnergy;successful_drains=$expectedEnergy;category=$(if($expectedEnergy){"I_NATIVE_DRAIN_SUCCEEDED"}else{"HISTORICAL_PHYSICAL_HURT_FALSE_INVULNERABILITY"});
        requested_percentage=$(if($expectedEnergy){$expectedPercentage}else{0});target_magicule_loss=$lossMP;target_aura_loss=$lossAP;attacker_magicule_gain=$gainMP;attacker_aura_gain=$gainAP;
        magicule_recovery=$regenMP;aura_recovery=$regenAP;native_magicule_cost=$nativeMPcost;hp_loss=$hpLoss;hp_heal=$healHP;shp_delta=$r.post.shp-$r.pre.shp;cooldown_ticks_recorded=$window;target_tick_delta=$r.post.target_tick-$r.pre.target_tick;pre_invulnerability=$r.pre.cooldown;pre_last_hurt=$r.pre.last_hurt;incoming_amount=$by.incoming_lowest[0].amount;server_tick=$r.pre.server_tick;world_empty_time=$r.pre.world_empty_time;adaptive_pre=$r.pre.adaptive;adaptive_post=$r.post.adaptive;resource_writes=$by.resource_after.Count}
}
$report=[ordered]@{schema='tno.phase6.energy_native_path.validation.v1';checkpoint='ES3B';mode=$mode;status='PASS';rows=$rows.Count;raw_sha256=(Get-FileHash -LiteralPath $LogPath).Hash.ToLowerInvariant();results=$results;
    errors=0;duplicate_drains=0;recursions=0;unexpected_bypasses=0;unaccounted_resource_changes=0;production_changed=$false;limitations='Bounded original-fixture differential; old 269 rows lack direct return/timer data and cannot individually inherit these causes'}
$json=$report|ConvertTo-Json -Depth 20
if($OutputPath){Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing evidence overwrite';[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")}
$json
