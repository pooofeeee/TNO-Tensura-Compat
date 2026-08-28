param(
    [Parameter(Mandatory = $true)] [string] $LogPath,
    [Parameter(Mandatory = $true)] [string] $OutputPath,
    [Parameter(Mandatory = $true)]
    [ValidateSet('MAGIC_WEAPON', 'HOLY_WEAPON', 'SOUL_EATER', 'ELEMENTAL_SLOTTING', 'ENERGY_STEAL', 'SEVERANCE')]
    [string] $ExpectedFamily,
    [Parameter(Mandatory = $true)] [string] $ExpectedBoss,
    [Parameter(Mandatory = $true)] [int] $ExpectedCases,
    [switch] $Endgame
)

$ErrorActionPreference = 'Stop'
& (Join-Path $PSScriptRoot 'extract-phase5f-suite-b.ps1') `
    -LogPath $LogPath `
    -OutputPath $OutputPath `
    -ExpectedFamily $ExpectedFamily `
    -ExpectedBoss $ExpectedBoss `
    -ExpectedCases $ExpectedCases `
    -Suite C `
    -Endgame:$Endgame
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
