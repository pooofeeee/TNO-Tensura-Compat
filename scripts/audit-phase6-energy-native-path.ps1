param([Parameter(Mandatory=$true)][string]$TensuraJar,
      [Parameter(Mandatory=$true)][string]$JavaHome,
      [string]$MinecraftJar='build/moddev/artifacts/neoforge-21.1.248.jar',
      [string]$OutputPath)
$ErrorActionPreference='Stop'
function Require($condition,$message) { if (!$condition) { throw $message } }
Add-Type -AssemblyName System.IO.Compression.FileSystem
$zip=[IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $TensuraJar))
function Entry($name) {
    $e=$zip.GetEntry($name); Require ($null -ne $e) "Missing entry $name"
    $r=[IO.StreamReader]::new($e.Open()); try {$r.ReadToEnd()} finally {$r.Dispose()}
}
try {
    $definition=Entry 'data/tensura/enchantment/energy_steal.json' | ConvertFrom-Json
    $effect=$definition.effects.'tensura:after_damage'[0]
    Require ($effect.enchanted -eq 'attacker' -and $effect.affected -eq 'victim') 'Native targets changed'
    Require ($effect.effect.type -eq 'tensura:energy_steal' -and $effect.effect.cooldown -eq 20 -and $effect.effect.percentage.base -eq 0.01) 'Native effect changed'
    $codes=@{}; $classes=@(foreach($name in @('enchantment.effect.EnergyStealEntity','enchantment.TensuraEnchantmentHelper',
        'enchantment.template.EnchantmentPostDamageEffect','mixin.MixinAbstractArrow','mixin.MixinPlayer',
        'util.EnergyHelper','storage.ep.ExistenceStorage','data.TensuraEntityTags')) {
        $class='io.github.manasmods.tensura.'+$name
        $code=(& (Join-Path $JavaHome 'bin/javap.exe') -p -s -c -classpath $TensuraJar $class) -join "`n"
        Require ($LASTEXITCODE -eq 0) "javap failed: $class"; $codes[$name]=$code
        $stream=$zip.GetEntry($class.Replace('.','/')+'.class').Open()
        try {$hash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant()} finally {$stream.Dispose()}
        [ordered]@{class=$class;sha256=$hash;descriptors=@($code -split "`n" | Where-Object {$_ -match 'descriptor:'} | ForEach-Object {$_.Trim()})}
    })
    foreach($needle in @('bipush        60','isAlive:','isOnCooldown:','addCooldown:', 'drainEnergy:','DrainType.EP','GainType.NORMAL')) {
        Require ($codes['enchantment.effect.EnergyStealEntity'].Contains($needle)) "Effect bytecode changed: $needle"
    }
    foreach($needle in @('hasEnergyDrainImmunity:','ENERGY_PROTECTION','ENERGY_DRAIN_EVENT','GainType','setAura:','setMagicule:','getEP:','ENERGY_DRAIN:','setHealth:')) {
        Require ($codes['util.EnergyHelper'].Contains($needle)) "Helper bytecode changed: $needle"
    }
    Require ($codes['data.TensuraEntityTags'].Contains('String no_current_ep_drain')) 'Exclusion tag mapping changed'
    $arrow=(& (Join-Path $JavaHome 'bin/javap.exe') -p -s -c -classpath $MinecraftJar net.minecraft.world.entity.projectile.AbstractArrow) -join "`n"
    Require ($LASTEXITCODE -eq 0) 'Minecraft javap failed'
    Require ($arrow -match '(?s)298: invokevirtual[^\n]*Entity.hurt:[^\n]*\n\s+301: ifeq\s+609.*391: invokestatic[^\n]*doPostAttackEffectsWithItemSource:') 'Pinned arrow success-branch offsets changed'
    $old=@(Get-Content docs/benchmarks/phase6-endgame-viability/energy_steal.jsonl | ConvertFrom-Json | Where-Object kind -eq row)
    Require ($old.Count -eq 320) 'Historical count changed'
    $admitted=@($old | Where-Object energy_drain_event_count -eq 1)
    $absent=@($old | Where-Object energy_drain_event_count -eq 0)
    Require ($admitted.Count -eq 51 -and $absent.Count -eq 269) 'Historical admission changed'
    Require (@($old | Where-Object physical_damage_event_count -ne 1).Count -eq 0) 'Historical physical observation changed'
    $report=[ordered]@{
        schema='tno.phase6.energy_native_path.static.v1';checkpoint='ES1';status='PASS';runtime_status='PENDING';
        accepted_base='38262bfa99ca4cecd3a2ba58cdb8cc6595893a4c';production_changed=$false;
        artifacts=@(
            @{name='Tensura';version='2.0.1.1';sha256=(Get-FileHash $TensuraJar).Hash.ToLowerInvariant()},
            @{name='NeoForge patched Minecraft';version='21.1.248 / 1.21.1';sha256=(Get-FileHash $MinecraftJar).Hash.ToLowerInvariant()},
            @{name='Royal Variations';file_version='2.0.4';sha256=(Get-FileHash -LiteralPath 'libs/royal-variations-[NeoForge]_1.21.1_2.0.4.jar').Hash.ToLowerInvariant()},
            @{name='L2 Hostility';version='3.0.18';sha256=(Get-FileHash 'run/elemental-runtime-mods/l2hostility-3.0.18.jar').Hash.ToLowerInvariant()});
        definition=$definition;
        tags=@(foreach($n in @('item/handheld_enchantable','item/ranged_enchantable','item/weapon_and_tool_enchantable','entity_type/no_current_ep_drain','entity_type/non_living')) {
            @{path="data/tensura/tags/$n.json";value=(Entry "data/tensura/tags/$n.json" | ConvertFrom-Json)}
        });classes=$classes;
        references=@{
            arrow='AbstractArrow.onHitEntity: bytecode 298 Entity.hurt, 301 ifeq 609, 304-309 Enderman return, 311 LivingEntity, 368 ServerLevel, 391 post effects; Tensura MixinAbstractArrow injects AFTER post effects ordinal 0';
            melee='Tensura MixinPlayer.attack injects AFTER EnchantmentHelper.doPostAttackEffects ordinal 1 on successful primary attack branch; different from after_attack at first attempted hurt';
            source='javap -p -s -c on the hashed installed artifacts; readable local decompilation run/energy-native-source via Vineflower 1.10.1';
            effect_bytecode=$codes['enchantment.effect.EnergyStealEntity'];
            helper_methods=@([regex]::Matches($codes['util.EnergyHelper'],'(?ms)^  public static (?:boolean hasEnergyDrainImmunity|boolean drainEnergy|void gainAura|void gainMagicule)\(.*?(?=^  (?:public|private|protected)|\z)') | ForEach-Object {$_.Value})
        };
        call_graph=@(
            'Actual bow release -> native arrow tick/collision -> AbstractArrow.onHitEntity -> Entity.hurt',
            'hurt true + non-Enderman living victim + server -> EnchantmentHelper.doPostAttackEffectsWithItemSource -> Tensura arrow after_damage hook',
            'arrow weapon nonnull + living owner -> TensuraEnchantmentHelper.doAdditionalAfterDamage',
            'nonempty stack/enchantments + mainhand matchingSlot + AFTER_DAMAGE effect enchanted != VICTIM + conditional damageContext match + affected victim -> EnchantmentPostDamageEffect.apply',
            'EnergyStealEntity.apply(...,float): originalDamage unused -> applyEnergySteal(int,EnchantedItemInUse,Entity)',
            'target invulnerableTime < 60 + alive + LivingEntity -> player weapon cooldown check -> addCooldown(20); nonplayer skips cooldown',
            'existing TNO EnergyStealEntityMixin scales only existing percentage=true, EP, NORMAL drain argument; original called exactly once',
            'EnergyHelper.drainEnergy: positive amount -> multipart head -> immunity -> Energy Protection -> positive amount -> native ENERGY_DRAIN_EVENT',
            'accepted event -> EP current Aura gain-then-subtract, current Magicule gain-then-subtract, at least one corresponding target attribute -> dirty + markHurt',
            'current EP <= 0 and alive -> native energy_drain death source/HP zero/absorption zero/die; otherwise no DamageSource, HP or SHP damage; return true',
            'native true -> notification sound; false -> no sound; player cooldown remains set');
        gates=@{
            physical='Arrow callback requires hurt true, not an independent positive actual HP test. Incoming cancellation and native hurt-false paths prevent it; zero final HP damage alone does not establish rejection. Normal invulnerability comparison may return false; target overrides can do so earlier.';
            callback='server, non-Enderman living victim, living owner, stored weapon with matching mainhand effect; no Energy-specific random chance, affinity, skill, ownership grant, minimum EP or positive originalDamage gate';
            effect='target invulnerableTime >=60, dead, nonliving -> no drain; player item cooldown -> no drain and no new cooldown; otherwise cooldown 20 set BEFORE drain, including when drain later rejects; nonplayer no cooldown';
            immunity='hasInfiniteMaterials; NO_ENERGY_DRAIN maps to no_current_ep_drain; labyrinth PVP off; target != attacker and Anti Skill toggled or present in active preset';
            helper='amount <=0 before or after Energy Protection level*10% reduction; event result false; EP branch has neither MAX_AURA nor MAX_MAGICULE attribute -> false';
            gain='NONE, nonpositive amount, dead attacker or missing corresponding attribute -> no gain; multipart owner resolves to head';
            defenses='No direct matching damage Resistance/Nullification check in drain; their physical-hurt admission remains authoritative. Energy Protection, Anti Skill and entity/game-rule gates apply independently. No new DamageSource or L2 damage event during normal resource transfer.'
        };
        accounting=@{
            percentage='I uses float 0.01 widened to double 0.009999999776482582; Stage S0-S7 multiplies by 1.05..1.40 exactly once before native helper';
            pools='EP drains min(currentAura,currentAura*p) and min(currentMagicule,currentMagicule*p) separately; not max EP, Gear EP or SHP. Native event may modify percentage/type/amount/gain before calculation.';
            caps='NORMAL uses minimum of max attribute and positive spiritual limit. If current <= cap: min(cap,current+drain); if already above cap: current+drain. Existence setters additionally upper-clamp at 2147483647. Target loss does not depend on actual attacker gain.';
            zero='Zero current pools do not by themselves return false: existence of either target max attribute makes EP branch successful even if its drain is zero; sum Aura+Magicule <=0 invokes native depletion death.';
            return='drain true means accepted branch with target attribute, not proof of positive drain or equal transfer. Cooldown is charged before native drain return.'
        };
        historical=@{rows=320;native_events=51;coarse_absent=269;physical_incoming_observed=320;
            absent_with_incoming=269;sha256=(Get-FileHash docs/benchmarks/phase6-endgame-viability/energy_steal.jsonl).Hash.ToLowerInvariant();
            missing_observations=@('actual Entity.hurt return','Energy apply entry','item cooldown at apply','drain entry/return','read-only resource ledger');
            classification='failureReason maps any absent Energy event to PREREQUISITE_HIT_FAILED; this alone does not establish Tank/Dementor/Adaptive causality';
            fixture='Real native Royal Arrow onHitEntity called directly, then discard; unlike Elemental empty overload. Old fixture explicitly empties attacker current pools and ticks FakePlayer cooldown once/server tick.'};
        hypothesis='The old absent-operation label may combine hurt-false, post-hurt target gating, item cooldown, or helper rejection. Reduced HP damage is not sufficient proof. Observe all boundaries before attributing L2 causality.';
        positive_control='Neutral naturally initialized Iron Golem, survival FakePlayer without resource/cap grants, legal vanilla bow + plain arrow, plain versus Energy I, native release/tick/collision. Preserve native crit/owner/stack. Read-only physical/callback/apply/drain/cooldown and HP/SHP/MP/AP ledger. Tick native FakePlayer cooldown as gameplay scheduler, separately from observers; never reset it.';
        next='ES2 native positive control after ES1 commit/push/live verification'
    }
} finally {$zip.Dispose()}
$json=$report|ConvertTo-Json -Depth 30
if($OutputPath) { Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing evidence overwrite'; New-Item -ItemType Directory -Force (Split-Path $OutputPath)|Out-Null; [IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n") }
if(!$OutputPath){$json}else{[pscustomobject]@{status=$report.status;checkpoint=$report.checkpoint;output=$OutputPath;classes=$classes.Count}}
