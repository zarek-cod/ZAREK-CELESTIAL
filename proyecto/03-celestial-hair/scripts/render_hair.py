"""Render Celestial Hair studies and combined Classic R15 views in Cycles/OptiX."""
from pathlib import Path
import sys

import bpy
from mathutils import Vector

ASSET=Path(__file__).resolve().parents[1]
HALO_ASSEMBLY=ASSET.parent/"02-eternal-halo/blender/EternalHalo_R15_DivineCrown.blend"
OUT=ASSET/"renders"
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
    scene.cycles.samples=60
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
    world=bpy.data.worlds.new("Celestial Hair cinematic" if cinematic else "Celestial Hair neutral")
    world.use_nodes=True
    nt=world.node_tree
    nt.nodes.clear()
    env=nt.nodes.new("ShaderNodeBackground")
    env.inputs[0].default_value=(.26,.32,.45,1) if cinematic else (.42,.42,.42,1)
    env.inputs[1].default_value=.38 if cinematic else .57
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
    light("01 | softbox",(-3.5,-4.5,5.8),530,(.91,.96,1) if cinematic else (1,1,1),2.6,(0,0,z))
    light("02 | rim",(3,2.5,3.7),570,(.22,.49,1) if cinematic else (1,1,1),3.2,(0,0,z))
    light("03 | fill",(2.1,-4,1.8),104,(.52,.73,1) if cinematic else (1,1,1),2.2,(0,0,z))
    if full:
        bpy.ops.mesh.primitive_plane_add(size=200,location=(0,0,-5.026))
        floor=bpy.context.object
        floor.name="STAGE - ground"
        material=bpy.data.materials.new("Ground | slate")
        material.node_tree.nodes.get("Principled BSDF").inputs["Base Color"].default_value=(.013,.023,.047,1)
        floor.data.materials.append(material)
    camera=bpy.data.objects.new("Celestial Hair camera",bpy.data.cameras.new("Lens"))
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



def open_model(variant):
    bpy.ops.wm.open_mainfile(filepath=str(ASSET/"blender"/f"CelestialHair_{variant}.blend"))
    set_gpu(bpy.context.scene)


def equip(with_accessories):
    bpy.ops.wm.open_mainfile(filepath=str(HALO_ASSEMBLY))
    set_gpu(bpy.context.scene)
    with bpy.data.libraries.load(str(ASSET/"blender/CelestialHair_UGC.blend"),link=False) as (source,target):
        target.objects=["CelestialHair_UGC"]
    collection=bpy.data.collections.new("Celestial Hair · Classic R15 test")
    bpy.context.scene.collection.children.link(collection)
    collection.objects.link(target.objects[0])
    if not with_accessories:
        for name in ("DivineCrown_UGC","EternalHalo_UGC"):
            bpy.data.objects.remove(bpy.data.objects[name],do_unlink=True)


def view_table():
    return (
        ("frente",(0,-5,.37)), ("espalda",(0,5,.70)),
        ("izquierda",(-5,0,.57)), ("derecha",(5,0,.57)),
        ("superior",(.0,-.025,5)),
    )


mode=sys.argv[sys.argv.index("--")+1] if "--" in sys.argv else "all"
if mode=="preview":
    open_model("MASTER")
    stage(True)
    stage_label="cinematic MASTER"
    render("01_hair_preview",(2,-5,.9),(0,0,-.41),2.17,(1000,920))
    equip(False)
    stage(False)
    stage_label="neutral UGC"
    render("02_r15_preview",(0,-5,.37),(0,0,-.46),2.13,(1050,960))
    equip(True)
    stage(True)
    stage_label="cinematic combined UGC"
    render("03_combined_preview",(1.7,-5,.95),(0,0,.14),3.03,(1120,1150))
else:
    open_model("MASTER")
    stage(False)
    stage_label="neutral MASTER"
    for name,offset in view_table():
        render("hair_"+name,offset,(0,0,-.38),2.17,(1450,1190))
    stage(True)
    stage_label="cinematic MASTER"
    render("hair_perspectiva",(2.1,-5.4,1.25),(0,0,-.42),2.22,(1530,1270))
    render("hair_detalle_flequillo",(.68,-4.2,.47),(0,-.36,-.33),1.36,(1450,1070))
    render("hair_detalle_nuca",(-1.7,4.8,.93),(.0,.25,-.41),1.54,(1450,1070))
    equip(False)
    stage(False)
    stage_label="neutral UGC on R15"
    render("r15_cabello",(1.53,-5.4,.51),(0,0,-.49),2.33,(1430,1200))
    render("r15_ojos",(0,-5,.0),(0,0,-.545),2.03,(1450,1130))
    equip(True)
    stage(True)
    stage_label="cinematic combined UGC"
    render("conjunto_perspectiva",(1.75,-5.6,1.15),(0,0,.13),3.13,(1630,1580))
    render("conjunto_espalda",(-1.25,5.5,1.26),(0,0,.14),3.13,(1520,1480))
    stage(False)
    stage_label="neutral combined UGC"
    render("conjunto_frente",(0,-5.3,.88),(0,0,.12),3.04,(1450,1450))
    render("conjunto_lateral",(5.3,0,.99),(0,0,.12),3.11,(1450,1450))
    stage(True,True)
    stage_label="cinematic full R15"
    render("conjunto_R15_completo",(2.2,-8,1.35),(0,0,-1.78),6.84,(1160,1450))
    scene=bpy.context.scene
    scene.render.filepath="//../renders/conjunto_R15_completo.png"
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type=="VIEW_3D":
                area.spaces.active.region_3d.view_perspective="CAMERA"
    bpy.ops.wm.save_as_mainfile(filepath=str(ASSET/"blender/CelestialHair_R15_Conjunto.blend"),compress=True)
