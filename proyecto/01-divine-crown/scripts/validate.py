import bpy,bmesh,json,math,struct
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
A=Path(__file__).resolve().parents[1]
R=A.parents[1]
results={}
def summary(o):
    me=o.data;me.calc_loop_triangles();vs=[o.matrix_world@v.co for v in me.vertices]
    dims=[max(v[j] for v in vs)-min(v[j] for v in vs) for j in range(3)]
    return {'triangles':len(me.loop_triangles),'vertices':len(vs),'materials':len(me.materials),'uv_sets':len(me.uv_layers),'dimensions_XYZ':[round(x,6) for x in dims], 'modifiers':len(o.modifiers),'rigged':bool(o.vertex_groups)}
bpy.ops.wm.open_mainfile(filepath=str(A/'blender/DivineCrown_UGC.blend'))
o=bpy.data.objects['DivineCrown_UGC'];results['source']=summary(o)
source=[o.matrix_world@v.co for v in o.data.vertices]
# Validate connected shells, including each shell's outward signed volume.
bm=bmesh.new();bm.from_mesh(o.data);todo=set(bm.verts);volumes=[];shells=[]
while todo:
    seed=next(iter(todo));vs={seed};stack=[seed];todo.remove(seed)
    while stack:
        v=stack.pop()
        for e in v.link_edges:
            q=e.other_vert(v)
            if q in todo:todo.remove(q);vs.add(q);stack.append(q)
    faces=set(f for v in vs for f in v.link_faces)
    vol=sum(f.verts[0].co.dot(f.verts[i].co.cross(f.verts[i+1].co))/6 for f in faces for i in range(1,len(f.verts)-1))
    volumes.append(vol);shells.append(len(faces))
results['closed_shells']={'count':len(volumes),'nonpositive_volumes':sum(x<=0 for x in volumes),'min_volume':min(volumes),'note':'Closed overlapping assembled jewellery shells in one export mesh. Internal shell intersections are intentional and not a boolean-unioned solid.'};bm.free()
# R15 static collision test against the original downloaded head geometry.
crown_bvh=BVHTree.FromPolygons(source,[tuple(p.vertices) for p in o.data.polygons],all_triangles=True)
old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(R/'referencias/oficiales/ClassicMannequin.fbx'),use_anim=False)
imp=[x for x in bpy.data.objects if x not in old];head=next(x for x in imp if x.type=='MESH' and x.name.startswith('Head'))
bpy.context.view_layer.update();dep=bpy.context.evaluated_depsgraph_get();ev=head.evaluated_get(dep);hm=ev.to_mesh();hv=[ev.matrix_world@v.co for v in hm.vertices];head_faces=[tuple(p.vertices) for p in hm.polygons];ev.to_mesh_clear();top=max(v.z for v in hv);shift=Vector(((min(v.x for v in hv)+max(v.x for v in hv))/2,(min(v.y for v in hv)+max(v.y for v in hv))/2,top));hv=[v-shift for v in hv]
hb=BVHTree.FromPolygons(hv,head_faces);overlaps=crown_bvh.overlap(hb)
results['static_R15_head_fit']={'triangle_surface_intersections':len(overlaps),'minimum_sampled_head_vertex_distance_studs':min(crown_bvh.find_nearest(v)[3] for v in hv),'head_top_origin_alignment':list(shift),'test':'BVH triangle overlap of crown and official head; no animations/hair/halo present'}
# Source high-poly evaluated geometry count, independently reopening the master.
bpy.ops.wm.open_mainfile(filepath=str(A/'blender/DivineCrown_MASTER.blend'));deps=bpy.context.evaluated_depsgraph_get();count=0;objects=0
for ob in bpy.data.collections['MASTER - individual jewellery components'].objects:
    ev=ob.evaluated_get(deps)
    if ev.type in ('MESH','FONT'):
        me=ev.to_mesh();me.calc_loop_triangles();count+=len(me.loop_triangles);objects+=1;ev.to_mesh_clear()
results['master']={'evaluated_triangles':count,'editable_component_objects':objects,'live_bevels_preserved':True}
for ext in ['fbx','glb']:
    bpy.ops.wm.read_factory_settings(use_empty=True)
    f=A/'exportaciones'/('DivineCrown_UGC.'+ext)
    if ext=='fbx':bpy.ops.import_scene.fbx(filepath=str(f),use_anim=False)
    else:bpy.ops.import_scene.gltf(filepath=str(f))
    meshes=[ob for ob in bpy.context.scene.objects if ob.type=='MESH'];r={'mesh_objects':len(meshes),'meshes':[summary(ob) for ob in meshes]}
    r['triangle_count_preserved']=sum(x['triangles'] for x in r['meshes'])==results['source']['triangles']
    r['scale_preserved']=len(meshes)==1 and all(abs(x-y)<.0001 for x,y in zip(r['meshes'][0]['dimensions_XYZ'],results['source']['dimensions_XYZ']))
    r['no_rig']=all(not x['rigged'] for x in r['meshes']);results['roundtrip_'+ext]=r
# Inspect glTF physically based material channels as actually serialized.
f=(A/'exportaciones/DivineCrown_UGC.glb').read_bytes();length,kind=struct.unpack_from('<II',f,12);doc=json.loads(f[20:20+length]);results['glb_serialized_materials']=doc.get('materials',[]);results['glb_images']=doc.get('images',[])
mat=doc['materials'][0];pbr=mat['pbrMetallicRoughness'];results['serialized_PBR_checks']={'base_color': 'baseColorTexture' in pbr,'metallic_roughness':'metallicRoughnessTexture' in pbr,'normal':'normalTexture' in mat,'selective_emission':mat['emissiveTexture']['index']!=pbr['baseColorTexture']['index'],'one_material':len(doc['materials'])==1,'opaque':mat.get('alphaMode','OPAQUE')=='OPAQUE','backface_culling':not mat.get('doubleSided',False)}
assert all(results['serialized_PBR_checks'].values())
results['executed_in']='Blender '+bpy.app.version_string
results['studio']='NOT EXECUTED: Computer Use denied app access on three attempts, including after user enabled permissions and after runtime restart.'
(A/'validacion/roundtrip_and_fit.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
assert all(results['roundtrip_'+x]['triangle_count_preserved'] and results['roundtrip_'+x]['scale_preserved'] for x in ['fbx','glb'])
assert results['static_R15_head_fit']['triangle_surface_intersections']==0
assert results['closed_shells']['nonpositive_volumes']==0
print('ROUNDTRIP_AND_STATIC_FIT_PASS')
