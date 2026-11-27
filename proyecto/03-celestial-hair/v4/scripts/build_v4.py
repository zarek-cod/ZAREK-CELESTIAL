"""Refine V3 C, author a controlled UGC retopology, and export the evaluated V4."""
from pathlib import Path
import argparse
import json
import math
import sys

import bpy
import bmesh
import numpy as np
from mathutils import Vector

HERE=Path(__file__).resolve().parent
ASSET=HERE.parent
HAIR=ASSET.parent
WORK=HAIR/"work/v4"
sys.path.insert(0,str(HAIR/"v3/scripts"))
import produce as sculpt
from diseno import DESIGNS
sys.path.insert(0,str(HAIR/"scripts"))
import validate_hair as checks

SOURCE=HAIR/"v3/blender/CelestialHair_V3_C_MASTER.blend"
GRID=7
PADDING=.042
STEM="CelestialHair_V4"
SOFT=(.78,.82,.88)
original_closed_mesh=sculpt.closed_mesh
control_sections={}

# V3 C stays the source. Changes are localized to eye-facing bangs, nape
# endpoints, and the root section under the original crown's metal band.
def refine_recipe():
    edited=[]
    for index,(name, zone, stations, color, roll) in enumerate(DESIGNS["C"][1]):
        result=[]
        for i,(x,y,z,width,depth) in enumerate(stations):
            tip=i/(len(stations)-1)
            if zone=="Flequillo":
                lower=float(sculpt.smooth(-.22,-.51,z))
                near_eye=float(sculpt.smooth(.43,.08,abs(x)))
                lift=lower*near_eye
                z+=.135*lift
                width*=1-.14*lift
                if "entrecejo" in name:
                    x-=.061*lower
                    depth*=1-.12*lower
                if "intermedia derecha" in name:
                    x+=.064*lower
            if zone in {"Nuca","Nuca superior"}:
                ease=float(sculpt.smooth(.39,1,tip))
                x+=.048*ease*math.sin(index*1.91)
                y+=.036*ease*math.cos(index*2.37)
                z+=.068*ease*math.sin(index*1.73+.4)
                roll_delta=.12*math.sin(index*1.71)
                width*=1+.13*ease*math.cos(index*1.43)
            result.append((x,y,z,width,depth))
        if zone in {"Nuca","Nuca superior"}:
            roll+=roll_delta
        if index in {21,24,26,40,42,44}:
            color=2
        edited.append((name,zone,result,color,roll))
    return edited


def inset_control(name, positions, mapping, sides, tile, collection, material, level):
    rings=[]
    for section in positions:
        center=sum(section,Vector((0,0,0)))/sides
        radial=Vector((center.x,center.y,0))
        r=radial.length
        z=center.z
        if r>.32:
            radial.normalize()
            band=float(sculpt.smooth(.16,-.026,z)*(1-sculpt.smooth(.207,.365,-z)))
            front=.55+.45*abs(radial.y)
            amount=(.015+.016*front)*band*float(sculpt.smooth(.36,.54,r))
            if name.startswith("Base"):
                # Keep the filler inside the visible locks even through the band.
                # Narrow the most prominent frontal and lateral cap without cutting the hairline.
                below=float(sculpt.smooth(.17,.00,z)*(1-sculpt.smooth(.32,.51,-z)))
                amount=.018*below+.010*band
            elif -.26<z<.13 and r>.39 and "Diagonal blanca principal" not in name:
                # Keep the outward face of each fold above the under-sculpt.
                # Station translation leaves the edge thickness unchanged.
                ceiling=.597+.070*abs(radial.x)**1.5
                outer=max(point.dot(radial) for point in section)-amount
                lift=float(sculpt.smooth(.135,.016,z)*(1-sculpt.smooth(.145,.270,-z)))
                amount-=min(.021,max(0,ceiling-outer))*lift

        else:
            amount=0
        rings.append([point-radial*amount for point in section])
    control_sections[tile]=(name,rings,list(mapping),sides)
    return original_closed_mesh(name,rings,mapping,sides,tile,collection,material,level)


