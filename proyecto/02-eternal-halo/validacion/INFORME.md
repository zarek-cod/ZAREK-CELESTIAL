
# Validación de Eternal Halo

Ejecutada en Blender 5.2.2 LTS con bpy. Los renders se realizaron con Cycles y OptiX en una NVIDIA GeForce RTX 5060 Laptop GPU. [Resultados JSON](resultados.json) · [Registro de validación](validation.log) · [Registro de render](render.log).

| Comprobación | Resultado |
| --- | --- |
| UGC | 3.628 triángulos, 1.846 vértices fuente, 1 malla, 1 material y 1 conjunto UV. |
| MASTER y GOD MODE | 17.672 triángulos por variante. 79 componentes en cada fuente editable. GOD MODE exporta 2 mallas. |
| Topología y normales | Cero bordes abiertos, bordes no manifold, caras degeneradas o carcasas con volumen negativo según las comprobaciones locales. Las 18 carcasas cerradas de UGC incluyen los aros, destellos y trazos eléctricos; hay uniones visuales por solapamiento. |
| UV | Coordenadas en 0–1 y cero triángulos de UV degenerados. Los dos aros tienen bandas distintas. Las piezas de color sólido reutilizan zonas de color dentro del mismo atlas. |
| Tamaño en studs | X 2,464 × Y 0,518 × Z 2,459. Los extremos están dentro de la caja Classic Hat de 3 × 4 × 3 centrada en el origen indicado para HatAttachment. Las escalas Normal y Slender tienen límites más estrechos y quedan fuera del alcance de esta variante. |
| Texturas | Base Color RGB de 1024². Normal tangente OpenGL RGB y Roughness, Metalness y EmissiveMask de 256². Los tres últimos mapas son grises de 8 bits. |
| FBX y GLB | Reimportados en Blender. Se mantuvieron la escala, los triángulos, el número de mallas por variante, el material por malla y el UV. El GLB incorpora texturas de color, normal, metalness/roughness y una textura de emisión RGB aparte. |
| Iluminación | Se revisaron vistas neutras, perspectivas y detalles cinematográficos, más las láminas y el encuadre de cuerpo completo. El resplandor cinematográfico usa el compositor de Blender. |

## Corona, R15 y espacio para el cabello

Se usaron el modelo UGC de Divine Crown y las 15 piezas del maniquí oficial Classic R15 guardadas en la escena de ajuste de la corona. El origen del halo coincide con el punto de colocación en la parte superior de la cabeza de esa escena. El ajuste manual del RBXL de Divine Crown se documenta aparte y no se usó para medir las posiciones en Blender.

- BVH sobre las mallas trianguladas detectó cero cruces de superficie de UGC y MASTER con Divine Crown y el R15.
- El halo UGC queda al menos 0,0635 studs por encima de la cota de la punta más alta. La menor distancia observada al muestrear vértices contra superficies de la corona fue de 0,2235 studs. La separación vertical de MASTER fue de 0,0461 studs.
- En GOD MODE, la envolvente vertical calculada sobre cada vértice mantiene al menos 0,0034 studs sobre la cota máxima de la corona durante una vuelta completa. Se evaluaron además 30 fotogramas con cero cruces entre los grupos de los dos aros. Los cálculos corresponden a los pivotes y velocidades de la escena entregada.
- Como referencia para el cabello se reservó una envolvente de 0,83 studs de radio y 0,78 studs por encima del anclaje. Hace falta el modelo de Celestial Hair para verificar su ajuste con ambos accesorios. Cambiar el anclaje, tamaño o pivote requiere repetir la comprobación.

## Confirmación manual en Roblox Studio

El equipo del usuario confirmó la importación de Eternal Halo y el ajuste visual conjunto con Divine Crown mediante AFT en Roblox Studio. Aprobó provisionalmente la apariencia del conjunto. La escena guardada es [EternalHalo_Test.rbxl](../roblox/EternalHalo_Test.rbxl). Se comprobó la cabecera binaria y se registró el SHA-256. Los resultados de Blender corresponden a la escena de referencia original.

Quedan pendientes las pruebas de animación en Studio, el ajuste definitivo con el cabello y la validación oficial del Marketplace.

La clasificación propuesta es Hat Classic. Roblox exige que el punto de anclaje quede sobre la superficie visible de la cabeza. La geometría de este diseño queda elevada y el origen de referencia queda en la cabeza. AFT y la validación oficial deberán confirmar la admisibilidad de esta colocación. No se subió ningún activo a Roblox ni se gastaron Robux.

- [Especificaciones de accesorios rígidos](https://create.roblox.com/docs/avatar/rigid-accessories/specifications)
- [Accessory Fitting Tool](https://create.roblox.com/docs/avatar/accessory-fitting-tool)
- [Texturas PBR y máscara emisiva](https://create.roblox.com/docs/art/modeling/surface-appearance)
- [Sistema de validación oficial](https://create.roblox.com/docs/marketplace/validation-system)
- [Marketplace Policy](https://create.roblox.com/docs/marketplace/marketplace-policy)
