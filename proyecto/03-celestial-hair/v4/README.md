# Celestial Hair V4

La versión definitiva parte de la propuesta C y aplica el contraste de B en el atlas. El flequillo corregido deja visibles los dos ojos del maniquí Classic R15. El MASTER conserva los mechones editables y el UGC tiene una sola malla de 3.934 triángulos con un solo material PBR.

| Entrega | Archivos |
| --- | --- |
| Modelos de Blender | [MASTER editable](blender/CelestialHair_V4_MASTER.blend) · [UGC](blender/CelestialHair_V4_UGC.blend) |
| Exportaciones | [GLB con mapas PBR](exportaciones/CelestialHair_V4_UGC.glb) · [FBX](exportaciones/CelestialHair_V4_UGC.fbx) |
| Atlas | [Color](texturas/CelestialHair_V4_Color.png) · [Normal tangente](texturas/CelestialHair_V4_Normal.png) · [Rugosidad](texturas/CelestialHair_V4_Rugosidad.png) · [Altura de fibras del MASTER](texturas/CelestialHair_V4_Altura_MASTER.png) |
| Revisión artística | [Concepto, propuesta C y V4](renders/Comparacion_Concepto_C_V4.jpg) · [MASTER](renders/V4_MASTER.png) · [Frente](renders/V4_frente.png) · [Espalda](renders/V4_espalda.png) · [Perfil](renders/V4_perfil.png) · [Tres cuartos](renders/V4_perspectiva.png) |
| Conjunto en Cycles | [Luz neutra](renders/V4_conjunto_neutro.png) · [Luz cinematográfica](renders/V4_conjunto_cine.png) |
| Roblox Studio | [Escenario de prueba](roblox/CelestialHair_Test.rbxl) · [Tres R15](validacion/Studio_General.jpg) · [Conjunto cercano](validacion/Studio_Conjunto_neutro.jpg) · [Conjunto cinematográfico](validacion/Studio_Conjunto_cine.jpg) |
| Validación | [Informe](validacion/INFORME.md) · [Geometría y mapas](validacion/archivos.json) · [Ajuste Blender](validacion/ajuste.json) · [Registro de Studio](validacion/Studio_resultados.txt) |

## Revisar en Roblox Studio

Abre `CelestialHair_Test.rbxl` en Studio y pulsa **F5** para iniciar la presentación local. Haz clic en la vista 3D si el teclado sigue enfocado en el Explorador.

| Tecla | Vista o prueba |
| --- | --- |
| **0** | General con los tres maniquíes |
| **1** | Cabello individual |
| **2** | Cabello con Divine Crown |
| **3** | Cabello, Divine Crown y Eternal Halo |
| **V** | Frente, tres cuartos y nuca en la cámara seleccionada |
| **L** | Luz neutra o cinematográfica |
| **7 / 8 / 9** | Animaciones en sitio de caminar, correr y saltar |

La reapertura y el render se verificaron en el equipo de trabajo. Si otra instalación de Studio no resuelve las referencias de la importación local, el GLB de esta entrega contiene la malla y sus mapas. El proyecto fuente del halo conserva los otros dos accesorios del escenario. Importa en local con `Cargar a Roblox` desactivado y usa AFT en categoría **Pelo** y escala **Bloque clásico**. Los scripts adjuntos reproducen el montaje y la presentación.

## Reproducir Blender

Desde `03-celestial-hair`, con los archivos de Git LFS descargados, usa Blender 5.2 y Python con Pillow para la lámina. Los modos `measure` y `preview` permiten inspeccionar el ajuste antes de regenerar la entrega completa.

```powershell
& $BlenderExe -b -t 8 --python v4/scripts/build_v4.py -- final
& $BlenderExe -b --python v4/scripts/verificar_v4.py
python v4/scripts/comparar_v4.py
```

Los scripts de Studio se ejecutan en una copia local con la corona y el halo en `Workspace`, una vez generado el pelo mediante AFT. Ejecuta [creación](scripts/studio_crear_escena.luau) y [ajuste](scripts/studio_ajustar_escena.luau) en la barra de comandos. Inserta el código de [presentación](scripts/studio_presentacion.luau) en `StarterPlayerScripts/PresentacionV4`.
