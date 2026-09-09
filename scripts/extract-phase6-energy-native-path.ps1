param([Parameter(Mandatory=$true)][string]$LogPath,[ValidateSet('ES2')][string]$Checkpoint='ES2',[string]$OutputPath)
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
Require ($catalog.Count -eq 1 -and $suite.Count -eq 1 -and $rows.Count -eq 2 -and $records.Count -eq 4) 'Incomplete or extra records'
Require ($suite[0].status -eq 'complete' -and $suite[0].completed_cases -eq 2 -and $suite[0].force_load_restored -and $catalog[0].checkpoint -eq $Checkpoint) 'Incomplete checkpoint'
foreach($mod in @('tensura','l2hostility','apotheosis','royalvariations')){Require ($null -ne $catalog[0].mods.$mod) "Missing $mod"}
$ids=[Collections.Generic.HashSet[string]]::new();$results=@()
$resources=@('hp','shp','target_magicule','target_aura','owner_hp','owner_shp','owner_magicule','owner_aura')
$sourceBoundaries=@('physical_attempt','incoming_highest','incoming_lowest','damage_post','physical_return','after_damage_dispatch')
$effectBoundaries=@('energy_callback','energy_apply','energy_apply_return')
$drainBoundaries=@('drain_enter','energy_event','drain_return')
$allowed=$sourceBoundaries+$effectBoundaries+$drainBoundaries+@('resource_before','resource_after','cooldown_add_before','cooldown_add_after','cooldown_tick_before','cooldown_tick_after')
for($i=0;$i -lt $rows.Count;$i++) {
    $r=$rows[$i];$label="ES2 row $i";$traces=@($r.traces);$expectedEnergy=$i
    Require ($r.case -eq $i -and $r.mode -ceq @('vanilla_plain','vanilla_energy')[$i] -and $r.enchanted -eq [bool]$i) "$label matrix"
    Require ($r.target_id -ceq 'minecraft:iron_golem' -and $r.bow -ceq 'minecraft:bow' -and $r.weapon_item -ceq $r.bow -and $r.projectile -ceq 'minecraft:arrow') "$label identity"
    Require ($r.stage -ceq 'NONE' -and $r.delivery -ceq 'native_free_ticks' -and $r.spawn_count -eq 1 -and $ids.Add($r.projectile_uuid)) "$label delivery"
    Require ($r.can_hit -and $r.owner_retained -and $r.weapon_retained -and $r.legal_enchantment -and !$r.owner_creative -and @($r.owner_skills).Count -eq 0 -and $r.weapon_energy_level -eq $i) "$label eligibility"
    Require (!$r.native_immune -and !$r.physical_resistance -and !$r.physical_nullification -and $r.energy_protection -eq 0 -and !$r.target_no_ai -and !$r.l2_initialized) "$label unexpected defense"
    Require ($r.target_tick_at_release -gt 0 -and $r.pre.target_tick -eq $r.target_tick_at_release -and $r.post.target_tick -gt $r.pre.target_tick -and $r.observation_ticks -eq 25) "$label native ticking"
    $by=@{};foreach($b in $allowed){$by[$b]=@($traces|Where-Object boundary -eq $b)}
    foreach($b in $sourceBoundaries){Require ($by[$b].Count -eq 1) "$label physical/dispatch count $b"}
    foreach($b in ($effectBoundaries+$drainBoundaries+@('cooldown_add_before','cooldown_add_after'))){Require ($by[$b].Count -eq $expectedEnergy) "$label native count $b"}
    Require ($by.physical_return[0].result -and $by.incoming_lowest[0].result -and $by.damage_post[0].amount -gt 0 -and $by.physical_attempt[0].projectile_age -gt 0) "$label physical admission"
    $ordered=$sourceBoundaries+$(if($i){@('energy_callback','energy_apply','cooldown_add_before','cooldown_add_after','drain_enter','energy_event','drain_return','energy_apply_return')}else{@()})
    $prev=-1;foreach($b in $ordered){Require ($by[$b][0].sequence -gt $prev) "$label invalid operation order $b";$prev=$by[$b][0].sequence}
    foreach($b in $sourceBoundaries){$t=$by[$b][0];Require ($t.source -ceq 'minecraft:arrow' -and $t.direct_uuid -ceq $r.projectile_uuid -and $t.direct -ceq $r.projectile -and $t.owner_retained -and $t.source_object -eq $by.physical_attempt[0].source_object -and $t.resistance_bypass -eq 0) "$label physical source $b";Require (($t.tags -join ';') -ceq 'minecraft:always_kills_armor_stands;minecraft:is_projectile;minecraft:panic_causes;neoforge:is_physical;tensura:is_physical') "$label source tags"}
    foreach($b in $effectBoundaries){foreach($t in $by[$b]){
        Near $t.native_percentage ([double][float]0.01) "$label native percentage" 0.000000000001
        Require ($t.enchantment_level -eq 1 -and $t.configured_cooldown -eq 20 -and $t.effect_owner_retained -and $t.effect_item -ceq $r.bow -and $t.effect_weapon_same_components -and $t.effect_stage -ceq 'NONE') "$label effect identity"
    }}
    foreach($b in $drainBoundaries){foreach($t in $by[$b]){Near $t.amount ([double][float]0.01) "$label unclassified native percentage" 0.000000000001;Require ($t.percentage -and $t.drain_type -ceq 'EP' -and $t.gain_type -ceq 'NORMAL' -and $t.item_cooldown -eq 20) "$label native drain arguments/cooldown"}}
    $state=@{};foreach($res in $resources){$state[$res]=[double]$r.pre.$res}
    $clock=$r.pre.item_clock;$cooldown=$r.pre.item_cooldown;$pending=$null;$clockPending=$null;$addPending=$null
    $drainOpen=$false;$drainWrites=@();$hpLoss=0.0;$regenMP=0.0;$regenAP=0.0
    for($j=0;$j -lt $traces.Count;$j++) {
        $t=$traces[$j];Require ($t.sequence -eq $j -and $t.boundary -in $allowed) "$label sequence/unknown boundary"
        Require ($t.projectile_uuid -ceq $r.projectile_uuid -and $t.target_uuid -ceq $r.target_uuid -and $t.owner_uuid -ceq $r.owner_uuid) "$label trace identity"
        Require ($t.relative_tick -ge 0 -and $t.relative_tick -le 25) "$label trace timing"
        foreach($cap in @('owner_max_magicule','owner_max_aura','target_max_magicule','target_max_aura','owner_magicule_attribute','owner_aura_attribute','owner_magicule_limit','owner_aura_limit')){Near $t.$cap $r.pre.$cap "$label capacity mutation $cap"}
        if($t.boundary -eq 'resource_after') {
            Require ($null -ne $pending -and $pending.sequence -eq $j-1 -and $pending.resource -ceq $t.resource -and $pending.requested -eq $t.requested) "$label unpaired resource write"
            $res=$t.resource;Require ($res -in $resources) "$label unknown resource"
            $value=[double]$t.requested
            if($res -in @('target_magicule','target_aura','owner_magicule','owner_aura')){$value=[math]::Min([double]2147483647,$value)}
            elseif($res -eq 'hp'){$value=[double][float][math]::Clamp($value,0,[double]$t.target_max_hp)}
            $delta=$value-$state[$res]; Near $t.$res $value "$label setter result $res"
            if($drainOpen){Require ($t.native_callers -contains 'io.github.manasmods.tensura.util.EnergyHelper.drainEnergy') "$label non-native transfer";$drainWrites+=@{resource=$res;delta=$delta}}
            elseif([math]::Abs($delta) -gt 0.000001){
                if($res -eq 'hp' -and $delta -lt 0){Require ($t.native_callers -contains 'net.minecraft.world.entity.LivingEntity.actuallyHurt') "$label unknown HP loss";$hpLoss-=$delta}
                elseif($res -eq 'target_magicule' -and $delta -gt 0){Require ($t.native_callers -contains 'io.github.manasmods.tensura.storage.ep.ExistenceStorage.handleMagiculeRegen') "$label unknown MP gain";$regenMP+=$delta}
                elseif($res -eq 'target_aura' -and $delta -gt 0){Require ($t.native_callers -contains 'io.github.manasmods.tensura.storage.ep.ExistenceStorage.handleAuraRegen') "$label unknown AP gain";$regenAP+=$delta}
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
    Require ($by.cooldown_tick_before.Count -eq 25 -and $by.cooldown_tick_after.Count -eq 25 -and $r.post.item_clock -eq $clock -and $r.post.item_cooldown -eq $cooldown) "$label final cooldown"
    foreach($res in $resources){Near $r.post.$res $state[$res] "$label final unaccounted $res"}
    foreach($cap in @('owner_max_magicule','owner_max_aura','target_max_magicule','target_max_aura','owner_magicule_attribute','owner_aura_attribute','owner_magicule_limit','owner_aura_limit')){Near $r.post.$cap $r.pre.$cap "$label final capacity mutation $cap"}
    Near $hpLoss $by.damage_post[0].amount "$label HP damage ledger"
    $lossMP=0.0;$lossAP=0.0;$gainMP=0.0;$gainAP=0.0
    if($i){
        Require (($drainWrites.resource -join ';') -ceq 'owner_aura;target_aura;owner_magicule;target_magicule') "$label native transfer order/count"
        $before=$by.drain_enter[0];$after=$by.drain_return[0];$p=[double][float]0.01
        $lossMP=[math]::Min($before.target_magicule,$before.target_magicule*$p);$lossAP=[math]::Min($before.target_aura,$before.target_aura*$p)
        foreach($pool in @('magicule','aura')){
            $target='target_'+$pool;$owner='owner_'+$pool;$cap='owner_max_'+$pool;$loss=if($pool -eq 'magicule'){$lossMP}else{$lossAP}
            $newOwner=if($before.$owner -gt $before.$cap){$before.$owner+$loss}else{[math]::Min($before.$cap,$before.$owner+$loss)};$newOwner=[math]::Min([double]2147483647,$newOwner)
            Near ($before.$target-$after.$target) $loss "$label wrong target resource loss $pool"
            Near $after.$owner $newOwner "$label wrong attacker resource gain $pool"
        }
        $gainMP=$after.owner_magicule-$before.owner_magicule;$gainAP=$after.owner_aura-$before.owner_aura
        Near $r.post.target_magicule ($r.pre.target_magicule-$lossMP+$regenMP) "$label MP reconciliation"
        Near $r.post.target_aura ($r.pre.target_aura-$lossAP+$regenAP) "$label AP reconciliation"
    }
    $results+=@{case=$i;mode=$r.mode;physical_attempts=1;physical_incoming=1;physical_applied=1;hurt_true=1;callbacks=$i;apply_calls=$i;drains=$i;successful_drains=$i;
        requested_percentage=$(if($i){[double][float]0.01}else{0});target_magicule_loss=$lossMP;target_aura_loss=$lossAP;attacker_magicule_gain=$gainMP;attacker_aura_gain=$gainAP;
        magicule_recovery=$regenMP;aura_recovery=$regenAP;hp_loss=$hpLoss;shp_delta=$r.post.shp-$r.pre.shp;cooldown_ticks_recorded=25;resource_writes=$by.resource_after.Count}
}
$report=[ordered]@{schema='tno.phase6.energy_native_path.validation.v1';checkpoint=$Checkpoint;status='PASS';rows=$rows.Count;raw_sha256=(Get-FileHash -LiteralPath $LogPath).Hash.ToLowerInvariant();results=$results;
    errors=0;duplicate_drains=0;recursions=0;unexpected_bypasses=0;unaccounted_resource_changes=0;production_changed=$false;limitations='ES2 neutral native bow only; Royal/L2 causality and final decision pending'}
$json=$report|ConvertTo-Json -Depth 20
if($OutputPath){Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing evidence overwrite';[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")}
$json
