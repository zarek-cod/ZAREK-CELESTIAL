"""Compose the V2 review boards from original artwork and actual Cycles renders."""

from pathlib import Path
import argparse
import hashlib
import json

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ASSET = Path(__file__).resolve().parents[1]
RENDERS = ASSET / "renders"
REFERENCES = ASSET.parents[1] / "referencias"
BG = "#08111f"
PANEL = "#111e30"
WHITE = "#edf6ff"
BLUE = "#8bdfff"
MUTED = "#a8bfd7"


def font(size, bold=False):
    file = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(f"C:/Windows/Fonts/{file}", size)


def board(size, title, description):
    image = Image.new("RGB", size, BG)
    pen = ImageDraw.Draw(image)
    pen.text((42, 32), title, font=font(48, True), fill=WHITE)
    pen.text((44, 98), description, font=font(24), fill=MUTED)
    return image, pen


def place(image, pen, art, x, y, width, height):
    panel = ImageOps.contain(art.convert("RGB"), (width - 12, height - 12), Image.Resampling.LANCZOS)
    pen.rectangle((x, y, x + width - 1, y + height - 1), fill=PANEL)
    image.paste(panel, (x + (width - panel.width) // 2, y + (height - panel.height) // 2))


def render_board(output, title, description, panels):
    rows = (len(panels) + 2) // 3
    image, pen = board((1812, 150 + 458 * rows + 16), title, description)
    for i, (name, label) in enumerate(panels):
        x, y = 42 + i % 3 * 582, 150 + i // 3 * 458
        with Image.open(RENDERS / (name + ".png")) as art:
            place(image, pen, art, x, y, 564, 405)
        pen.text((x + 3, y + 416), label, font=font(22, True), fill=BLUE)
    image.save(RENDERS / output, quality=94, subsampling=0)


def compare():
    image, pen = board(
        (1812, 2616),
        "Celestial Hair · revisión V2",
        "Concepto ZAREK y dos versiones sobre Classic R15. V1 y V2 comparten cámara, escala y luz neutra.",
    )
    for i, label in enumerate(("CONCEPTO ZAREK", "CELESTIAL HAIR V1", "CELESTIAL HAIR V2")):
        pen.text((42 + i * 582, 164), label, font=font(27, True), fill=BLUE if i == 2 else WHITE)
    front_back = "01-avatar-definitivo.png"
    side = "03-concepto-anterior-detalles.png"
    rows = (
        ("frente", "Frente", front_back, (321, 88, 568, 228), (85, 235, 1115, 1040)),
        ("espalda", "Espalda", front_back, (1207, 91, 1480, 245), (85, 235, 1115, 1040)),
        ("izquierda", "Lateral izquierdo · perfil auxiliar", side, (100, 931, 195, 1002), (85, 235, 1115, 1040)),
        ("derecha", "Lateral derecho · perfil auxiliar", side, (1064, 930, 1157, 1002), (85, 235, 1115, 1040)),
        ("detalle", "Detalle del flequillo y los bordes", "accesorios/01-cabello-celestial.png", None, (72, 285, 1128, 1075)),
    )
    for index, (key, label, ref, art_crop, render_crop) in enumerate(rows):
        top = 221 + 467 * index
        pen.text((42, top), label, font=font(24, True), fill=WHITE)
        with Image.open(REFERENCES / ref) as concept:
            art = concept.crop(art_crop) if art_crop else concept.copy()
        place(image, pen, art, 42, top + 46, 564, 398)
        for i, ver in enumerate(("v1", "v2"), start=1):
            with Image.open(ASSET / "work" / ver / "matched" / (key + ".png")) as shot:
                place(image, pen, shot.crop(render_crop), 42 + 582 * i, top + 46, 564, 398)
    pen.text(
        (42, 2564),
        "Los perfiles proceden del concepto auxiliar. La lámina definitiva solo ofrece frente y espalda.",
        font=font(20), fill=MUTED,
    )
    image.save(RENDERS / "comparacion_referencia.jpg", quality=95, subsampling=0)


def verify_images():
    details = {}
    for file in sorted(RENDERS.iterdir()):
        if file.suffix.lower() not in {".jpg", ".png"}:
            continue
        with Image.open(file) as image:
            image.load()
            assert image.mode == "RGB" and min(image.size) >= 1000, file
            assert any(hi - lo > 85 for lo, hi in image.getextrema()), file
            details[file.name] = {
                "size": list(image.size),
                "sha256": hashlib.sha256(file.read_bytes()).hexdigest(),
            }
    assert sum(name.endswith(".png") for name in details) == 15, details.keys()
    for file in (ASSET / "texturas").glob("*.png"):
        with Image.open(file) as image:
            constant = Image.new(image.mode, image.size, image.getpixel((0, 0)))
            assert ImageChops.difference(image, constant).getbbox(), file
    (ASSET / "validacion/archivos_render.json").write_text(json.dumps(details, indent=2) + "\n", encoding="utf-8")
    print("CELESTIAL_HAIR_RENDER_FILES_PASS", len(details))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--compare", action="store_true", help="Rebuild the triptych from both matched render sets.")
    args = parser.parse_args()
    render_board(
        "lamina_mechones.jpg", "Celestial Hair V2 · estudio MASTER",
        "Modelado individual en luz neutra y acercamientos con luz cinematográfica.",
        (
            ("hair_frente", "FRENTE"), ("hair_espalda", "ESPALDA"), ("hair_superior", "CORONILLA"),
            ("hair_izquierda", "LATERAL IZQUIERDO"), ("hair_derecha", "LATERAL DERECHO"),
            ("hair_perspectiva", "PERSPECTIVA"), ("hair_detalle_flequillo", "FLEQUILLO"),
            ("hair_detalle_nuca", "NUCA"), ("r15_ojos", "UGC · OJOS EN R15"),
        ),
    )
    render_board(
        "lamina_conjunto.jpg", "Celestial Hair V2 · conjunto equipado",
        "Ajuste estático Classic R15 con Divine Crown y Eternal Halo en Blender.",
        (
            ("conjunto_frente", "FRENTE · NEUTRA"), ("conjunto_espalda", "ESPALDA · CINE"),
            ("conjunto_lateral", "PERFIL · NEUTRA"), ("r15_cabello", "UGC · SIN CORONA NI HALO"),
            ("conjunto_perspectiva", "PERSPECTIVA · CINE"), ("conjunto_R15_completo", "R15 COMPLETO"),
        ),
    )
    if args.compare:
        compare()
    verify_images()
