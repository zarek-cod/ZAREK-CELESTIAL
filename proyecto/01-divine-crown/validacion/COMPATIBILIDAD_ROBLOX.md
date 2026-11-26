# Compatibilidad Roblox - Divine Crown

Se verificó la geometría en Blender. El equipo del usuario importó Divine Crown y ajustó su colocación visual manualmente con Accessory Fitting Tool (AFT) en Roblox Studio. Animaciones y validación oficial del Marketplace pendientes.

- Categoría propuesta: Hat. Escala de ajuste: Classic R15.
- Una malla, un material, un UV; 3672 triángulos y 2090 vértices fuente. GLB divide vértices por costuras: 6748 vértices, mismo número de triángulos.
- Tamaño Roblox esperado: X=1.80, Y=0.94, Z=1.63 studs. Centro de attachment propuesto en (0,0,0). Límite Classic Hat consultado: 3×4×3 centrado en attachment. Normal/Slender no se han probado.
- 131 carcasas cerradas ensambladas en la única malla. Ninguna con volumen no positivo; 0 bordes abiertos/no manifold y 0 caras degeneradas. Las piezas superpuestas no son una unión booleana; el análisis exhaustivo de autointersecciones no se ha ejecutado.
- 0 UV fuera de 0..1, 0 triángulos de área UV cero. No se afirma una prueba exacta de solapamientos UV.
- Simetría bilateral de cuerpo verificada. La firma Z posterior introduce 20 vértices intencionalmente asimétricos.
- Normal OpenGL tangente horneada desde biseles del maestro, separando las 131 piezas para evitar contaminación de rayos entre vecinas.
- BaseColor RGB 1024². Normal RGB 256²; Roughness/Metalness/EmissiveMask gris 256². La fuente Normal_source1024 no se incluye en la configuración UGC.
- Emisión propuesta: 0.65. La documentación permite máscaras emisivas de avatar y fuerza 0..40. Su importación y apariencia reales en Studio no están verificadas. glTF contiene una textura emisiva RGB independiente; Roblox requiere su máscara gris.
- El marcador de Blender documenta el origen de referencia. La jerarquía final y las propiedades del HatAttachment quedan por verificar.
- Verificadas reimportaciones FBX y GLB en Blender: escala y 3672 triángulos preservados; una malla, un material, un UV, sin rig. Esto no constituye una importación en Studio.
- Cabeza del maniquí oficial Classic: 0 cruces de superficies por BVH en ajuste estático. Distancia mínima muestreada en vértices: 0.0583 studs. Los renders de ajuste mantienen 15 partes oficiales y desactivan animaciones de transformación del FBX.
- Pendientes: caminar, correr, saltar, probar otras escalas, verificar la compatibilidad definitiva con el cabello y realizar la validación oficial del Marketplace.

## Prueba manual en Roblox Studio

El equipo del usuario confirmó la importación y el ajuste visual con AFT. La escena se guardó como [DivineCrown_Test.rbxl](../roblox/DivineCrown_Test.rbxl). Se comprobaron la cabecera y el SHA-256 del archivo. El verificador Luau queda pendiente de ejecución.

## Fuentes oficiales consultadas 25/11/2026 - America/Lima
- https://create.roblox.com/docs/avatar/rigid-accessories/specifications
- https://create.roblox.com/docs/art/modeling/texture-specifications
- https://create.roblox.com/docs/art/modeling/surface-appearance
- https://create.roblox.com/docs/marketplace/validation-system
- https://create.roblox.com/docs/avatar/rigid-accessories/export
- https://create.roblox.com/docs/avatar/accessory-fitting-tool

La página general de rígidos menciona 2048², mientras que el sistema de validación especifica 1024 para ColorMap y 256 para Normal/Metalness/Roughness. Se aplicó el presupuesto más conservador por campo; snapshots íntegros y SHA256 están en validacion/fuentes/.
