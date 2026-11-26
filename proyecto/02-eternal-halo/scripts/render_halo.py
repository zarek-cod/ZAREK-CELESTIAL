
"""Render saved meshes in Cycles on OptiX. No Roblox place is edited."""
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ASSET=Path(__file__).resolve().parents[1]
CROWN=ASSET.parent/"01-divine-crown/blender/DivineCrown_UGC_R15_fit.blend"
OUT=ASSET/"renders"
FRAMING={
    "front":(0,-6,.95), "back":(0,6,2.08), "left":(-6,0,1.05),
    "right":(6,0,1.05), "perspective":(3.2,-5,2.5),
}


def set_gpu(scene):
    scene.render.engine="CYCLES"
    prefs=bpy.context.preferences.addons["cycles"].preferences
    prefs.compute_device_type="OPTIX"
    prefs.get_devices()
    names=[]
    for device in prefs.devices:
        device.use=device.type=="OPTIX"
        if device.use:
            names.append(device.name)
    if not names:
        raise RuntimeError("No OptiX GPU detected")
    print("CYCLES_OPTIX_DEVICE",names,flush=True)
    scene.cycles.device="GPU"
    scene.cycles.samples=56
    scene.cycles.use_adaptive_sampling=True
    scene.cycles.adaptive_threshold=.028
    scene.cycles.use_denoising=True
    scene.render.image_settings.file_format="PNG"
    scene.render.image_settings.color_mode="RGB"
    scene.render.image_settings.color_depth="8"
    scene.render.film_transparent=False
    scene.render.resolution_percentage=100
    scene.view_settings.view_transform="AgX"
    scene.view_settings.look="None"
    scene.view_settings.exposure=0
    bpy.context.preferences.filepaths.save_version=0


def point_at(obj,target):
    obj.rotation_euler=(Vector(target)-obj.location).to_track_quat("-Z","Y").to_euler()


def light(name,xyz,power,color,size,target):
    data=bpy.data.lights.new(name,"AREA")
    data.energy=power
    data.color=color
    data.shape="DISK"
    data.size=size
    obj=bpy.data.objects.new(name,data)
    bpy.context.scene.collection.objects.link(obj)
    obj.location=xyz
    point_at(obj,target)


def stage(cinematic,full=False):
    scene=bpy.context.scene
    for obj in list(scene.objects):
        if obj.type in {"LIGHT","CAMERA"} or obj.name.startswith("STAGE -"):
            bpy.data.objects.remove(obj,do_unlink=True)
    world=bpy.data.worlds.new("Eternal Halo cinematic" if cinematic else "Eternal Halo neutral")
    world.use_nodes=True
    nt=world.node_tree
    nt.nodes.clear()
    env=nt.nodes.new("ShaderNodeBackground")
    env.inputs[0].default_value=(.26,.32,.45,1) if cinematic else (.52,.52,.52,1)
    env.inputs[1].default_value=.58 if cinematic else .7
    bg=nt.nodes.new("ShaderNodeBackground")
    tex=nt.nodes.new("ShaderNodeTexCoord")
    xyz=nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(tex.outputs["Normal"],xyz.inputs[0])
    rng=nt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value=-.65
    rng.inputs["From Max"].default_value=.58
    nt.links.new(xyz.outputs["Z"],rng.inputs[0])
    ramp=nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color=(.0008,.0014,.004,1) if cinematic else (.096,.116,.141,1)
    ramp.color_ramp.elements[1].color=(.003,.007,.023,1) if cinematic else (.225,.253,.291,1)
    nt.links.new(rng.outputs[0],ramp.inputs[0])
    nt.links.new(ramp.outputs[0],bg.inputs[0])
    mixer=nt.nodes.new("ShaderNodeMixShader")
    path=nt.nodes.new("ShaderNodeLightPath")
    nt.links.new(path.outputs["Is Camera Ray"],mixer.inputs[0])
    nt.links.new(env.outputs[0],mixer.inputs[1])
    nt.links.new(bg.outputs[0],mixer.inputs[2])
    out=nt.nodes.new("ShaderNodeOutputWorld")
    nt.links.new(mixer.outputs[0],out.inputs["Surface"])
    scene.world=world
    z=-1 if full else .35
    light("01 | softbox",(-3.5,-4.5,5.8),590,(.83,.93,1) if cinematic else (1,1,1),4.4,(0,0,z))
    light("02 | rim",(3,2.5,3.7),570,(.22,.49,1) if cinematic else (1,1,1),3.2,(0,0,z))
    light("03 | fill",(2.1,-4,1.8),170,(.48,.76,1) if cinematic else (1,1,1),2.2,(0,0,z))
    if full:
        bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-5.026))
        floor=bpy.context.object
        floor.name="STAGE - ground"
        material=bpy.data.materials.new("Ground | slate")
        material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=(.013,.023,.047,1)
        floor.data.materials.append(material)
    camera=bpy.data.objects.new("Eternal Halo camera",bpy.data.cameras.new("Lens"))
    scene.collection.objects.link(camera)
    scene.camera=camera
    camera.data.type="ORTHO"
    camera.data.lens=56
    scene.compositing_node_group=None
    if cinematic:
        g=bpy.data.node_groups.new("Optical glow · render only","CompositorNodeTree")
        scene.compositing_node_group=g
        g.interface.new_socket(name="Image",in_out="OUTPUT",socket_type="NodeSocketColor")
        source=g.nodes.new("CompositorNodeRLayers")
        glow=g.nodes.new("CompositorNodeGlare")
        glow.inputs["Type"].default_value="Fog Glow"
        glow.inputs["Threshold"].default_value=.55
        glow.inputs["Strength"].default_value=.52
        glow.inputs["Size"].default_value=.42
        glow.inputs["Tint"].default_value=(.09,.41,1,1)
        output=g.nodes.new("NodeGroupOutput")
        g.links.new(source.outputs["Image"],glow.inputs["Image"])
        g.links.new(glow.outputs["Image"],output.inputs["Image"])


