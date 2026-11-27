"""Build a matched Blender comparison and crop the original Studio evidence."""
from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image, ImageDraw, ImageFont, ImageOps

ASSET = Path(__file__).resolve().parents[1]
HAIR = ASSET.parent
WORK = HAIR / "work/v5"
REF = HAIR.parents[1] / "referencias"
OUT = ASSET / "validacion" / "studio"
INK, MUTED, PANEL = "#edf4ff", "#a8bddb", "#111d2c"


def font(size, bold=False):
    return ImageFont.truetype("segoeuib.ttf" if bold else "segoeui.ttf", size)


def put(canvas, path, box, crop=None):
    with Image.open(path) as source:
        picture = source.convert("RGB")
        if crop:
            picture = picture.crop(crop)
        x, y, width, height = box
        picture = ImageOps.contain(picture, (width, height), Image.Resampling.LANCZOS)
        canvas.paste(picture, (x + (width - picture.width) // 2, y + (height - picture.height) // 2))


def comparison():
    canvas = Image.new("RGB", (2060, 1740), "#0a1422")
    draw = ImageDraw.Draw(canvas)
    draw.text((43, 24), "Celestial Hair V5", font=font(52, True), fill=INK)
    draw.text((46, 95), "Silueta, capas y contraste entre mechones", font=font(26), fill=MUTED)
    columns = (42, 542, 1042, 1542)
    for x, name in zip(columns, ("Concepto ZAREK", "V3 · Propuesta C", "V4 · UGC", "V5 · UGC")):
        draw.text((x, 145), name, font=font(32, True), fill="#b8e6ff")
    rows = (
        ("frente", "Frente", "01-avatar-definitivo.png", (300,36,596,247)),
        ("espalda", "Espalda", "01-avatar-definitivo.png", (1195,36,1486,257)),
        ("perspectiva", "Tres cuartos · concepto auxiliar", "03-concepto-anterior-detalles.png", (97,906,203,1016)),
    )
    renders = HAIR / "v4" / "renders"
    for index, (key, label, reference, ref_crop) in enumerate(rows):
        y = 203 + index * 503
        draw.text((44, y), label, font=font(23, True), fill=INK)
        items = ((REF / reference, ref_crop), (renders / f"V3C_{key}.png", None),
                 (renders / f"V4_{key}.png", None), (ASSET / "renders" / f"V5_{key}.png", None))
        for x, (path,crop) in zip(columns,items):
            draw.rectangle((x,y+39,x+473,y+468),fill=PANEL)
            put(canvas,path,(x,y+39,474,430),crop or (59,116,1341,1259))
    canvas.save(ASSET / "renders" / "Comparacion_Concepto_C_V4_V5.jpg", quality=95, subsampling=0)


def studio():
    OUT.mkdir(parents=True, exist_ok=True)
    close = (570, 207, 1423, 833)
    wide = (410, 207, 1579, 833)
    for mode in ("neutra", "cine"):
        choices = [("general", wide)]
        choices += [(f"solo_{view}", close) for view in
                    ("frente", "trescuartos", "derecho", "nuca", "izquierdo")]
        choices += [(f"conjunto_{view}", close) for view in
                    (("frente", "trescuartos") if mode == "neutra" else ("trescuartos", "derecho", "nuca", "izquierdo"))]
        if mode == "neutra":
            choices += [(f"corona_{view}", close) for view in ("frente","trescuartos","derecho","nuca")]
        for key,crop in choices:
            name = key+"_"+mode
            with Image.open(WORK/f"{name}_raw.jpg") as source:
                assert source.size == (1920,1032), (name,source.size)
                source.crop(crop).save(OUT/f"{name}.jpg",quality=96,subsampling=0,optimize=True)
    for key,crop in (
        ("importacion", (0,65,800,760)), ("aft", None),
        ("anim_caminar", close), ("anim_correr", close), ("anim_saltar", close),
    ):
        with Image.open(WORK/f"{key}_raw.jpg") as source:
            image = source.crop(crop) if crop else source
            image.save(OUT/f"{key}.jpg",quality=96,subsampling=0,optimize=True)
    with Image.open(WORK/"general_neutra_raw.jpg") as source:
        source.crop((365,166,1624,834)).save(OUT/"calidad_q21.jpg",quality=96,subsampling=0,optimize=True)

    panels = (
        ("Flequillo · luz neutra", "solo_frente_neutra"),
        ("Nuca · luz neutra", "solo_nuca_neutra"),
        ("Corona y halo · luz cinematográfica", "conjunto_trescuartos_cine"),
    )
    canvas = Image.new("RGB",(1620,507),"#0a1422")
    draw = ImageDraw.Draw(canvas)
    for i,(label,file) in enumerate(panels):
        x = 18 + i*540
        draw.text((x+10,17),label,font=font(27,True),fill=INK)
        with Image.open(OUT/(file+".jpg")) as image:
            # Remove the HUD from the three panels. Individual captures retain it.
            shot = image.crop((97,0,image.width-97,image.height-60))
            shot = ImageOps.contain(shot,(510,438),Image.Resampling.LANCZOS)
            canvas.paste(shot,(x + (510-shot.width)//2,58))
    canvas.save(OUT/"Resumen_Studio_V5.jpg",quality=96,subsampling=0)


def hashes():
    entries = {}
    for directory in (ASSET/"renders", OUT):
        for path in sorted(directory.iterdir()):
            if path.suffix not in {".jpg",".png"}:
                continue
            with Image.open(path) as picture:
                picture.load()
                entries[path.relative_to(ASSET).as_posix()] = {
                    "size": list(picture.size), "sha256": hashlib.sha256(path.read_bytes()).hexdigest()
                }
    (ASSET/"validacion"/"imagenes.json").write_text(json.dumps(entries,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capturas", action="store_true", help="Recortar las capturas locales originales de work/v5.")
    args = parser.parse_args()
    comparison()
    if args.capturas:
        studio()
    if OUT.is_dir():
        hashes()
