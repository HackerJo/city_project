#Requires -Version 5.1
<#
.SYNOPSIS
  Baut die Lehrerausgabe für Windows.
.DESCRIPTION
  Erstellt Lehrer_Stadt.exe und Stadt_Erkennung.exe mit PyInstaller und
  sammelt die benötigten Dateien im Ordner build\lehrerausgabe.
  Die exportierte Godot-EXE benötigt zusätzlich die zugehörige .pck-Datei.
  Die rohe parts.csv wird explizit nach _internal\cityviewer\data kopiert,
  weil der Builder sie benötigt und die .pck sie nicht enthält.
.PARAMETER ProjectRoot
  Projektstamm. Standard ist der Ordner, in dem dieses Skript liegt.
.EXAMPLE
  .\build_lehrerausgabe.ps1
#>
[CmdletBinding()]
param(
    [string]$ProjectRoot = $PSScriptRoot
)

$ErrorActionPreference = 'Stop'

$Dist = Join-Path $ProjectRoot 'dist'
$Build = Join-Path $ProjectRoot 'build\lehrerausgabe'
$InternalCityViewer = Join-Path $Build '_internal\cityviewer'
$InternalCityViewerData = Join-Path $InternalCityViewer 'data'

Write-Host "Projekt: $ProjectRoot"
Write-Host "Ziel: $Build"

$Python = Get-Command python -ErrorAction SilentlyContinue
if (-not $Python) {
    throw "python wurde nicht gefunden. Bitte Python installieren oder PATH prüfen."
}
Write-Host "Python: $($Python.Source)"

$PyInstallerCheck = & python -m PyInstaller --version 2>&1
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller ist als Modul nicht verfügbar. Bitte installieren: python -m pip install pyinstaller"
}
Write-Host "PyInstaller-Version: $PyInstallerCheck"

Write-Host "`n[1/5] Lehrer_Stadt.exe wird gebaut ..."
& python -m PyInstaller --noconfirm --clean build_teacher_app.spec
if ($LASTEXITCODE -ne 0) {
    throw "Build von Lehrer_Stadt.exe fehlgeschlagen."
}

Write-Host "`n[2/5] Stadt_Erkennung.exe wird gebaut ..."
& python -m PyInstaller --noconfirm --clean build_detect_city.spec
if ($LASTEXITCODE -ne 0) {
    throw "Build von Stadt_Erkennung.exe fehlgeschlagen."
}

Write-Host "`n[3/5] Lehrerausgabe wird zusammengestellt ..."
if (Test-Path -LiteralPath $Build) {
    Remove-Item -LiteralPath $Build -Recurse -Force
}
New-Item -ItemType Directory -Force -Path $Build | Out-Null

Copy-Item -Path (Join-Path $Dist 'Lehrer_Stadt\*') -Destination $Build -Recurse -Force
Copy-Item -Path (Join-Path $Dist 'Stadt_Erkennung\*') -Destination $Build -Recurse -Force

# Benötigte Projektdateien in die Lehrerausgabe kopieren
$Copies = @(
    @{ Source = 'examples'; Destination = 'examples' },
    @{ Source = 'output/layout.json'; Destination = 'output/layout.json' },
    @{ Source = 'output/buildings.json'; Destination = 'output/buildings.json' },
    @{ Source = 'output/print'; Destination = 'output/print' },
    @{ Source = 'cityviewer/data/buildings.json'; Destination = 'cityviewer/data/buildings.json' },
    @{ Source = 'cityviewer/data/parts.csv'; Destination = 'cityviewer/data/parts.csv' },
    @{ Source = 'cityviewer/data/city.json'; Destination = 'cityviewer/data/city.json' },
    @{ Source = 'cityviewer/CityViewer.exe'; Destination = 'cityviewer/CityViewer.exe' },
    @{ Source = 'cityviewer/CityViewer.pck'; Destination = 'cityviewer/CityViewer.pck' },
    @{ Source = 'Readme.Teacher.md'; Destination = 'Readme.Teacher.md' },
    @{ Source = 'THIRD_PARTY_NOTICES.md'; Destination = 'THIRD_PARTY_NOTICES.md' }
)

foreach ($Copy in $Copies) {
    $Source = Join-Path $ProjectRoot $Copy.Source
    $Destination = Join-Path $Build $Copy.Destination
    if (-not (Test-Path -LiteralPath $Source)) {
        Write-Warning "Quelle fehlt: $($Copy.Source)"
        continue
    }
    $DestinationParent = Split-Path -Parent $Destination
    if (-not (Test-Path -LiteralPath $DestinationParent)) {
        New-Item -ItemType Directory -Force -Path $DestinationParent | Out-Null
    }
    Copy-Item -Path $Source -Destination $Destination -Recurse -Force
}

# Explizite Kopie der rohen parts.csv und city.json nach _internal\cityviewer\data,
# damit der Builder sie findet. Die .pck enthält diese Dateien nicht zuverlässig.
Write-Host "`nExplizite Kopie von parts.csv und city.json nach _internal\cityviewer\data ..."
if (-not (Test-Path -LiteralPath $InternalCityViewerData)) {
    New-Item -ItemType Directory -Force -Path $InternalCityViewerData | Out-Null
}
foreach ($Name in @('parts.csv', 'city.json')) {
    $Source = Join-Path $ProjectRoot "cityviewer\data\$Name"
    $Destination = Join-Path $InternalCityViewerData $Name
    if (Test-Path -LiteralPath $Source) {
        Copy-Item -Path $Source -Destination $Destination -Force
        Write-Host "  Kopiert: $Name"
    } else {
        Write-Warning "  Quelle fehlt: $Name"
    }
}

Write-Host "`n[4/5] Prüfung der Lehrerausgabe ..."
$Required = @(
    'Lehrer_Stadt.exe',
    'Stadt_Erkennung.exe',
    'cityviewer/CityViewer.exe',
    'cityviewer/CityViewer.pck',
    'cityviewer/data/buildings.json',
    'cityviewer/data/parts.csv',
    'cityviewer/data/city.json',
    'output/layout.json',
    'output/buildings.json',
    'output/print/cards.pdf',
    'output/print/grid_sheet.pdf',
    'examples/demos.json'
)

$Missing = @()
foreach ($Relative in $Required) {
    $Candidate = Join-Path $Build $Relative
    if (Test-Path -LiteralPath $Candidate) {
        Write-Host "  Vorhanden: $Relative"
    } else {
        Write-Warning "  Fehlt: $Relative"
        $Missing += $Relative
    }
}

# Zusätzliche Prüfung: parts.csv und city.json müssen auch in _internal liegen
foreach ($Name in @('parts.csv', 'city.json')) {
    $Candidate = Join-Path $InternalCityViewerData $Name
    if (Test-Path -LiteralPath $Candidate) {
        Write-Host "  Vorhanden in _internal: cityviewer/data/$Name"
    } else {
        Write-Warning "  Fehlt in _internal: cityviewer/data/$Name"
        $Missing += "_internal/cityviewer/data/$Name"
    }
}

if ($Missing.Count -gt 0) {
    throw "Lehrerausgabe unvollständig. Fehlende Dateien: $($Missing -join ', ')"
}

Write-Host "`n[5/5] Lehrerausgabe erstellt: $Build"
Write-Host "Nächster Schritt: Lehrer_Stadt.exe auf einem Rechner ohne Python/Godot testen."
