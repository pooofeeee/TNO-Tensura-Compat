$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Resolve-Path "$PSScriptRoot/../..").Path
$original='docs/benchmarks/post-phase6-six-family-readiness'
# Copies only small assessment records into a new ignored run directory. No historical data is mutated.
$temporary=Join-Path 'run' ('readiness-validator-' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $temporary | Out-Null
$tests=@(
 @{name='wrong_source_baseline';file='evidence-manifest.json';mutate={param($j) $j.source_baseline='0000000000000000000000000000000000000000'};expected='Incorrect accepted baseline'},
 @{name='wrong_immutable_blob_hash';file='evidence-manifest.json';mutate={param($j) $j.artifacts[0].git_blob_sha256='0'*64};expected='Wrong SHA256'},
 @{name='missing_commit';file='evidence-manifest.json';mutate={param($j) $j.commits[0].commit='0'*40};expected='git failed'},
 @{name='altered_accepted_decision';file='evidence-manifest.json';mutate={param($j) ($j.decision_artifacts|Where-Object family -eq 'SOUL').expected='SOUL_FIX_REQUIRED'};expected='Accepted decision mismatch'},
 @{name='missing_family';file='readiness-matrix.json';mutate={param($j) $j.families=@($j.families | Where-Object family -ne 'HOLY')};expected='schema|Schema'},
 @{name='duplicate_family';file='readiness-matrix.json';mutate={param($j) $j.families[1].family='MAGIC'};expected='Families missing or duplicated'},
 @{name='unpinned_citation';file='readiness-matrix.json';mutate={param($j) $j.families[0].evidence_sources[0]='docs/not-a-source.json'};expected='Unpinned citation'},
 @{name='energy_as_hp';file='readiness-matrix.json';mutate={param($j) ($j.families|Where-Object family -eq 'ENERGY_STEAL').resource_channel=@('HP')};expected='Energy channels conflated'},
 @{name='candidate_rejection_applied_to_production';file='readiness-matrix.json';mutate={param($j) ($j.families|Where-Object family -eq 'SEVERANCE').production_status='REJECTED_ARCHITECTURE'};expected='Candidate C rejection incorrectly'},
 @{name='forged_soul_event_count';file='readiness-matrix.json';mutate={param($j) ($j.families|Where-Object family -eq 'SOUL').runtime_evidence.counts.accepted_spiritual_events=13};expected='Counter differs'},
 @{name='old_energy_absences_falsely_attributed';file='readiness-matrix.json';mutate={param($j) ($j.families|Where-Object family -eq 'ENERGY_STEAL').runtime_evidence.counts.old_absences_individually_attributed=269};expected='Counter differs'},
 @{name='invalid_proof_classification';file='non-interaction-review.json';mutate={param($j) $j.invariants[0].classification='UNIVERSALLY_PROVEN'};expected='schema|Schema'},
 @{name='phase7_auto_authorized';file='readiness-decision.json';mutate={param($j) $j.phase7_authorized=$true};expected='schema|Schema|authorization'},
 @{name='ready_despite_owner_question';file='readiness-decision.json';mutate={param($j) $j.decision='POST_PHASE6_READY_FOR_PHASE7'};expected='Unresolved question marked ready'},
 @{name='weakness_as_engineering_blocker';file='readiness-decision.json';mutate={param($j) $j.decision='POST_PHASE6_NOT_READY_BLOCKED'};expected='Weakness mislabeled engineering blocker'},
 @{name='invalid_manifest_role';file='evidence-manifest.json';mutate={param($j) $j.artifacts[0].role='UNCONDITIONAL_RUNTIME_PASS'};expected='schema|Schema'},
 @{name='duplicate_supersession';file='supersession-map.json';mutate={param($j) $j.findings[1].id=$j.findings[0].id};expected='Duplicate supersession'},
 @{name='decision_summary_drift';file='readiness-decision.json';mutate={param($j) $j.six_family_summary[0].production_status='UNRESOLVED_BLOCKER'};expected='Decision summary differs'},
 @{name='missing_supersession_reference';file='readiness-decision.json';mutate={param($j) $j.PSObject.Properties.Remove('superseded_findings_reference')};expected='schema|Schema'}
)
& "$PSScriptRoot/validate.ps1" -Checkpoint R4 -NoReport | Out-Null
$results=@()
foreach ($test in $tests) {
 $folder=Join-Path $temporary $test.name
 New-Item -ItemType Directory -Path $folder | Out-Null
 Get-ChildItem -LiteralPath $original -File | Where-Object { $_.Extension -in @('.json','.log') } | ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $folder }
 $file=Join-Path $folder $test.file
 $json=Get-Content -Raw -LiteralPath $file | ConvertFrom-Json -Depth 100
 & $test.mutate $json
 $json|ConvertTo-Json -Depth 100|Set-Content -Encoding utf8 -LiteralPath $file
 $reason=$null
 try { & "$PSScriptRoot/validate.ps1" -Checkpoint R4 -EvidenceDirectory $folder -NoReport | Out-Null } catch { $reason=$_.Exception.Message }
 if (-not $reason -or $reason -notmatch $test.expected) { throw "Unexpected test outcome for $($test.name): $reason" }
 $results += [ordered]@{mutation=$test.name;rejected=$true;reason=$reason}
 Write-Output "PASS corruption $($results.Count)/$($tests.Count): $($test.name)"
}
[ordered]@{schema='tno.post_phase6.readiness.validator_tests.v1';checkpoint='R4';status='PASS';positive_control='PASS';negative_tests=$results.Count;tests=$results;temporary_copies=$temporary;historical_evidence_mutated=$false;scope='Assessment schema/provenance/counter consolidation and decision logic only; no new combat extractor or runtime experiment'} | ConvertTo-Json -Depth 12 | Set-Content -Encoding utf8 -LiteralPath "$original/validator-corruption-tests.json"