def atlas(recipe, size, detail_size):
    y,x=np.mgrid[:size,:size].astype(np.float32)
    xx=(x+.5)/size*GRID
    yy=(y+.5)/size*GRID
    cell=xx.astype(np.int16)+GRID*yy.astype(np.int16)
    u=np.clip((xx%1-PADDING)/(1-2*PADDING),0,1)
    v=np.clip((yy%1-PADDING)/(1-2*PADDING),0,1)
    accents=np.zeros(GRID**2,dtype=np.uint8)
    accents[:len(recipe)]=[part[3] for part in recipe]
    slot=accents[cell]
    a=u*math.tau
    lobe=.5+.5*np.cos(a)
    wave=a+.052*np.sin(v*5.7+cell*.77)+.021*np.sin(v*14-cell*.27)
    group=.58*np.cos(wave*9+cell*.39)+.23*np.sin(wave*15-cell*.81)
    fine=.57*np.sin(wave*22+cell)+.29*np.cos(wave*38-v*2)+.14*np.sin(wave*53+v*4)
    strand=.55*np.sin(wave*67+cell*.78)+.45*np.sin(wave*94-v*7)
    glossy=.5+.5*np.cos(wave*4+cell*.29)
    pearl=np.clip(.23+.61*lobe+.19*glossy+.12*group+.11*fine+.038*strand,0,1)
    white=np.array([245,248,255],dtype=np.float32)
    silver=np.array([209,217,235],dtype=np.float32)
    graphite=np.array([17,24,39],dtype=np.float32)
    darkness=np.array([2,3,8],dtype=np.float32)
    base=silver+(white-silver)*pearl[:,:,None]
    root=1-sculpt.smooth(.035,.42,v)
    reverse=1-sculpt.smooth(.10,.55,lobe)
    occlusion=np.clip(root*.75+reverse*.76+(slot==2)*(.24+.17*reverse)+.045*np.maximum(0,-group),0,.985)
    base=base+(graphite-base)*occlusion[:,:,None]
    edge=np.exp(-((lobe-.31)/.081)**2)*sculpt.smooth(.20,.48,v)*(.61+.19*glossy)
    base=base+(darkness-base)*edge[:,:,None]
    blue=np.array([0,71,255],dtype=np.float32)
    cyan=np.array([0,217,255],dtype=np.float32)
    electric=(slot==1)*sculpt.smooth(.53,.84,v)*np.exp(-((lobe-.49)/.115)**2)*(.13+.30*glossy)
    accent=blue+(cyan-blue)*(.14*sculpt.smooth(.73,1,v))[:,:,None]
    base=base+(accent-base)*electric[:,:,None]
    scalp=cell==len(recipe)
    ribs=.5+.5*np.cos(a*14+.45*np.sin(a*4)+.14*np.sin(v*6))
    scalp_color=np.clip(.43+.47*ribs**.69+.079*group+.056*fine+.038*strand-.145*root,0,1)
    base[scalp]=(graphite+(white-graphite)*scalp_color[:,:,None])[scalp]
    rough=np.clip(.50+.085*reverse+.055*root+.032*group+.029*fine,.42,.73)
    height=np.clip(.50+.098*group+.151*fine+.079*strand,0,1)
    albedo=np.rint(base).astype(np.uint8)
    arrays={"Color":albedo,"Rugosidad":np.rint(rough*255).astype(np.uint8),
            "Altura_MASTER":np.rint(height*255).astype(np.uint8)}
    for key,data in arrays.items():
        if key=="Rugosidad":
            factor=size//detail_size
            data=np.rint(data.reshape(detail_size,factor,detail_size,factor).mean(axis=(1,3))).astype(np.uint8)
        sculpt.png(ASSET/"texturas"/f"{STEM}_{key}.png",data)
    return height


