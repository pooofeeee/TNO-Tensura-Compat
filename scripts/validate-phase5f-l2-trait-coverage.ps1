param(
    [string]$CoveragePath = "docs/benchmarks/phase5f-l2-traits/coverage.jsonl",
    [string]$CatalogEvidencePath = "docs/benchmarks/phase5f-l2-traits/forced/luminous_valentine.jsonl",
    [string]$NaturalEvidenceDirectory = "docs/benchmarks/phase5f-l2-traits/natural",
    [string]$ProfileEvidenceDirectory = "docs/benchmarks/phase5f-l2-traits/profiles"
)

$ErrorActionPreference = "Stop"

function Assert-Condition {
    param([bool]$Condition, [string]$Message)
    if (-not $Condition) {
        throw $Message
    }
}

$allowedTerminalClasses = @(
    "LEGAL_RUNTIME_CONFIRMED",
    "FORCED_RUNTIME_CONFIRMED",
    "NOT_RUNTIME_OBSERVABLE",
    "BLOCKED_BY_ENTITY_RESTRICTION",
    "BLOCKED_BY_TECHNICAL_LIMITATION"
)

Assert-Condition (Test-Path -LiteralPath $CoveragePath -PathType Leaf) "Coverage artifact is missing: $CoveragePath"
Assert-Condition (Test-Path -LiteralPath $CatalogEvidencePath -PathType Leaf) "Catalog evidence is missing: $CatalogEvidencePath"
Assert-Condition (Test-Path -LiteralPath $NaturalEvidenceDirectory -PathType Container) "Natural evidence directory is missing: $NaturalEvidenceDirectory"
Assert-Condition (Test-Path -LiteralPath $ProfileEvidenceDirectory -PathType Container) "Profile evidence directory is missing: $ProfileEvidenceDirectory"

$coverage = @(Get-Content -LiteralPath $CoveragePath | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json })
$catalogRecords = @(Get-Content -LiteralPath $CatalogEvidencePath | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json })
$catalogRecord = @($catalogRecords | Where-Object { $_.kind -eq "trait_catalog" })
$forcedRows = @($catalogRecords | Where-Object { $_.kind -eq "forced_trait_result" })
$naturalFiles = @(Get-ChildItem -LiteralPath $NaturalEvidenceDirectory -Filter "*.jsonl" -File)
$naturalRecords = @($naturalFiles | ForEach-Object { Get-Content -LiteralPath $_.FullName | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json } })
$naturalProfiles = @($naturalRecords | Where-Object { $_.kind -eq "natural_profile" })
$naturalResults = @($naturalRecords | Where-Object { $_.kind -eq "matrix_result" })
$profileFiles = @(Get-ChildItem -LiteralPath $ProfileEvidenceDirectory -Filter "*.jsonl" -File)
$profileRecords = @($profileFiles | ForEach-Object { Get-Content -LiteralPath $_.FullName | Where-Object { $_.Trim() } | ForEach-Object { $_ | ConvertFrom-Json } })
$legalProfiles = @($profileRecords | Where-Object { $_.kind -eq "legal_defensive_profile_result" })
$profileResults = @($profileRecords | Where-Object { $_.kind -eq "matrix_result" })

Assert-Condition ($catalogRecord.Count -eq 1) "Expected exactly one live trait_catalog record, found $($catalogRecord.Count)"
$catalog = @($catalogRecord[0].traits)
Assert-Condition ($catalog.Count -eq 39) "Expected 39 live catalog traits, found $($catalog.Count)"
Assert-Condition ($coverage.Count -eq 39) "Expected exactly 39 terminal coverage rows, found $($coverage.Count)"
Assert-Condition ($forcedRows.Count -eq 110) "Expected 110 full forced-rank rows, found $($forcedRows.Count)"
Assert-Condition ($naturalFiles.Count -eq 7) "Expected seven natural evidence files, found $($naturalFiles.Count)"
Assert-Condition ($naturalProfiles.Count -eq 70) "Expected 70 natural profiles, found $($naturalProfiles.Count)"
Assert-Condition ($naturalResults.Count -eq 7) "Expected seven natural terminal results, found $($naturalResults.Count)"
Assert-Condition (@($naturalResults | Where-Object { $_.status -ne "complete" -or [int]$_.case_error_count -ne 0 }).Count -eq 0) "Natural evidence contains an incomplete or erroneous suite"
Assert-Condition ($profileFiles.Count -eq 7) "Expected seven legal-profile evidence files, found $($profileFiles.Count)"
Assert-Condition ($legalProfiles.Count -eq 49) "Expected 49 legal defensive profiles, found $($legalProfiles.Count)"
Assert-Condition ($profileResults.Count -eq 7) "Expected seven legal-profile terminal results, found $($profileResults.Count)"
Assert-Condition (@($profileResults | Where-Object { $_.status -ne "complete" -or [int]$_.case_error_count -ne 0 }).Count -eq 0) "Legal-profile evidence contains an incomplete or erroneous suite"
Assert-Condition (@($legalProfiles | Where-Object { -not $_.all_attached_traits_legal }).Count -eq 0) "A constructed profile contains an illegal attached trait"
Assert-Condition (@($legalProfiles | Where-Object { $_.unexpected_L2_bypass }).Count -eq 0) "A constructed profile reports an unexpected L2 bypass"
Assert-Condition (@($legalProfiles | Where-Object { $_.production_combat_mutated -or $_.APO_profile -ne "NONE" }).Count -eq 0) "A constructed profile mutated production combat or enabled Apotheosis"

