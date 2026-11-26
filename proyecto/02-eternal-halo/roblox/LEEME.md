
# Eternal Halo en Roblox Studio

El equipo confirmó el ajuste visual manual del halo y la corona en [EternalHalo_Test.rbxl](EternalHalo_Test.rbxl). Los pasos permiten repetir la prueba. Animaciones y validación del Marketplace siguen pendientes.

## UGC estático

1. Abrir una copia local de DivineCrown_Test.rbxl e importar EternalHalo_UGC.glb o EternalHalo_UGC.fbx en studs, con la subida a Roblox desactivada.
2. Comprobar una sola malla y el tamaño aproximado 2,464 × 0,518 × 2,459 studs (X, Y, Z). Conservar la orientación y la escala respecto a la corona usada en la escena.
3. Abrir AFT, elegir Hat y Classic, y generar el accesorio. Colocar el HatAttachment en la superficie superior visible de la cabeza. Usar el desplazamiento de la malla para mantener ambos aros encima de la corona.
4. Revisar el ajuste desde los cuatro lados, con la corona y el halo equipados sobre el mismo R15. Comprobar el árbol del accesorio, sus dimensiones y la posición del attachment. Guardar una copia local de la escena y las vistas de cada prueba.
5. Revisar Plastic, opacidad total, vértices blancos y una instancia SurfaceAppearance. Eternal Halo usa BaseColor, Normal OpenGL, Roughness, Metalness y la máscara gris EmissiveMask. La textura RGB EmissiveColor corresponde al GLB. Confirmar visualización sin emisión y con emisión antes de fijar su intensidad.
6. Quedan pendientes las animaciones en Studio, el ajuste con futuro cabello y la validación oficial del Marketplace.

## GOD MODE en una experiencia

Los aros Zenith y Meridian tienen mallas y pivotes independientes. El GLB y el FBX guardan la pose de reposo. En el .blend los pivotes permanecen alineados con cada aro y los nodos PreviewSpin dan una vuelta y dos vueltas en sentido opuesto cada diez segundos. Reproducir los fotogramas 1–240 en Blender muestra la prueba de rotación.

Consultar [god_mode_rig.json](god_mode_rig.json) para las matrices de reposo y las ocho posiciones FX. Las posiciones se expresan en el espacio local del pivote de cada aro y en studs. El eje local +Z de Blender corresponde a +Y en glTF. Para ajustar una posición local a glTF, transformar (x, y, z) a (x, z, -y). Verificar la conversión y los pivotes en el importador de Studio antes de conectarlos al HatAttachment.

Los puntos FX se pueden replicar como Attachments hijos de cada MeshPart. Con ellos quedan definidos los orígenes para ParticleEmitter y los pares de Attachment0/Attachment1 para Beam cuando se implementen los efectos propios del juego. Los scripts, partículas y rayos dinámicos son trabajo futuro de la experiencia. La geometría eléctrica estática ya está incluida también en UGC. Las pruebas de rotación de esta entrega se ejecutaron en Blender.
