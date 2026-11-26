"""Build, fit, preview and render the three editable V3 hair sculpts in Blender."""
from pathlib import Path
import argparse
import json
import math
import struct
import sys
import zlib

import bpy
import bmesh
import numpy as np
from mathutils import Vector
from mathutils.bvhtree import BVHTree

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from diseno import DESIGNS

ASSET = HERE.parent
HAIR = ASSET.parent
ASSEMBLY = HAIR.parent / "02-eternal-halo/blender/EternalHalo_R15_DivineCrown.blend"
SCRATCH = HAIR / "work/v3"
ACCESSORIES = ("DivineCrown_UGC", "EternalHalo_UGC")
GRID = 7
PADDING = .042
SIDES = 12


def png(path, array):
    height, width = array.shape[:2]
    kind = 2 if array.ndim == 3 else 0

    def chunk(name, data):
        return struct.pack(">I", len(data)) + name + data + struct.pack(">I", zlib.crc32(name+data))

    payload = b"".join(b"\0"+row.tobytes() for row in array[::-1])
    header = struct.pack(">IIBBBBB", width, height, 8, kind, 0, 0, 0)
    path.write_bytes(b"\x89PNG\r\n\x1a\n"+chunk(b"IHDR",header)+chunk(b"IDAT",zlib.compress(payload,7))+chunk(b"IEND",b""))


def smooth(a, b, t):
    t = np.clip((t-a)/(b-a), 0, 1)
    return t*t*(3-2*t)


def atlas(code, recipe, size):
    # Packed fibers follow every control cage around the circumference and down the length.
    y, x = np.mgrid[:size,:size].astype(np.float32)
    x = (x+.5)/size*GRID
    y = (y+.5)/size*GRID
    cell = x.astype(np.int16)+GRID*y.astype(np.int16)
    u = np.clip((x%1-PADDING)/(1-2*PADDING),0,1)
    v = np.clip((y%1-PADDING)/(1-2*PADDING),0,1)
    kind = np.zeros(GRID*GRID, dtype=np.uint8)
    kind[:len(recipe)] = [part[3] for part in recipe]
    strand = kind[cell]
    angle = u*math.tau
    face = .5+.5*np.cos(angle)
    root = 1-smooth(.040, .53 if code=="B" else .30, v)
    side = 1-smooth(.13,.67,face)
    path = angle+.035*np.sin(v*5.3+cell*.79)+.018*np.sin(v*13+cell*.22)
    broad = np.sin(path*8 + cell*.31)
    comb = .53*np.sin(path*23+cell*.47)+.33*np.sin(path*41-cell*.73)+.14*np.sin(path*57+v*3)
    micro = .57*np.sin(path*71+v*2.4+cell)+.43*np.sin(path*95-v*4)
    crystalline = .5+.5*np.cos(path*4+cell*.61)
    glow = smooth(.035,.64,face)*(.26+.61*crystalline)
    pale = np.clip(.36+.39*glow+.106*broad+.102*comb+.051*micro,0,1)
    silver = np.array([193,207,231],dtype=np.float32)
    snow = np.array([254,255,255],dtype=np.float32)
    pigment = silver+(snow-silver)*pale[:,:,None]
    shade = np.array([19,28,52],dtype=np.float32)
    color_shadow = np.array([6,11,24],dtype=np.float32)
    black_contrast = .91 if code=="B" else .60
    blend = np.clip(root*.86+side*black_contrast+root*side*.17+(strand==2)*((.59 if code=="B" else .24)+.22*side+(.12 if code=="B" else 0)*broad),0,.96)
    pigment = pigment*(1-blend[:,:,None])+shade*blend[:,:,None]
    carbon = np.exp(-((face-.125)/.060)**2)*smooth(.09,.37,v)*(.40 if code=="A" else .58)
    pigment = pigment*(1-carbon[:,:,None])+color_shadow*carbon[:,:,None]
    blue = np.array([26,102,246],dtype=np.float32)
    accents = (strand==1)*smooth(.45,.80,v)*smooth(.30,.13,abs(face-.55))*(.19+.29*crystalline)
    pigment = pigment*(1-accents[:,:,None])+blue*accents[:,:,None]
    scalp = cell==len(recipe)
    canopies = .5+.5*np.cos(angle*14 + .43*np.sin(angle*4)+.13*np.sin(v*6))
    darker = .17 if code=="B" else .075
    scalp_light = np.clip(.68+.24*canopies+.075*broad+.059*comb+.032*micro-darker,0,1)
    base = np.array([46,59,88],dtype=np.float32)
    veil = np.array([241,247,255],dtype=np.float32)
    pigment[scalp] = (base+(veil-base)*scalp_light[:,:,None])[scalp]
    rough = np.clip(.435+.105*side+.057*root+.045*broad+.027*comb,.36,.70)
    height = np.clip(.5+.060*broad+.13*comb+.040*micro,0,1)
    prefix = ASSET/"texturas"/f"{code}_"
    png(Path(str(prefix)+"Color.png"),np.rint(np.clip(pigment,0,255)).astype(np.uint8))
    png(Path(str(prefix)+"Rugosidad.png"),np.rint(255*rough).astype(np.uint8))
    png(Path(str(prefix)+"Fibra.png"),np.rint(255*height).astype(np.uint8))


