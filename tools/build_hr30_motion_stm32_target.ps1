param(
    [Parameter(Mandatory = $true)]
    [string]$ToolRoot,
    [string]$BuildRoot = "",
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($BuildRoot)) {
    $BuildRoot = Join-Path $repoRoot "tmp\hr30-motion-stm32"
}
if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    $OutputDirectory = Join-Path $repoRoot "firmware\hr30-motion-controller\output\stm32h743-p0.1"
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
$objcopy = Join-Path $ToolRoot "bin\llvm-objcopy.exe"
$objdump = Join-Path $ToolRoot "bin\llvm-objdump.exe"
$readelf = Join-Path $ToolRoot "bin\llvm-readelf.exe"
$sizeTool = Join-Path $ToolRoot "bin\llvm-size.exe"
foreach ($required in @($clang, $objcopy, $objdump, $readelf, $sizeTool)) {
    if (-not (Test-Path -LiteralPath $required)) { throw "Pinned LLVM tool missing: $required" }
}
$version = (& $clang --version) -join "`n"
if ($LASTEXITCODE -ne 0 -or $version -notmatch "clang version 22\.1\.8" -or
    $version -notmatch "ca7933e47d3a3451d81e72ac174dcb5aa28b59d1") {
    throw "Compiler is not locked LLVM-MinGW clang 22.1.8 / ca7933e4"
}

$bindingPaths = @(
    "hr30/whole-body-p0.1/actuator-bus-axis-binding.csv",
    "hr30/whole-body-p0.1/actuator-bus-topology.csv",
    "hr30/whole-body-p0.1/electrical/axis-commissioning-station-p0.1/axis-commissioning-matrix.csv",
    "hr30/whole-body-p0.1/electrical/motion-controller-p0.1/control-gpio-map.csv",
    "hr30/whole-body-p0.1/electrical/motion-controller-p0.1/uart-pin-map.csv"
)
$stream = New-Object System.IO.MemoryStream
foreach ($path in $bindingPaths) {
    $nameBytes = [System.Text.Encoding]::UTF8.GetBytes($path)
    $stream.Write($nameBytes, 0, $nameBytes.Length)
    $stream.WriteByte(0)
    $fileBytes = [System.IO.File]::ReadAllBytes((Join-Path $repoRoot $path))
    $stream.Write($fileBytes, 0, $fileBytes.Length)
    $stream.WriteByte(0)
}
$stream.Position = 0
$sha = [System.Security.Cryptography.SHA256]::Create()
$bindingHash = ([BitConverter]::ToString($sha.ComputeHash($stream))).Replace("-", "").ToLowerInvariant()
if ($bindingHash -ne "6764f0163c02e7b52f6f76cfcbd5b90ea4c37cd292e459d9e99bc6981baed471") {
    throw "Target configuration binding changed; review and regenerate the configuration word"
}

$env:SOURCE_DATE_EPOCH = "1786924800"
$utf8NoBom = New-Object System.Text.UTF8Encoding($false)
$include = @(
    "-Ifirmware/hr30-motion-controller/include",
    "-Ifirmware/hr30-motion-controller/platform/stm32h743"
)
$targetCommon = @(
    "--no-default-config", "--target=arm-none-eabi", "-mcpu=cortex-m7", "-mthumb", "-mfloat-abi=soft",
    "-std=c11", "-Os", "-Wall", "-Wextra", "-Werror", "-Wconversion", "-Wshadow", "-Wformat=2",
    "-ffreestanding", "-fno-builtin", "-fdata-sections", "-ffunction-sections", "-fstack-usage",
    "-fno-unwind-tables", "-fno-asynchronous-unwind-tables"
) + $include

function Invoke-Checked([string]$Description, [string]$Program, [string[]]$Arguments) {
    & $Program @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Description failed with exit code $LASTEXITCODE" }
}

