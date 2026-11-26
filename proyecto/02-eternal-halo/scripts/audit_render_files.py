
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageChops

asset=Path(__file__).resolve().parents[1]
renders=asset/"renders"
axes=("frente","espalda","izquierda","derecha","perspectiva","detalle")
real_renders={f"{prefix}_{side}.png" for prefix in ("halo","conjunto") for side in axes}
real_renders.update(("conjunto_R15_completo.png","halo_ugc_neutro.png","godmode_frame_036.png"))
boards={"lamina_halo.jpg","lamina_conjunto.jpg","comparacion_referencia.jpg"}
assert real_renders|boards=={f.name for f in renders.iterdir() if f.is_file()}
index={}
for path in sorted(renders.iterdir()):
    with Image.open(path) as image:
        image.load()
        assert min(image.size)>=1000
        assert image.mode=="RGB" and any(hi-lo>100 for lo,hi in image.getextrema())
        index[path.name]={"size":list(image.size),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}

for name in ("EmissiveMask","Metalness","Roughness","Normal","BaseColor","EmissiveColor"):
    with Image.open(asset/f"texturas/{name}.png") as image:
        image.load()
        assert ImageChops.difference(image,Image.new(image.mode,image.size,image.getpixel((0,0)))).getbbox(),name

report={"renders_png":len(real_renders),"review_boards":len(boards),"files":index,
        "textures_nonuniform":True}
(asset/"validacion/render_files.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(f"PASS: decoded {len(real_renders)} Cycles PNG renders and {len(boards)} JPEG review boards")
