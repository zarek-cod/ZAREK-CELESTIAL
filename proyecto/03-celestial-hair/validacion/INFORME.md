
# Validación de Celestial Hair

El modelo se construyó y comprobó en Blender 5.2.2 LTS. Las vistas se renderizaron con Cycles, OptiX y una NVIDIA GeForce RTX 5060 Laptop GPU. [Resultados JSON](resultados.json) · [Construcción](build.log) · [Validación](validation.log) · [Render](render.log).

| Prueba | Resultado |
| --- | --- |
| Presupuesto UGC | 3.976 triángulos de un máximo documentado de 4.000. 2.092 vértices, una malla, un material y un UV. |
| Maestro | 55.536 triángulos. 51 mechones editables y una base cerrada. |
| Geometría y orientación | Cero aristas abiertas, no manifold o con orientación inconsistente, cero caras degeneradas y cero carcasas con volumen negativo en ambas variantes. Las capas se superponen para formar el cabello. Esta comprobación no mide todas las intersecciones entre mechones. |
| UV del UGC | 52 islas en cuadros separados. Cero coordenadas fuera de 0–1, triángulos UV degenerados y solapamientos de área superior a 5 × 10⁻⁹ del atlas. |
| Dimensiones | X 1,717 × Y 1,270 × Z 1,423 studs en ejes de Roblox. Comprobado además contra los márgenes asimétricos de Hair Classic desde el origen propuesto. |
| PBR | Base Color RGB de 1024², Normal OpenGL tangente RGB de 256² y Roughness gris de 8 bits de 256². Metalness 0, adecuado para un material dieléctrico. |
| Reimportación | FBX y GLB reimportados en Blender. Mantuvieron el número de triángulos, dimensiones, un material y un UV. Se comprobó el binario GLB y los tamaños de color, normal y rugosidad empaquetada. |

El Maestro genera las hendiduras de fibra como parte del perfil tridimensional de cada mechón. El mapa tangente UGC implementa la misma función de relieve en el atlas a partir de sus pendientes, sin necesidad de horneado por proyección. El color y la rugosidad usan la misma dirección de fibra. La silueta y los cambios de perfil grandes se conservan en malla.

## Divine Crown, Eternal Halo y Classic R15

La prueba usa las piezas reales de la escena conjunta en Blender de Eternal Halo, con las 15 piezas del maniquí oficial y el origen de colocación en la parte superior de la cabeza. Los RBXL manuales de los dos accesorios anteriores corresponden a pruebas separadas en Studio.

- El BVH triangulado dio cero pares de intersección con Divine Crown, Eternal Halo y el cuerpo fuera de la cabeza, tanto en MASTER como en UGC. La menor distancia muestreada entre vértice y superficie de UGC fue 0,0162 studs respecto a la corona y 0,8448 studs respecto al halo.
- La cabeza cruza la base y raíces de los mechones que se integran bajo el peinado. Se registraron 1.746 pares de triángulos en UGC y 4.281 en MASTER. El contacto es intencional para asentar el cabello. La oclusión de ojos y el contorno visible se comprobaron por separado.
- El muestreo frontal del R15 dio 0 oclusiones sobre 120 rayos por ojo en las regiones definidas, y 0 de 120 en la región central reservada para máscara. Dos puntos de referencia bajo las patillas quedan a 0,202 y 0,170 studs del cabello, a izquierda y derecha. La máscara y los pendientes finales harán falta para verificar su ajuste.
- Las primeras vistas tapaban parcialmente los ojos. Se levantaron las puntas, se ajustaron las raíces y el abanico lateral, y se añadieron cuatro mechones a la coronilla. El BVH mostró 146 cruces de la corona en una iteración intermedia. Tras ajustar la transición del aro quedaron 12 en un mechón. Se corrigieron con el ajuste de su trayectoria y el muestreo de su punta. [Comparación del flequillo](iteracion_flequillo.jpg).

## Pruebas pendientes

Se detectó la ventana de EternalHalo_Test.rbxl abierta, pero Computer Use devolvió «Computer Use was not approved to use Roblox Studio». Quedan pendientes la importación de Celestial Hair, la creación de HairAttachment con AFT, el ajuste de las tres piezas juntas en Studio, las animaciones y el validador del Marketplace. Las pruebas registradas aquí corresponden a Classic R15 en Blender. No hubo subidas a Roblox ni gasto de Robux.

- [Accesorios rígidos, dimensiones Hair y anclajes](https://create.roblox.com/docs/avatar/rigid-accessories/specifications)
- [Texturas y UV](https://create.roblox.com/docs/art/modeling/texture-specifications)
- [Validación y presupuesto por mapas](https://create.roblox.com/docs/marketplace/validation-system)
- [Exportación de accesorios rígidos](https://create.roblox.com/docs/avatar/rigid-accessories/export)
- [Plantillas y maniquíes de Roblox](https://create.roblox.com/docs/avatar/resources)