def coord(tile, u, v):
    return ((tile%GRID+PADDING+(1-2*PADDING)*u)/GRID,
            (tile//GRID+PADDING+(1-2*PADDING)*v)/GRID)


def closed_mesh(name, positions, mapping, sides, tile, collection, material, level):
    vertices = [point for ring in positions for point in ring]
    vertices.extend([sum(ring,Vector((0,0,0)))/sides for ring in (positions[0],positions[-1])])
    cap1, cap2 = len(vertices)-2,len(vertices)-1
    rows = len(positions)
    faces, coordinates = [], []
    for j in range(sides):
        next_j = (j+1)%sides
        u0, u1 = j/sides, (j+1)/sides
        faces.append((cap1,next_j,j))
        coordinates.append([((u0+u1)*.5,0),(u1,mapping[0]),(u0,mapping[0])])
        for i in range(rows-1):
            q,r = i*sides,(i+1)*sides
            faces.append((q+j,q+next_j,r+next_j,r+j))
            coordinates.append([(u0,mapping[i]),(u1,mapping[i]),(u1,mapping[i+1]),(u0,mapping[i+1])])
        end = (rows-1)*sides
        faces.append((cap2,end+j,end+next_j))
        coordinates.append([((u0+u1)*.5,1),(u0,mapping[-1]),(u1,mapping[-1])])
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices,[],faces)
    mesh.update()
    uv = mesh.uv_layers.new(name="Flujo de fibras")
    for polygon, values in zip(mesh.polygons,coordinates):
        polygon.use_smooth=True
        for i,(u,v) in zip(polygon.loop_indices,values):
            uv.data[i].uv = coord(tile,u,v)

    mesh.calc_loop_triangles()
    volume = sum(vertices[a].dot(vertices[b].cross(vertices[c]))
                 for tri in mesh.loop_triangles for a,b,c in [tri.vertices])
    if volume<0:
        bm=bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.reverse_faces(bm,faces=bm.faces)
        bm.to_mesh(mesh)
        bm.free()
    obj = bpy.data.objects.new(name,mesh)
    collection.objects.link(obj)
    mesh.materials.append(material)
    sub = obj.modifiers.new("Escultura · Catmull Clark","SUBSURF")
    sub.levels = sub.render_levels = level
    sub.uv_smooth = "PRESERVE_BOUNDARIES"
    return obj


def cage(spec, tile, collection, material):
    name, zone, knots, accent, roll = spec
    stations = []
    for i, knot in enumerate(knots):
        if i:
            before=knots[i-1]
            for height in (.08,-.074,-.181,-.238):
                if before[2]>height>knot[2] and min(before[2]-height,height-knot[2])>.009:
                    fraction=(height-before[2])/(knot[2]-before[2])
                    stations.append(tuple(a+(b-a)*fraction for a,b in zip(before,knot)))
        stations.append(knot)
    centers = [Vector(a[:3]) for a in stations]
    widths = [(p[3],p[4]) for p in stations]
    # A second small ring holds the point through subdivision without a crease.
    tip = centers[-1]
    centers.insert(-1, tip.lerp(centers[-2],.21))
    widths.insert(-1,(widths[-2][0]*.27,widths[-2][1]*.31))
    gaps = [(b-a).length for a,b in zip(centers,centers[1:])]
    length = sum(gaps)
    distance = 0
    previous = None
    rings, mapping = [], []
    for i, position in enumerate(centers):
        t = min(1.0, distance/length)
        mapping.append(.013+.975*t)
        if i<len(gaps):
            distance += gaps[i]
        tangent=(centers[min(i+1,len(centers)-1)]-centers[max(0,i-1)]).normalized()
        radial=Vector((position.x,position.y,(position.z+.36)*.88))
        side=tangent.cross(radial)
        if side.length<.00001:
            side=tangent.cross(Vector((0,1,0)))
        side.normalize()
        if previous is not None and side.dot(previous)<0:
            side.negate()
        previous=side.copy()
        outward=side.cross(tangent).normalized()
        angle=roll*(2*t-1)*.56+.104*math.sin(t*math.tau+tile*.72)
        axes=side*math.cos(angle)+outward*math.sin(angle),outward*math.cos(angle)-side*math.sin(angle)
        width,depth=widths[i]
        ring=[]
        for j in range(SIDES):
            bearing=j*math.tau/SIDES
            outer=math.cos(bearing)
            s=math.sin(bearing)
            shoulder=1+.13*outer+.10*s*math.sin(t*math.pi+tile*.49)
            lobes=1+(.07*math.sin(bearing*3+t*3+tile)+.057*math.cos(bearing*5-t))*math.sin(t*math.pi)**.7
            ring.append(position+axes[0]*(s*width*shoulder)+axes[1]*(outer*depth*lobes+.10*s*depth))
        # At the root-to-silhouette transition, position the full oval under the
        # crown instead of flattening it. Positive travel keeps the outer lid layered.
        radial2=Vector((position.x,position.y,0))
        if radial2.length>.34 and -.43<position.z<.16 and i not in (0,len(centers)-1):
            radial2.normalize()
            x,y=radial2.x,radial2.y
            opening=(x*x/.710**2+y*y/.624**2)**-.5
            opening+=.024*float(smooth(.07,.18,position.z))
            opening+=.087*float(smooth(-.175,-.410,position.z))
            outermost=max(point.dot(radial2) for point in ring)
            guide=float(smooth(.17,.035,position.z)*(1-smooth(.14,.35,-position.z)))
            leave=.013+.007*((tile%4)/3)
            if name in {"B · Diagonal de tormenta","C · Diagonal blanca principal"}:
                leave+=.031
            move=(opening-leave-outermost)*guide
            if move>0:
                move*=.91
            ring=[point+radial2*move for point in ring]
        rings.append(ring)
    obj = closed_mesh(name,rings,mapping,SIDES,tile,collection,material,2)
    obj["Sistema"] = zone
    obj["Perfil"] = "Volumen cerrado, perfil oval asimétrico y jaula editable"
    return obj


def scalp(code, tile, collection, material):
    # Continuous underpainting over the dome with a scalloped, receding frontal hairline.
    rings=[]
    points=56
    for i,(r,h) in enumerate([
        (.085,.280),(.218,.269),(.353,.221),(.471,.133),(.546,.047),(.572,-.039),
        (.594,-.133),(.594,-.247),(.593,-.401),(.606,-.610),(.595,-.820),(.563,-.930),(.477,-.915),
    ]):
        ring=[]
        for j in range(points):
            theta=j*math.tau/points
            a=theta+(.13 if code=="A" else -.19 if code=="B" else .21)*math.sin(i*math.pi/13)*math.sin(theta+.9)
            front=math.cos(a)
            front_edge=max(0,front)**1.5
            weight=max(0,(i-7)/5)**1.1
            scallop=.027*math.cos(theta*9+.67)+.022*math.sin(theta*13+.23)
            terminal=-.917+.545*front_edge+scallop
            if i>=8:
                z=-.314+(.98 if i==12 else (i-8)/3.1)*(terminal+.314)
                if i==12:
                    z+=.024
            else:
                z=h+weight*(.49*front_edge+scallop)
            band=float(smooth(.17,.56,r))
            ridge=.5+.5*math.cos(theta*14+.43*math.sin(theta*4))
            flare=(.012*(ridge-.50)+.008*math.cos(theta*9+.31))*band
            if h<-.4:
                flare+=.013*(ridge-.34)*float(smooth(.4,.90,abs(h)))
            if code=="B":
                z-=.016*max(0,-front)*weight
            ring.append(Vector(((r+flare+.006)*math.sin(a),-(r+flare)*math.cos(a),z)))
        rings.append(ring)
    return closed_mesh("Base continua · coronilla y nuca",rings,
                       np.linspace(.025,.97,len(rings)),points,tile,collection,material,1)


def look_material(code):
    material=bpy.data.materials.new(f"Celestial Hair {code} · seda pigmentada")
    shader=material.node_tree.nodes.get("Principled BSDF")
    shader.inputs["IOR"].default_value=1.46
    shader.inputs["Specular IOR Level"].default_value=.27
    shader.inputs["Anisotropic"].default_value=.43
    shader.inputs["Anisotropic Rotation"].default_value=.25
    shader.inputs["Sheen Weight"].default_value=.21
    shader.inputs["Sheen Roughness"].default_value=.53
    shader.inputs["Sheen Tint"].default_value=(.76,.84,1,1)
    node_tree=material.node_tree
    tangent=node_tree.nodes.new("ShaderNodeTangent")
    tangent.direction_type="UV_MAP"
    tangent.uv_map="Flujo de fibras"
    tangent.location=(-370,-520)
    node_tree.links.new(tangent.outputs["Tangent"],shader.inputs["Tangent"])
    bump=node_tree.nodes.new("ShaderNodeBump")
    bump.inputs["Strength"].default_value=.29
    bump.inputs["Distance"].default_value=.0075
    bump.location=(-330,-260)
    node_tree.links.new(bump.outputs["Normal"],shader.inputs["Normal"])
    for i,(label,target,space) in enumerate([
        ("Color",shader.inputs["Base Color"],"sRGB"),
        ("Rugosidad",shader.inputs["Roughness"],"Non-Color"),
        ("Fibra",bump.inputs["Height"],"Non-Color"),
    ]):
        image=bpy.data.images.load(str(ASSET/"texturas"/f"{code}_{label}.png"))
        image.colorspace_settings.name=space
        image.pack()
        node=node_tree.nodes.new("ShaderNodeTexImage")
        node.image=image
        node.label=label
        node.location=(-770,280-330*i)
        node_tree.links.new(node.outputs["Color"],target)
    material.diffuse_color=(.84,.91,1,1)
    return material


def mesh_bvh(objects):
    vertices, tris = [], []
    dg=bpy.context.evaluated_depsgraph_get()
    for object_ in objects:
        evaluated=object_.evaluated_get(dg)
        mesh=evaluated.to_mesh()
        mesh.calc_loop_triangles()
        start=len(vertices)
        vertices.extend(evaluated.matrix_world@v.co for v in mesh.vertices)
        tris.extend(tuple(start+v for v in t.vertices) for t in mesh.loop_triangles)
        evaluated.to_mesh_clear()
    return vertices,tris,BVHTree.FromPolygons(vertices,tris,all_triangles=True)


def fit(parts):
    bv=bpy.data.objects
    crown=mesh_bvh([bv[ACCESSORIES[0]]])[2]
    halo=mesh_bvh([bv[ACCESSORIES[1]]])[2]
    head=mesh_bvh([bv["Head_Geo"]])[2]
    measures={}
    for part in parts:
        points, faces, tree = mesh_bvh([part])
        overlaps = tree.overlap(crown)
        pairs=[len(overlaps),len(tree.overlap(halo))]
        if any(pairs):
            crossing=[points[v] for face,_ in overlaps for v in faces[face]]
            measures[part.name]={"pairs":pairs,"z": [round(fn(v.z for v in crossing),4) for fn in (min,max)] if crossing else []}
    vertices,tris,hair=mesh_bvh(parts)
    eyes=[]
    for a,b in ((-.36,-.14),(.14,.36)):
        total=0
        for x in np.linspace(a,b,16):
            for z in np.linspace(-.705,-.575,11):
                origin=(float(x),-2.,float(z))
                hit=head.ray_cast(origin,(0,1,0),3)[3]
                if hit is not None:
                    total+=hair.ray_cast(origin,(0,1,0),hit-.0004)[0] is not None
        eyes.append(total)
    uncovered=[]
    for z in (-.03,-.073,-.126,-.17,-.226,-.284):
        n=0
        for i in range(96):
            angle=i*math.tau/96
            direction=(math.sin(angle),math.cos(angle),0)
            origin=(-2*direction[0],-2*direction[1],z)
            hit=head.ray_cast(origin,direction,3)[3]
            if hit is not None:
                n+=hair.ray_cast(origin,direction,hit-.0003)[0] is None
        uncovered.append(n)
    return {
        "editable_objects":len(parts),"evaluated_triangles":len(tris),
        "bounds_xyz_blender":[[round(fn(v[i] for v in vertices),5) for i in range(3)] for fn in (min,max)],
        "crown_triangle_pairs":len(hair.overlap(crown)),"halo_triangle_pairs":len(hair.overlap(halo)),
        "details_crossings_crown_halo":measures,
        "crown_min_hair_vertex_distance_studs":round(min(crown.find_nearest(v)[3] for v in vertices),6),
        "halo_min_hair_vertex_distance_studs":round(min(halo.find_nearest(v)[3] for v in vertices),6),
        "scalp_uncovered_by_height_out_of_96":uncovered,"blocked_eye_samples_out_of_176_per_eye":eyes,
    }


def aim(object_, target):
    object_.rotation_euler=(Vector(target)-object_.location).to_track_quat("-Z","Y").to_euler()


def stage():
    scene=bpy.context.scene
    scene.compositing_node_group=None
    for obj in list(scene.objects):
        if obj.type in {"LIGHT","CAMERA"} or obj.name.startswith("STAGE -"):
            bpy.data.objects.remove(obj,do_unlink=True)
    for obj in scene.objects:
        if obj.name.endswith("_Geo"):
            obj.data=obj.data.copy()
            obj.data.materials.clear()
    clay=bpy.data.materials.new("Escena de revisión · arcilla gris cálida")
    shader=clay.node_tree.nodes["Principled BSDF"]
    shader.inputs["Base Color"].default_value=(.12,.107,.114,1)
    shader.inputs["Roughness"].default_value=.58
    for obj in scene.objects:
        if obj.name.endswith("_Geo"):
            obj.data.materials.append(clay)

    world=bpy.data.worlds.new("Sala de revisión")
    world.use_nodes=True
    tree=world.node_tree
    tree.nodes.clear()
    light = tree.nodes.new("ShaderNodeBackground")
    light.inputs[0].default_value=(.46,.50,.58,1)
    light.inputs[1].default_value=.29
    backdrop=tree.nodes.new("ShaderNodeBackground")
    backdrop.inputs[0].default_value=(.025,.038,.062,1)
    path=tree.nodes.new("ShaderNodeLightPath")
    mix=tree.nodes.new("ShaderNodeMixShader")
    output=tree.nodes.new("ShaderNodeOutputWorld")
    tree.links.new(path.outputs["Is Camera Ray"],mix.inputs[0])
    tree.links.new(light.outputs[0],mix.inputs[1])
    tree.links.new(backdrop.outputs[0],mix.inputs[2])
    tree.links.new(mix.outputs[0],output.inputs["Surface"])
    scene.world=world

    def softbox(name, place, energy, color, size):
        data=bpy.data.lights.new(name,"AREA")
        data.energy,data.color,data.shape,data.size=energy,color,"DISK",size
        obj=bpy.data.objects.new(name,data)
        scene.collection.objects.link(obj)
        obj.location=place
        aim(obj,(0,0,-.2))

    softbox("Portrait · key",(-3.4,-4.6,4.5),340,(1,.944,.90),4.0)
    softbox("Silver edge",(3.8,3.4,4.3),435,(.61,.75,1),3.7)
    softbox("Front bounce",(3.0,-4.2,.5),85,(.89,.94,1),3)
    softbox("Rear softbox",(-4.3,3.8,.65),225,(.95,.975,1),3.4)
    cam=bpy.data.objects.new("Camara de revisión",bpy.data.cameras.new("Retrato"))
    scene.collection.objects.link(cam)
    cam.data.type="ORTHO"
    scene.camera=cam

    scene.render.engine="CYCLES"
    prefs=bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type="OPTIX"
    prefs.get_devices()
    active=[]
    for device in prefs.devices:
        device.use=device.type=="OPTIX"
        if device.use:
            active.append(device.name)
    if not active:
        raise RuntimeError("No se encontró una GPU OptiX")
    scene.cycles.device="GPU"
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.025
    scene.cycles.use_denoising=True
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGB"
    scene.render.film_transparent=False
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="AgX - Medium High Contrast"
    scene.view_settings.exposure=.34
    return scene,active


def render(scene,name, direction, center, scale, folder, quick, keep=False):
    scene.cycles.samples=24 if quick else 64
    scene.render.resolution_x,scene.render.resolution_y=(800,790) if quick else (1400,1370)
    camera=scene.camera
    camera.location=Vector(center)+Vector(direction)
    camera.data.ortho_scale=scale
    aim(camera,center)
    scene.render.filepath=str(folder/(name+".png"))
    if not keep:
        bpy.ops.render.render(write_still=True)
        print("V3_RENDER",name,flush=True)


def export_probe(code, hair, output):
    # An evaluated full-resolution MASTER scene export for Studio's general 3D importer.
    # Nodes remain separate so each mesh is below the importer per-mesh budget.
    bpy.ops.object.select_all(action="DESELECT")
    for obj in hair:
        obj.select_set(True)
    bpy.context.view_layer.objects.active=hair[0]
    material=hair[0].data.materials[0]
    tree=material.node_tree
    shader=tree.nodes.get("Principled BSDF")
    # The Blender Bump texture is a scalar height map. There is no baked tangent
    # normal at the MASTER review stage, so export only color and roughness.
    bump_link=shader.inputs["Normal"].links[0]
    bump_output=bump_link.from_socket
    tree.links.remove(bump_link)
    try:
        bpy.ops.export_scene.gltf(filepath=str(output/f"V3_{code}_MASTER_Studio.glb"),export_format="GLB",
            use_selection=True,export_apply=True,export_animations=False,export_texcoords=True,
            export_normals=True,export_materials="EXPORT")
    finally:
        tree.links.new(bump_output,shader.inputs["Normal"])


def run(code, mode):
    label, recipe=DESIGNS[code]
    bpy.ops.wm.open_mainfile(filepath=str(ASSEMBLY))
    bpy.context.preferences.filepaths.save_version=0
    atlas(code,recipe,768 if mode in {"preview","measure"} else 1792)
    material=look_material(code)
    model=bpy.data.collections.new(f"MASTER V3 {code} · {label}")
    bpy.context.scene.collection.children.link(model)
    regions={}
    for name in sorted({spec[1] for spec in recipe}|{"Base"}):
        region=bpy.data.collections.new(f"V3 {code} · {name}")
        model.children.link(region)
        regions[name]=region
    parts=[cage(spec,i,regions[spec[1]],material) for i,spec in enumerate(recipe)]
    parts.append(scalp(code,len(recipe),regions["Base"],material))
    bpy.context.view_layer.update()
    measures=fit(parts)
    if mode=="measure":
        print("V3_FIT",code,json.dumps(measures,ensure_ascii=False),flush=True)
        return
    if mode=="final":
        if measures["crown_triangle_pairs"] or measures["halo_triangle_pairs"]:
            raise RuntimeError(f"Interferencia en {code}: {measures}")
        if any(measures["blocked_eye_samples_out_of_176_per_eye"]) or any(measures["scalp_uncovered_by_height_out_of_96"]):
            raise RuntimeError(f"Cobertura incorrecta en {code}: {measures}")
        export_probe(code,parts,SCRATCH)
    scene,device=stage()
    measures["renderer"]=device
    measures["plan"]=label
    print("V3_FIT",code,json.dumps(measures,ensure_ascii=False),flush=True)
    folder=SCRATCH if mode=="preview" else ASSET/"renders"
    include_kit=lambda on: [setattr(bpy.data.objects[item],"hide_render",not on) for item in ACCESSORIES]
    for item in ACCESSORIES:
        bpy.data.objects[item].hide_set(True)
    include_kit(False)
    render(scene,code+"_frente",(0,-6,.21),(0,0,-.39),2.30,folder,mode=="preview")
    render(scene,code+"_espalda",(0,6,.95),(0,.075,-.44),2.31,folder,mode=="preview")
    render(scene,code+"_perspectiva",(4.20,-5.75,1.46),(0,0,-.37),2.38,folder,mode=="preview")
    if mode=="preview":
        return
    include_kit(True)
    if code=="C":
        render(scene,"C_frente_equipado",(0,-6,.50),(0,0,.07),3.14,folder,False)
        render(scene,"C_espalda_equipado",(0,6,.65),(0,.03,.07),3.14,folder,False)
    render(scene,code+"_conjunto",(1.4,-6,1.02),(0,0,.08),3.17,folder,False)
    include_kit(False)
    render(scene,code+"_perspectiva",(4.20,-5.75,1.46),(0,0,-.37),2.38,folder,False,keep=True)
    scene.render.filepath=f"//../renders/{code}_perspectiva.png"
    bpy.ops.object.select_all(action="DESELECT")
    parts[0].select_set(True)
    bpy.context.view_layer.objects.active=parts[0]
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.region_3d.view_perspective="CAMERA"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET/"blender"/f"CelestialHair_V3_{code}_MASTER.blend"),compress=True)
    (ASSET/"validacion"/f"{code}_ajuste.json").write_text(json.dumps(measures,ensure_ascii=False,indent=2)+"\n",encoding="utf8")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("mode", choices=("preview","final","measure"))
    parser.add_argument("design", nargs="*", choices=("A","B","C"))
    args=parser.parse_args(sys.argv[sys.argv.index("--")+1:])
    for folder in (SCRATCH,ASSET/"texturas",ASSET/"renders",ASSET/"blender",ASSET/"validacion"):
        folder.mkdir(parents=True,exist_ok=True)
    for design in args.design or DESIGNS:
        run(design,args.mode)
