param([Parameter(Mandatory=$true)][string]$LogPath,[ValidateSet('ES3A')][string]$Checkpoint='ES3A',[string]$OutputPath)
$ErrorActionPreference='Stop'
function Require($condition,$message) { if(!$condition){throw $message} }
function Near($a,$b,$message,$tolerance=0.00001) {
    Require ($null -ne $a -and $null -ne $b -and [double]::IsFinite([double]$a) -and [double]::IsFinite([double]$b) -and [math]::Abs([double]$a-[double]$b) -le $tolerance) "$message ($a != $b)"
}
$records=@(Get-Content -LiteralPath $LogPath | ForEach-Object {
    if($_.StartsWith('{')){$_|ConvertFrom-Json}elseif($_.Contains('TNO_ENERGY_NATIVE_PATH ')){$_.Substring($_.IndexOf('{'))|ConvertFrom-Json}
})
Require (@($records|Where-Object kind -eq error).Count -eq 0) 'Runtime error'
$catalog=@($records|Where-Object kind -eq catalog);$suite=@($records|Where-Object kind -eq suite_result);$rows=@($records|Where-Object kind -eq row)
Require ($catalog.Count -eq 1 -and $suite.Count -eq 1 -and $rows.Count -eq 35 -and $records.Count -eq 37) 'Incomplete or extra records'
Require ($suite[0].status -eq 'complete' -and $suite[0].completed_cases -eq 8 -and $suite[0].completed_rows -eq 35 -and $suite[0].force_load_restored -and $catalog[0].checkpoint -eq 'ES3') 'Incomplete checkpoint'
foreach($mod in @('tensura','l2hostility','apotheosis','royalvariations')){Require ($null -ne $catalog[0].mods.$mod) "Missing $mod"}
$ids=[Collections.Generic.HashSet[string]]::new();$results=@()
$resources=@('hp','shp','target_magicule','target_aura','owner_hp','owner_shp','owner_magicule','owner_aura')
$sourceBoundaries=@('physical_attempt','incoming_highest','incoming_lowest','damage_post','physical_return','after_damage_dispatch')
$effectBoundaries=@('energy_callback','energy_apply','energy_apply_return')
$drainBoundaries=@('drain_enter','energy_event','drain_return')
$allowed=$sourceBoundaries+$effectBoundaries+$drainBoundaries+@('resource_before','resource_after','cooldown_add_before','cooldown_add_after','cooldown_tick_before','cooldown_tick_after')
$profiles=@{
 orc_disaster='adaptive=5;dementor=1;dispell=2;drain=2;regenerate=5;tank=5;wither=1'
 gazel_dwargo='adaptive=5;dementor=1;dispell=2;reflect=1;regenerate=5;tank=5'
 luminous_valentine='adaptive=5;dementor=1;dispell=3;killer_aura=1;reflect=2;regenerate=5;soul_burner=2;tank=5'
}
for($i=0;$i -lt $rows.Count;$i++) {
 $r=$rows[$i];$label="ES3A row $i";$traces=@($r.traces)
 # Gson serializes float HP with its shortest round-trip spelling; setter requested values are widened doubles.
 foreach($snap in @($r.pre,$r.post)+$traces){foreach($field in @('hp','owner_hp','target_max_hp')){$snap.$field=[double][float]$snap.$field}}
 $case=if($i -lt 3){$i}elseif($i -lt 33){3+[int][math]::Floor(($i-3)/10)}else{$i-27}
 $shot=if($i -ge 3 -and $i -lt 33){($i-3)%10}else{0}
 $target=if($case -lt 3){'neutral'}elseif($case -lt 6){'orc_disaster'}elseif($case -eq 6){'gazel_dwargo'}else{'luminous_valentine'}
 $mode=if($case -lt 6){@('royal_plain_s0','royal_native_s0','royal_native_s7')[$case%3]}else{'royal_native_s7'}
 $stage=if($mode.EndsWith('s7')){'S7'}else{'S0'};$coefficient=if($stage -eq 'S7'){1.4}else{1.05}
 $expectedEnergy=[int](!$mode.Contains('plain') -and $case -lt 6);$applied=[int]($case -lt 6);$incoming=[int]($case -ne 6)
 $expectedPercentage=([double][float]0.01)*$coefficient
 Require ($r.case -eq $case -and $r.shot -eq $shot -and $r.mode -ceq $mode -and $r.target -ceq $target -and $r.stage -ceq $stage -and $r.enchanted -eq !$mode.Contains('plain')) "$label matrix"
 $targetId=if($target -eq 'neutral'){'minecraft:iron_golem'}elseif($target -eq 'luminous_valentine'){'tensura_neb:luminous_valentine'}else{'tensura:'+$target}
 Require ($r.target_id -ceq $targetId -and $r.bow -ceq 'royalvariations:royal_bow' -and $r.weapon_item -ceq $r.bow -and $r.projectile -ceq 'royalvariations:royal_arrow') "$label identity"
 Require ($r.delivery -ceq 'native_final_lane_ticks' -and $r.spawn_count -eq 1 -and $ids.Add($r.projectile_uuid)) "$label delivery"
 Require ($r.can_hit -and $r.owner_retained -and $r.weapon_retained -and $r.legal_enchantment -and !$r.owner_creative -and @($r.owner_skills).Count -eq 0 -and $r.weapon_energy_level -eq [int]$r.enchanted) "$label eligibility"
 Require (!$r.native_immune -and $r.physical_resistance -eq ($case -eq 6) -and $r.physical_nullification -eq ($case -eq 7) -and $r.energy_protection -eq 0 -and !$r.target_no_ai) "$label native defense"
 Require ($r.target_tick_at_release -gt 0 -and $r.pre.target_tick -eq $r.target_tick_at_release -and $r.post.target_tick-$r.pre.target_tick -eq 20 -and $r.observation_ticks -eq 20) "$label native ticking"
 if($target -eq 'neutral'){Require (!$r.l2_initialized) "$label neutral L2"}else{
  Require ($r.l2_initialized -and $r.l2_level -eq 1000) "$label L2 level"
  foreach($key in @('traits','traits_after')){$actual=($r.$key.PSObject.Properties|Sort-Object Name|ForEach-Object {$_.Name.Replace('l2hostility:','')+'='+$_.Value}) -join ';';Require ($actual -ceq $profiles[$target]) "$label L2 profile"}
 }
 if($shot -gt 0){$prior=$rows[$i-1];Require ($r.target_uuid -ceq $prior.target_uuid -and $r.owner_uuid -ceq $prior.owner_uuid) "$label repeated actors";foreach($res in $resources){Near $r.pre.$res $prior.post.$res "$label reset between shots $res"};Require ($r.pre.item_clock -eq $prior.post.item_clock -and $r.pre.item_cooldown -eq $prior.post.item_cooldown) "$label cooldown reset between shots"}
 $by=@{};foreach($b in $allowed){$by[$b]=@($traces|Where-Object boundary -eq $b)}
 foreach($b in @('physical_attempt','physical_return')){Require ($by[$b].Count -eq 1) "$label physical count $b"}
 foreach($b in @('incoming_highest','incoming_lowest')){Require ($by[$b].Count -eq $incoming) "$label incoming count"}
 foreach($b in @('damage_post','after_damage_dispatch')){Require ($by[$b].Count -eq $applied) "$label post count"}
 foreach($b in ($effectBoundaries+$drainBoundaries+@('cooldown_add_before','cooldown_add_after'))){Require ($by[$b].Count -eq $expectedEnergy) "$label native count $b"}
 Require ($by.physical_return[0].result -eq [bool]$applied -and $by.physical_attempt[0].projectile_age -gt 0) "$label hurt admission"
 if($incoming){Require ($by.incoming_lowest[0].result -eq [bool]$applied) "$label incoming admission"}
 if($case -eq 6){Require ($r.pre.native_phase -eq 0 -and $by.physical_return[0].native_phase -eq 1 -and $by.physical_return[0].cooldown -eq 80) "$label Gazel native phase gate"}
 if($case -eq 7){Require (($r.target_skills -join ';').Contains('Toggled:1b,skill:"tensura:physical_attack_nullification"')) "$label missing native Nullification"}
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
        Require ($t.relative_tick -ge 0 -and $t.relative_tick -le 20) "$label trace timing"
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
                elseif($res -eq 'hp' -and $delta -gt 0 -and ($t.native_callers -contains 'dev.xkmc.l2hostility.content.traits.common.RegenTrait.tick' -or ($case -in @(3,4,5) -and $t.native_callers -contains 'io.github.manasmods.tensura.entity.monster.OrcDisasterEntity.healAndEat'))){$healHP+=$delta}
                elseif($res -eq 'target_magicule' -and $case -eq 7 -and $delta -eq -25 -and $t.native_callers -contains 'io.github.manasmods.tensura.ability.skill.extra.UniversalPerceptionSkill.onTick'){$nativeMPcost-=$delta}
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
    Require ($by.cooldown_tick_before.Count -eq 20 -and $by.cooldown_tick_after.Count -eq 20 -and $r.post.item_clock -eq $clock -and $r.post.item_cooldown -eq $cooldown) "$label final cooldown"
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
    $results+=@{case=$case;shot=$shot;mode=$r.mode;target=$target;physical_attempts=1;physical_incoming=$incoming;physical_applied=$applied;hurt_true=$applied;callbacks=$expectedEnergy;apply_calls=$expectedEnergy;drains=$expectedEnergy;successful_drains=$expectedEnergy;category=$(if($expectedEnergy){"I_NATIVE_DRAIN_SUCCEEDED"}elseif($case -eq 6){"D_NATIVE_GAZEL_PHASE_HURT_FALSE"}elseif($case -eq 7){"B_NATIVE_PHYSICAL_NULLIFICATION"}else{"PLAIN_PHYSICAL_CONTROL"});
        requested_percentage=$(if($expectedEnergy){$expectedPercentage}else{0});target_magicule_loss=$lossMP;target_aura_loss=$lossAP;attacker_magicule_gain=$gainMP;attacker_aura_gain=$gainAP;
        magicule_recovery=$regenMP;aura_recovery=$regenAP;native_magicule_cost=$nativeMPcost;hp_loss=$hpLoss;hp_heal=$healHP;shp_delta=$r.post.shp-$r.pre.shp;cooldown_ticks_recorded=20;resource_writes=$by.resource_after.Count}
}
$report=[ordered]@{schema='tno.phase6.energy_native_path.validation.v1';checkpoint=$Checkpoint;status='PASS';rows=$rows.Count;raw_sha256=(Get-FileHash -LiteralPath $LogPath).Hash.ToLowerInvariant();results=$results;
    errors=0;duplicate_drains=0;recursions=0;unexpected_bypasses=0;unaccounted_resource_changes=0;production_changed=$false;limitations='ES3A native Royal matrix; historical 269 failures causal reproduction and final decision pending'}
$json=$report|ConvertTo-Json -Depth 20
if($OutputPath){Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing evidence overwrite';[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")}
$json
