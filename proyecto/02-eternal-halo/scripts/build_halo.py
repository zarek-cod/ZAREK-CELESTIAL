
"""Build the Eternal Halo asset variants, atlas, and static/experience exports."""
from pathlib import Path
from math import cos, sin, pi, radians
import json
import struct
import sys
import zlib

import bpy
import bmesh
import numpy as np
from mathutils import Vector, Matrix

ASSET = Path(__file__).resolve().parents[1]
TAU = pi * 2
# Each closed profile is laid out radially, from the inside edge over the top and down.
MAIN = [(-.066,.000),(-.056,.023),(-.041,.031),(-.022,.035),(-.009,.027),
        (.018,.034),(.047,.024),(.062,.008),(.059,-.010),(.036,-.026),
        (-.014,-.028),(-.052,-.018)]
SECOND = [(-.035,0),(-.027,.015),(-.014,.020),(.003,.017),(.021,.018),
          (.034,.008),(.032,-.008),(.014,-.016),(-.011,-.017),(-.028,-.010)]
FRAME = [
    (1.165, 1.228, Matrix.Identity(3), MAIN, .035, .434),
    (1.036, 1.034, Matrix.Rotation(radians(25),3,"Z") @ Matrix.Rotation(radians(9),3,"X") @ Matrix.Rotation(radians(-25),3,"Z"), SECOND, .474, .790),
]
PALETTES = [
    [(14,43,127),(9,139,255),(225,249,255),(86,198,255),(9,46,231),(28,180,255),
     (241,252,255),(2,123,255),(8,46,212),(16,137,255),(8,29,142),(33,104,238)],
    [(12,57,155),(17,197,255),(184,248,255),(12,110,255),(76,224,255),
     (32,124,246),(17,69,180),(47,181,255),(11,61,190),(23,93,234)],
]
SWATCHES = [(5,110,255),(78,222,255),(247,254,255),(15,80,224),(12,48,126)]
SWATCH_X = [.1,.3,.5,.7,.9]
PBR = None
TEX = {
    "BaseColor": ("sRGB",1024), "Roughness": ("Non-Color",256),
    "Metalness": ("Non-Color",256), "Normal": ("Non-Color",256),
    "EmissiveMask": ("Non-Color",256), "EmissiveColor": ("sRGB",256),
}


