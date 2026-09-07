param([string]$OutputPath, [string]$Check)
$ErrorActionPreference = 'Stop'
$baseline = 'b50061eb9040474a7fb8bdeb780f46a30201d63f'
$e2 = 'db8d2583085aa7bd9ff6580adba70f271b97633f'
$directory = 'docs/benchmarks/phase6-elemental-native-event-path'
function Require([bool]$Condition, [string]$Message) { if (!$Condition) { throw $Message } }
$validation = (& (Join-Path $PSScriptRoot 'extract-phase6-elemental-native-path.ps1') -LogPath "$directory/e2-runtime.jsonl") | ConvertFrom-Json
Require ($validation.status -ceq 'PASS') 'Runtime revalidation failed'
$rows = @(Get-Content "$directory/e2-runtime.jsonl" | ConvertFrom-Json | Where-Object kind -eq row)
$results = foreach ($element in @('earth','fire','space','water','wind')) {
    $selected = @($rows | Where-Object element -eq $element)
    $source = "tensura:${element}_elemental"
    $traces = @($selected | ForEach-Object traces | Where-Object source -eq $source)
    $calls = @($traces | Where-Object boundary -eq native_hurt_call)
    $neutralFree = $selected | Where-Object { $_.target -eq 'neutral' -and $_.mode -eq 'royal_free' }
    Require (@($neutralFree.traces | Where-Object { $_.source -eq $source -and $_.boundary -eq 'damage_post' }).Count -eq 1) "Missing untouched Royal positive control: $element"
    [ordered]@{
        element=$element;projectile=$selected[0].projectile;source=$source;cases=$selected.Count
        historical_empty_dispatch=@($selected | Where-Object mode -eq royal_legacy).Count
        native_source_creations=$calls.Count
        incoming_events=@($traces | Where-Object boundary -eq incoming_highest).Count
        applied_events=@($traces | Where-Object boundary -eq damage_post).Count
        matching_nullification=@($traces | Where-Object { $_.boundary -eq 'incoming_lowest' -and $_.canceled }).Count
        fire_resistance_pre_event=@($calls | Where-Object { $_.source_is_fire -and $_.target_fire_resistance }).Count
        untouched_royal_neutral_positive_control=$true
        production_prerequisite_fix_indicated=$false
    }
}
$allowedModified = @('build.gradle','src/main/java/com/tno/tensuracompat/TNOTensuraCompat.java','src/main/resources/tno_tensura_compat.mixins.json')
$modified = @(git diff --name-only --diff-filter=MD $baseline --)
Require (@($modified | Where-Object { $_ -notin $allowedModified }).Count -eq 0) 'Locked existing source or historical evidence changed'
$allowedAddedJava = @('src/main/java/com/tno/tensuracompat/debug/Phase6ElementalNativePathResearch.java','src/main/java/com/tno/tensuracompat/mixin/ElementalDamageObservationMixin.java','src/main/java/com/tno/tensuracompat/mixin/ElementalFlyingObservationMixin.java','src/main/java/com/tno/tensuracompat/mixin/ElementalVanillaObservationMixin.java')
$addedJava = @(git diff --name-only --diff-filter=A $baseline -- src/main/java)
Require (@($addedJava | Where-Object { $_ -notin $allowedAddedJava }).Count -eq 0) 'Unexpected new Java implementation'
$blobs = foreach ($file in @(git ls-tree -r --name-only $e2 -- $directory)) {
    $committed = git rev-parse "${e2}:$file"
    $working = git hash-object -- $file
    Require ($LASTEXITCODE -eq 0 -and $committed -ceq $working) "Protected evidence changed: $file"
    [ordered]@{file=$file;git_blob=$committed;unchanged=$true}
}
$provenance = Get-Content "$directory/e2-provenance.json" -Raw | ConvertFrom-Json
$tests = $provenance.tests | Measure-Object tests -Sum
Require ($tests.Sum -eq 54 -and @($provenance.tests | Where-Object { $_.failures -ne 0 -or $_.errors -ne 0 }).Count -eq 0) 'Invalid Java validation evidence'
$negative = Get-Content "$directory/e2-extractor-tests.json" -Raw | ConvertFrom-Json
Require ($negative.status -ceq 'PASS' -and $negative.negative_tests -eq 8) 'Invalid extractor corruption evidence'
$report = [ordered]@{
    schema='tno.phase6.elemental_native_path.decision.v1';checkpoint='E3';status='COMPLETE'
    source_e2=$e2;source_baseline=$baseline
    decision='HISTORICAL_HARNESS_DISPATCH_DEFECT; NO_PRODUCTION_NATIVE_PATH_FIX_INDICATED'
    first_missing_prerequisite='Native tickHandler collision dispatch through the two-argument Tensura callback; historical onHit invokes an inherited empty one-argument overload and immediately discards the projectile'
    earth_causal_proof='Same projectile survives the empty historical call and creates its native source when ordinary ticking resumes; untouched vanilla/Royal flight agrees'
    results=@($results)
    safe_research_correction='Let legitimately released projectiles tick; observe native collision results and distinguish source creation, incoming event dispatch, and applied damage'
    production_fix_possible='No missing production prerequisite was demonstrated; Fire Resistance and matching Nullification are authoritative defenses, not safe fix targets'
    production_prototype_implemented=$false;production_implementation_authorized=$false
    scope_limits=@('Single-core, single-release cases; neutral adapter and two initialized Lv1000 boss profiles only','Survival FakePlayer fixture; no human-client multiplayer acceptance','Temporary pre-profile L2 effects remain visible; no innate Orc fire immunity or exact endgame balance claim','No full boss roster, multi-core, sustained viability or active PASS/HIT_NO_DAMAGE veto matrix')
    historical_interpretation='Original absent-event rows remain unchanged, but their boss-unavailability attribution cannot be inferred from the empty dispatch; the removed pre-flight implementation is not reconstructed'
    validation=[ordered]@{runtime='PASS';cases=90;native_source_creations=$validation.native_source_creations;native_family_events=$validation.native_family_events;native_family_post_events=$validation.native_family_post_events;native_fire_resistance_pre_event=$validation.native_fire_resistance_pre_event;nullified_native_family_events=$validation.nullified_native_family_events;java_build='PASS';java_tests=[int]$tests.Sum;extractor_negative_tests=8;locked_existing_combat_and_evidence_unchanged=$true;protected_evidence=@($blobs)}
    checkpoints=[ordered]@{E1='57d733755bca4acafa995e42a498f69e7b504dbe';E2a='c4b2c47b33574f0cdc8d16ec41bf3b4f36a15780';E2=$e2}
    candidate_c='REJECTED_EXHAUSTED';stage_framework='COMPLETE_LOCKED';magic_holy='COMPLETE_LOCKED';original_phase7='NOT_STARTED'
    exact_next_task='Owner review of E3 Elemental findings. If accepted and separately authorized, Soul Eater native soul_scatter eligibility research; do not start permanent production or another family automatically.'
}
$json = $report | ConvertTo-Json -Depth 14
if ($Check) {
    $saved = Get-Content -LiteralPath $Check -Raw | ConvertFrom-Json | ConvertTo-Json -Depth 14
    Require ($saved -ceq $json) 'Decision does not reproduce exactly'
}
if ($OutputPath) {
    Require (!(Test-Path -LiteralPath $OutputPath)) 'Refusing to overwrite decision'
    [IO.File]::WriteAllText([IO.Path]::GetFullPath($OutputPath), $json + "`n")
}
[pscustomobject]$report | Select-Object status,decision,results,exact_next_task | ConvertTo-Json -Depth 8
