
# Prueba de Celestial Hair en Roblox Studio

Usar una copia local de [EternalHalo_Test.rbxl](../../02-eternal-halo/roblox/EternalHalo_Test.rbxl). Esa escena documenta el ajuste manual de corona y halo. Las posiciones del .blend combinado corresponden a la referencia Classic de Blender y sirven para reproducir el encaje.

1. Importar CelestialHair_UGC.glb como una sola malla con escala de importación Stud. Desactivar la subida a Roblox. Si se necesita FBX, comprobar la misma escala y asignar los mapas PBR independientes.
2. Comprobar X 1,717 × Y 1,270 × Z 1,423 studs y la orientación de la parte frontal. La escala de diseño es Classic.
3. Abrir Accessory Fitting Tool y elegir Hair y Classic. Usar la superficie superior visible de la cabeza como referencia para generar HairAttachment. El marcador del .blend indica dónde se tomó el origen, el anclaje se crea con AFT.
4. Equipar las tres piezas en el mismo R15. Comparar frente, perfil, nuca y coronilla con la [lámina de ajuste](../renders/lamina_conjunto.jpg). Verificar que los ojos estén libres, que las raíces entren dentro de la silueta del cabello, y que no atraviesen el aro interior ni las gemas.
5. Comprobar Plastic y opacidad total en el MeshPart. En SurfaceAppearance asignar ColorMap, NormalMap OpenGL y RoughnessMap. El cabello usa metalness 0. Si el importador no resuelve los mapas de manera local, registrar esa limitación sin subir activos ni gastar Robux.
6. Probar giro de cabeza, caminar, correr y saltar. Guardar la copia local y capturas de resultados. Las pruebas de esta guía quedan pendientes para Celestial Hair.

La separación mínima muestreada respecto a la corona en Blender fue 0,016 studs. Si el ajuste manual de la corona en Studio difiere, revisar en AFT el desplazamiento de Celestial Hair antes de proponer cambios en los accesorios aprobados. El cabello deja espacio de referencia para la futura máscara y pendientes. Probar esas piezas cuando existan.
