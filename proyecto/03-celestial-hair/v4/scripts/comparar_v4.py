"""Compose V4 review sheets from the project concept and actual local renders."""
from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont, ImageOps

ASSET=Path(__file__).resolve().parents[1]
RENDERS=ASSET/"renders"
REFS=ASSET.parents[2]/"referencias"
WORK=ASSET.parent/"work/v4"
OUT=ASSET/"validacion"
FONT=Path("C:/Windows/Fonts")
DARK="#0a1324"
TEXT="#edf5ff"
MUTED="#acc1d9"
BLUE="#82cdff"


def font(size,bold=False):
    return ImageFont.truetype(str(FONT/("arialbd.ttf" if bold else "arial.ttf")),size)


def board(width,height,title,note):
    canvas=Image.new("RGB",(width,height),DARK)
    ink=ImageDraw.Draw(canvas)
    ink.text((43,30),title,fill=TEXT,font=font(48,True))
    ink.text((44,94),note,fill=MUTED,font=font(24))
    return canvas,ink


def panel(canvas,path,box,crop=None):
    x,y,w,h=box
    with Image.open(path) as src:
        image=src.crop(crop) if crop else src.copy()
    image=ImageOps.contain(image.convert("RGB"),(w,h),Image.Resampling.LANCZOS)
    canvas.paste(image,(x+(w-image.width)//2,y+(h-image.height)//2))


def comparison():
    canvas,ink=board(1872,1696,"Celestial Hair V4","Comparación de silueta, flequillo y nuca. Las dos mallas comparten luz y encuadre.")
    col=[45,640,1235]
    for x,label in zip(col,("Concepto ZAREK","V3 · Propuesta C","V4 · UGC")):
        ink.text((x,147),label,fill=BLUE,font=font(30,True))
    for row,(view,label,reference,crop) in enumerate((
        ("frente","Frente","01-avatar-definitivo.png",(300,36,596,247)),
        ("espalda","Espalda","01-avatar-definitivo.png",(1195,36,1486,257)),
        ("perspectiva","Perspectiva · concepto auxiliar","03-concepto-anterior-detalles.png",(97,906,203,1016)),
    )):
        y=205+row*491
        ink.text((47,y),label,fill=TEXT,font=font(22,True))
        for x,path,rect in (
            (col[0],REFS/reference,crop),
            (col[1],RENDERS/f"V3C_{view}.png",(55,125,1345,1195)),
            (col[2],RENDERS/f"V4_{view}.png",(55,125,1345,1195)),
        ):
            panel(canvas,path,(x,y+36,578,419),rect)
    canvas.save(RENDERS/"Comparacion_Concepto_C_V4.jpg",quality=95,subsampling=0)


def verify():
    digests={}
    for path in sorted(RENDERS.glob("*")):
        if path.suffix.lower() not in {".jpg",".png"}:
            continue
        with Image.open(path) as image:
            image.load()
            assert min(image.size)>1200
            digests[path.name]={"size":list(image.size),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    (OUT/"renders.json").write_text(json.dumps(digests,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    comparison()
    verify()