def material(master=False, maps=True):
    mat=bpy.data.materials.new(f"{STEM} · {'MASTER' if master else 'UGC'}")
    mat.diffuse_color=(.83,.87,.96,1)
    mat.use_backface_culling=True
    tree=mat.node_tree
    bsdf=tree.nodes["Principled BSDF"]
    bsdf.inputs["Roughness"].default_value=.56
    bsdf.inputs["Metallic"].default_value=0
    if master:
        bsdf.inputs["Specular IOR Level"].default_value=.26
        bsdf.inputs["Anisotropic"].default_value=.35
        bsdf.inputs["Anisotropic Rotation"].default_value=.25
        bsdf.inputs["Sheen Weight"].default_value=.14
        tangent=tree.nodes.new("ShaderNodeTangent")
        tangent.direction_type="UV_MAP"
        tangent.uv_map="Flujo de fibras"
        tree.links.new(tangent.outputs[0],bsdf.inputs["Tangent"])
    if not maps:
        return mat
    items=[("Color",bsdf.inputs["Base Color"],"sRGB"),("Rugosidad",bsdf.inputs["Roughness"],"Non-Color")]
    if master:
        normal=tree.nodes.new("ShaderNodeBump")
        normal.inputs["Strength"].default_value=.22
        normal.inputs["Distance"].default_value=.005
        items.append(("Altura_MASTER",normal.inputs["Height"],"Non-Color"))
    else:
        normal=tree.nodes.new("ShaderNodeNormalMap")
        normal.uv_map="Flujo de fibras"
        items.append(("Normal",normal.inputs["Color"],"Non-Color"))
    tree.links.new(normal.outputs["Normal"],bsdf.inputs["Normal"])
    normal.location=(-300,-190)
    for i,(key,target,color) in enumerate(items):
        tex=tree.nodes.new("ShaderNodeTexImage")
        tex.location=(-650,245-300*i)
        tex.label=key
        tex.image=bpy.data.images.load(str(ASSET/"texturas"/f"{STEM}_{key}.png"))
        tex.image.colorspace_settings.name=color
        tex.image.pack()
        tree.links.new(tex.outputs["Color"],target)
    return mat


def select(objects):
    bpy.ops.object.select_all(action="DESELECT")
    for obj in objects:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]


def joined(objects,name):
    select(objects)
    bpy.ops.object.join()
    obj=bpy.context.object
    obj.name=name
    return obj


def resample_row(row,sides):
    # The center line and the profile are fitted independently. Circumferential
    # samples retain the atlas registration across evaluated and retopologized meshes.
    count=len(row)
    smoothed=[row[i]*.79+(row[i-1]+row[(i+1)%count])*.105 for i in range(count)]
    result=[]
    for j in range(sides):
        i=j*count/sides
        k=int(i)
        result.append(smoothed[k].lerp(smoothed[(k+1)%count],i-k))
    return result


def simplify_tile(data,tile,zone,collection,mat):
    name, rings, mapping, _ = data
    if zone=="Base":
        n,sides=9,27
    elif tile in (0,1,3,4,5,6,8,9,10,12,13,16,20,23,26,39):
        n,sides=7,8
    else:
        n,sides=6,6
    centers=[sum(row,Vector((0,0,0)))/len(row) for row in rings]
    if zone=="Base":
        ts=[0,1,3,5,6,7,8,10,12]
    else:
        measure=[0.]
        for i in range(1,len(rings)):
            before=centers[i]-centers[i-1]
            between=centers[min(i+1,len(rings)-1)]-centers[i]
            bend=before.angle(between,0) if i<len(rings)-1 else 0
            z=centers[i].z
            rim=.031*math.exp(-((z+.163)/.079)**2)
            measure.append(measure[-1]+before.length+.068*bend+rim)
        # Keep profile definition at the final bend and at the tip.
        ts=np.interp(np.linspace(0,measure[-1],n),measure,np.arange(len(rings)))
    positions=[]
    for at in ts:
        i=int(at)
        last=len(rings)-1
        f=at-i
        if zone=="Base":
            row=rings[i]
        elif at<=.001 or at>=last-.001:
            row=rings[i]
        else:
            # Regular Catmull-Clark limits lie on a uniform cubic B-spline
            # through the neighboring cage rings. Preserve the authored tips.
            w0=(1-f)**3/6
            w1=(3*f**3-6*f*f+4)/6
            w2=(-3*f**3+3*f*f+3*f+1)/6
            w3=f**3/6
            row=[a*w0+b*w1+c*w2+d*w3 for a,b,c,d in
                 zip(rings[max(0,i-1)],rings[i],rings[min(i+1,last)],rings[min(i+2,last)])]
        positions.append(resample_row(row,sides))
    if zone=="Base":
        # A small allowance compensates the chord error at the fitted rim.
        for row in positions[2:7]:
            for point in row:
                point.x*=1.006
                point.y*=1.006
    uv=[float(np.interp(at,np.arange(len(mapping)),mapping)) for at in ts]
    obj=original_closed_mesh(name,positions,uv,sides,tile,collection,mat,0)
    for modifier in list(obj.modifiers):
        obj.modifiers.remove(modifier)
    return obj


