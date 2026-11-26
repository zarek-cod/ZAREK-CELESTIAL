from pathlib import Path
import urllib.request, hashlib,json,datetime
from PIL import Image,ImageStat
A=Path(__file__).resolve().parents[1]
urls={
'rigid-specifications':'https://create.roblox.com/docs/avatar/rigid-accessories/specifications.md',
'avatar-resources':'https://create.roblox.com/docs/avatar/resources.md',
'rigid-export':'https://create.roblox.com/docs/avatar/rigid-accessories/export.md',
'blender':'https://create.roblox.com/docs/art/blender.md',
'texture-specifications':'https://create.roblox.com/docs/art/modeling/texture-specifications.md',
'surface-appearance':'https://create.roblox.com/docs/art/modeling/surface-appearance.md',
'accessory-fitting-tool':'https://create.roblox.com/docs/avatar/accessory-fitting-tool.md',
'validation-system':'https://create.roblox.com/docs/marketplace/validation-system.md'}
sources=[]
for slug,url in urls.items():
    try:
        req=urllib.request.Request(url,headers={'User-Agent':'ZAREK-Crown-production/1.0'})
        data=urllib.request.urlopen(req,timeout=25).read();(A/'validacion/fuentes'/(slug+'.md')).write_bytes(data)
        sources.append({'url':url,'retrieved':'2026-11-25 America/Lima','sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)})
    except Exception as e:sources.append({'url':url,'error':str(e)})
(A/'validacion/fuentes/manifest.json').write_text(json.dumps(sources,indent=2),encoding='utf-8')
# Exact output channel formats. Preserve the high-resolution normal source for editing only.
tex=[]
for p in (A/'texturas').glob('*.png'):
    im=Image.open(p)
    if any(s in p.name for s in ['Metalness','Roughness','EmissiveMask']):im=im.convert('L');im.save(p)
    else:im=im.convert('RGB');im.save(p)
    tex.append({'file':p.name,'resolution':list(im.size),'mode':im.mode,'extrema':im.getextrema(),'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
(A/'validacion/textures.json').write_text(json.dumps(tex,indent=2),encoding='utf-8')
print(json.dumps({'sources_saved':sum('error' not in s for s in sources),'sources_failed':[s for s in sources if 'error' in s],'textures':tex},indent=2))
