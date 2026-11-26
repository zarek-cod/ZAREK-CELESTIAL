
"""Arrange the source artwork and the delivered Cycles renders for visual review."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageOps

A=Path(__file__).resolve().parents[1]
R=A/"renders"
REF=A.parents[1]/"referencias/01-avatar-definitivo.png"
BLACK="#08111e"
PANEL="#101e30"
WHITE="#edf5ff"
BLUE="#73dfff"
MUTED="#a9c3df"


def font(size,bold=False):
    name="arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts")/name),size)


def canvas(width,height,title,subtitle):
    board=Image.new("RGB",(width,height),BLACK)
    draw=ImageDraw.Draw(board)
    draw.rectangle((36,38,79,43),fill=BLUE)
    draw.text((36,58),title,font=font(40,True),fill=WHITE)
    draw.text((36,110),subtitle,font=font(19),fill=MUTED)
    return board,draw


def panel(board,draw,im,x,y,w,h,label):
    draw.rectangle((x,y,x+w,y+h),fill=PANEL)
    im=ImageOps.contain(im.convert("RGB"),(w-12,h-12),Image.Resampling.LANCZOS)
    board.paste(im,(x+(w-im.width)//2,y+(h-im.height)//2))
    draw.text((x,y+h+10),label,font=font(20,True),fill=BLUE)


def contacts(prefix,title,desc):
    board,draw=canvas(1800,1104,title,desc)
    labels=[("frente","FRENTE"),("espalda","ESPALDA"),("izquierda","LADO IZQUIERDO"),
            ("derecha","LADO DERECHO"),("perspectiva","PERSPECTIVA"),("detalle","DETALLE")]
    for i,(name,label) in enumerate(labels):
        with Image.open(R/f"{prefix}_{name}.png") as im:
            panel(board,draw,im,36+(i%3)*583,159+(i//3)*457,561,405,label)
    board.save(R/f"lamina_{prefix}.jpg",quality=94,subsampling=0)


def compare():
    board,draw=canvas(1800,1280,"ETERNAL HALO / REFERENCIA Y MODELO","Avatar definitivo frente a la corona y el halo equipados en el maniquí Classic R15")
    with Image.open(REF) as src:
        source_front=src.crop((268,0,636,212))
        source_back=src.crop((1152,0,1530,215))
    for i,(ref,side,label) in enumerate([(source_front,"frente","FRENTE"),(source_back,"espalda","ESPALDA")]):
        y=158+i*482
        panel(board,draw,ref,36,y,670,416,f"{label} / RECORTE DE LA REFERENCIA")
        with Image.open(R/f"conjunto_{side}.png") as im:
            panel(board,draw,im,740,y,1023,416,f"{label} / RENDER CYCLES")
    draw.text((36,1157),"Se conservan el doble anillo, los perfiles de luz y los destellos. El halo inferior se inclina 9°.",font=font(22),fill=WHITE)
    draw.text((36,1200),"Las descargas del concepto se traducen a trazos estáticos en UGC. El cabello queda para una comprobación posterior.",font=font(20),fill=MUTED)
    board.save(R/"comparacion_referencia.jpg",quality=95,subsampling=0)


if __name__=="__main__":
    contacts("halo","ETERNAL HALO / VISTAS DEL ACCESORIO","Vistas ortogonales del UGC en luz neutra y detalles del MASTER en luz cinematográfica")
    contacts("conjunto","ETERNAL HALO + DIVINE CROWN","Dos accesorios UGC equipados en Blender sobre el maniquí oficial Classic R15")
    compare()
    print("ETERNAL_HALO_REVIEW_BOARDS_PASS")
