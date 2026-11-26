
param(
    [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
    [string]$ReviewPython
)

$ErrorActionPreference = 'Stop'
$asset = Split-Path $PSScriptRoot
$logs = Join-Path $asset 'validacion'
New-Item -ItemType Directory -Path $logs -Force | Out-Null

function Invoke-Stage([string]$Script,[string]$Log) {
    $scriptPath = Join-Path $PSScriptRoot $Script
    $logPath = Join-Path $logs $Log
    & $Blender -b --factory-startup --python-exit-code 1 --python $scriptPath *> $logPath
    if ($LASTEXITCODE -ne 0) {
        throw "Falló $Script. Consultar $logPath"
    }
}

Invoke-Stage 'build_hair.py' 'build.log'
Invoke-Stage 'validate_hair.py' 'validation.log'
Invoke-Stage 'render_hair.py' 'render.log'
if ($ReviewPython) {
    & $ReviewPython (Join-Path $PSScriptRoot 'layout_review.py')
    if ($LASTEXITCODE -ne 0) {
        throw 'Falló la composición de las láminas de revisión.'
    }
}
