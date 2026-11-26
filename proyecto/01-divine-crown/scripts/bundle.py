import sys, json, shutil, zipfile,hashlib
from pathlib import Path
A=Path(__file__).resolve().parents[1];ROOT=A.parents[1]
OUT=Path(sys.argv[1]).resolve()
assert OUT.name=='outputs', 'Use the designated Codex outputs directory.'
DEST=OUT/'ZAREK_Divine_Crown';DEST.mkdir(parents=True,exist_ok=True)
files=[p for p in A.rglob('*') if p.is_file() and 'work' not in p.relative_to(A).parts and p.suffix not in ('.blend1','.blend2','.tmp') and '__pycache__' not in p.parts and p.name!='checksums.sha256']
(A/'checksums.sha256').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+p.relative_to(A).as_posix()+'\n' for p in sorted(files)),encoding='utf-8')
files.append(A/'checksums.sha256')
for p in files:
    q=DEST/p.relative_to(A);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
for p in (ROOT/'docs').iterdir():
    if p.is_file():q=DEST/'docs'/p.name;q.parent.mkdir(exist_ok=True);shutil.copy2(p,q)
for rel in ['referencias/01-avatar-definitivo.png','referencias/02-logo-original.png','referencias/accesorios/02-corona-divina.png','referencias/oficiales/ClassicMannequin.fbx','referencias/oficiales/Rig_and_Attachments_Templates.zip']:
    p=ROOT/rel;q=DEST/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
shutil.copy2(A/'work/presentacion-1.png',DEST/'Vista_previa_presentacion.png')
archive=OUT/'ZAREK_Divine_Crown_Revision.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
    for p in sorted(DEST.rglob('*')):
        if p.is_file():z.write(p,Path('ZAREK_Divine_Crown')/p.relative_to(DEST))
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
for rel in ['blender/DivineCrown_MASTER.blend','blender/DivineCrown_UGC.blend','exportaciones/DivineCrown_UGC.fbx','exportaciones/DivineCrown_UGC.glb','DivineCrown_Presentacion.pdf']:
    p=A/rel;q=DEST/rel;assert hashlib.sha256(p.read_bytes()).digest()==hashlib.sha256(q.read_bytes()).digest()
print(json.dumps({'folder':str(DEST),'archive':str(archive),'archive_bytes':archive.stat().st_size,'files':len(list(DEST.rglob('*'))),'zip_integrity':'PASS','core_deliverable_hashes':'MATCH'},indent=2))
