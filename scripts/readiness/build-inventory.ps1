param([string]$Repository = (Resolve-Path "$PSScriptRoot/../..").Path)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $Repository
$base = 'd212695c006f503f1b175e4b9a7a57e2f0ebf5ac'
$out = 'docs/benchmarks/post-phase6-six-family-readiness'
New-Item -ItemType Directory -Force -Path $out | Out-Null
function Git([string[]]$Arguments) {
    $result = & git.exe @Arguments
    if ($LASTEXITCODE -ne 0) { throw "git failed: $Arguments" }
    return $result
}
function BlobHash([string]$Blob) {
    $start = [Diagnostics.ProcessStartInfo]::new('git')
    $start.ArgumentList.Add('cat-file'); $start.ArgumentList.Add('blob'); $start.ArgumentList.Add($Blob)
    $start.RedirectStandardOutput = $true; $start.UseShellExecute = $false; $start.CreateNoWindow = $true
    $process = [Diagnostics.Process]::Start($start)
    $hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($process.StandardOutput.BaseStream)).ToLowerInvariant()
    $process.WaitForExit()
    if ($process.ExitCode -ne 0) { throw "Missing blob $Blob" }
    $process.Dispose()
    return $hash
}
$branches = @(
 'phase-6-production-stage-framework', 'phase-6-preflight-elemental-positive-control',
 'phase-6-post-endgame-viability-research', 'phase-6-endgame-effectiveness-calibration',
 'phase-6-endgame-magic-holy-production', 'phase-6-severance-regenerate-research',
 'phase-6-regenerate-adaptive-wound-architecture-research', 'phase-6-regenerate-severance-counter-protocol-research',
 'phase-6-candidate-c-sustained-viability-research', 'phase-6-elemental-native-event-path-research',
 'phase-6-soul-native-event-path-research', 'phase-6-energy-steal-physical-prerequisite-research'
)
$commits = @($branches | ForEach-Object {
    $sha = Git @('rev-parse', $_)
    Git @('merge-base', '--is-ancestor', $sha, $base) | Out-Null
    [ordered]@{branch=$_; commit=$sha; ancestor_of_source_baseline=$true}
})
$paths = @(Git @('ls-tree','-r','--name-only',$base) | Where-Object {
    $_ -match '^docs/phase-6-(production-implementation|preflight-elemental-positive-control|endgame-viability-research|endgame-effectiveness-calibration|endgame-magic-holy-production|severance-regenerate-research|regenerate-adaptive-wound-architecture-research|regenerate-severance-counter-protocol-research|candidate-c-sustained-viability-research|elemental-native-event-path-research|soul-native-event-path-research|energy-steal-physical-prerequisite-research)\.md$' -or
    ($_ -match '^docs/benchmarks/phase6-' -and $_ -notmatch 'diagnostic|startup-control') -or
    $_ -match '^src/main/java/com/tno/tensuracompat/(core|compat)/' -or
    $_ -match '^src/main/java/com/tno/tensuracompat/mixin/(AbstractArrow|AdditionalDamageEntity|EnergyStealEntity|GearHandler|SeveranceDamageEntity|SlottingHelper|SpiritualDamageEntity|TensuraProjectile)Mixin.java$'
} | Sort-Object -Unique)
$artifacts = @($paths | ForEach-Object {
    $blob = Git @('rev-parse', "${base}:$_")
    if ((Git @('hash-object', '--', $_)) -ne $blob) { throw "Working copy differs: $_" }
    [ordered]@{path=$_; revision=$base; git_blob_sha1=$blob; git_blob_sha256=(BlobHash $blob); role=$(if ($_ -match '^src/') {'production_source'} elseif ($_ -match '^docs/phase-6') {'accepted_document_with_checkpoint_history'} elseif ($_ -match 'phase6-endgame-viability|r3-physical-wall|r4-proportional|w4-trait') {'historical_interpretation_requires_supersession_map'} else {'accepted_or_supporting_artifact_read_in_checkpoint_context'})}
})
$manifest = [ordered]@{
 schema='tno.post_phase6.readiness.provenance.v1'; checkpoint='R1'; source_baseline=$base
 recovery=[ordered]@{working_tree='CLEAN'; fetched=$true; live_energy_sha=$base; newer_energy_work=$false; readiness_work_found=$false; new_branch='post-phase6-six-family-readiness-assessment'; applicable_agents='NONE_FOUND_IN_REPOSITORY_OR_ANCESTORS'; original_phase7='NOT_STARTED'}
 hash_semantics='SHA-256 is over immutable raw Git blob bytes; git_blob_sha1 is Git object identity. Working copies are compared using git hash-object with repository attributes, allowing checkout line endings. No runtime blob is copied.'
 commits=$commits; artifacts=$artifacts
 native_authority=[ordered]@{tensura_version='2.0.1.1'; jar_sha256='c12ec9aaa1488c662ede52b4bd0150ec114e7bdac32af20c0e723612dd79d8b9'; authority='Accepted installed-artifact bytecode audits, especially e1-static.json, s1-native-path-audit.json, es1-native-path-audit.json and es3b-historical-timing-audit.json'; l2_version='3.0.18'; native_runtime_repeated=$false}
 decision_artifacts=@(
  @{family='MAGIC';path='docs/phase-6-endgame-magic-holy-production.md';kind='DOCUMENT_AND_P5_RAW';note='No separate final-decision JSON was published; production document and benchmark README govern P5 acceptance'},
  @{family='HOLY';path='docs/phase-6-endgame-magic-holy-production.md';kind='DOCUMENT_AND_P5_RAW';note='Shared production policy; independently captured native family'},
  @{family='SEVERANCE';path='docs/phase-6-severance-regenerate-research.md';kind='DOCUMENT_AND_R5_RAW';note='Current production is distinct from rejected Candidate C'},
  @{family='ELEMENTAL';path='docs/benchmarks/phase6-elemental-native-event-path/e3-decision.json';field='decision';expected='HISTORICAL_HARNESS_DISPATCH_DEFECT; NO_PRODUCTION_NATIVE_PATH_FIX_INDICATED';kind='JSON'},
  @{family='SOUL';path='docs/benchmarks/phase6-soul-native-event-path/s4-decision.json';field='decision';expected='SOUL_NATIVE_PATH_VALID_NO_FIX';kind='JSON'},
  @{family='ENERGY_STEAL';path='docs/benchmarks/phase6-energy-steal-physical-prerequisite/es4-final-decision.json';field='decision';expected='ENERGY_NATIVE_PATH_VALID_NO_FIX';kind='JSON'},
  @{family='CANDIDATE_C_OPTIONAL_ARCHITECTURE';path='docs/benchmarks/phase6-candidate-c-sustained-viability/v4-decision.json';field='terminal_decision';expected='CANDIDATE_C_REJECTED';kind='JSON'},
  @{family='REGENERATE_COUNTER_PROTOCOL';path='docs/benchmarks/phase6-regenerate-severance-counter-protocol/p4-decision.json';field='outcome';expected='OUTCOME_1_HARD_DYNAMIC_COUNTER_VALID';kind='JSON'}
 )
 coverage_notes=@('Inventory membership is not a blanket runtime PASS: checkpoint context, supersession and cited scope control each claim.', 'Original foundation 6F raw temporary captures/harness were not retained in Git; its 29-case/89-row acceptance and APO case are document-level evidence.', 'Excluded diagnostic and startup-control files remain untouched in the source baseline; they are not decisive acceptance evidence.', 'Historical next-task fields are checkpoint-local history; later accepted commits and the current owner request supersede them.')
}
$manifest | ConvertTo-Json -Depth 15 | Set-Content -Encoding utf8 -LiteralPath "$out/evidence-manifest.json"
Write-Output "Inventoried $($artifacts.Count) immutable artifacts and $($commits.Count) accepted branch checkpoints."
