#Requires -Version 5.1
<#
.SYNOPSIS
  Startet die exportierte CityViewer.exe mit einer Beispielstadt.
.DESCRIPTION
  Dieser Test prüft den Start des eigenständigen Windows-Viewers. Er ersetzt
  nicht die Sichtprüfung von Gebäuden, Texturen, Steuerung und Rückkehr mit Esc.
.PARAMETER ViewerExe
  Pfad zur exportierten CityViewer.exe.
.PARAMETER Godot
  Optionaler Pfad zur Godot-Programmdatei; wird für den Start der exportierten
  EXE nicht benötigt, bleibt aber für Kompatibilität verfügbar.
.PARAMETER ProjectRoot
  Projektstamm. Standard ist der Ordner, in dem dieses Skript liegt.
.PARAMETER CityJson
  Pfad zu einer zu prüfenden city.json. Standard ist eine Demo-Stadt.
.EXAMPLE
  .\test_viewer_windows.ps1 -ViewerExe ".\cityviewer\build\windows\CityViewer.exe"
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string]$ViewerExe,

    [string]$Godot = '',

    [string]$ProjectRoot = $PSScriptRoot,
    [string]$CityJson = ''
)

$ErrorActionPreference = 'Stop'

$ResolvedViewer = (Resolve-Path -LiteralPath $ViewerExe).Path
$CityViewer = Join-Path $ProjectRoot 'cityviewer'

if ([string]::IsNullOrWhiteSpace($CityJson)) {
    $CityJson = Join-Path $ProjectRoot 'examples\city02\city.json'
}

if (-not (Test-Path -LiteralPath $CityJson -PathType Leaf)) {
    throw "Stadtdaten nicht gefunden: $CityJson"
}

if (-not [string]::IsNullOrWhiteSpace($Godot)) {
    $ResolvedGodot = (Resolve-Path -LiteralPath $Godot).Path
    Write-Host "Godot: $ResolvedGodot"
}

Write-Host "Viewer: $ResolvedViewer"
Write-Host "Stadtdaten: $CityJson"
Write-Host "Der Viewer wird gestartet. Prüfen Sie Gebäude, Texturen, Farben und Steuerung."

$Process = Start-Process `
    -FilePath $ResolvedViewer `
    -ArgumentList @(
        ('"' + $CityJson + '"')
    ) `
    -WorkingDirectory $ProjectRoot `
    -NoNewWindow `
    -Wait `
    -PassThru

Write-Host ("ExitCode: {0}" -f $Process.ExitCode)

if ($Process.ExitCode -ne 0) {
    throw "Der Viewer wurde mit Fehlercode $($Process.ExitCode) beendet."
}

Write-Host "Der Viewer wurde regulär beendet. Sichtprüfung nicht vergessen."
