param([Parameter(Mandatory=$true)][string]$LogPath,[ValidateSet('S2','S3')][string]$Checkpoint='S2',
      [string]$OutputPath,[string]$ValidationPath)
$ErrorActionPreference='Stop'
function Require($condition,$message) { if(!$condition) { throw $message } }
function Close([double]$a,[double]$b,$message) { Require ([double]::IsFinite($a) -and [double]::IsFinite($b) -and [Math]::Abs($a-$b) -lt 0.00002) $message }
function Save-New($path,$value) { if($path) { Require (!(Test-Path -LiteralPath $path)) "Refusing to overwrite $path"; [IO.File]::WriteAllText([IO.Path]::GetFullPath($path),$value+"`n") } }
$lines=[Collections.Generic.List[string]]::new()
$records=@(foreach($line in [IO.File]::ReadLines((Resolve-Path -LiteralPath $LogPath))) {
    $offset=$line.IndexOf('TNO_SOUL_NATIVE_PATH ')
    if($offset -ge 0) { $line=$line.Substring($offset+21) } elseif(!$line.StartsWith('{')) { continue }
    $value=$line | ConvertFrom-Json
    Require ($value.schema -ceq 'tno.phase6.soul_native_path.runtime.v1') 'Unknown schema'
    $lines.Add($line);$value
})
$catalog=@($records | Where-Object kind -eq catalog);$suite=@($records | Where-Object kind -eq suite_result);$rows=@($records | Where-Object kind -eq row)
$count=if($Checkpoint -eq 'S2'){2}else{20}
Require ($catalog.Count -eq 1 -and $suite.Count -eq 1 -and $rows.Count -eq $count -and $records.Count -eq $count+2) 'Incomplete/error capture'
Require ($catalog[0].requested_cases -eq $count -and $suite[0].completed_cases -eq $count -and $suite[0].status -eq 'complete' -and $suite[0].force_load_restored) 'Incomplete suite'
foreach($mod in @('tensura','l2hostility','apotheosis','royalvariations','tensura_neb')) { Require ($null -ne $catalog[0].mods.$mod) "Missing mod $mod" }
Require ($catalog[0].mods.tensura -ceq '2.0.1.1' -and $catalog[0].mods.l2hostility -ceq '3.0.18') 'Wrong native stack'
$soulTags=@('apothic_attributes:cannot_critically_strike','minecraft:bypasses_armor','minecraft:bypasses_effects','minecraft:bypasses_enchantments','minecraft:bypasses_invulnerability','minecraft:bypasses_resistance','minecraft:bypasses_shield','minecraft:bypasses_wolf_armor','minecraft:no_anger','minecraft:no_knockback','tensura:bypass_barrier','tensura:bypass_dimension_fault','tensura:bypass_distortion_field','tensura:bypass_dodge','tensura:bypass_multidimensional_barrier','tensura:bypass_protection_enchantment','tensura:is_spiritual')
$physicalTags=@('minecraft:always_kills_armor_stands','minecraft:is_projectile','minecraft:panic_causes','neoforge:is_physical','tensura:is_physical')
$uuids=[Collections.Generic.HashSet[string]]::new();$summaries=@()
foreach($row in $rows) {
    $i=$summaries.Count;$label="case $i"
    Require ($row.case -eq $i) "$label order"
    if($Checkpoint -eq 'S2') {
        Require ($row.mode -ceq @('vanilla_plain','vanilla_soul')[$i] -and $row.target -ceq 'neutral' -and $row.stage -ceq 'NONE') "$label matrix"
    } else {
        Require ($row.target -ceq @('neutral','orc_disaster','gazel_dwargo','luminous_valentine','hinata_sakaguchi')[[int][Math]::Floor($i/4)] -and $row.mode -ceq @('royal_legacy_s0','royal_legacy_s7','royal_native_s0','royal_native_s7')[$i%4]) "$label matrix"
        Require ($row.stage -ceq $(if($i%2 -eq 0){'S0'}else{'S7'})) "$label Stage"
        Require ($row.delivery -ceq $(if($row.mode.Contains('legacy')){'legacy_collision'}else{'native_final_lane_ticks'})) "$label delivery semantics"
    }
    $targetId=if($row.target -eq 'neutral'){'minecraft:iron_golem'}elseif($row.target -eq 'luminous_valentine'){'tensura_neb:luminous_valentine'}else{'tensura:'+$row.target}
    Require ($row.target_id -ceq $targetId -and $row.projectile -ceq $(if($Checkpoint -eq 'S2'){'minecraft:arrow'}else{'royalvariations:royal_arrow'})) "$label native identities"
    Require ($row.spawn_count -eq 1 -and $uuids.Add($row.projectile_uuid)) "$label duplicate delivery"
    Require ($row.can_hit -and $row.owner_retained -and $row.weapon_retained -and $row.legal_enchantment -and !$row.owner_creative -and @($row.owner_skills).Count -eq 0) "$label invalid prerequisites"
    Require (!$row.target_no_ai -and $row.target_tick_at_release -gt 0 -and $row.pre.target_tick -eq $row.target_tick_at_release -and $row.post.target_tick -gt $row.pre.target_tick) "$label target not ticking"
    Require (!$row.native_immune -and $row.spiritual_resistance -eq ($row.target -in @('gazel_dwargo','hinata_sakaguchi')) -and !$row.spiritual_nullification) "$label unexpected native defense"
    if($row.target -ne 'neutral') {
        Require ($row.l2_initialized -and $row.l2_level -eq 1000) "$label L2 initialization"
        $traitText=($row.traits.PSObject.Properties | Sort-Object Name | ForEach-Object {$_.Name+'='+$_.Value}) -join ';'
        $afterText=($row.traits_after.PSObject.Properties | Sort-Object Name | ForEach-Object {$_.Name+'='+$_.Value}) -join ';'
        $expectedTraits=switch($row.target) {
            orc_disaster {'adaptive=5;dementor=1;dispell=2;drain=2;regenerate=5;tank=5;wither=1'}
            gazel_dwargo {'adaptive=5;dementor=1;dispell=2;reflect=1;regenerate=5;tank=5'}
            hinata_sakaguchi {'adaptive=5;dementor=1;dispell=2;reflect=2;regenerate=5;tank=5'}
            luminous_valentine {'adaptive=5;dementor=1;dispell=3;killer_aura=1;reflect=2;regenerate=5;soul_burner=2;tank=5'}
        }
        Require ($traitText.Replace('l2hostility:','') -ceq $expectedTraits -and $afterText -ceq $traitText) "$label L2 profile changed"
    }
    Require ($row.weapon_soul_level -eq [int]$row.enchanted) "$label enchantment mismatch"
    $traces=@($row.traces);$attempt=@($traces | Where-Object boundary -eq physical_attempt);$physicalReturn=@($traces | Where-Object boundary -eq physical_return)
    $incoming=@($traces | Where-Object boundary -eq incoming_highest);$lowest=@($traces | Where-Object boundary -eq incoming_lowest);$post=@($traces | Where-Object boundary -eq damage_post)
    $callback=@($traces | Where-Object boundary -eq soul_callback);$source=@($traces | Where-Object boundary -eq soul_source);$soulReturn=@($traces | Where-Object boundary -eq soul_return)
    $event=@($traces | Where-Object boundary -eq spiritual_event);$writeBefore=@($traces | Where-Object boundary -eq shp_write_before);$writeAfter=@($traces | Where-Object boundary -eq shp_write_after)
    $soulCount=[int]$row.enchanted
    $flightUnresolved=$Checkpoint -eq 'S3' -and $i -eq 19
    $expectedIncoming=[int]($row.target -ne 'gazel_dwargo');$expectedApplied=[int]($row.target -in @('neutral','orc_disaster'))
    $expectedSource=if($row.target -eq 'gazel_dwargo'){0}else{$soulCount}
    $expectedEvent=if($row.target -in @('gazel_dwargo','hinata_sakaguchi')){0}else{$soulCount}
    if($flightUnresolved){$soulCount=0;$expectedIncoming=0;$expectedApplied=0;$expectedSource=0;$expectedEvent=0;Require (!$row.projectile_removed -and $row.projectile_age_end -eq 4 -and $row.observation_ticks -eq 25) "$label unresolved flight capture changed"}
    Require ($attempt.Count -eq [int](!$flightUnresolved) -and $physicalReturn.Count -eq [int](!$flightUnresolved) -and $incoming.Count -eq $expectedIncoming -and $lowest.Count -eq $expectedIncoming -and $post.Count -eq $expectedApplied) "$label physical counts"
    if(!$flightUnresolved){Require ($physicalReturn[0].result -eq [bool]$expectedApplied) "$label physical admission"}
    if($expectedApplied) { Require ($lowest[0].result -and $post[0].amount -gt 0) "$label physical application" }
    elseif($expectedIncoming) {
        $physicalDefense=if($row.target -eq 'hinata_sakaguchi'){'physical_attack_resistance'}else{'physical_attack_nullification'}
        Require (!$lowest[0].result -and ($row.target_skills -join ';').Contains('Toggled:1b,skill:"tensura:'+$physicalDefense+'"')) "$label native physical cancellation"
        if($row.target -eq 'hinata_sakaguchi'){Require ($attempt[0].amount -le $attempt[0].hp/2) "$label native physical Resistance threshold"}
    }
    if(!$flightUnresolved){Require (($attempt[0].projectile_age -eq 0) -eq $row.mode.Contains('legacy')) "$label delivery age"}
    Require ($callback.Count -eq $soulCount -and $source.Count -eq $expectedSource -and $soulReturn.Count -eq $expectedSource -and $event.Count -eq $expectedEvent -and $writeBefore.Count -eq $expectedEvent -and $writeAfter.Count -eq $expectedEvent) "$label native Soul counts"
    foreach($trace in $traces | Where-Object { $_.PSObject.Properties.Name -contains 'source' }) {
        $soul=$trace.boundary -in @('soul_source','spiritual_event','soul_return')
        Require ($trace.source -ceq $(if($soul){'tensura:soul_scatter'}else{'minecraft:arrow'})) "$label source substitution"
        Require ($trace.owner_retained -and $trace.direct_uuid -ceq $(if($soul){$row.owner_uuid}else{$row.projectile_uuid})) "$label source ownership"
        Require (($trace.tags -join ';') -ceq ($(if($soul){$soulTags}else{$physicalTags}) -join ';')) "$label source tags"
        Require ($trace.source_object -eq $(if($soul){$source[0].source_object}else{$attempt[0].source_object})) "$label source replaced"
        $bypass=if($soul -and $row.spiritual_resistance -and $row.stage -eq 'S7'){1}else{0}
        Close $trace.resistance_bypass $bypass "$label unexpected bypass"
    }
    $damage=0.0
    if($soulCount) {
        Require ([array]::IndexOf($traces,$callback[0]) -gt [array]::IndexOf($traces,$physicalReturn[0])) "$label callback admission/order"
        Close $callback[0].amount $attempt[0].amount "$label attempted amount attribution"
        if($expectedSource) {
            Require ($callback[0].cooldown -lt 40 -and $soulReturn[0].result -eq [bool]$expectedEvent) "$label native source admission"
            $scale=switch($row.stage){ NONE{1.0} S0{1.05} S7{1.4} }
            Close $source[0].amount ($callback[0].amount*$scale) "$label native Stage scale"
            if($expectedEvent) { $damage=$writeBefore[0].shp-$writeAfter[0].shp;Close $damage $source[0].amount "$label Soul accounting" }
            else { Require ($row.spiritual_resistance -and $source[0].amount -le $source[0].hp/2) "$label native Resistance threshold" }
            Close $source[0].hp $soulReturn[0].hp "$label unexpected Soul HP change"
            foreach($resource in @('target_magicule','target_aura','owner_hp','owner_shp','owner_magicule','owner_aura')) { Close $source[0].$resource $soulReturn[0].$resource "$label Soul resource transfer $resource" }
        } else {
            Require ($callback[0].cooldown -eq 80 -and $row.pre.native_phase -eq 0 -and $physicalReturn[0].native_phase -eq 1) "$label Gazel native encounter gate"
        }
    }
    # Independently reconcile every recorded state against actual native storage writes.
    $shp=[double]$row.pre.shp;$pending=$null;$positive=0.0;$negative=0.0;$nebRecovered=0.0
    foreach($trace in $traces) {
        Require ($trace.boundary -in @('physical_attempt','physical_return','incoming_highest','incoming_lowest','damage_post','soul_callback','soul_source','soul_return','spiritual_event','shp_write_before','shp_write_after','storage_before','storage_after','resource_before','resource_after')) "$label unknown boundary"
        if($trace.boundary -eq 'storage_after') {
            Require ($null -ne $pending) "$label unpaired resource write"
            Close $trace.requested_shp $pending.requested_shp "$label changed storage argument"
            Close $trace.shp $trace.requested_shp "$label incorrect resource accounting"
            $delta=$trace.shp-$shp
            if($delta -lt 0) {
                Require ($trace.native_callers -contains 'io.github.manasmods.tensura.damage.TensuraDamageHelper.directSpiritualHurt') "$label unexplained SHP subtraction"
                $negative-=$delta
            } elseif($delta -gt 0) {
                $known=$trace.native_callers -contains 'io.github.manasmods.tensura.storage.ep.ExistenceStorage.handleSpiritualHealthRegen' -or $trace.native_callers -contains 'io.github.manasmods.tensura.effect.ability.InstantRegenerationEffect.healSHP'
                if(!$known) {
                    # The old SHP stack filter omitted the addon namespace. Its immediately adjacent HP
                    # heal retains the caller; installed NEB tick bytecode pairs heal(10) with SHP+50.
                    $previous=$traces[[array]::IndexOf($traces,$pending)-1]
                    Require ($row.target -eq 'luminous_valentine' -and @($trace.native_callers).Count -eq 0 -and $previous.boundary -eq 'resource_after' -and $previous.resource -eq 'hp' -and $previous.native_callers -contains 'io.github.manasmods.tensura_neb.entity.LuminousValentineEntity.tick' -and $previous.relative_tick -eq $trace.relative_tick) "$label unexplained recovery"
                    Close ($previous.requested-$previous.hp) 10 "$label native NEB heal pair"
                    Close $delta 50 "$label native NEB SHP pair";$nebRecovered+=$delta
                }
                $positive+=$delta
            }
            $shp=$trace.shp;$pending=$null
        } else {
            Close $trace.shp $shp "$label unobserved SHP movement"
            if($trace.boundary -eq 'storage_before') { Require ($null -eq $pending) "$label nested/duplicate resource write"; $pending=$trace }
        }
    }
    Require ($null -eq $pending) "$label unfinished resource write"
    Close $row.post.shp $shp "$label persistent resource accounting"
    Close $negative $damage "$label duplicate Soul subtraction"
    Close ($row.pre.shp-$damage+$positive) $row.post.shp "$label total SHP accounting"
    $physicalDamage=if($post.Count){$post[0].amount}else{0}
    $hpRecovery=0.0;$hpLoss=0.0;$mpSpent=0.0;$mpRecovery=0.0;$mpSkillSpent=0.0;$bossDrainGain=0.0;$ownerDrain=0.0
    if($Checkpoint -eq 'S2') {
        Close ($row.pre.hp-$row.post.hp) $physicalDamage "$label physical HP accounting"
        foreach($resource in @('target_magicule','target_aura')) { Close $row.pre.$resource $row.post.$resource "$label unaccounted $resource" }
    } else {
        foreach($resource in @('hp','target_magicule','target_aura','owner_hp','owner_shp','owner_magicule','owner_aura')) {
            $state=[double]$row.pre.$resource;$pending=$null
            foreach($trace in $traces) {
                if($trace.boundary -eq 'resource_after' -and $trace.resource -eq $resource) {
                    Require ($null -ne $pending) "$label unpaired $resource write"
                    Close $trace.requested $pending.requested "$label changed $resource argument"
                    $expected=if($resource -eq 'hp'){[Math]::Clamp($trace.requested,0,$row.pre.hp)}else{[Math]::Min($trace.requested,2147483647)}
                    Require ([Math]::Abs($trace.$resource-$expected) -lt $(if($resource -eq 'hp'){0.002}else{0.00002})) "$label wrong $resource setter result"
                    $delta=$trace.$resource-$state
                    if($resource -eq 'hp') {
                        if($delta -gt 0){$hpRecovery+=$delta;Require (($trace.native_callers -join ';') -match '(RegenerateTrait|RegenerationEffect|\.heal;)') "$label nonnative HP recovery"}
                        elseif($delta -lt 0){$hpLoss-=$delta;Require (($trace.native_callers -join ';') -match 'LivingEntity.actuallyHurt') "$label nonnative HP damage"}
                    } elseif($resource -eq 'target_magicule') {
                        if($delta -lt 0){
                            if($trace.native_callers -contains 'io.github.manasmods.tensura.effect.ability.InstantRegenerationEffect.applyEffectTick'){$mpSpent-=$delta}
                            else {Require ($trace.native_callers -contains 'io.github.manasmods.tensura.ability.skill.extra.UniversalPerceptionSkill.onTick') "$label unknown magicule cost";$mpSkillSpent-=$delta}
                        }
                        elseif($delta -gt 0){
                            if($trace.native_callers -contains 'io.github.manasmods.tensura.util.EnergyHelper.drainEnergy'){$bossDrainGain+=$delta}
                            else {$mpRecovery+=$delta;Require ($trace.native_callers -contains 'io.github.manasmods.tensura.storage.ep.ExistenceStorage.handleMagiculeRegen') "$label unknown magicule recovery"}
                        }
                    } elseif($resource -eq 'owner_magicule' -and $delta -lt 0) {
                        Require ($row.target -eq 'luminous_valentine' -and $trace.native_callers -contains 'io.github.manasmods.tensura.util.EnergyHelper.drainEnergy') "$label unknown owner drain"
                        $ownerDrain-=$delta
                    } else {Close $delta 0 "$label unknown $resource movement"}
                    $state=[double]$trace.$resource;$pending=$null
                } else {
                    Close $trace.$resource $state "$label unobserved $resource movement"
                    if($trace.boundary -eq 'resource_before' -and $trace.resource -eq $resource){Require ($null -eq $pending) "$label nested $resource write";$pending=$trace}
                }
            }
            Require ($null -eq $pending) "$label unfinished $resource write";Close $state $row.post.$resource "$label persistent $resource accounting"
        }
        Require ([Math]::Abs($hpLoss-$physicalDamage) -lt 0.002) "$label physical HP attribution"
        if($row.target -eq 'orc_disaster'){Require ($physicalDamage -lt $attempt[0].amount) "$label missing physical mitigation"}
        # Native gainMagicule caps NORMAL gain; victim loss need not equal recipient gain at capacity.
        Require ($bossDrainGain -ge 0 -and $bossDrainGain -le $ownerDrain) "$label native boss drain accounting"
        if($ownerDrain -gt $bossDrainGain) {
            Require (@($traces | Where-Object { $_.boundary -eq 'resource_after' -and $_.resource -eq 'target_magicule' -and $_.native_callers -contains 'io.github.manasmods.tensura.util.EnergyHelper.gainMagicule' -and $_.native_callers -contains 'io.github.manasmods.tensura.util.EnergyHelper.drainEnergy' }).Count -gt 0) "$label missing native capped gain"
        }
    }
    if($Checkpoint -eq 'S2') { foreach($resource in @('owner_hp','owner_shp','owner_magicule','owner_aura')) { Close $row.pre.$resource $row.post.$resource "$label unaccounted $resource" } }
    $summaries += [ordered]@{case=$i;mode=$row.mode;target=$row.target;stage=$row.stage;flight_unresolved=$flightUnresolved;physical_attempts=$attempt.Count;physical_incoming=$incoming.Count;physical_applied=$post.Count;
        physical_damage=$physicalDamage;native_hp_recovery=$hpRecovery;soul_callbacks=$callback.Count;soul_sources=$source.Count;spiritual_events=$event.Count;soul_hp_incoming=0;soul_hp_applied=0;
        shp_damage=$damage;native_shp_recovery=$positive;neb_shp_recovery_reconstructed_from_adjacent_native_heal=$nebRecovered;native_regeneration_mp_cost=$mpSpent;native_perception_mp_cost=$mpSkillSpent;native_mp_recovery=$mpRecovery;native_boss_mp_drain_gain=$bossDrainGain;owner_mp_drained_by_boss=$ownerDrain;native_drain_not_retained_by_boss=($ownerDrain-$bossDrainGain);
        pre_hp=$row.pre.hp;post_hp=$row.post.hp;pre_shp=$row.pre.shp;post_shp=$row.post.shp;
        first_divergence=$(if($flightUnresolved){'No physical attempt observed; projectile still alive at age 4 after 25 server ticks. Flight cause unresolved; this row cannot establish a Soul gate.'}else{switch($row.target){gazel_dwargo{'native encounter opening rejects physical attempt and sets cooldown 80; Soul callback exits before source'}hinata_sakaguchi{'physical Resistance cancels HP event; Soul source then rejected by native Spiritual Resistance HP/2 gate'}luminous_valentine{'physical nullification cancels HP event; Soul still succeeds, native regeneration restores SHP'}default{'none at native Soul path; ordinary Soul HP event absence is expected'}}})}
}
$report=[ordered]@{schema='tno.phase6.soul_native_path.validation.v1';checkpoint=$Checkpoint;status='PASS';cases=$count;errors=0;duplicates=0;unaccounted_resource_changes=0;
    evidence_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes(($lines -join "`n")+"`n"))).ToLowerInvariant();rows=$summaries}
Save-New $OutputPath ($lines -join "`n"); Save-New $ValidationPath ($report | ConvertTo-Json -Depth 30)
$report | ConvertTo-Json -Depth 30
