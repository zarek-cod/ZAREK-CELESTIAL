
"""Editable cubic lock meshes, unique UV atlas, and FBX/GLB export for Celestial Hair."""
from dataclasses import dataclass
from math import atan2, cos, hypot, pi, sin, tau
from pathlib import Path
import random
import struct
import zlib

import bpy
import bmesh
import numpy as np
from mathutils import Vector

A=Path(__file__).resolve().parents[1]
COLS,ROWS=8,7
GUTTER=.074


@dataclass(frozen=True)
class Lock:
    label: str
    group: str
    path: tuple
    width: float
    depth: float
    normal: tuple
    twist: float=.0
    primary: bool=False


def lock(label,group,a,b,c,d,width,depth,normal=(0,-1,.33),twist=0,primary=False):
    return Lock(label,group,(a,b,c,d),width,depth,normal,twist,primary)


# Every visible lock has an independent cubic flow, shoulder width, depth, roll and tip.
# Coordinates are in studs with Blender -Y forward. Origin is the top of the Classic head.
DESIGN=[
    lock("01 Sweep over left brow","Fringe",(.28,-.19,.10),(.25,-.61,.15),(-.02,-.693,-.17),(-.36,-.596,-.415),.155,.075,twist=.32,primary=True),
    lock("02 Long central hook","Fringe",(.36,-.18,.035),(.34,-.64,.025),(.24,-.70,-.270),(.018,-.608,-.534),.125,.066,twist=-.17,primary=True),
    lock("03 Swept left wing","Fringe",(.082,-.27,.06),(-.06,-.615,-.08),(-.46,-.64,-.406),(-.801,-.408,-.451),.125,.058,twist=.43,primary=True),
    lock("04 Smaller center split","Fringe",(.08,-.29,.05),(.06,-.583,-.10),(-.09,-.632,-.315),(-.136,-.617,-.474),.098,.062,twist=-.4,primary=True),
    lock("05 Right crest curl","Fringe",(.265,-.24,.012),(.45,-.56,-.075),(.564,-.613,-.417),(.504,-.481,-.503),.099,.064,twist=.19,primary=True),
    lock("06 Right outer sweep","Fringe",(.42,-.12,.045),(.55,-.389,-.128),(.645,-.59,-.440),(.804,-.396,-.396),.115,.063,twist=-.39,primary=True),
    lock("07 Inner right split","Fringe",(.30,-.222,.0),(.352,-.490,-.15),(.435,-.578,-.366),(.351,-.552,-.442),.088,.058,twist=.53,primary=True),
    lock("08 Left lower layer","Fringe",(-.14,-.23,.016),(-.327,-.567,-.185),(-.523,-.579,-.482),(-.638,-.440,-.515),.11,.061,twist=.33,primary=True),
    lock("09 Left falling temple","Fringe",(-.36,-.152,-.026),(-.45,-.37,-.151),(-.566,-.50,-.51),(-.692,-.409,-.675),.098,.065,twist=.36,primary=True),
    lock("10 Right falling temple","Fringe",(.46,-.14,-.03),(.52,-.37,-.18),(.645,-.504,-.47),(.654,-.39,-.686),.090,.065,twist=-.45,primary=True),
    lock("11 Crossing crown tuft","Part",(.235,.38,.058),(.30,.14,.252),(.025,-.342,.196),(-.481,-.603,-.266),.126,.066,(0,-.30,1),.31,True),
    lock("12 Back-swept part","Part",(.265,-.11,.088),(.344,.13,.226),(.419,.397,.148),(.628,.483,-.273),.111,.064,(.45,.5,.9),-.22,True),
]


