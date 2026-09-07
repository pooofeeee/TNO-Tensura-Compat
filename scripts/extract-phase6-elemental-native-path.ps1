param(
    [Parameter(Mandatory=$true)][string]$LogPath,
    [string]$OutputPath,
    [string]$ValidationPath
)
$ErrorActionPreference = 'Stop'
$schema = 'tno.phase6.elemental_native_path.runtime.v1'
$marker = 'TNO_ELEMENTAL_NATIVE_PATH '
function Require([bool]$Condition,[string]$Message) { if (!$Condition) { throw $Message } }
function Close([double]$Actual,[double]$Expected,[string]$Message) {
    Require ([double]::IsFinite($Actual) -and [Math]::Abs($Actual-$Expected) -lt 0.00001) $Message
}
function Same-Map($Left,$Right) {
    $a = @($Left.PSObject.Properties | ForEach-Object { $_.Name + '=' + $_.Value } | Sort-Object)
    $b = @($Right.PSObject.Properties | ForEach-Object { $_.Name + '=' + $_.Value } | Sort-Object)
    return ($a -join ';') -ceq ($b -join ';')
}
function Save-New([string]$Path,[string]$Text) {
    if (!$Path) { return }
    Require (!(Test-Path -LiteralPath $Path)) "Refusing to overwrite $Path"
    New-Item -ItemType Directory -Force (Split-Path $Path) | Out-Null
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($Path), $Text + "`n")
}
$lines = [Collections.Generic.List[string]]::new()
$records = foreach ($line in [IO.File]::ReadLines((Resolve-Path -LiteralPath $LogPath))) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -ge 0) { $line = $line.Substring($index + $marker.Length) }
    elseif (!$line.StartsWith('{')) { continue }
    $value = $line | ConvertFrom-Json
    Require ($value.schema -ceq $schema) 'Unexpected schema'
    $lines.Add($line)
    $value
}
Require (@($records).Count -eq 92) 'Expected 92 records'
Require (@($records | Where-Object kind -eq error).Count -eq 0) 'Capture contains errors'
$catalogs = @($records | Where-Object kind -eq catalog)
$suites = @($records | Where-Object kind -eq suite_result)
$rows = @($records | Where-Object kind -eq row)
Require ($catalogs.Count -eq 1 -and $suites.Count -eq 1 -and $rows.Count -eq 90) 'Incomplete matrix'
Require ($catalogs[0].requested_cases -eq 90 -and $catalogs[0].full_stack -and !$catalogs[0].production_prototype) 'Invalid catalog'
Require ($suites[0].status -eq 'complete' -and $suites[0].completed_cases -eq 90 -and $suites[0].force_load_restored) 'Suite did not complete/clean up'
$elements = @('earth','fire','space','water','wind')
$targets = @('neutral','orc_disaster','luminous_valentine')
$modes = @('vanilla_free','royal_legacy','royal_rescue','royal_native','royal_native_s7','royal_free')
$projectiles = @('stone_shot','fire_bolt','space_cut_projectile','water_ball','wind_sphere')
$speeds = @(3.0,2.0,1.75,1.25,1.0)
$burns = @(0,100,0,-1,-1)
$knock = @(1.5,0,0,1.0,3.0)
$nullification = @('earth','flame','spatial','water','wind')
$orc = [pscustomobject]@{'l2hostility:adaptive'=5;'l2hostility:dementor'=1;'l2hostility:dispell'=2;'l2hostility:drain'=2;'l2hostility:regenerate'=5;'l2hostility:tank'=5;'l2hostility:wither'=1}
$luminous = [pscustomobject]@{'l2hostility:adaptive'=5;'l2hostility:dementor'=1;'l2hostility:dispell'=3;'l2hostility:killer_aura'=1;'l2hostility:reflect'=2;'l2hostility:regenerate'=5;'l2hostility:soul_burner'=2;'l2hostility:tank'=5}
$uuids = [Collections.Generic.HashSet[string]]::new()
$summaries = [Collections.Generic.List[object]]::new()
$expectedCase = 0
foreach ($element in $elements) { foreach ($target in $targets) { foreach ($mode in $modes) {
    $row = $rows[$expectedCase]
    $label = "case $expectedCase $element/$target/$mode"
    Require ($row.case -eq $expectedCase -and $row.element -ceq $element -and $row.target -ceq $target -and $row.mode -ceq $mode) "${label}: matrix order mismatch"
    $ei = [array]::IndexOf($elements,$element)
    $source = "tensura:${element}_elemental"
    $projectile = 'tensura:' + $projectiles[$ei]
    $targetId = switch ($target) { neutral {'minecraft:armor_stand'} orc_disaster {'tensura:orc_disaster'} luminous_valentine {'tensura_neb:luminous_valentine'} }
    Require ($row.target_id -ceq $targetId -and $row.projectile -ceq $projectile) "$label identity mismatch"
    Require ($row.spawn_count -eq 1 -and $uuids.Add($row.projectile_uuid)) "$label duplicated/missing projectile"
    Require ($row.owner_retained -and !$row.owner_creative -and @($row.owner_skills).Count -eq 0) "$label changed owner prerequisite"
    Require ($row.projectile_skill -ceq 'null' -and $row.projectile_mp_cost -eq 0 -and $row.projectile_ap_cost -eq 0) "$label injected skill/cost"
    Require ($row.slotting_capacity -eq 1 -and $row.core_count_before -eq 1 -and $row.core_count_after -eq 1) "$label changed Slotting loadout"
    Require ($row.pickable -and $row.can_hit_at_release -and !$row.target_no_ai) "$label ineligible/non-ticking target"
    $stage = if ($mode -eq 'vanilla_free') {'NONE'} elseif ($mode -eq 'royal_native_s7') {'S7'} else {'S0'}
    $amount = if ($stage -eq 'NONE') {1.0} elseif ($stage -eq 'S7') {1.4} else {1.05}
    Require ($row.stage -ceq $stage) "$label unexpected Stage"
    Close $row.damage $amount "$label damage not from locked native/Stage path"
    Close $row.speed $speeds[$ei] "$label altered native speed"
    Close $row.knockback $knock[$ei] "$label altered native knockback"
    Require ($row.burn_ticks -eq $burns[$ei] -and $row.no_gravity -eq ($element -eq 'wind')) "$label altered utility"
    Require ($row.elemental_attack -eq ($element -ne 'water')) "$label normalized Water flag"
    if ($target -ne 'neutral') {
        Require ($row.l2_level -eq 1000 -and $row.l2_initialized) "$label invalid L2 initialization"
        $expectedTraits = if ($target -eq 'orc_disaster') {$orc} else {$luminous}
        Require ((Same-Map $row.traits $expectedTraits) -and (Same-Map $row.traits_after $expectedTraits)) "$label changed accepted trait ranks"
    }
    else { Require (!$row.l2_initialized -and $row.l2_level -eq 0 -and @($row.target_skills).Count -eq 0) "$label invalid neutral control" }
    foreach ($trace in $row.traces) { Require ($trace.uuid -ceq $row.projectile_uuid) "$label trace projectile replaced" }
    $legacy = @($row.traces | Where-Object phase -eq LEGACY_CALL)
    if ($mode -in 'royal_legacy','royal_rescue') {
        Require (($legacy.boundary -join ',') -ceq 'vanilla_on_hit,one_argument_hit') "$label historical route no longer an empty callback"
        Require ($row.legacy_trace_count -eq 2 -and !$row.legacy_removed) "$label legacy control removed/mutated projectile"
        Close $row.legacy_hp $row.pre_hp "$label legacy call damaged HP"
        Close $row.legacy_shp $row.pre_shp "$label legacy call damaged SHP"
    }
    else { Require ($legacy.Count -eq 0) "$label unexpected legacy dispatch" }
    $run = @($row.traces | Where-Object phase -eq RUN)
    if ($mode -eq 'royal_legacy') {
        Require ($run.Count -eq 0 -and $row.projectile_age_end -eq 0) "$label historical discard unexpectedly ticked"
    }
    else {
        Require ($row.projectile_age_end -gt 0 -and $row.target_ticks_elapsed -gt 0) "$label did not tick naturally"
        $expectedStart = 'native_projectile_gate,two_argument_hit,one_argument_hit,deal_damage,native_hurt_call'
        Require ($run.Count -ge 8 -and ($run[0..4].boundary -join ',') -ceq $expectedStart) "$label native call sequence changed"
        Require ($run[0].detail -ceq 'DEFAULT/NONE') "$label unexpected native gate/deflection"
        foreach ($boundary in @('native_projectile_gate','two_argument_hit','deal_damage','native_hurt_call','native_hurt_return')) {
            Require (@($run | Where-Object boundary -eq $boundary).Count -eq 1) "$label $boundary duplicated/missing"
        }
        $family = @($run | Where-Object source -eq $source)
        foreach ($boundary in @('native_hurt_call','incoming_highest','incoming_lowest','native_hurt_return')) {
            Require (@($family | Where-Object boundary -eq $boundary).Count -eq 1) "$label missing/duplicated $source at $boundary"
        }
        $call = @($family | Where-Object boundary -eq native_hurt_call)[0]
        Close $call.amount $amount "$label wrong native hurt amount"
        foreach ($trace in $family) {
            Require ($trace.direct -ceq $projectile -and $trace.direct_uuid -ceq $row.projectile_uuid -and $trace.owner_retained) "$label changed native source identity"
            Require ($trace.magic_type -ceq $(if ($element -eq 'water') {'null'} else {'SPIRITUAL'})) "$label magic type changed"
            Require ($trace.resistance_bypass -eq 0) "$label unexpected resistance bypass"
        }
        $post = @($family | Where-Object boundary -eq damage_post)
        $low = @($family | Where-Object boundary -eq incoming_lowest)[0]
        $returned = @($family | Where-Object boundary -eq native_hurt_return)[0]
        if ($target -eq 'luminous_valentine') {
            Require ($low.canceled -and !$returned.result -and $post.Count -eq 0) "$label Nullification did not remain authoritative"
            $skill = 'skill:"tensura:' + $nullification[$ei] + '_attack_nullification"'
            Require (@($row.target_skills | Where-Object { $_.Contains($skill) -and $_.Contains('Toggled:1b') }).Count -eq 1) "$label missing native matching Nullification"
        }
        else { Require (!$low.canceled -and $returned.result -and $post.Count -eq 1 -and $post[0].amount -gt 0) "$label working native path failed" }
        $otherSources = @($run | Where-Object { $_.source -and $_.source -ne $source } | ForEach-Object source | Sort-Object -Unique)
        foreach ($other in $otherSources) { Require ($element -eq 'fire' -and $other -eq 'minecraft:on_fire') "$label unexpected extra damage source $other" }
    }
    $summaries.Add([ordered]@{case=$expectedCase;element=$element;target=$target;mode=$mode;
        native_event_created=($mode -ne 'royal_legacy');nullified=($mode -ne 'royal_legacy' -and $target -eq 'luminous_valentine');
        native_damage=$row.damage;projectile_age=$row.projectile_age_end})
    $expectedCase++
} } }
$validation = [ordered]@{schema='tno.phase6.elemental_native_path.validation.v1';status='PASS';cases=90;
    historical_empty_dispatch_cases=15;same_projectile_rescues=15;native_family_events=75;
    native_family_post_events=50;nullified_native_family_events=25;duplicate_family_events=0;
    injected_skills=0;unexpected_bypass=0;unique_projectiles=$uuids.Count;rows=@($summaries)}
Save-New $OutputPath ($lines -join "`n")
Save-New $ValidationPath ($validation | ConvertTo-Json -Depth 10)
$validation | Select-Object status,cases,historical_empty_dispatch_cases,same_projectile_rescues,native_family_events,native_family_post_events,nullified_native_family_events,unique_projectiles | ConvertTo-Json
