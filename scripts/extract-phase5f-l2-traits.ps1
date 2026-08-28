param(
    [Parameter(Mandatory = $true)]
    [string] $LogPath,

    [Parameter(Mandatory = $true)]
    [string] $OutputPath,

    [Parameter(Mandatory = $true)]
    [ValidateSet('catalog', 'natural', 'forced')]
    [string] $ExpectedMode,

    [Parameter(Mandatory = $true)]
    [string] $ExpectedBoss,

    [string] $ExpectedTrait = ''
)

$ErrorActionPreference = 'Stop'
$marker = 'TNO_PHASE5F_L2_TRAITS '
$expectedLevels = @(50, 100, 150, 200, 300, 400, 500, 600, 800, 1000)
$expectedTraits = @(
    'l2hostility:tank', 'l2hostility:speedy', 'l2hostility:protection',
    'l2hostility:invisible', 'l2hostility:fiery', 'l2hostility:regenerate',
    'l2hostility:adaptive', 'l2hostility:reflect', 'l2hostility:shulker',
    'l2hostility:grenade', 'l2hostility:corrosion', 'l2hostility:erosion',
    'l2hostility:growth', 'l2hostility:split', 'l2hostility:drain',
    'l2hostility:counter_strike', 'l2hostility:gravity', 'l2hostility:moonwalk',
    'l2hostility:arena', 'l2hostility:dementor', 'l2hostility:dispell',
    'l2hostility:undying', 'l2hostility:teleport', 'l2hostility:repelling',
    'l2hostility:pulling', 'l2hostility:reprint', 'l2hostility:killer_aura',
    'l2hostility:ragnarok', 'l2hostility:master', 'l2hostility:weakness',
    'l2hostility:slowness', 'l2hostility:poison', 'l2hostility:wither',
    'l2hostility:levitation', 'l2hostility:blindness', 'l2hostility:nausea',
    'l2hostility:soul_burner', 'l2hostility:freezing', 'l2hostility:cursed'
) | Sort-Object

$resolvedLog = (Resolve-Path -LiteralPath $LogPath).Path
$content = [IO.File]::ReadAllText($resolvedLog)
$records = [Collections.Generic.List[object]]::new()
foreach ($line in ($content -split "`r?`n")) {
    $index = $line.IndexOf($marker, [StringComparison]::Ordinal)
    if ($index -lt 0) { continue }
    $json = $line.Substring($index + $marker.Length)
    if (-not $json.StartsWith('{')) { continue }
    try { $value = $json | ConvertFrom-Json }
    catch { throw "Malformed L2 trait-matrix JSON in ${resolvedLog}: $json" }
    $records.Add([pscustomobject]@{ Json = $json; Value = $value })
}

$starts = @($records | Where-Object { $_.Value.kind -eq 'matrix_start' })
$catalogs = @($records | Where-Object { $_.Value.kind -eq 'trait_catalog' })
$profiles = @($records | Where-Object { $_.Value.kind -eq 'natural_profile' })
$forcedResults = @($records | Where-Object { $_.Value.kind -eq 'forced_trait_result' })
$errors = @($records | Where-Object { $_.Value.kind -eq 'case_error' })
$results = @($records | Where-Object { $_.Value.kind -eq 'matrix_result' })

if ($starts.Count -ne 1 -or $catalogs.Count -ne 1 -or $results.Count -ne 1) {
    throw "Expected one matrix_start, trait_catalog, and matrix_result; found $($starts.Count), $($catalogs.Count), $($results.Count)."
}
if ($errors.Count -ne 0) { throw "Capture contains $($errors.Count) case_error record(s)." }
foreach ($record in @($starts[0], $catalogs[0], $results[0])) {
    if ($record.Value.schema -ne 'tno.phase5f.l2_trait_matrix.v1' -or
        $record.Value.mode -ne $ExpectedMode -or $record.Value.boss -ne $ExpectedBoss) {
        throw 'Capture schema, mode, or boss does not match the requested artifact.'
    }
}

$catalog = $catalogs[0].Value
if ([int]$catalog.trait_count -ne 39) { throw "Expected 39 live traits; found $($catalog.trait_count)." }
$actualTraits = @($catalog.traits.trait_id | Sort-Object)
if ((Compare-Object $actualTraits $expectedTraits).Count -ne 0) {
    throw 'Live trait catalog does not equal the required 39-trait set.'
}
foreach ($trait in $catalog.traits) {
    if (-not $trait.enabled -or [int]$trait.min_level -lt 0 -or [int]$trait.cost -lt 0 -or
        [int]$trait.native_max_rank -lt 1) {
        throw "Invalid runtime catalog metadata for $($trait.trait_id)."
    }
}

$result = $results[0].Value
$expectedProfiles = if ($ExpectedMode -eq 'natural') { 10 }
    elseif ($ExpectedMode -eq 'forced') {
        if ($ExpectedTrait) {
            [int](@($catalog.traits | Where-Object { $_.trait_id -eq $ExpectedTrait })[0].native_max_rank)
        }
        else { [int](($catalog.traits | Measure-Object -Property native_max_rank -Sum).Sum) }
    }
    else { 0 }
