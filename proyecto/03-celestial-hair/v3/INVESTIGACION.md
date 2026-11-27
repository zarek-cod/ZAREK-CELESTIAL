# Investigación artística · Celestial Hair V3

## Técnica elegida

El bloque principal define primero el perfil del cráneo y el flujo desde la raya hacia las sienes y la nuca. Las capas gruesas aportan silueta. Los mechones secundarios cruzan y cubren sus arranques. Los surcos de textura siguen la longitud de cada mechón. El tutorial de YanSculpts sirvió para revisar la secuencia de bloqueo y escultura, y Disney Animation documenta el control jerárquico de guías y mechones para conservar formas estilizadas. [YanSculpts](https://www.youtube.com/watch?v=2HIqc02BBeY) · [Disney Animation](https://media.disneyanimation.com/uploads/production/publication_asset/175/asset/a13-kaur.pdf)

Construimos jaulas de sección oval asimétrica con volumen interior y puntas sostenidas por anillos pequeños. Catmull-Clark mantiene una malla de control editable. La base continua se esculpe aparte para cubrir la coronilla y sostener los solapes. Se revisaron las tres siluetas al inicio y después se agregaron capas superficiales. Los ajustes al aro mueven estaciones completas y dejan intacta su sección. El sombreado mate y anisotrópico usa atlas de color, rugosidad y altura de fibras. [Superficie de subdivisión de Blender](https://docs.blender.org/manual/en/5.2/modeling/modifiers/generate/subdivision_surface.html) · [Remallado y QuadriFlow](https://docs.blender.org/manual/en/5.2/modeling/meshes/retopology.html)

## Complementos y reconstrucción

| Herramienta | Licencia y viabilidad | Evaluación para este cabello |
| --- | --- | --- |
| HairMesh para Blender 5.1+ | GPL-3.0-or-later. Iconos CC0. | Traza contornos sobre la cabeza y forma quads con bucles regulares. Es un candidato para retocar transiciones y retopología, condicionado al control manual del perfil. No se incorporó código ni geometría de la herramienta. [Repositorio y licencia](https://github.com/riel-gab/hairmesh) |
| Blender GBH Tool | GPL-2.0-or-later en su repositorio. El autor distribuye también una versión comercial. | Puede generar mechones, fibras o tarjetas. Es útil para probar detalle terciario. Elegimos jaulas nativas sin dependencias para conservar la edición de los volúmenes. [Repositorio del autor](https://github.com/GixoXYZ/BlenderGBHTool) |
| TripoSR | MIT. El repositorio reporta unos 6 GB para una imagen con el ajuste predeterminado, sobre una RTX 5060 Laptop con 8.151 MiB medidos. | Es un candidato para una silueta aproximada. Requeriría comprobar CUDA y PyTorch en Windows y construir bucles editables a partir de una malla extraída. Es una evaluación documental, sin ejecución local. [Repositorio y requisitos](https://github.com/VAST-AI-Research/TripoSR) |
| Hunyuan3D-2 / mini | Tencent Hunyuan Community License con condiciones propias. El repositorio informa 6 GB para forma y 16 GB con texturas para la familia 2.0. | La forma sola podría caber. Una malla de reconstrucción necesitaría remodelado de mechones y retopología antes de encajar con las piezas de ZAREK. Es una evaluación documental. [Repositorio y licencia](https://github.com/Tencent-Hunyuan/Hunyuan3D-2) |
| TRELLIS.2 | MIT para el repositorio, con componentes auxiliares bajo sus propias licencias. La configuración oficial indica Linux y 24 GB de VRAM. | El flujo oficial excede la memoria disponible. La salida texturizada tampoco proporciona jaulas dirigibles por mechón. [Repositorio y requisitos](https://github.com/microsoft/TRELLIS.2) |

El frente y la espalda del concepto definitivo gobiernan C. Las dos imágenes adicionales se consultaron para entender capas, grosor y fibra. Las dos propuestas alternativas son originales. Todas las mallas y mapas entregados se construyeron para ZAREK con Blender y Python.
