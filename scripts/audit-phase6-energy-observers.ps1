param([string]$OutputPath)
$ErrorActionPreference='Stop'
function Require($condition,$message){if(!$condition){throw $message}}
$runnerPath='src/main/java/com/tno/tensuracompat/debug/Phase6EnergyNativePathResearch.java';$runner=Get-Content $runnerPath -Raw
Require ($runner.Contains('!FMLEnvironment.production && Boolean.getBoolean("tno.phase6.energyNativePath")')) 'Missing opt-in guard'
foreach($forbidden in @('EnergyHelper.drainEnergy(','.applyEnergySteal(','.setHealth(','.setMagicule(','.setAura(','.setSpiritualHealth(','.addCooldown(','.removeCooldown(','.setCritArrow(','.setBaseDamage(')){
    Require (!$runner.Contains($forbidden)) "Fixture contains unauthorized operation $forbidden"
}
Require (!$runner.Contains('"onHitEntity"') -and !$runner.Contains('"setMarking"')) 'Manual collision/Mark mutation'
Require ($runner.Contains('player.getCooldowns().tick();')) 'Missing native FakePlayer clock scheduler'
$paths=@($runnerPath,'build.gradle','src/main/java/com/tno/tensuracompat/TNOTensuraCompat.java','src/main/resources/tno_tensura_compat.mixins.json')
$mixins=@(Get-ChildItem src/main/java/com/tno/tensuracompat/mixin/Energy*ObservationMixin.java)
Require ($mixins.Count -eq 7) 'Observer inventory changed'
foreach($file in $mixins){
    $code=Get-Content $file.FullName -Raw
    Require ($code -notmatch 'cancellable\s*=\s*true|\.cancel\(|\.setReturnValue\(|\.setAmount\(|\.setHealth\(|\.setMagicule\(|\.setAura\(|\.addCooldown\(') "Mutable observer $($file.Name)"
    if($file.Name -eq 'EnergyArrowObservationMixin.java'){Require ([regex]::Matches($code,'original.call\(').Count -eq 1 -and $code.Contains('return result;')) 'Physical original call changed'}
    $paths+=$file.FullName
}
$locked=@('src/main/java/com/tno/tensuracompat/core','src/main/java/com/tno/tensuracompat/mixin/EnergyStealEntityMixin.java','src/main/java/com/tno/tensuracompat/mixin/AdditionalDamageEntityMixin.java','src/main/java/com/tno/tensuracompat/mixin/SpiritualDamageEntityMixin.java','src/main/java/com/tno/tensuracompat/mixin/AbstractArrowMixin.java')
$diff=git diff 38262bfa99ca4cecd3a2ba58cdb8cc6595893a4c -- $locked
Require (!$diff) 'Locked production diff'
$testFiles=@(Get-ChildItem build/test-results/test/TEST-*.xml)
$tests=0;$failures=0;$errors=0;$skipped=0
foreach($f in $testFiles){$x=[xml](Get-Content $f.FullName -Raw);$tests+=[int]$x.testsuite.tests;$failures+=[int]$x.testsuite.failures;$errors+=[int]$x.testsuite.errors;$skipped+=[int]$x.testsuite.skipped}
Require ($tests -gt 0 -and $failures -eq 0 -and $errors -eq 0 -and $skipped -eq 0) 'Unit tests not passing'
$report=[ordered]@{schema='tno.phase6.energy_native_path.observer_audit.v1';status='PASS';opt_in_only=$true;read_only_observers=$true;physical_original_calls=1;locked_production_unchanged=$true;
    unit_tests=@{tests=$tests;failures=$failures;errors=$errors;skipped=$skipped};files=@(foreach($p in $paths){@{path=[IO.Path]::GetRelativePath((Get-Location).Path,[IO.Path]::GetFullPath($p)).Replace('\','/');sha256=(Get-FileHash -LiteralPath $p).Hash.ToLowerInvariant()}})}
$json=$report|ConvertTo-Json -Depth 20
if($OutputPath){Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing evidence overwrite';[IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath),$json+"`n")};$json
