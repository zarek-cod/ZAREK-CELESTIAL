"""ZAREK Divine Crown: deterministic original mesh, PBR bake, export, QA and Cycles views.
Run: blender -b --factory-startup --python build_crown.py -- build|render
Coordinates: +Z up, -Y front; one Blender unit is one stud. Origin = HatAttachment.
"""
import bpy, bmesh, math, json, sys, time, platform
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
from math import sin, cos, pi
ROOT=Path(__file__).resolve().parents[3]
A=ROOT/'proyecto/01-divine-crown'
for d in ['blender','texturas','exportaciones','renders','validacion','work','roblox']:(A/d).mkdir(exist_ok=True)
MODE=sys.argv[sys.argv.index('--')+1] if '--' in sys.argv else 'build'
T0=time.time()

def activate(o):
    bpy.ops.object.select_all(action='DESELECT');o.hide_set(False);o.select_set(True);bpy.context.view_layer.objects.active=o

def gpu(scene):
    scene.render.engine='CYCLES'
    p=bpy.context.preferences.addons['cycles'].preferences
    p.compute_device_type='OPTIX';p.get_devices()
    ds=[]
    for d in p.devices:
        d.use=d.type=='OPTIX';ds.append({'name':d.name,'type':d.type,'use':d.use})
    if not any(d['use'] for d in ds):raise RuntimeError('No OptiX GPU found')
    scene.cycles.device='GPU';scene.cycles.samples=64;scene.cycles.use_denoising=True
    scene.cycles.seed=23
    return ds

def material(name,color,metal=0,rough=.3,emission=0):
    m=bpy.data.materials.new(name);m.use_nodes=True
    bs=m.node_tree.nodes.get('Principled BSDF');bs.inputs['Base Color'].default_value=(*color,1)
    bs.inputs['Metallic'].default_value=metal;bs.inputs['Roughness'].default_value=rough
    if emission:
        bs.inputs['Emission Color'].default_value=(*color,1);bs.inputs['Emission Strength'].default_value=emission
    m.diffuse_color=(*color,1)
    return m

def mesh(name,verts,faces,mat,bevel=0,indices=None):
    me=bpy.data.meshes.new(name);me.from_pydata(verts,[],faces);me.materials.append(mat);me.update()
    o=bpy.data.objects.new(name,me);bpy.context.collection.objects.link(o)
    if indices:
        for m in indices[0]:me.materials.append(m)
        for p,k in zip(me.polygons,indices[1]):p.material_index=k
    bm=bmesh.new();bm.from_mesh(me);bmesh.ops.recalc_face_normals(bm,faces=bm.faces);bm.to_mesh(me);bm.free()
    if bevel:
        mod=o.modifiers.new('Jeweller edge - editable','BEVEL');mod.width=bevel;mod.segments=3
    PARTS.append(o)
    return o

def loc(t,x,r,z):return (sin(t)*r+cos(t)*x,-cos(t)*r+sin(t)*x,z)

def ring(name,rx,ry,z,h,thick,mat,n=48,serrate=0):
    vs=[]
    for i in range(n):
        t=2*pi*i/n;top=z+h+(serrate if i%4==0 else -serrate*.35)
        vs.extend([(rx*sin(t),-ry*cos(t),z),((rx-thick)*sin(t),-(ry-thick)*cos(t),z),((rx-thick)*sin(t),-(ry-thick)*cos(t),top),(rx*sin(t),-ry*cos(t),top)])
    fs=[]
    for i in range(n):
        j=(i+1)%n
        for k in range(4):fs.append((4*i+k,4*j+k,4*j+(k+1)%4,4*i+(k+1)%4))
    return mesh(name,vs,fs,mat,.003)

def panel(name,t,poly,r,depth,mat,bevel=.003):
    n=len(poly);vs=[loc(t,x,r+d,z) for d in [0,depth] for x,z in poly]
    fs=[tuple(reversed(range(n))),tuple(range(n,2*n))]
    fs.extend((i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n))
    return mesh(name,vs,fs,mat,bevel)