def add_side_layers():
    guide=[
        ("Crest",(.41,.12,.065),(.54,.123,-.014),(.707,-.23,-.455),(.851,-.265,-.333),.108,.068),
        ("Temple",(.49,.06,-.002),(.57,-.115,-.206),(.687,-.339,-.485),(.701,-.27,-.700),.128,.073),
        ("Outer wing",(.44,.34,-.058),(.543,.229,-.21),(.720,.058,-.535),(.861,-.086,-.528),.118,.071),
        ("Sideburn",(.545,-.011,-.147),(.594,-.151,-.36),(.636,-.285,-.646),(.570,-.247,-.835),.088,.065),
        ("Behind ear",(.49,.22,-.040),(.589,.197,-.33),(.645,.217,-.67),(.617,.169,-.930),.114,.066),
        ("Occipital edge",(.44,.348,-.106),(.54,.417,-.26),(.686,.397,-.494),(.774,.326,-.631),.102,.063),
    ]
    for side,sign in (("L",-1),("R",1)):
        for j,(name,*values) in enumerate(guide):
            a,b,c,d,w,h=values
            def point(p,k):
                x,y,z=p
                shift=(.027*sin(j*1.7+k*.9) if sign==1 else 0)
                return (sign*(x+shift),y+(0.025*cos(j*.91) if sign==1 and k>0 else 0),
                        z+(.043*sin(j*1.13) if sign==1 and k>0 else 0))
            DESIGN.append(lock(f"{side} {name}","Temple",*(point(p,k) for k,p in enumerate((a,b,c,d))),w,h,
                               (sign,.09 if j>2 else -.28,.46),sign*(.21+.13*cos(j))))


def add_back_layers():
    rng=random.Random(592)
    for tier,count in enumerate((8,8,3)):
        for i in range(count):
            p=i/(count-1)
            theta=-1.17+2.34*p+(tier%2)*.06
            sweep=.16*cos(i*1.12)+(.075 if tier==0 else -.07)
            bottom=(-.640,-.859,-.990)[tier]+.16*abs(p-.5)*2+rng.uniform(-.067,.032)
            w=(.136,.123,.111)[tier]*rng.uniform(.87,1.09)
            h=(.078,.074,.065)[tier]*rng.uniform(.91,1.1)
            def pos(angle,r,z):
                return (r*sin(angle),r*cos(angle),z)
            root=pos(theta-.18,(.375,.495,.52)[tier],(.088,-.12,-.35)[tier])
            bulge=pos(theta-sweep*.35,(.66,.63,.63)[tier],(-.12,-.29,-.52)[tier])
            bend=pos(theta+sweep*.4,(.72,.74,.67)[tier],bottom+.17)
            tip=pos(theta+sweep,(.719,.68,.61)[tier]+rng.uniform(-.020,.014),bottom)
            DESIGN.append(lock(f"Back {tier+1}.{i+1:02}",("Occiput","Back layers","Nape")[tier],root,bulge,bend,tip,
                               w,h,(sin(theta),cos(theta),.34),rng.uniform(-.49,.49)))


def prepare_design():
    add_side_layers()
    add_back_layers()
    # Feathered face framing ends sit outside the eye silhouette and above the jaw.
    DESIGN.extend([
       lock("15 Whorl · front left","Whorl",(.12,.115,.10),(-.19,.014,.280),(-.415,-.13,.198),(-.56,-.375,-.165),.145,.072,(-.27,-.20,1),.22),
       lock("16 Whorl · back left","Whorl",(.13,.11,.112),(-.121,.107,.285),(-.27,.36,.194),(-.396,.505,-.218),.145,.072,(-.15,.38,1),.38),
       lock("17 Whorl · rear crown","Whorl",(.09,-.055,.102),(.11,.17,.322),(.12,.417,.249),(.055,.631,-.230),.164,.073,(.10,.39,1),-.24),
       lock("18 Whorl · short right","Whorl",(.16,.122,.085),(.279,.066,.252),(.487,-.073,.153),(.611,-.26,-.200),.119,.068,(.41,-.22,1),-.26),
       lock("13 Part left back flow","Part",(.18,-.024,.122),(-.18,-.03,.231),(-.27,.362,.158),(-.492,.55,-.273),.106,.059,(-.35,.43,1),.39),
       lock("14 Part left outward flow","Part",(.20,-.142,.123),(-.11,-.237,.22),(-.40,-.376,.095),(-.635,-.377,-.323),.103,.059,(-.45,-.32,1),-.24),
       lock("L thin face framing tip","Temple",(-.43,-.29,-.12),(-.55,-.43,-.30),(-.61,-.472,-.53),(-.684,-.370,-.786),.073,.039,(-.7,-.6,.31),.63),
       lock("R thin face framing tip","Temple",(.45,-.23,-.16),(.50,-.40,-.30),(.562,-.492,-.53),(.522,-.375,-.790),.073,.045,(.72,-.48,.33),-.37),
    ])


