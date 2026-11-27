# Validación local de Celestial Hair V5

## Qué cambió en la malla y el atlas

V5 conserva los controles de la propuesta C editados en V4. Se hundió la base de la coronilla bajo las capas exteriores y se recuperó un mechón de coronilla para cubrir la unión posterior. Se suavizaron las capas del flequillo y se recuperaron dos mechones interiores para evitar que la base dominara la vista frontal. La altura extrema de la nuca del UGC subió unos 0,078 studs. El volumen se redistribuyó hacia la parte media de los mechones.

La retopología muestrea posiciones y normales en las islas UV de la superficie subdividida del MASTER. Reserva más segmentos para las curvas de las capas visibles y las proximidades de la punta. El UGC mantiene 38 volúmenes cerrados dentro de una sola malla. Algunos encuentros entre puntas y coronilla aún se leen angulares en el primerísimo plano, sobre todo al mirar desde arriba. [Comparación con las versiones anteriores](../renders/Comparacion_Concepto_C_V4_V5.jpg).

El Base Color de 1.024 × 1.024 tiene filos casi negros estrechos hacia las zonas visibles, sombras azul noche en los giros y fibras longitudinales en plata. En algunos extremos se añadieron acentos azules. El normal tangente OpenGL Y+ se proyectó con Cycles desde el MASTER y se filtró a 512 × 512. Se normalizaron los vectores tras incorporar el detalle longitudinal. El GLB conserva tangentes y los mismos PNG de color y normal. La rugosidad va empaquetada en el canal G del mapa PBR del GLB. [Convención PBR de Roblox](https://create.roblox.com/docs/onboarding/artists#pbr-and-materials) · [Verificación de exportaciones](archivos.json).

## Medidas de Blender

| Prueba | Resultado |
| --- | --- |
| MASTER | 46 objetos y 196.320 triángulos evaluados. Misma subdivisión que V4 |
| UGC | 3.992 triángulos, 2.072 vértices, una malla, un material y un atlas UV |
| Topología | 0 aristas no manifold, 0 orientaciones inconsistentes, 0 caras degeneradas y 0 triángulos UV degenerados |
| Reimportación | FBX y GLB conservan el conteo, los límites y las normales personalizadas |
| Dimensiones X × Y × Z en ejes de Roblox | 1,877 × 1,340 × 1,458 studs antes de AFT |
| Ojos y cuero cabelludo | 0 de 176 rayos ocluidos por ojo. Cobertura en las seis alturas muestreadas |
| Corona | 0 pares de triángulos cruzados. Separación aproximada mínima de vértice en UGC de 0,0217 studs en el montaje del archivo |
| Halo | 0 pares cruzados. Separación aproximada mínima de vértice de 0,8124 studs en UGC |

El presupuesto oficial del accesorio rígido es de 4.000 triángulos. Las medidas del cabello Classic incluyen el volumen en torno a `HairAttachment`. Los renders se hicieron en Cycles con OptiX y una NVIDIA GeForce RTX 5060 Laptop GPU. [Especificación de accesorios rígidos](https://create.roblox.com/docs/avatar/rigid-accessories/specifications#geometry-and-budgets) · [Datos del ajuste](ajuste.json) · [Registro de Blender](produccion.log).

## Pruebas de Roblox Studio

Se importó el GLB con la subida desactivada y se generó el accesorio MeshPart en AFT con **Pelo · Bloque clásico**. En los tres R15 se verificaron `HairAttachment`, `RenderFidelity.Precise` y referencias `SurfaceAppearance` para color, normal y rugosidad. Se bajaron 0,030 studs las copias de Divine Crown en el RBXL V5. La revisión del borde del aro se hizo en vistas frontales, de tres cuartos, laterales y posterior. La separación visual con el halo se mantuvo. Se abrió y reprodujo una copia exacta del RBXL en el mismo equipo. [Importación local](studio/importacion.jpg) · [Resultado en AFT](studio/aft.jpg) · [Escenario reabierto](studio/reapertura.jpg).

Las capturas se hicieron con Studio en **Q21** y el cliente de prueba en **calidad 10**. Los ojos se ven completos de frente. Los bordes negros y las sombras de los mechones se ven bajo los dos perfiles de iluminación. Las fibras más finas y los reflejos azules se aprecian mejor en las vistas cercanas. [Calidad gráfica](studio/calidad_q21.jpg) · [Registro de Studio](Studio_resultados.txt).

| Configuración | Capturas |
| --- | --- |
| Cabello · neutra | [Frente](studio/solo_frente_neutra.jpg) · [Tres cuartos](studio/solo_trescuartos_neutra.jpg) · [Derecha](studio/solo_derecho_neutra.jpg) · [Nuca](studio/solo_nuca_neutra.jpg) · [Izquierda](studio/solo_izquierdo_neutra.jpg) |
| Cabello · cinematográfica | [Frente](studio/solo_frente_cine.jpg) · [Tres cuartos](studio/solo_trescuartos_cine.jpg) · [Derecha](studio/solo_derecho_cine.jpg) · [Nuca](studio/solo_nuca_cine.jpg) · [Izquierda](studio/solo_izquierdo_cine.jpg) |
| Cabello y corona | [Frente](studio/corona_frente_neutra.jpg) · [Tres cuartos](studio/corona_trescuartos_neutra.jpg) · [Perfil](studio/corona_derecho_neutra.jpg) · [Nuca](studio/corona_nuca_neutra.jpg) |
| Cabello, corona y halo | [Frente neutro](studio/conjunto_frente_neutra.jpg) · [Tres cuartos cinematográfico](studio/conjunto_trescuartos_cine.jpg) · [Derecha](studio/conjunto_derecho_cine.jpg) · [Nuca](studio/conjunto_nuca_cine.jpg) · [Izquierda](studio/conjunto_izquierdo_cine.jpg) |

En las pruebas en sitio de [caminar](studio/anim_caminar.jpg), [correr](studio/anim_correr.jpg) y [saltar](studio/anim_saltar.jpg) se reprodujeron 3 de 3 clips y se tomaron 20 muestras por movimiento. La mayor separación medida entre los anclajes equipados fue de 6,77 × 10⁻⁷ studs. Las pruebas cubren Classic R15 en esta escena. El Marketplace y la apertura en otro equipo siguen pendientes. Cero publicaciones en Roblox y cero Robux.
