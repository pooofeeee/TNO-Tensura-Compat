param([Parameter(Mandatory=$true)][string]$TensuraJar,
      [Parameter(Mandatory=$true)][string]$JavaHome,
      [string]$OutputPath)
$ErrorActionPreference='Stop'
function Require($condition,$message) { if (!$condition) { throw $message } }
$zip=[IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $TensuraJar))
function Read-Entry($name) {
    $reader=[IO.StreamReader]::new($zip.GetEntry($name).Open())
    try { $reader.ReadToEnd() } finally { $reader.Dispose() }
}
try {
    $definition=Read-Entry 'data/tensura/enchantment/soul_eater.json' | ConvertFrom-Json
    $damageType=Read-Entry 'data/tensura/damage_type/soul_scatter.json' | ConvertFrom-Json
    $tags=@(foreach($entry in $zip.Entries) {
        if ($entry.FullName -like 'data/*/tags/damage_type/*.json' -and (Read-Entry $entry.FullName).Contains('tensura:soul_scatter')) { $entry.FullName }
    })
    $classes=@(foreach($name in @('enchantment.effect.SpiritualDamageEntity','enchantment.TensuraEnchantmentHelper',
        'enchantment.template.EnchantmentPostDamageWithTypeEffect','damage.TensuraDamageHelper',
        'mixin.MixinAbstractArrow','mixin.MixinPlayer','handler.DamagingHandler','event.TensuraEntityEvents')) {
        $class='io.github.manasmods.tensura.'+$name
        $code=(& (Join-Path $JavaHome 'bin/javap.exe') -p -s -c -classpath $TensuraJar $class) -join "`n"
        Require ($LASTEXITCODE -eq 0) "javap failed: $class"
        $entry=$zip.GetEntry($class.Replace('.','/')+'.class'); $stream=$entry.Open()
        try {$hash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant()} finally {$stream.Dispose()}
        if($name -eq 'damage.TensuraDamageHelper') {
            foreach($needle in @('SPIRITUAL_HURT_EVENT','setSpiritualHealth','SPIRITUAL_ATTACK_NULLIFICATION','SPIRITUAL_ATTACK_RESISTANCE','NO_SPIRITUAL_DAMAGE')) {
                Require ($code.Contains($needle)) "Native helper changed: $needle"
            }
        }
        if($name -eq 'enchantment.effect.SpiritualDamageEntity') {
            Require ($code.Contains('directSpiritualHurt:') -and $code.Contains('bipush        40')) 'Soul callback changed'
        }
        [ordered]@{class=$class;class_sha256=$hash;descriptors=@($code -split "`n" | Where-Object {$_ -match 'descriptor:'} | ForEach-Object {$_.Trim()})}
    })
    $old=@(Get-Content docs/benchmarks/phase6-endgame-viability/soul_eater.jsonl | ConvertFrom-Json | Where-Object kind -eq row)
    Require ($old.Count -eq 320) 'Historical row count changed'
    Require (@($old | Where-Object failure_reason -eq NATIVE_EVENT_ABSENT).Count -eq 320) 'Historical event observation changed'
    $report=[ordered]@{
        schema='tno.phase6.soul_native_path.static.v1';checkpoint='S1';status='PASS';runtime_status='PENDING';
        source_head='deeb10247883b1825338349b8a6250e39d026a2e';tensura_version='2.0.1.1';
        tensura_sha256=(Get-FileHash -LiteralPath $TensuraJar).Hash.ToLowerInvariant();
        definition=$definition;damage_type=$damageType;direct_packaged_tags=$tags;
        supported_items=(Read-Entry 'data/tensura/tags/item/handheld_enchantable.json' | ConvertFrom-Json);
        excluded_entities=(Read-Entry 'data/tensura/tags/entity_type/no_spiritual_damage.json' | ConvertFrom-Json);
        classes=$classes;
        call_graph=@('Player.attack or AbstractArrow.onHitEntity: injection AFTER first Entity.hurt call, independent of returned success',
            'TensuraEnchantmentHelper.doAdditionalAfterAttack -> mainhand enchantment iteration -> AFTER_ATTACK conditional effect',
            'EnchantmentPostDamageWithTypeEffect.apply(...,float) -> TOTAL_ATTACK_MULTIPLY uses attempted physical amount',
            'SpiritualDamageEntity.postDamage(int,EnchantedItemInUse,Entity,float): cooldown<40 and LivingEntity -> new DamageSource(holder,owner)',
            'existing TNO SpiritualDamageEntityMixin: Stage scale then existing matching Resistance recovery -> original helper',
            'TensuraDamageHelper.directSpiritualHurt(LivingEntity,Entity,DamageSource,float): entity exclusion, spiritual nullification, resistance HP/2 gate and 50% reduction',
            'five-argument helper: server + immunity + Spiritual Protection + positive amount -> native SPIRITUAL_HURT_EVENT',
            'native event accepted -> subtract SHP (clamped zero), mark hurt, native death if SHP zero, dirty and sync; no ordinary hurt call in normal branch');
        callback_prerequisites=@('server side','mainhand enchanted source stack','living owner for arrows','arrow weapon item nonnull','arrow victim not Enderman','SkillUtils.shouldCancelInteraction(owner) false','matchingSlot and conditional effect match','target LivingEntity with invulnerableTime < 40');
        helper_rejections=@('no_spiritual_damage entity tag','active spiritual nullification','active spiritual resistance and amount <= HP/2','client','dead or infinite-material target','labyrinth PVP disabled','Anti Skill toggled or active preset when attacker differs','Spiritual Protection reduces amount to <=0','native spiritual event returns false');
        special_event_branches=@('DamagingHandler: Ogre Berserker amplifier >=1 calls native target.hurt with physical-converted source then interrupts spiritual subtraction','TrainingDummy emits native feedback then interrupts subtraction');
        resources='No Soul Eater skill, affinity, EP threshold, cost, transfer, heal, random roll or cooldown mutation in normal native callback/helper. Native SHP reaching zero causes HP/absorption zero and death. Physical path may independently change resources.';
        defenses='Normal SHP branch does not dispatch NeoForge HP damage events: ordinary L2 HP-event mitigation is not a missing downstream hook. Native spiritual Resistance uses direct toggles/HP threshold, not source bypass metadata. Runtime required for stack interactions.';
        historical=[ordered]@{rows=$old.Count;absent_hp_events=320;shp_decreased_rows=@($old | Where-Object { $_.post_SHP -lt $_.pre_SHP }).Count;sha256=(Get-FileHash docs/benchmarks/phase6-endgame-viability/soul_eater.jsonl).Hash.ToLowerInvariant();
            delivery='Phase5FSuiteBBenchmark.fireFullDraw invokes real AbstractArrow.onHitEntity(EntityHitResult) after eligibility check, then discards. This is not Elemental empty overload.'};
        hypothesis='Ordinary HP-event absence is expected despite native Soul callback, spiritual event and SHP damage. Royal legacy delivery already reaches the callback; native target gates explain boss exclusions.';
        positive_control='Normally ticking eligible vanilla living target, survival FakePlayer, legal Soul Eater mainhand native bow or sword, genuine attack/release and collision. Observe callback, helper entry/exit and native spiritual event without mutation; compare no-enchantment control. Do not use armor stand because native entity tag excludes it.';
        production_changed=$false
    }
} finally {$zip.Dispose()}
$json=$report | ConvertTo-Json -Depth 30
if($OutputPath) {
    Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing to overwrite evidence'
    New-Item -ItemType Directory -Force (Split-Path $OutputPath) | Out-Null
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")
}
$json
