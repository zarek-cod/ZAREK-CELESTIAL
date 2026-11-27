param(
    [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
    [string]$ReviewPython,
    [switch]$CompararV1
)

$ErrorActionPreference = 'Stop'
$asset = Split-Path $PSScriptRoot
$logs = Join-Path $asset 'validacion'
if ($CompararV1) {
    $v1 = Join-Path $asset 'work\v1\blender\CelestialHair_UGC.blend'
    if (-not $ReviewPython -or -not (Test-Path -LiteralPath $v1 -PathType Leaf)) {
        throw 'Comparar V1 requiere Python con Pillow y una copia del .blend UGC de V1 en work/v1/blender/.'
    }
}

function Invoke-Stage([string]$Script,[string]$Log,[string[]]$StageArgs = @()) {
    $scriptPath = Join-Path $PSScriptRoot $Script
    $logPath = Join-Path $logs $Log
    & $Blender -b --factory-startup --python-exit-code 1 --python $scriptPath @StageArgs *> $logPath
    if ($LASTEXITCODE -ne 0) {
        throw "Falló $Script. Consultar $logPath"
    }
}

Invoke-Stage 'build_hair.py' 'build.log'
Invoke-Stage 'validate_hair.py' 'validation.log'
Invoke-Stage 'render_hair.py' 'render.log'
if ($CompararV1) {
    Invoke-Stage 'render_hair.py' 'render_comparacion.log' @('--', 'compare')
}
if ($ReviewPython) {
    $layoutArgs = @()
    if ($CompararV1) { $layoutArgs = @('--compare') }
    & $ReviewPython (Join-Path $PSScriptRoot 'layout_review.py') @layoutArgs
    if ($LASTEXITCODE -ne 0) {
        throw 'Falló la composición de las láminas de revisión.'
    }
}
