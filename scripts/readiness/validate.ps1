param(
 [ValidateSet('R1','R2','R3','R4')][string]$Checkpoint='R1',
 [string]$EvidenceDirectory='docs/benchmarks/post-phase6-six-family-readiness',
 [switch]$NoReport
)
$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Resolve-Path "$PSScriptRoot/../..").Path
function Assert($Condition,[string]$Message) { if (-not $Condition) { throw $Message } }
function Git([string[]]$Arguments) {
 $result=& git.exe @Arguments
 Assert ($LASTEXITCODE -eq 0) "git failed: $Arguments"
 return $result
}
function ReadJson([string]$Name) { return Get-Content -Raw -LiteralPath "$EvidenceDirectory/$Name" | ConvertFrom-Json -Depth 100 }
function CheckSchema([string]$Name) {
 Assert (Test-Json -LiteralPath "$EvidenceDirectory/$Name.json" -SchemaFile "$EvidenceDirectory/$Name.schema.json" -ErrorAction Stop) "Schema failed: $Name"
}
$base='d212695c006f503f1b175e4b9a7a57e2f0ebf5ac'
$manifest=ReadJson 'evidence-manifest.json'
Assert ($manifest.source_baseline -eq $base) 'Incorrect accepted baseline'
foreach ($c in $manifest.commits) {
 Git @('cat-file','-e',"$($c.commit)^{commit}") | Out-Null
 Git @('merge-base','--is-ancestor',$c.commit,$base) | Out-Null
}
$indexed=@{}
foreach ($a in $manifest.artifacts) {
 Assert (-not $indexed.ContainsKey($a.path)) "Duplicate artifact: $($a.path)"
 $indexed[$a.path]=$a
 Assert ($a.revision -eq $base) "Wrong revision: $($a.path)"
 Assert ((Git @('rev-parse',"${base}:$($a.path)")) -eq $a.git_blob_sha1) "Wrong blob: $($a.path)"
 Assert ((Git @('hash-object','--',$a.path)) -eq $a.git_blob_sha1) "Evidence/source rewritten: $($a.path)"
 $start=[Diagnostics.ProcessStartInfo]::new('git')
 $start.ArgumentList.Add('cat-file'); $start.ArgumentList.Add('blob'); $start.ArgumentList.Add($a.git_blob_sha1)
 $start.RedirectStandardOutput=$true; $start.UseShellExecute=$false; $start.CreateNoWindow=$true
 $p=[Diagnostics.Process]::Start($start)
 $hash=[Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($p.StandardOutput.BaseStream)).ToLowerInvariant()
 $p.WaitForExit(); Assert ($p.ExitCode -eq 0) 'Blob read failed'; $p.Dispose()
 Assert ($hash -eq $a.git_blob_sha256) "Wrong SHA256: $($a.path)"
}
function CheckReferences($Paths) { foreach ($path in $Paths) { Assert ($indexed.ContainsKey($path)) "Unpinned citation: $path" } }
foreach ($d in $manifest.decision_artifacts) {
 CheckReferences @($d.path)
 if ($d.kind -eq 'JSON') {
  $source=Get-Content -Raw -LiteralPath $d.path | ConvertFrom-Json -Depth 100
  Assert ($source.($d.field) -ceq $d.expected) "Accepted decision mismatch: $($d.family)"
 }
}
$supersession=ReadJson 'supersession-map.json'
Assert ($supersession.findings.Count -ge 7) 'Missing supersession coverage'
foreach ($s in $supersession.findings) { CheckReferences $s.old_sources; CheckReferences $s.new_sources }
$allowed='^(docs/post-phase6-six-family-readiness-assessment\.md|docs/benchmarks/post-phase6-six-family-readiness/|scripts/readiness/)'
foreach ($line in @(Git @('diff','--name-status',$base))) {
 $parts=$line -split "`t"
 Assert ($parts[0] -eq 'A' -and $parts[1] -match $allowed) "Changed accepted file or out-of-scope addition: $line"
}
foreach ($path in @(Git @('ls-files','--others','--exclude-standard'))) { Assert ($path -match $allowed) "Untracked out-of-scope work: $path" }
Git @('diff','--check',$base) | Out-Null
$schemaCount=0
if ($Checkpoint -eq 'R4') {
 CheckSchema 'evidence-manifest'; CheckSchema 'supersession-map'; $schemaCount+=2
 Assert (@($supersession.findings.id | Sort-Object -Unique).Count -eq 9) 'Duplicate supersession'
 # R4 consumes the protected R1-R3 records without modifying their accepted content.
 $protectedR3='5d71569502aec771f49c8f1dbe33154e6f7809b5'
 foreach ($name in @('evidence-manifest.json','supersession-map.json','readiness-matrix.json','readiness-matrix.schema.json','non-interaction-review.json','non-interaction-review.schema.json','r1-validation.json','r2-validation.json','r3-validation.json')) {
  $path="docs/benchmarks/post-phase6-six-family-readiness/$name"
  Assert ((Git @('hash-object','--',$path)) -eq (Git @('rev-parse',"${protectedR3}:$path"))) "Protected R1-R3 record changed: $name"
 }
}
if ($Checkpoint -in @('R2','R3','R4')) {
 CheckSchema 'readiness-matrix'; $schemaCount++
 $matrix=ReadJson 'readiness-matrix.json'
 $families=@('MAGIC','HOLY','SOUL','ELEMENTAL','ENERGY_STEAL','SEVERANCE')
 Assert ((($matrix.families.family | Sort-Object) -join ',') -eq (($families | Sort-Object) -join ',')) 'Families missing or duplicated'
 Assert ($matrix.source_baseline -eq $base) 'Matrix baseline mismatch'
 foreach ($f in $matrix.families) { CheckReferences $f.evidence_sources; foreach ($s in $f.superseded_findings) { Assert ($s -in $supersession.findings.id) "Unknown supersession $s" } }
 Assert (($matrix.families | Where-Object family -eq 'SOUL').resource_channel -contains 'SHP') 'Soul channel lost'
 Assert ((@(($matrix.families | Where-Object family -eq 'ENERGY_STEAL').resource_channel) -join ',') -eq 'MAGICULES,AURA') 'Energy channels conflated'
 Assert (($matrix.families | Where-Object family -eq 'SEVERANCE').production_status -ne 'REJECTED_ARCHITECTURE') 'Candidate C rejection incorrectly applied to production Severance'
 # Cross-check the consolidated counters directly against pinned accepted decisions.
 function CheckCounts($Actual,$Expected,[string]$Family) {
  foreach ($key in $Expected.Keys) { Assert ($Actual.$key -eq $Expected[$key]) "Counter differs from accepted evidence: $Family/$key" }
 }
 $soul=Get-Content -Raw docs/benchmarks/phase6-soul-native-event-path/s4-decision.json | ConvertFrom-Json -Depth 100
 CheckCounts ($matrix.families | Where-Object family -eq 'SOUL').runtime_evidence.counts @{
  royal_releases=$soul.royal_counts.releases;physical_attempts=$soul.royal_counts.physical_attempts;physical_incoming=$soul.royal_counts.physical_incoming;physical_applied=$soul.royal_counts.physical_applied;soul_callbacks=$soul.royal_counts.soul_callbacks;soul_sources=$soul.royal_counts.soul_sources;accepted_spiritual_events=$soul.royal_counts.spiritual_accepted;ordinary_soul_hp_events=$soul.royal_counts.ordinary_soul_hp_incoming;duplicate_deliveries=$soul.validation.duplicate_deliveries
 } 'SOUL'
 $elemental=Get-Content -Raw docs/benchmarks/phase6-elemental-native-event-path/e2-validation.json | ConvertFrom-Json -Depth 100
 CheckCounts ($matrix.families | Where-Object family -eq 'ELEMENTAL').runtime_evidence.counts @{
  cases=$elemental.unique_projectiles;historical_empty_dispatch=$elemental.historical_empty_dispatch_cases;same_projectile_rescues=$elemental.same_projectile_native_path_rescues;native_sources=$elemental.native_source_creations;incoming=$elemental.native_family_events;applied=$elemental.native_family_post_events;matching_nullification=$elemental.nullified_native_family_events;fire_resistance_pre_event=$elemental.native_fire_resistance_pre_event;duplicate_family_events=$elemental.duplicate_family_events
 } 'ELEMENTAL'
 $energy=Get-Content -Raw docs/benchmarks/phase6-energy-steal-physical-prerequisite/es4-final-decision.json | ConvertFrom-Json -Depth 100
 CheckCounts ($matrix.families | Where-Object family -eq 'ENERGY_STEAL').runtime_evidence.counts @{
  strict_rows=$energy.validation.strict_rows;live_attempts=$energy.accepted_live_royal.attempts;live_incoming=$energy.accepted_live_royal.incoming;live_applied_hurt_true=$energy.accepted_live_royal.hurt_true;live_callbacks_apply_drains=$energy.accepted_live_royal.drain;historical_differential_attempts=$energy.historical_differential.attempts;historical_differential_incoming=$energy.historical_differential.incoming;historical_differential_hurt_true_drains=$energy.historical_differential.drain;directly_proven_new_invulnerability_failures=$energy.first_proven_combat_divergence.server_ticks.Count;old_absences_individually_attributed=$energy.historical_reassessment.old_rows_individually_attributed_with_direct_timer_return_evidence;duplicate_drains=$energy.validation.duplicate_drains
 } 'ENERGY_STEAL'
 $candidate=Get-Content -Raw docs/benchmarks/phase6-candidate-c-sustained-viability/v4-decision.json | ConvertFrom-Json -Depth 100
 CheckCounts ($matrix.families | Where-Object family -eq 'SEVERANCE').runtime_evidence.counts @{
  candidate_c_cases=$candidate.official_validation.case_count;candidate_c_releases=$candidate.official_validation.release_count;candidate_c_regenerate_cycles=$candidate.official_validation.Regenerate_events;candidate_c_trajectory_samples=$candidate.official_validation.counts.trajectory
 } 'SEVERANCE/CANDIDATE_C'
}
if ($Checkpoint -in @('R3','R4')) {
 CheckSchema 'non-interaction-review'; $schemaCount++
 $global=ReadJson 'non-interaction-review.json'
 Assert ($global.invariants.Count -eq 14) 'Expected 14 global invariants'
 Assert (@($global.invariants.id | Sort-Object -Unique).Count -eq 14) 'Duplicate invariant'
 foreach ($i in $global.invariants) { CheckReferences $i.evidence_sources }
}
if ($Checkpoint -eq 'R4') {
 CheckSchema 'readiness-decision'; $schemaCount++
 $decision=ReadJson 'readiness-decision.json'
 Assert ($decision.source_baseline -eq $base) 'Decision baseline mismatch'
 Assert ((($decision.six_family_summary.family | Sort-Object) -join ',') -eq (($matrix.families.family | Sort-Object) -join ',')) 'Decision family summary missing or duplicated'
 foreach ($summary in $decision.six_family_summary) {
  $accepted=$matrix.families | Where-Object family -eq $summary.family
  foreach ($field in @('mechanical_status','stage_status','production_status','endgame_status','phase7_blocker')) { Assert ($summary.$field -ceq $accepted.$field) "Decision summary differs from accepted matrix: $($summary.family)/$field" }
  Assert (($summary.known_limitations -join "`n") -ceq ($accepted.known_limitations -join "`n")) "Decision summary limitations differ: $($summary.family)"
 }
 Assert (-not $decision.phase7_started -and -not $decision.phase7_authorized) 'Phase 7 authorization invented'
 Assert (-not $decision.production_changed -and -not $decision.historical_evidence_changed) 'Locked work changed'
 Assert ($decision.candidate_c -eq 'REJECTED_EXHAUSTED') 'Candidate C reopened'
 $owners=@($matrix.families | Where-Object phase7_blocker -eq 'OWNER_DECISION_REQUIRED')
 $blockers=@($matrix.families | Where-Object phase7_blocker -eq 'YES')
 if ($decision.decision -eq 'POST_PHASE6_READY_WITH_OWNER_DECISIONS') { Assert ($owners.Count -gt 0 -and $decision.owner_decisions.Count -gt 0 -and $blockers.Count -eq 0 -and $decision.engineering_blockers.Count -eq 0) 'Owner decision inconsistent with matrix' }
 if ($decision.decision -eq 'POST_PHASE6_READY_FOR_PHASE7') { Assert ($owners.Count -eq 0 -and $blockers.Count -eq 0 -and $decision.owner_decisions.Count -eq 0 -and $decision.engineering_blockers.Count -eq 0) 'Unresolved question marked ready' }
 if ($decision.decision -eq 'POST_PHASE6_NOT_READY_BLOCKED') { Assert ($blockers.Count -gt 0 -and $decision.engineering_blockers.Count -gt 0) 'Weakness mislabeled engineering blocker' }
 foreach ($owner in $decision.owner_decisions) { Assert ($owner.family -eq 'GLOBAL' -or $owner.family -in $owners.family) 'Owner question not reflected in matrix' }
 $build=ReadJson 'build-validation.json'
 Assert ($build.exit_code -eq 0 -and $build.tests -eq 54 -and $build.failures -eq 0 -and $build.errors -eq 0 -and $build.skipped -eq 0) 'Required build did not pass'
 Assert ($build.log_sha256 -eq (Get-FileHash -Algorithm SHA256 -LiteralPath "$EvidenceDirectory/clean-build.log").Hash.ToLowerInvariant()) 'Build log hash mismatch'
 foreach ($sha in $decision.prior_checkpoint_shas.PSObject.Properties.Value) { Git @('cat-file','-e',"${sha}^{commit}") | Out-Null; Git @('merge-base','--is-ancestor',$sha,'HEAD') | Out-Null }
}
$report=[ordered]@{schema='tno.post_phase6.readiness.validation.v1';checkpoint=$Checkpoint;status='PASS';source_baseline=$base;accepted_commits=$manifest.commits.Count;pinned_artifacts=$manifest.artifacts.Count;decisions_checked=$manifest.decision_artifacts.Count;supersessions=$supersession.findings.Count;json_schemas_validated=$schemaCount;production_changed=$false;historical_evidence_changed=$false;new_runtime_experiments=0;diff_check='PASS';limits='Assessment integrity and accepted-artifact verification; no new combat or balance proof'}
if (-not $NoReport) { $report | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 -LiteralPath "$EvidenceDirectory/$($Checkpoint.ToLower())-validation.json" }
$report | ConvertTo-Json -Depth 10
