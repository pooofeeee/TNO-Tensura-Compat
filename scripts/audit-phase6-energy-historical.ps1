param([string]$OutputPath)
$ErrorActionPreference='Stop'
function Require($c,$m){if(!$c){throw $m}}
function Hash($p){(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant()}
$java='C:/Program Files/Java/jdk-21/bin/javap.exe'
$mc='build/moddev/artifacts/neoforge-21.1.248.jar'
$l2='run/elemental-runtime-mods/l2hostility-3.0.18.jar'
$tensura='C:/Users/youra/.gradle/caches/modules-2/files-2.1/maven.modrinth/Br0kXPwc/uw05A7u2/aba444ddc65593bd86a6b618749063efad20add0/Br0kXPwc-uw05A7u2.jar'
$classes=@(
 @($mc,'net.minecraft.server.level.ServerLevel'),@($mc,'net.minecraft.world.entity.LivingEntity'),
 @($mc,'net.neoforged.neoforge.common.world.chunk.ForcedChunkManager'),
 @($l2,'dev.xkmc.l2hostility.content.traits.common.AdaptingTrait'),
 @($tensura,'io.github.manasmods.tensura.effect.ability.SelfRegenerationEffect'))
$bytecode=@{}
foreach($pair in $classes){$code=(& $java -p -s -c -classpath $pair[0] $pair[1]) -join "`n";Require ($LASTEXITCODE -eq 0) "javap $($pair[1])";$bytecode[$pair[1]]=$code}
$world=$bytecode[$classes[0][1]];$living=$bytecode[$classes[1][1]];$adaptive=$bytecode[$classes[3][1]]
Require ($world -match '(?s)Field players:.*ForcedChunkManager.hasForcedChunks:.*resetEmptyTime:.*Field emptyTime:I.*sipush\s+300.*if_icmpge.*entityTickList:') 'World suspension boundary changed'
Require ($living.Contains('Field invulnerableTime:I') -and $living.Contains('Field lastHurt:F') -and $living.Contains('BYPASSES_COOLDOWN')) 'Physical admission authority changed'
Require ($adaptive.Contains('getMsgId:') -and $adaptive.Contains('Math.pow:') -and $adaptive.Contains('adaption:')) 'Adaptive authority changed'
$fixture='src/main/java/com/tno/tensuracompat/debug/Phase5FSuiteBBenchmark.java'
$current=Get-Content $fixture -Raw;$historical=(git show "0cc6005:$fixture") -join "`n"
Require ($LASTEXITCODE -eq 0) 'Historical source missing'
$methodNames=@('spawnCase','createTarget','waitForAttachment','configureLevel','installAcceptedEndgameProfile','waitForScaling','waitForClone','resetActors','beginRun','runCase','closeCurrentHit','fireFullDraw','createPlayer','equipBow','stabilize')
$methods=@(foreach($name in $methodNames){
 $pattern='(?ms)^        private [^\r\n]+\b'+$name+'\([^\r\n]*\).*?(?=^        private |^    \})'
 $oldPattern=if($name -eq 'equipBow'){$pattern.Replace('equipBow','equipBenchmarkBow')}else{$pattern};$old=[regex]::Match($historical,$oldPattern).Value;$now=[regex]::Match($current,$pattern).Value
 Require ($old.Length -gt 0 -and $now.Length -gt 0) "Method audit missing $name"
 @{method=$name;historical_source=$old;current_source=$now;identical_text=($old.Replace("`r",'') -ceq $now.Replace("`r",''))}
})
$observer=Get-Content src/main/java/com/tno/tensuracompat/debug/Phase6EnergyNativePathResearch.java -Raw
Require ($observer.Contains('!FMLEnvironment.production && Boolean.getBoolean("tno.phase6.energyHistorical")')) 'Historical guard missing'
Require ($observer.Contains('if(HISTORICAL_TICKET) { level.setChunkForced(0,1,true);level.getChunk(0,1); }')) 'Single ticket control changed'
Require ($observer.Contains('if(HISTORICAL_TICKET && !active.alreadyForced) active.level.setChunkForced(0,1,false);')) 'Ticket restoration missing'
foreach($op in @('.resetEmptyTime(','.setHealth(','.setMagicule(','.setAura(','.setSpiritualHealth(','.addCooldown(','.removeCooldown(','.setNoAi(','.hurt(','"onHitEntity"')){Require (!$observer.Contains($op)) "Observer/control supplies forbidden mechanic $op"}
Require ($observer -notmatch 'invulnerableTime\s*=(?!=)|\.tickCount\s*=(?!=)') 'Artificial target timer'
Require ([regex]::Matches((git diff b414ffa -- $fixture) -join "`n",'(?m)^\+.*historicalShotBegin').Count -eq 1) 'Historical physical hook inventory'
$lockedDiff=git diff 38262bfa99ca4cecd3a2ba58cdb8cc6595893a4c -- src/main/java/com/tno/tensuracompat/core src/main/java/com/tno/tensuracompat/mixin/EnergyStealEntityMixin.java src/main/java/com/tno/tensuracompat/mixin/AdditionalDamageEntityMixin.java src/main/java/com/tno/tensuracompat/mixin/SpiritualDamageEntityMixin.java src/main/java/com/tno/tensuracompat/mixin/AbstractArrowMixin.java
Require (!$lockedDiff) 'Production changed'
$priorDocs=@(git diff --name-only b414ffa -- docs | Where-Object {$_ -notmatch 'phase6-energy-steal-physical-prerequisite|phase-6-energy-steal-physical-prerequisite-research.md'})
Require ($priorDocs.Count -eq 0) 'Protected prior evidence changed'
$oldPath='docs/benchmarks/phase6-endgame-viability/energy_steal.jsonl'
$oldRows=@([IO.File]::ReadLines([IO.Path]::GetFullPath($oldPath))|ConvertFrom-Json|Where-Object kind -eq row)
Require ($oldRows.Count -eq 320 -and @($oldRows|Where-Object energy_drain_event_count -eq 1).Count -eq 51 -and @($oldRows|Where-Object energy_drain_event_count -eq 0).Count -eq 269) 'Historical evidence changed'
$config='run/config/l2configs/l2hostility-server.toml';Require ((Get-Content $config -Raw) -match 'adaptFactor\s*=\s*0\.5\b') 'Adaptive configuration changed'
$report=[ordered]@{
 schema='tno.phase6.energy_native_path.historical_timing_audit.v1';checkpoint='ES3B';status='PASS';
 original_fixture_commit=(git rev-parse 0cc6005);recovery_checkpoint='b414ffafa67ff989a6e61cbe5eb618a756a9b924';
 artifacts=@(@{name='patched Minecraft';sha256=(Hash $mc)},@{name='Tensura 2.0.1.1';sha256=(Hash $tensura)},@{name='L2 3.0.18';sha256=(Hash $l2)},@{name='L2 server config';sha256=(Hash $config)},@{name='historical 320 rows';sha256=(Hash $oldPath)});
 bytecode=$bytecode;fixture_methods=$methods;
 historical_protocol=@{
  creation='Native entity type create; fresh target for first stage at each level, pristine serialized pre-combat target clone for subsequent stages; addFreshEntity; same target and FakePlayer reused across ten shots';
  initialization='5-tick attachment wait, native L2 reinit and accepted profile, delayed datapack scaling wait and profile reapply; clone uses 5-tick wait';
  resets='Original fixture only: fill pools and HP once at case start, clear target invulnerableTime, empty attacker MP/AP; creative FakePlayer capacity attributes 1e9. No between-shot pool/HP/invulnerability resets';
  schedule='ServerTick.Post stabilizes actors, ticks native FakePlayer cooldown once, releases at first RUN tick and every 20 ticks; 200-tick window, last row observes 19 ticks. Server sprint changes wall time only';
  delivery='Royal Bow releaseUsing(20-tick draw), real single Royal Arrow, native canHitEntity check, historical marking=false and arrow crit=false, final lane, immediate arrow onHitEntity then discard, projectile age 0';
  lifetime='Same mainhand ItemStack reused within case; offhand ammunition refreshed each release; new arrow/source identity each shot; Adaptive data preserved until next case profile initialization';
  native_ticks='No AI disabling in Energy. Target/native AI/L2/regeneration advance only while ServerLevel entity loop runs. Position stabilization does not call target.tick. FakePlayer is absent from ServerLevel.players';
  suspension='NeoForge ServerLevel.tick tests players or ForcedChunkManager.hasForcedChunks; otherwise emptyTime++ < 300 gates entityTickList. Chunk ticking eligibility alone does not imply this world-level loop runs';
  admission='LivingEntity.baseTick decrements invulnerableTime and hurtTime. hurt fires incoming before comparing amount <= lastHurt with invulnerableTime > 10 and no bypass tag; this branch returns false before actuallyHurt/L2 onDamaged/after_damage';
  adaptive='Native source key getMsgId() = arrow; first admitted count 1, later admitted count increments; factor pow(0.5,count-1). Rejected shots do not increment or evaluate this onDamaged modifier';
  control='One legitimate forced target-chunk ticket (0,1), restored to previous state; world native loop stays active. No direct target tick, timer repair, physical bypass, resource grant or Energy invocation introduced';
  comparison_to_ES3A='Accepted ES3a already holds a legitimate forced chunk (80,80), keeps native entity ticks active, uses survival 50-capacity attacker and native projectile tick/collision; real gameplay prerequisite success already protected'
 };
 locked_production_unchanged=$true;prior_evidence_unchanged=$true;
 interpretation='The unchanged two-case baseline crosses the native empty-time boundary. Ticket-only control tests that proven world-loop prerequisite; baseline snapshots were captured before the optional ticket flag was added. No historical evidence is rewritten.'
}
$json=$report|ConvertTo-Json -Depth 30
if($OutputPath){Require (!(Test-Path $OutputPath)) 'Refusing evidence overwrite';[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")};$json
