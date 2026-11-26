
param(
    [string]$Blender = 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe',
    [string]$ReviewPython
)

$ErrorActionPreference = 'Stop'
$asset = Split-Path $PSScriptRoot
$log = Join-Path $asset 'validacion'
New-Item -ItemType Directory -Path $log -Force | Out-Null

function Invoke-BlenderStage([string]$Script, [string]$LogName) {
    $file = Join-Path $PSScriptRoot $Script
    $destination = Join-Path $log $LogName
    & $Blender -b --factory-startup --python-exit-code 1 --python $file *> $destination
    if ($LASTEXITCODE -ne 0) {
        throw "Falló $Script. Consultar $destination"
    }
}

Invoke-BlenderStage 'build_halo.py' 'build.log'
Invoke-BlenderStage 'validate_halo.py' 'validation.log'
Invoke-BlenderStage 'render_halo.py' 'render.log'
if ($ReviewPython) {
    & $ReviewPython (Join-Path $PSScriptRoot 'layout_review.py')
    if ($LASTEXITCODE -ne 0) {
        throw 'Falló la composición de las láminas.'
    }
}
