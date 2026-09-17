param(
    [string]$PythonExe = "python",
    [string]$OutputDirectory = ""
)

$ErrorActionPreference = "Stop"
$repo = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
if (-not $OutputDirectory) {
    $OutputDirectory = Join-Path $repo "release"
}
$output = [IO.Path]::GetFullPath($OutputDirectory)
$work = Join-Path $repo ".release-work"
$staging = Join-Path $output "staging"

$version = (& $PythonExe -c "from privateer.version import __version__; print(__version__)" | Select-Object -Last 1).Trim()
$displayVersion = (& $PythonExe -c "from privateer.version import display_version; print(display_version())" | Select-Object -Last 1).Trim()
if (-not $version) {
    throw "Could not determine the Privateer version"
}

foreach ($path in @($work, $staging)) {
    $full = [IO.Path]::GetFullPath($path)
    if (-not $full.StartsWith($repo + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
        throw "Refusing to clean a build path outside the repository: $full"
    }
    if (Test-Path -LiteralPath $full) {
        Remove-Item -LiteralPath $full -Recurse -Force
    }
}
New-Item -ItemType Directory -Path $output -Force | Out-Null

& $PythonExe -m PyInstaller `
    --noconfirm `
    --clean `
    --windowed `
    --onedir `
    --noupx `
    --name Privateer `
    --paths $repo `
    --collect-submodules privateer `
    --distpath $staging `
    --workpath $work `
    --specpath $work `
    (Join-Path $PSScriptRoot "privateer_launcher.py")
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller failed with exit code $LASTEXITCODE"
}

$app = Join-Path $staging "Privateer"
Copy-Item -LiteralPath (Join-Path $PSScriptRoot "END_USER_INSTALL.txt") -Destination (Join-Path $app "INSTALL.txt")
[IO.File]::WriteAllText(
    (Join-Path $app "VERSION.txt"),
    "Privateer $displayVersion (Windows x64)$([Environment]::NewLine)",
    [Text.UTF8Encoding]::new($false)
)

$archive = Join-Path $output "Privateer-$version-Windows-x64.zip"
if (Test-Path -LiteralPath $archive) {
    Remove-Item -LiteralPath $archive -Force
}
Compress-Archive -Path (Join-Path $app "*") -DestinationPath $archive -CompressionLevel Optimal

Write-Output $archive