if ($result.status -ne 'complete' -or [int]$result.case_error_count -ne 0 -or
    [int]$result.profile_count -ne $expectedProfiles -or
    [int]$result.requested_profile_count -ne $expectedProfiles) {
    throw 'Capture lacks one clean, complete matrix_result.'
}

if ($profiles.Count -ne $expectedProfiles) {
    if ($ExpectedMode -eq 'natural') {
        throw "Expected $expectedProfiles natural profiles; found $($profiles.Count)."
    }
    elseif ($profiles.Count -ne 0) { throw 'Forced/catalog capture unexpectedly contains natural profiles.' }
}
if ($ExpectedMode -eq 'natural') {
    $actualLevels = @($profiles.Value.requested_level | Sort-Object -Unique)
    if ((Compare-Object $actualLevels $expectedLevels).Count -ne 0) {
        throw 'Natural matrix does not contain the exact requested level ladder.'
    }
    foreach ($profile in $profiles.Value) {
        if ([int]$profile.attached_level -ne [int]$profile.requested_level -or
            -not $profile.l2_initialized -or -not $profile.tensura_l2h_scaling_marker -or
            $profile.APO_profile -ne 'NONE' -or [int]$profile.complete_trait_eligibility_count -ne 39 -or
            $profile.trait_budget_observability -ne 'NOT_EXPOSED_AFTER_GENERATION' -or
            $profile.consumed_trait_budget -ne 'NOT_RUNTIME_OBSERVABLE' -or
            $profile.remaining_trait_budget -ne 'NOT_RUNTIME_OBSERVABLE') {
            throw "Invalid natural profile at requested level $($profile.requested_level)."
        }
        $eligibility = @($profile.trait_eligibility.trait_id | Sort-Object)
        if ((Compare-Object $eligibility $expectedTraits).Count -ne 0) {
            throw "Incomplete legality table at requested level $($profile.requested_level)."
        }
        foreach ($generated in $profile.traits) {
            $legal = @($profile.trait_eligibility | Where-Object { $_.trait_id -eq $generated.id })
            if ($legal.Count -ne 1 -or -not $legal[0].legal_at_requested_level) {
                throw "Generated illegal trait $($generated.id) at requested level $($profile.requested_level)."
            }
        }
    }
}

if ($ExpectedMode -eq 'forced') {
    if ($forcedResults.Count -ne $expectedProfiles) {
        throw "Expected $expectedProfiles forced trait results; found $($forcedResults.Count)."
    }
    $expectedCatalog = if ($ExpectedTrait) { @($catalog.traits | Where-Object { $_.trait_id -eq $ExpectedTrait }) }
        else { @($catalog.traits) }
    if ($expectedCatalog.Count -eq 0) { throw "Expected trait filter $ExpectedTrait is absent from the live catalog." }
    foreach ($trait in $expectedCatalog) {
        $rows = @($forcedResults.Value | Where-Object { $_.trait_id -eq $trait.trait_id } | Sort-Object rank)
        $expectedRanks = @(1..([int]$trait.native_max_rank))
        $actualRanks = @($rows | ForEach-Object { [int]$_.rank })
        if ((Compare-Object $actualRanks $expectedRanks).Count -ne 0) {
            throw "Forced rank coverage is incomplete for $($trait.trait_id)."
        }
        foreach ($row in $rows) {
            if (-not $row.compatibility_evidence_only -or $row.balance_evidence_allowed -or
                -not $row.forced_attachment_used -or -not $row.runtime_probe_completed -or
                $row.APO_profile -ne 'NONE' -or $row.production_combat_mutated -or
                $row.real_royal_bow -ne 'royalvariations:royal_bow' -or
                $row.real_royal_arrow -ne 'royalvariations:royal_arrow' -or
                $row.royal_arrow_mark_enabled -or -not $row.tensura_l2h_scaling_marker -or
                $row.unexpected_L2_bypass) {
                throw "Invalid forced runtime row for $($trait.trait_id) rank $($row.rank)."
            }
            $expectedClass = if ($row.legal_for_tested_entity) { 'FORCED_DIAGNOSTIC' }
                else { 'FORCED_ILLEGAL_DIAGNOSTIC' }
            if ($row.evidence_class -ne $expectedClass) {
                throw "Incorrect forced legality label for $($trait.trait_id) rank $($row.rank)."
            }
        }
    }
}

$outputDir = Split-Path -Parent $OutputPath
if ($outputDir) { [IO.Directory]::CreateDirectory($outputDir) | Out-Null }
$preserved = @($starts[0], $catalogs[0]) + $profiles + $forcedResults + @($results[0])
$text = ($preserved.Json -join "`n") + "`n"
[IO.File]::WriteAllText($OutputPath, $text, [Text.UTF8Encoding]::new($false))

Write-Output "Validated L2 trait matrix: mode=$ExpectedMode boss=$ExpectedBoss traits=39 profiles=$expectedProfiles errors=0"
Write-Output "Wrote $($preserved.Count) JSONL records to $OutputPath"
