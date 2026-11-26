# Celestial Hair V3 · selección artística

[Comparación A, B y C](renders/Comparacion_ABC.jpg) · [C junto al concepto definitivo](renders/Concepto_y_C.jpg) · [Investigación y licencias](INVESTIGACION.md)

| Propuesta | Diseño | Escena MASTER |
| --- | --- | --- |
| A · Angelical | Raya abierta, cortinas largas y nuca más extendida. | [Editable A](blender/CelestialHair_V3_A_MASTER.blend) |
| B · Celestial oscuro | Flequillo barrido, sien asimétrica y capas de contraste grafito y plata. | [Editable B](blender/CelestialHair_V3_B_MASTER.blend) |
| C · Concepto ZAREK | Flequillo blanco diagonal, puntas abiertas en las sienes y nuca poblada en dos alturas. | [Editable C](blender/CelestialHair_V3_C_MASTER.blend) |

Las tres escenas contienen jaulas por mechón y materiales con mapas empacados de color, rugosidad y altura de fibras. Las colecciones están organizadas por volumen. Para editar la forma del cabello, selecciona el mechón y entra en Edit Mode. La corona y el halo de referencia se pueden mostrar desde el Outliner de cada escena. El [informe](validacion/INFORME.md) registra las distancias y el alcance de la prueba de Studio.

## Reproducción

Con Blender 5.2 LTS y OptiX, ejecuta el generador desde esta carpeta. El modo `preview` permite inspeccionar la forma en baja resolución y `final` reconstruye las tres escenas, texturas y renders. Los GLB temporales se escriben en `../work/v3` y conservan la malla MASTER dividida por mechón. Usan color y rugosidad en Studio. Dentro de Blender el canal de altura alimenta el nodo Bump del material.

```powershell
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' -b --factory-startup --python-exit-code 1 --python .\scripts\produce.py -- final A B C
python .\scripts\comparar.py
```

`comparar.py` usa Pillow. Se conservan [V1](https://github.com/zarek-cod/ZAREK-CELESTIAL/tree/3c6b0b56cc480b6990942fb5c610641329a49c44/proyecto/03-celestial-hair) y [V2](https://github.com/zarek-cod/ZAREK-CELESTIAL/tree/8acbcdf92d4737bbadeb50b3842df79da7e25c3d/proyecto/03-celestial-hair). La retopología UGC queda para la propuesta seleccionada.
