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
$count=if($Checkpoint -eq 'S2'){2}else{16}
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
    } else { throw 'S3 validation not installed yet' }
    Require ($row.target_id -ceq 'minecraft:iron_golem' -and $row.projectile -ceq 'minecraft:arrow') "$label native identities"
    Require ($row.spawn_count -eq 1 -and $uuids.Add($row.projectile_uuid)) "$label duplicate delivery"
    Require ($row.can_hit -and $row.owner_retained -and $row.weapon_retained -and $row.legal_enchantment -and !$row.owner_creative -and @($row.owner_skills).Count -eq 0) "$label invalid prerequisites"
    Require (!$row.target_no_ai -and $row.target_tick_at_release -ge 20 -and $row.post.target_tick -gt $row.pre.target_tick) "$label target not ticking"
    Require (!$row.native_immune -and !$row.spiritual_resistance -and !$row.spiritual_nullification) "$label unexpected control defense"
    Require ($row.weapon_soul_level -eq [int]$row.enchanted) "$label enchantment mismatch"
    $traces=@($row.traces);$attempt=@($traces | Where-Object boundary -eq physical_attempt);$physicalReturn=@($traces | Where-Object boundary -eq physical_return)
    $incoming=@($traces | Where-Object boundary -eq incoming_highest);$lowest=@($traces | Where-Object boundary -eq incoming_lowest);$post=@($traces | Where-Object boundary -eq damage_post)
    $callback=@($traces | Where-Object boundary -eq soul_callback);$source=@($traces | Where-Object boundary -eq soul_source);$soulReturn=@($traces | Where-Object boundary -eq soul_return)
    $event=@($traces | Where-Object boundary -eq spiritual_event);$writeBefore=@($traces | Where-Object boundary -eq shp_write_before);$writeAfter=@($traces | Where-Object boundary -eq shp_write_after)
    $soulCount=[int]$row.enchanted
    Require ($attempt.Count -eq 1 -and $physicalReturn.Count -eq 1 -and $incoming.Count -eq 1 -and $lowest.Count -eq 1 -and $post.Count -eq 1) "$label physical counts"
    Require ($physicalReturn[0].result -and $lowest[0].result -and $post[0].amount -gt 0 -and $attempt[0].projectile_age -gt 0) "$label physical admission"
    Require ($callback.Count -eq $soulCount -and $source.Count -eq $soulCount -and $soulReturn.Count -eq $soulCount -and $event.Count -eq $soulCount -and $writeBefore.Count -eq $soulCount -and $writeAfter.Count -eq $soulCount) "$label native Soul counts"
    foreach($trace in $traces | Where-Object { $_.PSObject.Properties.Name -contains 'source' }) {
        $soul=$trace.boundary -in @('soul_source','spiritual_event','soul_return')
        Require ($trace.source -ceq $(if($soul){'tensura:soul_scatter'}else{'minecraft:arrow'})) "$label source substitution"
        Require ($trace.owner_retained -and $trace.direct_uuid -ceq $(if($soul){$row.owner_uuid}else{$row.projectile_uuid})) "$label source ownership"
        Require (($trace.tags -join ';') -ceq ($(if($soul){$soulTags}else{$physicalTags}) -join ';')) "$label source tags"
        Require ($trace.source_object -eq $(if($soul){$source[0].source_object}else{$attempt[0].source_object})) "$label source replaced"
        Close $trace.resistance_bypass 0 "$label unexpected bypass"
    }
    $damage=0.0
    if($row.enchanted) {
        Require ($soulReturn[0].result -and $callback[0].cooldown -lt 40 -and [array]::IndexOf($traces,$callback[0]) -gt [array]::IndexOf($traces,$physicalReturn[0])) "$label callback admission/order"
        Close $callback[0].amount $attempt[0].amount "$label attempted amount attribution"
        Close $source[0].amount $callback[0].amount "$label native control scale"
        $damage=$writeBefore[0].shp-$writeAfter[0].shp
        Close $damage $source[0].amount "$label Soul accounting"
        Close $source[0].hp $soulReturn[0].hp "$label unexpected Soul HP change"
        foreach($resource in @('target_magicule','target_aura','owner_hp','owner_shp','owner_magicule','owner_aura')) { Close $source[0].$resource $soulReturn[0].$resource "$label Soul resource transfer $resource" }
    }
    # Independently reconcile every recorded state against actual native storage writes.
    $shp=[double]$row.pre.shp;$pending=$null;$positive=0.0;$negative=0.0
    foreach($trace in $traces) {
        Require ($trace.boundary -in @('physical_attempt','physical_return','incoming_highest','incoming_lowest','damage_post','soul_callback','soul_source','soul_return','spiritual_event','shp_write_before','shp_write_after','storage_before','storage_after')) "$label unknown boundary"
        if($trace.boundary -eq 'storage_after') {
            Require ($null -ne $pending) "$label unpaired resource write"
            Close $trace.requested_shp $pending.requested_shp "$label changed storage argument"
            Close $trace.shp $trace.requested_shp "$label incorrect resource accounting"
            $delta=$trace.shp-$shp
            if($delta -lt 0) {
                Require ($trace.native_callers -contains 'io.github.manasmods.tensura.damage.TensuraDamageHelper.directSpiritualHurt') "$label unexplained SHP subtraction"
                $negative-=$delta
            } elseif($delta -gt 0) {
                Require ($trace.native_callers -contains 'io.github.manasmods.tensura.storage.ep.ExistenceStorage.handleSpiritualHealthRegen') "$label unexplained recovery"
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
    Close ($row.pre.hp-$row.post.hp) $post[0].amount "$label physical HP accounting"
    foreach($resource in @('target_magicule','target_aura','owner_hp','owner_shp','owner_magicule','owner_aura')) { Close $row.pre.$resource $row.post.$resource "$label unaccounted $resource" }
    $summaries += [ordered]@{case=$i;mode=$row.mode;target=$row.target;stage=$row.stage;physical_attempts=1;physical_incoming=1;physical_applied=1;
        physical_damage=$post[0].amount;soul_callbacks=$callback.Count;soul_sources=$source.Count;spiritual_events=$event.Count;soul_hp_incoming=0;soul_hp_applied=0;
        shp_damage=$damage;native_shp_recovery=$positive;pre_hp=$row.pre.hp;post_hp=$row.post.hp;pre_shp=$row.pre.shp;post_shp=$row.post.shp}
}
$report=[ordered]@{schema='tno.phase6.soul_native_path.validation.v1';checkpoint=$Checkpoint;status='PASS';cases=$count;errors=0;duplicates=0;unaccounted_resource_changes=0;
    evidence_sha256=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData([Text.Encoding]::UTF8.GetBytes(($lines -join "`n")+"`n"))).ToLowerInvariant();rows=$summaries}
Save-New $OutputPath ($lines -join "`n"); Save-New $ValidationPath ($report | ConvertTo-Json -Depth 30)
$report | ConvertTo-Json -Depth 30
