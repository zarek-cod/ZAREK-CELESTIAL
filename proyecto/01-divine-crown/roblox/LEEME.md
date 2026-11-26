# Importación y prueba local de Divine Crown

El equipo importó y ajustó visualmente la corona con AFT en [DivineCrown_Test.rbxl](DivineCrown_Test.rbxl). Las animaciones y la validación oficial del Marketplace siguen pendientes. La secuencia siguiente permite repetir la prueba.

1. Crear un lugar local nuevo. No modificar proyectos existentes.
2. Usar File > Import 3D y elegir `exportaciones/DivineCrown_UGC.glb` o `.fbx`.
3. Desactivar **Upload to Roblox**. Scale Unit: **Stud**. Conservar orientación del archivo. No introducir una escala adicional de 100.
4. Confirmar que se obtiene una sola malla. Su tamaño esperado en Studio es X=1.80, Y=0.94, Z=1.63 studs. No importar luces, cámaras ni maniquíes de los .blend de exhibición.
5. Comprobar ColorMap, NormalMap OpenGL, RoughnessMap y MetalnessMap en SurfaceAppearance. El GLB usa empaquetado metallic-roughness estándar de glTF; los PNG independientes son los archivos que corresponden a cada campo Roblox. Si se usa SurfaceAppearance, vaciar TextureID. Material=Plastic, Transparency=0, Color=(1,1,1).
6. BaseColor: 1024² RGB. Normal: 256² RGB. Roughness, Metalness y EmissiveMask: 256², gris de 8 bits. `Normal_source1024.png` es fuente de edición; no usarla como NormalMap del artículo UGC.
7. Avatar > Accessory abre AFT. Elegir la malla, Accessory > Hat > Classic. Ajustar el punto al tope visible de la cabeza. El marcador de Blender es solo una referencia: importar attachments rígidos desde Blender no está soportado; AFT debe generar HatAttachment.
8. Revisar el límite Classic 3×4×3 centrado en attachment. Generar **MeshPart Accessory**. Mantener el pelo y el halo como pruebas futuras, cuando esos accesorios estén aprobados y modelados.
9. Seleccionar el Accessory y un modelo R15 con Humanoid. Ejecutar el contenido de `VerifyImportedCrown.luau` en Command Bar para la comprobación local de jerarquía y alineación. Este script queda fuera del accesorio; no se distribuye dentro del artículo Marketplace. No se ha ejecutado en esta entrega.
10. Usar los avatares y animaciones de AFT para caminar, correr, saltar y rotar la cabeza. Examinar frente, espalda y laterales; registrar capturas, clipping y escala. Estas pruebas siguen PENDIENTES.
11. Si Studio ofrece **EmissiveMaskContent**, asignar la máscara con los recursos que permita la sesión local y una fuerza propuesta de 0.65 (dentro de 0..40). EmissiveColor es el mapa RGB para glTF, no sustituye la máscara gris Roblox. El color azul sigue presente con emisión 0. No inventar IDs para los mapas; la subida de imágenes o mallas a Roblox no está autorizada.
12. Guardar .rbxl local y las evidencias en esta carpeta. Detenerse antes de cualquier upload, pago o publicación. La validación oficial Marketplace queda pendiente.

Fuentes vigentes archivadas en `../validacion/fuentes/`: rigid-specifications, rigid-export, blender, texture-specifications, surface-appearance, accessory-fitting-tool y validation-system.