def jewel(name,t,r,z,w,h,depth,frame=True):
    poly=[(0,z+h*.5),(-w*.5,z),(0,z-h*.5),(w*.5,z)]
    if frame:panel(name+' platinum setting',t,[(x*1.27,z+(zz-z)*1.16) for x,zz in poly],r-.012,.035,SILVER,.003)
    # Eight crown facets around a recessed table, plus a closed opaque pavilion.
    vs=[loc(t,x,r,zz) for x,zz in poly]+[loc(t,x*.58,r+depth, z+(zz-z)*.64) for x,zz in poly]+[loc(t,0,r-.035,z)]
    fs=[]
    for i in range(4):
        j=(i+1)%4;fs.extend([(i,j,j+4),(i,j+4,i+4),(j,i,8)])
    fs.append((4,5,6,7))
    ids=[]
    for i in range(4):ids.extend([1 if i in (0,3) else 0,2 if i==0 else 0,0])
    ids.append(0)
    return mesh(name,vs,fs,BLUE,0,([CYAN,ICE],ids))

def rib(name,t,points,r,width,mat):
    # Closed angular ribbon relief, no curve tessellation explosion.
    for i,(a,b) in enumerate(zip(points,points[1:])):
        dx=b[0]-a[0];dz=b[1]-a[1];length=math.hypot(dx,dz);nx=-dz/length*width/2;nz=dx/length*width/2
        panel(name+str(i),t,[(a[0]+nx,a[1]+nz),(b[0]+nx,b[1]+nz),(b[0]-nx,b[1]-nz),(a[0]-nx,a[1]-nz)],r,.009,mat,0)

def bolt(name,t,r,z):
    vs=[loc(t,cos(i*2*pi/6)*.018,r+d,z+sin(i*2*pi/6)*.018) for d in [0,.013] for i in range(6)]
    fs=[tuple(range(5,-1,-1)),tuple(range(6,12))]+[(i,(i+1)%6,(i+1)%6+6,i+6) for i in range(6)]
    return mesh(name,vs,fs,SILVER,0)

def blade(t,i,height,width):
    r=math.sqrt((.79*sin(t))**2+(.70*cos(t))**2)
    # Black root, diamond cross-section and silver cutting faces; physically closed.
    verts=[loc(t,-width,r,.13),loc(t,width,r,.13),loc(t,width*.70,r+.015,.33),loc(t,0,r+.095,height),loc(t,-width*.70,r+.015,.33),loc(t,0,r+.062,.30),loc(t,0,r-.052,.29)]
    faces=[(0,1,5),(1,2,5),(2,3,5),(3,4,5),(4,0,5),(1,0,6),(2,1,6),(3,2,6),(4,3,6),(0,4,6)]
    mesh('Spear %02d - argent facets'%i,verts,faces,SILVER,.0015,([BLACK,ICE_METAL],[0,0,0,2,0,1,1,1,1,1]))
    panel('Spear %02d socket'%i,t,[(-width*1.25,.08),(-width*.95,.28),(0,.37),(width*.95,.28),(width*1.25,.08),(0,.035)],r+.012,.027,BLACK,.003)
    # Front ridge is separate, genuine metal inlay.
    rib('Spear %02d ridge'%i,t,[(0,.32),(0,height-.08)],r+.058,.010,SILVER)

def join(parts,name,apply=False):
    bpy.ops.object.select_all(action='DESELECT')
    for o in parts:o.hide_set(False);o.select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    if apply:
        for o in parts:
            bpy.context.view_layer.objects.active=o
            for m in list(o.modifiers):bpy.ops.object.modifier_apply(modifier=m.name)
    bpy.context.view_layer.objects.active=parts[0];bpy.ops.object.join();o=bpy.context.object;o.name=name
    return o

def image_new(name,size,noncolor=False):
    im=bpy.data.images.new(name,width=size,height=size,alpha=False)
    if noncolor:im.colorspace_settings.name='Non-Color'
    return im

