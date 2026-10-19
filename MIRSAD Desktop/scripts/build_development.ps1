param([switch]$SkipTests,[switch]$PrepareOnly)
$ErrorActionPreference = 'Stop'
$desktopRoot = [System.IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$pythonPath = Join-Path $desktopRoot '.venv\Scripts\python.exe'
$assetPath = Join-Path $desktopRoot 'assets'
if (-not (Test-Path -LiteralPath $pythonPath)) { throw 'Create the independent .venv first.' }
$env:PYTHONPATH = Join-Path $desktopRoot 'src'
$originalPath = $env:PATH
# Resolve native dependencies from this runtime and Windows only. Ambient GIS or
# Poppler DLLs can otherwise shadow Windows ICU and break Qt in the frozen EXE.
$basePythonDir = (& $pythonPath -c "import sys; print(sys.base_prefix)").Trim()
$basePythonExe = Join-Path $basePythonDir 'python.exe'
$canImportQt = $false
try {
    $proc = Start-Process -FilePath $pythonPath -ArgumentList '-c "from PySide6.QtCore import Qt"' -NoNewWindow -PassThru -Wait
    $canImportQt = ($proc.ExitCode -eq 0)
} catch {
    $canImportQt = $false
}
if (-not $canImportQt -and (Test-Path -LiteralPath $basePythonExe)) {
    $runner = $basePythonExe
    $env:PYTHONPATH = @((Join-Path $desktopRoot 'src'), (Join-Path $desktopRoot '.venv\Lib\site-packages')) -join ';'
} else {
    $runner = $pythonPath
}
$env:PATH = @((Split-Path $pythonPath), $basePythonDir, (Join-Path $env:SystemRoot 'System32'), $env:SystemRoot) -join ';'
Push-Location -LiteralPath $desktopRoot
try {
    & $runner ../scripts/build_climate_source_catalogue.py
    if ($LASTEXITCODE -ne 0) { throw 'Climate source catalogue generation failed.' }
    & $runner scripts/vendor_science.py
    if ($LASTEXITCODE -ne 0) { throw 'Scientific kernel validation failed.' }
    & $runner scripts/prepare_assets.py
    if ($LASTEXITCODE -ne 0) { throw 'Asset validation failed.' }
    & $runner scripts/build_user_guide.py
    if ($LASTEXITCODE -ne 0) { throw 'Bilingual user guide validation failed.' }
    & $runner ../scripts/build_tool_help.py
    if ($LASTEXITCODE -ne 0) { throw 'Toolbox help metadata generation failed.' }
    $helpPowerShell = Join-Path $PSHOME 'pwsh.exe'
    if (-not (Test-Path -LiteralPath $helpPowerShell)) { $helpPowerShell = Join-Path $PSHOME 'powershell.exe' }
    & $runner scripts/prepare_help_compiler.py --powershell $helpPowerShell
    if ($LASTEXITCODE -ne 0) { throw 'CHM compiler preparation failed. Run scripts/prepare_help_compiler.py --download once if missing.' }
    & $runner scripts/build_chm.py
    if ($LASTEXITCODE -ne 0) { throw 'Compiled bilingual CHM help validation failed.' }
    if (-not $SkipTests) {
        & $runner -m unittest discover -s tests -v
        if ($LASTEXITCODE -ne 0) { throw 'Tests failed. Development executable was not replaced.' }
    }
    & $runner -m PyInstaller --noconfirm --clean --onedir --windowed --name MIRSAD `
        --distpath .build/dist --workpath .build/pyinstaller --specpath .build `
        --paths src --paths "$desktopRoot\.venv\Lib\site-packages" --add-data "$assetPath;assets" --icon (Join-Path $assetPath 'mirsad.ico') --collect-all pyogrio `
        --version-file (Join-Path $assetPath 'version_info.txt') --collect-all rasterio --collect-submodules scipy.interpolate `
        --exclude-module arcpy --exclude-module PyQt5 --exclude-module PyQt6 launcher.py
    if ($LASTEXITCODE -ne 0) { throw 'Build failed.' }
    # PyInstaller writes one named directory. Move its contents to the fixed development location.
    if ($PrepareOnly) { & $runner scripts/finalize_build.py --verify-only }
    else { & $runner scripts/finalize_build.py }
    if ($LASTEXITCODE -ne 0) { throw 'Packaged application validation failed.' }
    if ($PrepareOnly) { Write-Output 'Verified build candidate is ready; runtime/development was not replaced.' }
    else { Write-Output (Join-Path $desktopRoot 'runtime\development\MIRSAD.exe') }
} finally {
    $env:PATH = $originalPath
    Pop-Location
}
