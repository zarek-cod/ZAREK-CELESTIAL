# Historial de mejoras

1. Bloque inicial: geometría original de joyería, 3672 triángulos UGC. Vista real conservada en validacion/iteration01.png. Detectadas agujas demasiado altas y reflejos poco legibles.
2. Bajadas las agujas de 1.00 a 0.78 studs y ajustado el estudio de reflejos. Corregida la simetría de los cristales intermedios.
3. El render UGC reveló metales negros por horneado Diffuse. Evidencia fallida conservada en iteration02_failed_metal_bake.png. Sustituido por pase Emission del color base, independiente de metalness.
4. Inspeccionado GLB real: se reemplazó la mezcla de nodos de emisión por mapa RGB explícito para conservar una emisión selectiva.
5. Sustituido bake normal agregado por selección de cada una de las 131 piezas del maestro y su correspondiente carcasa UGC.
6. El render del maniquí reveló que la animación importada restablecía la posición del padre. Desactivada la animación de referencia del FBX y añadida aserción de cabeza en origen antes del render. Repetidas las vistas equipadas.
7. Reimportación FBX/GLB y prueba BVH de cabeza repetidas sobre la versión corregida. Renders y reportes finales publicados en rama de revisión, sin fusionar main.