def bake_target(o,im):
    for m in o.data.materials:
        n=m.node_tree.nodes.new('ShaderNodeTexImage');n.image=im;m.node_tree.nodes.active=n

def save_image(im,path,small=None,gray=False):
    if small:im.scale(small,small)
    scene=bpy.context.scene;scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_depth='8'
    scene.render.image_settings.color_mode='BW' if gray else 'RGB'
    im.filepath_raw=str(path);im.file_format='PNG';im.save()
    # Blender Image.save uses image settings; final channel conversion is handled in package.py.

def bake_scalar(o,name,socket,res,gray=True):
    im=image_new(name,res,True);bake_target(o,im);saved=[]
    for m in o.data.materials:
        nt=m.node_tree;bs=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output')
        em=nt.nodes.new('ShaderNodeEmission')
        v=bs.inputs[socket].default_value if socket else (1 if m.name.startswith(('03_','04_','05_')) else 0)
        em.inputs['Color'].default_value=(v,v,v,1);nt.links.new(em.outputs[0],out.inputs['Surface']);saved.append((nt,bs,out,em))
    activate(o);bpy.context.scene.render.bake.use_selected_to_active=False;bpy.ops.object.bake(type='EMIT')
    for nt,bs,out,em in saved:nt.links.new(bs.outputs['BSDF'],out.inputs['Surface']);nt.nodes.remove(em)
    save_image(im,A/'texturas'/('DivineCrown_'+name+'.png'),gray=gray)
    return im

def setup_stage(scene):
    scene.render.resolution_x=1600;scene.render.resolution_y=1200;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGB';scene.render.film_transparent=False
    scene.view_settings.view_transform='AgX'
    scene.world=bpy.data.worlds.new('Midnight atelier');scene.world.use_nodes=True
    scene.world.node_tree.nodes['Background'].inputs[0].default_value=(.32,.38,.48,1);scene.world.node_tree.nodes['Background'].inputs[1].default_value=.65
    wn=scene.world.node_tree.nodes;wl=scene.world.node_tree.links;bg=wn.get('Background');dark=wn.new('ShaderNodeBackground');dark.inputs[0].default_value=(.004,.007,.015,1);dark.inputs[1].default_value=.35;lp=wn.new('ShaderNodeLightPath');mix=wn.new('ShaderNodeMixShader');wl.new(lp.outputs['Is Camera Ray'],mix.inputs[0]);wl.new(bg.outputs[0],mix.inputs[1]);wl.new(dark.outputs[0],mix.inputs[2]);wl.new(mix.outputs[0],wn.get('World Output').inputs[0])
    def light(name,xyz,power,size,color,shape='DISK'):
        d=bpy.data.lights.new(name,'AREA');d.energy=power;d.shape=shape;d.size=size;d.color=color;o=bpy.data.objects.new(name,d);scene.collection.objects.link(o);o.location=xyz;o.rotation_euler=(Vector((0,0,.3))-o.location).to_track_quat('-Z','Y').to_euler()
    light('Key - platinum softbox',(-3,-4,5),450,4,(.80,.89,1))
    light('Rim - electric blue',(3,2,3),380,3,(.13,.31,1))
    light('Front - platinum card',(0,-5,1.2),70,3,(1,1,1))
    light('Fill - celestial',(2,-3,1.5),180,2,(.38,.80,1))
    light('Back - silver strip',(-2,3,2),350,2,(1,1,1))
    cam=bpy.data.cameras.new('Product lens');ob=bpy.data.objects.new('Product lens',cam);scene.collection.objects.link(ob);scene.camera=ob;cam.type='ORTHO';cam.ortho_scale=2.7
    # seamless dark ground, far below the open ring
    bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-.20));floor=bpy.context.object;floor.name='STAGE - shadow receiver';floor.data.materials.append(material('Stage obsidian',(.007,.012,.023),.25,.32))
    return floor