def fit_inside_crown(p):
    # Keep the roots inside the measured ring envelope. The hair fans out below the lower rim.
    u=max(0,min(1,(-p.z-.235)/.115))
    u=u*u*(3-2*u)
    rx,ry=.683+.207*u,.597+.205*u
    factor=hypot(p.x/rx,p.y/ry)
    if factor>1:
        p.x/=factor
        p.y/=factor
    return p


def profile_scale(t):
    # Broad midshaft with a short swept tip, avoiding straight radial cones.
    return float(np.interp(t,[0,.13,.28,.46,.63,.78,.89,.96,1],
                          [.48,.82,1.015,.96,.79,.53,.27,.095,0]))


def ribbon_relief(u,v,index):
    phase=.53*sin(index*2.17)
    theta=u*tau
    front=np.maximum(0,np.sin(theta))
    # Longitudinal grooves vary in width and bow toward the point.
    bend=.40*np.sin(v*5+phase)+.21*np.sin(v*9-.3)
    wave=np.cos(theta*11+bend+phase)*.62+np.cos(theta*18-bend*.7+phase)*.38
    taper=np.sin(np.pi*np.clip(v,0,1))**.43
    return wave * front**.42 * taper


def frame(l,t):
    p0,p1,p2,p3=map(Vector,l.path)
    b=1-t
    point=b**3*p0+3*b*b*t*p1+3*b*t*t*p2+t**3*p3
    tangent=(3*b*b*(p1-p0)+6*b*t*(p2-p1)+3*t*t*(p3-p2)).normalized()
    outer=Vector(l.normal)
    outer=(outer-tangent*outer.dot(tangent)).normalized()
    width=tangent.cross(outer).normalized()
    roll=l.twist*(.2+.8*t)+.16*sin(t*pi)
    return point,width*cos(roll)+outer*sin(roll),outer*cos(roll)-width*sin(roll)


