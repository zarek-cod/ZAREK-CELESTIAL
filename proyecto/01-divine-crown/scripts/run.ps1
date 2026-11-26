param([ValidateSet('All','Build','Render','Validate')][string]$Stage='All')
$ErrorActionPreference='Stop'
$blender='C:\Program Files\Blender Foundation\Blender 5.2\blender.exe'
$asset=Split-Path $PSScriptRoot -Parent
function Run-Blender([string]$Script,[string[]]$Options,[string]$Log){
    & $blender -b --factory-startup --python-exit-code 1 --python (Join-Path $PSScriptRoot $Script) -- @Options *> (Join-Path $asset ('validacion\'+$Log))
    if($LASTEXITCODE -ne 0){throw ('Blender failed; read '+$Log)}
}
if($Stage -in @('All','Build')){Run-Blender 'build_crown.py' @('build') 'build.log'}
if($Stage -in @('All','Validate')){Run-Blender 'validate.py' @() 'validate.log'}
if($Stage -in @('All','Render')){
    Run-Blender 'build_crown.py' @('render','UGC') 'render_ugc.log'
    Run-Blender 'build_crown.py' @('render','MASTER') 'render_master.log'
}
Write-Output 'Requested Blender stages completed. Studio and Marketplace checks are separate.'
