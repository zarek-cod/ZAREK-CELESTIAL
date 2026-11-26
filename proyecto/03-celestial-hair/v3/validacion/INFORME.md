# Celestial Hair V3 · revisión técnica

Las tres propuestas conservan el modelado MASTER editable. El análisis estático utiliza la escena de Blender con Classic R15 y la geometría de Divine Crown y Eternal Halo de la rama de dependencia.

| Medición | A · Angelical | B · Celestial oscuro | C · Concepto ZAREK |
| --- | ---: | ---: | ---: |
| Objetos editables incluidos en el cabello | 40 | 38 | 46 |
| Triángulos evaluados del MASTER | 172.896 | 160.992 | 197.856 |
| Pares de triángulos cruzados con corona | 0 | 0 | 0 |
| Pares de triángulos cruzados con halo | 0 | 0 | 0 |
| Distancia mínima muestreada de vértice a corona, en studs | 0,00345 | 0,00155 | 0,00347 |
| Oclusiones de ojo en Blender, sobre 176 rayos por ojo | 0 | 0 | 0 |
| Puntos de cuero cabelludo descubiertos, sobre 96 rayos en cada una de 6 alturas | 0 | 0 | 0 |

La holgura medida con la corona es pequeña. Las cifras corresponden a poses estáticas en Blender y la comparación muestra transiciones visibles en algunos solapes. El material de B tiene zonas grafito de mayor amplitud. El flequillo de C configura una diagonal más corta que A, con contraste menos marcado que en el dibujo.

[Mediciones A](A_ajuste.json) · [Mediciones B](B_ajuste.json) · [Mediciones C](C_ajuste.json) · [Registro de Blender/Cycles](produccion.log) · [Verificación de renders](renders.json)

## Prueba en Roblox Studio

- C se importó dos veces como modelo 3D local con la opción «Cargar a Roblox» desactivada. El importador de Studio mostró éxito y el Workspace contenía 46 MeshParts y 46 SurfaceAppearance. Se usó una copia de `EternalHalo_Test.rbxl` y se creó un R15 con HumanoidDescription.
- El primer GLB expuso un defecto de exportación. El mapa de altura de las fibras aparecía como normal en glTF y producía bandas brillantes. Se volvió a importar con albedo y rugosidad, y se alineó con HairAttachment sin el giro de la primera prueba. El mapa de altura sigue activo en el material del MASTER en Blender.
- Se revisó C estáticamente con dos accesorios clonados de la escena. En el R15 de Studio se probó un desplazamiento vertical adicional de 0,091 studs. El ojo bajo el mechón central quedó parcialmente cubierto y requiere ajuste después de elegir el diseño. El diagnóstico geométrico de Blender usa otra cabeza de referencia.
- A y B también se importaron al Workspace local, como mallas sueltas en un solo GLB con 78 MeshParts y 78 SurfaceAppearance confirmados. Su prueba de encaje sobre Classic R15 se realizó en Blender. La etapa de UGC, el montaje AFT, la prueba animada y el validador de Marketplace quedan pendientes de la selección artística. Se guardó la copia de prueba local como `../work/v3/CelestialHair_V3_Prueba_Local.rbxl`.

[Importador de Roblox Studio](https://create.roblox.com/docs/studio/importer) · [SurfaceAppearance](https://create.roblox.com/docs/reference/engine/classes/SurfaceAppearance) · [Script de la prueba en Studio](../scripts/studio_c_ajuste.luau) · [C en el R15 de Studio](Studio_C_frente.png) · [A y B junto a C en el Workspace](Studio_ABC.png)