def to_atlas(i,u,v):
    return ((i%COLS+GUTTER+(1-2*GUTTER)*u)/COLS,
            (i//COLS+GUTTER+(1-2*GUTTER)*v)/ROWS)


def create_mesh(name,vertices,faces,uvs,mat,collection):
    mesh=bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    layer=mesh.uv_layers.new(name="HairAtlas")
    for polygon,coords in zip(mesh.polygons,uvs):
        polygon.use_smooth=True
        for loop,uv in zip(polygon.loop_indices,coords):
            layer.data[loop].uv=uv
    bm=bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=bm.faces)
    if bm.calc_volume(signed=True)<0:
        bmesh.ops.reverse_faces(bm,faces=bm.faces)
    bm.to_mesh(mesh)
    bm.free()
    obj=bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    obj.data.materials.append(mat)
    return obj


def lock_mesh(definition,index,high,mat,collection):
    if high:
        samples,cross=(25,32) if definition.primary else (19,24)
    else:
        samples,cross=(9,8) if definition.primary else (5,6)
        if definition.label.startswith("14 "):
            samples=6
        if definition.group in ("Back layers","Nape"):
            samples=3
        if definition.group=="Whorl":
            samples=4
        if definition.label.startswith(("04 ","07 ","08 ","12 ")):
            samples=8
        if definition.label in {"02 Long central hook","09 Left falling temple","10 Right falling temple"}:
            samples=10
    vertices=[]
    lengths=[]
    for row in range(samples):
        t=row/samples
        p,side,outer=frame(definition,t)
        scaling=profile_scale(t)
        lengths.append(t)
        for j in range(cross):
            u=j/cross
            a=u*tau
            x=cos(a)
            y=sin(a)
            # The flattened tear-drop cross-section has a raised ridge and rounded shoulders.
            lift=(y*(.81+.19*abs(y))) if y>0 else y*.56
            lift+=.132*max(0,y)*sin(a*3.0+.7+1.1*t)
            groove=.105*float(ribbon_relief(u,t,index)) if high else 0
            point=p+side*(definition.width*scaling*x)+outer*(definition.depth*scaling*(lift+groove))
            vertices.append(fit_inside_crown(point))
    tip_index=len(vertices)
    vertices.append(fit_inside_crown(Vector(definition.path[-1])))
    root_index=len(vertices)
    vertices.append(fit_inside_crown(Vector(definition.path[0])))
    faces=[]
    uvs=[]
    def add(face,values):
        faces.append(face)
        uvs.append([to_atlas(index,u,v) for u,v in values])
    for j in range(cross):
        u=j/cross
        w=(j+1)/cross
        k=(j+1)%cross
        add((root_index,k,j),((.5,0),(w,.045),(u,.045)))
        for r in range(samples-1):
            lo=.045+.910*lengths[r]
            hi=.045+.910*lengths[r+1]
            add((r*cross+j,r*cross+k,(r+1)*cross+k,(r+1)*cross+j),((u,lo),(w,lo),(w,hi),(u,hi)))
        lo=.045+.910*lengths[-1]
        r=(samples-1)*cross
        add((r+j,r+k,tip_index),((u,lo),(w,lo),(u+(w-u)*.5,1)))
    obj=create_mesh(definition.label,vertices,faces,uvs,mat,collection)
    if high:
        obj["Bezier control points"]=[x for p in definition.path for x in p]
        obj["Width in studs"]=definition.width
        obj["Thickness in studs"]=definition.depth
        obj["Atlas tile"]=index
    return obj


def scalp(index,high,mat,collection):
    # Concealed foundation underneath the moving layers, sealed on the inside of the head.
    n=48 if high else 16
    ring=[(.13,.79),(.30,.645),(.55,.51),(.81,.35),(1.0,.10),(1.0,.0),(.96,-.27),(.70,-.52)]
    if not high:
        ring=[ring[i] for i in (0,2,3,4,5,6,7)]
    verts=[]
    for frac,zeta in ring:
        for i in range(n):
            theta=i/n*tau
            forward=(1+cos(theta))/2
            # The front hairline is high; at the back the nape is covered.
            end=-.84+.54*forward**1.42
            z=end+(-end+.168)*(zeta if zeta>=0 else 0)
            if zeta<0:
                z=end+(-zeta)*.105
            silhouette=(.605+.012*sin(theta*3+.44),.603+.016*cos(theta*3))
            verts.append(fit_inside_crown(Vector((silhouette[0]*sin(theta)*frac,-silhouette[1]*cos(theta)*frac,z))))
    verts.extend([(0,0,.170),(0,0,-.286)])
    faces=[];uvs=[]
    m=len(ring)
    def add(face,coords):
        faces.append(face);uvs.append([to_atlas(index,u,v) for u,v in coords])
    for j in range(n):
        k=(j+1)%n
        u=j/n
        w=(j+1)/n
        add((m*n,j,k),((.5,0),(u,.05),(w,.05)))
        for r in range(m-1):
            v0=.05+.90*r/(m-1)
            v1=.05+.90*(r+1)/(m-1)
            add((r*n+j,(r+1)*n+j,(r+1)*n+k,r*n+k),((u,v0),(u,v1),(w,v1),(w,v0)))
        lo=(m-1)*n
        add((lo+k,lo+j,m*n+1),((w,.95),(u,.95),(.5,1)))
    return create_mesh("Scalp · hidden roots",verts,faces,uvs,mat,collection)


def write_png(file,pixels):
    h,w=pixels.shape[:2]
    kind=2 if pixels.ndim==3 else 0
    def chunk(tag,data):
        return struct.pack(">I",len(data))+tag+data+struct.pack(">I",zlib.crc32(tag+data))
    stream=b"".join(b"\0"+row.tobytes() for row in pixels[::-1])
    header=struct.pack(">IIBBBBB",w,h,8,kind,0,0,0)
    file.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)+chunk(b"IDAT",zlib.compress(stream,9))+chunk(b"IEND",b""))


