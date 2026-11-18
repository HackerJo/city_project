#Requires -Version 5.1
<#
.SYNOPSIS
  Erstellt den eigenständigen Windows-Viewer für das City-Projekt.
.DESCRIPTION
  Führt den Godot-Erstimport und anschließend den Windows-Export aus.
  Das Skript muss im Projektstamm liegen, also neben teacher_app.py.
.PARAMETER Godot
  Vollständiger Pfad zur Godot-Programmdatei.
.PARAMETER ExportPreset
  Name des zu verwendenden Godot-Export-Presets.
.PARAMETER ProjectRoot
  Projektstamm. Standard ist der Ordner, in dem dieses Skript liegt.
.PARAMETER OutputDir
  Zielordner für die exportierte CityViewer.exe.
.EXAMPLE
  .\build_viewer_windows.ps1 -Godot ".\Godot_v4.7.2-stable_win64.exe"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$Godot,

    [string]$ExportPreset = 'Windows Desktop 2',

    [string]$ProjectRoot = $PSScriptRoot,
    [string]$OutputDir = ''
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($OutputDir)) {
    $OutputDir = Join-Path $ProjectRoot 'cityviewer\build\windows'
}

$ResolvedGodot = (Resolve-Path -LiteralPath $Godot).Path
$CityViewer = Join-Path $ProjectRoot 'cityviewer'
$ExportPresetFile = Join-Path $CityViewer 'export_presets.cfg'
$ProjectFile = Join-Path $CityViewer 'project.godot'
$Executable = Join-Path $OutputDir 'CityViewer.exe'

if (-not (Test-Path -LiteralPath $ProjectFile -PathType Leaf)) {
    throw "Godot-Projektdatei nicht gefunden: $ProjectFile"
}
if (-not (Test-Path -LiteralPath $ExportPresetFile -PathType Leaf)) {
    throw "Exportprofil nicht gefunden: $ExportPresetFile"
}

$PresetContent = Get-Content -LiteralPath $ExportPresetFile -Raw
if ($PresetContent -notmatch [regex]::Escape('name="' + $ExportPreset + '"')) {
    throw "Export-Preset '$ExportPreset' wurde in $ExportPresetFile nicht gefunden."
}

function Invoke-Godot {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$Arguments,

        [Parameter(Mandatory = $true)]
        [string]$StepName
    )

    Write-Host ""
    Write-Host "$StepName"
    Write-Host ("Befehl: {0} {1}" -f $ResolvedGodot, ($Arguments -join ' '))

    $Process = Start-Process `
        -FilePath $ResolvedGodot `
        -ArgumentList $Arguments `
        -WorkingDirectory $ProjectRoot `
        -NoNewWindow `
        -Wait `
        -PassThru

    Write-Host ("ExitCode: {0}" -f $Process.ExitCode)

    if ($Process.ExitCode -ne 0) {
        throw "$StepName fehlgeschlagen. ExitCode: $($Process.ExitCode). Bitte die vollständige Godot-Ausgabe prüfen."
    }

    return $Process
}

Write-Host "Godot: $ResolvedGodot"
Write-Host "Projekt: $CityViewer"
Write-Host "Export-Preset: $ExportPreset"
Write-Host "Zieldatei: $Executable"

Invoke-Godot -StepName "[1/3] Godot-Erstimport wird ausgeführt ..." -Arguments @(
    '--headless',
    '--path', $CityViewer,
    '--import'
)

Write-Host ""
Write-Host "[2/3] Windows-Export wird ausgeführt ..."
New-Item -ItemType Directory -Force -Path $OutputDir | Out-Null

$QuotedPreset = '"' + $ExportPreset + '"'
$QuotedExecutable = '"' + $Executable + '"'

Invoke-Godot -StepName "[2/3] Godot-Windows-Export wird ausgeführt ..." -Arguments @(
    '--headless',
    '--path', $CityViewer,
    '--export-release',
    $QuotedPreset,
    $QuotedExecutable
)

if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
    throw "Erwartete Datei wurde nicht erzeugt: $Executable"
}

Write-Host ""
Write-Host "[3/3] Exportdateien werden geprüft ..."
$Missing = @()
foreach ($RelativePath in @(
    'data\buildings.json',
    'data\parts.csv',
    'data\city.json'
)) {
    $Candidate = Join-Path $CityViewer $RelativePath
    if (Test-Path -LiteralPath $Candidate -PathType Leaf) {
        Write-Host "  Quellressource vorhanden: $RelativePath"
    } else {
        Write-Warning "  Quellressource fehlt: $RelativePath"
        $Missing += $RelativePath
    }
}

if ($Missing.Count -gt 0) {
    throw "Der Export kann unvollständig sein. Fehlende Quellressourcen: $($Missing -join ', ')"
}

Write-Host ""
Write-Host "Export abgeschlossen: $Executable"
Write-Host "Nächster Schritt: .\test_viewer_windows.ps1 -ViewerExe `"$Executable`" -Godot `"$ResolvedGodot`""
