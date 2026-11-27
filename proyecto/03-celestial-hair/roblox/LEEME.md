# Prueba de Celestial Hair V2 en Roblox Studio

Trabaja sobre una copia local de [EternalHalo_Test.rbxl](../../02-eternal-halo/roblox/EternalHalo_Test.rbxl), donde ya se ajustaron manualmente la corona y el halo. El [conjunto en Blender](../blender/CelestialHair_R15_Conjunto.blend) documenta el encaje estático de referencia para Classic R15.

1. Importa [CelestialHair_UGC.glb](../exportaciones/CelestialHair_UGC.glb) como una sola malla con unidad Stud y desactiva la subida a Roblox. Si usas [FBX](../exportaciones/CelestialHair_UGC.fbx), comprueba la escala y los mapas por separado.
2. Comprueba X 1,8974 × Y 1,3724 × Z 1,5662 studs y la orientación frontal. Abre Accessory Fitting Tool, elige Hair con la referencia Classic y genera HairAttachment sobre la cabeza. El marcador del .blend representa el origen de referencia.
3. Equipa el cabello, la corona y el halo en el R15. Compara frente, laterales y espalda con la [lámina del conjunto](../renders/lamina_conjunto.jpg). Revisa ojos y posición del pelo respecto al aro interior de la corona. La distancia mínima muestreada en Blender fue 0,00978 studs. El ajuste manual de corona y halo guardado en Studio puede tener otro desplazamiento.
4. Comprueba opacidad total y SurfaceAppearance bajo luz normal. El material usa [Base Color](../texturas/CelestialHair_BaseColor.png), [Normal OpenGL](../texturas/CelestialHair_Normal.png) y [Roughness](../texturas/CelestialHair_Roughness.png) con metalness 0. Si la sesión local no puede resolver los mapas, registra la limitación.
5. Prueba giros de cabeza, caminar, correr y saltar. Guarda la prueba y las imágenes en la copia local.

La importación, el aspecto de los materiales, AFT y las animaciones de V2 quedan pendientes porque el control de aplicaciones denegó el acceso a Roblox Studio. Las pruebas deben permanecer locales, sin publicación ni gasto de Robux.