def texture_signals(size):
    y,x=np.mgrid[0:size,0:size].astype(np.float32)
    x=(x+.5)/size*COLS
    y=(y+.5)/size*ROWS
    i=x.astype(int)+y.astype(int)*COLS
    u=np.clip(((x%1)-GUTTER)/(1-2*GUTTER),0,1)
    v=np.clip(((y%1)-GUTTER)/(1-2*GUTTER),0,1)
    t=np.clip((v-.045)/.910,0,1)
    a=tau*u
    phase=.53*np.sin(i*2.17)
    bend=.4*np.sin(t*5+phase)+.21*np.sin(t*9-.3)
    groove=.62*np.cos(a*11+bend+phase)+.38*np.cos(a*18-bend*.7+phase)
    front=np.maximum(0,np.sin(a))
    hair_value=218+21*front-18*(1-t)**2.9+5.1*np.sin(i*1.9)+5.2*groove*front
    hair_value-=12*np.maximum(0,-np.sin(a))**1.22
    # Slim fibers ride the width of the curved lock and soften at the roots.
    fiber=np.sin(a*35-bend*2.7+phase)*.60+np.sin(a*53+bend*2+phase)*.4
    hair_value+=(2.1+1.5*t)*fiber
    hair_value+=6.0*front*np.sin(a*4.0+.28*np.sin(t*7)+phase)
    tint=1-front*.72
    rgb=np.stack((hair_value-13*tint,hair_value-8*tint,np.minimum(254,hair_value+5*tint+4)),axis=-1)
    cap=i>=len(DESIGN)
    rgb[cap]=np.stack((hair_value[cap]-.0,hair_value[cap]+3,np.minimum(251,hair_value[cap]+13)),axis=-1)*.91
    rough=np.clip(.48+.12*(1-front)+.043*groove-.059*t,.39,.66)
    relief=groove*front**.42*np.maximum(0,np.sin(pi*t))**.43
    normal=np.stack((-np.gradient(relief,axis=1)*.36,-np.gradient(relief,axis=0)*.25,np.ones(x.shape)),axis=-1)
    normal/=np.linalg.norm(normal,axis=-1,keepdims=True)
    normal[cap]=[0,0,1]
    return np.clip(rgb+.5,0,255).astype(np.uint8),(rough*255+.5).astype(np.uint8),((normal*.5+.5)*255+.5).astype(np.uint8)


def textures():
    high,_,_=texture_signals(1024)
    _,rough,normal=texture_signals(256)
    for key,image in [("BaseColor",high),("Roughness",rough),("Normal",normal)]:
        write_png(A/"texturas"/f"CelestialHair_{key}.png",image)


