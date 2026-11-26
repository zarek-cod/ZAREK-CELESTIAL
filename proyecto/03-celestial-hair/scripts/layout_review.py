
"""Build review boards from the original concept and output PNGs."""
from pathlib import Path
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont, ImageOps, ImageChops

A=Path(__file__).resolve().parents[1]
R=A/"renders"
REF=A.parents[1]/"referencias/01-avatar-definitivo.png"
ORIGINAL=A/"work/r15_iteracion01.png"
BG="#08111f"
PANEL="#142338"
WHITE="#edf6ff"
BLUE="#8bdfff"
MUTED="#a8bfd7"


def font(size,bold=False):
    return ImageFont.truetype("C:/Windows/Fonts/"+("arialbd.ttf" if bold else "arial.ttf"),size)


def board(size,title,detail):
    im=Image.new("RGB",size,BG)
    pen=ImageDraw.Draw(im)
    pen.rectangle((36,33,90,38),fill=BLUE)
    pen.text((36,55),title,font=font(42,True),fill=WHITE)
    pen.text((36,113),detail,font=font(22),fill=MUTED)
    return im,pen


def panel(im,pen,art,box,label):
    x,y,w,h=box
    source=art.convert("RGB")
    art=ImageOps.contain(source,(w-12,h-12),Image.Resampling.LANCZOS)
    pen.rectangle((x,y,x+w,y+h),fill=PANEL)
    im.paste(art,(x+(w-art.width)//2,y+(h-art.height)//2))
    pen.text((x,y+h+12),label,font=font(21,True),fill=BLUE)


def atlas():
    im,pen=board((1810,1100),"CELESTIAL HAIR / ESTUDIO DE MECHONES","Geometría MASTER en luz neutra y luz cinematográfica")
    panels=(("hair_frente","FRENTE"),("hair_espalda","ESPALDA"),("hair_superior","SUPERIOR"),
            ("hair_izquierda","LADO IZQUIERDO"),("hair_derecha","LADO DERECHO"),("hair_perspectiva","PERSPECTIVA"))
    for i,(name,label) in enumerate(panels):
        with Image.open(R/(name+".png")) as art:
            panel(im,pen,art,(36+i%3*588,157+i//3*460,562,407),label)
    im.save(R/"lamina_mechones.jpg",quality=94,subsampling=0)


def combined():
    im,pen=board((1810,1100),"CELESTIAL HAIR / AJUSTE DEL CONJUNTO","Classic R15 con Divine Crown y Eternal Halo. Renders del ajuste estático en Blender.")
    panels=(("conjunto_frente","FRENTE"),("conjunto_espalda","ESPALDA"),("conjunto_lateral","LATERAL"),
            ("r15_ojos","FLEQUILLO Y OJOS"),("conjunto_perspectiva","PERSPECTIVA"),("conjunto_R15_completo","R15 COMPLETO"))
    for i,(name,label) in enumerate(panels):
        with Image.open(R/(name+".png")) as art:
            panel(im,pen,art,(36+i%3*588,157+i//3*460,562,407),label)
    im.save(R/"lamina_conjunto.jpg",quality=94,subsampling=0)


def compare():
    im,pen=board((1620,1250),"CELESTIAL HAIR / CONCEPTO Y MODELO","Recortes del avatar definitivo junto a los renders del conjunto en Blender")
    with Image.open(REF) as source:
        refs=[source.crop((330,87,563,242)),source.crop((1223,91,1470,236))]
    for i,(art,name,label) in enumerate(zip(refs,("conjunto_frente","conjunto_espalda"),("FRENTE","ESPALDA"))):
        y=161+i*516
        panel(im,pen,art,(36,y,686,445),f"{label} / REFERENCIA")
        with Image.open(R/(name+".png")) as shot:
            width,height=shot.size
            cropped=shot.crop((int(width*.16),int(height*.37),int(width*.84),int(height*.93)))
            panel(im,pen,cropped,(747,y,837,445),f"{label} / MODELO EQUIPADO")
    im.save(R/"comparacion_referencia.jpg",quality=95,subsampling=0)


def iteration():
    if not ORIGINAL.exists():
        return
    im,pen=board((1590,850),"CELESTIAL HAIR / REVISIÓN DEL FLEQUILLO","Se levantaron las puntas y se abrió el espacio frente a los ojos del maniquí Classic.")
    with Image.open(ORIGINAL) as old:
        panel(im,pen,old,(36,157,742,620),"PRIMER ENCAJE EN R15")
    with Image.open(R/"r15_ojos.png") as new:
        panel(im,pen,new,(807,157,746,620),"RESULTADO FINAL EN R15")
    im.save(A/"validacion/iteracion_flequillo.jpg",quality=95,subsampling=0)


def verify_images():
    details={}
    for file in sorted(R.iterdir()):
        if file.suffix.lower() not in {".jpg",".png"}:
            continue
        with Image.open(file) as image:
            image.load()
            assert image.mode=="RGB" and min(image.size)>=1000
            assert any(hi-lo>85 for lo,hi in image.getextrema())
            details[file.name]={"size":list(image.size),"sha256":hashlib.sha256(file.read_bytes()).hexdigest()}
    assert sum(f.endswith(".png") for f in details)==15,len(details)
    for file in (A/"texturas").glob("*.png"):
        with Image.open(file) as im:
            constant=Image.new(im.mode,im.size,im.getpixel((0,0)))
            assert ImageChops.difference(im,constant).getbbox(),file
    (A/"validacion/archivos_render.json").write_text(json.dumps(details,indent=2)+"\n",encoding="utf-8")
    print("CELESTIAL_HAIR_RENDER_FILES_PASS",len(details))


if __name__=="__main__":
    atlas()
    combined()
    compare()
    iteration()
    verify_images()
