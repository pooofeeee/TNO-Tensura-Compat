param([Parameter(Mandatory=$true)][string]$TensuraJar,[Parameter(Mandatory=$true)][string]$NebJar,
      [Parameter(Mandatory=$true)][string]$JavaHome,[string]$OutputPath)
$ErrorActionPreference='Stop'
function Code($jar,$class) { $text=(& (Join-Path $JavaHome 'bin/javap.exe') -p -s -c -classpath $jar $class) -join "`n";if($LASTEXITCODE -ne 0){throw "javap failed $class"};$text }
function Require($condition,$message){if(!$condition){throw $message}}
$gazel=Code $TensuraJar 'io.github.manasmods.tensura.entity.human.GazelDwargoEntity'
$neb=Code $NebJar 'io.github.manasmods.tensura_neb.entity.LuminousValentineEntity'
$energy=Code $TensuraJar 'io.github.manasmods.tensura.util.EnergyHelper'
$storage=Code $TensuraJar 'io.github.manasmods.tensura.storage.ep.ExistenceStorage'
$resist=Code $TensuraJar 'io.github.manasmods.tensura.ability.skill.resist.ResistSkill'
Require ($gazel -match '(?s)public boolean hurt.*?bipush\s+80.*?Field invulnerableTime') 'Gazel opening gate changed'
Require ($neb -match '(?s)float 10.0f.*?Method heal:.*?getSpiritualHealth:.*?double 50.0d.*?setSpiritualHealth:') 'NEB paired heal changed'
Require ($energy -match '(?s)public static void gainMagicule.*?MAX_MAGICULE.*?Math.min:.*?setMagicule:') 'Native gain cap changed'
Require ($storage -match '(?s)handleSpiritualHealthRegen.*?SPIRITUAL_HEALTH_REGENERATION.*?setSpiritualHealth:') 'Native SHP regeneration changed'
Require ($resist.Contains('hpDamageBypassResistance') -and $resist.Contains('resistanceDamageMultiplier')) 'Native Resistance config path changed'
$report=[ordered]@{schema='tno.phase6.soul_native_path.comparison_static.v1';status='PASS';
    tensura_sha256=(Get-FileHash -LiteralPath $TensuraJar).Hash.ToLowerInvariant();neb_sha256=(Get-FileHash -LiteralPath $NebJar).Hash.ToLowerInvariant();
    facts=@(
        [ordered]@{class='io.github.manasmods.tensura.entity.human.GazelDwargoEntity';method='hurt(DamageSource,float):boolean';finding='phase 0 opening changes phase to 1, sets target and invulnerableTime=80, returns false before superclass HP events';runtime='physical_return phase 1/cooldown 80, then Soul callback at cooldown 80 and no source'},
        [ordered]@{class='io.github.manasmods.tensura_neb.entity.LuminousValentineEntity';method='tick():void';bytecode='415..433';finding='heal(10) immediately followed by current SHP + 50 setter in non-phase-2 periodic branch; no clamp in this addition';runtime='S3 row 15 has adjacent native NEB HP heal(10) stack and SHP+50; old SHP-only stack filter omitted addon namespace, so attribution combines adjacency and installed bytecode'},
        [ordered]@{class='io.github.manasmods.tensura.util.EnergyHelper';method='gainMagicule(LivingEntity,double,GainType):void';bytecode='NORMAL branch 80..150';finding='native NORMAL gain caps at max Magicule (with limited spiritual max), except when already over cap; drain victim loss can exceed recipient gain';scope='Incidental Luminous AI accounting only; not Energy Steal engraving research'},
        [ordered]@{class='io.github.manasmods.tensura.storage.ep.ExistenceStorage';method='handleSpiritualHealthRegen(MinecraftServer,LivingEntity,IExistence):void';finding='native SHP regeneration attribute with maximum clamp'},
        [ordered]@{class='io.github.manasmods.tensura.effect.ability.InstantRegenerationEffect';method='applyEffectTick(LivingEntity,int):boolean / healSHP(LivingEntity,IExistence,double,double,double):void';finding='native SHP healing may consume Magicule; separate from Soul effect'},
        [ordered]@{class='io.github.manasmods.tensura.ability.skill.resist.ResistSkill';method='native event handling';finding='matching physical Resistance uses configured HP damage threshold; Hinata active physical Resistance cancels ordinary physical incoming. Her separate direct spiritual Resistance gate is audited in S1.'}
    );production_changed=$false}
$json=$report|ConvertTo-Json -Depth 15
if($OutputPath){Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing to overwrite evidence';[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")}
$json
