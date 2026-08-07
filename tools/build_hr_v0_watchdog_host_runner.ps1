param(
    [Parameter(Mandatory = $true)]
    [string]$ToolRoot,
    [string]$BuildRoot = "",
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($BuildRoot)) {
    $BuildRoot = Join-Path $repoRoot "tmp\watchdog-host-vector"
}
$buildRootFull = [System.IO.Path]::GetFullPath($BuildRoot)
$repoTmpFull = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "tmp"))
if (-not $buildRootFull.StartsWith($repoTmpFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "BuildRoot must stay inside $repoTmpFull"
}

$clang = Join-Path $ToolRoot "bin\clang.exe"
if (-not (Test-Path -LiteralPath $clang)) {
    throw "Pinned LLVM-MinGW clang is missing: $clang"
}
$version = (& $clang --version) -join "`n"
if ($LASTEXITCODE -ne 0 -or $version -notmatch "clang version 22\.1\.8" -or
    $version -notmatch "Target: x86_64-w64-windows-gnu") {
    throw "Compiler identity differs from locked LLVM-MinGW 20260616 / LLVM 22.1.8"
}

$env:SOURCE_DATE_EPOCH = "1786060800"
$fileMap = "-ffile-prefix-map=$repoRoot=project-button"
$macroMap = "-fmacro-prefix-map=$repoRoot=project-button"
$common = @(
    "--target=x86_64-w64-windows-gnu",
    "-std=c11",
    "-O2",
    "-Wall",
    "-Wextra",
    "-Werror",
    "-Wconversion",
    "-Wshadow",
    "-Wformat=2",
    $fileMap,
    $macroMap,
    "-Wl,--build-id=none,--no-insert-timestamp",
    "-Ifirmware/watchdog/include",
    "firmware/watchdog/tests/c_vector_runner.c",
    "firmware/watchdog/src/pb_watchdog.c"
)

$outputs = @()
foreach ($label in @("a", "b")) {
    $build = Join-Path $buildRootFull ("build-" + $label)
    if (Test-Path -LiteralPath $build) {
        $resolved = (Resolve-Path $build).Path
        if (-not $resolved.StartsWith($buildRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove unexpected path: $resolved"
        }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $build | Out-Null
    $output = Join-Path $build "pb_watchdog_vector_runner.exe"
    Push-Location $repoRoot
    try {
        & $clang @common "-o" $output
        if ($LASTEXITCODE -ne 0) { throw "Host vector build-$label failed" }
    }
    finally {
        Pop-Location
    }
    $outputs += $output
}

$hashA = (Get-FileHash -Algorithm SHA256 $outputs[0]).Hash.ToLowerInvariant()
$hashB = (Get-FileHash -Algorithm SHA256 $outputs[1]).Hash.ToLowerInvariant()
if ($hashA -ne $hashB) {
    throw "The two clean host-vector builds are not reproducible"
}
if (-not [string]::IsNullOrWhiteSpace($OutputDirectory)) {
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    Copy-Item -LiteralPath $outputs[0] -Destination $OutputDirectory -Force
}

[pscustomobject]@{
    artifact = "pb_watchdog_vector_runner.exe"
    bytes = (Get-Item $outputs[0]).Length
    sha256 = $hashA
    build_a_matches_build_b = $true
} | Format-Table -AutoSize
Write-Host "HR-V0 compiled-C host vector runner reproduction: PASS"
Write-Host "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
Write-Host "Host execution evidence is not target HIL, functional-safety validation or permission to energize."
