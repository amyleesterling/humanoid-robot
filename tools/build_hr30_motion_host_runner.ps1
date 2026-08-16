param(
    [Parameter(Mandatory = $true)]
    [string]$ToolRoot,
    [string]$BuildRoot = "",
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($BuildRoot)) {
    $BuildRoot = Join-Path $repoRoot "tmp\hr30-motion-host"
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $repoRoot "firmware\hr30-motion-controller\output\host-p0.1"
}
$buildRootFull = [System.IO.Path]::GetFullPath($BuildRoot)
$repoTmpFull = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "tmp"))
if (-not $buildRootFull.StartsWith($repoTmpFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "BuildRoot must stay inside $repoTmpFull"
}
$outputFull = [System.IO.Path]::GetFullPath($OutputDirectory)
$allowedOutput = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "firmware\hr30-motion-controller\output"))
if (-not $outputFull.StartsWith($allowedOutput, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "OutputDirectory must stay inside $allowedOutput"
}

$clang = Join-Path $ToolRoot "bin\clang.exe"
if (-not (Test-Path -LiteralPath $clang)) { throw "Pinned clang missing: $clang" }
$version = (& $clang --version) -join "`n"
if ($LASTEXITCODE -ne 0 -or $version -notmatch "clang version 22\.1\.8") {
    throw "Compiler is not the locked LLVM-MinGW clang 22.1.8"
}

$env:SOURCE_DATE_EPOCH = "1786838400"
$common = @(
    "--target=x86_64-w64-windows-gnu",
    "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-Wconversion", "-Wshadow", "-Wformat=2",
    "-ffile-prefix-map=$repoRoot=project-button",
    "-fmacro-prefix-map=$repoRoot=project-button",
    "-Wl,--build-id=none,--no-insert-timestamp",
    "-Ifirmware/hr30-motion-controller/include",
    "firmware/hr30-motion-controller/tests/hr30_motion_vector_runner.c",
    "firmware/hr30-motion-controller/src/hr30_motion.c"
)

$outputs = @()
foreach ($label in @("a", "b")) {
    $build = Join-Path $buildRootFull ("build-" + $label)
    if (Test-Path -LiteralPath $build) {
        $resolved = (Resolve-Path $build).Path
        if (-not $resolved.StartsWith($buildRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove unexpected build path: $resolved"
        }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $build | Out-Null
    $binary = Join-Path $build "hr30_motion_vector_runner.exe"
    Push-Location $repoRoot
    try {
        & $clang @common "-o" $binary
        if ($LASTEXITCODE -ne 0) { throw "host build-$label failed" }
        $runOutput = (& $binary) -join "`n"
        if ($LASTEXITCODE -ne 0 -or $runOutput -notmatch "PASS: HR-30 FIRST_POWER_NO_MOTION") {
            throw "compiled vector runner-$label failed"
        }
        [System.IO.File]::WriteAllText((Join-Path $build "vector-output.txt"), $runOutput.TrimEnd() + "`n", (New-Object System.Text.UTF8Encoding($false)))
    }
    finally { Pop-Location }
    $outputs += [pscustomobject]@{ binary = $binary; log = (Join-Path $build "vector-output.txt") }
}

$hashA = (Get-FileHash -Algorithm SHA256 $outputs[0].binary).Hash.ToLowerInvariant()
$hashB = (Get-FileHash -Algorithm SHA256 $outputs[1].binary).Hash.ToLowerInvariant()
$logHashA = (Get-FileHash -Algorithm SHA256 $outputs[0].log).Hash.ToLowerInvariant()
$logHashB = (Get-FileHash -Algorithm SHA256 $outputs[1].log).Hash.ToLowerInvariant()
if ($hashA -ne $hashB -or $logHashA -ne $logHashB) {
    throw "two clean host builds or executions differ"
}

New-Item -ItemType Directory -Force -Path $outputFull | Out-Null
Copy-Item -LiteralPath $outputs[0].binary -Destination (Join-Path $outputFull "hr30_motion_vector_runner.exe") -Force
Copy-Item -LiteralPath $outputs[0].log -Destination (Join-Path $outputFull "vector-output.txt") -Force

$sourcePaths = @(
    "firmware/hr30-motion-controller/include/hr30_motion.h",
    "firmware/hr30-motion-controller/src/hr30_motion.c",
    "firmware/hr30-motion-controller/tests/hr30_motion_vector_runner.c",
    "firmware/hr30-motion-controller/platform/stm32h743/hr30_stm32h743_io.h",
    "tools/build_hr30_motion_host_runner.ps1"
)
$sourceHashes = [ordered]@{}
foreach ($path in $sourcePaths) {
    $sourceHashes[$path] = (Get-FileHash -Algorithm SHA256 (Join-Path $repoRoot $path)).Hash.ToLowerInvariant()
}
$evidence = [ordered]@{
    identifier = "HR30-MOTION-FIRST-POWER-NO-MOTION-P0.1"
    warning = "PRELIMINARY - HOST-COMPILED LOGIC EVIDENCE ONLY - NOT TARGET HIL OR AUTHORITY TO CONNECT, POWER, MOVE, OR ENERGIZE"
    profile = "FIRST_POWER_NO_MOTION"
    compiler = (($version -split "`n")[0]).Trim()
    target = "x86_64-w64-windows-gnu host evidence"
    source_date_epoch = 1786838400
    two_clean_builds_byte_identical = $true
    two_executions_byte_identical = $true
    vector_result = "PASS"
    axis_count = 25
    bus_count = 8
    target_binary_built = $false
    target_hil_executed = $false
    functional_safety_credit = $false
    energization_authority = $false
    source_sha256 = $sourceHashes
    binary = [ordered]@{ path = "hr30_motion_vector_runner.exe"; bytes = (Get-Item $outputs[0].binary).Length; sha256 = $hashA }
    execution_log = [ordered]@{ path = "vector-output.txt"; bytes = (Get-Item $outputs[0].log).Length; sha256 = $logHashA }
}
$evidence | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 (Join-Path $outputFull "build-evidence.json")

Write-Host "PASS: two byte-identical HR-30 host builds and compiled-C executions"
Write-Host "PRELIMINARY - NO TARGET HIL, FUNCTIONAL-SAFETY CREDIT, OR ENERGIZATION AUTHORITY"
