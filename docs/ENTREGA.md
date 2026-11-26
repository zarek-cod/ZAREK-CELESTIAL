# Entrega de revisión - Divine Crown

Repositorio privado: https://github.com/zarek-cod/ZAREK-CELESTIAL

PR en borrador, sin fusionar: https://github.com/zarek-cod/ZAREK-CELESTIAL/pull/1

Rama: accessory/01-divine-crown

## Rutas locales de producción

Raíz: `C:\Users\joels\Desktop\ZAREK-CELESTIAL\proyecto\01-divine-crown`

- `blender\DivineCrown_MASTER.blend`: maestro editable, 22.476 triángulos evaluados y 132 componentes.
- `blender\DivineCrown_UGC.blend`: versión UGC de 3.672 triángulos.
- `blender\DivineCrown_UGC_R15_fit.blend` y `DivineCrown_MASTER_R15_fit.blend`: escenarios de ajuste estático.
- `exportaciones\DivineCrown_UGC.fbx` y `.glb`: exportaciones reimportadas en Blender.
- `texturas\`: mapas BaseColor, Normal OpenGL, Roughness, Metalness y EmissiveMask; fuente normal de edición y RGB emisivo glTF aparte.
- `renders\`: 16 vistas reales, láminas por variante y comparación con referencia.
- `DivineCrown_Presentacion.pdf`: presentación de cuatro páginas, renderizada y revisada con Poppler.
- `validacion\`: informes, datos de geometría, comprobación de PBR serializado, BVH de cabeza, logs y fuentes oficiales con hashes.
- `scripts\run.ps1`: pipeline Blender reproducible. `build_crown.py` modela/hornea/exporta; `validate.py` verifica. `package_delivery.py` produce la presentación y los informes.
- `roblox\`: pasos exactos y verificador Luau externo, pendientes de ejecución en Studio.

## Resultado comprobado

Una malla / un material / un UV para la versión UGC. Geometría cerrada sin caras degeneradas; simetría salvo firma Z posterior. FBX y GLB conservan la escala y los triángulos. El GLB contiene BaseColor, Normal, MetallicRoughness y emisión selectiva. La prueba BVH estática sobre la cabeza oficial no detectó cruces de superficies. Los renders equipados muestran las 15 partes del maniquí oficial Classic, sin crear cabello ni halo.

Herramientas: Blender 5.2.2 LTS, bpy/Python 3.13, NumPy, Cycles/OptiX en RTX 5060 Laptop GPU; Python de Codex, Pillow, ReportLab, Poppler; Git, Git LFS y GitHub CLI. No se instaló software ni se utilizó servicio de pago.

## Pendiente, con motivo

Computer Use rechazó el acceso a Roblox Studio en tres intentos, antes y después de la confirmación del usuario y después del reinicio del runtime. Mensaje: `Computer Use was not approved to use Roblox Studio`.

Por tanto NO se han ejecutado importación Studio, generación AFT/HatAttachment, equipamiento Studio, animaciones de caminar/correr/saltar ni validador Marketplace. La colocación Blender es una prueba estática, no un reemplazo de esas pruebas. Ajuste Normal/Slender, compatibilidad con futuro pelo/halo y análisis exhaustivo de autointersecciones de las carcasas ensambladas siguen pendientes.

El modelo se entrega para revisión visual. Detalles posteriores interpretados desde el concepto, cuyo recorte de corona es pequeño. No se declara identidad exacta ni aprobación Marketplace. No hubo subida de activos a Roblox, compras ni gasto de Robux.

Se detiene exclusivamente en Divine Crown. El PR permanece en borrador y no se fusiona; el siguiente accesorio requiere aprobación explícita.
