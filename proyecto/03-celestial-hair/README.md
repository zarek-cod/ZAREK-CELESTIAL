# Celestial Hair V2

Rediseño del cabello de ZAREK CELESTIAL para Classic R15. El flequillo nace de una raya asimétrica y se abre sobre los ojos. La silueta combina ondas laterales hacia fuera con mechones largos y escalonados en la nuca. Los mechones plateados tienen raíces oscuras, cantos finos de carbón y reflejos azules localizados.

| Entrega | Archivos |
| --- | --- |
| Revisión artística | [Concepto original, V1 y V2](renders/comparacion_referencia.jpg) · [Estudio de los mechones](renders/lamina_mechones.jpg) · [Conjunto equipado](renders/lamina_conjunto.jpg) |
| Escenas editables | [MASTER](blender/CelestialHair_MASTER.blend) · [UGC](blender/CelestialHair_UGC.blend) · [Classic R15 con corona y halo](blender/CelestialHair_R15_Conjunto.blend) |
| Exportaciones UGC | [GLB con los mapas PBR](exportaciones/CelestialHair_UGC.glb) · [FBX](exportaciones/CelestialHair_UGC.fbx) |
| Mapas | [Color 1024](texturas/CelestialHair_BaseColor.png) · [Normal OpenGL 256](texturas/CelestialHair_Normal.png) · [Rugosidad 256](texturas/CelestialHair_Roughness.png) |
| Evidencias | [Informe](validacion/INFORME.md) · [Mediciones y hashes](validacion/resultados.json) · [Registro de horneado](validacion/build.log) · [Guía de importación local](roblox/LEEME.md) |

## Edición y reproducción

MASTER conserva 35 mechones editables, una base continua y las guías Bézier archivadas en la escena. Las guías sirven como referencia de las espinas, radios y giros. Para regenerar la geometría desde las espinas, edita los puntos, anchos y torsiones de `RIBBONS` en [build_hair.py](scripts/build_hair.py). Para retocar la escultura existente en Blender, edita directamente las mallas agrupadas de MASTER. El UGC es un accesorio rígido con una malla, un material y un atlas UV.

Desde esta carpeta, ejecuta `.\scripts\run.ps1` en PowerShell con Blender 5.2 y una GPU OptiX. Usa `-ReviewPython <ruta>` con Python y Pillow para reconstruir las láminas. Para rehacer también la comparación, obtén los binarios de [V1 en el historial](https://github.com/zarek-cod/ZAREK-CELESTIAL/tree/3c6b0b56cc480b6990942fb5c610641329a49c44/proyecto/03-celestial-hair) con Git LFS y copia `CelestialHair_UGC.blend` a `work/v1/blender/`. Ejecuta el script PowerShell con `-ReviewPython <ruta> -CompararV1`. Ambos conjuntos renderizados para la comparación se guardan en `work/`.

El ajuste estático de las tres piezas se midió en Blender. La revisión artística, la importación y el ajuste AFT de V2 en Roblox Studio, las animaciones y la validación de Marketplace siguen pendientes.