def png(path, array):
    """Write PNG pixels without a view transform. Data arrays use bottom-left UV origin."""
    h,w = array.shape[:2]
    channels = 2 if array.ndim == 3 else 0
    def chunk(name, payload):
        return struct.pack(">I",len(payload))+name+payload+struct.pack(">I",zlib.crc32(name+payload))
    image = b"".join(b"\x00"+row.tobytes() for row in array[::-1])
    payload = struct.pack(">IIBBBBB",w,h,8,channels,0,0,0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",payload)+chunk(b"IDAT",zlib.compress(image,9))+chunk(b"IEND",b""))


def atlas(size):
    """Return sRGB albedo, height and linear PBR signals for both wrapped profiles."""
    vv, uu = np.mgrid[0:size,0:size].astype(np.float32)
    uu=(uu+.5)/size
    vv=(vv+.5)/size
    s=np.clip((uu-.028)/.944,0,1)
    a=s*TAU
    color=np.zeros((*s.shape,3),np.float32)
    rough=np.full(s.shape,.4,np.float32)
    metal=np.full(s.shape,.25,np.float32)
    emit=np.zeros(s.shape,np.float32)
    height=np.zeros(s.shape,np.float32)
    for i, (_,_,_,profile, bottom, top) in enumerate(FRAME):
        cells=len(profile)
        band=(vv>=bottom-.011)&(vv<=top+.011)
        line=np.clip((vv-bottom)/(top-bottom)*cells,0,cells-.0001)
        row=line.astype(np.int32)
        side=line-row
        light=np.array(PALETTES[i],np.float32)[row]
        pulse=(.83+.10*np.cos(a*7+.45)+.06*np.cos(a*17-1.8))[:,:,None]
        joints=np.exp(-(np.sin(8*a+.17)/.095)**2)
        strokes=np.exp(-(np.sin(39*a+2.8*line)/.21)**2)
        # Two fine tracks split and rejoin around the cobalt trough.
        channel=4.25 if i==0 else 3.46
        wander=.24*np.arcsin(.96*np.sin(a*14+.3))+.28*np.sin(a*5+.17)
        trace=np.exp(-((line-channel-wander)/.105)**2)
        fork=np.exp(-((line-channel-wander-.37*np.sin(a*23))/ .078)**2) * np.maximum(0,np.sin(11*a+1.1))**4
        charge=np.clip(trace*.75+fork*.65,0,1)
        edges=np.exp(-((side-.18)/.085)**2)+.44*np.exp(-((side-.85)/.07)**2)
        spark=np.exp(-(np.sin(a*5+.24)/.25)**2)
        detail=light*pulse - joints[:,:,None]*np.array([13,27,32]) + charge[:,:,None]*np.array([100,148,74])
        detail+= (edges*(strokes*.54+spark*.30))[:,:,None]*np.array([16,24,12])
        color[band]=detail[band]
        rough[band]=(.23+.23*joints+.12*(row%3==0)-.07*charge)[band]
        metal[band]=(.07+.57*(row%4==0)+.14*joints)[band]
        emit[band]=np.clip(.14+(.57*(row%4==2))+.29*(row%3==1)+.42*charge+.15*spark-.12*joints,.08,1)[band]
        height[band]=(.42*edges+.64*charge+.16*np.sin(a*40+line*4)-.63*joints+.20*strokes)[band]
    for i,rgb in enumerate(SWATCHES):
        detail=(vv>=.84)&(np.abs(uu-SWATCH_X[i])<=.1)
        color[detail]=rgb
        emit[detail]=[.67,.90,1.0,.47,.19][i]
        rough[detail]=[.23,.21,.20,.23,.36][i]
        metal[detail]=[.13,.08,.04,.16,.48][i]
    return np.clip(color,0,255), np.clip(rough,0,1), np.clip(metal,0,1), np.clip(emit,0,1), height


def make_textures():
    c, _, _, _, _=atlas(1024)
    png(ASSET/"texturas/BaseColor.png",c.astype(np.uint8))
    c,r,m,e,h=atlas(256)
    normal=np.stack((-np.gradient(h,axis=1)*.27,-np.gradient(h,axis=0)*.28,np.ones(h.shape)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    png(ASSET/"texturas/Normal.png",((normal*.5+.5)*255+.5).astype(np.uint8))
    for name,v in [("Roughness",r),("Metalness",m),("EmissiveMask",e)]:
        png(ASSET/f"texturas/{name}.png",(v*255+.5).astype(np.uint8))
    linear=np.where(c/255<=.04045,c/255/12.92,((c/255+.055)/1.055)**2.4)*e[:,:,None]
    srgb=np.where(linear<=.0031308,linear*12.92,1.055*np.power(linear,1/2.4)-.055)
    png(ASSET/"texturas/EmissiveColor.png",(srgb*255+.5).astype(np.uint8))


def make_material():
    mat=bpy.data.materials.new("ZAREK Eternal Halo | atlas PBR")
    nodes=mat.node_tree.nodes
    links=mat.node_tree.links
    shader=nodes.get("Principled BSDF")
    mat.diffuse_color=(.04,.36,.96,1)
    mat.use_backface_culling=True
    tex={}
    for index,(key,(space,_)) in enumerate(TEX.items()):
        img=bpy.data.images.load(str(ASSET/"texturas"/(key+".png")),check_existing=True)
        img.colorspace_settings.name=space
        img.pack()
        node=nodes.new("ShaderNodeTexImage")
        node.name=key
        node.label=key + (" · Roblox SurfaceAppearance" if key=="EmissiveMask" else "")
        node.location=(-600,720-index*290)
        node.image=img
        tex[key]=node.outputs["Color"]
    for key,socket in [("BaseColor","Base Color"),("Roughness","Roughness"),
                       ("Metalness","Metallic"),("EmissiveColor","Emission Color")]:
        links.new(tex[key],shader.inputs[socket])
    normal=nodes.new("ShaderNodeNormalMap")
    normal.location=(-290,20)
    normal.inputs["Strength"].default_value=.7
    links.new(tex["Normal"],normal.inputs["Color"])
    links.new(normal.outputs["Normal"],shader.inputs["Normal"])
    shader.inputs["Emission Strength"].default_value=1.55
    return mat


def closed_mesh(name,verts,faces,collection):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(verts,[],faces)
    mesh.update()
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj=bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    mesh.materials.append(PBR)
    return obj


def ring_position(i,angle,delta_r=0,delta_z=0):
    radius,z,rotate,*_=FRAME[i]
    return rotate @ Vector((sin(angle)*(radius+delta_r),-cos(angle)*(radius+delta_r),delta_z))+Vector((0,0,z))


def make_ring(i,count,name,collection):
    profile=FRAME[i][3]
    lower,upper=FRAME[i][4:]
    k=len(profile)
    verts=[]
    for j in range(count):
        a=TAU*j/count
        modulation=1+.035*cos(8*a)+.021*sin(16*a-.4)
        for dr,dz in profile:
            verts.append(ring_position(i,a,dr*modulation,dz*modulation))
    faces=[(j*k+p,((j+1)%count)*k+p,((j+1)%count)*k+(p+1)%k,j*k+(p+1)%k)
           for j in range(count) for p in range(k)]
    obj=closed_mesh(name,verts,faces,collection)
    uv=obj.data.uv_layers.new(name="EternalHaloAtlas")
    for poly in obj.data.polygons:
        poly.use_smooth=True
        rows=[divmod(v,k) for v in poly.vertices]
        seam_u={x for x,_ in rows}=={0,count-1}
        seam_v={y for _,y in rows}=={0,k-1}
        for loop,(x,y) in zip(poly.loop_indices,rows):
            u=1 if not x and seam_u else x/count
            v=1 if not y and seam_v else y/k
            uv.data[loop].uv=(.028+.944*u,lower+(upper-lower)*v)
    obj.data.set_sharp_from_angle(angle=radians(44))
    return obj


def swatch_uv(obj,indices):
    # Insets inside identically colored swatches. Reuse is deliberate for metal/energy details.
    uv=obj.data.uv_layers.new(name="EternalHaloAtlas")
    for poly,s in zip(obj.data.polygons,indices):
        for j,loop in enumerate(poly.loop_indices):
            a=TAU*j/poly.loop_total
            uv.data[loop].uv=(SWATCH_X[s]+cos(a)*.055,.916+sin(a)*.043)


def make_star(i,angle,size,name,collection):
    p=ring_position(i,angle,.019,.015)
    radial=(p-ring_position(i,angle,-.10,.015)).normalized()
    up=FRAME[i][2] @ Vector((0,0,1))
    across=up.cross(radial)
    outline=[up, .19*(up+across),.76*across,.19*(-up+across),
             -up,.19*(-up-across),-.76*across,.19*(up-across)]
    verts=[p+v*size for v in outline]+[p+radial*size*.25,p-radial*size*.22]
    faces=[(j,(j+1)%8,k) for k in (8,9) for j in range(8)]
    obj=closed_mesh(name,verts,faces,collection)
    swatch_uv(obj,[2 if j%4 in (0,3) else 1 for j in range(16)])
    return obj


def tube(points,radii,sides,name,collection,s=0):
    verts=[]
    for j,p in enumerate(points):
        tangent=(points[min(j+1,len(points)-1)]-points[max(j-1,0)]).normalized()
        u=tangent.cross(Vector((0,0,1))).normalized()
        v=tangent.cross(u).normalized()
        verts.extend(p+radii[j]*(cos(TAU*k/sides)*u+sin(TAU*k/sides)*v) for k in range(sides))
    faces=[tuple(range(sides-1,-1,-1))]
    faces.extend((j*sides+k,(j+1)*sides+k,(j+1)*sides+(k+1)%sides,j*sides+(k+1)%sides)
                 for j in range(len(points)-1) for k in range(sides))
    faces.append(tuple(range((len(points)-1)*sides,len(points)*sides)))
    obj=closed_mesh(name,verts,faces,collection)
    swatch_uv(obj,[s if j%6 else min(2,s+1) for j in range(len(faces))])
    return obj


def arcs(i,start,span,n,name,collection,branch=False):
    edge=FRAME[i][3]
    width=max(dr for dr,_ in edge)
    points=[]
    radii=[]
    for k in range(n):
        t=k/(n-1)
        amp=sin(pi*t)
        irregular=(.40+.60*cos(t*TAU*2.45+.25)**2) * amp
        dr=width-.006+(.048 if i==0 else .034)*irregular
        z=-.005+.042*amp*sin(9*t+.3)
        if branch:
            dr+=.046*t
            z-=.055*t
        points.append(ring_position(i,start+span*t,dr,z))
        radii.append((.0027+.0047*amp)*(.68 if branch else 1))
    return tube(points,radii,5 if n>10 else 4,name,collection,1 if branch else 0)


def group(name):
    c=bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def detail_geometry(i,collection,high):
    stars=[(.0,.118),(1.67,.068),(3.20,.082),(4.93,.060)] if i==0 else [(.77,.050),(2.50,.059),(5.08,.050)]
    objects=[make_star(i,a,s,f"Stellar facet {i+1}.{j+1:02}",collection)
             for j,(a,s) in enumerate(stars)]
    arcspec=[(.06,.53),(2.23,.46),(3.35,.38),(4.74,.51)] if i==0 else [(.92,.46),(2.88,.54),(5.31,.49)]
    for j,(start,span) in enumerate(arcspec):
        objects.append(arcs(i,start,span,25 if high else 8,f"Lightning tracer {i+1}.{j+1:02}",collection))
        if high or (i==0 and j in (0,2)):
            objects.append(arcs(i,start+span*.30,span*.42,15 if high else 6,f"Fork {i+1}.{j+1:02}",collection,True))
    if high:
        for j in range(12):
            start=(j+.22)*TAU/12
            points=[]
            for k in range(12):
                t=k/11
                points.append(ring_position(i,start+.22*t,-.049 if i==0 else -.023,.020+.005*sin(pi*t)))
            radii=[.0018+.0032*sin(pi*k/11) for k in range(12)]
            objects.append(tube(points,radii,6,f"Inner filament {i+1}.{j+1:02}",collection,1))
        for j in range(16):
            a=(j+.66)*TAU/16
            points=[ring_position(i,a,.023 if i==0 else .012,.032 if i==0 else .017),
                    ring_position(i,a+.019,.047 if i==0 else .022,.024 if i==0 else .018),
                    ring_position(i,a+.036,.052 if i==0 else .029,.018 if i==0 else .014)]
            objects.append(tube(points,[.0025,.0043,.0017],5,f"Prism seam {i+1}.{j+1:02}",collection,2))
    return objects


def reset():
    global PBR
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.unit_settings.system="NONE"
    bpy.context.preferences.filepaths.save_version=0
    PBR=make_material()


def select(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]


def triangulate(obj):
    select([obj])
    mod=obj.modifiers.new("Explicit triangulation","TRIANGULATE")
    mod.keep_custom_normals=True
    bpy.ops.object.modifier_apply(modifier=mod.name)


def default_view():
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                space=area.spaces.active
                space.region_3d.view_rotation=Vector((-.53,1,-.45)).to_track_quat("-Z","Y")
                space.region_3d.view_distance=4.9
                space.region_3d.view_location=(0,0,1.17)
                space.shading.color_type="MATERIAL"


def save(name):
    default_view()
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET/"blender"/(name+".blend")),compress=True)


def export(objects,name):
    select(objects)
    bpy.ops.export_scene.fbx(filepath=str(ASSET/"exportaciones"/(name+".fbx")),use_selection=True,
        object_types={"MESH"},apply_scale_options="FBX_SCALE_UNITS",axis_forward="-Z",axis_up="Y",
        bake_space_transform=True,path_mode="COPY",embed_textures=True,bake_anim=False)
    bpy.ops.export_scene.gltf(filepath=str(ASSET/"exportaciones"/(name+".glb")),use_selection=True,
        export_format="GLB",export_yup=True,export_apply=True,export_animations=False)


def build_ugc():
    collection=group("UGC · single rigid hat")
    objects=[make_ring(0,72,"Zenith",collection),make_ring(1,64,"Meridian",collection)]
    objects+=detail_geometry(0,collection,False)+detail_geometry(1,collection,False)
    select(objects)
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name="EternalHalo_UGC"
    triangulate(obj)
    obj.data.calc_loop_triangles()
    assert len(obj.data.loop_triangles)<=4000, len(obj.data.loop_triangles)
    pin=bpy.data.objects.new("HatAttachment · Blender placement reference",None)
    collection.objects.link(pin)
    pin.empty_display_type="ARROWS"
    pin.empty_display_size=.13
    save("EternalHalo_UGC")
    export([obj],"EternalHalo_UGC")


def build_high(animated):
    root=group("GOD MODE · experience" if animated else "MASTER · editable components")
    groups=[]
    for i,name in enumerate(("Zenith","Meridian")):
        c=bpy.data.collections.new(name)
        root.children.link(c)
        objects=[make_ring(i,256 if i==0 else 224,f"{name}_Band",c)]+detail_geometry(i,c,True)
        groups.append(objects)
        if not animated:
            continue
        center=Vector((0,0,FRAME[i][1]))
        # Keep each band and effect geometry separately editable in the .blend.
        pivot=bpy.data.objects.new(f"{name}_Pivot",None)
        c.objects.link(pivot)
        pivot.rotation_mode="XYZ"
        basis=FRAME[i][2].to_4x4()
        basis.translation=center
        pivot.matrix_world=basis
        bpy.context.view_layer.update()
        mount=bpy.data.objects.new(f"{name}_PreviewSpin",None)
        c.objects.link(mount)
        mount.parent=pivot
        bpy.context.view_layer.update()
        for obj in objects:
            original=obj.matrix_world.copy()
            obj.parent=mount
            obj.matrix_world=original
        for j,a in enumerate((.18,1.79,3.32,4.93)):
            socket=bpy.data.objects.new(f"{name}_FX_{j+1:02}",None)
            c.objects.link(socket)
            socket.empty_display_type="SPHERE"
            socket.empty_display_size=.025
            socket.parent=mount
            socket.location=basis.inverted() @ ring_position(i,a,.043,.015)
        mount.keyframe_insert(data_path="rotation_euler",index=2,frame=1)
        mount.rotation_euler.z=TAU*(1 if i==0 else -2)
        mount.keyframe_insert(data_path="rotation_euler",index=2,frame=241)
        for fc in mount.animation_data.action.layers[0].strips[0].channelbag(mount.animation_data.action_slot).fcurves:
            for key in fc.keyframe_points:
                key.interpolation="LINEAR"
    scene=bpy.context.scene
    scene.render.fps=24
    scene.frame_end=240
    scene.frame_set(1)
    if not animated:
        select(groups[0][:1])
        save("EternalHalo_MASTER")
        return
    save("EternalHalo_GOD_MODE")
    # Flatten per-ring export at the bind pose while preserving the original editable .blend.
    bpy.context.view_layer.update()
    exports=[]
    rig={}
    for name,objects in zip(("Zenith","Meridian"),groups):
        clones=[]
        for source in objects:
            obj=bpy.data.objects.new(source.name+"_Export",source.data.copy())
            scene.collection.objects.link(obj)
            obj.matrix_world=source.matrix_world
            clones.append(obj)
        select(clones)
        bpy.ops.object.join()
        part=bpy.context.object
        part.name=name
        pivot=bpy.data.objects[f"{name}_Pivot"].matrix_world.copy()
        part.data.transform(pivot.inverted() @ part.matrix_world)
        part.matrix_world=pivot
        triangulate(part)
        sockets=[o for o in bpy.context.scene.objects if o.name.startswith(name+"_FX_")]
        def triples(vec):
            return [round(x,6) for x in vec]
        rig[name]={
            "pivot_pose_blender_rows":[[round(v,6) for v in row] for row in pivot],
            "spin_axis_local_blender":[0,0,1],
            "rotation_degrees_per_second":36 if name=="Zenith" else -72,
            "particle_or_beam_points_local_blender":{
                point.name:triples(pivot.inverted() @ point.matrix_world.translation)
                for point in sorted(sockets,key=lambda o:o.name)
            }
        }
        exports.append(part)
    export(exports,"EternalHalo_GOD_MODE")
    manifest={"units":"studs","blender_to_gltf_axes":"(x, z, -y)",
              "asset_root":"Top of the R15 head. Authoring origin at (0,0,0).",
              "rotation_preview":"Blender .blend, 24 fps, frames 1 to 240.",
              "parts":rig}
    (ASSET/"roblox/god_mode_rig.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    for folder in ("blender","texturas","exportaciones","validacion"):
        (ASSET/folder).mkdir(exist_ok=True)
    mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "all"
    assert mode in ("all","god"), mode
    if mode=="all":
        make_textures()
        reset()
        build_ugc()
        reset()
        build_high(False)
    reset()
    build_high(True)
    print("ETERNAL_HALO_BUILD_PASS",flush=True)
