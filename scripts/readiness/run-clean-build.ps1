$ErrorActionPreference='Stop'
Set-Location -LiteralPath (Resolve-Path "$PSScriptRoot/../..").Path
$out='docs/benchmarks/post-phase6-six-family-readiness'
$archive='run/readiness-preclean-build-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.zip'
$existing=@('build/test-results','build/reports','build/libs') | Where-Object { Test-Path -LiteralPath $_ }
if ($existing.Count -gt 0) { Compress-Archive -LiteralPath $existing -DestinationPath $archive }
$env:JAVA_HOME='C:/Program Files/Java/jdk-21'
& ./gradlew.bat clean build -Pphase5f_runtime_mods_dir=run/elemental-runtime-mods --console=plain 2>&1 | Tee-Object -FilePath "$out/clean-build.log"
$code=$LASTEXITCODE
$tests=0; $failures=0; $errors=0; $skipped=0
$reports=@(Get-ChildItem -LiteralPath 'build/test-results/test' -Filter 'TEST-*.xml')
$suites=@($reports | ForEach-Object {
 [xml]$xml=Get-Content -Raw -LiteralPath $_.FullName
 $s=$xml.testsuite
 $tests += [int]$s.tests; $failures += [int]$s.failures; $errors += [int]$s.errors; $skipped += [int]$s.skipped
 [ordered]@{name=$s.name;tests=[int]$s.tests;failures=[int]$s.failures;errors=[int]$s.errors;skipped=[int]$s.skipped;sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath $_.FullName).Hash.ToLowerInvariant()}
})
$result=[ordered]@{
 schema='tno.post_phase6.readiness.build.v1'; checkpoint='R4'; command='./gradlew.bat clean build -Pphase5f_runtime_mods_dir=run/elemental-runtime-mods --console=plain'; java_home=$env:JAVA_HOME
 production_source_baseline='d212695c006f503f1b175e4b9a7a57e2f0ebf5ac'; assessment_head_before_R4=(git rev-parse HEAD)
 exit_code=$code; tests=$tests;failures=$failures;errors=$errors;skipped=$skipped;suites=$suites
 log_sha256=(Get-FileHash -Algorithm SHA256 -LiteralPath "$out/clean-build.log").Hash.ToLowerInvariant()
 preserved_prior_build_archive=$archive;preserved_prior_build_archive_sha256=$(if(Test-Path -LiteralPath $archive){(Get-FileHash -Algorithm SHA256 -LiteralPath $archive).Hash.ToLowerInvariant()}else{$null})
 interpretation='Build/test health only; not new native combat runtime or balance evidence. Gradle may reuse eligible cached tasks; actual task outcomes retained in log.'
}
$result | ConvertTo-Json -Depth 10 | Set-Content -Encoding utf8 -LiteralPath "$out/build-validation.json"
if ($code -ne 0 -or $tests -ne 54 -or $failures -ne 0 -or $errors -ne 0 -or $skipped -ne 0) { throw 'Required clean build failed; inspect saved build report/log' }
Write-Output "BUILD PASS: $tests tests, no failures/errors/skips."