function Normalize-Text([string]$InputPath, [string]$OutputPath) {
    $text = [System.IO.File]::ReadAllText($InputPath)
    $text = $text.Replace($buildRootFull.Replace("\", "/"), "<BUILD_ROOT>")
    $text = $text.Replace($buildRootFull, "<BUILD_ROOT>")
    $text = $text.Replace($repoRoot.Replace("\", "/"), "<REPO_ROOT>")
    $text = $text.Replace($repoRoot, "<REPO_ROOT>")
    $text = [regex]::Replace($text, "build-[ab]", "build")
    $text = [regex]::Replace($text, "[ \t]+(?=\r?$)", "", [System.Text.RegularExpressions.RegexOptions]::Multiline)
    $text = $text.Replace("`r`n", "`n").TrimEnd("`r", "`n") + "`n"
    [System.IO.File]::WriteAllText($OutputPath, $text, $utf8NoBom)
}

function Invoke-CleanTargetBuild([string]$Label) {
    $build = Join-Path $buildRootFull ("build-" + $Label)
    if (Test-Path -LiteralPath $build) {
        $resolved = (Resolve-Path $build).Path
        if (-not $resolved.StartsWith($buildRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove unexpected build path: $resolved"
        }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $build | Out-Null
    Push-Location $repoRoot
    try {
        Invoke-Checked "portable core compile" $clang ($targetCommon + @(
            "-c", "firmware/hr30-motion-controller/src/hr30_motion.c", "-o", (Join-Path $build "hr30_motion.o")
        ))
        Invoke-Checked "STM32 target compile" $clang ($targetCommon + @(
            "-c", "firmware/hr30-motion-controller/platform/stm32h743/hr30_stm32h743_target.c",
            "-o", (Join-Path $build "hr30_stm32h743_target.o")
        ))
        Invoke-Checked "startup assembly" $clang @(
            "--no-default-config", "--target=arm-none-eabi", "-mcpu=cortex-m7", "-mthumb", "-mfloat-abi=soft",
            "-c", "firmware/hr30-motion-controller/platform/stm32h743/startup_hr30_stm32h743.S",
            "-o", (Join-Path $build "startup.o")
        )
        $rawMap = Join-Path $build "hr30-motion-controller-stm32h743.raw.map"
        $elf = Join-Path $build "hr30-motion-controller-stm32h743.elf"
        Invoke-Checked "target link" $clang @(
            "--no-default-config", "--target=arm-none-eabi", "-mcpu=cortex-m7", "-mthumb", "-mfloat-abi=soft",
            "-nostdlib", "-fuse-ld=lld", "-Wl,--gc-sections", "-Wl,--build-id=none", "-Wl,-Map,$rawMap",
            "-Wl,-T,firmware/hr30-motion-controller/platform/stm32h743/stm32h743zit6_hr30.ld",
            (Join-Path $build "startup.o"), (Join-Path $build "hr30_stm32h743_target.o"),
            (Join-Path $build "hr30_motion.o"), "-o", $elf
        )
        Invoke-Checked "binary conversion" $objcopy @("-O", "binary", $elf, (Join-Path $build "hr30-motion-controller-stm32h743.bin"))
        Invoke-Checked "Intel HEX conversion" $objcopy @("-O", "ihex", $elf, (Join-Path $build "hr30-motion-controller-stm32h743.hex"))
        (& $sizeTool -A $elf) | Set-Content -Encoding ascii (Join-Path $build "size.raw.txt")
        if ($LASTEXITCODE -ne 0) { throw "llvm-size failed" }
        (& $objdump -h -s -d $elf) | Set-Content -Encoding ascii (Join-Path $build "disassembly.raw.txt")
        if ($LASTEXITCODE -ne 0) { throw "llvm-objdump failed" }
        (& $readelf -h -S -s $elf) | Set-Content -Encoding ascii (Join-Path $build "elf-inspection.raw.txt")
        if ($LASTEXITCODE -ne 0) { throw "llvm-readelf failed" }
        Normalize-Text $rawMap (Join-Path $build "hr30-motion-controller-stm32h743.map")
        Normalize-Text (Join-Path $build "size.raw.txt") (Join-Path $build "size.txt")
        Normalize-Text (Join-Path $build "disassembly.raw.txt") (Join-Path $build "disassembly.txt")
        Normalize-Text (Join-Path $build "elf-inspection.raw.txt") (Join-Path $build "elf-inspection.txt")
    }
    finally { Pop-Location }
    return $build
}

function Invoke-HostVectors([string]$Build) {
    Push-Location $repoRoot
    try {
        $core = Join-Path $Build "hr30_motion_vector_runner.exe"
        Invoke-Checked "core host vector compile" $clang @(
            "--target=x86_64-w64-windows-gnu", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-Wconversion", "-Wshadow", "-Wformat=2", "-fno-builtin",
            "-Ifirmware/hr30-motion-controller/include",
            "firmware/hr30-motion-controller/tests/hr30_motion_vector_runner.c",
            "firmware/hr30-motion-controller/src/hr30_motion.c", "-o", $core
        )
        $coreOutput = (& $core) -join "`n"
        if ($LASTEXITCODE -ne 0 -or $coreOutput -notmatch "PASS: HR-30 FIRST_POWER_NO_MOTION") {
            throw "core compiled vectors failed"
        }
        [System.IO.File]::WriteAllText((Join-Path $Build "core-vector-output.txt"), $coreOutput.TrimEnd() + "`n", $utf8NoBom)

        $mmio = Join-Path $Build "hr30_stm32h743_mmio_runner.exe"
        Invoke-Checked "STM32 MMIO host vector compile" $clang @(
            "--target=x86_64-w64-windows-gnu", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
            "-Wconversion", "-Wshadow", "-Wformat=2", "-fno-builtin", "-DHR30_TARGET_HOST_SIMULATION",
            "-Ifirmware/hr30-motion-controller/include", "-Ifirmware/hr30-motion-controller/platform/stm32h743",
            "firmware/hr30-motion-controller/tests/hr30_stm32h743_mmio_runner.c",
            "firmware/hr30-motion-controller/platform/stm32h743/hr30_stm32h743_target.c",
            "firmware/hr30-motion-controller/src/hr30_motion.c", "-o", $mmio
        )
        $mmioOutput = (& $mmio) -join "`n"
        if ($LASTEXITCODE -ne 0 -or $mmioOutput -notmatch "PASS: STM32H743 MMIO simulation") {
            throw "STM32 MMIO compiled vectors failed"
        }
        [System.IO.File]::WriteAllText((Join-Path $Build "mmio-vector-output.txt"), $mmioOutput.TrimEnd() + "`n", $utf8NoBom)
    }
    finally { Pop-Location }
}

$buildA = Invoke-CleanTargetBuild "a"
$buildB = Invoke-CleanTargetBuild "b"
Invoke-HostVectors $buildA
Invoke-HostVectors $buildB

$artifacts = @(
    "hr30-motion-controller-stm32h743.elf", "hr30-motion-controller-stm32h743.bin",
    "hr30-motion-controller-stm32h743.hex", "hr30-motion-controller-stm32h743.map",
    "disassembly.txt", "elf-inspection.txt", "size.txt",
    "core-vector-output.txt", "mmio-vector-output.txt",
    "hr30_motion.su", "hr30_stm32h743_target.su"
)
$comparison = @()
foreach ($artifact in $artifacts) {
    $pathA = Join-Path $buildA $artifact
    $pathB = Join-Path $buildB $artifact
    if (-not (Test-Path -LiteralPath $pathA) -or -not (Test-Path -LiteralPath $pathB)) {
        throw "Expected target artifact missing: $artifact"
    }
    $hashA = (Get-FileHash -Algorithm SHA256 $pathA).Hash.ToLowerInvariant()
    $hashB = (Get-FileHash -Algorithm SHA256 $pathB).Hash.ToLowerInvariant()
    $comparison += [ordered]@{ path = $artifact; bytes = (Get-Item $pathA).Length; sha256 = $hashA; builds_match = ($hashA -eq $hashB) }
}
if ($comparison.builds_match -contains $false) {
    $comparison | Format-Table -AutoSize
    throw "Two clean STM32 target builds are not byte-identical"
}

if (Test-Path -LiteralPath $outputFull) {
    $resolvedOutput = (Resolve-Path $outputFull).Path
    if (-not $resolvedOutput.StartsWith($allowedOutput, [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to replace unexpected output path: $resolvedOutput"
    }
    Remove-Item -LiteralPath $resolvedOutput -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $outputFull | Out-Null
foreach ($artifact in $artifacts) {
    Copy-Item -LiteralPath (Join-Path $buildA $artifact) -Destination $outputFull -Force
}

$sourcePaths = @(
    "firmware/hr30-motion-controller/include/hr30_motion.h",
    "firmware/hr30-motion-controller/src/hr30_motion.c",
    "firmware/hr30-motion-controller/tests/hr30_motion_vector_runner.c",
    "firmware/hr30-motion-controller/tests/hr30_stm32h743_mmio_runner.c",
    "firmware/hr30-motion-controller/platform/stm32h743/hr30_stm32h743_io.h",
    "firmware/hr30-motion-controller/platform/stm32h743/hr30_stm32h743_registers.h",
    "firmware/hr30-motion-controller/platform/stm32h743/hr30_stm32h743_target.h",
    "firmware/hr30-motion-controller/platform/stm32h743/hr30_stm32h743_target.c",
    "firmware/hr30-motion-controller/platform/stm32h743/startup_hr30_stm32h743.S",
    "firmware/hr30-motion-controller/platform/stm32h743/stm32h743zit6_hr30.ld",
    "firmware/hr30-motion-controller/target-toolchain-lock.json",
    "tools/build_hr30_motion_stm32_target.ps1"
)
$sourceHashes = [ordered]@{}
foreach ($path in $sourcePaths) {
    $sourceHashes[$path] = (Get-FileHash -Algorithm SHA256 (Join-Path $repoRoot $path)).Hash.ToLowerInvariant()
}
$evidence = [ordered]@{
    identifier = "HR30-MOTION-STM32H743-FIRST-POWER-P0.1"
    warning = "PRELIMINARY - UNFLASHED TARGET BUILD AND HOST MMIO EVIDENCE ONLY - NOT APPROVED FOR CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION"
    profile = "FIRST_POWER_NO_MOTION"
    compiler = (($version -split "`n")[0]).Trim()
    compiler_revision = "ca7933e47d3a3451d81e72ac174dcb5aa28b59d1"
    target = "arm-none-eabi / Cortex-M7 / Thumb-2 / soft-float / freestanding"
    source_date_epoch = 1786924800
    configuration_binding_sha256 = $bindingHash
    configuration_word = "0x6764f016"
    vector_count = 166
    reset_clock_policy = "retain reset HSI 64 MHz; no PLL or clock-tree reconfiguration"
    systick_policy = "64,000-cycle polling tick; TICKINT disabled; interrupts globally disabled"
    uart_policy = "all eight UART clock gates cleared; 13 TX/RX signals analog/no-pull; eight direction pins output-low"
    two_clean_target_builds_byte_identical = $true
    core_compiled_vectors = "PASS"
    mmio_compiled_vectors = "PASS"
    stm32_target_binary_built = $true
    target_binary_flashed = $false
    target_hil_executed = $false
    oscilloscope_boot_state_verified = $false
    physical_uart_write_path_audited = $false
    functional_safety_credit = $false
    connection_authority = $false
    powered_test_authority = $false
    motion_authority = $false
    energization_authority = $false
    source_sha256 = $sourceHashes
    binding_inputs = $bindingPaths
    artifacts = $comparison
    primary_sources = @(
        [ordered]@{ document = "ST DS12110"; revision = "Rev 11 / January 2026"; url = "https://www.st.com/resource/en/datasheet/stm32h743vi.pdf" },
        [ordered]@{ document = "ST RM0433"; revision = "Rev 8 / January 2023"; url = "https://www.st.com/resource/en/reference_manual/rm0433-stm32h742-stm32h743753-and-stm32h750-value-line-advanced-armbased-32bit-mcus-stmicroelectronics.pdf" },
        [ordered]@{ document = "ST PM0253"; revision = "Rev 6 / May 2026"; url = "https://www.st.com/resource/en/programming_manual/DM00237416.pdf" },
        [ordered]@{ document = "ST ES0392"; revision = "Rev 15 / September 2025"; url = "https://www.st.com/resource/en/errata_sheet/es0392-stm32h742xig-stm32h743xig-stm32h750xb-stm32h753xi-device-errata-stmicroelectronics.pdf" },
        [ordered]@{ document = "ST cmsis-device-h7"; revision = "v1.10.7 / commit de8243d2c15f87936f28a49fcd9e6f5ba10fc233 / 2026-02-04"; url = "https://github.com/STMicroelectronics/cmsis-device-h7" }
    )
}
[System.IO.File]::WriteAllText((Join-Path $outputFull "build-evidence.json"), ($evidence | ConvertTo-Json -Depth 10) + "`n", $utf8NoBom)

$manifestRows = @()
Get-ChildItem -LiteralPath $outputFull -File | Where-Object { $_.Name -ne "artifact-manifest.csv" } | Sort-Object Name | ForEach-Object {
    $manifestRows += [pscustomobject]@{
        path = $_.Name
        bytes = $_.Length
        sha256 = (Get-FileHash -Algorithm SHA256 $_.FullName).Hash.ToLowerInvariant()
    }
}
$manifestRows | Export-Csv -NoTypeInformation -Encoding utf8 (Join-Path $outputFull "artifact-manifest.csv")

Write-Host "PASS: two byte-identical freestanding STM32H743 target builds"
Write-Host "PASS: core vectors and register-level MMIO vectors"
Write-Host "PRELIMINARY - TARGET NOT FLASHED; NO HIL, SAFETY CREDIT, OR AUTHORITY TO CONNECT, POWER, MOVE, OR ENERGIZE"