def camera(xyz,target,scale):
    c=bpy.context.scene.camera;c.location=xyz;c.rotation_euler=(Vector(target)-c.location).to_track_quat('-Z','Y').to_euler();c.data.ortho_scale=scale

def stats(o):
    me=o.data;me.calc_loop_triangles();bm=bmesh.new();bm.from_mesh(me)
    r={'vertices':len(me.vertices),'triangles':len(me.loop_triangles),'faces':len(me.polygons),'mesh_objects':1,'materials':len(me.materials),'uv_sets':len(me.uv_layers),'boundary_edges':sum(e.is_boundary for e in bm.edges),'nonmanifold_edges':sum(not e.is_manifold for e in bm.edges),'degenerate_faces':sum(f.calc_area()<1e-12 for f in bm.faces),'dimensions_blender_XYZ':[round(v,6) for v in o.dimensions]}
    uv=me.uv_layers.active
    r['uv_out_of_bounds']=sum(not(-1e-6<=v<=1.000001) for x in uv.data for v in x.uv) if uv else None
    r['uv_zero_area_triangles']=sum(abs((uv.data[t.loops[1]].uv-uv.data[t.loops[0]].uv).cross(uv.data[t.loops[2]].uv-uv.data[t.loops[0]].uv))<1e-12 for t in me.loop_triangles) if uv else None
    # Symmetry checks geometry against its mirrored vertex set, to 1e-5 studs.
    coords={tuple(round(x,5) for x in v.co) for v in me.vertices}
    r['unmatched_mirror_vertices']=sum(tuple(round(x,5) for x in (-v.co.x,v.co.y,v.co.z)) not in coords for v in me.vertices)
    r['symmetry_note']='Rear physical Z signature intentionally breaks bilateral symmetry; all other vertices must mirror.'
    r['bilateral_body_vertices_unmatched']=sum(tuple(round(x,5) for x in (-v.co.x,v.co.y,v.co.z)) not in coords for v in me.vertices if not (abs(v.co.x)<.103 and v.co.y>.78 and v.co.z<.05))
    r['signed_volume']=bm.calc_volume(signed=True);bm.free();return r