def material():
    mat=bpy.data.materials.new("Celestial Hair | silver dielectric PBR")
    mat.diffuse_color=(.64,.72,.88,1)
    mat.use_backface_culling=True
    nodes,links=mat.node_tree.nodes,mat.node_tree.links
    shader=nodes.get("Principled BSDF")
    shader.inputs["Metallic"].default_value=0
    shader.inputs["Roughness"].default_value=.53
    shader.inputs["IOR"].default_value=1.48
    shader.inputs["Specular IOR Level"].default_value=.29
    normal=nodes.new("ShaderNodeNormalMap")
    normal.location=(-300,-310)
    normal.inputs["Strength"].default_value=.78
    links.new(normal.outputs[0],shader.inputs["Normal"])
    for index,(name,use) in enumerate((("BaseColor",shader.inputs["Base Color"]),
                                       ("Roughness",shader.inputs["Roughness"]),
                                       ("Normal",normal.inputs["Color"]))):
        image=bpy.data.images.load(str(A/"texturas"/f"CelestialHair_{name}.png"))
        image.colorspace_settings.name="sRGB" if name=="BaseColor" else "Non-Color"
        image.pack()
        node=nodes.new("ShaderNodeTexImage")
        node.name=name
        node.label=name
        node.location=(-640,390-index*280)
        node.image=image
        links.new(node.outputs["Color"],use)
    return mat


def select(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]


def build(high):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.save_version=0
    scene=bpy.context.scene
    scene.unit_settings.system="NONE"
    groups={}
    mat=material()
    for name in dict.fromkeys([d.group for d in DESIGN]+["Foundation"] if high else ["Hair"]):
        c=bpy.data.collections.new(name)
        scene.collection.children.link(c)
        groups[name]=c
    objects=[lock_mesh(d,i,high,mat,groups[d.group if high else "Hair"]) for i,d in enumerate(DESIGN)]
    objects.append(scalp(len(DESIGN),high,mat,groups["Foundation" if high else "Hair"]))
    select(objects)
    if not high:
        bpy.ops.object.join()
        obj=bpy.context.object
        obj.name="CelestialHair_UGC"
        obj.data.name="CelestialHair · rigid mesh"
        tri=obj.modifiers.new("Final triangulation","TRIANGULATE")
        tri.keep_custom_normals=True
        bpy.ops.object.modifier_apply(modifier=tri.name)
        obj.data.calc_loop_triangles()
        print("UGC TRIANGLES",len(obj.data.loop_triangles),flush=True)
        assert len(obj.data.loop_triangles)<=4000
        assert len(obj.data.uv_layers)==1 and len(obj.data.materials)==1
    else:
        select(objects[:1])
    attach=bpy.data.objects.new("HairAttachment · Blender placement reference",None)
    scene.collection.objects.link(attach)
    attach.empty_display_type="ARROWS"
    attach.empty_display_size=.15
    scene["Roblox placement"]="Classic R15 head top. Blender X right, -Y front, +Z up. One unit = one stud."
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                view=area.spaces.active
                view.region_3d.view_rotation=Vector((-.47,1,-.28)).to_track_quat("-Z","Y")
                view.region_3d.view_distance=3.8
                view.region_3d.view_location=(0,0,-.38)
                view.shading.color_type="MATERIAL"
    stem="CelestialHair_MASTER" if high else "CelestialHair_UGC"
    bpy.ops.wm.save_as_mainfile(filepath=str(A/"blender"/f"{stem}.blend"),compress=True)
    if high:
        return
    select([obj])
    bpy.ops.export_scene.fbx(filepath=str(A/"exportaciones"/f"{stem}.fbx"),use_selection=True,
                            object_types={"MESH"},apply_scale_options="FBX_SCALE_UNITS",axis_forward="-Z",
                            axis_up="Y",bake_space_transform=True,path_mode="COPY",embed_textures=True,bake_anim=False)
    bpy.ops.export_scene.gltf(filepath=str(A/"exportaciones"/f"{stem}.glb"),use_selection=True,
                             export_format="GLB",export_yup=True,export_apply=True,export_animations=False)


if __name__=="__main__":
    for sub in ("blender","texturas","exportaciones"):
        (A/sub).mkdir(exist_ok=True)
    prepare_design()
    assert len(DESIGN)+1<=COLS*ROWS,len(DESIGN)+1
    textures()
    build(True)
    build(False)
    print("CELESTIAL_HAIR_BUILD_PASS",flush=True)