def triangles(obj):
    modifier=obj.modifiers.new("Explicit triangles and smooth loops","TRIANGULATE")
    modifier.quad_method="FIXED"
    modifier.keep_custom_normals=True
    select([obj])
    bpy.ops.object.modifier_apply(modifier=modifier.name)


def duplicate_for_bake(source,location,evaluated):
    data=bpy.data.meshes.new_from_object(source.evaluated_get(bpy.context.evaluated_depsgraph_get())) if evaluated else source.data.copy()
    copy=bpy.data.objects.new("Baking "+source.name,data)
    bpy.context.scene.collection.objects.link(copy)
    copy.location=location
    copy.data.materials.clear()
    return copy


def bake(high, low, height):
    src=[]
    dst=[]
    for tile,a,b in zip(low.keys(),[high[i] for i in low],low.values()):
        offset=Vector((3.8*(tile%GRID),3.8*(tile//GRID),0))
        src.append(duplicate_for_bake(a,offset,True))
        dst.append(duplicate_for_bake(b,offset,False))
    source=joined(src,"Isolated V4 sculpt surfaces")
    target=joined(dst,"Isolated V4 retopology")
    triangles(target)
    mat=bpy.data.materials.new("Bake target")
    image=bpy.data.images.new("V4 tangent bake 1024",1024,1024,alpha=True)
    image.colorspace_settings.name="Non-Color"
    tex=mat.node_tree.nodes.new("ShaderNodeTexImage")
    tex.image=image
    mat.node_tree.nodes.active=tex
    target.data.materials.append(mat)
    scene=bpy.context.scene
    scene.render.engine="CYCLES"
    scene.cycles.device="CPU"
    scene.cycles.samples=4
    select([target,source])
    bpy.ops.object.bake(type="NORMAL",normal_space="TANGENT",use_selected_to_active=True,max_ray_distance=.157,
        cage_extrusion=.051,margin=7,margin_type="EXTEND",normal_r="POS_X",normal_g="POS_Y",normal_b="POS_Z")
    pixels=np.fromiter(image.pixels[:],dtype=np.float32).reshape(256,4,256,4,4)
    xyz=pixels[:,:,:,:,:3]*2-1
    weight=((pixels[:,:,:,:,3]>.2)&(xyz[:,:,:,:,2]>.03))[:,:,:,:,None]
    valid=weight.sum(axis=(1,3))
    mean=(xyz*weight).sum(axis=(1,3))/np.maximum(1,valid)
    mean[valid[:,:,0]==0]=(0,0,1)
    mean[:,:,:2]*=.55
    mean[:,:,2]=np.maximum(.60,mean[:,:,2])
    # Add fine, UV-oriented detail as derivatives. Height never connects to an
    # exported normal socket, only these normalized tangent-space RGB vectors.
    reduced=height.reshape(256,4,256,4).mean(axis=(1,3))
    dv,du=np.gradient(reduced)
    mean[:,:,0]-=np.clip(du*.53,-.18,.18)
    mean[:,:,1]-=np.clip(dv*.53,-.18,.18)
    mean/=np.maximum(.001,np.linalg.norm(mean,axis=2,keepdims=True))
    vectors=np.rint((mean*.5+.5)*255).astype(np.uint8)
    assert np.count_nonzero(valid)>25000 and np.median(vectors[:,:,2])>200
    sculpt.png(ASSET/"texturas"/f"{STEM}_Normal.png",vectors)
    bpy.data.objects.remove(source,do_unlink=True)
    bpy.data.objects.remove(target,do_unlink=True)
    return {"rays_valid_downsample_pixels":int(np.count_nonzero(valid)),
            "size":256,"space":"MikkTSpace/OpenGL Y+","median_blue":int(np.median(vectors[:,:,2])),
            "method":"Cycles selected-to-active, isolated surfaces; filtered and blended with longitudinal detail"}


def source_objects():
    recipe=refine_recipe()
    control_sections.clear()
    parts=bpy.data.collections.new("Celestial Hair V4 · MASTER")
    bpy.context.scene.collection.children.link(parts)
    zones={}
    for kind in sorted({spec[1] for spec in recipe}|{"Base"}):
        zone=bpy.data.collections.new("V4 · "+kind)
        parts.children.link(zone)
        zones[kind]=zone
    mat=material(master=True)
    sculpt.closed_mesh=inset_control
    try:
        objects={i:sculpt.cage(spec,i,zones[spec[1]],mat) for i,spec in enumerate(recipe)}
        objects[len(recipe)]=sculpt.scalp("C",len(recipe),zones["Base"],mat)
    finally:
        sculpt.closed_mesh=original_closed_mesh
    return objects,parts,recipe


def low_objects(recipe):
    layer=bpy.data.collections.new("Celestial Hair V4 · UGC")
    bpy.context.scene.collection.children.link(layer)
    blank=material(maps=False)
    # Tuck away several overlapping internal crown locks in the game mesh.
    omit={27,28,30,32,34,35}
    zones=[spec[1] for spec in recipe]+["Base"]
    result={i:simplify_tile(control_sections[i],i,zones[i],layer,blank)
            for i in range(len(zones)) if i not in omit}
    return result,layer


def fit(objects):
    bpy.context.view_layer.update()
    return sculpt.fit(list(objects.values()) if isinstance(objects,dict) else objects)


def export(obj):
    select([obj])
    folder=ASSET/"exportaciones"
    root=folder/(STEM+"_UGC")
    bpy.ops.export_scene.gltf(filepath=str(root.with_suffix(".glb")),export_format="GLB",use_selection=True,
        export_apply=True,export_animations=False,export_tangents=True,export_yup=True)
    bpy.ops.export_scene.fbx(filepath=str(root.with_suffix(".fbx")),use_selection=True,
        object_types={"MESH"},apply_scale_options="FBX_SCALE_UNITS",axis_forward="-Z",axis_up="Y",
        bake_space_transform=True,path_mode="COPY",embed_textures=True,bake_anim=False,use_tspace=True)


def hide(objects, hidden):
    for obj in objects:
        obj.hide_set(hidden)
        obj.hide_render=hidden


def save_master(objects, variant, folder):
    scene=bpy.context.scene
    scene["Referencia"]="V3 C · Concepto ZAREK"
    scene["Unidades"]="1 unidad Blender = 1 stud. Frente -Y."
    select([objects[0]])
    bpy.ops.wm.save_as_mainfile(filepath=str(folder/f"{STEM}_{variant}.blend"),compress=True)


def views(quick, high, low, stage, folder):
    for view,rot,scale,center in [
        ("frente",(0,-6,.05),2.31,(0,0,-.41)),
        ("espalda",(0,6,.72),2.33,(0,.08,-.43)),
        ("perfil",(6,0,.44),2.33,(0,0,-.45)),
        ("perspectiva",(3.5,-5.5,.96),2.36,(0,0,-.41)),
    ]:
        if quick and view=="perfil":
            continue
        sculpt.render(stage, "V4_"+view,rot,center,scale,folder,quick)


def run(mode):
    bpy.ops.wm.open_mainfile(filepath=str(sculpt.ASSEMBLY))
    bpy.context.preferences.filepaths.save_version=0
    height=atlas(refine_recipe(),1024,256)
    high,master_layer,recipe=source_objects()
    low,ugc_layer=low_objects(recipe)
    results={"MASTER":fit(high),"UGC":fit(low)}
    print("V4_FIT",json.dumps(results,ensure_ascii=False),flush=True)
    if mode=="measure":
        return
    if mode=="final":
        assert results["UGC"]["evaluated_triangles"]<=4000,results["UGC"]
        for tag,measure in results.items():
            assert not measure["crown_triangle_pairs"] and not measure["halo_triangle_pairs"],(tag,measure)
        results["normal"]=bake(high,low,height)
    obj=joined(list(low.values()),STEM+"_UGC")
    triangles(obj)
    obj.data.materials.clear()
    obj.data.materials.append(material(master=mode=="preview"))
    folder=WORK if mode=="preview" else ASSET/"renders"
    scene,gpu=sculpt.stage()
    results["gpu"]=gpu
    rendered=mode=="final" or mode=="preview"
    if mode=="final":
        export(obj)
        (ASSET/"validacion"/"ajuste.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf8")
        hide([obj],True)
        hide([bpy.data.objects[n] for n in sculpt.ACCESSORIES],True)
        sculpt.render(scene,"V4_MASTER",(3.5,-5.5,.87),(0,0,-.41),2.36,folder,False,keep=True)
        save_master(list(high.values()),"MASTER",ASSET/"blender")
        sculpt.render(scene,"V4_MASTER",(3.5,-5.5,.87),(0,0,-.41),2.36,folder,False)
        hide(high.values(),True)
        hide([obj],False)
        save_master([obj],"UGC",ASSET/"blender")
    if rendered:
        hide(high.values(),True)
        hide([bpy.data.objects[n] for n in sculpt.ACCESSORIES],True)
        hide([obj],False)
        views(mode=="preview",high,obj,scene,folder)
    if mode!="final":
        return
    hide([bpy.data.objects[n] for n in sculpt.ACCESSORIES],False)
    sculpt.render(scene,"V4_conjunto_neutro",(0,-6.2,.49),(0,0,.057),3.18,folder,False)
    scene.world.node_tree.nodes.get("Background").inputs[1].default_value=.19
    bpy.data.lights["Silver edge"].color=(.27,.52,1.0)
    bpy.data.lights["Silver edge"].energy=590
    sculpt.render(scene,"V4_conjunto_cine",(2.6,-6.1,1.15),(0,0,.05),3.14,folder,False)
    hide([obj],True)
    with bpy.data.libraries.load(str(SOURCE),link=False) as (source,target):
        target.collections=[n for n in source.collections if n.startswith("MASTER V3 C ")]
    scene.collection.children.link(target.collections[0])
    hide(target.collections[0].all_objects,False)
    bpy.data.lights["Silver edge"].color=(.61,.75,1)
    bpy.data.lights["Silver edge"].energy=435
    scene.world.node_tree.nodes.get("Background").inputs[1].default_value=.29
    hide([bpy.data.objects[n] for n in sculpt.ACCESSORIES],True)
    for name,rot,center,scale in [
        ("frente",(0,-6,.05),(0,0,-.41),2.31),
        ("espalda",(0,6,.72),(0,.08,-.43),2.33),
        ("perspectiva",(3.5,-5.5,.96),(0,0,-.41),2.36)
    ]:
        sculpt.render(scene,"V3C_"+name,rot,center,scale,folder,False)
    (ASSET/"validacion"/"ajuste.json").write_text(json.dumps(results,indent=2,ensure_ascii=False)+"\n",encoding="utf8")


if __name__=="__main__":
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode",choices=("measure","preview","final"))
    run(ap.parse_args(sys.argv[sys.argv.index("--")+1:]).mode)
