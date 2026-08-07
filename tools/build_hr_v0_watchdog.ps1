param(
    [Parameter(Mandatory = $true)]
    [string]$ToolRoot,
    [string]$BuildRoot = "",
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if ([string]::IsNullOrWhiteSpace($BuildRoot)) {
    $BuildRoot = Join-Path $repoRoot "tmp\watchdog-repro"
}
$buildRootFull = [System.IO.Path]::GetFullPath($BuildRoot)
$repoTmpFull = [System.IO.Path]::GetFullPath((Join-Path $repoRoot "tmp"))
if (-not $buildRootFull.StartsWith($repoTmpFull, [System.StringComparison]::OrdinalIgnoreCase)) {
    throw "BuildRoot must stay inside $repoTmpFull"
}

$sdk = Join-Path $ToolRoot "pico-sdk"
$arm = Join-Path $ToolRoot "arm"
$cmake = Join-Path $ToolRoot "cmake\cmake-4.3.3-windows-x86_64\bin\cmake.exe"
$ninja = Join-Path $ToolRoot "ninja\ninja.exe"
$picotool = Join-Path $ToolRoot "picotool-prebuilt"
$python = Join-Path $ToolRoot "python\python.exe"
$objdump = Join-Path $arm "bin\arm-none-eabi-objdump.exe"

foreach ($required in @($sdk, $arm, $cmake, $ninja, $picotool, $python, $objdump)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Pinned tool is missing: $required"
    }
}
if ((Get-Content (Join-Path $sdk ".git\HEAD") -Raw).Trim() -ne "98a542c1a62fb549ffb5d66a3e5892b06276b670") {
    throw "Pico SDK checkout is not the locked 2.3.0 revision"
}

$env:PICO_SDK_PATH = $sdk
$env:PICO_TOOLCHAIN_PATH = $arm
$env:SOURCE_DATE_EPOCH = "1786060800"
$env:PATH = (Join-Path $arm "bin") + ";" + (Split-Path $ninja) + ";" + $env:PATH

function Invoke-CleanBuild([string]$Label) {
    $build = Join-Path $buildRootFull ("build-" + $Label)
    if (Test-Path -LiteralPath $build) {
        $resolved = (Resolve-Path $build).Path
        if (-not $resolved.StartsWith($buildRootFull, [System.StringComparison]::OrdinalIgnoreCase)) {
            throw "Refusing to remove unexpected path: $resolved"
        }
        Remove-Item -LiteralPath $resolved -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path $buildRootFull | Out-Null
    $configureOutput = & $cmake `
        -S (Join-Path $repoRoot "firmware\watchdog") `
        -B $build `
        -G Ninja `
        -DCMAKE_BUILD_TYPE=MinSizeRel `
        "-DCMAKE_MAKE_PROGRAM=$ninja" `
        "-DPICOTOOL_FETCH_FROM_GIT_PATH=$picotool" `
        "-DPython3_EXECUTABLE=$python"
    $configureExit = $LASTEXITCODE
    $configureOutput | Out-Host
    if ($configureExit -ne 0) { throw "CMake configure failed for build-$Label" }
    $buildOutput = & $cmake --build $build
    $buildExit = $LASTEXITCODE
    $buildOutput | Out-Host
    if ($buildExit -ne 0) { throw "CMake build failed for build-$Label" }

    Push-Location $build
    try {
        (& $objdump -h "project_button_watchdog.elf") |
            Set-Content -Encoding ascii "project_button_watchdog.canonical.dis"
        (& $objdump -d "project_button_watchdog.elf") |
            Add-Content -Encoding ascii "project_button_watchdog.canonical.dis"
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        $disPath = Join-Path $build "project_button_watchdog.canonical.dis"
        $disText = [System.IO.File]::ReadAllText($disPath)
        $disText = [regex]::Replace($disText, "[ \t]+(?=\r?$)", "", [System.Text.RegularExpressions.RegexOptions]::Multiline)
        $disText = $disText.Replace("`r`n", "`n").TrimEnd("`r", "`n") + "`n"
        [System.IO.File]::WriteAllText($disPath, $disText, $utf8NoBom)
        $mapText = [System.IO.File]::ReadAllText((Join-Path $build "project_button_watchdog.elf.map"))
        $mapText = $mapText.Replace($ToolRoot.Replace("\", "/"), "<TOOL_ROOT>")
        $mapText = $mapText.Replace($ToolRoot, "<TOOL_ROOT>")
        $mapText = [regex]::Replace(
            $mapText,
            "CMakeFiles/project_button_watchdog\.dir/[^\s]*?/pico-sdk/",
            "CMakeFiles/project_button_watchdog.dir/PICO_SDK/"
        )
        $mapText = [regex]::Replace($mapText, "[ \t]+(?=\r?$)", "", [System.Text.RegularExpressions.RegexOptions]::Multiline)
        $mapText = $mapText.Replace("`r`n", "`n").TrimEnd("`r", "`n") + "`n"
        [System.IO.File]::WriteAllText(
            (Join-Path $build "project_button_watchdog.canonical.map"),
            $mapText,
            $utf8NoBom
        )
    }
    finally {
        Pop-Location
    }
    return $build
}

$buildA = Invoke-CleanBuild "a"
$buildB = Invoke-CleanBuild "b"
$artifacts = @(
    "project_button_watchdog.elf",
    "project_button_watchdog.uf2",
    "project_button_watchdog.bin",
    "project_button_watchdog.hex",
    "project_button_watchdog.canonical.map",
    "project_button_watchdog.canonical.dis"
)
$results = foreach ($artifact in $artifacts) {
    $pathA = Join-Path $buildA $artifact
    $pathB = Join-Path $buildB $artifact
    $hashA = (Get-FileHash $pathA -Algorithm SHA256).Hash.ToLowerInvariant()
    $hashB = (Get-FileHash $pathB -Algorithm SHA256).Hash.ToLowerInvariant()
    [pscustomobject]@{
        artifact = $artifact
        bytes = (Get-Item $pathA).Length
        sha256 = $hashA
        match = ($hashA -eq $hashB)
    }
}
if ($results.match -contains $false) {
    $results | Format-Table -AutoSize
    throw "The two clean watchdog builds are not reproducible"
}

if (-not [string]::IsNullOrWhiteSpace($OutputDirectory)) {
    New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
    foreach ($artifact in $artifacts) {
        Copy-Item -LiteralPath (Join-Path $buildA $artifact) -Destination $OutputDirectory -Force
    }
}

$results | Format-Table -AutoSize
Write-Host "HR-V0 watchdog two-build reproduction: PASS"
Write-Host "PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION"
Write-Host "This script does not flash hardware, perform HIL validation, or authorize energization."