def render(name,offset,target,scale,size=(1440,1000),perspective=False):
    scene=bpy.context.scene
    camera=scene.camera
    camera.location=Vector(target)+Vector(offset)
    point_at(camera,target)
    camera.data.type="PERSP" if perspective else "ORTHO"
    if perspective:
        camera.data.lens=scale
    else:
        camera.data.ortho_scale=scale
    scene.render.resolution_x,scene.render.resolution_y=size
    folder=ASSET/"work" if mode=="preview" else OUT
    scene.render.filepath=str(folder/(name+".png"))
    bpy.ops.render.render(write_still=True)
    print("RENDER_PASS",name,stage_label,flush=True)


def open_model(name):
    bpy.ops.wm.open_mainfile(filepath=str(ASSET/"blender"/(f"EternalHalo_{name}.blend")))
    set_gpu(bpy.context.scene)


def equip():
    bpy.ops.wm.open_mainfile(filepath=str(CROWN))
    set_gpu(bpy.context.scene)
    with bpy.data.libraries.load(str(ASSET/"blender/EternalHalo_UGC.blend"),link=False) as (src,dst):
        dst.objects=["EternalHalo_UGC"]
    collection=bpy.data.collections.new("Eternal Halo · original Crown reference fit")
    bpy.context.scene.collection.children.link(collection)
    collection.objects.link(dst.objects[0])
    bpy.context.scene["fit_scope"]="Blender; original crown and R15 pose from the first PR. Studio AFT place is separate."


mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "all"
OUT.mkdir(exist_ok=True)
if mode in {"all","preview"}:
    open_model("MASTER")
    stage(True)
    stage_label="cinematic"
    if mode=="preview":
        render("halo_preview",FRAMING["perspective"],(0,0,1.13),2.95,(960,720))
    else:
        render("halo_perspectiva",FRAMING["perspective"],(0,0,1.13),2.93)
        render("halo_detalle",(1.18,-3.1,1.4),(0,-.94,1.20),1.37,(1440,1080))
if mode in {"all","views","rear"}:
    open_model("UGC")
    stage(False)
    stage_label="neutral"
    for key,label in [("front","frente"),("back","espalda"),("left","izquierda"),("right","derecha")]:
        if mode!="rear" or key=="back":
            render("halo_"+label,FRAMING[key],(0,0,1.12),2.92)
    if mode!="rear":
        render("halo_ugc_neutro",FRAMING["perspective"],(0,0,1.12),2.92)
if mode in {"all","fit","preview","rear"}:
    equip()
    if mode!="preview":
        stage(False)
        stage_label="neutral, UGC with crown"
        for key,label in [("front","frente"),("back","espalda"),("left","izquierda"),("right","derecha")]:
            if mode!="rear" or key=="back":
                target=(0,0,.30 if key=="back" else .20)
                scale=3.64 if key=="back" else 3.40
                render("conjunto_"+label,FRAMING[key],target,scale,(1420,1110))
    if mode=="rear":
        sys.exit(0)
    stage(True)
    stage_label="cinematic, UGC with crown"
    if mode=="preview":
        render("conjunto_preview",(2.6,-5.9,1.90),(0,0,.27),3.44,(900,740))
    else:
        render("conjunto_perspectiva",(2.55,-6,2.02),(0,0,.23),3.52,(1560,1280))
        render("conjunto_detalle",(1.85,-5.2,1.38),(0,-.17,.80),2.88,(1560,1030))
        stage(True,True)
        render("conjunto_R15_completo",(2.5,-8,1.7),(0,0,-1.8),6.95,(1160,1420))
        scene=bpy.context.scene
        scene.render.filepath="//../renders/conjunto_R15_completo.png"
        bpy.ops.wm.save_as_mainfile(filepath=str(ASSET/"blender/EternalHalo_R15_DivineCrown.blend"),compress=True)
if mode in {"all","god"}:
    open_model("GOD_MODE")
    stage(True)
    stage_label="cinematic, Blender spin preview"
    bpy.context.scene.frame_set(36)
    render("godmode_frame_036",FRAMING["perspective"],(0,0,1.14),2.96)