if MODE=='build':
    bpy.ops.wm.read_factory_settings(use_empty=True);scene=bpy.context.scene;scene.unit_settings.system='NONE';devices=gpu(scene)
    BLACK=material('01_Obsidian titanium',(.005,.007,.012),1,.28)
    SILVER=material('02_Polished platinum',(.58,.69,.83),1,.20)
    BLUE=material('03_Electric sapphire',(.0005,.022,.72),.18,.20,.55)
    CYAN=material('04_Ion cyan',(.001,.38,.75),.12,.22,.65)
    ICE=material('05_Celestial facet',(.06,.35,.65),.15,.19,.3)
    ICE_METAL=material('06_Silver blade edge',(.82,.88,.98),1,.16)
    DARK=material('07_Recessed graphite',(.014,.022,.041),1,.38)
    PARTS=[]
    ring('Foundation - continuous closed inner comfort band',.775,.69,-.16,.27,.065,BLACK,n=48)
    ring('Lower platinum lip',.784,.699,-.152,.023,.023,SILVER,n=48)
    ring('Upper obsidian battlement',.79,.705,.075,.095,.043,BLACK,n=48,serrate=.026)
    ring('Inlaid lower cobalt channel',.779,.694,-.108,.014,.012,BLUE,n=48)
    # Overlapping armour leaves are deliberate assembled shells, never flat decal planes.
    for i in range(24):
        t=i*2*pi/24;r=math.sqrt((.78*sin(t))**2+(.70*cos(t))**2)
        poly=[(-.105,-.065),(-.12,.055),(-.045,.17),(0,.202),(.045,.17),(.12,.055),(.105,-.065),(0,-.112)]
        panel('Obsidian scale %02d'%i,t,poly,r,.025,BLACK,.0025)
        panel('Argent engraved chevron %02d'%i,t,[(-.061,.042),(0,.089),(.061,.042),(0,.055)],r+.028,.009,SILVER,0)
        if i%2:bolt('Precision rivet %02d'%i,t,r+.030,-.036)
    for i in range(12):
        t=i*2*pi/12
        h=.78 if i in (0,6) else (.71 if i%2==0 else .51)
        blade(t,i,h,.075 if i%2==0 else .062)
        r=math.sqrt((.79*sin(t))**2+(.705*cos(t))**2)+.055
        jewel('Sapphire %02d'%i,t,r,.151,.185 if i in (0,6) else .115,.36 if i in (0,6) else .235,.055)
    # Six tiny free-standing diamond tips set between primary spires.
    for i in range(6):
        t=(i+.5)*2*pi/6;r=math.sqrt((.78*sin(t))**2+(.70*cos(t))**2)
        jewel('Secondary ion crystal %02d'%i,t,r+.048,.22,.053,.13,.021,False)
    # Rear Z trademark, custom closed extruded polygon; no font/license dependencies.
    zpoly=[(-.082,.064),(.085,.064),(.054,.030),(-.025,-.029),(.082,-.029),(.062,-.063),(-.091,-.063),(-.061,-.023),(.022,.033),(-.102,.033)]
    panel('ZAREK - rear signature Z',pi,[(x,z-.025) for x,z in zpoly],.787,.012,SILVER,0)
    # Editable micro branding on inner rear; excluded from UGC triangle budget, baked in detail normal only.
    cu=bpy.data.curves.new('ZAREK maker inscription','FONT');cu.body='ZAREK';cu.size=.071;cu.extrude=.001;cu.resolution_u=2;cu.align_x='CENTER'
    tx=bpy.data.objects.new('ZAREK interior hallmark - master only',cu);scene.collection.objects.link(tx);tx.location=(0,.618,-.08);tx.rotation_euler=(pi/2,0,0);cu.materials.append(SILVER)
    # Preserve independent source objects and live bevels.
    high=bpy.data.collections.new('MASTER - individual jewellery components');scene.collection.children.link(high)
    for o in PARTS+[tx]:
        for c in list(o.users_collection):c.objects.unlink(o)
        high.objects.link(o)
    lowparts=[]
    for o in PARTS:
        q=o.copy();q.data=o.data.copy();q.name='UGC source - '+o.name
        for m in list(q.modifiers):q.modifiers.remove(m)
        scene.collection.objects.link(q);lowparts.append(q)
    low=join(lowparts,'DivineCrown_UGC')
    # Deterministic smart unwrap to one 0..1 UV atlas.
    activate(low);bpy.ops.object.mode_set(mode='EDIT');bpy.ops.mesh.select_all(action='SELECT');bpy.ops.uv.smart_project(angle_limit=math.radians(68),island_margin=.006,area_weight=.7,correct_aspect=True,scale_to_bounds=True);bpy.ops.object.mode_set(mode='OBJECT')
    low.hide_render=True;low.hide_set(True)
    floor=setup_stage(scene);camera((3,-5,2.8),(0,0,.30),2.8)
    # An explicit Blender marker is reference only. AFT must generate the actual rigid attachment in Studio.
    marker=bpy.data.objects.new('HatAttachment_REFERENCE_ONLY',None);scene.collection.objects.link(marker);marker.empty_display_type='ARROWS';marker.empty_display_size=.15
    marker['note']='Origin is the desired HatAttachment; not exported as a supported rigid attachment. Generate with AFT.'
    scene['asset']='ZAREK Divine Crown';scene['scale']='1 Blender unit = 1 stud. Classic R15 target.'
    bpy.ops.wm.save_as_mainfile(filepath=str(A/'blender/DivineCrown_MASTER.blend'))
    # Preview is a real Cycles render, before accepting the sculpt.
    scene.render.resolution_percentage=50;scene.cycles.samples=24;scene.render.filepath=str(A/'work/first-preview.png');bpy.ops.render.render(write_still=True)
    scene.render.resolution_percentage=100;scene.cycles.samples=64
    # Bake material and bevel detail onto the low-poly atlas.
    high.hide_render=True;high.hide_viewport=True;floor.hide_render=True;low.hide_render=False;low.hide_set(False);activate(low)
    scene.render.bake.margin=8;scene.render.bake.use_selected_to_active=False
    im=image_new('BaseColor',1024);bake_target(low,im);scene.render.bake.use_pass_direct=False;scene.render.bake.use_pass_indirect=False;scene.render.bake.use_pass_color=True
    colorlinks=[]
    for mat in low.data.materials:
        nt=mat.node_tree;pb=nt.nodes.get('Principled BSDF');out=nt.nodes.get('Material Output');em=nt.nodes.new('ShaderNodeEmission');em.inputs['Color'].default_value=pb.inputs['Base Color'].default_value;nt.links.new(em.outputs[0],out.inputs['Surface']);colorlinks.append((nt,pb,out,em))
    bpy.ops.object.bake(type='EMIT')
    for nt,pb,out,em in colorlinks:nt.links.new(pb.outputs['BSDF'],out.inputs['Surface']);nt.nodes.remove(em)
    save_image(im,A/'texturas/DivineCrown_BaseColor.png')
    rough=bake_scalar(low,'Roughness','Roughness',256)
    metal=bake_scalar(low,'Metalness','Metallic',256)
    emiss=bake_scalar(low,'EmissiveMask',None,256)
    # Selected-to-active ray bake from evaluated editable master (bevels) into UGC.
    high.hide_viewport=False;high.hide_render=False
    bake_parts=[]
    for o in PARTS:
        q=o.copy();q.data=o.data.copy();scene.collection.objects.link(q);bake_parts.append(q)
    baked=join(bake_parts,'BAKE HIGH evaluated bevels',apply=True)
    normal=image_new('Normal',1024,True);bake_target(low,normal)
    bpy.ops.object.select_all(action='DESELECT');baked.select_set(True);low.select_set(True);bpy.context.view_layer.objects.active=low
    scene.render.bake.use_selected_to_active=True;scene.render.bake.cage_extrusion=.017;scene.render.bake.max_ray_distance=.035
    bpy.ops.object.bake(type='NORMAL');save_image(normal,A/'texturas/DivineCrown_Normal_source1024.png');normal.scale(256,256);save_image(normal,A/'texturas/DivineCrown_Normal.png')
    scene.render.bake.use_selected_to_active=False;bpy.data.objects.remove(baked,do_unlink=True);high.hide_viewport=True;high.hide_render=True
    # Collapse to one atlas material. Atlas colors are preserved in the unlit fallback.
    m=bpy.data.materials.new('DivineCrown - single PBR atlas');m.use_nodes=True;nt=m.node_tree;bs=nt.nodes.get('Principled BSDF')
    def tex(im,x,y):
        n=nt.nodes.new('ShaderNodeTexImage');n.image=im;n.location=(x,y);n.interpolation='Linear';return n
    base=tex(im,-600,400);nt.links.new(base.outputs['Color'],bs.inputs['Base Color'])
    nt.links.new(tex(rough,-600,100).outputs['Color'],bs.inputs['Roughness']);nt.links.new(tex(metal,-600,-150).outputs['Color'],bs.inputs['Metallic'])
    nn=nt.nodes.new('ShaderNodeNormalMap');nn.location=(-250,-350);nt.links.new(tex(normal,-600,-400).outputs['Color'],nn.inputs['Color']);nt.links.new(nn.outputs[0],bs.inputs['Normal'])
    import numpy as np
    smallbase=im.copy();smallbase.scale(256,256);bc=np.array(smallbase.pixels[:],dtype=np.float32).reshape(-1,4);mask=np.array(emiss.pixels[:],dtype=np.float32).reshape(-1,4);bc[:,:3]*=mask[:,:3];bc[:,3]=1
    emcolor=image_new('EmissionColor',256);emcolor.pixels.foreach_set(bc.ravel());save_image(emcolor,A/'texturas/DivineCrown_EmissiveColor.png')
    nt.links.new(tex(emcolor,-600,-650).outputs['Color'],bs.inputs['Emission Color']);bs.inputs['Emission Strength'].default_value=.65
    m.use_backface_culling=True
    low.data.materials.clear();low.data.materials.append(m)
    for f in low.data.polygons:f.material_index=0
    activate(low);tri=low.modifiers.new('Explicit export triangulation','TRIANGULATE');bpy.ops.object.modifier_apply(modifier=tri.name)
    report=stats(low);report['cycles_devices']=devices;report['blender_version']=bpy.app.version_string;report['python_version']=sys.version;report['normal_bake']='Executed Cycles selected-to-active from master bevel geometry';report['target']='Classic R15 Hat';report['dimensions_roblox_XYZ']=[report['dimensions_blender_XYZ'][0],report['dimensions_blender_XYZ'][2],report['dimensions_blender_XYZ'][1]]
    report['max_abs_attachment_axes_studs']=[round(max(abs(v.co[j]) for v in low.data.vertices),6) for j in [0,2,1]]
    report['local_checks']={'triangle_budget':report['triangles']<=4000,'watertight':report['nonmanifold_edges']==0,'nondegenerate':report['degenerate_faces']==0,'one_mesh_one_material_one_uv':report['materials']==1 and report['uv_sets']==1,'bilateral_body_symmetry':report['bilateral_body_vertices_unmatched']==0,'uv_bounds':report['uv_out_of_bounds']==0,'classic_hat_bounds':all(v<=lim for v,lim in zip(report['max_abs_attachment_axes_studs'],[1.5,2,1.5]))}
    report['not_tested']=['Marketplace server validation','Studio AFT generation','Rthro Normal/Slender fit','future hair and halo intersections','self intersections between assembled shells']
    (A/'validacion/geometry.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print('GEOMETRY',json.dumps(report),flush=True)
    if not all(report['local_checks'].values()):raise RuntimeError('Local mesh QA failed')
    # Remove master from the optimized .blend; the master file retains all editable source parts.
    for o in list(high.objects):bpy.data.objects.remove(o,do_unlink=True)
    bpy.data.collections.remove(high)
    floor.hide_render=False;low.hide_render=False
    bpy.ops.file.pack_all();camera((3,-5,2.8),(0,0,.30),2.8)
    bpy.ops.wm.save_as_mainfile(filepath=str(A/'blender/DivineCrown_UGC.blend'))
    activate(low)
    bpy.ops.export_scene.fbx(filepath=str(A/'exportaciones/DivineCrown_UGC.fbx'),use_selection=True,object_types={'MESH'},apply_scale_options='FBX_SCALE_UNITS',global_scale=1,axis_forward='-Z',axis_up='Y',bake_space_transform=True,path_mode='COPY',embed_textures=True,add_leaf_bones=False,bake_anim=False)
    bpy.ops.export_scene.gltf(filepath=str(A/'exportaciones/DivineCrown_UGC.glb'),export_format='GLB',use_selection=True,export_yup=True,export_apply=True,export_extras=True)
    manifest={'name':'ZAREK Divine Crown','type':'Hat','body_scale':'Classic','attachment':'HatAttachment','attachment_generation':'Studio AFT required; Blender reference marker is not a rigid accessory attachment import','origin_blender':[0,0,0],'units':'studs, import Scale Unit=Stud','triangles':report['triangles'],'maps':{'ColorMap':'DivineCrown_BaseColor.png','NormalMap':'DivineCrown_Normal.png','MetalnessMap':'DivineCrown_Metalness.png','RoughnessMap':'DivineCrown_Roughness.png','EmissiveMaskContent':'DivineCrown_EmissiveMask.png'},'emissive_strength_proposed':.65,'official_marketplace_validation':'PENDING - no upload authorized','geometry_checks':report['local_checks']}
    (A/'exportaciones/manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    print('BUILD_DONE_SECONDS',time.time()-T0,flush=True)

elif MODE=='render':
    variant=sys.argv[sys.argv.index('--')+2] if len(sys.argv)>sys.argv.index('--')+2 else 'UGC'
    bpy.ops.wm.open_mainfile(filepath=str(A/'blender'/('DivineCrown_'+variant+'.blend')))
    scene=bpy.context.scene;gpu(scene);scene.render.resolution_percentage=100
    views=[('front',(0,-6,1.4),(0,0,.32),2.35),('back',(0,6,1.4),(0,0,.32),2.35),('left',(-6,0,1.5),(0,0,.32),2.35),('right',(6,0,1.5),(0,0,.32),2.35),('perspective',(3,-5,2.8),(0,0,.30),2.8),('detail',(1.2,-4,1.0),(0,-.52,.27),1.25)]
    for name,xyz,target,scale in views:
        camera(xyz,target,scale);scene.render.filepath=str(A/'renders'/(variant.lower()+'_'+name+'.png'));bpy.ops.render.render(write_still=True);print('RENDER_DONE',variant,name,flush=True)
    # Fit the exact official Classic mannequin mesh by the top of its visible head surface.
    old=set(bpy.data.objects);bpy.ops.import_scene.fbx(filepath=str(ROOT/'referencias/oficiales/ClassicMannequin.fbx'))
    imported=[o for o in bpy.data.objects if o not in old]
    meshes=[o for o in imported if o.type=='MESH'];bpy.context.view_layer.update()
    head=next(o for o in meshes if o.name.startswith('Head'))
    deps=bpy.context.evaluated_depsgraph_get();he=head.evaluated_get(deps);hm=he.to_mesh();hv=[head.matrix_world@v.co for v in hm.vertices];he.to_mesh_clear();headtop=max(v.z for v in hv);cx=(min(v.x for v in hv)+max(v.x for v in hv))/2;cy=(min(v.y for v in hv)+max(v.y for v in hv))/2
    shift=Vector((cx,cy,headtop))
    # Apply translation only to imported roots; preserve armature and all child transforms.
    for o in imported:
        if o.parent not in imported:o.location-=shift
    bpy.context.view_layer.update()
    for o in meshes:
        o.data.materials.clear();o.data.materials.append(material('R15 reference - porcelain',(.16,.20,.29),.1,.48))
    for o in imported:
        if o.type!='MESH':o.hide_render=True
    scene.objects['STAGE - shadow receiver'].location.z=-headtop-.04
    allv=[]
    deps=bpy.context.evaluated_depsgraph_get()
    for o in meshes:
        ev=o.evaluated_get(deps);me=ev.to_mesh();allv.extend(o.matrix_world@v.co for v in me.vertices);ev.to_mesh_clear()
    zmin=min(v.z for v in allv);scene.objects['STAGE - shadow receiver'].location.z=zmin-.025
    camera((4,-8,3),(0,0,(zmin+.9)/2),max(4.7,(.9-zmin)*1.15));scene.render.filepath=str(A/'renders'/(variant.lower()+'_equipped_R15.png'));bpy.ops.render.render(write_still=True)
    camera((2.3,-5,1.7),(0,0,-.1),3);scene.render.filepath=str(A/'renders'/(variant.lower()+'_fit_detail_R15.png'));bpy.ops.render.render(write_still=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(A/'blender'/('DivineCrown_'+variant+'_R15_fit.blend')))
    fit={'mannequin':'Roblox official ClassicMannequin.fbx, original unchanged','parts':len(meshes),'headtop_original':headtop,'head_center_original':[cx,cy],'fit_transform':'head visible top translated to HatAttachment_REFERENCE origin','fit_scope':'Static fit in Blender. Not a Studio AFT/animation test.'}
    (A/'validacion'/('fit_'+variant.lower()+'.json')).write_text(json.dumps(fit,indent=2),encoding='utf-8')
    print('RENDERS_DONE_SECONDS',time.time()-T0,flush=True)
else:raise ValueError(MODE)