$duplicateCoverageIds = @($coverage | Group-Object trait_id | Where-Object Count -ne 1)
Assert-Condition ($duplicateCoverageIds.Count -eq 0) "Coverage contains duplicate or empty trait IDs: $($duplicateCoverageIds.Name -join ', ')"

$catalogById = @{}
foreach ($trait in $catalog) {
    $catalogById[$trait.trait_id] = $trait
}

$coverageIds = @($coverage.trait_id | Sort-Object)
$catalogIds = @($catalog.trait_id | Sort-Object)
Assert-Condition (($coverageIds -join "|") -eq ($catalogIds -join "|")) "Coverage trait IDs do not exactly match the live L2 registry"

$testedEntities = @($naturalProfiles | ForEach-Object { $_.boss } | Sort-Object -Unique)
Assert-Condition ($testedEntities.Count -eq 7) "Expected seven distinct natural-matrix entities, found $($testedEntities.Count)"
$level1000Profiles = @($naturalProfiles | Where-Object { [int]$_.requested_level -eq 1000 })
Assert-Condition ($level1000Profiles.Count -eq 7) "Expected one Lv1000 legality profile per entity, found $($level1000Profiles.Count)"

foreach ($row in $coverage) {
    $catalogTrait = $catalogById[$row.trait_id]
    Assert-Condition ($null -ne $catalogTrait) "Unknown trait ID: $($row.trait_id)"
    Assert-Condition ([int]$row.native_max_rank -eq [int]$catalogTrait.native_max_rank) "Native max rank mismatch for $($row.trait_id)"

    $expectedRanks = @(1..([int]$catalogTrait.native_max_rank))
    $testedRanks = @($row.tested_ranks | ForEach-Object { [int]$_ } | Sort-Object -Unique)
    Assert-Condition (($testedRanks -join ",") -eq ($expectedRanks -join ",")) "Tested ranks are incomplete for $($row.trait_id)"

    $actualForcedRows = @($forcedRows | Where-Object { $_.trait_id -eq $row.trait_id })
    $actualForcedRanks = @($actualForcedRows | ForEach-Object { [int]$_.rank } | Sort-Object -Unique)
    Assert-Condition ($actualForcedRows.Count -eq $expectedRanks.Count) "Forced row count is incomplete for $($row.trait_id)"
    Assert-Condition (($actualForcedRanks -join ",") -eq ($expectedRanks -join ",")) "Forced ranks are incomplete for $($row.trait_id)"
    Assert-Condition ($row.forced_evidence.performed -eq $true) "Forced evidence is not marked performed for $($row.trait_id)"
    $actualForcedClasses = @($actualForcedRows | ForEach-Object { $_.evidence_class } | Sort-Object -Unique)
    Assert-Condition ($actualForcedClasses.Count -eq 1 -and $row.forced_evidence.evidence_class -eq $actualForcedClasses[0]) "Forced evidence class mismatch for $($row.trait_id)"

    $actualNaturalProfiles = @($naturalProfiles | Where-Object { $_.trait_ranks.PSObject.Properties.Name -contains $row.trait_id })
    $actualNaturalRanks = @($actualNaturalProfiles | ForEach-Object { [int]$_.trait_ranks.($row.trait_id) } | Sort-Object -Unique)
    $reportedNaturalRanks = @($row.natural_occurrence_evidence.observed_ranks | ForEach-Object { [int]$_ } | Sort-Object -Unique)
    Assert-Condition ([int]$row.natural_occurrence_evidence.profile_count -eq $actualNaturalProfiles.Count) "Natural profile count mismatch for $($row.trait_id)"
    Assert-Condition (($reportedNaturalRanks -join ",") -eq ($actualNaturalRanks -join ",")) "Natural rank evidence mismatch for $($row.trait_id)"

    $legalityAt1000 = @($level1000Profiles | ForEach-Object { $_.trait_eligibility | Where-Object { $_.trait_id -eq $row.trait_id } })
    Assert-Condition ($legalityAt1000.Count -eq 7) "Incomplete seven-entity legality evidence for $($row.trait_id)"
    $legalForAllTestedSemibosses = @($legalityAt1000 | Where-Object { -not $_.legal_at_requested_level }).Count -eq 0
    Assert-Condition ($row.legality.legal_for_tested_semibosses -eq $legalForAllTestedSemibosses) "Legality mismatch for $($row.trait_id)"

    $reportedEntities = @($row.tested_entities | Sort-Object -Unique)
    Assert-Condition (($reportedEntities -join "|") -eq ($testedEntities -join "|")) "Tested entity set mismatch for $($row.trait_id)"

    Assert-Condition ($allowedTerminalClasses -contains $row.terminal_classification) "Invalid terminal class for $($row.trait_id): $($row.terminal_classification)"
    Assert-Condition ($row.l2_behavior_authoritative -eq $true) "L2 authority must be explicit for $($row.trait_id)"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace([string]$row.runtime_behavior)) "runtime_behavior is missing for $($row.trait_id)"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace([string]$row.behavior_category)) "behavior_category is missing for $($row.trait_id)"
    Assert-Condition (-not [string]::IsNullOrWhiteSpace([string]$row.tno_interaction)) "tno_interaction is missing for $($row.trait_id)"
    Assert-Condition (@($row.evidence_paths).Count -gt 0) "Evidence paths are missing for $($row.trait_id)"

    foreach ($evidencePath in @($row.evidence_paths)) {
        Assert-Condition (Test-Path -LiteralPath $evidencePath -PathType Leaf) "Missing evidence path for $($row.trait_id): $evidencePath"
    }

    if ($row.terminal_classification -eq "LEGAL_RUNTIME_CONFIRMED") {
        Assert-Condition ($row.legality.legal_for_tested_semibosses -eq $true) "Legal terminal row is not legal for $($row.trait_id)"
        Assert-Condition ([int]$row.natural_occurrence_evidence.profile_count -gt 0) "Legal terminal row lacks natural occurrence for $($row.trait_id)"
    }
    if ($row.terminal_classification -eq "FORCED_RUNTIME_CONFIRMED") {
        Assert-Condition ($row.forced_evidence.performed -eq $true) "Forced terminal row lacks forced evidence for $($row.trait_id)"
    }
    if ($row.terminal_classification -eq "BLOCKED_BY_ENTITY_RESTRICTION") {
        Assert-Condition ($row.legality.legal_for_tested_semibosses -eq $false) "Entity-restricted row is marked legal for $($row.trait_id)"
        Assert-Condition ($row.forced_evidence.evidence_class -eq "FORCED_ILLEGAL_DIAGNOSTIC") "Restricted row lacks illegal-diagnostic labeling for $($row.trait_id)"
    }

    $expectedTerminalClass = if ($actualNaturalProfiles.Count -gt 0) {
        "LEGAL_RUNTIME_CONFIRMED"
    } elseif ($legalForAllTestedSemibosses) {
        "FORCED_RUNTIME_CONFIRMED"
    } else {
        "BLOCKED_BY_ENTITY_RESTRICTION"
    }
    Assert-Condition ($row.terminal_classification -eq $expectedTerminalClass) "Terminal class mismatch for $($row.trait_id): expected $expectedTerminalClass"
}

$terminalCounts = $coverage | Group-Object terminal_classification | Sort-Object Name
Write-Output "Validated Phase 5F L2 trait coverage: 39/39 live traits, no duplicates, all native ranks represented."
foreach ($count in $terminalCounts) {
    Write-Output "  $($count.Name)=$($count.Count)"
}
