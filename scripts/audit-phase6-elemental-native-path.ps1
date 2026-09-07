param(
    [Parameter(Mandatory=$true)][string]$TensuraJar,
    [Parameter(Mandatory=$true)][string]$MinecraftJar,
    [Parameter(Mandatory=$true)][string]$JavaHome,
    [switch]$IncludeFireGuard,
    [string]$OutputPath
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.IO.Compression.FileSystem
$javap = Join-Path $JavaHome 'bin/javap.exe'
function Inspect-Class([string]$Jar, [string]$Name) {
    $lines = & $javap -p -c -classpath $Jar $Name
    if ($LASTEXITCODE -ne 0) { throw "javap failed: $Name" }
    return $lines -join "`n"
}
function Require([bool]$Condition,[string]$Message) {
    if (!$Condition) { throw $Message }
}
$baseName = 'io.github.manasmods.tensura.entity.'
$base = Inspect-Class $TensuraJar ($baseName + 'TensuraProjectile')
$flying = Inspect-Class $TensuraJar ($baseName + 'projectile.TensuraFlyingProjectile')
$vanilla = Inspect-Class $MinecraftJar 'net.minecraft.world.entity.projectile.Projectile'
Require ($vanilla -match 'Method onHitEntity:\(Lnet/minecraft/world/phys/EntityHitResult;\)V') 'Vanilla dispatch changed'
Require ($vanilla -match 'protected void onHitEntity\(net.minecraft.world.phys.EntityHitResult\);\s+Code:\s+0: return') 'Vanilla callback no longer empty'
Require ($flying -match 'Method onHitEntity:\(Lnet/minecraft/world/phys/EntityHitResult;Lio/github/manasmods/manascore/skill/api/EntityEvents\$ProjectileHitResult;\)V') 'Native flight dispatch changed'
Require ($flying -match 'EntityEvents.PROJECTILE_HIT') 'Native event gate missing'
$single = '(?m)^  (public|protected) void onHitEntity\(net.minecraft.world.phys.EntityHitResult\);'
Require (!($base -match $single) -and !($flying -match $single)) 'Tensura base now overrides single-argument callback'
$zip = [IO.Compression.ZipFile]::OpenRead((Resolve-Path -LiteralPath $TensuraJar))
try {
    $elements = @('Earth','Fire','Space','Water','Wind')
    $classes = @('StoneShotProjectile','FireBoltProjectile','SpaceCutProjectile','WaterBallProjectile','WindSphereProjectile')
    $audit = for ($i=0; $i -lt 5; $i++) {
        $name = $baseName + 'projectile.magic.' + $classes[$i]
        $code = Inspect-Class $TensuraJar $name
        Require (!($code -match $single)) "Unexpected single-argument override: $name"
        $entry = $zip.GetEntry(($name.Replace('.','/')) + '.class')
        $stream = $entry.Open()
        try { $hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($stream)).ToLowerInvariant() }
        finally { $stream.Dispose() }
        $reader = [IO.StreamReader]::new($zip.GetEntry("data/tensura/slotting/combination_$($i+1).json").Open())
        try { $combination = $reader.ReadToEnd() | ConvertFrom-Json }
        finally { $reader.Dispose() }
        [ordered]@{element=$elements[$i];class=$name;class_sha256=$hash;
            single_argument_override=$false;
            custom_two_argument_override=($code -match 'protected void onHitEntity\(net.minecraft.world.phys.EntityHitResult,');
            constructor_sets_elemental_attack=($code -match 'Method setElementalAttack:');
            combination=$combination}
    }
}
finally { $zip.Dispose() }
$old = @(Get-Content docs/benchmarks/phase6-endgame-viability/elemental_slotting.jsonl | ConvertFrom-Json | Where-Object kind -eq 'row')
$preflight = @(Get-Content docs/benchmarks/phase6-preflight-elemental-positive-control.jsonl | ConvertFrom-Json | Where-Object kind -eq 'row')
Require ($old.Count -eq 320) 'Historical matrix count changed'
Require (@($old | Where-Object failure_reason -eq 'NATIVE_EVENT_ABSENT').Count -eq 320) 'Historical absence changed'
Require ($preflight.Count -eq 90) 'Preflight row count changed'
$report = [ordered]@{
    schema='tno.phase6.elemental_native_path.static.v1'; checkpoint='E1'; status='PASS';
    source_head='b50061eb9040474a7fb8bdeb780f46a30201d63f';
    tensura_sha256=(Get-FileHash -LiteralPath $TensuraJar).Hash.ToLowerInvariant();
    minecraft_development_sha256=(Get-FileHash -LiteralPath $MinecraftJar).Hash.ToLowerInvariant();
    vanilla_dispatch='Projectile.onHit(HitResult) -> onHitEntity(EntityHitResult): empty return';
    native_dispatch='TensuraFlyingProjectile.tickHandler -> canHitEntity -> EntityEvents.PROJECTILE_HIT -> onHitEntity(EntityHitResult, ProjectileHitResult)';
    native_damage='applyHitEntity -> hitEntity -> dealDamage(Entity,float,float) -> native getDamageSource -> target.hurt';
    historical_dispatch='Phase5FSuiteBBenchmark.Session.dispatchSlottingProjectile -> onHit(EntityHitResult) -> immediate capture -> discard';
    historical_absent_rows=$old.Count; historical_preflight_rows=$preflight.Count;
    elements=@($audit); runtime_status='PENDING'; production_changed=$false
}
$json = $report | ConvertTo-Json -Depth 20
if ($IncludeFireGuard) {
    $living = Inspect-Class $MinecraftJar 'net.minecraft.world.entity.LivingEntity'
    $hurt = [regex]::Match($living, '(?s)public boolean hurt\(net.minecraft.world.damagesource.DamageSource, float\);.*?(?=\n  (public|protected|private) )').Value
    Require ($hurt -match '(?s)DamageTypeTags.IS_FIRE:.*?MobEffects.FIRE_RESISTANCE:.*?Method hasEffect:.*?iconst_0\s+\d+: ireturn') 'Native Fire Resistance rejection changed'
    Require ($hurt.IndexOf('CommonHooks.onEntityIncomingDamage:') -gt $hurt.IndexOf('MobEffects.FIRE_RESISTANCE:')) 'Incoming event no longer follows Fire Resistance gate'
    $report['checkpoint'] = 'E2'; $report['schema'] = 'tno.phase6.elemental_native_path.static.v2'
    $report['fire_guard'] = 'LivingEntity.hurt: IS_FIRE && FIRE_RESISTANCE -> false, before CommonHooks.onEntityIncomingDamage'
    $json = $report | ConvertTo-Json -Depth 20
}
if ($OutputPath) {
    if (Test-Path -LiteralPath $OutputPath) { throw 'Refusing to overwrite evidence' }
    New-Item -ItemType Directory -Force (Split-Path $OutputPath) | Out-Null
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath), $json + "`n")
}
$json
