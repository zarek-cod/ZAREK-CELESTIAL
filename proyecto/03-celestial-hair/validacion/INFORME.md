# Celestial Hair V2 · informe de validación

## Revisión artística

Se usaron [frente y espalda del concepto definitivo](../../../referencias/01-avatar-definitivo.png) y su [detalle de cabello](../../../referencias/accesorios/01-cabello-celestial.png). Los dos perfiles proceden del [concepto auxiliar](../../../referencias/03-concepto-anterior-detalles.png), ya que la ilustración definitiva no incluye esas vistas. La [lámina de tres columnas](../renders/comparacion_referencia.jpg) encuadra V1 y V2 con las mismas cámaras, el mismo R15, la misma corona y halo y la misma luz neutra. La iluminación y los elementos del concepto corresponden a la ilustración original.

La primera pasada del nuevo modelado definió el flujo asimétrico y las ondas de las sienes. Una segunda pasada corrigió la coincidencia de superficies provocado por la proyección rígida contra el aro de la corona. La tercera pasada aclaró las caras interiores, añadió dos mechones de transición en la nuca, redistribuyó cortes donde se curvan las puntas y horneó el relieve de MASTER. El primer plano sin corona mostró que el cuero cabelludo asomaba entre algunos mechones. En el encaje final se adaptó la base al cráneo Classic y se añadieron cortes al mechón principal para seguir la curvatura junto al aro. Las imágenes neutras muestran que las puntas y algunos encuentros de los mechones se ven más angulares en UGC que en MASTER. El contorno posterior es más abierto y los reflejos azules más discretos que en la ilustración. V1 se conserva en el historial y V2 queda pendiente de revisión artística.

## Modelado y PBR

- MASTER con espinas Bézier de puntos colocados por mechón, secciones variables con torsión y surcos de fibra. Tiene **221.984 triángulos**, 35 mechones editables y una base continua.
- UGC con muestreo adaptativo de las mismas espinas por longitud y curvatura. Tiene **3.984 triángulos**, 2.064 vértices, 36 componentes cerrados dentro de una sola malla y un material. El límite oficial para accesorios rígidos es 4.000 triángulos. [Especificaciones de Roblox](https://create.roblox.com/docs/avatar/rigid-accessories/specifications)
- Blender Cycles horneó normales tangentes por proyección del MASTER hacia el UGC a 1024 × 1024. Se separó temporalmente cada par correspondiente durante la proyección para evitar capturar el relieve del mechón vecino. El mapa resultante se filtró y renormalizó a 256 × 256, en convención OpenGL. El horneado se ejecutó en CPU. [Registro del proceso](build.log) · [Manual de Cycles](https://docs.blender.org/manual/en/latest/render/cycles/baking.html)
- Base Color RGB de 1024 × 1024 con fibras longitudinales, raíces oscuras, sombras entre capas y reflejos eléctricos localizados. Roughness de 256 × 256 con variación por fibra. El material UGC usa metalness 0. [Sistema de validación de Roblox](https://create.roblox.com/docs/marketplace/validation-system)

## Validación local

| Prueba | Resultado |
| --- | --- |
| Topología | Cero bordes abiertos o no manifold, caras degeneradas, inversiones de arista o componentes orientados hacia dentro en MASTER y UGC. |
| UV del UGC | Un canal, 36 islas y cero solapes de área positiva por encima de la tolerancia 5 × 10⁻⁹. Sin triángulos UV degenerados o coordenadas fuera de rango. |
| Classic Hair | 1,8974 × 1,3724 × 1,5662 studs en ejes Roblox X, Y, Z. Las extensiones relativas a HairAttachment del ensayo están dentro de los límites documentados. AFT debe crear y comprobar el anclaje real. |
| Reimportación | FBX y GLB conservan una malla, sus 3.984 triángulos y los límites geométricos medidos en Blender. Se verificaron en GLB los tres mapas PBR embebidos, metallic 0 y el descarte de caras posteriores. |
| R15 y accesorios | Cero pares de triángulos cruzados con corona, halo o cuerpo por debajo de la cabeza en MASTER y UGC. El contacto con el cuero cabelludo sirve para asentar las raíces. |
| Distancias de referencia | En UGC la distancia vértice-superficie mínima muestreada fue 0,00978 studs a la corona y 0,87520 al halo. En MASTER fue 0,02042 y 0,85978 studs respectivamente. Son resultados de la escena estática de Blender. |
| Coronilla | 768 rayos radiales en ocho alturas de la cabeza Classic, sin puntos de cuero cabelludo descubiertos en cada variante. |
| Ojos | Cero obstrucciones en 120 rayos frontales por ojo para cada variante. |
| Máscara futura | Cero obstrucciones en 120 rayos proyectados sobre la zona facial central reservada, para cada variante. |
| Pendientes futuros | En UGC, los puntos de referencia de los lóbulos están a 0,24951 y 0,22604 studs de la superficie del cabello. |
| Iluminación | 15 imágenes en Cycles OptiX con una NVIDIA GeForce RTX 5060 Laptop GPU. Comparación neutra sin compositor. Brillo óptico reducido en la iluminación cinematográfica del conjunto. |

[Resultados completos](resultados.json) · [Reimportación y mediciones](validation.log) · [Renders](render.log) · [Comparación](render_comparacion.log) · [Resoluciones e integridad de imágenes](archivos_render.json)

## Pendientes

El control de aplicaciones encontró abierta la escena de corona y halo, pero denegó el acceso a Roblox Studio. Siguen pendientes la importación de V2, su ajuste AFT con el conjunto guardado, la comprobación visual de SurfaceAppearance bajo luz normal de Roblox Studio, las animaciones y la validación oficial de Marketplace. La máscara y los pendientes aún no existen como accesorios, por lo que el muestreo de espacio indica disponibilidad en la escena estática. Su compatibilidad real requiere probarlos cuando existan. No se publicó el accesorio en Roblox.
