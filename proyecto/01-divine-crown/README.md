# ZAREK Divine Crown

Entrega de revisión del primer accesorio. Modelado real original, exclusivamente corona. **Studio/AFT y aprobación oficial siguen pendientes.**

## Abrir
- `blender/DivineCrown_MASTER.blend`: 22,476 triángulos evaluados, 132 piezas editables con biseles vivos y materiales de fuente.
- `blender/DivineCrown_UGC.blend`: 3,672 triángulos, atlas PBR empaquetado.
- `blender/DivineCrown_UGC_R15_fit.blend`: ajuste estático sobre las 15 partes oficiales del maniquí Classic.
- `exportaciones/DivineCrown_UGC.fbx` y `.glb`: una malla, sin cámaras/luces/maniquí.
- `DivineCrown_Presentacion.pdf`: presentación con vistas, detalles y comparación.
- `validacion/COMPATIBILIDAD_ROBLOX.md`: resultados y límites de lo comprobado.

## Reproducir
Windows / Blender 5.2.2 LTS instalado en `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`. Python bpy y NumPy vienen con Blender; no hacen falta paquetes de pago.

Desde esta carpeta: `powershell -File scripts/run.ps1 -Stage All`. Alternativamente ejecutar Blender con `-b --factory-startup --python-exit-code 1 --python scripts/build_crown.py -- build`, luego `-- render UGC`, `-- render MASTER`, y `scripts/validate.py`. Para la presentación usar el Python de Codex con Pillow y ReportLab: `scripts/package_delivery.py`. La captura de fuentes es opcional: `scripts/collect_evidence.py`.

Todos los objetos modelados se generan en esta carpeta. Unidades: 1 unidad Blender = 1 stud. Blender: +Z arriba, -Y frente. Roblox: +Y arriba. Importar como Stud.

## Alcance de la fidelidad
Se conservaron banda negra angular, gemas azules volumétricas, engastes y bordes de plata, puntas afiladas, simetría y firma Z. La vista posterior se interpreta a partir del concepto; no hay plano técnico dimensional. El recorte original es pequeño y contiene cabello/halo. El resultado se presenta para revisión visual del usuario; no se declara idéntico ni aprobado. El ajuste conjunto con cabello/halo requiere sus modelos futuros.

## Licencias y procedencia
Geometría y mapas nuevos creados para este proyecto, sin modelos comerciales ajenos. Referencias originales proporcionadas por el usuario, sin reasignar autoría ni licencia. Maniquí y rig descargados de Creator Hub de Roblox y sujetos a sus términos; originales preservados, uso como referencia. Blender es GPL y gratuito; su uso no impone la GPL sobre los modelos producidos. Git, Git LFS, Python, NumPy, Pillow y ReportLab son herramientas gratuitas. No se instaló software ni se utilizó servicio de pago.

## Revisión
Rama privada `accessory/01-divine-crown`. No se fusiona el PR ni se inicia el siguiente componente sin aprobación explícita. No se ha publicado ni comprado nada en Roblox.
