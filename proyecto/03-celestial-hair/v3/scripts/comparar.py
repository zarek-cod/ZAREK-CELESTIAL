"""Create the V3 contact sheets from the actual Blender render outputs."""
from pathlib import Path
import hashlib
import json
from PIL import Image, ImageDraw, ImageFont, ImageOps

asset = Path(__file__).resolve().parents[1]
renders = asset / "renders"
references = asset.parents[2] / "referencias"
font_dir = Path("C:/Windows/Fonts")
background = "#0b1322"
white = "#edf6ff"
muted = "#b3c5d9"
accent = "#8fd3ff"


def font(size, bold=False):
    return ImageFont.truetype(str(font_dir / ("arialbd.ttf" if bold else "arial.ttf")), size)


def title(size, label, description):
    canvas = Image.new("RGB", size, background)
    draw = ImageDraw.Draw(canvas)
    draw.text((42,30), label, font=font(50,True), fill=white)
    draw.text((44,99), description, font=font(23), fill=muted)
    return canvas, draw


def panel(canvas, file, box, crop=None):
    x,y,w,h=box
    with Image.open(file) as original:
        source=original.crop(crop) if crop else original
        shot=ImageOps.contain(source.convert("RGB"),(w,h),Image.Resampling.LANCZOS)
    canvas.paste(shot,(x+(w-shot.width)//2,y+(h-shot.height)//2))


labels=["A · Angelical", "B · Celestial oscuro", "C · Concepto ZAREK"]
canvas,d=title((1820,2240),"Celestial Hair V3","Tres esculturas MASTER sobre Classic R15, con la misma luz y cámara en cada fila.")
for i, label in enumerate(labels):
    d.text((44+i*580,152),label,font=font(32,True),fill=accent)
for j,(view,label) in enumerate([
    ("frente","Frente"),("espalda","Espalda"),("perspectiva","Perspectiva"),("conjunto","Con Divine Crown y Eternal Halo"),
]):
    top=205+j*503
    d.text((44,top),label,font=font(23,True),fill=white)
    for i,code in enumerate("ABC"):
        panel(canvas,renders/f"{code}_{view}.png",(42+i*580,top+37,557,449))
canvas.save(renders/"Comparacion_ABC.jpg",quality=94,subsampling=0)

canvas,d=title((1690,1460),"Propuesta C · concepto ZAREK","Frente y espalda del concepto definitivo junto al modelo con corona y halo.")
original=references/"01-avatar-definitivo.png"
for row,(view, art_crop) in enumerate([
    ("frente",(311,40,582,224)),("espalda",(1202,42,1486,247))
]):
    y=157+row*645
    d.text((43,y),"Concepto definitivo",font=font(29,True),fill=accent)
    d.text((871,y),"Propuesta C en Blender",font=font(29,True),fill=accent)
    panel(canvas,original,(42,y+48,775,567),art_crop)
    panel(canvas,renders/f"C_{view}_equipado.png",(862,y+48,775,567),(222,240,1178,1110))
canvas.save(renders/"Concepto_y_C.jpg",quality=94,subsampling=0)

images={}
for path in sorted(renders.iterdir()):
    if path.suffix.lower() not in {".jpg",".png"}:
        continue
    with Image.open(path) as image:
        image.load()
        if image.mode!="RGB" or min(image.size)<1300:
            raise ValueError(f"Unexpected output {path}")
        images[path.name]={"size":image.size,"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
assert len(images)==16, images.keys()
(asset/"validacion"/"renders.json").write_text(json.dumps(images,indent=2)+"\n",encoding="utf8")
