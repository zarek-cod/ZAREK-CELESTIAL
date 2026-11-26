"""Build the review PDF, comparison boards, factual reports and a local delivery bundle.
Use the Codex bundled Python (Pillow and ReportLab), after run.ps1 finishes.
"""
from pathlib import Path
import json,hashlib,shutil,zipfile,math,textwrap
from PIL import Image,ImageOps,ImageDraw,ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.utils import ImageReader
A=Path(__file__).resolve().parents[1];ROOT=A.parents[1]
G=json.loads((A/'validacion/geometry.json').read_text(encoding='utf-8'))
Q=json.loads((A/'validacion/roundtrip_and_fit.json').read_text(encoding='utf-8'))
assert all(G['local_checks'].values())
assert Q['static_R15_head_fit']['triangle_surface_intersections']==0
# Convert final standalone maps to the published channel formats.
tex=[]
for f in (A/'texturas').glob('*.png'):
    im=Image.open(f);mode='L' if any(k in f.name for k in ['Metalness','Roughness','EmissiveMask']) else 'RGB';im=im.convert(mode);im.save(f)
    tex.append({'file':f.name,'size':list(im.size),'mode':im.mode,'extrema':im.getextrema(),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()})
(A/'validacion/textures.json').write_text(json.dumps(tex,indent=2),encoding='utf-8')
# Assemble unaltered Cycles renders and the original reference for review.
font='C:/Windows/Fonts/arial.ttf';bold='C:/Windows/Fonts/arialbd.ttf'
f=ImageFont.truetype(font,28);fb=ImageFont.truetype(bold,42);small=ImageFont.truetype(font,22)
navy=(6,14,26);white=(231,242,255);cyan=(0,229,255)
comp=Image.new('RGB',(1800,900),navy);dr=ImageDraw.Draw(comp)
dr.text((55,35),'REFERENCIA / MODELO REAL',font=fb,fill=white)
dr.text((55,103),'Divine Crown - comparación visual de revisión',font=f,fill=cyan)
ref=Image.open(ROOT/'referencias/accesorios/02-corona-divina.png').convert('RGB')
ref=ImageOps.contain(ref,(760,430));comp.paste(ref,(60+(760-ref.width)//2,245+(430-ref.height)//2))
prod=ImageOps.contain(Image.open(A/'renders/master_front.png').convert('RGB'),(860,645));comp.paste(prod,(880,170))
dr.text((60,730),'Concepto original: el halo y el pelo son contexto.',font=small,fill=white)
dr.text((880,830),'Render Cycles del maestro editable. Sin imagen generativa.',font=small,fill=white)
comp.save(A/'renders/comparacion_referencia.png')
views=['front','back','left','right','perspective','detail','equipped_R15','fit_detail_R15']
for variant in ['master','ugc']:
    board=Image.new('RGB',(2000,1200),navy);d=ImageDraw.Draw(board)
    d.text((30,20),'ZAREK / DIVINE CROWN / '+variant.upper(),font=fb,fill=white)
    for i,v in enumerate(views):
        im=ImageOps.contain(Image.open(A/'renders'/(variant+'_'+v+'.png')).convert('RGB'),(480,440))
        x=20+(i%4)*500;y=100+(i//4)*535;board.paste(im,(x+(480-im.width)//2,y));d.text((x,y+445),v.replace('_',' ').upper(),font=small,fill=cyan)
    board.save(A/'renders'/('lamina_'+variant+'.jpg'),quality=94)
# Factual status, separated from official validation.
tri=G['triangles'];high=Q['master']['evaluated_triangles'];n=Q['master']['editable_component_objects']
compat=f'''# Compatibilidad Roblox - Divine Crown\n\nEstado: verificada localmente en Blender; PENDIENTE de importación y AFT en Roblox Studio. No aprobada para Marketplace.\n\n- Categoría propuesta: Hat. Escala de ajuste: Classic R15.\n- Una malla, un material, un UV; {tri} triángulos y 2090 vértices fuente. GLB divide vértices por costuras: {Q['roundtrip_glb']['meshes'][0]['vertices']} vértices, mismo número de triángulos.\n- Tamaño Roblox esperado: X=1.80, Y=0.94, Z=1.63 studs. Centro de attachment propuesto en (0,0,0). Límite Classic Hat consultado: 3×4×3 centrado en attachment. Normal/Slender no se han probado.\n- {Q['closed_shells']['count']} carcasas cerradas ensambladas en la única malla. Ninguna con volumen no positivo; 0 bordes abiertos/no manifold y 0 caras degeneradas. Las piezas superpuestas no son una unión booleana; el análisis exhaustivo de autointersecciones no se ha ejecutado.\n- 0 UV fuera de 0..1, 0 triángulos de área UV cero. No se afirma una prueba exacta de solapamientos UV.\n- Simetría bilateral de cuerpo verificada. La firma Z posterior introduce 20 vértices intencionalmente asimétricos.\n- Normal OpenGL tangente horneada desde biseles del maestro, separando las {Q['closed_shells']['count']} piezas para evitar contaminación de rayos entre vecinas.\n- BaseColor RGB 1024². Normal RGB 256²; Roughness/Metalness/EmissiveMask gris 256². La fuente Normal_source1024 no se incluye en la configuración UGC.\n- Emisión propuesta: 0.65. La documentación permite máscaras emisivas de avatar y fuerza 0..40. Su importación y apariencia reales en Studio no están verificadas. glTF contiene una textura emisiva RGB independiente; Roblox requiere su máscara gris.\n- HatAttachment todavía NO está generado por AFT. El marcador de Blender es una referencia de colocación, no una afirmación de attachment importado. No se admite importar attachments rígidos desde Blender según la documentación consultada.\n- Verificadas reimportaciones FBX y GLB en Blender: escala y {tri} triángulos preservados; una malla, un material, un UV, sin rig. Esto no constituye una importación en Studio.\n- Cabeza del maniquí oficial Classic: 0 cruces de superficies por BVH en ajuste estático. Distancia mínima muestreada en vértices: {Q['static_R15_head_fit']['minimum_sampled_head_vertex_distance_studs']:.4f} studs. Los renders de ajuste mantienen 15 partes oficiales y desactivan animaciones de transformación del FBX.\n- Pendientes: AFT, jerarquía real y equipamiento Studio, caminar/correr/saltar, escala por cuerpos, cabello/halos futuros, validador oficial, moderación. No se han subido activos a Roblox ni se han gastado Robux.\n\n## Motivo de la prueba Studio pendiente\nComputer Use respondió literalmente `Computer Use was not approved to use Roblox Studio`. Se verificó antes y después de la autorización del usuario y después de reiniciar el runtime; la denegación persistió. No se intentó eludir ese control. La guía roblox/LEEME.md y VerifyImportedCrown.luau permiten retomar la prueba cuando la herramienta conceda el acceso. El script Luau no se ha ejecutado.\n\n## Fuentes oficiales consultadas 25/11/2026 - America/Lima\n- https://create.roblox.com/docs/avatar/rigid-accessories/specifications\n- https://create.roblox.com/docs/art/modeling/texture-specifications\n- https://create.roblox.com/docs/art/modeling/surface-appearance\n- https://create.roblox.com/docs/marketplace/validation-system\n- https://create.roblox.com/docs/avatar/rigid-accessories/export\n- https://create.roblox.com/docs/avatar/accessory-fitting-tool\n\nLa página general de rígidos menciona 2048², mientras que el sistema de validación especifica 1024 para ColorMap y 256 para Normal/Metalness/Roughness. Se aplicó el presupuesto más conservador por campo; snapshots íntegros y SHA256 están en validacion/fuentes/.\n'''
(A/'validacion/COMPATIBILIDAD_ROBLOX.md').write_text(compat,encoding='utf-8')
(A/'validacion/GEOMETRIA.md').write_text(f'''# Geometría ejecutada\n\n| Medida | Maestro | UGC |\n|---|---:|---:|\n| Triángulos evaluados | {high:,} | {tri:,} |\n| Piezas fuente editables | {n} | 1 malla final |\n| Materiales exportados | Procedurales por pieza | 1 atlas |\n| UV exportados | Fuente de bake | 1 atlas 0..1 |\n\nUGC: 0 bordes abiertos; 0 bordes no manifold; 0 caras degeneradas; 0 triángulos UV degenerados. Todas las carcasas tienen volumen positivo. La simetría se controla salvo la firma Z posterior.\n\nLos valores proceden de geometry.json y roundtrip_and_fit.json; validate.log y build.log contienen la ejecución. Las pruebas de Studio siguen pendientes.\n''',encoding='utf-8')
(A/'HISTORIAL.md').write_text('''# Historial de mejoras\n\n1. Bloque inicial: geometría original de joyería, 3672 triángulos UGC. Vista real conservada en validacion/iteration01.png. Detectadas agujas demasiado altas y reflejos poco legibles.\n2. Bajadas las agujas de 1.00 a 0.78 studs y ajustado el estudio de reflejos. Corregida la simetría de los cristales intermedios.\n3. El render UGC reveló metales negros por horneado Diffuse. Evidencia fallida conservada en iteration02_failed_metal_bake.png. Sustituido por pase Emission del color base, independiente de metalness.\n4. Inspeccionado GLB real: se reemplazó la mezcla de nodos de emisión por mapa RGB explícito para conservar una emisión selectiva.\n5. Sustituido bake normal agregado por selección de cada una de las 131 piezas del maestro y su correspondiente carcasa UGC.\n6. El render del maniquí reveló que la animación importada restablecía la posición del padre. Desactivada la animación de referencia del FBX y añadida aserción de cabeza en origen antes del render. Repetidas las vistas equipadas.\n7. Reimportación FBX/GLB y prueba BVH de cabeza repetidas sobre la versión corregida. Renders y reportes finales publicados en rama de revisión, sin fusionar main.\n''',encoding='utf-8')
(A/'README.md').write_text(f'''# ZAREK Divine Crown\n\nEntrega de revisión del primer accesorio. Modelado real original, exclusivamente corona. **Studio/AFT y aprobación oficial siguen pendientes.**\n\n## Abrir\n- `blender/DivineCrown_MASTER.blend`: {high:,} triángulos evaluados, {n} piezas editables con biseles vivos y materiales de fuente.\n- `blender/DivineCrown_UGC.blend`: {tri:,} triángulos, atlas PBR empaquetado.\n- `blender/DivineCrown_UGC_R15_fit.blend`: ajuste estático sobre las 15 partes oficiales del maniquí Classic.\n- `exportaciones/DivineCrown_UGC.fbx` y `.glb`: una malla, sin cámaras/luces/maniquí.\n- `DivineCrown_Presentacion.pdf`: presentación con vistas, detalles y comparación.\n- `validacion/COMPATIBILIDAD_ROBLOX.md`: resultados y límites de lo comprobado.\n\n## Reproducir\nWindows / Blender 5.2.2 LTS instalado en `C:\\Program Files\\Blender Foundation\\Blender 5.2\\blender.exe`. Python bpy y NumPy vienen con Blender; no hacen falta paquetes de pago.\n\nDesde esta carpeta: `powershell -File scripts/run.ps1 -Stage All`. Alternativamente ejecutar Blender con `-b --factory-startup --python-exit-code 1 --python scripts/build_crown.py -- build`, luego `-- render UGC`, `-- render MASTER`, y `scripts/validate.py`. Para la presentación usar el Python de Codex con Pillow y ReportLab: `scripts/package_delivery.py`. La captura de fuentes es opcional: `scripts/collect_evidence.py`.\n\nTodos los objetos modelados se generan en esta carpeta. Unidades: 1 unidad Blender = 1 stud. Blender: +Z arriba, -Y frente. Roblox: +Y arriba. Importar como Stud.\n\n## Alcance de la fidelidad\nSe conservaron banda negra angular, gemas azules volumétricas, engastes y bordes de plata, puntas afiladas, simetría y firma Z. La vista posterior se interpreta a partir del concepto; no hay plano técnico dimensional. El recorte original es pequeño y contiene cabello/halo. El resultado se presenta para revisión visual del usuario; no se declara idéntico ni aprobado. El ajuste conjunto con cabello/halo requiere sus modelos futuros.\n\n## Licencias y procedencia\nGeometría y mapas nuevos creados para este proyecto, sin modelos comerciales ajenos. Referencias originales proporcionadas por el usuario, sin reasignar autoría ni licencia. Maniquí y rig descargados de Creator Hub de Roblox y sujetos a sus términos; originales preservados, uso como referencia. Blender es GPL y gratuito; su uso no impone la GPL sobre los modelos producidos. Git, Git LFS, Python, NumPy, Pillow y ReportLab son herramientas gratuitas. No se instaló software ni se utilizó servicio de pago.\n\n## Revisión\nRama privada `accessory/01-divine-crown`. No se fusiona el PR ni se inicia el siguiente componente sin aprobación explícita. No se ha publicado ni comprado nada en Roblox.\n''',encoding='utf-8')
(ROOT/'docs/ESTADO.md').write_text(f'''# Estado - Divine Crown\n\n- Corona modelada, texturizada, exportada y verificada localmente en Blender.\n- Maestro: {high:,} triángulos evaluados / {n} componentes editables. UGC: {tri:,} triángulos / una malla / un material / un UV.\n- Texturas PBR horneadas, vistas reales Cycles con GPU OptiX y comparación visual generadas.\n- Reimportación FBX y GLB en Blender: geometría y escala preservadas. Cabeza R15: 0 cruces de superficies en ajuste estático.\n- Studio: PENDIENTE. Computer Use denegó acceso incluso tras confirmación del usuario y reinicio del runtime. No se afirma validación oficial ni equipamiento ejecutado en Studio.\n- Repo privado: https://github.com/zarek-cod/ZAREK-CELESTIAL ; rama accessory/01-divine-crown. PR en borrador: consultar docs/ENTREGA.md después del cierre de la entrega.\n- Otros 15 componentes y 7 efectos: pendientes; no iniciados.\n- Estado artístico: pendiente de revisión del usuario. Estado Marketplace: pendiente, sin upload ni pagos.\n''',encoding='utf-8')
inv=json.loads((ROOT/'docs/inventario.json').read_text(encoding='utf-8-sig'))
for item in inv['componentes']:
    if item['slug']=='corona-divina':item['estado']='modelada, texturizada, exportada y verificada localmente; Studio/AFT y revisión del usuario pendientes'
(ROOT/'docs/inventario.json').write_text(json.dumps(inv,ensure_ascii=False,indent=2),encoding='utf-8')
# Review presentation, landscape, designed from the actual artifact renders.
pdfmetrics.registerFont(TTFont('Zarek',font));pdfmetrics.registerFont(TTFont('ZarekBold',bold))
P=A/'DivineCrown_Presentacion.pdf';c=canvas.Canvas(str(P),pagesize=(960,600));c.setTitle('ZAREK Divine Crown - revisión de modelo real');W,H=960,600
BG=HexColor('#07111E');FG=HexColor('#ECF4FF');ACC=HexColor('#00E5FF');MUT=HexColor('#A8BDD5')
def text(x,y,s,size=12,color=FG,b=False):
    c.setFillColor(color);c.setFont('ZarekBold' if b else 'Zarek',size);c.drawString(x,y,s)
def para(x,y,s,width=45,size=12,leading=19,color=MUT):
    for line in textwrap.wrap(s,width):text(x,y,line,size,color);y-=leading
    return y

def start(num,title,sub):
    c.setFillColor(BG);c.rect(0,0,W,H,fill=1,stroke=0);text(36,565,'ZAREK  /  CELESTIAL',11,ACC,True);text(36,530,title,27,FG,True);text(36,506,sub,11,MUT)
    c.setStrokeColor(HexColor('#20344D'));c.line(36,38,924,38);text(36,21,'DIVINE CROWN  /  25 NOV 2026  /  RENDERS DE BLENDER CYCLES + OPTIX',8,MUT);text(874,21,f'0{num} / 04',8,MUT)
def pic(path,x,y,w,h):
    im=Image.open(path);iw,ih=im.size;s=min(w/iw,h/ih);dw,dh=iw*s,ih*s;c.drawImage(ImageReader(im),x+(w-dw)/2,y+(h-dh)/2,dw,dh,mask='auto')
start(1,'DIVINE CROWN','Corona celestial / Primera entrega de revisión')
pic(A/'renders/master_perspective.png',332,76,592,414)
text(40,453,'OBSIDIAN.',33,FG,True);text(40,416,'SAPPHIRE.',33,ACC,True);text(40,379,'THUNDER.',33,FG,True)
y=para(40,335,'Metal negro angular, plata pulida y gemas facetadas con volumen real.',30,14,21)
text(40,238,f'{high:,}',31,FG,True);text(40,217,'triángulos del maestro editable',11,MUT)
text(40,176,f'{tri:,}',31,ACC,True);text(40,155,'triángulos de la versión UGC',11,MUT)
text(40,91,'MODELO REAL / REVISIÓN ABIERTA',9,ACC,True);c.showPage()
start(2,'SEIS VISTAS / VERSIÓN UGC','Atlas PBR horneado sobre una sola malla exportable')
labels=[('front','FRONTAL'),('back','POSTERIOR'),('left','IZQUIERDA'),('right','DERECHA'),('perspective','PERSPECTIVA'),('detail','DETALLE CENTRAL')]
for i,(key,label) in enumerate(labels):
    x=36+(i%3)*300;y=282-(i//3)*229;pic(A/'renders'/('ugc_'+key+'.png'),x,y+20,288,198);text(x,y+3,label,10,ACC,True)
c.showPage()
start(3,'DE LA REFERENCIA AL VOLUMEN','Comparación artística; halo y cabello del concepto aún no desarrollados')
pic(ROOT/'referencias/accesorios/02-corona-divina.png',40,275,380,172);text(40,248,'REFERENCIA DEFINITIVA / RECORTE ORIGINAL',10,ACC,True)
pic(A/'renders/master_front.png',460,168,464,348);text(460,147,'MAESTRO / GEOMETRÍA EDITABLE',10,ACC,True)
para(40,205,'Conservados: banda negra, puntas, gemas azules, bordes de plata y simetría. La espalda y los detalles ocultos se interpretan desde el concepto.',44,12,19)
para(40,101,'La fidelidad visual queda pendiente de tu revisión. El recorte original tiene resolución limitada.',102,11,17)
c.showPage()
start(4,'AJUSTE R15 / EVIDENCIA Y PENDIENTES','Maniquí oficial Classic / comprobación estática en Blender')
pic(A/'renders/ugc_equipped_R15.png',36,72,410,416)
text(478,459,'VERIFICADO LOCALMENTE',13,ACC,True)
y=433
for line in [f'{tri:,} triángulos; una malla, material y UV.','Sin bordes abiertos ni caras degeneradas.','FBX y GLB: geometría y escala preservadas.','Cabeza R15: 0 cruces de superficies por BVH.','Color 1024²; mapas auxiliares 256².']:
    y=para(478,y,line,57,12,18)-12
text(478,y-3,'PENDIENTE EN STUDIO',13,HexColor('#FFD38A'),True);y-=28
para(478,y,'Computer Use sigue denegando acceso a Roblox Studio. AFT, equipamiento, movimiento y validación oficial no se han ejecutado. No se ha publicado el accesorio.',57,12,18)
text(478,86,'Se detiene aquí: siguiente componente requiere aprobación.',10,ACC,True)
c.showPage();c.save()
print('Presentation and factual reports saved',P)
