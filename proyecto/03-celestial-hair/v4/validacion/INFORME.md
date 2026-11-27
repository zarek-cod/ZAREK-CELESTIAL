# Validación de Celestial Hair V4

Pruebas locales realizadas en Blender 5.2.2 LTS y Roblox Studio. Los renders de Blender se generaron en Cycles con OptiX y una NVIDIA GeForce RTX 5060 Laptop GPU.

## Geometría, materiales y ajuste estático

Se mantuvieron los controles de los mechones de la propuesta C y se editaron las secciones del flequillo, el volumen dentro del aro de la corona y las puntas posteriores. El blanco celestial domina el albedo. El grafito, los cantos casi negros, los reflejos plata y los acentos azul eléctrico y cian están en el mapa de color. El atlas conserva la orientación de las fibras a lo largo de los mechones. En el UGC quedan transiciones angulares en algunos encuentros de la coronilla y la nuca cuando se inspecciona de cerca. [Comparación](../renders/Comparacion_Concepto_C_V4.jpg) · [Render del MASTER](../renders/V4_MASTER.png).

| Comprobación | Resultado |
| --- | --- |
| MASTER | 46 objetos editables y 195.552 triángulos evaluados |
| UGC | 1 malla, 1 material, 1 UV, 40 componentes cerrados, 2.047 vértices y 3.934 triángulos |
| Topología y UV | 0 aristas no manifold, 0 aristas con orientación inconsistente, 0 caras degeneradas y 0 triángulos UV degenerados |
| Reimportación Blender | FBX y GLB conservan malla única, material, UV, conteo y dimensiones |
| Dimensiones X × Y × Z | Exportación en ejes Roblox de 1,882 × 1,435 × 1,448 studs. `Handle.Size` medido en Studio de 1,823 × 1,410 × 1,403 studs |
| Visibilidad de los ojos | 0 de 176 rayos bloqueados por ojo en el MASTER y en el UGC, desde la vista frontal de referencia |
| Corona | 0 pares de triángulos que se cruzan. Distancia mínima aproximada de vértices del pelo a la corona de 0,0171 studs en MASTER y 0,0182 en UGC |
| Halo | 0 pares de triángulos que se cruzan. Distancias correspondientes de 0,7919 y 0,7971 studs |

El presupuesto vigente de un accesorio rígido es de 4.000 triángulos. En escala Classic, Hair admite 3 studs de ancho, hasta 2 arriba y 3 abajo, y hasta 1,5 delante y 2 detrás del anclaje. Las distancias de la tabla corresponden al montaje estático en Blender. [Mediciones](ajuste.json) · [Verificación de exportaciones](archivos.json) · [Especificación de accesorios rígidos](https://create.roblox.com/docs/avatar/rigid-accessories/specifications).

El normal UGC es RGB en espacio tangente OpenGL Y+, con base MikkTSpace. Cycles proyectó las normales del MASTER sobre la retopología por mechón. Después se filtraron y normalizaron los vectores, incorporando el gradiente longitudinal de las fibras. El mapa de altura se conecta al nodo Bump del MASTER. La verificación del GLB comprobó tangentes exportadas y coincidencia de los bytes de los tres PNG. El color es sRGB de 1.024 px, normal y rugosidad son mapas lineales de 256 px y la metalicidad es cero. [Verificación de mapas](archivos.json) · [Convención PBR de Roblox](https://create.roblox.com/docs/onboarding/artists#pbr-and-materials).

## Pruebas ejecutadas en Studio

1. Se importó el GLB en local con la subida desactivada. AFT generó un accesorio MeshPart usando **Pelo** y **Bloque clásico**, con `HairAttachment`. Al montar la escena se fijó explícitamente `AccessoryType.Hair` y se conservó el CFrame del anclaje de AFT. [Importador](Studio_Importacion_local.jpg) · [Confirmación de AFT](Studio_AFT.jpg).
2. Se equipó el mismo accesorio en tres R15 separados. Se confirmó `SurfaceAppearance` con referencias de color, normal y rugosidad en cada `Handle`. Se revisaron los dos ojos, los bordes de la corona y el espacio bajo el halo con cámaras cercanas y dos configuraciones de luz. [Cabello](Studio_Cabello.jpg) · [Con corona](Studio_Corona.jpg) · [Con corona y halo](Studio_Conjunto_neutro.jpg) · [Luz cinematográfica](Studio_Conjunto_cine.jpg) · [Nuca](Studio_Nuca.jpg).
3. Se elevó la corona unos 0,340 studs y el halo unos 0,347 studs en sus copias del escenario para alinear la separación con el montaje de Blender. Las tres configuraciones equipadas se volvieron a inspeccionar en la presentación local. La copia del RBXL se reabrió en el mismo equipo y mostró las tres configuraciones. [Escenario](../roblox/CelestialHair_Test.rbxl) · [Vista general tras reabrir](Studio_Reapertura.jpg).
4. Se reprodujeron caminar, correr y saltar mediante `Animator` en los tres R15. Se tomaron 20 muestras por prueba y se compararon las posiciones mundiales de los anclajes del accesorio y la cabeza. Estas pruebas reproducen las animaciones en el sitio y cubren el seguimiento de los anclajes.

| Animación | Clips activos | Muestras | Mayor desviación del anclaje |
| --- | --- | --- | --- |
| [Caminar](Studio_Caminar.jpg) | 3 de 3 | 20 | 6,745 × 10⁻⁷ studs |
| [Correr](Studio_Correr.jpg) | 3 de 3 | 20 | 6,750 × 10⁻⁷ studs |
| [Saltar](Studio_Saltar.jpg) | 3 de 3 | 20 | 6,750 × 10⁻⁷ studs |

Los resultados corresponden a Classic R15 en este escenario. La disponibilidad de las referencias en otro equipo y la validación oficial del Marketplace siguen pendientes. Importación, ajuste y pruebas se realizaron en local, con cero subidas a Roblox y cero Robux. [Registro de Studio](Studio_resultados.txt).
